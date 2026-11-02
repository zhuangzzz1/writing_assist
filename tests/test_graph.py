import uuid

import pytest

from agents.utils import InputValidationError, ResponseValidationError
from langgraph_core.graph import create_writing_assistant_service
from langgraph_core.state import make_initial_state
from tests.helpers import (
    FakeClient,
    coordinator_payload,
    coordinator_payload_v2,
    support_payload,
    support_payload_v2,
)


def state_for(route="support_agent", debug=False):
    return make_initial_state(
        "This is a complete synthetic draft with a clear main idea.",
        "6th Grade",
        assignment_context="Persuasive Essay",
        debug_enabled=debug,
    )


def session_and_thread():
    return uuid.uuid4().hex, uuid.uuid4().hex


def test_normal_route_returns_feedback_practice_and_history(tmp_path):
    client = FakeClient([coordinator_payload(), support_payload()])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()

    result = service.start_run(session_id, thread_id, state_for())

    assert result.pending is False
    assert result.state["routing_decision"] == "support_agent"
    assert len(result.state["practice_exercises"]) == 1
    assert result.state["agent_path"] == [
        "Assessment Coordinator",
        "Instructional Support Agent",
    ]
    record = service.get_run(thread_id)
    assert record.status == "completed"
    assert record.state["student_output"] == result.state["student_output"]


def test_clarification_resumes_exact_thread_after_service_restart(tmp_path):
    database = str(tmp_path / "app.db")
    session_id, thread_id = session_and_thread()
    first = create_writing_assistant_service(
        FakeClient([coordinator_payload("ask_clarification")]), database
    )
    pending = first.start_run(session_id, thread_id, state_for())

    assert pending.pending_question == "Do you want outline help or draft feedback?"
    assert first.get_run(thread_id).status == "awaiting_clarification"

    resumed_service = create_writing_assistant_service(
        FakeClient([coordinator_payload(), support_payload()]), database
    )
    result = resumed_service.resume_run(session_id, thread_id, "I want draft feedback.")

    assert result.pending is False
    assert result.state["clarification_history"] == [
        {
            "question": "Do you want outline help or draft feedback?",
            "answer": "I want draft feedback.",
        }
    ]
    assert result.state["agent_path"] == [
        "Assessment Coordinator",
        "Clarification",
        "Assessment Coordinator",
        "Instructional Support Agent",
    ]


def test_two_unclear_answers_escalate_to_non_safety_teacher_review(tmp_path):
    client = FakeClient(
        [
            coordinator_payload("ask_clarification"),
            coordinator_payload("ask_clarification"),
            coordinator_payload("ask_clarification"),
        ]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()
    service.start_run(session_id, thread_id, state_for())
    service.resume_run(session_id, thread_id, "I am not sure.")

    result = service.resume_run(session_id, thread_id, "Anything, I guess.")

    assert result.state["routing_decision"] == "teacher_review"
    assert result.state["teacher_flag_category"] == "clarification_limit"
    assert result.state["flag_teacher"] is True
    assert len(result.state["clarification_history"]) == 2
    assert "not sure what kind of writing help" in result.state["student_output"]
    assert client.responses == []


def test_boundary_route_bypasses_support_and_separates_audiences(tmp_path):
    client = FakeClient([coordinator_payload("teacher_review")])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()

    result = service.start_run(session_id, thread_id, state_for())

    assert result.state["agent_path"] == ["Assessment Coordinator", "Teacher Review"]
    assert "no teacher has been notified" in result.state["teacher_message"]
    assert "trusted adult" in result.state["student_output"]
    assert "revision" not in result.state["student_output"].lower()


def test_direct_response_affirms_without_practice(tmp_path):
    client = FakeClient([coordinator_payload("direct_response")])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()

    result = service.start_run(session_id, thread_id, state_for())

    assert result.state["feedback_type"] == "direct"
    assert result.state["practice_exercises"] == []
    assert "do not have a priority revision" in result.state["student_output"]


def test_malformed_assessment_pauses_for_clarification(tmp_path):
    service = create_writing_assistant_service(
        FakeClient(["malformed"]), str(tmp_path / "app.db")
    )
    session_id, thread_id = session_and_thread()

    result = service.start_run(session_id, thread_id, state_for())

    assert result.pending is True
    assert result.state["routing_decision"] == "ask_clarification"


def test_debug_logs_contain_prompts_only_when_enabled(tmp_path):
    client = FakeClient([coordinator_payload("direct_response")])
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()

    result = service.start_run(session_id, thread_id, state_for(debug=True))

    assert "prompt" in result.state["execution_logs"][0]
    assert "raw_response" in result.state["execution_logs"][0]


def test_invalid_support_output_marks_run_failed(tmp_path):
    client = FakeClient(
        [coordinator_payload(), support_payload(include_practice=False)]
    )
    service = create_writing_assistant_service(client, str(tmp_path / "app.db"))
    session_id, thread_id = session_and_thread()

    with pytest.raises(ResponseValidationError):
        service.start_run(session_id, thread_id, state_for())
    assert service.get_run(thread_id).status == "failed"


def test_resume_requires_matching_session_and_pending_status(tmp_path):
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload("ask_clarification")]), str(tmp_path / "app.db")
    )
    session_id, thread_id = session_and_thread()
    service.start_run(session_id, thread_id, state_for())

    with pytest.raises(InputValidationError, match="not available"):
        service.resume_run("another-session", thread_id, "Answer")
    with pytest.raises(InputValidationError, match="short answer"):
        service.resume_run(session_id, thread_id, " ")


def test_delete_session_removes_history_and_checkpoint(tmp_path):
    service = create_writing_assistant_service(
        FakeClient([coordinator_payload("ask_clarification")]), str(tmp_path / "app.db")
    )
    session_id, thread_id = session_and_thread()
    service.start_run(session_id, thread_id, state_for())
    config = {"configurable": {"thread_id": thread_id}}
    assert service.checkpointer.get_tuple(config) is not None

    service.delete_session(session_id)

    assert service.list_runs(session_id) == []
    assert service.checkpointer.get_tuple(config) is None


def test_v2_graph_records_repair_calls_and_choice_based_support(tmp_path):
    client = FakeClient(
        [
            "malformed",
            coordinator_payload_v2(),
            support_payload_v2(include_practice=False),
            support_payload_v2(),
        ]
    )
    service = create_writing_assistant_service(
        client, str(tmp_path / "app.db"), version="v2"
    )
    session_id, thread_id = session_and_thread()
    state = state_for(debug=True)
    state["app_version"] = "v2"
    state["affect_check_in"] = "unsure"

    result = service.start_run(session_id, thread_id, state)

    assert result.pending is False
    assert result.state["revision_need"] == "standard"
    assert result.state["coordinator_repair_count"] == 1
    assert len(result.state["practice_exercises"]) == 2
    assessment_log = result.state["execution_logs"][0]
    assert assessment_log["api_calls"] == 2
    assert len(assessment_log["raw_responses"]) == 2
    support_log = result.state["execution_logs"][1]
    assert support_log["api_calls"] == 2
    assert len(support_log["raw_responses"]) == 2
    assert service.get_run(thread_id).status == "completed"


def test_initial_state_rejects_invalid_grade_level():
    with pytest.raises(ValueError, match="grade level"):
        make_initial_state("Synthetic writing", "4th Grade")


def test_initial_state_rejects_invalid_affect_check_in():
    with pytest.raises(ValueError, match="affect"):
        make_initial_state("Synthetic writing", "6th Grade", affect_check_in="angry")


def test_v2_frustrated_boundary_b_reaches_teacher_review(tmp_path):
    from ui.components import load_fixture

    fixture = load_fixture("Boundary B: revision frustration")
    client = FakeClient(
        [
            coordinator_payload_v2(
                "teacher_review",
                teacher_flag_category="frustration",
                teacher_flag_reason="The writer reports repeated revision frustration.",
                teacher_evidence=["I have revised this so many times."],
            )
        ]
    )
    service = create_writing_assistant_service(
        client, str(tmp_path / "app.db"), version="v2"
    )
    session_id, thread_id = session_and_thread()
    state = make_initial_state(
        fixture.writing,
        fixture.grade_level,
        assignment_context=fixture.assignment_context,
        student_concerns=fixture.student_concerns,
        app_version="v2",
        affect_check_in="frustrated",
    )

    result = service.start_run(session_id, thread_id, state)

    assert result.state["affect_check_in"] == "frustrated"
    assert result.state["routing_decision"] == "teacher_review"
    assert result.state["teacher_flag_category"] == "frustration"
    assert result.state["agent_path"] == ["Assessment Coordinator", "Teacher Review"]
    assert "put a lot of effort" in result.state["student_output"]
    assert '"affect_check_in": "frustrated"' in client.calls[0][0][1]["content"]
