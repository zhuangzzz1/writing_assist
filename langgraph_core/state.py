from typing import Any, Literal, NotRequired, TypedDict

from agents.utils import validate_writing_input


GradeLevel = Literal["5th Grade", "6th Grade", "7th Grade"]
RoutingDecision = Literal[
    "ask_clarification",
    "support_agent",
    "teacher_review",
    "direct_response",
]
TeacherFlagCategory = Literal[
    "none",
    "concerning_content",
    "frustration",
    "clarification_limit",
]
AffectCheckIn = Literal["", "ready", "unsure", "frustrated"]
RevisionNeed = Literal["not_applicable", "light_touch", "standard"]


class ClarificationTurn(TypedDict):
    question: str
    answer: str


class WritingAssistantState(TypedDict):
    writing: str
    grade_level: GradeLevel
    assignment_context: str
    student_concerns: str
    affect_check_in: AffectCheckIn
    app_version: str
    debug_enabled: bool
    clarification_history: list[ClarificationTurn]
    clarification_count: int
    agent_path: list[str]
    execution_logs: list[dict[str, Any]]
    timestamps: dict[str, float]

    writing_complete: NotRequired[bool]
    missing_context: NotRequired[bool]
    unclear_intent: NotRequired[bool]
    no_issues_found: NotRequired[bool]
    revision_need: NotRequired[RevisionNeed]
    strengths: NotRequired[list[str]]
    issues: NotRequired[list[dict[str, Any]]]
    skill_gaps: NotRequired[list[str]]
    routing_decision: NotRequired[RoutingDecision]
    flag_teacher: NotRequired[bool]
    teacher_flag_reason: NotRequired[str]
    teacher_flag_category: NotRequired[TeacherFlagCategory]
    teacher_evidence: NotRequired[list[str]]
    needs_feedback: NotRequired[bool]
    needs_practice: NotRequired[bool]
    coordinator_decision: NotRequired[str]
    coordinator_reasoning: NotRequired[str]
    coordinator_repair_count: NotRequired[int]
    clarification_question: NotRequired[str]

    feedback_type: NotRequired[Literal["scaffolded", "direct"]]
    feedback_content: NotRequired[str]
    feedback_strengths: NotRequired[list[str]]
    feedback_priorities: NotRequired[list[dict[str, Any]]]
    practice_exercises: NotRequired[list[dict[str, Any]]]
    student_output: NotRequired[str]
    teacher_message: NotRequired[str]


def make_initial_state(
    writing: str,
    grade_level: GradeLevel,
    assignment_context: str = "",
    student_concerns: str = "",
    app_version: str = "v1",
    debug_enabled: bool = False,
    affect_check_in: AffectCheckIn = "",
) -> WritingAssistantState:
    if grade_level not in ("5th Grade", "6th Grade", "7th Grade"):
        raise ValueError("Unsupported grade level.")
    if affect_check_in not in ("", "ready", "unsure", "frustrated"):
        raise ValueError("Unsupported affect check-in.")
    return {
        "writing": validate_writing_input(writing),
        "grade_level": grade_level,
        "assignment_context": assignment_context.strip(),
        "student_concerns": student_concerns.strip(),
        "affect_check_in": affect_check_in,
        "app_version": app_version,
        "debug_enabled": debug_enabled,
        "clarification_history": [],
        "clarification_count": 0,
        "agent_path": [],
        "execution_logs": [],
        "timestamps": {},
    }
