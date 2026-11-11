#!/usr/bin/env python3
"""
Persona Simulation for V3.5.0 Track B Evaluation

Run 3 student personas against the garden_source_accurate scenario
with billable DeepSeek API calls to evaluate Track B improvements
(severity-based ranking, reasoning operation classification).

Personas:
- Maya: Conceptual confusion (tests Step 0, claim anchoring)
- Jordan: Procedural confusion (tests reasoning operation classification)
- Sam: Motivational avoidance (tests concrete-first steps)

Usage:
    python scripts/simulate_personas_v3_5_0.py
"""

import json
import sys
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.utils import DeepSeekClient
from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from ui.scenarios import get_scenario


@dataclass
class PersonaResult:
    """Evidence captured from one persona simulation."""
    persona_name: str
    confusion_type: str

    # Round 1
    round1_issues: list[dict[str, Any]]
    round1_candidates: list[dict[str, Any]]
    round1_first_candidate: dict[str, Any]
    round1_hint: dict[str, Any]

    # Persona response
    persona_reasoning: str
    revision_text: str
    revision_type: str  # "surface_only" | "partial" | "complete"

    # Round 2 (if revision made)
    round2_issues: list[dict[str, Any]] | None
    round2_first_candidate: dict[str, Any] | None

    # Track B specific
    severity_ranking: dict[str, Any]
    reasoning_operations: dict[str, Any]

    # Metadata
    total_tokens: int
    total_latency_ms: int
    model_calls: int


class PersonaSimulator:
    """Simulates student persona behavior."""

    def __init__(self, service):
        self.service = service

    def _extract_model_metadata(self, state: dict[str, Any]) -> tuple[int, int, int]:
        """Extract token usage and latency from execution logs."""
        total_tokens = 0
        total_latency = 0
        model_calls = 0

        for log in state.get("execution_logs", []):
            for call in log.get("model_calls", []):
                model_calls += 1
                total_tokens += call.get("token_usage", {}).get("total_tokens", 0)
                total_latency += call.get("latency_ms", 0)

        return total_tokens, total_latency, model_calls

    def simulate_maya(self, scenario, session_id: str) -> PersonaResult:
        """
        Maya: Conceptual confusion

        Doesn't understand "claim" as argument terminology.
        Will fix surface number error but not add warrant.
        """
        print("\n=== Persona 1: Maya (Conceptual Confusion) ===")

        # Round 1: Initial submission
        ids_1 = {
            "composition_id": uuid.uuid4().hex,
            "round_id": uuid.uuid4().hex,
            "thread_id": uuid.uuid4().hex,
            "snapshot_id": uuid.uuid4().hex,
        }

        state1 = make_review_state(
            scenario.draft,
            scenario.grade_level,
            composition_id=ids_1["composition_id"],
            round_id=ids_1["round_id"],
            thread_id=ids_1["thread_id"],
            genre_selection=scenario.genre,
            assignment_prompt=scenario.assignment_prompt,
            teacher_directions=scenario.teacher_directions,
            source_material=scenario.source_material,
            student_concerns=scenario.student_concerns,
            scenario_id=scenario.scenario_id,
            fixture_version=scenario.fixture_version,
            debug_enabled=True,
        )

        result1 = self.service.start_composition(session_id, state1, ids_1["snapshot_id"])
        state1 = result1.state

        issues = state1["issues"]
        candidates = state1["revision_candidates"]
        first_candidate = candidates[0]
        hint = first_candidate["hint"]

        print(f"Round 1: {len(issues)} issues")
        print(f"First issue severity: {issues[0].get('finding_severity')}")
        print(f"First issue reasoning_operation: {issues[0].get('reasoning_operation')}")
        print(f"Hint steps: {len(hint['steps'])}")
        print(f"Hint Step 0: {hint['steps'][0][:80]}...")

        # Maya's reasoning
        persona_reasoning = (
            "I see the hint says something about 'claim' but I don't know what that means. "
            "It says 'some students' and the number is 62%, that's more than half. "
            "I should change 'some' to 'most'. But I don't understand what other sentence "
            "they want me to add."
        )

        # Maya's revision: fixes "some" → "most", doesn't add warrant
        revised_draft = scenario.draft.replace(
            "This result shows that some students are interested in fresh food.",
            "This result shows that most students are interested in fresh food."
        )

        print(f"\nMaya's revision: Changed 'some' to 'most', no warrant added")

        # Round 2: Submit revision
        ids_2 = {
            "round_id": uuid.uuid4().hex,
            "thread_id": uuid.uuid4().hex,
            "snapshot_id": uuid.uuid4().hex,
        }

        snapshots = self.service.storage.list_snapshots(ids_1["composition_id"])
        composition = self.service.storage.get_composition(ids_1["composition_id"])

        state2 = make_review_state(
            revised_draft,
            scenario.grade_level,
            composition_id=ids_1["composition_id"],
            round_id=ids_2["round_id"],
            thread_id=ids_2["thread_id"],
            original_writing=snapshots[0].writing,
            previous_writing=snapshots[0].writing,
            genre_selection=composition.genre_selection,
            assignment_prompt=composition.assignment_prompt,
            teacher_directions=composition.teacher_directions,
            source_material=composition.source_material,
            student_concerns=composition.student_concerns,
            scenario_id=scenario.scenario_id,
            fixture_version=scenario.fixture_version,
            revision_number=1,
            selected_goals=[{
                "goal_id": issues[0]["goal_id"],
                "title": first_candidate["title"],
            }],
            goal_self_reports={issues[0]["goal_id"]: "attempted"},
            text_diff=build_text_diff(snapshots[0].writing, revised_draft),
            debug_enabled=True,
        )

        result2 = self.service.submit_revision(session_id, state2, ids_2["snapshot_id"])
        state2 = result2.state

        round2_issues = state2.get("issues", [])
        round2_first = state2["revision_candidates"][0] if state2.get("revision_candidates") else None

        if round2_issues:
            print(f"Round 2: Same issue re-flagged (severity: {round2_issues[0].get('finding_severity')})")

        # Extract metadata
        tokens1, latency1, calls1 = self._extract_model_metadata(state1)
        tokens2, latency2, calls2 = self._extract_model_metadata(state2)

        return PersonaResult(
            persona_name="Maya",
            confusion_type="conceptual",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text=revised_draft,
            revision_type="surface_only",
            round2_issues=round2_issues,
            round2_first_candidate=round2_first,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity"),
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": issues[0].get("finding_severity") == "accuracy" if issues else False,
            },
            reasoning_operations={
                "round1_first_operation": issues[0].get("reasoning_operation"),
                "round1_first_starter": hint.get("sentence_starter"),
            },
            total_tokens=tokens1 + tokens2,
            total_latency_ms=latency1 + latency2,
            model_calls=calls1 + calls2,
        )

    def simulate_jordan(self, scenario, session_id: str) -> PersonaResult:
        """
        Jordan: Procedural confusion

        Understands concepts but needs structural scaffolding.
        Tests reasoning operation classification → starter alignment.
        """
        print("\n=== Persona 2: Jordan (Procedural Confusion) ===")

        # Round 1 only - Jordan understands but needs starters
        ids = {
            "composition_id": uuid.uuid4().hex,
            "round_id": uuid.uuid4().hex,
            "thread_id": uuid.uuid4().hex,
            "snapshot_id": uuid.uuid4().hex,
        }

        state = make_review_state(
            scenario.draft,
            scenario.grade_level,
            composition_id=ids["composition_id"],
            round_id=ids["round_id"],
            thread_id=ids["thread_id"],
            genre_selection=scenario.genre,
            assignment_prompt=scenario.assignment_prompt,
            teacher_directions=scenario.teacher_directions,
            source_material=scenario.source_material,
            student_concerns=scenario.student_concerns,
            scenario_id=scenario.scenario_id,
            fixture_version=scenario.fixture_version,
            debug_enabled=True,
        )

        result = self.service.start_composition(session_id, state, ids["snapshot_id"])
        state = result.state

        issues = state["issues"]
        candidates = state["revision_candidates"]
        first_candidate = candidates[0]
        hint = first_candidate["hint"]

        print(f"Round 1: {len(issues)} issues")

        # Check both suggestions for reasoning operation classification
        for i, (issue, candidate) in enumerate(zip(issues[:2], candidates[:2]), 1):
            print(f"\nIssue {i}:")
            print(f"  Severity: {issue.get('finding_severity')}")
            print(f"  Reasoning operation: {issue.get('reasoning_operation')}")
            print(f"  Starter: {candidate['hint'].get('sentence_starter')}")

        persona_reasoning = (
            "I understand both suggestions conceptually. For the first one, the starter "
            "'This evidence matters because ____' fits perfectly - I need to explain WHY "
            "62% matters. For the second one about responsibility, I get what they want "
            "but the starter will guide what I write."
        )

        # Jordan would produce good revisions with appropriate starters
        # Track B should fix Finding 7: no more "When ____, ____" for causal moves

        tokens, latency, calls = self._extract_model_metadata(state)

        return PersonaResult(
            persona_name="Jordan",
            confusion_type="procedural",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text="[Not simulated - Jordan would complete revision]",
            revision_type="complete",
            round2_issues=None,
            round2_first_candidate=None,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity"),
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": issues[0].get("finding_severity") == "accuracy" if issues else False,
            },
            reasoning_operations={
                "issue1_operation": issues[0].get("reasoning_operation"),
                "issue1_starter": candidates[0]["hint"].get("sentence_starter"),
                "issue2_operation": issues[1].get("reasoning_operation") if len(issues) > 1 else None,
                "issue2_starter": candidates[1]["hint"].get("sentence_starter") if len(candidates) > 1 else None,
            },
            total_tokens=tokens,
            total_latency_ms=latency,
            model_calls=calls,
        )

    def simulate_sam(self, scenario, session_id: str) -> PersonaResult:
        """
        Sam: Motivational avoidance

        Understands but freezes on blank revision.
        Tests concrete-first procedural steps (Track A F12).
        """
        print("\n=== Persona 3: Sam (Motivational Avoidance) ===")

        # Round 1 only
        ids = {
            "composition_id": uuid.uuid4().hex,
            "round_id": uuid.uuid4().hex,
            "thread_id": uuid.uuid4().hex,
            "snapshot_id": uuid.uuid4().hex,
        }

        state = make_review_state(
            scenario.draft,
            scenario.grade_level,
            composition_id=ids["composition_id"],
            round_id=ids["round_id"],
            thread_id=ids["thread_id"],
            genre_selection=scenario.genre,
            assignment_prompt=scenario.assignment_prompt,
            teacher_directions=scenario.teacher_directions,
            source_material=scenario.source_material,
            student_concerns=scenario.student_concerns,
            scenario_id=scenario.scenario_id,
            fixture_version=scenario.fixture_version,
            debug_enabled=True,
        )

        result = self.service.start_composition(session_id, state, ids["snapshot_id"])
        state = result.state

        issues = state["issues"]
        candidates = state["revision_candidates"]
        first_candidate = candidates[0]
        hint = first_candidate["hint"]

        print(f"Round 1: {len(issues)} issues")
        print(f"First issue severity: {issues[0].get('finding_severity')}")
        print(f"Hint step 1 (after Step 0): {hint['steps'][1][:80]}...")
        print(f"Stuck step: {first_candidate['stuck_step'][:80]}...")

        persona_reasoning = (
            "I know what they want me to do, but I'm stuck on how to start. "
            "The hint's first real step after the concept explanation is concrete - "
            "it tells me exactly where to look. That helps me get unstuck."
        )

        tokens, latency, calls = self._extract_model_metadata(state)

        return PersonaResult(
            persona_name="Sam",
            confusion_type="motivational",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text="[Not simulated - Sam would complete with concrete first step]",
            revision_type="complete",
            round2_issues=None,
            round2_first_candidate=None,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity"),
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": issues[0].get("finding_severity") == "accuracy" if issues else False,
            },
            reasoning_operations={
                "round1_first_operation": issues[0].get("reasoning_operation"),
                "round1_first_starter": hint.get("sentence_starter"),
            },
            total_tokens=tokens,
            total_latency_ms=latency,
            model_calls=calls,
        )


    def _run_round1(
        self,
        scenario,
        session_id: str,
        grade_level_override: str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        """Submit a draft and return (state, first_candidate, issues, candidates)."""
        ids = {
            "composition_id": uuid.uuid4().hex,
            "round_id": uuid.uuid4().hex,
            "thread_id": uuid.uuid4().hex,
            "snapshot_id": uuid.uuid4().hex,
        }
        state = make_review_state(
            scenario.draft,
            grade_level_override or scenario.grade_level,
            composition_id=ids["composition_id"],
            round_id=ids["round_id"],
            thread_id=ids["thread_id"],
            genre_selection=scenario.genre,
            assignment_prompt=scenario.assignment_prompt,
            teacher_directions=scenario.teacher_directions,
            framework_name=getattr(scenario, "framework_name", ""),
            framework_components=list(getattr(scenario, "framework_components", [])),
            source_material=scenario.source_material,
            student_concerns=scenario.student_concerns,
            scenario_id=scenario.scenario_id,
            fixture_version=scenario.fixture_version,
            debug_enabled=True,
        )
        result = self.service.start_composition(session_id, state, ids["snapshot_id"])
        state = result.state
        issues = state.get("issues", [])
        candidates = state.get("revision_candidates", [])
        return state, ids, issues, candidates

    def simulate_alex(self, scenario, session_id: str) -> PersonaResult:
        """
        Alex: 5th Grade — no-source argument draft.

        Tests whether severity ranking and hint layering work without a source.
        Alex is a grade-level 5th grader who writes short, assertive sentences
        but doesn't yet know how to explain a reason beyond asserting it.
        Development-tier findings are expected to dominate when no accuracy
        violations are possible without source material.
        """
        print("\n=== Persona 4: Alex (5th Grade — no source) ===")

        state, ids, issues, candidates = self._run_round1(scenario, session_id)
        first_candidate = candidates[0] if candidates else {}
        hint = first_candidate.get("hint", {})

        print(f"Round 1: {len(issues)} issues")
        if issues:
            print(f"First issue severity: {issues[0].get('finding_severity')}")
            print(f"First issue operation: {issues[0].get('reasoning_operation')}")
        if hint.get("steps"):
            print(f"Hint Step 0: {hint['steps'][0][:80]}...")

        persona_reasoning = (
            "The feedback says I need to explain my reason, not just say it. "
            "I know why I think this but I never wrote the why part down. "
            "The hint gives me a step that starts with finding my reason sentence — "
            "that's easy, I can see it. Then I need to add a because sentence."
        )

        tokens, latency, calls = self._extract_model_metadata(state)

        return PersonaResult(
            persona_name="Alex",
            confusion_type="procedural",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text="[Not simulated - Alex would add one because-sentence]",
            revision_type="partial",
            round2_issues=None,
            round2_first_candidate=None,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity") if issues else None,
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": (issues[0].get("finding_severity") == "accuracy") if issues else False,
            },
            reasoning_operations={
                "round1_first_operation": issues[0].get("reasoning_operation") if issues else None,
                "round1_first_starter": hint.get("sentence_starter"),
            },
            total_tokens=tokens,
            total_latency_ms=latency,
            model_calls=calls,
        )

    def simulate_river(self, scenario, session_id: str) -> PersonaResult:
        """
        River: 7th Grade — RACES informational with source.

        Tests framework coverage (RACES) and informational genre.
        River follows directions carefully but conflates 'Cite' (RACES step C)
        with quoting rather than paraphrasing, so the C step gets a quote
        without a signal phrase. The Coordinator should flag a RACES coverage
        gap and the feedback should use a source_based reasoning operation.
        """
        print("\n=== Persona 5: River (7th Grade — RACES informational) ===")

        state, ids, issues, candidates = self._run_round1(scenario, session_id)
        first_candidate = candidates[0] if candidates else {}
        hint = first_candidate.get("hint", {})

        print(f"Round 1: {len(issues)} issues")
        framework_coverage = state.get("framework_coverage", [])
        print(f"Framework coverage entries: {len(framework_coverage)}")
        for entry in framework_coverage:
            print(f"  {entry.get('component')}: {entry.get('status')}")
        if issues:
            print(f"First issue severity: {issues[0].get('finding_severity')}")
            print(f"First issue operation: {issues[0].get('reasoning_operation')}")
        if hint.get("steps"):
            print(f"Hint Step 0: {hint['steps'][0][:80]}...")

        persona_reasoning = (
            "My teacher said to use RACES. I restated, answered, and I know I cited "
            "because I copied a sentence from the text. But the feedback says my "
            "explanation step is missing. The E step — I see it now, I skipped the "
            "why-it-connects part entirely and went straight to the sum-up."
        )

        tokens, latency, calls = self._extract_model_metadata(state)

        return PersonaResult(
            persona_name="River",
            confusion_type="conceptual",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text="[Not simulated - River would add an E-step explanation sentence]",
            revision_type="partial",
            round2_issues=None,
            round2_first_candidate=None,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity") if issues else None,
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": (issues[0].get("finding_severity") == "accuracy") if issues else False,
            },
            reasoning_operations={
                "round1_first_operation": issues[0].get("reasoning_operation") if issues else None,
                "round1_first_starter": hint.get("sentence_starter"),
                "framework_coverage": [
                    {"component": e.get("component"), "status": e.get("status")}
                    for e in framework_coverage
                ],
            },
            total_tokens=tokens,
            total_latency_ms=latency,
            model_calls=calls,
        )

    def simulate_devon(self, scenario, session_id: str) -> PersonaResult:
        """
        Devon: 6th Grade — source mismatch argument.

        Tests accuracy-tier detection when a student invents or inflates
        source details (500 students vs. 50; 'improve health' vs. 'try vegetables').
        Expects accuracy findings to dominate and rank first. Devon is confident
        and doesn't think they misread the source — this tests whether the hint
        Step 0 concept restatement is clear enough to surface the mismatch.
        """
        print("\n=== Persona 6: Devon (6th Grade — source mismatch) ===")

        state, ids, issues, candidates = self._run_round1(scenario, session_id)
        first_candidate = candidates[0] if candidates else {}
        hint = first_candidate.get("hint", {})

        print(f"Round 1: {len(issues)} issues")
        if issues:
            for i, issue in enumerate(issues[:3], 1):
                print(f"  Issue {i}: severity={issue.get('finding_severity')}, "
                      f"op={issue.get('reasoning_operation')}, "
                      f"source_dependent={issue.get('source_dependent')}")
        if hint.get("steps"):
            print(f"Hint Step 0: {hint['steps'][0][:80]}...")

        persona_reasoning = (
            "The feedback says I got the survey number wrong — I wrote 500 but it was 50. "
            "I didn't realize I misread it. It also says the survey didn't measure health, "
            "just whether students would try vegetables. I need to go back to the source "
            "and reread it carefully before I revise."
        )

        tokens, latency, calls = self._extract_model_metadata(state)

        # Check whether all accuracy issues have source_dependent=True
        accuracy_issues = [i for i in issues if i.get("finding_severity") == "accuracy"]

        return PersonaResult(
            persona_name="Devon",
            confusion_type="conceptual",
            round1_issues=issues,
            round1_candidates=candidates,
            round1_first_candidate=first_candidate,
            round1_hint=hint,
            persona_reasoning=persona_reasoning,
            revision_text="[Not simulated - Devon would reread source and correct numbers]",
            revision_type="partial",
            round2_issues=None,
            round2_first_candidate=None,
            severity_ranking={
                "round1_first_severity": issues[0].get("finding_severity") if issues else None,
                "round1_second_severity": issues[1].get("finding_severity") if len(issues) > 1 else None,
                "accuracy_ranked_first": (issues[0].get("finding_severity") == "accuracy") if issues else False,
                "accuracy_issue_count": len(accuracy_issues),
                "accuracy_issues_source_dependent": all(
                    i.get("source_dependent") for i in accuracy_issues
                ) if accuracy_issues else None,
            },
            reasoning_operations={
                "round1_first_operation": issues[0].get("reasoning_operation") if issues else None,
                "round1_first_starter": hint.get("sentence_starter"),
            },
            total_tokens=tokens,
            total_latency_ms=latency,
            model_calls=calls,
        )


def compare_with_baseline(results: list[PersonaResult]) -> dict[str, Any]:
    """Compare v3.5.0 results with v3.4.1 baseline."""

    comparison = {
        "v3_5_0_date": datetime.now(timezone.utc).isoformat(),
        "personas": {},
        "track_b_findings": {},
    }

    # Track B Finding 6: Severity-based ranking
    severity_checks = []
    for result in results:
        severity_checks.append({
            "persona": result.persona_name,
            "first_severity": result.severity_ranking["round1_first_severity"],
            "accuracy_ranked_first": result.severity_ranking["accuracy_ranked_first"],
        })

    comparison["track_b_findings"]["f6_severity_ranking"] = {
        "description": "Accuracy-tier findings should rank first",
        "checks": severity_checks,
        "baseline_behavior": "No severity field existed; fabricated content ranked with warrant gaps",
        "v3_5_0_behavior": "finding_severity field added; accuracy tier ranks first",
    }

    # Track B Finding 7: Reasoning operation classification
    operation_checks = []
    for result in results:
        if "issue1_operation" in result.reasoning_operations:
            operation_checks.append({
                "persona": result.persona_name,
                "issue1_operation": result.reasoning_operations["issue1_operation"],
                "issue1_starter": result.reasoning_operations["issue1_starter"],
                "issue2_operation": result.reasoning_operations.get("issue2_operation"),
                "issue2_starter": result.reasoning_operations.get("issue2_starter"),
            })
        else:
            operation_checks.append({
                "persona": result.persona_name,
                "round1_operation": result.reasoning_operations["round1_first_operation"],
                "round1_starter": result.reasoning_operations["round1_first_starter"],
            })

    comparison["track_b_findings"]["f7_reasoning_operation"] = {
        "description": "Causal operations should not receive 'When ____, ____' starters",
        "checks": operation_checks,
        "baseline_behavior": "No reasoning_operation field; 'When' starters appeared on causal moves",
        "v3_5_0_behavior": "reasoning_operation classification guides starter selection",
    }

    # Per-persona details
    for result in results:
        comparison["personas"][result.persona_name] = {
            "confusion_type": result.confusion_type,
            "revision_type": result.revision_type,
            "persona_reasoning": result.persona_reasoning,
            "round1_issue_count": len(result.round1_issues),
            "round2_issue_count": len(result.round2_issues) if result.round2_issues else 0,
            "severity_ranking": result.severity_ranking,
            "reasoning_operations": result.reasoning_operations,
            "tokens": result.total_tokens,
            "latency_ms": result.total_latency_ms,
            "model_calls": result.model_calls,
        }

    return comparison


def main():
    """Run persona simulations and generate comparison report."""

    # Load client from .env
    client = DeepSeekClient.from_env(require_thinking=False)

    # Setup
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    db_path = f"data/persona_simulation_v3_5_0_{timestamp}.db"

    print(f"Running persona simulation v3.5.0 (6 personas)")
    print(f"Database: {db_path}")
    print(f"Billable API calls will be made to DeepSeek")

    service = create_writing_assistant_service(client, db_path)
    simulator = PersonaSimulator(service)

    # Scenarios
    garden_accurate = get_scenario("garden_source_accurate")     # 6th Grade, argument, src
    garden_mismatch = get_scenario("garden_source_mismatch")     # 6th Grade, argument, src mismatch
    short_arg_5     = get_scenario("short_grade5_argument")      # 5th Grade, auto, no src
    races_info_7    = get_scenario("races_informational_pollination")  # 7th Grade, informational, src

    session_id = uuid.uuid4().hex

    # --- Original 3 personas (garden_source_accurate, 6th Grade) ---
    maya   = simulator.simulate_maya(garden_accurate, session_id)
    jordan = simulator.simulate_jordan(garden_accurate, session_id)
    sam    = simulator.simulate_sam(garden_accurate, session_id)

    # --- New 3 personas (different grades and scenarios) ---
    alex   = simulator.simulate_alex(short_arg_5, session_id)       # 5th Grade, no source
    river  = simulator.simulate_river(races_info_7, session_id)     # 7th Grade, RACES
    devon  = simulator.simulate_devon(garden_mismatch, session_id)  # 6th Grade, source mismatch

    results = [maya, jordan, sam, alex, river, devon]

    # Generate comparison
    comparison = compare_with_baseline(results)

    # Summary stats
    total_tokens  = sum(r.total_tokens for r in results)
    total_latency = sum(r.total_latency_ms for r in results)
    total_calls   = sum(r.model_calls for r in results)

    comparison["summary"] = {
        "total_personas": len(results),
        "total_model_calls": total_calls,
        "total_tokens": total_tokens,
        "total_latency_ms": total_latency,
        "avg_tokens_per_persona": total_tokens // len(results),
        "avg_latency_per_persona_ms": total_latency // len(results),
    }

    # Save results
    Path("data/evidence").mkdir(parents=True, exist_ok=True)
    output_path = f"data/evidence/persona_simulation_v3_5_0_{timestamp}.json"
    with open(output_path, "w") as f:
        json.dump({
            "metadata": {
                "version": "v3.5.0",
                "date": timestamp,
                "scenarios": {
                    "garden_accurate": "garden_source_accurate (6th Grade, argument, src)",
                    "garden_mismatch": "garden_source_mismatch (6th Grade, argument, src mismatch)",
                    "short_arg_5":     "short_grade5_argument (5th Grade, argument, no src)",
                    "races_info_7":    "races_informational_pollination (7th Grade, informational, src)",
                },
                "database": db_path,
                "model_config": client.model_config(),
            },
            "results": [asdict(r) for r in results],
            "comparison": comparison,
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"SIMULATION COMPLETE — 6 personas")
    print(f"{'='*70}")
    print(f"Output: {output_path}")
    print(f"\n{'Persona':<10} {'Grade':<10} {'Scenario':<30} {'Sev':<10} {'Op':<14} {'Steps'}")
    print("-" * 85)
    scenario_labels = {
        "Maya":   "garden_source_accurate",
        "Jordan": "garden_source_accurate",
        "Sam":    "garden_source_accurate",
        "Alex":   "short_grade5_argument",
        "River":  "races_informational_pollination",
        "Devon":  "garden_source_mismatch",
    }
    grade_labels = {
        "Maya": "6th", "Jordan": "6th", "Sam": "6th",
        "Alex": "5th", "River": "7th", "Devon": "6th",
    }
    for r in results:
        sev   = r.severity_ranking["round1_first_severity"]
        ops   = r.reasoning_operations
        op    = ops.get("round1_first_operation") or ops.get("issue1_operation")
        steps = len(r.round1_hint.get("steps", []))
        print(f"{r.persona_name:<10} {grade_labels[r.persona_name]:<10} "
              f"{scenario_labels[r.persona_name]:<30} {str(sev):<10} {str(op):<14} {steps}")

    print(f"\nTrack B Findings:")
    print(f"  F6 Severity ranking:")
    for c in comparison["track_b_findings"]["f6_severity_ranking"]["checks"]:
        print(f"    {c['persona']}: {c['first_severity']}, accuracy_first={c['accuracy_ranked_first']}")
    print(f"  F7 Reasoning operation:")
    for c in comparison["track_b_findings"]["f7_reasoning_operation"]["checks"]:
        op = c.get("round1_operation") or c.get("issue1_operation")
        s  = c.get("round1_starter") or c.get("issue1_starter")
        print(f"    {c['persona']}: op={op}, starter={repr(s)}")

    print(f"\nTotals: {total_calls} calls, {total_tokens:,} tokens, {total_latency/1000:.1f}s")
    return output_path


if __name__ == "__main__":
    main()
