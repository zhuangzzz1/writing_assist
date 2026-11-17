import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from agents.assessment_coordinator import AssessmentCoordinator
from agents.prompts import (
    COORDINATOR_FINAL_PROMPT,
    PHASE1_COORDINATOR_FINAL_PROMPT,
    PHASE1_COORDINATOR_ROUND_PROMPT,
    PHASE1_PROMPT_VERSION,
    PHASE1_SCHEMA_VERSION,
    PHASE1_SUPPORT_FINAL_PROMPT,
    PHASE1_SUPPORT_ROUND_PROMPT,
    SUPPORT_FINAL_PROMPT,
)
from agents.support_agent import InstructionalSupportAgent
from agents.utils import DeepSeekClient
from langgraph_core.nodes import direct_response_node
from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.revision import build_revision_history, build_text_diff
from langgraph_core.state import make_review_state
from scripts.evaluate_v3 import phase1_diagnostics, run_mode
from storage.sqlite_storage import SQLiteStorage
from tests.helpers import (
    FakeClient,
    candidate_for,
    coordinator_payload,
    final_support_payload,
    issue_for,
    support_payload,
)
from ui.scenarios import (
    load_phase1_development_scenarios,
    load_phase1_transfer_scenarios,
)


ROOT = Path(__file__).resolve().parents[1]
PREVIOUS = "A claim.\n\nAn optional example. The survey says 24 of 40. A reason."
CURRENT = "A clearer claim.\n\nA reason."
REFERENCE = "A reason."


def phase1_state(*, revision=True, framework_components=None):
    selected = [candidate_for(issue_for(PREVIOUS, "An optional example."))]
    state = make_review_state(
        CURRENT if revision else PREVIOUS,
        "6th Grade",
        original_writing=PREVIOUS,
        previous_writing=PREVIOUS if revision else "",
        genre_selection="argument",
        assignment_prompt="Use the survey. Explain your choice.",
        teacher_directions="Include the class survey result. Explain your reason.",
        revision_number=1 if revision else 0,
        selected_goals=selected if revision else [],
        text_diff=build_text_diff(PREVIOUS, CURRENT) if revision else {},
    )
    if framework_components is not None:
        state["framework_name"] = "Custom"
        state["framework_components"] = framework_components
    return state


def observation(**overrides):
    value = {
        "goal_id": "goal_1",
        "status": "specific_improvement",
        "observation": "The selected goal has a bounded text observation.",
        "evidence_reference": REFERENCE,
        "goal_outcome": "fully_addressed",
        "narrowing": "none",
        "narrowing_evidence_reference": "",
        "requirement_source": "",
        "requirement_reference": "",
        "carry_forward": False,
    }
    value.update(overrides)
    return value


def apply_narrowing(value, narrowing):
    value["narrowing"] = narrowing
    if narrowing == "discretionary":
        value["narrowing_evidence_reference"] = "An optional example."
    elif narrowing == "required":
        value["narrowing_evidence_reference"] = "The survey says 24 of 40."
        value["requirement_source"] = "teacher_directions"
        value["requirement_reference"] = "Include the class survey result."
    return value


def current_issue(goal_id="goal_1", category="evidence_elaboration"):
    return issue_for(CURRENT, REFERENCE, goal_id, category=category)


def coordinator_raw(state, *, route="direct_response", issues=None, observations=None, polish=None, **overrides):
    return coordinator_payload(
        state,
        route=route,
        issues=issues or [],
        observations=observations or [],
        optional_polish=polish or [],
        **overrides,
    )


def validate_coordinator(state, raw):
    return AssessmentCoordinator(
        FakeClient([]), phase1_contract=True
    )._round_values(raw, state)


@pytest.mark.parametrize(
    ("outcome", "status", "narrowing", "carry_forward", "route"),
    [
        ("fully_addressed", "specific_improvement", "none", False, "direct_response"),
        ("partially_addressed", "specific_improvement", "none", True, "support_agent"),
        ("not_addressed", "improvement_not_yet_evident", "none", True, "support_agent"),
        ("uncertain", "uncertain", "none", True, "support_agent"),
        ("not_addressed", "specific_improvement", "discretionary", False, "direct_response"),
        ("not_addressed", "improvement_not_yet_evident", "discretionary", False, "direct_response"),
        ("partially_addressed", "specific_improvement", "discretionary", True, "support_agent"),
        ("partially_addressed", "specific_improvement", "required", True, "support_agent"),
        ("not_addressed", "improvement_not_yet_evident", "required", True, "support_agent"),
        ("not_addressed", "specific_improvement", "required", False, "support_agent"),
        ("uncertain", "uncertain", "discretionary", False, "direct_response"),
    ],
)
def test_phase1_permitted_observation_outcome_narrowing_route_matrix(
    outcome, status, narrowing, carry_forward, route
):
    state = phase1_state()
    item = observation(
        status=status,
        goal_outcome=outcome,
        carry_forward=carry_forward,
    )
    apply_narrowing(item, narrowing)
    issues = []
    if carry_forward:
        issues = [
            current_issue(
                category="task_alignment" if narrowing == "required" else "evidence_elaboration"
            )
        ]
    elif route == "support_agent":
        issues = [current_issue("goal_requirement", "task_alignment")]
    raw = coordinator_raw(
        state,
        route=route,
        issues=issues,
        observations=[item],
    )

    values = validate_coordinator(state, raw)

    assert values["routing_decision"] == route
    assert values["selected_goal_observations"][0]["goal_outcome"] == outcome
    assert values["selected_goal_observations"][0]["narrowing"] == narrowing
    assert values["selected_goal_observations"][0]["carry_forward"] is carry_forward


@pytest.mark.parametrize(
    "changes",
    [
        {"goal_outcome": "fully_addressed", "narrowing": "discretionary", "narrowing_evidence_reference": "An optional example."},
        {"goal_outcome": "fully_addressed", "carry_forward": True},
        {"goal_outcome": "fully_addressed", "status": "improvement_not_yet_evident"},
        {"goal_outcome": "partially_addressed", "carry_forward": False},
        {"goal_outcome": "partially_addressed", "status": "improvement_not_yet_evident", "carry_forward": True},
        {"goal_outcome": "not_addressed", "status": "specific_improvement", "carry_forward": True},
        {"goal_outcome": "not_addressed", "status": "improvement_not_yet_evident", "carry_forward": False},
        {"goal_outcome": "uncertain", "status": "specific_improvement", "carry_forward": True},
        {"goal_outcome": "uncertain", "status": "uncertain", "carry_forward": False},
        {"narrowing": "none", "narrowing_evidence_reference": "An optional example."},
        {"narrowing": "discretionary", "narrowing_evidence_reference": "An optional example.", "requirement_source": "framework"},
        {"narrowing": "required", "narrowing_evidence_reference": "The survey says 24 of 40."},
    ],
)
def test_phase1_rejects_inconsistent_observation_combinations(changes):
    state = phase1_state()
    item = observation(**changes)
    raw = coordinator_raw(state, observations=[item])

    with pytest.raises(ValueError):
        validate_coordinator(state, raw)


def test_phase1_carry_forward_requires_same_id_live_candidate():
    state = phase1_state()
    item = observation(
        status="improvement_not_yet_evident",
        goal_outcome="not_addressed",
        carry_forward=True,
    )
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue("different_goal")],
        observations=[item],
    )

    with pytest.raises(ValueError, match="same goal ID"):
        validate_coordinator(state, raw)


def test_phase1_fully_addressed_goal_cannot_be_recreated_as_live_issue():
    state = phase1_state()
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue()],
        observations=[observation()],
    )

    with pytest.raises(ValueError, match="fully addressed"):
        validate_coordinator(state, raw)


def test_phase1_partial_goal_requires_same_id_live_issue():
    state = phase1_state()
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue("different_goal")],
        observations=[item],
    )

    with pytest.raises(ValueError, match="same goal ID"):
        validate_coordinator(state, raw)


def test_phase1_direct_response_rejects_open_and_required_narrowing_goals():
    state = phase1_state()
    open_item = observation(
        status="improvement_not_yet_evident",
        goal_outcome="not_addressed",
        carry_forward=True,
    )
    with pytest.raises(ValueError):
        validate_coordinator(
            state, coordinator_raw(state, observations=[open_item])
        )

    required = observation(
        status="specific_improvement",
        goal_outcome="not_addressed",
        carry_forward=False,
    )
    apply_narrowing(required, "required")
    with pytest.raises(ValueError, match="Direct response"):
        validate_coordinator(state, coordinator_raw(state, observations=[required]))


@pytest.mark.parametrize("deleted", ["Missing text.", "A reason."])
def test_phase1_narrowing_evidence_must_be_deleted_previous_text(deleted):
    state = phase1_state()
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "discretionary")
    item["narrowing_evidence_reference"] = deleted
    raw = coordinator_raw(state, observations=[item])

    with pytest.raises(ValueError, match="previous-draft text absent"):
        validate_coordinator(state, raw)


def test_phase1_required_narrowing_requires_exact_requirement_reference():
    state = phase1_state()
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "required")
    item["requirement_reference"] = "Include every possible detail."
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue("goal_requirement", "task_alignment")],
        observations=[item],
    )

    with pytest.raises(ValueError, match="exactly quote"):
        validate_coordinator(state, raw)


def test_phase1_required_narrowing_needs_live_task_alignment_issue():
    state = phase1_state()
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "required")
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue("goal_other")],
        observations=[item],
    )

    with pytest.raises(ValueError, match="task-alignment"):
        validate_coordinator(state, raw)


def test_phase1_same_id_required_narrowing_issue_must_be_task_aligned():
    state = phase1_state()
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    apply_narrowing(item, "required")
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue()],
        observations=[item],
    )

    with pytest.raises(ValueError, match="task-alignment|task aligned"):
        validate_coordinator(state, raw)


def test_phase1_assignment_requirement_reference_is_supported():
    state = phase1_state()
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "required")
    item["requirement_source"] = "assignment_prompt"
    item["requirement_reference"] = "Use the survey."
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue("goal_requirement", "task_alignment")],
        observations=[item],
    )

    values = validate_coordinator(state, raw)

    assert values["selected_goal_observations"][0]["requirement_reference"] == "Use the survey."


def test_phase1_framework_narrowing_links_every_commissioned_component_to_live_issue():
    state = phase1_state(framework_components=["Survey evidence", "Reasoning"])
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    apply_narrowing(item, "required")
    item["requirement_source"] = "framework"
    item["requirement_reference"] = "Survey evidence"
    coverage = [
        {
            "framework": "Custom",
            "component": component,
            "status": "issue",
            "reference": "",
            "paragraph_number": None,
            "occurrence": None,
            "goal_id": "goal_1",
        }
        for component in state["framework_components"]
    ]
    raw = coordinator_raw(
        state,
        route="support_agent",
        issues=[current_issue(category="task_alignment")],
        observations=[item],
        framework_coverage=coverage,
    )

    values = validate_coordinator(state, raw)
    assert len(values["framework_coverage"]) == 2

    unlinked = json.loads(raw)
    unlinked["framework_coverage"][0]["status"] = "present"
    unlinked["framework_coverage"][0]["reference"] = REFERENCE
    unlinked["framework_coverage"][0]["paragraph_number"] = 2
    unlinked["framework_coverage"][0]["occurrence"] = 1
    unlinked["framework_coverage"][0]["goal_id"] = ""
    with pytest.raises(ValueError, match="must link coverage"):
        validate_coordinator(state, json.dumps(unlinked))


def polish(reference=REFERENCE, paragraph=2):
    return {
        "description": "You could make this wording more precise another day.",
        "draft_reference": reference,
        "paragraph_number": paragraph,
        "occurrence": 1,
    }


def test_phase1_optional_only_direct_response_has_validated_bounded_polish():
    state = phase1_state(revision=False)
    raw = coordinator_raw(state, polish=[polish()])

    values = validate_coordinator(state, raw)
    result = direct_response_node({**state, **values}, {})

    assert values["issues"] == []
    assert len(values["optional_polish"]) == 1
    assert result["revision_candidates"] == []
    assert "optional future polish" in result["student_output"]
    assert "required revisions" in result["student_output"]


def test_phase1_no_issue_direct_response_has_empty_optional_polish():
    state = phase1_state(revision=False)

    values = validate_coordinator(state, coordinator_raw(state))
    result = direct_response_node({**state, **values}, {})

    assert values["optional_polish"] == []
    assert "You can stop rather than changing" in result["student_output"]
    assert "Optional future polish" not in result["student_output"]


@pytest.mark.parametrize("route", ["support_agent", "ask_clarification"])
def test_phase1_optional_polish_is_rejected_outside_direct_response(route):
    state = phase1_state(revision=False)
    issues = [issue_for(state["writing"], REFERENCE)] if route == "support_agent" else []
    raw = coordinator_raw(state, route=route, issues=issues, polish=[polish()])

    with pytest.raises(ValueError, match="Optional polish|Boundary routes"):
        validate_coordinator(state, raw)


def test_phase1_teacher_safety_fallback_discards_optional_polish():
    state = phase1_state(revision=False)
    raw = coordinator_raw(state, route="teacher_review", polish=[polish()])

    values = validate_coordinator(state, raw)

    assert values["routing_decision"] == "teacher_review"
    assert values["flag_teacher"] is True
    assert values["optional_polish"] == []


def test_phase1_valid_teacher_override_clears_optional_polish_during_normalization():
    state = phase1_state(revision=False)
    raw = coordinator_raw(
        state,
        route="direct_response",
        polish=[polish()],
        flag_teacher=True,
        teacher_flag_category="concerning_content",
        teacher_flag_reason="The submission needs human review.",
    )

    values = validate_coordinator(state, raw)

    assert values["routing_decision"] == "teacher_review"
    assert values["optional_polish"] == []
    assert values["issues"] == []


def test_phase1_optional_polish_reference_must_be_exact():
    state = phase1_state(revision=False)
    raw = coordinator_raw(state, polish=[polish("Missing text.")])

    with pytest.raises(ValueError, match="Optional polish needs"):
        validate_coordinator(state, raw)


def test_phase1_unique_optional_polish_location_is_normalized_and_recorded():
    state = phase1_state(revision=False)
    raw = coordinator_raw(state, polish=[polish(REFERENCE, paragraph=1)])

    values = validate_coordinator(state, raw)

    assert values["optional_polish"][0]["paragraph_number"] == 2
    assert values["coordinator_optional_polish_normalizations"] == [
        {
            "optional_polish_index": 0,
            "previous_paragraph_number": 1,
            "previous_occurrence": 1,
            "paragraph_number": 2,
            "occurrence": 1,
        }
    ]


def test_phase1_ambiguous_optional_polish_location_requires_repair():
    state = phase1_state(revision=False)
    state["writing"] = f"{REFERENCE}\n\n{REFERENCE}"
    raw = coordinator_raw(state, polish=[polish(REFERENCE, paragraph=3)])

    with pytest.raises(ValueError, match="Optional polish needs"):
        validate_coordinator(state, raw)


def test_phase1_optional_polish_is_limited_to_three_entries():
    state = phase1_state(revision=False)
    raw = coordinator_raw(state, polish=[polish() for _ in range(4)])

    with pytest.raises(ValueError):
        validate_coordinator(state, raw)


def phase1_support_handoff():
    state = phase1_state()
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    issue = current_issue()
    assessment = validate_coordinator(
        state,
        coordinator_raw(
            state,
            route="support_agent",
            issues=[issue],
            observations=[item],
        ),
    )
    return {**state, **assessment}, item


def test_phase1_support_preserves_all_fields_and_only_paraphrases_observation():
    handoff, item = phase1_support_handoff()
    raw = json.loads(support_payload(handoff))
    raw["goal_feedback"] = [{**item, "observation": "You made one part clearer, and one part remains."}]

    result = InstructionalSupportAgent(
        FakeClient([]), phase1_contract=True
    )._round_values(json.dumps(raw), handoff)

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
        assert feedback[field] == item[field]
    assert "remaining work is still listed" in result["student_output"]


@pytest.mark.parametrize(
    ("field", "changed"),
    [
        ("status", "uncertain"),
        ("evidence_reference", "A clearer claim."),
        ("goal_outcome", "fully_addressed"),
        ("narrowing", "discretionary"),
        ("narrowing_evidence_reference", "An optional example."),
        ("requirement_source", "teacher_directions"),
        ("requirement_reference", "Include the class survey result."),
        ("carry_forward", False),
    ],
)
def test_phase1_support_cannot_change_verified_outcome_fields(field, changed):
    handoff, item = phase1_support_handoff()
    raw = json.loads(support_payload(handoff))
    feedback = dict(item)
    feedback[field] = changed
    raw["goal_feedback"] = [feedback]

    with pytest.raises(ValueError, match="Support cannot change"):
        InstructionalSupportAgent(
            FakeClient([]), phase1_contract=True
        )._round_values(json.dumps(raw), handoff)


def test_phase1_direct_response_bypasses_support_without_dropping_outcome_fields():
    state = phase1_state()
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "discretionary")
    values = validate_coordinator(
        state, coordinator_raw(state, observations=[item])
    )

    result = direct_response_node({**state, **values}, {})

    assert result["goal_feedback"] == [item]
    assert result["revision_candidates"] == []


def test_phase1_neutral_ui_labels_cover_support_and_direct_response_fields():
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    apply_narrowing(item, "required")
    script = f"""
import streamlit as st
from ui.components import render_goal_feedback
render_goal_feedback({repr([item])}, {repr([{"goal_id": "goal_1", "title": "Use the survey"}])})
"""
    app = AppTest.from_string(script).run()

    assert not app.exception
    text = "\n".join(element.value for element in [*app.markdown, *app.caption])
    assert "Partially addressed" in text
    assert "Required narrowing" in text
    assert "The survey says 24 of 40." in text
    assert "Include the class survey result." in text
    assert "another improvement does not erase it" in text


def test_phase1_fully_addressed_ui_is_bounded_to_selected_goal_not_mastery():
    item = observation()
    script = f"""
import streamlit as st
from ui.components import render_goal_feedback
render_goal_feedback({repr([item])}, [])
"""
    app = AppTest.from_string(script).run()

    text = "\n".join(element.value for element in [*app.markdown, *app.caption])
    assert "Fully addressed for this selected goal in this draft" in text
    assert "not a claim of overall mastery" in text


def test_phase1_discretionary_ui_does_not_call_narrowing_a_solved_goal():
    item = observation(goal_outcome="not_addressed", carry_forward=False)
    apply_narrowing(item, "discretionary")
    script = f"""
import streamlit as st
from ui.components import render_goal_feedback
render_goal_feedback({repr([item])}, [])
"""
    app = AppTest.from_string(script).run()

    text = "\n".join(element.value for element in [*app.markdown, *app.caption])
    assert "not the same as solving the original goal" in text
    assert "original target no longer applies" in text


def test_phase1_round_state_and_revision_history_survive_reopen(tmp_path):
    database = str(tmp_path / "phase1.db")
    storage = SQLiteStorage(database)
    initial = phase1_state(revision=False)
    initial.update(
        {
            "composition_id": "composition",
            "round_id": "round-0",
            "thread_id": "thread-0",
        }
    )
    storage.create_composition("session", initial, "snapshot-0")
    revision = phase1_state()
    revision.update(
        {
            "composition_id": "composition",
            "round_id": "round-1",
            "thread_id": "thread-1",
        }
    )
    storage.create_revision("session", revision, "snapshot-1")
    item = observation(goal_outcome="partially_addressed", carry_forward=True)
    apply_narrowing(item, "required")
    saved = {
        **revision,
        "routing_decision": "support_agent",
        "selected_goal_observations": [item],
        "goal_feedback": [item],
        "issues": [current_issue(category="task_alignment")],
        "revision_candidates": [candidate_for(current_issue(category="task_alignment"))],
        "optional_polish": [],
    }
    storage.save_round_result("thread-1", saved, False, 12)

    reopened = SQLiteStorage(database)
    round_record = reopened.get_round("round-1")
    assert round_record.state["selected_goal_observations"] == [item]
    history = build_revision_history(
        reopened.list_snapshots("composition"), reopened.list_rounds("composition")
    )
    goal = history[0]["selected_goals"][0]
    for field in (
        "goal_outcome",
        "narrowing",
        "narrowing_evidence_reference",
        "requirement_source",
        "requirement_reference",
    ):
        assert goal[field] == item[field]


def test_phase1_carry_forward_does_not_auto_select_next_goal():
    handoff, _ = phase1_support_handoff()
    previous_selection = list(handoff["selected_goals"])
    raw = json.loads(support_payload(handoff))
    raw["goal_feedback"] = handoff["selected_goal_observations"]
    result = InstructionalSupportAgent(
        FakeClient([]), phase1_contract=True
    )._round_values(json.dumps(raw), handoff)

    assert result["revision_candidates"][0]["goal_id"] == "goal_1"
    assert handoff["selected_goals"] == previous_selection
    assert "next_selected_goals" not in result


def test_phase1_history_leaves_legacy_outcomes_unknown():
    snapshots = [
        SimpleNamespace(revision_number=0, snapshot_id="s0", writing=PREVIOUS, selected_goals=[]),
        SimpleNamespace(
            revision_number=1,
            snapshot_id="s1",
            writing=CURRENT,
            selected_goals=[candidate_for(issue_for(PREVIOUS, "An optional example."))],
        ),
    ]
    rounds = [
        SimpleNamespace(
            revision_number=1,
            round_id="r1",
            status="completed",
            state={
                "writing": CURRENT,
                "routing_decision": "direct_response",
                "selected_goal_observations": [
                    {
                        "goal_id": "goal_1",
                        "status": "specific_improvement",
                        "observation": "Legacy observation.",
                        "carry_forward": False,
                    }
                ],
            },
        )
    ]

    goal = build_revision_history(snapshots, rounds)[0]["selected_goals"][0]

    assert "goal_outcome" not in goal
    assert "narrowing" not in goal
    assert "requirement_reference" not in goal


def test_phase1_evaluator_selector_uses_candidate_versions_and_prompts(tmp_path, monkeypatch):
    scenarios = load_phase1_development_scenarios()
    scenario = scenarios[0]
    state = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        assignment_prompt=scenario.assignment_prompt,
        teacher_directions=scenario.teacher_directions,
        source_material=scenario.source_material,
    )
    client = FakeClient([coordinator_raw(state)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261117T000000Z",
        "phase1_development",
        scenario_number=1,
        experiment_arm="phase1",
        max_model_calls=2,
    )

    configuration = result["summary"]["configuration"]
    assert configuration["prompt_version"] == PHASE1_PROMPT_VERSION
    assert configuration["schema_version"] == PHASE1_SCHEMA_VERSION
    assert client.calls[0][0][0]["content"] == PHASE1_COORDINATOR_ROUND_PROMPT
    assert result["records"][0]["review_annotations"]
    assert result["summary"]["errors"] == []


def test_phase1_service_flow_uses_all_candidate_prompts_and_preserves_final_handoff(tmp_path):
    initial = phase1_state(revision=False)
    initial.update(
        {
            "composition_id": "phase1-composition",
            "round_id": "initial-round",
            "thread_id": "initial-thread",
        }
    )
    initial_issue = issue_for(initial["writing"], "A claim.")
    initial_handoff = {
        **initial,
        "issues": [initial_issue],
        "selected_goal_observations": [],
        "source_limitations": [],
    }
    selected = [candidate_for(initial_issue)]
    revision = make_review_state(
        CURRENT,
        "6th Grade",
        composition_id=initial["composition_id"],
        round_id="revision-round",
        thread_id="revision-thread",
        original_writing=PREVIOUS,
        previous_writing=PREVIOUS,
        genre_selection="argument",
        assignment_prompt=initial["assignment_prompt"],
        teacher_directions=initial["teacher_directions"],
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(PREVIOUS, CURRENT),
    )
    final = make_review_state(
        CURRENT,
        "6th Grade",
        composition_id=initial["composition_id"],
        round_id="final-round",
        thread_id="final-thread",
        review_mode="final",
        original_writing=PREVIOUS,
        genre_selection="argument",
        assignment_prompt=initial["assignment_prompt"],
        teacher_directions=initial["teacher_directions"],
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(PREVIOUS, CURRENT),
    )
    final["working_genre"] = "argument"
    improvement = {
        "finding_id": "improvement_1",
        "summary": "The revised claim is more specific.",
        "original_reference": "A claim.",
        "final_reference": "A clearer claim.",
        "goal_id": "goal_1",
    }
    client = FakeClient(
        [
            coordinator_raw(initial, route="support_agent", issues=[initial_issue]),
            support_payload(initial_handoff),
            coordinator_raw(
                revision,
                route="direct_response",
                observations=[observation()],
            ),
            json.dumps(
                {
                    "original_strengths": ["The original states a claim."],
                    "improvements": [improvement],
                    "regressions": [],
                    "future_areas": [],
                    "coordinator_reasoning": "The exact changed reference supports the finding.",
                }
            ),
            final_support_payload(
                {
                    **final,
                    "comparison_improvements": [improvement],
                    "comparison_regressions": [],
                }
            ),
        ]
    )
    service = create_writing_assistant_service(
        client,
        str(tmp_path / "phase1-flow.db"),
        coordinator=AssessmentCoordinator(
            client,
            round_prompt=PHASE1_COORDINATOR_ROUND_PROMPT,
            final_prompt=PHASE1_COORDINATOR_FINAL_PROMPT,
            phase1_contract=True,
        ),
        support_agent=InstructionalSupportAgent(
            client,
            round_prompt=PHASE1_SUPPORT_ROUND_PROMPT,
            final_prompt=PHASE1_SUPPORT_FINAL_PROMPT,
            phase1_contract=True,
        ),
    )

    first = service.start_composition("session", initial, "snapshot-0")
    revised = service.submit_revision("session", revision, "snapshot-1")
    reflection = service.finish_composition(
        "session", final, "snapshot-0", "snapshot-1"
    )

    assert first.state["revision_candidates"][0]["goal_id"] == "goal_1"
    assert revised.state["goal_feedback"][0]["goal_outcome"] == "fully_addressed"
    assert reflection.state["final_reflection"]["improvements"][0]["finding_id"] == (
        "improvement_1"
    )
    assert client.responses == []
    assert [call[0][0]["content"] for call in client.calls] == [
        PHASE1_COORDINATOR_ROUND_PROMPT,
        PHASE1_SUPPORT_ROUND_PROMPT,
        PHASE1_COORDINATOR_ROUND_PROMPT,
        PHASE1_COORDINATOR_FINAL_PROMPT,
        PHASE1_SUPPORT_FINAL_PROMPT,
    ]


def test_phase1_diagnostics_describe_outcomes_without_quality_scores():
    records = [
        {
            "initial_state": {
                "routing_decision": "direct_response",
                "optional_polish": [polish()],
                "execution_logs": [{"node": "assessment_coordinator"}],
            },
            "revision_states": [
                {
                    "routing_decision": "support_agent",
                    "execution_logs": [{"node": "assessment_coordinator"}],
                    "goal_feedback": [
                        observation(
                            goal_outcome="partially_addressed",
                            carry_forward=True,
                        )
                    ],
                }
            ],
        },
        {
            "initial_state": {
                "routing_decision": "support_agent",
                "execution_logs": [],
            },
            "revision_states": [],
        },
    ]

    result = phase1_diagnostics(records)

    assert result["goal_outcome_counts"] == {"partially_addressed": 1}
    assert result["narrowing_counts"] == {"none": 1}
    assert result["carry_forward_counts"]["true"] == 1
    assert result["stopping_or_support_route_counts"] == {
        "no_meaningful_issue": 0,
        "optional_only": 1,
        "work_remaining": 1,
    }
    assert result["optional_polish_entry_count"] == 1
    assert "quality_score" not in json.dumps(result)


def test_phase1_evaluator_can_explicitly_skip_final_for_round_regression(tmp_path, monkeypatch):
    client = FakeClient([])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )
    captured = []
    captured_final_prompts = []

    def fake_run(service, session_id, scenario):
        captured.append(scenario.finish)
        captured_final_prompts.append(service.support_agent.final_prompt)
        return {
            "scenario_id": scenario.scenario_id,
            "fixture_version": scenario.fixture_version,
            "initial_state": {},
        }

    monkeypatch.setattr("scripts.evaluate_v3.run_scenario", fake_run)
    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261117T000001Z",
        "acceptance",
        scenario_number=1,
        experiment_arm="phase1",
        max_model_calls=2,
        skip_final=True,
    )

    assert captured == [False]
    assert captured_final_prompts == [PHASE1_SUPPORT_FINAL_PROMPT]
    assert result["summary"]["errors"] == []


def test_phase1_candidate_is_consolidated_without_changing_default_final_prompts():
    assert PHASE1_COORDINATOR_FINAL_PROMPT != COORDINATOR_FINAL_PROMPT
    assert PHASE1_SUPPORT_FINAL_PROMPT != SUPPORT_FINAL_PROMPT
    assert PHASE1_PROMPT_VERSION == "v3.9.5-phase1"
    assert PHASE1_SCHEMA_VERSION == "v3.9.0"
    for prompt in (PHASE1_COORDINATOR_ROUND_PROMPT, PHASE1_SUPPORT_ROUND_PROMPT):
        assert prompt.count("Return only one valid JSON object") == 1
        assert "replaces any conflicting" not in prompt
        assert "| empty" not in prompt
    assert "scope_narrowed" not in PHASE1_COORDINATOR_ROUND_PROMPT.split(
        "never use scope_narrowed", 1
    )[-1]
    assert "five-issue maximum" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "Selected-goal completion" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "Required-deletion audit" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "normal student-facing target is one to three issues" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "UNATTRIBUTED CLAIMS AND OPENING HOOKS" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "Absence from the source is not proof" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "REVISION STUDENT-CONCERN RECHECK" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "A different selected goal does not satisfy" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "fourth or fifth issue is permitted only" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "stuck_step must not supply a sentence opening" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "partially_addressed always requires" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "using goal_outcome=not_addressed or uncertain" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "coordinator_rationale only as background context" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "Permitted ELD connector support" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "minor, non-obscuring spelling" in PHASE1_COORDINATOR_FINAL_PROMPT
    assert "never mention, praise, or criticize edits from text_diff" in PHASE1_SUPPORT_FINAL_PROMPT
    assert "Independently complete the clarity/reasoning" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "stopping with fewer than five issues" not in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "mandatory multi-paragraph checklist" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "regular and irregular third-person forms may share" in PHASE1_COORDINATOR_ROUND_PROMPT
    assert "never exceed five items" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "same writing move and passage scope" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "same passage scope as revision_action and self_check" in PHASE1_SUPPORT_ROUND_PROMPT
    assert "regular suffix patterns from irregular forms" in PHASE1_SUPPORT_ROUND_PROMPT
    for prompt in (PHASE1_COORDINATOR_ROUND_PROMPT, PHASE1_SUPPORT_ROUND_PROMPT):
        assert "equips" not in prompt

    schema = PHASE1_COORDINATOR_ROUND_PROMPT.split("7. OUTPUT SCHEMA", 1)[1]
    assert schema.index('"flag_teacher"') < schema.index('"routing_decision"')
    assert schema.index('"routing_decision"') < schema.index('"selected_goal_observations"')
    assert schema.index('"selected_goal_observations"') < schema.index('"issues"')


@pytest.mark.parametrize(
    ("name", "prompt"),
    [
        ("coordinator_round", PHASE1_COORDINATOR_ROUND_PROMPT),
        ("support_round", PHASE1_SUPPORT_ROUND_PROMPT),
        ("coordinator_final", PHASE1_COORDINATOR_FINAL_PROMPT),
        ("support_final", PHASE1_SUPPORT_FINAL_PROMPT),
    ],
)
def test_phase1_prompt_output_example_is_valid_json(name, prompt):
    start = prompt.rindex("\n{\n") + 1
    end = prompt.rindex("\n}") + 2

    value = json.loads(prompt[start:end])

    assert isinstance(value, dict), name
    assert value, name


def test_phase1_fixture_sets_are_versioned_complete_and_reserved():
    development = load_phase1_development_scenarios()
    transfer = load_phase1_transfer_scenarios()

    assert len(development) == 16
    assert len(transfer) == 8
    assert all(item.fixture_version == "v3.9.0-phase1-development.2" for item in development)
    assert all(item.fixture_version == "v3.9.0-phase1-transfer.1" for item in transfer)
    assert all(item.review_annotations for item in [*development, *transfer])
    for filename in ("phase1_development.json", "phase1_transfer.json"):
        metadata = json.loads((ROOT / "test_cases/v3" / filename).read_text())
        assert metadata["candidate_prompt_version"] == PHASE1_PROMPT_VERSION
        assert metadata["candidate_schema_version"] == PHASE1_SCHEMA_VERSION
    assert all(not item.lineage["historical_control_available"] for item in transfer)
    ids = {item.scenario_id for item in development}
    assert "phase1_garbage_transport_discretionary" in ids
    assert "phase1_garbage_partial_agreement_4" in ids
    assert "phase1_garbage_partial_agreement_6" in ids
    assert "phase1_garbage_snapshot_7_initial_probe" in ids
    by_id = {item.scenario_id: item for item in development}
    assert "distance trash travels" in by_id[
        "phase1_garbage_transport_discretionary"
    ].controlled_round["revision_candidates"][0]["revision_action"]
    partial_six = by_id[
        "phase1_garbage_partial_agreement_6"
    ].controlled_round["revision_candidates"][0]["revision_action"]
    assert "burning-system paragraph" in partial_six
    assert "bury-station paragraph" in partial_six
    for scenario in [*development, *transfer]:
        previous = scenario.draft
        for revision in scenario.revisions:
            assert revision.draft.strip()
            for reference in revision.goal_references:
                assert reference in previous
            previous = revision.draft


def test_phase1_counterfactuals_remove_targeted_supporting_text():
    data = json.loads((ROOT / "test_cases/v3/phase1_development.json").read_text())
    snapshots = data["snapshots"]
    boundaries = snapshots["garbage_boundaries_corrected"]
    references = snapshots["garbage_references_corrected"]
    assert "system ,in the present" not in boundaries
    assert "system, I hope" not in boundaries
    assert "the volume of it" not in references
    assert "robots will change them" not in references
    assert "Lechate being collected" not in references


def test_phase1_distinctive_fixture_vocabulary_does_not_leak_into_runtime():
    production_paths = [
        ROOT / "agents/prompts.py",
        ROOT / "agents/assessment_coordinator.py",
        ROOT / "agents/support_agent.py",
        ROOT / "langgraph_core/nodes.py",
        ROOT / "langgraph_core/routing.py",
        ROOT / "langgraph_core/revision.py",
        ROOT / "langgraph_core/graph.py",
        ROOT / "ui/components.py",
        ROOT / "ui/layout.py",
        ROOT / "ui/editor.py",
    ]
    distinctive_terms = [
        "Super Garbage Dealing System",
        "dewater station",
        "Lechate being collected",
        "quiet lunch table",
        "grandma's old clock",
        "Rainwater Helper",
        "Yellow Umbrella",
        "This proves that opening early would raise grades",
    ]
    leaked = {
        str(path.relative_to(ROOT)): term
        for path in production_paths
        for term in distinctive_terms
        if term.lower() in path.read_text(encoding="utf-8").lower()
    }

    assert leaked == {}
