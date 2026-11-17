import json
from pathlib import Path

import pytest

from agents.prompts import (
    PHASE2_LEAN_COORDINATOR_FINAL_PROMPT,
    PHASE2_LEAN_COORDINATOR_ROUND_PROMPT,
    PHASE2_LEAN_PROMPT_VERSION,
    PHASE2_LEAN_SCHEMA_VERSION,
    PHASE2_LEAN_SUPPORT_FINAL_PROMPT,
    PHASE2_LEAN_SUPPORT_ROUND_PROMPT,
)
from agents.support_agent import InstructionalSupportAgent
from agents.utils import DeepSeekClient
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from scripts.evaluate_v3 import (
    BudgetedClient,
    SupportReasoningClient,
    resolve_model_call_budget,
    run_mode,
)
from tests.helpers import FakeClient, candidate_for, issue_for
from ui.scenarios import (
    load_acceptance_scenarios,
    load_phase1_development_scenarios,
    load_phase2_branch_scenarios,
)

PREVIOUS = "A claim.\n\nAn optional example. A reason."
CURRENT = "A clearer claim.\n\nA reason."
REFERENCE = "A reason."


def lean_handoff():
    issue = issue_for(CURRENT, REFERENCE)
    selected = [candidate_for(issue)]
    state = make_review_state(
        CURRENT,
        "6th Grade",
        original_writing=PREVIOUS,
        previous_writing=PREVIOUS,
        genre_selection="argument",
        revision_number=1,
        selected_goals=selected,
        goal_self_reports={"goal_1": "attempted"},
        text_diff=build_text_diff(PREVIOUS, CURRENT),
    )
    expected = {
        "goal_id": "goal_1",
        "status": "specific_improvement",
        "observation": "The reason is clearer, but the connection remains incomplete.",
        "evidence_reference": REFERENCE,
        "goal_outcome": "partially_addressed",
        "narrowing": "none",
        "narrowing_evidence_reference": "",
        "requirement_source": "",
        "requirement_reference": "",
        "carry_forward": True,
    }
    state.update(
        {
            "working_genre": "argument",
            "strengths": ["The draft gives a reason."],
            "issues": [issue],
            "framework_coverage": [],
            "selected_goal_observations": [expected],
            "source_limitations": ["Add the passage for verification."],
            "coordinator_reasoning": "The selected goal has a meaningful remainder.",
        }
    )
    return state, expected


def lean_round_payload(state):
    candidates = []
    for issue in state["issues"]:
        candidates.append(
            {
                "goal_id": issue["goal_id"],
                "title": "Explain the connection",
                "why_it_matters": "Readers need to understand how your ideas connect.",
                "revision_action": "Explain the connection in your own words.",
                "hint": {
                    "steps": [
                        "A clear reason explains how ideas connect.",
                        "Find the reason in this passage.",
                        "Explain the connection in your own words.",
                    ],
                    "self_check": "Does your revision explain the connection?",
                },
                "stuck_step": "Say one connecting idea aloud before writing it.",
            }
        )
    return {
        "strengths": ["You give a clear reason."],
        "candidates": candidates,
        "goal_feedback": [
            {
                "goal_id": item["goal_id"],
                "observation": "You made one part clearer, and one part remains.",
            }
            for item in state["selected_goal_observations"]
        ],
    }


def lean_agent():
    return InstructionalSupportAgent(
        FakeClient([]),
        round_prompt=PHASE2_LEAN_SUPPORT_ROUND_PROMPT,
        final_prompt=PHASE2_LEAN_SUPPORT_FINAL_PROMPT,
        phase1_contract=True,
        lean_contract=True,
    )


def test_lean_round_merges_full_handoff_from_coordinator():
    state, expected = lean_handoff()

    result = lean_agent()._round_values(json.dumps(lean_round_payload(state)), state)

    candidate = result["revision_candidates"][0]
    issue = state["issues"][0]
    assert candidate["draft_reference"] == issue["draft_reference"]
    assert candidate["paragraph_number"] == issue["paragraph_number"]
    assert candidate["occurrence"] == issue["occurrence"]
    assert candidate["hint"]["passage_reference"] == issue["draft_reference"]
    assert result["source_limitations"] == state["source_limitations"]
    feedback = result["goal_feedback"][0]
    assert feedback["observation"] == "You made one part clearer, and one part remains."
    for field in (
        "goal_id",
        "status",
        "evidence_reference",
        "goal_outcome",
        "narrowing",
        "narrowing_evidence_reference",
        "requirement_source",
        "requirement_reference",
        "carry_forward",
    ):
        assert feedback[field] == expected[field]


def test_lean_round_restores_coordinator_candidate_order():
    state, _ = lean_handoff()
    second = issue_for(
        CURRENT,
        "A clearer claim.",
        goal_id="goal_2",
        description="The revised claim can be more specific.",
    )
    state["issues"].append(second)
    payload = lean_round_payload(state)
    payload["candidates"].reverse()

    result = lean_agent()._round_values(json.dumps(payload), state)

    assert [item["goal_id"] for item in result["revision_candidates"]] == [
        "goal_1",
        "goal_2",
    ]


@pytest.mark.parametrize(
    ("location", "field", "value"),
    [
        ("candidate", "draft_reference", "tampered reference"),
        ("candidate", "paragraph_number", 99),
        ("candidate", "occurrence", 99),
        ("hint", "passage_reference", "tampered reference"),
        ("goal_feedback", "status", "uncertain"),
        ("goal_feedback", "evidence_reference", "tampered evidence"),
        ("goal_feedback", "goal_outcome", "fully_addressed"),
        ("goal_feedback", "narrowing", "required"),
        ("goal_feedback", "narrowing_evidence_reference", "tampered deletion"),
        ("goal_feedback", "requirement_source", "framework"),
        ("goal_feedback", "requirement_reference", "tampered requirement"),
        ("goal_feedback", "carry_forward", False),
        ("top", "source_limitations", []),
    ],
)
def test_lean_round_rejects_copied_or_tampered_handoff_fields(location, field, value):
    state, _ = lean_handoff()
    payload = lean_round_payload(state)
    if location == "candidate":
        payload["candidates"][0][field] = value
    elif location == "hint":
        payload["candidates"][0]["hint"][field] = value
    elif location == "goal_feedback":
        payload["goal_feedback"][0][field] = value
    else:
        payload[field] = value

    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        lean_agent()._round_values(json.dumps(payload), state)


@pytest.mark.parametrize("kind", ["candidate", "goal_feedback"])
def test_lean_round_rejects_unknown_ids(kind):
    state, _ = lean_handoff()
    payload = lean_round_payload(state)
    target = payload["candidates"][0] if kind == "candidate" else payload["goal_feedback"][0]
    target["goal_id"] = "unknown_goal"

    with pytest.raises(ValueError, match="exactly one"):
        lean_agent()._round_values(json.dumps(payload), state)


def test_lean_round_still_enforces_full_instructional_validation():
    state, _ = lean_handoff()
    payload = lean_round_payload(state)
    payload["candidates"][0]["hint"]["steps"][1] = "Complete ____ in this passage."

    with pytest.raises(ValueError, match="Completion blanks"):
        lean_agent()._round_values(json.dumps(payload), state)


def final_handoff():
    state = make_review_state(
        CURRENT,
        "6th Grade",
        review_mode="final",
        original_writing=PREVIOUS,
        genre_selection="argument",
        text_diff=build_text_diff(PREVIOUS, CURRENT),
    )
    state.update(
        {
            "original_strengths": ["The original states a claim."],
            "comparison_improvements": [
                {
                    "finding_id": "improvement_1",
                    "summary": "The claim is clearer.",
                    "original_reference": "A claim.",
                    "final_reference": "A clearer claim.",
                    "goal_id": "goal_1",
                }
            ],
            "comparison_regressions": [
                {
                    "finding_id": "regression_1",
                    "summary": "The optional example was removed.",
                    "original_reference": "An optional example.",
                    "final_reference": "",
                    "goal_id": "",
                }
            ],
            "future_areas": ["Consider another example."],
        }
    )
    return state


def lean_final_payload():
    return {
        "improvements": [
            {"finding_id": "improvement_1", "observation": "You made your claim clearer."}
        ],
        "regressions": [
            {
                "finding_id": "regression_1",
                "observation": "Your earlier example is no longer in the final draft.",
            }
        ],
        "conclusion": "You revisited your ideas and made your own choices.",
    }


def test_lean_final_merges_references_and_preserves_deletion_regression():
    state = final_handoff()

    result = lean_agent()._final_values(json.dumps(lean_final_payload()), state)

    reflection = result["final_reflection"]
    assert reflection["original_strengths"] == state["original_strengths"]
    assert reflection["future_possibilities"] == state["future_areas"]
    assert reflection["improvements"][0]["final_reference"] == "A clearer claim."
    assert reflection["regressions"][0]["final_reference"] == ""
    assert reflection["regressions"][0]["observation"] == (
        "Your earlier example is no longer in the final draft."
    )


@pytest.mark.parametrize("kind", ["improvements", "regressions"])
def test_lean_final_rejects_copied_final_reference(kind):
    payload = lean_final_payload()
    payload[kind][0]["final_reference"] = "tampered reference"

    with pytest.raises(ValueError, match="Extra inputs are not permitted"):
        lean_agent()._final_values(json.dumps(payload), final_handoff())


def test_lean_repair_requests_only_ids_and_prose_then_merges():
    state, _ = lean_handoff()
    invalid = lean_round_payload(state)
    invalid["candidates"][0]["hint"]["steps"] = ["Too short."]
    valid = lean_round_payload(state)
    client = FakeClient([json.dumps(invalid), json.dumps(valid)])
    agent = InstructionalSupportAgent(
        client,
        round_prompt=PHASE2_LEAN_SUPPORT_ROUND_PROMPT,
        final_prompt=PHASE2_LEAN_SUPPORT_FINAL_PROMPT,
        phase1_contract=True,
        lean_contract=True,
    )

    result = agent.run(state)

    assert len(result.raw_responses) == 2
    assert result.model_calls[1]["schema_repair"] is True
    correction = result.messages[-1]["content"]
    assert "Return only the required IDs and student-facing prose" in correction
    assert "Python supplies those fields deterministically" in correction
    assert result.values["revision_candidates"][0]["draft_reference"] == REFERENCE


def test_lean_contract_requires_phase1_and_prompt_schemas_are_lean():
    with pytest.raises(ValueError, match="requires the Phase 1"):
        InstructionalSupportAgent(FakeClient([]), lean_contract=True)

    round_schema = PHASE2_LEAN_SUPPORT_ROUND_PROMPT.split("7. OUTPUT SCHEMA", 1)[1]
    round_value = json.loads(round_schema[round_schema.index("{") : round_schema.rindex("}") + 1])
    assert set(round_value) == {"strengths", "candidates", "goal_feedback"}
    assert set(round_value["candidates"][0]) == {
        "goal_id",
        "title",
        "why_it_matters",
        "revision_action",
        "hint",
        "stuck_step",
    }
    assert set(round_value["candidates"][0]["hint"]) == {"steps", "self_check"}
    assert set(round_value["goal_feedback"][0]) == {"goal_id", "observation"}
    final_schema = PHASE2_LEAN_SUPPORT_FINAL_PROMPT.split("3. OUTPUT SCHEMA", 1)[1]
    final_value = json.loads(final_schema[final_schema.index("{") : final_schema.rindex("}") + 1])
    assert set(final_value["improvements"][0]) == {"finding_id", "observation"}
    assert set(final_value["regressions"][0]) == {"finding_id", "observation"}
    assert PHASE2_LEAN_COORDINATOR_ROUND_PROMPT
    assert PHASE2_LEAN_COORDINATOR_FINAL_PROMPT


def test_phase2_lean_evaluator_uses_versions_prompts_and_merge_contract(tmp_path, monkeypatch):
    client = FakeClient([])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )
    captured = []

    def fake_run(service, session_id, scenario):
        captured.append(service.support_agent)
        return {
            "scenario_id": scenario.scenario_id,
            "fixture_version": scenario.fixture_version,
            "initial_state": {},
        }

    monkeypatch.setattr("scripts.evaluate_v3.run_scenario", fake_run)
    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261117T000002Z",
        "phase1_development",
        scenario_number=1,
        experiment_arm="phase2_lean",
        max_model_calls=2,
    )

    support = captured[0]
    assert support.phase1_contract is True
    assert support.lean_contract is True
    assert support.round_prompt == PHASE2_LEAN_SUPPORT_ROUND_PROMPT
    assert support.final_prompt == PHASE2_LEAN_SUPPORT_FINAL_PROMPT
    configuration = result["summary"]["configuration"]
    assert configuration["prompt_version"] == PHASE2_LEAN_PROMPT_VERSION
    assert configuration["schema_version"] == PHASE2_LEAN_SCHEMA_VERSION
    assert result["summary"]["errors"] == []



def test_lean_completion_ellipsis_trace_is_rejected_after_merge():
    state, _ = lean_handoff()
    payload = lean_round_payload(state)
    payload["candidates"][0]["stuck_step"] = (
        'Finish this thought in your own words: "This supports my claim because…"'
    )

    with pytest.raises(ValueError, match="Instructional ellipses"):
        lean_agent()._round_values(json.dumps(payload), state)


def test_automatic_call_budget_adds_repair_headroom_and_preserves_explicit_caps():
    acceptance = load_acceptance_scenarios()[0]
    development = load_phase1_development_scenarios()[1]

    acceptance_budget = resolve_model_call_budget([acceptance], None, 2)
    assert acceptance_budget == {
        "max_model_calls": 8,
        "base_model_call_estimate": 6,
        "repair_headroom": 2,
        "mode": "base_plus_repairs",
    }
    development_budget = resolve_model_call_budget([development], None, 2)
    assert development_budget["max_model_calls"] == 4
    assert development_budget["base_model_call_estimate"] == 2
    explicit = resolve_model_call_budget([acceptance], 6, 2)
    assert explicit["max_model_calls"] == 6
    assert explicit["repair_headroom"] == 0
    assert explicit["mode"] == "explicit"


def test_support_reasoning_wrapper_shares_budget_and_restores_coordinator_effort():
    raw = FakeClient(["{}"])
    budgeted = BudgetedClient(raw, max_model_calls=2, max_total_tokens=None)
    support = SupportReasoningClient(budgeted, "low")

    assert support.chat_completion([{"role": "user", "content": "test"}]) == "{}"

    assert raw.reasoning_effort == "high"
    assert budgeted.model_calls == 1
    assert budgeted.attempts[0]["metadata"]["reasoning_effort"] == "low"
    assert budgeted.model_config()["reasoning_effort"] == "high"
    assert support.model_config()["reasoning_effort"] == "low"


def test_phase2_lean_low_effort_evaluator_records_split_configuration(tmp_path, monkeypatch):
    client = FakeClient([])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )
    captured = []

    def fake_run(service, session_id, scenario):
        captured.append(service)
        return {
            "scenario_id": scenario.scenario_id,
            "fixture_version": scenario.fixture_version,
            "initial_state": {},
        }

    monkeypatch.setattr("scripts.evaluate_v3.run_scenario", fake_run)
    result, database = run_mode(
        "thinking",
        tmp_path,
        "20261117T000003Z",
        "phase1_development",
        scenario_number=2,
        experiment_arm="phase2_lean",
        max_model_calls=None,
        repair_headroom=2,
        support_reasoning_effort="low",
    )

    service = captured[0]
    assert service.client.max_model_calls == 4
    assert service.client.model_config()["reasoning_effort"] == "high"
    assert service.support_agent.client.model_config()["reasoning_effort"] == "low"
    assert service.support_agent.client.client is service.client
    configuration = result["summary"]["configuration"]
    assert configuration["model_call_budget_mode"] == "base_plus_repairs"
    assert configuration["base_model_call_estimate"] == 2
    assert configuration["repair_headroom"] == 2
    assert configuration["support_reasoning_effort"] == "low"
    assert "support_low" in Path(database).name



def test_phase2_branch_fixtures_and_evaluator_budget_cover_targeted_matrix(tmp_path, monkeypatch):
    scenarios = load_phase2_branch_scenarios()
    assert len(scenarios) == 6
    required, optional, frustration, discouragement, deletion, whole_deletion = scenarios
    assert required.framework_components == (
        "Survey evidence",
        "Explanation of evidence",
    )
    assert required.controlled_round["revision_candidates"][0]["goal_id"] == "goal_survey"
    assert not optional.revisions
    assert frustration.student_concerns.startswith("This is hard")
    assert "give up" in discouragement.draft
    assert deletion.finish
    assert deletion.controlled_round["revision_number"] == 1
    assert "\n\n" not in whole_deletion.draft
    assert whole_deletion.finish
    assert "reccomendations" in optional.draft
    assert all(scenario.review_annotations for scenario in scenarios)

    client = FakeClient([])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )
    captured = []

    def fake_run(service, session_id, scenario):
        captured.append(scenario.scenario_id)
        return {
            "scenario_id": scenario.scenario_id,
            "fixture_version": scenario.fixture_version,
            "initial_state": {},
        }

    monkeypatch.setattr("scripts.evaluate_v3.run_scenario", fake_run)
    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261117T000004Z",
        "phase2_branches",
        experiment_arm="phase2_lean",
        max_model_calls=None,
        repair_headroom=2,
    )

    assert len(captured) == 6
    assert result["summary"]["configuration"]["base_model_call_estimate"] == 12
    assert result["summary"]["configuration"]["repair_headroom"] == 2
    assert result["summary"]["errors"] == []
