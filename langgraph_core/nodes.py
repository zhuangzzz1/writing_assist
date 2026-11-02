import time
from typing import Any

from langgraph.types import interrupt

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import InputValidationError
from langgraph_core.state import WritingAssistantState


def _with_metadata(
    state: WritingAssistantState,
    values: dict[str, Any],
    node: str,
    display_name: str,
    wall_started: float,
    timer_started: float,
    messages: list[dict[str, str]] | None = None,
    raw_response: str | list[str] | None = None,
) -> dict[str, Any]:
    raw_responses = (
        [raw_response]
        if isinstance(raw_response, str)
        else list(raw_response or [])
    )
    log: dict[str, Any] = {
        "node": node,
        "display_name": display_name,
        "timestamp": wall_started,
        "duration_ms": max(0, round((time.perf_counter() - timer_started) * 1000)),
        "state_changes": values.copy(),
        "api_call": bool(raw_responses),
        "api_calls": len(raw_responses),
    }
    if state.get("debug_enabled") and messages is not None:
        log["prompt"] = messages
        log["raw_response"] = raw_responses[-1] if raw_responses else None
        if len(raw_responses) > 1:
            log["raw_responses"] = raw_responses
    values["agent_path"] = [*state.get("agent_path", []), display_name]
    values["execution_logs"] = [*state.get("execution_logs", []), log]
    values["timestamps"] = {**state.get("timestamps", {}), node: wall_started}
    return values


def make_assessment_node(coordinator: AssessmentCoordinator):
    def assessment_node(state: WritingAssistantState) -> dict[str, Any]:
        wall_started = time.time()
        timer_started = time.perf_counter()
        result = coordinator.run(state)
        values = result.values
        clarification_count = state.get("clarification_count", 0)
        values["clarification_count"] = clarification_count
        if values["routing_decision"] == "ask_clarification":
            if clarification_count >= 2:
                history = state.get("clarification_history", [])
                values.update(
                    {
                        "routing_decision": "teacher_review",
                        "coordinator_decision": "teacher_review",
                        "flag_teacher": True,
                        "teacher_flag_category": "clarification_limit",
                        "teacher_flag_reason": (
                            "The student's goal remains unclear after two clarification answers."
                        ),
                        "teacher_evidence": [
                            f"Question: {turn['question']} Answer: {turn['answer']}"
                            for turn in history
                        ],
                        "coordinator_reasoning": (
                            "The clarification limit was reached, so the system stopped "
                            "and requested non-safety human review."
                        ),
                        "needs_feedback": False,
                        "needs_practice": False,
                    }
                )
            else:
                values["clarification_count"] = clarification_count + 1
        return _with_metadata(
            state,
            values,
            "assessment_coordinator",
            "Assessment Coordinator",
            wall_started,
            timer_started,
            result.messages,
            result.raw_responses,
        )

    return assessment_node


def clarification_node(state: WritingAssistantState) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    question = state.get("clarification_question") or (
        "What kind of help would you like with this writing?"
    )
    answer = interrupt(
        {
            "question": question,
            "clarification_number": state.get("clarification_count", 1),
        }
    )
    if not isinstance(answer, str) or not answer.strip():
        raise InputValidationError("Write a short answer before resuming the analysis.")
    turn = {"question": question, "answer": answer.strip()}
    values = {
        "clarification_history": [*state.get("clarification_history", []), turn]
    }
    return _with_metadata(
        state,
        values,
        "clarification",
        "Clarification",
        wall_started,
        timer_started,
    )


def make_support_node(support_agent: InstructionalSupportAgent):
    def support_node(state: WritingAssistantState) -> dict[str, Any]:
        wall_started = time.time()
        timer_started = time.perf_counter()
        result = support_agent.run(state)
        return _with_metadata(
            state,
            result.values,
            "support_agent",
            "Instructional Support Agent",
            wall_started,
            timer_started,
            result.messages,
            result.raw_responses,
        )

    return support_node


def teacher_review_node(state: WritingAssistantState) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    category = state.get("teacher_flag_category", "concerning_content")
    if category == "frustration":
        student_output = (
            "You have put a lot of effort into this draft, and it makes sense to feel "
            "discouraged after revising it so many times. You do not need to keep "
            "guessing alone.\n\n"
            "Please show your draft and your concern to a teacher or another trusted "
            "adult so you can decide on the next step together. This message is not a "
            "grade or a criticism of your writing."
        )
        follow_up = "Offer a one-to-one check-in about repeated revision fatigue and grades."
    elif category == "clarification_limit":
        student_output = (
            "I still am not sure what kind of writing help you want, and I do not want "
            "to guess and give you the wrong kind of feedback.\n\n"
            "Please ask a teacher or another trusted adult to help you describe the "
            "assignment and the help you need. Then you can return with that information."
        )
        follow_up = "Help the student define the assignment and the requested writing support."
    else:
        student_output = (
            "Thank you for sharing something so personal. What you have written takes "
            "courage.\n\n"
            "Please show this to a teacher or another trusted adult before you continue "
            "with writing feedback. Some of what you shared matters more than an essay "
            "grade right now. A school counselor or another trusted adult can listen "
            "and help you decide what to do next."
        )
        follow_up = "Review the submission and arrange an appropriate human check-in."

    reason = state.get("teacher_flag_reason", "Human review was requested.")
    evidence = state.get("teacher_evidence", [])
    teacher_lines = [
        "**Simulated teacher review — no teacher has been notified.**",
        f"**Category:** {category}",
        f"**Reason:** {reason}",
        f"**Recommended follow-up:** {follow_up}",
    ]
    if evidence:
        teacher_lines.append("**Evidence:**")
        teacher_lines.extend(f"- {item}" for item in evidence)
    values = {
        "student_output": student_output,
        "teacher_message": "\n\n".join(teacher_lines),
    }
    return _with_metadata(
        state,
        values,
        "teacher_review",
        "Teacher Review",
        wall_started,
        timer_started,
    )


def direct_response_node(state: WritingAssistantState) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    strengths = state.get("strengths", [])
    lines = [
        "Your draft looks complete and ready for its next audience. I do not have a "
        "priority revision to add right now."
    ]
    if strengths:
        lines.append("What stood out:")
        lines.extend(f"- {strength}" for strength in strengths)
    lines.append(
        "You can share it with your teacher when you are ready. You do not need to "
        "change something just to make a change."
    )
    content = "\n\n".join(lines)
    values = {
        "feedback_type": "direct",
        "feedback_content": content,
        "feedback_strengths": strengths,
        "feedback_priorities": [],
        "practice_exercises": [],
        "student_output": content,
    }
    return _with_metadata(
        state,
        values,
        "direct_response",
        "Direct Response",
        wall_started,
        timer_started,
    )
