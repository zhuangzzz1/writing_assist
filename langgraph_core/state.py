from typing import Any, Literal, NotRequired, TypedDict

from agents.utils import (
    MAX_ASSIGNMENT_CHARS,
    MAX_CONCERNS_CHARS,
    MAX_DIRECTIONS_CHARS,
    MAX_SOURCE_CHARS,
    validate_context_input,
    validate_writing_input,
)


GradeLevel = Literal["5th Grade", "6th Grade", "7th Grade"]
Genre = Literal["argument", "informational", "narrative"]
GenreSelection = Literal["auto", "argument", "informational", "narrative"]
RoutingDecision = Literal[
    "ask_clarification",
    "support_agent",
    "teacher_review",
    "direct_response",
]
TeacherFlagCategory = Literal[
    "none",
    "concerning_content",
    "serious_discouragement",
    "clarification_limit",
]
ObservationStatus = Literal[
    "specific_improvement",
    "improvement_not_yet_evident",
    "uncertain",
]
ReviewMode = Literal["round", "final"]

GRADE_LEVELS = ("5th Grade", "6th Grade", "7th Grade")
GENRE_SELECTIONS = ("auto", "argument", "informational", "narrative")
GOAL_SELF_REPORTS = ("", "attempted", "deferred")


class ClarificationTurn(TypedDict):
    question: str
    answer: str


class WritingAssistantState(TypedDict):
    composition_id: str
    round_id: str
    thread_id: str
    review_mode: ReviewMode
    writing: str
    original_writing: str
    previous_writing: str
    grade_level: GradeLevel
    genre_selection: GenreSelection
    assignment_prompt: str
    teacher_directions: str
    source_material: str
    source_material_available: bool
    student_concerns: str
    scenario_id: str
    fixture_version: str
    revision_number: int
    selected_goals: list[dict[str, Any]]
    goal_self_reports: dict[str, str]
    text_diff: dict[str, Any]
    app_version: str
    debug_enabled: bool
    model_config: dict[str, Any]
    clarification_history: list[ClarificationTurn]
    clarification_count: int
    review_stage: str
    agent_path: list[str]
    execution_logs: list[dict[str, Any]]
    timestamps: dict[str, float]

    working_genre: NotRequired[Genre | Literal[""]]
    genre_confidence: NotRequired[Literal["", "low", "medium", "high"]]
    genre_basis: NotRequired[str]
    strengths: NotRequired[list[str]]
    issues: NotRequired[list[dict[str, Any]]]
    source_limitations: NotRequired[list[str]]
    routing_decision: NotRequired[RoutingDecision]
    flag_teacher: NotRequired[bool]
    teacher_flag_reason: NotRequired[str]
    teacher_flag_category: NotRequired[TeacherFlagCategory]
    teacher_evidence: NotRequired[list[str]]
    selected_goal_observations: NotRequired[list[dict[str, Any]]]
    coordinator_reasoning: NotRequired[str]
    coordinator_repair_count: NotRequired[int]
    clarification_question: NotRequired[str]
    clarification_choices: NotRequired[list[str]]

    feedback_strengths: NotRequired[list[str]]
    revision_candidates: NotRequired[list[dict[str, Any]]]
    goal_feedback: NotRequired[list[dict[str, Any]]]
    student_output: NotRequired[str]
    teacher_message: NotRequired[str]

    original_strengths: NotRequired[list[str]]
    comparison_improvements: NotRequired[list[dict[str, Any]]]
    comparison_regressions: NotRequired[list[dict[str, Any]]]
    future_areas: NotRequired[list[str]]
    final_reflection: NotRequired[dict[str, Any]]


def make_review_state(
    writing: str,
    grade_level: GradeLevel,
    *,
    composition_id: str = "",
    round_id: str = "",
    thread_id: str = "",
    review_mode: ReviewMode = "round",
    original_writing: str | None = None,
    previous_writing: str = "",
    genre_selection: GenreSelection = "auto",
    assignment_prompt: str = "",
    teacher_directions: str = "",
    source_material: str = "",
    student_concerns: str = "",
    scenario_id: str = "",
    fixture_version: str = "",
    revision_number: int = 0,
    selected_goals: list[dict[str, Any]] | None = None,
    goal_self_reports: dict[str, str] | None = None,
    text_diff: dict[str, Any] | None = None,
    debug_enabled: bool = False,
    model_config: dict[str, Any] | None = None,
) -> WritingAssistantState:
    if grade_level not in GRADE_LEVELS:
        raise ValueError("Unsupported grade level.")
    if genre_selection not in GENRE_SELECTIONS:
        raise ValueError("Unsupported genre selection.")
    if review_mode not in ("round", "final"):
        raise ValueError("Unsupported review mode.")
    if revision_number < 0:
        raise ValueError("Revision number cannot be negative.")

    original = validate_writing_input(
        writing if original_writing is None else original_writing,
        label="draft",
    )
    current = validate_writing_input(writing, label="draft")
    previous = (
        validate_writing_input(previous_writing, label="previous draft")
        if previous_writing
        else ""
    )
    reports = dict(goal_self_reports or {})
    if any(value not in GOAL_SELF_REPORTS for value in reports.values()):
        raise ValueError("Unsupported goal self-report.")
    assignment_prompt = validate_context_input(
        assignment_prompt, "Assignment prompt", MAX_ASSIGNMENT_CHARS
    ).strip()
    teacher_directions = validate_context_input(
        teacher_directions, "Teacher directions", MAX_DIRECTIONS_CHARS
    ).strip()
    source_material = validate_context_input(
        source_material, "Source material", MAX_SOURCE_CHARS
    ).strip()
    student_concerns = validate_context_input(
        student_concerns, "Student concern", MAX_CONCERNS_CHARS
    ).strip()

    return {
        "composition_id": composition_id,
        "round_id": round_id,
        "thread_id": thread_id,
        "review_mode": review_mode,
        "writing": current,
        "original_writing": original,
        "previous_writing": previous,
        "grade_level": grade_level,
        "genre_selection": genre_selection,
        "assignment_prompt": assignment_prompt.strip(),
        "teacher_directions": teacher_directions.strip(),
        "source_material": source_material.strip(),
        "source_material_available": bool(source_material.strip()),
        "student_concerns": student_concerns.strip(),
        "scenario_id": scenario_id.strip(),
        "fixture_version": fixture_version.strip(),
        "revision_number": revision_number,
        "selected_goals": list(selected_goals or []),
        "goal_self_reports": reports,
        "text_diff": dict(text_diff or {}),
        "app_version": "v3",
        "debug_enabled": debug_enabled,
        "model_config": dict(model_config or {}),
        "clarification_history": [],
        "clarification_count": 0,
        "review_stage": "draft_saved",
        "agent_path": [],
        "execution_logs": [],
        "timestamps": {},
    }
