import time
from typing import Any

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import InputValidationError
from langgraph_core.state import WritingAssistantState


STAGE_LABELS = {
    "draft_saved": "Draft saved",
    "reviewing": "Reviewing your draft and selected goals",
    "preparing_feedback": "Preparing feedback",
    "complete": "Review complete",
}


def _notify(
    state: WritingAssistantState,
    config: RunnableConfig,
    stage: str,
) -> None:
    callback = config.get("configurable", {}).get("stage_callback")
    if callback:
        callback(STAGE_LABELS[stage])


def _with_metadata(
    state: WritingAssistantState,
    values: dict[str, Any],
    node: str,
    display_name: str,
    wall_started: float,
    timer_started: float,
    messages: list[dict[str, str]] | None = None,
    raw_responses: list[str] | None = None,
    model_calls: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    responses = list(raw_responses or [])
    log: dict[str, Any] = {
        "node": node,
        "display_name": display_name,
        "timestamp": wall_started,
        "duration_ms": max(0, round((time.perf_counter() - timer_started) * 1000)),
        "state_changes": values.copy(),
        "api_calls": len(responses),
        "model_calls": list(model_calls or []),
    }
    if state.get("debug_enabled") and messages is not None:
        log["prompt"] = messages
        log["raw_responses"] = responses
        log["raw_response"] = responses[-1] if responses else None
    values["agent_path"] = [*state.get("agent_path", []), display_name]
    values["execution_logs"] = [*state.get("execution_logs", []), log]
    values["timestamps"] = {**state.get("timestamps", {}), node: wall_started}
    return values


def make_assessment_node(coordinator: AssessmentCoordinator):
    def assessment_node(
        state: WritingAssistantState, config: RunnableConfig
    ) -> dict[str, Any]:
        _notify(state, config, "reviewing")
        wall_started = time.time()
        timer_started = time.perf_counter()
        result = coordinator.run(state)
        values = result.values
        values["review_stage"] = "reviewing"
        if state["review_mode"] == "final":
            values["routing_decision"] = "support_agent"
            values["flag_teacher"] = False
        clarification_count = state.get("clarification_count", 0)
        values["clarification_count"] = clarification_count
        if values["routing_decision"] == "ask_clarification":
            if clarification_count >= 2:
                history = state.get("clarification_history", [])
                values.update(
                    {
                        "routing_decision": "teacher_review",
                        "flag_teacher": True,
                        "teacher_flag_category": "clarification_limit",
                        "teacher_flag_reason": (
                            "Essential context remains unclear after two clarification answers."
                        ),
                        "teacher_evidence": [
                            f"Question: {turn['question']} Answer: {turn['answer']}"
                            for turn in history
                        ],
                        "coordinator_reasoning": (
                            "The clarification limit was reached, so normal feedback stopped "
                            "and non-safety human review was requested."
                        ),
                    }
                )
            else:
                values["clarification_count"] = clarification_count + 1
        if values["routing_decision"] == "support_agent":
            values["review_stage"] = "preparing_feedback"
            _notify(state, config, "preparing_feedback")
        return _with_metadata(
            state,
            values,
            "assessment_coordinator",
            "Assessment Coordinator",
            wall_started,
            timer_started,
            result.messages,
            result.raw_responses,
            result.model_calls,
        )

    return assessment_node


def clarification_node(
    state: WritingAssistantState, config: RunnableConfig
) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    question = state.get("clarification_question") or (
        "What would you like help with in this draft?"
    )
    answer = interrupt(
        {
            "question": question,
            "choices": state.get("clarification_choices", []),
            "clarification_number": state.get("clarification_count", 1),
        }
    )
    if not isinstance(answer, str) or not answer.strip():
        raise InputValidationError("Write a short answer before resuming the review.")
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
    def support_node(
        state: WritingAssistantState, config: RunnableConfig
    ) -> dict[str, Any]:
        wall_started = time.time()
        timer_started = time.perf_counter()
        result = support_agent.run(state)
        values = {**result.values, "review_stage": "complete"}
        _notify(state, config, "complete")
        return _with_metadata(
            state,
            values,
            "support_agent",
            "Instructional Support Agent",
            wall_started,
            timer_started,
            result.messages,
            result.raw_responses,
            result.model_calls,
        )

    return support_node


def teacher_review_node(
    state: WritingAssistantState, config: RunnableConfig
) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    category = state.get("teacher_flag_category", "concerning_content")
    if category == "serious_discouragement":
        student_output = (
            "Thank you for saying how difficult this has been. You do not need to keep "
            "working through serious discouragement alone.\n\n"
            "Please show your draft and your concern to a teacher or another trusted "
            "adult so you can decide on a manageable next step together. This is not a "
            "grade or a criticism of your writing."
        )
        follow_up = "Offer a one-to-one check-in about the student's explicit discouragement."
    elif category == "clarification_limit":
        student_output = (
            "I still do not have enough information to give responsible writing feedback, "
            "and I do not want to guess.\n\n"
            "Please ask a teacher or another trusted adult to help you describe the "
            "assignment and the help you need. Then you can return with that information."
        )
        follow_up = "Help the student clarify the assignment and requested writing support."
    else:
        student_output = (
            "Thank you for sharing something personal. Please show this writing to a "
            "teacher or another trusted adult before continuing with writing feedback.\n\n"
            "What you shared matters more than essay feedback right now. A trusted adult "
            "can listen and help you decide what to do next. No teacher has been notified "
            "automatically."
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
        "review_stage": "complete",
    }
    _notify(state, config, "complete")
    return _with_metadata(
        state,
        values,
        "teacher_review",
        "Teacher Review",
        wall_started,
        timer_started,
    )


def direct_response_node(
    state: WritingAssistantState, config: RunnableConfig
) -> dict[str, Any]:
    wall_started = time.time()
    timer_started = time.perf_counter()
    strengths = state.get("strengths", [])
    lines = [
        "I do not see a meaningful revision issue that you need to act on right now. "
        "You can stop rather than changing your writing just to make a change."
    ]
    if strengths:
        lines.append("What stood out:")
        lines.extend(f"- {strength}" for strength in strengths)
    lines.append("You can choose **Finish and reflect** whenever you are ready to stop.")
    content = "\n\n".join(lines)
    values = {
        "feedback_strengths": strengths,
        "revision_candidates": [],
        "goal_feedback": state.get("selected_goal_observations", []),
        "student_output": content,
        "review_stage": "complete",
    }
    _notify(state, config, "complete")
    return _with_metadata(
        state,
        values,
        "direct_response",
        "Direct Response",
        wall_started,
        timer_started,
    )
