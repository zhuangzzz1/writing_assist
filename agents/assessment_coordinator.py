import json
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from agents.prompts import COORDINATOR_FINAL_PROMPT, COORDINATOR_ROUND_PROMPT
from agents.utils import (
    DeepSeekClient,
    ResponseValidationError,
    ensure_bounded_language,
    parse_json_object,
)
from langgraph_core.assignment import language_corrections_optional
from langgraph_core.revision import (
    build_text_diff,
    reference_is_valid,
    reference_overlaps_change,
)
from langgraph_core.state import (
    Genre,
    ObservationStatus,
    RoutingDecision,
    TeacherFlagCategory,
    WritingAssistantState,
)


class IssueOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    category: Literal[
        "central_idea",
        "task_alignment",
        "evidence_elaboration",
        "organization",
        "language_conventions",
        "source_use",
    ]
    description: str = Field(min_length=1)
    draft_reference: str = Field(min_length=1)
    paragraph_number: int = Field(ge=1)
    occurrence: int = Field(ge=1)
    source_dependent: bool
    source_location: str = ""
    regression: bool = False
    obscures_meaning: bool | None = None


class GoalObservationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal_id: str = Field(min_length=1)
    status: ObservationStatus
    observation: str = Field(min_length=1)
    evidence_reference: str = ""
    carry_forward: bool


class FrameworkCoverageOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    framework: str = Field(min_length=1, max_length=80)
    component: str = Field(min_length=1, max_length=80)
    status: Literal["present", "issue"]
    reference: str = ""
    paragraph_number: int | None = None
    occurrence: int | None = None
    goal_id: str = ""

    @model_validator(mode="after")
    def check_status_details(self):
        if self.status == "present":
            if not self.reference or not self.paragraph_number or not self.occurrence:
                raise ValueError("Present components require an exact located reference.")
            if self.goal_id:
                raise ValueError("Present components cannot reference a revision issue.")
        else:
            if not self.goal_id:
                raise ValueError("Issue components require a Coordinator goal ID.")
            if self.reference or self.paragraph_number is not None or self.occurrence is not None:
                raise ValueError("Issue components use the referenced issue's draft reference.")
        return self


class AssessmentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    working_genre: Genre | Literal[""]
    genre_confidence: Literal["", "low", "medium", "high"]
    genre_basis: str
    strengths: list[str] = Field(max_length=3)
    issues: list[IssueOutput] = Field(max_length=5)
    framework_coverage: list[FrameworkCoverageOutput] = Field(
        default_factory=list, max_length=12
    )
    source_limitations: list[str] = Field(max_length=3)
    selected_goal_observations: list[GoalObservationOutput] = Field(max_length=3)
    routing_decision: RoutingDecision
    flag_teacher: bool
    teacher_flag_reason: str
    teacher_flag_category: TeacherFlagCategory
    teacher_evidence: list[str] = Field(max_length=5)
    coordinator_reasoning: str = Field(min_length=1)
    clarification_question: str = ""
    clarification_choices: list[str] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def check_route_details(self):
        if self.routing_decision == "ask_clarification" and not self.clarification_question:
            raise ValueError("Clarification routes require one question.")
        if self.routing_decision == "teacher_review" and not self.teacher_flag_reason:
            raise ValueError("Teacher review requires a reason.")
        if self.routing_decision == "support_agent" and not self.issues:
            raise ValueError("Support requires at least one meaningful issue.")
        if self.routing_decision == "direct_response" and self.issues:
            raise ValueError("Direct response cannot contain actionable issues.")
        goal_ids = [issue.goal_id for issue in self.issues]
        if len(goal_ids) != len(set(goal_ids)):
            raise ValueError("Issue goal IDs must be unique.")
        observation_ids = [item.goal_id for item in self.selected_goal_observations]
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("Each selected goal can have only one observation.")
        return self


class ComparisonFindingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    finding_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    summary: str = Field(min_length=1)
    original_reference: str = ""
    final_reference: str = ""
    goal_id: str = ""

    @model_validator(mode="after")
    def check_reference(self):
        if not self.original_reference and not self.final_reference:
            raise ValueError("A comparison finding needs an exact draft reference.")
        return self


class FinalAssessmentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    original_strengths: list[str] = Field(max_length=3)
    improvements: list[ComparisonFindingOutput] = Field(max_length=5)
    regressions: list[ComparisonFindingOutput] = Field(max_length=3)
    future_areas: list[str] = Field(max_length=3)
    coordinator_reasoning: str = Field(min_length=1)

    @model_validator(mode="after")
    def check_finding_ids(self):
        finding_ids = [
            finding.finding_id for finding in [*self.improvements, *self.regressions]
        ]
        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError("Comparison finding IDs must be unique.")
        return self


@dataclass
class AssessmentResult:
    values: dict[str, Any]
    raw_responses: list[str]
    messages: list[dict[str, str]]
    model_calls: list[dict[str, Any]]

    @property
    def raw_response(self) -> str:
        return self.raw_responses[-1]


class AssessmentCoordinator:
    def __init__(self, client: DeepSeekClient):
        self.client = client

    def _round_messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload: dict[str, Any] = {
            "current_draft": state["writing"],
            "grade_level": state["grade_level"],
            "genre_selection": state["genre_selection"],
            "assignment_prompt": state["assignment_prompt"],
            "teacher_directions": state["teacher_directions"],
            "framework_name": state.get("framework_name", ""),
            "framework_components": state.get("framework_components", []),
            "source_material_available": state["source_material_available"],
            "source_material": state["source_material"],
            "student_concerns": state["student_concerns"],
            "clarification_history": state["clarification_history"],
            "revision_number": state["revision_number"],
        }
        if state["revision_number"] > 0:
            payload.update(
                {
                    "original_draft": state["original_writing"],
                    "previous_draft": state["previous_writing"],
                    "text_diff": state["text_diff"],
                    "selected_goals": state["selected_goals"],
                    "goal_self_reports": state["goal_self_reports"],
                }
            )
        return [
            {"role": "system", "content": COORDINATOR_ROUND_PROMPT},
            {
                "role": "user",
                "content": "Assess this submission and return the required JSON object:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    def _final_messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload = {
            "original_draft": state["original_writing"],
            "final_submitted_draft": state["writing"],
            "grade_level": state["grade_level"],
            "working_genre": state.get("working_genre", ""),
            "assignment_prompt": state["assignment_prompt"],
            "teacher_directions": state["teacher_directions"],
            "framework_name": state.get("framework_name", ""),
            "framework_components": state.get("framework_components", []),
            "source_material_available": state["source_material_available"],
            "source_material": state["source_material"],
            "text_diff": state["text_diff"],
            "revision_history": state.get("revision_history", []),
        }
        return [
            {"role": "system", "content": COORDINATOR_FINAL_PROMPT},
            {
                "role": "user",
                "content": "Compare these submitted drafts and return the required JSON:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    def _metadata(self) -> dict[str, Any]:
        metadata = getattr(self.client, "last_response_metadata", {})
        if metadata:
            return dict(metadata)
        config = self.client.model_config() if hasattr(self.client, "model_config") else {}
        return {**config, "token_usage": {}}

    @staticmethod
    def _fallback_values(state: WritingAssistantState) -> dict[str, Any]:
        history = state.get("clarification_history", [])
        question = (
            "What would you like help with: your main idea, your organization, or "
            "your sentences? You can also describe a different goal."
        )
        if history:
            answer = history[-1].get("answer", "").strip()
            if len(answer) > 180:
                answer = answer[:177].rstrip() + "..."
            question = (
                f'You answered: "{answer}" What is one thing you want your reader '
                "to understand or notice in this draft?"
            )
        return {
            "working_genre": (
                state["genre_selection"] if state["genre_selection"] != "auto" else ""
            ),
            "genre_confidence": "",
            "genre_basis": "",
            "strengths": [],
            "issues": [],
            "framework_coverage": [],
            "source_limitations": [],
            "selected_goal_observations": [],
            "routing_decision": "ask_clarification",
            "flag_teacher": False,
            "teacher_flag_reason": "",
            "teacher_flag_category": "none",
            "teacher_evidence": [],
            "coordinator_reasoning": (
                "The assessment could not be validated, so the system is asking for "
                "essential context instead of guessing."
            ),
            "clarification_question": question,
            "clarification_choices": [],
        }

    @staticmethod
    def _safety_fallback(raw: dict[str, Any]) -> dict[str, Any]:
        category = raw.get("teacher_flag_category")
        if category not in (
            "concerning_content",
            "serious_discouragement",
            "clarification_limit",
        ):
            category = "concerning_content"
        evidence = raw.get("teacher_evidence")
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) for item in evidence
        ):
            evidence = []
        reason = raw.get("teacher_flag_reason")
        if not isinstance(reason, str) or not reason.strip():
            reason = (
                "The Coordinator requested human review, but some assessment details "
                "could not be validated."
            )
        return {
            "working_genre": "",
            "genre_confidence": "",
            "genre_basis": "",
            "strengths": [],
            "issues": [],
            "framework_coverage": [],
            "source_limitations": [],
            "selected_goal_observations": [],
            "routing_decision": "teacher_review",
            "flag_teacher": True,
            "teacher_flag_reason": reason.strip(),
            "teacher_flag_category": category,
            "teacher_evidence": evidence[:5],
            "coordinator_reasoning": "A human-review flag overrides malformed assessment details.",
            "clarification_question": "",
            "clarification_choices": [],
        }

    @staticmethod
    def _validate_round(output: AssessmentOutput, state: WritingAssistantState) -> None:
        selected = state["genre_selection"]
        if selected != "auto" and output.working_genre != selected:
            raise ValueError("The working genre must match the student's explicit selection.")
        if output.routing_decision in ("support_agent", "direct_response"):
            if not output.working_genre:
                raise ValueError("Normal feedback requires a working genre.")
        if language_corrections_optional(state["teacher_directions"]):
            for issue in output.issues:
                if (
                    issue.category == "language_conventions"
                    and issue.obscures_meaning is not True
                ):
                    raise ValueError(
                        "A language mechanics goal requires a true obscures_meaning judgment "
                        "when the teacher marks language corrections as optional."
                    )
        for issue in output.issues:
            if not reference_is_valid(
                state["writing"],
                issue.draft_reference,
                issue.paragraph_number,
                issue.occurrence,
            ):
                raise ValueError(
                    f"Issue {issue.goal_id} does not have an exact, correctly located reference."
                )
            if issue.source_dependent:
                if not state["source_material_available"]:
                    raise ValueError("Source-dependent findings require supplied source material.")
                if not issue.source_location:
                    raise ValueError("Source-dependent findings require a source location.")
            elif issue.source_location:
                raise ValueError("A source location is only valid for source-dependent findings.")

        coverage = output.framework_coverage
        if output.routing_decision not in ("support_agent", "direct_response"):
            if coverage:
                raise ValueError("Boundary routes cannot contain framework assessment.")
        elif state.get("framework_components"):
            framework = state.get("framework_name", "")
            expected = {(framework, component) for component in state["framework_components"]}
            actual = [(item.framework, item.component) for item in coverage]
            if len(actual) != len(expected) or set(actual) != expected:
                raise ValueError("Every required framework component needs exactly one coverage entry.")
            issue_ids = {issue.goal_id for issue in output.issues}
            for item in coverage:
                if item.status == "issue" and item.goal_id not in issue_ids:
                    raise ValueError("Framework issue coverage must reference a Coordinator issue.")
                if item.status == "present" and not reference_is_valid(
                    state["writing"],
                    item.reference,
                    item.paragraph_number,
                    item.occurrence,
                ):
                    raise ValueError("Present framework components require exact located references.")
        elif coverage:
            raise ValueError("Framework coverage requires an explicit framework requirement.")

        if state["revision_number"] > 0 and output.routing_decision in (
            "support_agent",
            "direct_response",
        ):
            expected_ids = [goal["goal_id"] for goal in state["selected_goals"]]
            actual_ids = [item.goal_id for item in output.selected_goal_observations]
            if set(actual_ids) != set(expected_ids) or len(actual_ids) != len(expected_ids):
                raise ValueError("Every selected goal requires exactly one observation.")
            for item in output.selected_goal_observations:
                if item.evidence_reference and not (
                    item.evidence_reference in state["writing"]
                    or item.evidence_reference in state["previous_writing"]
                ):
                    raise ValueError("Goal observation evidence must quote a submitted draft.")
        elif output.selected_goal_observations:
            raise ValueError("Initial and boundary routes cannot contain revision observations.")
        ensure_bounded_language(
            {
                "strengths": output.strengths,
                "issues": [issue.model_dump() for issue in output.issues],
                "source_limitations": output.source_limitations,
                "selected_goal_observations": [
                    item.model_dump() for item in output.selected_goal_observations
                ],
                "clarification_question": output.clarification_question,
                "clarification_choices": output.clarification_choices,
            },
            state["source_material_available"],
        )

    @staticmethod
    def _validate_final(output: FinalAssessmentOutput, state: WritingAssistantState) -> None:
        original = state["original_writing"]
        final = state["writing"]
        actual_diff = build_text_diff(original, final)
        for finding in [*output.improvements, *output.regressions]:
            if finding.original_reference and finding.original_reference not in original:
                raise ValueError("Original comparison references must be exact.")
            if finding.final_reference and finding.final_reference not in final:
                raise ValueError("Final comparison references must be exact.")
        if not actual_diff["changed"] and (output.improvements or output.regressions):
            raise ValueError("Unchanged drafts cannot produce improvement or regression findings.")
        for finding in output.improvements:
            if not finding.final_reference:
                raise ValueError("An improvement requires an exact final-draft reference.")
            if not reference_overlaps_change(
                original, final, finding.final_reference, "after"
            ):
                raise ValueError("An improvement reference must overlap an actual text change.")
        for finding in output.regressions:
            original_changed = bool(finding.original_reference) and reference_overlaps_change(
                original, final, finding.original_reference, "before"
            )
            final_changed = bool(finding.final_reference) and reference_overlaps_change(
                original, final, finding.final_reference, "after"
            )
            if not (original_changed or final_changed):
                raise ValueError("A regression reference must overlap an actual text change.")
        ensure_bounded_language(
            {
                "original_strengths": output.original_strengths,
                "improvements": [item.model_dump() for item in output.improvements],
                "regressions": [item.model_dump() for item in output.regressions],
                "future_areas": output.future_areas,
            },
            state["source_material_available"],
        )

    @staticmethod
    def _normalize_round(values: dict[str, Any]) -> dict[str, Any]:
        if values["flag_teacher"] or values["routing_decision"] == "teacher_review":
            values["routing_decision"] = "teacher_review"
            values["flag_teacher"] = True
            if values["teacher_flag_category"] == "none":
                values["teacher_flag_category"] = "concerning_content"
            if not values["teacher_flag_reason"]:
                values["teacher_flag_reason"] = (
                    "The Coordinator requested human review for this submission."
                )
        else:
            values["flag_teacher"] = False
        values["coordinator_repair_count"] = values.get("coordinator_repair_count", 0)
        return values

    def _round_values(self, raw_response: str, state: WritingAssistantState) -> dict[str, Any]:
        raw = parse_json_object(raw_response)
        if state["genre_selection"] != "auto":
            raw["working_genre"] = state["genre_selection"]
        safety_requested = raw.get("flag_teacher") is True or raw.get(
            "routing_decision"
        ) == "teacher_review"
        try:
            output = AssessmentOutput.model_validate(raw)
            self._validate_round(output, state)
        except (ValidationError, ValueError):
            if safety_requested:
                return self._safety_fallback(raw)
            raise
        return self._normalize_round(output.model_dump())

    def _final_values(self, raw_response: str, state: WritingAssistantState) -> dict[str, Any]:
        output = FinalAssessmentOutput.model_validate(parse_json_object(raw_response))
        self._validate_final(output, state)
        values = output.model_dump()
        values["comparison_improvements"] = values.pop("improvements")
        values["comparison_regressions"] = values.pop("regressions")
        return values

    @staticmethod
    def _repair_messages(
        messages: list[dict[str, str]], raw_response: str, error: Exception
    ) -> list[dict[str, str]]:
        return [
            *messages,
            {"role": "assistant", "content": raw_response},
            {
                "role": "user",
                "content": (
                    "The previous response failed deterministic validation. Return only a "
                    "corrected complete JSON object with exactly the required fields. Preserve "
                    "any human-review flag, keep valid content when possible, use exact draft "
                    "references and locations, and do not explain the correction. Validation "
                    f"error: {str(error)[:2000]}"
                ),
            },
        ]

    def run(self, state: WritingAssistantState) -> AssessmentResult:
        from time import perf_counter

        final_mode = state["review_mode"] == "final"
        messages = self._final_messages(state) if final_mode else self._round_messages(state)
        call_started = perf_counter()
        raw_response = self.client.chat_completion(messages, json_mode=True)
        initial_metadata = self._metadata()
        initial_metadata["latency_ms"] = max(0, round((perf_counter() - call_started) * 1000))
        raw_responses = [raw_response]
        model_calls = [initial_metadata]
        repair_count = 0
        try:
            values = (
                self._final_values(raw_response, state)
                if final_mode
                else self._round_values(raw_response, state)
            )
        except (ResponseValidationError, ValidationError, ValueError) as exc:
            repair_count = 1
            messages = self._repair_messages(messages, raw_response, exc)
            call_started = perf_counter()
            raw_response = self.client.chat_completion(messages, json_mode=True)
            repair_metadata = self._metadata()
            repair_metadata["latency_ms"] = max(0, round((perf_counter() - call_started) * 1000))
            repair_metadata["schema_repair"] = True
            raw_responses.append(raw_response)
            model_calls.append(repair_metadata)
            try:
                values = (
                    self._final_values(raw_response, state)
                    if final_mode
                    else self._round_values(raw_response, state)
                )
            except (ResponseValidationError, ValidationError, ValueError) as repair_exc:
                if final_mode:
                    raise ResponseValidationError(
                        "The final comparison could not be validated after one correction."
                    ) from repair_exc
                values = self._fallback_values(state)
                values["coordinator_reasoning"] = (
                    "The assessment and its single correction could not be validated, "
                    "so the system is asking for essential context instead of guessing."
                )
        values["coordinator_repair_count"] = repair_count
        return AssessmentResult(values, raw_responses, messages, model_calls)
