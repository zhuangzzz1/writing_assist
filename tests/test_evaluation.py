import json

from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from scripts.evaluate_v3 import (
    collect_states,
    repair_diagnostics_for_record,
    repair_diagnostics_for_state,
    run_scenario,
    select_goals,
    summarize,
)
from tests.helpers import (
    FakeClient,
    candidate_for,
    coordinator_payload,
    final_coordinator_payload,
    final_support_payload,
    issue_for,
    observation_for,
    support_payload,
)
from ui.scenarios import RevisionFixture, get_acceptance_scenario


def candidate(goal_id):
    return candidate_for(issue_for("A claim.\n\nA reason.", "A reason.", goal_id))


def test_repair_diagnostics_capture_invalid_final_response_and_validation_error_only():
    state = {
        "model_config": {"prompt_version": "v3.2.0", "schema_version": "v3.2.1"},
        "execution_logs": [
            {
                "display_name": "Assessment Coordinator",
                "node": "assessment_coordinator",
                "timestamp": 123.0,
                "model_calls": [
                    {"token_usage": {"total_tokens": 10}},
                    {
                        "schema_repair": True,
                        "latency_ms": 25,
                        "token_usage": {"total_tokens": 20},
                    },
                ],
                "raw_responses": ["invalid final JSON", "valid repaired JSON"],
                "prompt": [
                    {"role": "system", "content": "Rules"},
                    {
                        "role": "user",
                        "content": "Correct the response. Validation error: missing exact reference",
                    },
                ],
            }
        ],
    }

    diagnostics = repair_diagnostics_for_state(state, "scenario-test")

    assert diagnostics[0]["invalid_final_response"] == "invalid final JSON"
    assert diagnostics[0]["validation_error"] == "missing exact reference"
    assert diagnostics[0]["repair_metadata"]["latency_ms"] == 25
    assert "valid repaired JSON" not in json.dumps(diagnostics)
    assert "reasoning_content" not in json.dumps(diagnostics)


def test_first_goal_and_three_goal_selection_with_self_report_plans():
    candidates = [candidate("goal_1"), candidate("goal_2"), candidate("goal_3")]
    state = {"revision_candidates": candidates}

    first, first_reports = select_goals(
        state,
        RevisionFixture("First revision", "first", {"first": "attempted"}),
    )
    three, three_reports = select_goals(
        state,
        RevisionFixture(
            "Three-goal revision",
            "three",
            {"first": "attempted", "others": "deferred"},
        ),
    )

    assert first == [candidates[0]]
    assert first_reports == {"goal_1": "attempted"}
    assert three == candidates
    assert three_reports == {
        "goal_1": "attempted",
        "goal_2": "deferred",
        "goal_3": "deferred",
    }


def test_all_selected_goals_can_share_one_attempted_self_report():
    candidates = [candidate("goal_1"), candidate("goal_2"), candidate("goal_3")]

    selected, reports = select_goals(
        {"revision_candidates": candidates},
        RevisionFixture("Revision", "three", {"all": "attempted"}),
    )

    assert len(selected) == 3
    assert set(reports.values()) == {"attempted"}


def test_summary_separates_model_graph_and_service_time_and_collects_diagnostics():
    state = {
        "model_config": {},
        "revision_candidates": [],
        "execution_logs": [
            {
                "display_name": "Assessment Coordinator",
                "model_calls": [
                    {
                        "latency_ms": 50,
                        "token_usage": {
                            "prompt_tokens": 20,
                            "completion_tokens": 30,
                            "total_tokens": 50,
                            "reasoning_tokens": 10,
                        },
                    }
                ],
            }
        ],
    }
    record = {
        "scenario_id": "timing-test",
        "initial_state": state,
        "initial_review": {
            "graph_duration_ms": 70,
            "service_duration_ms": 90,
        },
        "repair_diagnostics": [{"validation_error": "example"}],
    }

    result = summarize(
        "nonthinking", FakeClient([]), [record], "acceptance"
    )

    assert result["total_recorded_model_latency_ms"] == 50
    assert result["total_graph_invocation_ms"] == 70
    assert result["total_service_ms"] == 90
    assert result["estimated_final_response_tokens"] == 20
    assert result["repair_diagnostics"][0]["validation_error"] == "example"
    assert result["observations"][0]["scenario_id"] == "timing-test"


def test_collect_states_includes_all_workflow_stages():
    record = {
        "initial_state": {"stage": "initial"},
        "clarification_states": [{"stage": "clarification"}],
        "genre_correction_state": {"stage": "correction"},
        "revision_states": [{"stage": "revision"}],
        "final_state": {"stage": "final"},
    }

    assert [state["stage"] for state in collect_states(record)] == [
        "initial",
        "correction",
        "final",
        "clarification",
        "revision",
    ]


def test_runner_preserves_full_revision_and_final_workflow(tmp_path):
    scenario = get_acceptance_scenario(1)
    reference = "This result shows that some students are interested in fresh food."
    initial = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        source_material=scenario.source_material,
    )
    initial_issue = issue_for(scenario.draft, reference)
    initial_coordinator = coordinator_payload(initial, issues=[initial_issue])
    initial_support = support_payload({**initial, **json.loads(initial_coordinator)})
    revised = scenario.revisions[0].draft
    selected = candidate_for(initial_issue)
    revision = make_review_state(
        revised,
        scenario.grade_level,
        original_writing=scenario.draft,
        previous_writing=scenario.draft,
        source_material=scenario.source_material,
        revision_number=1,
        selected_goals=[selected],
        text_diff=build_text_diff(scenario.draft, revised),
    )
    observation = observation_for(status="improvement_not_yet_evident")
    revision_issue = issue_for(revised, reference)
    revision_coordinator = coordinator_payload(
        revision,
        issues=[revision_issue],
        observations=[observation],
    )
    revision_support = support_payload(
        {**revision, **json.loads(revision_coordinator)}
    )
    final = make_review_state(
        revised,
        scenario.grade_level,
        review_mode="final",
        original_writing=scenario.draft,
        revision_number=1,
        text_diff=build_text_diff(scenario.draft, revised),
    )
    final_coordinator = json.loads(final_coordinator_payload(final))
    final_coordinator["improvements"][0].update(
        {
            "summary": "The final responsibility explanation is more specific.",
            "original_reference": "This would help them become better citizens.",
            "final_reference": "When students care for plants without being reminded, they practice noticing shared responsibilities.",
        }
    )
    final_handoff = {
        **final,
        "original_strengths": final_coordinator["original_strengths"],
        "comparison_improvements": final_coordinator["improvements"],
        "comparison_regressions": [],
        "future_areas": final_coordinator["future_areas"],
    }
    client = FakeClient(
        [
            initial_coordinator,
            initial_support,
            revision_coordinator,
            revision_support,
            json.dumps(final_coordinator),
            final_support_payload(final_handoff),
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "runner.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert len(record["revision_states"]) == 1
    assert record["final_state"]["final_reflection"]["improvements"]
    assert record["initial_review"]["service_duration_ms"] is not None
    assert record["revision_reviews"][0]["service_duration_ms"] is not None
    assert record["final_review"]["service_duration_ms"] is not None
    assert record["repair_diagnostics"] == []


def test_runner_applies_genre_correction_without_another_snapshot(tmp_path):
    scenario = get_acceptance_scenario(6)
    initial = make_review_state(
        scenario.draft, scenario.grade_level, genre_selection="auto"
    )
    reference = "Right now, readers have to sit at their desks."
    initial_coordinator = coordinator_payload(
        initial, issues=[issue_for(initial["writing"], reference)]
    )
    corrected = make_review_state(
        scenario.draft, scenario.grade_level, genre_selection="narrative"
    )
    corrected_coordinator = coordinator_payload(
        corrected,
        working_genre="narrative",
        issues=[issue_for(corrected["writing"], reference)],
    )
    client = FakeClient(
        [
            initial_coordinator,
            support_payload({**initial, **json.loads(initial_coordinator)}),
            corrected_coordinator,
            support_payload({**corrected, **json.loads(corrected_coordinator)}),
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "runner.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert record["genre_correction_state"]["working_genre"] == "narrative"
    assert len(service.storage.list_snapshots(record["initial_state"]["composition_id"])) == 1


def test_runner_reaches_clarification_limit_after_two_unclear_answers(tmp_path):
    scenario = get_acceptance_scenario(30)
    state = make_review_state(scenario.draft, scenario.grade_level)
    client = FakeClient(
        [coordinator_payload(state, route="ask_clarification") for _ in range(3)]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "runner.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert len(record["clarification_states"]) == 2
    final_state = record["clarification_states"][-1]
    assert final_state["routing_decision"] == "teacher_review"
    assert final_state["teacher_flag_category"] == "clarification_limit"
    assert len(client.calls) == 3

    summary = summarize("nonthinking", client, [record], "acceptance")

    assert summary["model_call_count"] == 3
    assert summary["token_usage"]["total_tokens"] == 90
    assert summary["total_graph_invocation_ms"] == record["clarification_reviews"][-1][
        "graph_duration_ms"
    ]


def test_repair_diagnostics_do_not_duplicate_resumed_thread_history():
    log = {
        "display_name": "Assessment Coordinator",
        "node": "assessment_coordinator",
        "timestamp": 123.0,
        "model_calls": [
            {"token_usage": {"total_tokens": 10}},
            {"schema_repair": True, "token_usage": {"total_tokens": 20}},
        ],
        "raw_responses": ["invalid", "valid"],
        "prompt": [
            {
                "role": "user",
                "content": "Correct it. Validation error: invalid reference",
            }
        ],
    }
    state = {
        "thread_id": "same-thread",
        "model_config": {},
        "execution_logs": [log],
    }
    record = {
        "scenario_id": "scenario-test",
        "initial_state": state,
        "clarification_states": [{**state, "execution_logs": [dict(log)]}],
    }

    diagnostics = repair_diagnostics_for_record(record)

    assert len(diagnostics) == 1
    assert diagnostics[0]["invalid_final_response"] == "invalid"
