import json
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from agents.prompts import PROMPTS
from agents.utils import DeepSeekClient, ResponseValidationError, parse_json_object
from langgraph_core.state import TeacherFlagCategory, WritingAssistantState


class IssueOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    type: str = Field(min_length=1)
    severity: Literal["high", "medium", "low"]
    description: str = Field(min_length=1)


class AssessmentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    writing_complete: bool
    missing_context: bool
    unclear_intent: bool
    no_issues_found: bool
    strengths: list[str]
    issues: list[IssueOutput] = Field(max_length=5)
    skill_gaps: list[str] = Field(max_length=5)
    routing_decision: Literal[
        "ask_clarification",
        "support_agent",
        "teacher_review",
        "direct_response",
    ]
    flag_teacher: bool
    teacher_flag_reason: str
    teacher_flag_category: TeacherFlagCategory
    teacher_evidence: list[str] = Field(max_length=5)
    needs_feedback: bool
    needs_practice: bool
    coordinator_reasoning: str = Field(min_length=1)
    clarification_question: str

    @model_validator(mode="after")
    def check_route_details(self):
        self.strengths = self.strengths[:3]
        if self.routing_decision == "ask_clarification" and not self.clarification_question:
            raise ValueError("Clarification routes require a question.")
        if self.routing_decision == "teacher_review" and not self.teacher_flag_reason:
            raise ValueError("Teacher review requires a reason.")
        return self


class AssessmentOutputV2(AssessmentOutput):
    revision_need: Literal["not_applicable", "light_touch", "standard"]

    @model_validator(mode="after")
    def check_revision_need(self):
        if self.routing_decision == "support_agent":
            if self.revision_need == "not_applicable":
                raise ValueError("Support routes require light_touch or standard revision need.")
            if self.revision_need == "light_touch" and len(self.issues) != 1:
                raise ValueError("Light-touch support requires exactly one issue.")
        elif self.revision_need != "not_applicable":
            raise ValueError("Non-support routes require not_applicable revision need.")
        return self


@dataclass
class AssessmentResult:
    values: dict[str, Any]
    raw_responses: list[str]
    messages: list[dict[str, str]]

    @property
    def raw_response(self) -> str:
        return self.raw_responses[-1]


class AssessmentCoordinator:
    def __init__(self, client: DeepSeekClient, version: str = "v1"):
        self.client = client
        self.version = version

    def _messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload = {
            "writing": state["writing"],
            "grade_level": state["grade_level"],
            "assignment_context": state.get("assignment_context", ""),
            "student_concerns": state.get("student_concerns", ""),
            "clarification_history": state.get("clarification_history", []),
        }
        if self.version == "v2":
            payload["affect_check_in"] = state.get("affect_check_in", "")
        return [
            {"role": "system", "content": PROMPTS[self.version]["coordinator"]},
            {
                "role": "user",
                "content": "Assess this submission and return the required JSON object:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    @staticmethod
    def _fallback_values(state: WritingAssistantState | None = None) -> dict[str, Any]:
        question = (
            "Is this a complete draft you want feedback on, or an outline or idea "
            "you want help developing?"
        )
        history = state.get("clarification_history", []) if state else []
        if history:
            answer = history[-1].get("answer", "").strip()
            if len(answer) > 180:
                answer = answer[:177].rstrip() + "..."
            question = (
                f'You explained: "{answer}" Which should I focus on first: developing '
                "your ideas, organizing your paragraphs, or improving your sentences?"
            )
        values = {
            "writing_complete": False,
            "missing_context": True,
            "unclear_intent": True,
            "no_issues_found": False,
            "strengths": [],
            "issues": [],
            "skill_gaps": [],
            "routing_decision": "ask_clarification",
            "flag_teacher": False,
            "teacher_flag_reason": "",
            "teacher_flag_category": "none",
            "teacher_evidence": [],
            "needs_feedback": False,
            "needs_practice": False,
            "coordinator_reasoning": (
                "The assessment response could not be validated, so the safe fallback "
                "is to clarify the student's goal."
            ),
            "clarification_question": question,
        }
        if state and state.get("app_version") == "v2":
            values["revision_need"] = "not_applicable"
        return values

    @staticmethod
    def _safety_fallback(raw: dict[str, Any]) -> dict[str, Any]:
        values = AssessmentCoordinator._fallback_values()
        category = raw.get("teacher_flag_category")
        if category not in ("concerning_content", "frustration", "clarification_limit"):
            category = "concerning_content"
        evidence = raw.get("teacher_evidence")
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) for item in evidence
        ):
            evidence = []
        reason = raw.get("teacher_flag_reason")
        if not isinstance(reason, str) or not reason.strip():
            reason = (
                "The coordinator flagged this submission for human review, but some "
                "assessment details could not be validated."
            )
        values.update(
            {
                "routing_decision": "teacher_review",
                "flag_teacher": True,
                "teacher_flag_reason": reason.strip(),
                "teacher_flag_category": category,
                "teacher_evidence": evidence[:5],
                "coordinator_reasoning": "A teacher flag overrides malformed assessment details.",
            }
        )
        return values

    @staticmethod
    def _normalize(values: dict[str, Any]) -> dict[str, Any]:
        route = values["routing_decision"]
        if route == "teacher_review":
            values["flag_teacher"] = True
            values["needs_feedback"] = False
            values["needs_practice"] = False
            if values["teacher_flag_category"] == "none":
                values["teacher_flag_category"] = "concerning_content"
        elif route == "support_agent":
            values["needs_feedback"] = True
            values["no_issues_found"] = False
            if not values["skill_gaps"] or values.get("revision_need") == "light_touch":
                values["needs_practice"] = False
        elif route == "direct_response":
            values["no_issues_found"] = True
            values["needs_feedback"] = False
            values["needs_practice"] = False
        else:
            values["needs_feedback"] = False
            values["needs_practice"] = False
        if "revision_need" in values and route != "support_agent":
            values["revision_need"] = "not_applicable"
        values["coordinator_decision"] = route
        return values

    def _values_from_response(self, raw_response: str) -> dict[str, Any]:
        raw = parse_json_object(raw_response)
        output_class = AssessmentOutputV2 if self.version == "v2" else AssessmentOutput
        if raw.get("flag_teacher") is True:
            try:
                assessment = output_class.model_validate(raw)
            except ValidationError:
                return self._safety_fallback(raw)
        else:
            assessment = output_class.model_validate(raw)
        return assessment.model_dump()

    def run(self, state: WritingAssistantState) -> AssessmentResult:
        messages = self._messages(state)
        raw_response = self.client.chat_completion(messages, json_mode=True)
        raw_responses = [raw_response]
        repair_count = 0
        try:
            values = self._values_from_response(raw_response)
        except (ResponseValidationError, ValidationError) as exc:
            if self.version != "v2":
                values = self._fallback_values()
            else:
                repair_count = 1
                messages = [
                    *messages,
                    {"role": "assistant", "content": raw_response},
                    {
                        "role": "user",
                        "content": (
                            "The previous response failed validation. Return only a corrected "
                            "complete JSON object that follows the system schema. Use the "
                            "original submission and clarification history, preserve any "
                            "teacher flag, and do not explain the correction. Validation error: "
                            f"{str(exc)[:2000]}"
                        ),
                    },
                ]
                raw_response = self.client.chat_completion(messages, json_mode=True)
                raw_responses.append(raw_response)
                try:
                    values = self._values_from_response(raw_response)
                except (ResponseValidationError, ValidationError):
                    values = self._fallback_values(state)
                    values["coordinator_reasoning"] = (
                        "The assessment and its single correction attempt could not be "
                        "validated, so the safe fallback uses the existing clarification "
                        "history to ask a context-sensitive question."
                    )
        if self.version == "v2":
            values.setdefault("revision_need", "not_applicable")
            values["coordinator_repair_count"] = repair_count
        return AssessmentResult(
            values=self._normalize(values),
            raw_responses=raw_responses,
            messages=messages,
        )
