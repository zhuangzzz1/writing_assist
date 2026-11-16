import json
import sqlite3

import pytest

from agents.assessment_coordinator import AssessmentCoordinator
from agents.prompts import (
    BASELINE_READABLE_PROMPT_VERSION,
    BASELINE_READABLE_SUPPORT_PROMPT,
    BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT,
    BASELINE_READABLE_V2_COORDINATOR_ROUND_PROMPT,
    BASELINE_READABLE_V2_PROMPT_VERSION,
    BASELINE_READABLE_V2_SUPPORT_PROMPT,
    CONSOLIDATED_SUPPORT_PROMPT_VERSION,
    REGRESSION_READABLE_COORDINATOR_FINAL_PROMPT,
    REGRESSION_READABLE_COORDINATOR_ROUND_PROMPT,
    REGRESSION_READABLE_PROMPT_VERSION,
    REGRESSION_READABLE_SUPPORT_PROMPT,
    STRUCTURAL_SUPPORT_ROUND_PROMPT,
    SUPPORT_ROUND_CONSOLIDATED_PROMPT,
    V3_7_1_SUPPORT_ROUND_PROMPT,
)
from agents.utils import DeepSeekClient
from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.revision import build_text_diff, draft_sha256
from langgraph_core.state import make_review_state
from scripts.readability_metrics import readability_metrics, record_readability
from scripts.evaluate_v3 import (
    collect_states,
    database_integrity,
    finalize_database,
    repair_diagnostics_for_record,
    BudgetedClient,
    EvaluationBudgetExceeded,
    repair_diagnostics_for_state,
    run_mode,
    run_scenario,
    run_support_scenario,
    scenario_state,
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
from ui.scenarios import (
    RevisionFixture,
    get_acceptance_scenario,
    get_experiment_scenario,
    load_coordinator_targeted_scenarios,
    load_final_history_scenarios,
    load_final_regression_scenarios,
    load_readability_coverage_scenarios,
    load_support_comparison_scenarios,
)


def candidate(goal_id, **overrides):
    return candidate_for(
        issue_for("A claim.\n\nA reason.", "A reason.", goal_id), **overrides
    )


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


def test_all_available_selects_up_to_three_actual_candidates_with_existing_report_plan():
    candidates = [
        candidate("goal_1"),
        candidate("goal_2", draft_reference="A second reason."),
        candidate("goal_3", draft_reference="A third reason."),
        candidate("goal_4", draft_reference="A fourth reason."),
    ]

    selected, reports = select_goals(
        {"revision_candidates": candidates},
        RevisionFixture(
            "Revision",
            "all_available",
            {"first": "attempted", "others": "deferred"},
        ),
    )

    assert selected == candidates[:3]
    assert reports == {
        "goal_1": "attempted",
        "goal_2": "deferred",
        "goal_3": "deferred",
    }

    two_selected, two_reports = select_goals(
        {"revision_candidates": candidates[:2]},
        RevisionFixture(
            "Revision",
            "all_available",
            {"first": "attempted", "others": "deferred"},
        ),
    )
    assert two_selected == candidates[:2]
    assert two_reports == {"goal_1": "attempted", "goal_2": "deferred"}


def test_all_selected_goals_can_share_one_attempted_self_report():
    candidates = [candidate("goal_1"), candidate("goal_2"), candidate("goal_3")]

    selected, reports = select_goals(
        {"revision_candidates": candidates},
        RevisionFixture("Revision", "three", {"all": "attempted"}),
    )

    assert len(selected) == 3
    assert set(reports.values()) == {"attempted"}


def test_explicit_goal_indices_and_references_select_the_intended_subset():
    candidates = [
        candidate("goal_1"),
        candidate("goal_2", draft_reference="A second reason."),
        candidate("goal_3", draft_reference="A third reason."),
    ]
    state = {"revision_candidates": candidates}

    by_index, index_reports = select_goals(
        state,
        RevisionFixture(
            "Revision",
            "explicit",
            {"first": "attempted", "others": "deferred"},
            goal_indices=(3, 1),
        ),
    )
    by_reference, _ = select_goals(
        state,
        RevisionFixture(
            "Revision",
            "explicit",
            {},
            goal_references=(
                candidates[2]["draft_reference"],
                candidates[0]["draft_reference"],
            ),
        ),
    )

    assert by_index == [candidates[2], candidates[0]]
    assert by_reference == by_index
    assert index_reports == {"goal_3": "attempted", "goal_1": "deferred"}


@pytest.mark.parametrize(
    "revision",
    [
        RevisionFixture("Revision", "explicit", {}, goal_indices=(1, 1)),
        RevisionFixture("Revision", "explicit", {}, goal_indices=(0,)),
        RevisionFixture("Revision", "explicit", {}, goal_indices=(4,)),
        RevisionFixture("Revision", "explicit", {}, goal_indices=(1, 2, 3, 4)),
        RevisionFixture("Revision", "explicit", {}, goal_references=("missing",)),
        RevisionFixture(
            "Revision", "explicit", {}, goal_indices=(1,), goal_references=("A reason.",)
        ),
        RevisionFixture("Revision", "all_available", {}, goal_indices=(1,)),
        RevisionFixture("Revision", "other", {}),
    ],
)
def test_invalid_explicit_goal_selection_fails_without_fallback(revision):
    candidates = [candidate("goal_1"), candidate("goal_2"), candidate("goal_3")]

    with pytest.raises(ValueError):
        select_goals({"revision_candidates": candidates}, revision)


def test_summary_separates_model_graph_and_service_time_and_collects_diagnostics():
    state = {
        "model_config": {},
        "revision_candidates": [],
        "execution_logs": [
            {
                "display_name": "Assessment Coordinator",
                "state_changes": {
                    "coordinator_reference_normalizations": [{"goal_id": "goal_1"}],
                    "coordinator_framework_normalizations": [
                        {"framework": "CER", "component": "Claim"}
                    ],
                },
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
    assert result["reference_normalization_counts"] == {
        "issue": 1,
        "framework_present": 1,
    }
    assert result["repair_diagnostics"][0]["validation_error"] == "example"
    assert result["observations"][0]["scenario_id"] == "timing-test"


def test_readability_metrics_report_sentence_lengths_and_long_action_heuristic():
    item = candidate("goal_1")
    item["why_it_matters"] = "Readers need context. Why does this help?"
    item["revision_action"] = "Find the reason. Explain your connection."
    item["hint"]["steps"] = ["Find the exact reason.", "Write one short explanation."]
    item["stuck_step"] = "Name one link."

    result = readability_metrics([item])

    assert result["field_sentence_words"]["why_it_matters"] == {
        "sentence_count": 2,
        "word_count": 7,
        "mean_words_per_sentence": 3.5,
        "max_words_per_sentence": 4,
    }
    assert result["field_sentence_words"]["revision_action"]["mean_words_per_sentence"] == 3
    assert result["field_sentence_words"]["hint_steps"]["max_words_per_sentence"] == 4
    assert result["long_actions"]["count"] == 0

    item["revision_action"] = " ".join(f"word{index}" for index in range(39))
    result = readability_metrics([item])
    assert result["long_actions"]["count"] == 1
    assert result["long_actions"]["goal_ids"] == ["goal_1"]


def test_readability_metrics_flag_repetition_and_scope_for_human_review_only():
    item = candidate("goal_1")
    item["revision_action"] = "Explain how the 62% result supports your claim."
    item["hint"]["steps"][1] = "Explain how the 62% result supports your claim."
    item["hint"]["self_check"] = "Did you check the 50% survey and fix every comma?"
    item["stuck_step"] = "Explain how the 62% result supports your claim."

    result = readability_metrics([item])
    detail = result["candidates"][0]

    assert detail["repetition_review_flags"]
    assert any(
        flag["reason"] == "different_numeric_anchors"
        for flag in detail["action_self_check_scope_review_flags"]
    )
    assert result["repetition"]["review_count"] >= 2
    assert result["action_self_check_scope"]["review_count"] >= 1
    assert "quality_score" not in result
    assert "flesch_kincaid" not in json.dumps(result).lower()


def test_record_readability_deduplicates_replayed_candidate_state():
    item = candidate("goal_1")
    state = {"thread_id": "thread", "revision_candidates": [item]}
    record = {
        "scenario_id": "scenario",
        "initial_state": state,
        "clarification_states": [state],
    }

    result = record_readability(record)

    assert result["candidate_count"] == 1
    assert result["candidates"][0]["scenario_id"] == "scenario"


def test_summary_does_not_estimate_visible_tokens_when_reasoning_usage_is_unavailable():
    state = {
        "model_config": {},
        "revision_candidates": [],
        "execution_logs": [
            {
                "display_name": "Assessment Coordinator",
                "model_calls": [
                    {
                        "token_usage": {
                            "prompt_tokens": 20,
                            "completion_tokens": 30,
                            "total_tokens": 50,
                            "reasoning_tokens": None,
                        },
                    }
                ],
            }
        ],
    }
    record = {"scenario_id": "usage-test", "initial_state": state}

    result = summarize("thinking", FakeClient([]), [record], "acceptance")

    assert result["token_usage"]["total_tokens"] == 50
    assert result["estimated_final_response_tokens"] is None


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


def test_evaluation_database_is_checkpointed_closed_and_hashed(tmp_path):
    database = str(tmp_path / "runner.db")
    service = create_writing_assistant_service(FakeClient([]), database)

    finalize_database(service)
    integrity = database_integrity(database)

    assert integrity["bytes"] > 0
    assert len(integrity["sha256"]) == 64
    assert integrity["wal_bytes_after_close"] == 0
    with sqlite3.connect(database) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    try:
        service.checkpointer.conn.execute("SELECT 1")
    except sqlite3.ProgrammingError:
        pass
    else:
        raise AssertionError("The evaluation checkpointer connection is still open.")


def test_evaluation_budget_stops_calls_beyond_the_authorized_call_cap():
    raw = FakeClient(['{"ok": true}', '{"ok": true}'])
    client = BudgetedClient(raw, max_model_calls=1, max_total_tokens=100)

    client.chat_completion([], json_mode=True)
    with pytest.raises(EvaluationBudgetExceeded, match="model-call cap"):
        client.chat_completion([], json_mode=True)

    assert client.model_calls == 1
    assert len(raw.calls) == 1
    assert client.attempts[0]["final_response"] == '{"ok": true}'
    assert "reasoning_content" not in json.dumps(client.attempts)


def test_evaluation_budget_stops_after_the_observed_token_cap():
    raw = FakeClient(['{"ok": true}', '{"ok": true}'])
    client = BudgetedClient(raw, max_model_calls=3, max_total_tokens=20)

    client.chat_completion([], json_mode=True)
    assert client.total_tokens == 30
    with pytest.raises(EvaluationBudgetExceeded, match="total-token"):
        client.chat_completion([], json_mode=True)

    assert client.model_calls == 1
    assert len(raw.calls) == 1


def test_token_cap_can_be_omitted_for_an_authorized_run():
    raw = FakeClient(['{"ok": true}', '{"ok": true}'])
    client = BudgetedClient(raw, max_model_calls=2, max_total_tokens=None)

    client.chat_completion([], json_mode=True)
    client.chat_completion([], json_mode=True)

    assert client.model_calls == 2
    assert client.total_tokens == 60
    assert len(client.attempts) == 2


def test_controlled_prefix_preserves_lineage_and_bounds_history_without_setup_calls(tmp_path):
    scenario = get_experiment_scenario(1)
    target = scenario.revisions[0].draft
    target_state = make_review_state(
        target,
        scenario.grade_level,
        original_writing=scenario.controlled_round["original_draft"],
        previous_writing=scenario.draft,
        genre_selection="narrative",
        revision_number=2,
    )
    response = coordinator_payload(
        target_state,
        route="direct_response",
        issues=[],
        observations=[observation_for("goal_sandcastle")],
    )
    client = FakeClient([response])
    service = create_writing_assistant_service(
        client,
        str(tmp_path / "controlled.db"),
        coordinator=AssessmentCoordinator(client, include_prior_findings=True),
    )
    service.experiment_arm = "gc_history"

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert record["controlled_prefix"] is True
    assert len(client.calls) == 1
    composition_id = record["initial_state"]["composition_id"]
    snapshots = service.storage.list_snapshots(composition_id)
    assert [snapshot.revision_number for snapshot in snapshots] == [0, 1, 2]
    assert snapshots[-1].writing == target
    details = record["revision_details"][0]
    assert details["selected_goal_ids"] == ["goal_sandcastle"]
    assert len(details["prior_findings"]) == 2
    assert {item["selection_status"] for item in details["prior_findings"]} == {
        "unselected"
    }
    model_payload = json.loads(client.calls[0][0][1]["content"].split("\n", 1)[1])
    assert model_payload["prior_findings"] == details["prior_findings"]
    assert record["initial_state"]["execution_logs"] == []
    assert record["revision_states"][0]["coordinator_repair_count"] == 0


def test_support_only_controlled_handoff_uses_one_support_call_and_preserves_round(tmp_path):
    scenario = get_experiment_scenario(7)
    setup = scenario.controlled_round
    state = make_review_state(
        scenario.draft,
        scenario.grade_level,
        original_writing=setup["original_draft"],
        previous_writing=setup["original_draft"],
        genre_selection="narrative",
        revision_number=1,
        selected_goals=setup["selected_goals"],
        goal_self_reports=setup["goal_self_reports"],
        text_diff=build_text_diff(setup["original_draft"], scenario.draft),
    )
    state.update(
        {
            "working_genre": "narrative",
            "issues": setup["issues"],
            "selected_goal_observations": setup["selected_goal_observations"],
            "source_limitations": [],
        }
    )
    client = FakeClient([support_payload(state)])
    service = create_writing_assistant_service(client, str(tmp_path / "support.db"))

    record = run_support_scenario(service, "session", scenario)

    assert record["support_only"] is True
    assert len(client.calls) == 1
    assert len(record["initial_state"]["goal_feedback"]) == 2
    assert {
        candidate["goal_id"]
        for candidate in record["initial_state"]["revision_candidates"]
    } == {"goal_run_on", "goal_sandcastle"}
    logs = record["initial_state"]["execution_logs"]
    assert [log["node"] for log in logs] == ["support_agent"]
    snapshots = service.storage.list_snapshots(record["initial_state"]["composition_id"])
    assert [snapshot.revision_number for snapshot in snapshots] == [0, 1]


@pytest.mark.parametrize("number", [14, 15])
def test_thinking_comparison_handoffs_are_mock_executable(number, tmp_path):
    scenario = get_experiment_scenario(number)
    setup = scenario.controlled_round
    state = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        assignment_prompt=scenario.assignment_prompt,
        teacher_directions=scenario.teacher_directions,
        source_material=scenario.source_material,
    )
    state.update(
        {
            "working_genre": "argument",
            "issues": setup["issues"],
            "source_limitations": setup["source_limitations"],
        }
    )
    client = FakeClient([support_payload(state)])
    service = create_writing_assistant_service(
        client, str(tmp_path / f"support-{number}.db")
    )

    record = run_support_scenario(service, "session", scenario)

    assert len(client.calls) == 1
    assert len(record["initial_state"]["revision_candidates"]) == len(setup["issues"])
    assert record["initial_state"]["source_limitations"] == setup["source_limitations"]
    assert [log["node"] for log in record["initial_state"]["execution_logs"]] == [
        "support_agent"
    ]



def test_consolidated_arm_uses_candidate_prompt_and_version(tmp_path, monkeypatch):
    scenario = load_support_comparison_scenarios()[0]
    setup = scenario.controlled_round
    handoff = {
        "issues": setup["issues"],
        "selected_goal_observations": setup.get("selected_goal_observations", []),
        "source_limitations": setup.get("source_limitations", []),
    }
    client = FakeClient([support_payload(handoff, legacy=True)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "nonthinking",
        tmp_path,
        "20261115T000000Z",
        "support_prompt",
        scenario_number=1,
        experiment_arm="support_consolidated",
        max_model_calls=2,
    )

    assert result["summary"]["experiment_arm"] == "support_consolidated"
    assert result["summary"]["configuration"]["prompt_version"] == (
        CONSOLIDATED_SUPPORT_PROMPT_VERSION
    )
    assert client.calls[0][0][0]["content"] == SUPPORT_ROUND_CONSOLIDATED_PROMPT
    assert result["records"][0]["support_only"] is True
    assert result["summary"]["errors"] == []


def test_current_arm_preserves_v3_7_control_contract(tmp_path, monkeypatch):
    scenario = load_support_comparison_scenarios()[0]
    setup = scenario.controlled_round
    handoff = {
        "issues": setup["issues"],
        "selected_goal_observations": setup.get("selected_goal_observations", []),
        "source_limitations": setup.get("source_limitations", []),
    }
    client = FakeClient([support_payload(handoff, legacy=True)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "nonthinking",
        tmp_path,
        "20261115T000000Z",
        "support_prompt",
        scenario_number=1,
        experiment_arm="current",
        max_model_calls=2,
    )

    configuration = result["summary"]["configuration"]
    assert configuration["prompt_version"] == "v3.7.1"
    assert configuration["schema_version"] == "v3.7.0"
    assert client.calls[0][0][0]["content"] == V3_7_1_SUPPORT_ROUND_PROMPT
    hint = result["records"][0]["initial_state"]["revision_candidates"][0]["hint"]
    assert "vocabulary_options" in hint
    assert "sentence_starter" in hint


def test_baseline_readable_arm_uses_v3_8_candidate_and_metrics(tmp_path, monkeypatch):
    scenario = load_support_comparison_scenarios()[0]
    setup = scenario.controlled_round
    handoff = {
        "issues": setup["issues"],
        "selected_goal_observations": setup.get("selected_goal_observations", []),
        "source_limitations": setup.get("source_limitations", []),
    }
    client = FakeClient([support_payload(handoff)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261115T000000Z",
        "support_prompt",
        scenario_number=1,
        experiment_arm="baseline_readable",
        max_model_calls=2,
    )

    summary = result["summary"]
    assert summary["configuration"]["prompt_version"] == BASELINE_READABLE_PROMPT_VERSION
    assert summary["configuration"]["schema_version"] == "v3.8.0"
    assert client.calls[0][0][0]["content"] == BASELINE_READABLE_SUPPORT_PROMPT
    hint = result["records"][0]["initial_state"]["revision_candidates"][0]["hint"]
    assert "vocabulary_options" not in hint
    assert "sentence_starter" not in hint
    assert summary["readability"]["candidate_count"] >= 1
    assert summary["observations"][0]["readability"]["candidate_count"] >= 1
    assert "not a quality threshold" in summary["readability_metric_notes"][1]


@pytest.mark.parametrize(
    ("arm", "prompt_version", "expected_support_prompt"),
    [
        ("structural_current", "v3.8.0", STRUCTURAL_SUPPORT_ROUND_PROMPT),
        (
            "baseline_readable_v2",
            BASELINE_READABLE_V2_PROMPT_VERSION,
            BASELINE_READABLE_V2_SUPPORT_PROMPT,
        ),
        (
            "regression_readable",
            REGRESSION_READABLE_PROMPT_VERSION,
            REGRESSION_READABLE_SUPPORT_PROMPT,
        ),
    ],
)
def test_structural_and_readability_arms_use_versioned_prompts_without_shape_change(
    tmp_path, monkeypatch, arm, prompt_version, expected_support_prompt
):
    scenario = load_support_comparison_scenarios()[0]
    setup = scenario.controlled_round
    handoff = {
        "issues": setup["issues"],
        "selected_goal_observations": setup.get("selected_goal_observations", []),
        "source_limitations": setup.get("source_limitations", []),
    }
    client = FakeClient([support_payload(handoff)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "thinking",
        tmp_path,
        f"20261116T000000{arm}",
        "support_prompt",
        scenario_number=1,
        experiment_arm=arm,
        max_model_calls=2,
    )

    summary = result["summary"]
    assert summary["configuration"]["prompt_version"] == prompt_version
    assert summary["configuration"]["schema_version"] == "v3.8.0"
    assert client.calls[0][0][0]["content"] == expected_support_prompt
    hint = result["records"][0]["initial_state"]["revision_candidates"][0]["hint"]
    assert "vocabulary_options" not in hint
    assert "sentence_starter" not in hint
    assert summary["errors"] == []


def test_v3_8_2_arm_uses_final_credit_prompt_with_controlled_history(
    tmp_path, monkeypatch
):
    scenario = load_final_regression_scenarios()[1]
    setup = scenario.controlled_round
    final = make_review_state(
        scenario.draft,
        scenario.grade_level,
        review_mode="final",
        original_writing=setup["original_draft"],
        revision_number=1,
        text_diff=build_text_diff(setup["original_draft"], scenario.draft),
    )
    coordinator = final_coordinator_payload(final, changed=False)
    values = json.loads(coordinator)
    handoff = {
        **final,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": [],
        "comparison_regressions": [],
        "future_areas": values["future_areas"],
    }
    client = FakeClient([coordinator, final_support_payload(handoff)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261116T000001Z",
        "final_regression",
        scenario_number=2,
        experiment_arm="baseline_readable_v2",
        max_model_calls=3,
    )

    assert result["summary"]["errors"] == []
    assert client.calls[0][0][0]["content"] == (
        BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT
    )
    assert result["records"][0]["source_lineage"]["scenario_number"] == 9


def test_regression_arm_targets_contextual_purpose_loss_without_changing_other_prompts(
    tmp_path, monkeypatch
):
    scenario = load_final_regression_scenarios()[3]
    setup = scenario.controlled_round
    final = make_review_state(
        scenario.draft,
        scenario.grade_level,
        review_mode="final",
        original_writing=setup["original_draft"],
        revision_number=1,
        text_diff=build_text_diff(setup["original_draft"], scenario.draft),
    )
    coordinator = final_coordinator_payload(final, changed=False)
    values = json.loads(coordinator)
    handoff = {
        **final,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": [],
        "comparison_regressions": [],
        "future_areas": values["future_areas"],
    }
    client = FakeClient([coordinator, final_support_payload(handoff)])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "thinking",
        tmp_path,
        "20261116T000002Z",
        "final_regression",
        scenario_number=4,
        experiment_arm="regression_readable",
        max_model_calls=3,
    )

    assert result["summary"]["errors"] == []
    assert result["summary"]["configuration"]["prompt_version"] == (
        REGRESSION_READABLE_PROMPT_VERSION
    )
    assert result["summary"]["configuration"]["schema_version"] == "v3.8.0"
    assert client.calls[0][0][0]["content"] == REGRESSION_READABLE_COORDINATOR_FINAL_PROMPT
    assert "CONTEXTUAL PURPOSE AND REGRESSION CHECK" in client.calls[0][0][0]["content"]
    assert "do not let credit for the caution suppress the regression" in (
        client.calls[0][0][0]["content"]
    )
    assert "CONTEXTUAL PURPOSE AND REGRESSION CHECK" not in (
        BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT
    )
    assert REGRESSION_READABLE_COORDINATOR_ROUND_PROMPT == (
        BASELINE_READABLE_V2_COORDINATOR_ROUND_PROMPT
    )
    assert REGRESSION_READABLE_SUPPORT_PROMPT == BASELINE_READABLE_V2_SUPPORT_PROMPT
    assert result["records"][0]["source_lineage"]["scenario_number"] == 9


def test_early_limit_arm_never_escalates_before_deterministic_boundary(
    tmp_path, monkeypatch
):
    scenario = load_coordinator_targeted_scenarios()[2]
    state, _ = scenario_state(scenario)
    response = coordinator_payload(
        state,
        route="teacher_review",
        teacher_flag_category="clarification_limit",
        teacher_flag_reason="Adversarial early-limit probe.",
    )
    client = FakeClient([response, response])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "nonthinking",
        tmp_path,
        "20261115T000000Z",
        "coordinator_targeted",
        scenario_number=3,
        experiment_arm="coordinator_early_limit",
        max_model_calls=3,
    )

    record = result["records"][0]
    assert record["initial_state"]["routing_decision"] == "ask_clarification"
    assert len(record["clarification_states"]) == 1
    assert record["clarification_states"][0]["routing_decision"] == "ask_clarification"
    assert record["clarification_states"][0]["clarification_count"] == 2
    assert "teacher_message" not in record["clarification_states"][0]
    assert "ADVERSARIAL CONTRACT PROBE" in client.calls[0][0][0]["content"]
    assert result["summary"]["errors"] == []



def test_clarification_probe_exercises_deterministic_limit_after_two_answers(
    tmp_path, monkeypatch
):
    scenario = load_coordinator_targeted_scenarios()[3]
    state, _ = scenario_state(scenario)
    response = coordinator_payload(state, route="ask_clarification")
    client = FakeClient([response, response, response])
    monkeypatch.setattr(
        DeepSeekClient,
        "from_env",
        classmethod(lambda cls, require_thinking=False: client),
    )

    result, _ = run_mode(
        "nonthinking",
        tmp_path,
        "20261115T000000Z",
        "coordinator_targeted",
        scenario_number=4,
        experiment_arm="coordinator_clarification_probe",
        max_model_calls=4,
    )

    record = result["records"][0]
    assert len(record["clarification_states"]) == 2
    final_state = record["clarification_states"][-1]
    assert final_state["routing_decision"] == "teacher_review"
    assert final_state["teacher_flag_category"] == "clarification_limit"
    assert "CLARIFICATION-BOUNDARY PROBE" in client.calls[0][0][0]["content"]
    assert result["summary"]["errors"] == []


@pytest.mark.parametrize(
    "scenario",
    [*load_final_history_scenarios(), *load_final_regression_scenarios()],
    ids=lambda scenario: scenario.scenario_id,
)
def test_final_history_controlled_fixtures_reach_final_with_authoritative_observation(
    scenario, tmp_path
):
    setup = scenario.controlled_round
    final = make_review_state(
        scenario.draft,
        scenario.grade_level,
        review_mode="final",
        original_writing=setup["original_draft"],
        revision_number=1,
        text_diff=build_text_diff(setup["original_draft"], scenario.draft),
    )
    coordinator = final_coordinator_payload(final, changed=False)
    values = json.loads(coordinator)
    handoff = {
        **final,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": [],
        "comparison_regressions": [],
        "future_areas": values["future_areas"],
    }
    client = FakeClient([coordinator, final_support_payload(handoff)])
    service = create_writing_assistant_service(client, str(tmp_path / "final-history.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    history = record["final_state"]["revision_history"]
    assert len(history) == 1
    actual = history[0]["selected_goals"][0]
    expected = setup["selected_goal_observations"][0]
    assert actual["goal_id"] == expected["goal_id"]
    assert actual["status"] == expected["status"]
    assert actual["observation"] == expected["observation"]
    assert actual["evidence_reference"] == expected["evidence_reference"]
    assert actual["carry_forward"] == expected["carry_forward"]
    assert actual["observation"] != setup["goal_feedback"][0]["observation"]
    assert history[0]["reviewed_draft_sha256"] == draft_sha256(scenario.draft)
    payload = json.loads(client.calls[0][0][1]["content"].split("\n", 1)[1])
    assert payload["revision_history"] == history
    assert payload["final_submitted_draft_sha256"] == history[0][
        "reviewed_draft_sha256"
    ]


def final_responses(scenario):
    original = (
        scenario.controlled_round.get("original_draft", scenario.draft)
        if scenario.controlled_round
        else scenario.draft
    )
    final_draft = (
        scenario.revisions[-1].draft if scenario.revisions else scenario.draft
    )
    final = make_review_state(
        final_draft,
        scenario.grade_level,
        review_mode="final",
        original_writing=original,
        revision_number=len(scenario.revisions),
        text_diff=build_text_diff(original, final_draft),
    )
    coordinator = json.loads(final_coordinator_payload(final))
    coordinator["improvements"][0]["goal_id"] = ""
    handoff = {
        **final,
        "original_strengths": coordinator["original_strengths"],
        "comparison_improvements": coordinator["improvements"],
        "comparison_regressions": coordinator["regressions"],
        "future_areas": coordinator["future_areas"],
    }
    return json.dumps(coordinator), final_support_payload(handoff)


def test_available_goal_successor_completes_with_two_candidates_without_count_error(
    tmp_path,
):
    scenario = load_readability_coverage_scenarios()[0]
    initial = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        assignment_prompt=scenario.assignment_prompt,
        teacher_directions=scenario.teacher_directions,
    )
    issues = [
        issue_for(
            scenario.draft,
            "Our school should allow a community garden.",
            "goal_claim",
        ),
        issue_for(scenario.draft, "Many students said yes.", "goal_evidence"),
    ]
    initial_coordinator = coordinator_payload(initial, issues=issues)
    initial_support = support_payload({**initial, **json.loads(initial_coordinator)})
    selected = [candidate_for(issue) for issue in issues]
    revision = make_review_state(
        scenario.revisions[0].draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        original_writing=scenario.draft,
        previous_writing=scenario.draft,
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(scenario.draft, scenario.revisions[0].draft),
    )
    observations = [
        observation_for("goal_claim"),
        observation_for(
            "goal_evidence",
            status="improvement_not_yet_evident",
            carry_forward=True,
        ),
    ]
    revision_coordinator = coordinator_payload(
        revision,
        issues=[
            issue_for(revision["writing"], "Many students said yes.", "goal_evidence")
        ],
        observations=observations,
    )
    revision_support = support_payload(
        {**revision, **json.loads(revision_coordinator)}
    )
    final_coordinator, final_support = final_responses(scenario)
    client = FakeClient(
        [
            initial_coordinator,
            initial_support,
            revision_coordinator,
            revision_support,
            final_coordinator,
            final_support,
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "available.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert len(record["initial_state"]["revision_candidates"]) == 2
    details = record["revision_details"][0]
    assert details["available_candidate_count"] == 2
    assert details["goal_selection_mode"] == "all_available"
    assert details["selected_goal_ids"] == ["goal_claim", "goal_evidence"]
    assert details["goal_self_reports"] == {
        "goal_claim": "attempted",
        "goal_evidence": "deferred",
    }
    assert len(record["final_state"]["revision_history"]) == 1
    assert len(record["final_state"]["revision_history"][0]["selected_goals"]) == 2


def test_controlled_three_goal_prefix_exercises_two_deferrals_independently(tmp_path):
    scenario = load_readability_coverage_scenarios()[1]
    selected = scenario.controlled_round["revision_candidates"]
    revision = make_review_state(
        scenario.revisions[0].draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        original_writing=scenario.draft,
        previous_writing=scenario.draft,
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(scenario.draft, scenario.revisions[0].draft),
    )
    observations = [
        observation_for("goal_claim"),
        observation_for(
            "goal_evidence", status="improvement_not_yet_evident", carry_forward=True
        ),
        observation_for(
            "goal_benefit", status="improvement_not_yet_evident", carry_forward=True
        ),
    ]
    revision_coordinator = coordinator_payload(
        revision,
        issues=[
            issue_for(revision["writing"], "Many students said yes.", "goal_evidence")
        ],
        observations=observations,
    )
    revision_support = support_payload(
        {**revision, **json.loads(revision_coordinator)}
    )
    final_coordinator, final_support = final_responses(scenario)
    client = FakeClient(
        [revision_coordinator, revision_support, final_coordinator, final_support]
    )
    service = create_writing_assistant_service(
        client, str(tmp_path / "controlled-three.db")
    )

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert record["controlled_prefix"] is True
    assert record["initial_state"]["execution_logs"] == []
    details = record["revision_details"][0]
    assert details["available_candidate_count"] == 3
    assert details["goal_selection_mode"] == "three"
    assert details["goal_self_reports"] == {
        "goal_claim": "attempted",
        "goal_evidence": "deferred",
        "goal_benefit": "deferred",
    }
    history = record["final_state"]["revision_history"][0]["selected_goals"]
    assert [goal["goal_id"] for goal in history] == [
        "goal_claim",
        "goal_evidence",
        "goal_benefit",
    ]


def test_direct_response_successor_finishes_without_revision_snapshot(tmp_path):
    scenario = load_readability_coverage_scenarios()[2]
    initial = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        assignment_prompt=scenario.assignment_prompt,
        teacher_directions=scenario.teacher_directions,
    )
    initial_coordinator = coordinator_payload(
        initial, route="direct_response", issues=[]
    )
    final = make_review_state(
        scenario.draft,
        scenario.grade_level,
        review_mode="final",
        original_writing=scenario.draft,
        revision_number=0,
        text_diff=build_text_diff(scenario.draft, scenario.draft),
    )
    final_coordinator = final_coordinator_payload(final, changed=False)
    values = json.loads(final_coordinator)
    handoff = {
        **final,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": [],
        "comparison_regressions": [],
        "future_areas": values["future_areas"],
    }
    client = FakeClient(
        [initial_coordinator, final_coordinator, final_support_payload(handoff)]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "direct.db"))

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert record["alternate_path"] == {
        "type": "direct_response_finish_without_revision",
        "route": "direct_response",
        "candidate_count": 0,
        "revision_count": 0,
    }
    assert record["revision_states"] == []
    assert len(
        service.storage.list_snapshots(record["initial_state"]["composition_id"])
    ) == 1
    assert record["final_state"]["final_reflection"]["improvements"] == []


def test_direct_response_successor_uses_staged_revision_when_candidate_exists(tmp_path):
    scenario = load_readability_coverage_scenarios()[2]
    reference = "A corner with cushions would make reading time more comfortable."
    initial = make_review_state(
        scenario.draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        assignment_prompt=scenario.assignment_prompt,
        teacher_directions=scenario.teacher_directions,
    )
    initial_coordinator = coordinator_payload(
        initial, issues=[issue_for(initial["writing"], reference)]
    )
    initial_support = support_payload({**initial, **json.loads(initial_coordinator)})
    selected = [candidate_for(issue_for(initial["writing"], reference))]
    revision = make_review_state(
        scenario.revisions[0].draft,
        scenario.grade_level,
        genre_selection=scenario.genre,
        original_writing=scenario.draft,
        previous_writing=scenario.draft,
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(scenario.draft, scenario.revisions[0].draft),
    )
    revision_coordinator = coordinator_payload(
        revision,
        issues=[issue_for(revision["writing"], scenario.revisions[0].draft.split(". ")[-1])],
        observations=[observation_for()],
    )
    revision_support = support_payload(
        {**revision, **json.loads(revision_coordinator)}
    )
    final_coordinator, final_support = final_responses(scenario)
    client = FakeClient(
        [
            initial_coordinator,
            initial_support,
            revision_coordinator,
            revision_support,
            final_coordinator,
            final_support,
        ]
    )
    service = create_writing_assistant_service(
        client, str(tmp_path / "candidate-path.db")
    )

    record = run_scenario(service, "session", scenario)

    assert "error" not in record
    assert "alternate_path" not in record
    assert len(record["revision_states"]) == 1
    assert len(
        service.storage.list_snapshots(record["initial_state"]["composition_id"])
    ) == 2
    assert record["final_state"]["final_reflection"]["improvements"]
