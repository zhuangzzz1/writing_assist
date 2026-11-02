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


@dataclass
class AssessmentResult:
    values: dict[str, Any]
    raw_response: str
    messages: list[dict[str, str]]


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
        return [
            {"role": "system", "content": PROMPTS[self.version]["coordinator"]},
            {
                "role": "user",
                "content": "Assess this submission and return the required JSON object:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    @staticmethod
    def _fallback_values() -> dict[str, Any]:
        return {
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
            "clarification_question": (
                "Is this a complete draft you want feedback on, or an outline or idea "
                "you want help developing?"
            ),
        }

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
            if not values["skill_gaps"]:
                values["needs_practice"] = False
        elif route == "direct_response":
            values["no_issues_found"] = True
            values["needs_feedback"] = False
            values["needs_practice"] = False
        else:
            values["needs_feedback"] = False
            values["needs_practice"] = False
        values["coordinator_decision"] = route
        return values

    def run(self, state: WritingAssistantState) -> AssessmentResult:
        messages = self._messages(state)
        raw_response = self.client.chat_completion(messages, json_mode=True)
        try:
            raw = parse_json_object(raw_response)
            if raw.get("flag_teacher") is True:
                try:
                    assessment = AssessmentOutput.model_validate(raw)
                    values = assessment.model_dump()
                except ValidationError:
                    values = self._safety_fallback(raw)
            else:
                assessment = AssessmentOutput.model_validate(raw)
                values = assessment.model_dump()
        except (ResponseValidationError, ValidationError):
            values = self._fallback_values()
        return AssessmentResult(
            values=self._normalize(values),
            raw_response=raw_response,
            messages=messages,
        )
