import json
import uuid

import pytest

from agents.utils import APIError, ConfigurationError, InputValidationError, ResponseValidationError
from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from tests.helpers import (
    INITIAL_DRAFT,
    FakeClient,
    coordinator_payload,
    final_coordinator_payload,
    final_support_payload,
    issue_for,
    observation_for,
    support_payload,
)


def identifiers():
    return [uuid.uuid4().hex for _ in range(4)]


def initial_state(writing=INITIAL_DRAFT, genre="argument", debug=False):
    composition_id, round_id, thread_id, snapshot_id = identifiers()
    state = make_review_state(
        writing,
        "6th Grade",
        composition_id=composition_id,
        round_id=round_id,
        thread_id=thread_id,
        genre_selection=genre,
        debug_enabled=debug,
    )
    return state, snapshot_id


def handoff(state, observations=None):
    return {
        **state,
        "working_genre": "argument",
        "strengths": ["Clear position"],
        "issues": [issue_for(state["writing"])],
        "selected_goal_observations": observations or [],
        "source_limitations": [],
    }


def revision_state(service, composition_id, writing, selected_goals, reports=None):
    snapshots = service.storage.list_snapshots(composition_id)
    composition = service.storage.get_composition(composition_id)
    _, round_id, thread_id, snapshot_id = identifiers()
    previous = snapshots[-1]
    state = make_review_state(
        writing,
        composition.grade_level,
        composition_id=composition_id,
        round_id=round_id,
        thread_id=thread_id,
        original_writing=snapshots[0].writing,
        previous_writing=previous.writing,
        genre_selection=composition.genre_selection,
        revision_number=previous.revision_number + 1,
        selected_goals=selected_goals,
        goal_self_reports=reports or {},
        text_diff=build_text_diff(previous.writing, writing),
    )
    return state, snapshot_id


def final_state(service, composition_id):
    snapshots = service.storage.list_snapshots(composition_id)
    composition = service.storage.get_composition(composition_id)
    _, round_id, thread_id, _ = identifiers()
    original = snapshots[0]
    final = snapshots[-1]
    state = make_review_state(
        final.writing,
        composition.grade_level,
        composition_id=composition_id,
        round_id=round_id,
        thread_id=thread_id,
        review_mode="final",
        original_writing=original.writing,
        revision_number=final.revision_number,
        selected_goals=final.selected_goals,
        text_diff=build_text_diff(original.writing, final.writing),
    )
    state["working_genre"] = "argument"
    return state, original.snapshot_id, final.snapshot_id


def test_initial_review_persists_original_before_model_and_supports_history(tmp_path):
    state, snapshot_id = initial_state()
    responses = [coordinator_payload(state), support_payload(handoff(state))]
    client = FakeClient(responses)
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    original_chat = client.chat_completion

    def inspected_chat(messages, **kwargs):
        assert service.storage.get_snapshot(state["composition_id"], 0) is not None
        return original_chat(messages, **kwargs)

    client.chat_completion = inspected_chat
    result = service.start_composition("session", state, snapshot_id)

    assert result.state["routing_decision"] == "support_agent"
    assert result.state["agent_path"] == [
        "Assessment Coordinator",
        "Instructional Support Agent",
    ]
    assert service.storage.get_composition(state["composition_id"]).status == "active"
    assert service.storage.get_snapshot(state["composition_id"], 0).writing == INITIAL_DRAFT


def test_revision_round_preserves_original_and_stores_selected_goals_and_reports(tmp_path):
    initial, original_snapshot_id = initial_state()
    revised = INITIAL_DRAFT + "\n\nStudents practice noticing what others need."
    observations = [observation_for()]
    initial_client = FakeClient(
        [coordinator_payload(initial), support_payload(handoff(initial))]
    )
    service = create_writing_assistant_service(initial_client, str(tmp_path / "app.db"))
    first = service.start_composition("session", initial, original_snapshot_id)
    selected = first.state["revision_candidates"][:1]
    revision, revision_snapshot_id = revision_state(
        service,
        initial["composition_id"],
        revised,
        selected,
        {"goal_1": "attempted"},
    )
    revision_handoff = handoff(revision, observations)
    client = FakeClient(
        [
            coordinator_payload(revision, observations=observations),
            support_payload(revision_handoff),
        ]
    )
    service.client = client
    # Replace the graph's agents through a fresh service sharing the same database.
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    result = service.submit_revision(
        "session", revision, revision_snapshot_id
    )

    snapshots = service.storage.list_snapshots(initial["composition_id"])
    assert [snapshot.revision_number for snapshot in snapshots] == [0, 1]
    assert snapshots[0].writing == INITIAL_DRAFT
    assert snapshots[1].writing == revised
    assert snapshots[1].goal_self_reports == {"goal_1": "attempted"}
    assert result.state["goal_feedback"][0]["status"] == "specific_improvement"
    assert result.state["text_diff"]["changed"] is True


def test_clarification_resumes_same_thread_after_service_restart(tmp_path):
    database = str(tmp_path / "app.db")
    state, snapshot_id = initial_state()
    first = create_writing_assistant_service(
        FakeClient([coordinator_payload(state, route="ask_clarification")]), database
    )
    pending = first.start_composition("session", state, snapshot_id)

    assert pending.pending
    thread_id = state["thread_id"]

    second = create_writing_assistant_service(
        FakeClient(
            [coordinator_payload(state), support_payload(handoff(state))]
        ),
        database,
    )
    result = second.resume_clarification(
        "session", state["composition_id"], "I want help explaining my reason."
    )

    assert result.thread_id == thread_id
    assert result.state["clarification_history"] == [
        {
            "question": "What would you like help with?",
            "answer": "I want help explaining my reason.",
        }
    ]
    assert result.state["agent_path"] == [
        "Assessment Coordinator",
        "Clarification",
        "Assessment Coordinator",
        "Instructional Support Agent",
    ]


def test_two_unclear_answers_route_to_clarification_limit(tmp_path):
    state, snapshot_id = initial_state()
    client = FakeClient(
        [coordinator_payload(state, route="ask_clarification") for _ in range(3)]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    service.start_composition("session", state, snapshot_id)
    service.resume_clarification("session", state["composition_id"], "Not sure")

    result = service.resume_clarification(
        "session", state["composition_id"], "Anything, I guess"
    )

    assert result.state["teacher_flag_category"] == "clarification_limit"
    assert result.state["routing_decision"] == "teacher_review"
    assert len(result.state["clarification_history"]) == 2
    assert "no teacher has been notified" in result.state["teacher_message"].lower()
    assert client.responses == []


def test_clear_second_answer_resumes_normal_support(tmp_path):
    state, snapshot_id = initial_state()
    client = FakeClient(
        [
            coordinator_payload(state, route="ask_clarification"),
            coordinator_payload(state, route="ask_clarification"),
            coordinator_payload(state),
            support_payload(handoff(state)),
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    service.start_composition("session", state, snapshot_id)
    service.resume_clarification("session", state["composition_id"], "Not sure")

    result = service.resume_clarification(
        "session", state["composition_id"], "Please help me explain my evidence."
    )

    assert result.state["routing_decision"] == "support_agent"
    assert not result.state.get("teacher_message")


def test_revision_teacher_override_bypasses_support_and_normal_critique(tmp_path):
    initial, original_snapshot_id = initial_state()
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload(initial), support_payload(handoff(initial))]),
        str(tmp_path / "app.db"),
    )
    first = service.start_composition("session", initial, original_snapshot_id)
    revision, snapshot_id = revision_state(
        service,
        initial["composition_id"],
        INITIAL_DRAFT + "\n\nI do not feel safe at school.",
        first.state["revision_candidates"][:1],
    )
    client = FakeClient(
        [
            coordinator_payload(
                revision,
                route="teacher_review",
                teacher_flag_reason="The revision includes a safety concern.",
                teacher_evidence=["I do not feel safe at school."],
            )
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    result = service.submit_revision("session", revision, snapshot_id)

    assert result.state["agent_path"] == ["Assessment Coordinator", "Teacher Review"]
    assert "trusted adult" in result.state["student_output"]
    assert "revision_candidates" not in result.state


def test_direct_response_does_not_force_revision_and_no_revision_finish_uses_no_model(tmp_path):
    state, snapshot_id = initial_state()
    client = FakeClient([coordinator_payload(state, route="direct_response")])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    result = service.start_composition("session", state, snapshot_id)

    assert result.state["revision_candidates"] == []
    assert "do not see a meaningful revision issue" in result.state["student_output"]

    final, original_id, final_id = final_state(service, state["composition_id"])
    reflection = service.finish_composition("session", final, original_id, final_id)

    assert reflection.state["final_reflection"]["improvements"] == []
    assert "No revised draft was submitted" in reflection.state["student_output"]
    assert client.responses == []
    assert len(client.calls) == 1


def test_genre_correction_reassesses_without_new_snapshot(tmp_path):
    state, snapshot_id = initial_state(genre="auto")
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload(state), support_payload(handoff(state))]),
        str(tmp_path / "app.db"),
    )
    service.start_composition("session", state, snapshot_id)
    correction, _ = initial_state()
    correction["composition_id"] = state["composition_id"]
    correction["revision_number"] = 0
    correction["genre_selection"] = "narrative"
    correction["writing"] = INITIAL_DRAFT
    correction["original_writing"] = INITIAL_DRAFT
    client = FakeClient(
        [
            coordinator_payload(correction, working_genre="narrative"),
            support_payload({**handoff(correction), "working_genre": "narrative"}),
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    result = service.reassess_genre("session", correction)

    assert result.state["working_genre"] == "narrative"
    assert len(service.storage.list_snapshots(state["composition_id"])) == 1
    assert len(service.storage.list_rounds(state["composition_id"])) == 2


def test_failed_review_retry_does_not_duplicate_snapshot(tmp_path):
    state, snapshot_id = initial_state()
    client = FakeClient(
        [APIError("Temporary"), coordinator_payload(state), support_payload(handoff(state))]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    with pytest.raises(APIError):
        service.start_composition("session", state, snapshot_id)
    assert service.storage.get_latest_round(state["composition_id"]).status == "failed"
    assert len(service.storage.list_snapshots(state["composition_id"])) == 1

    result = service.retry_round("session", state["composition_id"])

    assert result.state["routing_decision"] == "support_agent"
    assert len(service.storage.list_snapshots(state["composition_id"])) == 1
    assert service.storage.get_latest_round(state["composition_id"]).status == "completed"


def test_persistent_support_failure_preserves_snapshot_and_no_partial_feedback(tmp_path):
    state, snapshot_id = initial_state()
    invalid_state = handoff(state)
    invalid = support_payload(invalid_state, candidates=[])
    client = FakeClient([coordinator_payload(state), invalid, invalid])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    with pytest.raises(ResponseValidationError):
        service.start_composition("session", state, snapshot_id)

    record = service.storage.get_latest_round(state["composition_id"])
    assert record.status == "failed"
    assert record.state == {}
    assert service.storage.get_snapshot(state["composition_id"], 0).writing == INITIAL_DRAFT


def test_final_comparison_uses_original_and_latest_submitted_draft(tmp_path):
    initial, original_snapshot_id = initial_state()
    revised = INITIAL_DRAFT + "\n\nA clearer explanation."
    initial_client = FakeClient(
        [coordinator_payload(initial), support_payload(handoff(initial))]
    )
    service = create_writing_assistant_service(initial_client, str(tmp_path / "app.db"))
    first = service.start_composition("session", initial, original_snapshot_id)
    revision, revision_snapshot_id = revision_state(
        service, initial["composition_id"], revised, first.state["revision_candidates"][:1]
    )
    observations = [observation_for()]
    revision_client = FakeClient(
        [
            coordinator_payload(revision, observations=observations),
            support_payload(handoff(revision, observations)),
        ]
    )
    service = create_writing_assistant_service(revision_client, str(tmp_path / "app.db"))
    service.submit_revision("session", revision, revision_snapshot_id)
    final, original_id, final_id = final_state(service, initial["composition_id"])
    coordinator_response = final_coordinator_payload(final)
    coordinator_values = json.loads(coordinator_response)
    final_handoff = {
        **final,
        "original_strengths": coordinator_values["original_strengths"],
        "comparison_improvements": coordinator_values["improvements"],
        "comparison_regressions": coordinator_values["regressions"],
        "future_areas": coordinator_values["future_areas"],
    }
    final_client = FakeClient(
        [coordinator_response, final_support_payload(final_handoff)]
    )
    service = create_writing_assistant_service(final_client, str(tmp_path / "app.db"))

    result = service.finish_composition("session", final, original_id, final_id)

    assert result.state["original_writing"] == INITIAL_DRAFT
    assert result.state["writing"] == revised
    assert result.state["final_reflection"]["improvements"]
    assert service.storage.get_reflection(initial["composition_id"]).status == "completed"


def test_honest_stage_callback_order(tmp_path):
    state, snapshot_id = initial_state()
    client = FakeClient([coordinator_payload(state), support_payload(handoff(state))])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    stages = []

    result = service.start_composition("session", state, snapshot_id, stages.append)

    assert result.service_duration_ms is not None
    assert result.service_duration_ms >= service.storage.get_latest_round(
        state["composition_id"]
    ).duration_ms
    assert stages == [
        "Draft saved",
        "Reviewing your draft and selected goals",
        "Preparing feedback",
        "Review complete",
    ]
    logs = service.storage.get_latest_round(state["composition_id"]).state["execution_logs"]
    assert all("latency_ms" in call for log in logs for call in log["model_calls"])


def test_debug_capture_is_separately_opt_in(tmp_path):
    state, snapshot_id = initial_state(debug=False)
    client = FakeClient([coordinator_payload(state), support_payload(handoff(state))])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))

    result = service.start_composition("session", state, snapshot_id)

    serialized = json.dumps(result.state)
    assert "raw_response" not in serialized
    assert "reasoning_content" not in serialized
    assert result.state["model_config"]["thinking_enabled"] is True


def test_resume_requires_matching_session_and_nonempty_answer(tmp_path):
    state, snapshot_id = initial_state()
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload(state, route="ask_clarification")]),
        str(tmp_path / "app.db"),
    )
    service.start_composition("session", state, snapshot_id)

    with pytest.raises(InputValidationError, match="unavailable"):
        service.resume_clarification("other", state["composition_id"], "Answer")
    with pytest.raises(InputValidationError, match="short answer"):
        service.resume_clarification("session", state["composition_id"], " ")


def test_delete_session_removes_compositions_snapshots_reflections_and_checkpoints(tmp_path):
    state, snapshot_id = initial_state()
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload(state, route="ask_clarification")]),
        str(tmp_path / "app.db"),
    )
    service.start_composition("session", state, snapshot_id)
    final, original_id, final_id = final_state(service, state["composition_id"])
    final_result = service.finish_composition("session", final, original_id, final_id)
    config = {"configurable": {"thread_id": state["thread_id"]}}
    final_config = {"configurable": {"thread_id": final_result.thread_id}}
    assert service.checkpointer.get_tuple(config) is not None

    service.delete_session("session")

    assert service.storage.list_compositions("session") == []
    assert service.storage.list_snapshots(state["composition_id"]) == []
    assert service.storage.get_reflection(state["composition_id"]) is None
    assert service.checkpointer.get_tuple(config) is None
    assert service.checkpointer.get_tuple(final_config) is None


def test_v3_service_uses_configured_nonthinking_runtime(tmp_path):
    service = create_writing_assistant_service(
        FakeClient([], thinking=False), str(tmp_path / "app.db")
    )

    assert service.client.thinking is False


def test_thinking_evaluation_rejects_mismatched_explicit_requirement(tmp_path):
    with pytest.raises(ConfigurationError, match="controlled evaluation"):
        create_writing_assistant_service(
            FakeClient([], thinking=False),
            str(tmp_path / "app.db"),
            require_thinking=True,
        )


def test_controlled_nonthinking_service_requires_explicit_opt_in(tmp_path):
    service = create_writing_assistant_service(
        FakeClient([], thinking=False),
        str(tmp_path / "app.db"),
        require_thinking=False,
    )

    assert service.client.thinking is False


def test_three_goal_observations_deferrals_and_carry_forward_across_rounds(tmp_path):
    writing = "A clear claim.\n\nA first reason.\n\nA second reason."
    initial, snapshot_id = initial_state(writing)
    initial_issues = [
        issue_for(writing, "A clear claim.", "goal_1"),
        issue_for(writing, "A first reason.", "goal_2"),
        issue_for(writing, "A second reason.", "goal_3"),
    ]
    first_revision_text = writing.replace(
        "A clear claim.", "A clear claim with a specific purpose."
    )
    first_observations = [
        observation_for("goal_1", "specific_improvement"),
        observation_for(
            "goal_2",
            "improvement_not_yet_evident",
            observation="The selected goal can be carried forward.",
            carry_forward=True,
        ),
        observation_for(
            "goal_3",
            "improvement_not_yet_evident",
            observation="The selected goal can be carried forward.",
            carry_forward=True,
        ),
    ]
    client = FakeClient([])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    client.responses = [
        coordinator_payload(initial, issues=initial_issues),
        support_payload({**initial, "issues": initial_issues}),
    ]
    first = service.start_composition("session", initial, snapshot_id)
    selected = first.state["revision_candidates"]
    first_revision, first_snapshot_id = revision_state(
        service,
        initial["composition_id"],
        first_revision_text,
        selected,
        {"goal_1": "attempted", "goal_2": "deferred", "goal_3": "deferred"},
    )
    revision_issues = [
        issue_for(first_revision_text, "A clear claim with a specific purpose.", "goal_1"),
        issue_for(first_revision_text, "A first reason.", "goal_2"),
        issue_for(first_revision_text, "A second reason.", "goal_3"),
    ]
    client.responses = [
        coordinator_payload(
            first_revision,
            issues=revision_issues,
            observations=first_observations,
        ),
        support_payload(
            {
                **first_revision,
                "issues": revision_issues,
                "selected_goal_observations": first_observations,
            }
        ),
    ]

    reviewed = service.submit_revision(
        "session", first_revision, first_snapshot_id
    )

    assert len(reviewed.state["goal_feedback"]) == 3
    assert [item["status"] for item in reviewed.state["goal_feedback"]] == [
        "specific_improvement",
        "improvement_not_yet_evident",
        "improvement_not_yet_evident",
    ]
    snapshot = service.storage.get_snapshot(initial["composition_id"], 1)
    assert snapshot.goal_self_reports == {
        "goal_1": "attempted",
        "goal_2": "deferred",
        "goal_3": "deferred",
    }

    second_selected = [
        candidate
        for candidate in reviewed.state["revision_candidates"]
        if candidate["goal_id"] == "goal_2"
    ]
    second_revision_text = first_revision_text.replace(
        "A first reason.", "A first reason now explains its connection."
    )
    second_revision, second_snapshot_id = revision_state(
        service,
        initial["composition_id"],
        second_revision_text,
        second_selected,
        {"goal_2": "attempted"},
    )
    second_observation = observation_for("goal_2", "specific_improvement")
    client.responses = [
        coordinator_payload(
            second_revision,
            route="direct_response",
            issues=[],
            observations=[second_observation],
        )
    ]

    second = service.submit_revision(
        "session", second_revision, second_snapshot_id
    )

    assert second.state["routing_decision"] == "direct_response"
    assert second.state["goal_feedback"] == [second_observation]
    assert second.state["revision_candidates"] == []
    assert len(service.storage.list_snapshots(initial["composition_id"])) == 3
    assert len(client.calls) == 5


def test_failed_final_reflection_retries_without_duplicate_snapshots(tmp_path):
    initial, snapshot_id = initial_state()
    client = FakeClient([])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    client.responses = [coordinator_payload(initial, route="direct_response")]
    service.start_composition("session", initial, snapshot_id)
    revision, revision_snapshot_id = revision_state(
        service, initial["composition_id"], INITIAL_DRAFT, []
    )
    service.storage.create_revision("session", revision, revision_snapshot_id)
    final, original_id, final_id = final_state(service, initial["composition_id"])
    coordinator = final_coordinator_payload(final, changed=False)
    values = json.loads(coordinator)
    final_handoff = {
        **final,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": [],
        "comparison_regressions": [],
        "future_areas": values["future_areas"],
    }
    client.responses = [
        APIError("Temporary final failure"),
        coordinator,
        final_support_payload(final_handoff),
    ]

    with pytest.raises(APIError):
        service.finish_composition("session", final, original_id, final_id)
    assert service.storage.get_reflection(initial["composition_id"]).status == "failed"

    result = service.retry_final("session", initial["composition_id"])

    assert result.state["final_reflection"]["improvements"] == []
    assert service.storage.get_reflection(initial["composition_id"]).status == "completed"
    assert len(service.storage.list_snapshots(initial["composition_id"])) == 2
