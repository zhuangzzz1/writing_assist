import json
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agents.prompts import PROMPTS
from agents.utils import DeepSeekClient, ResponseValidationError, parse_json_object
from langgraph_core.state import WritingAssistantState


class PriorityOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    title: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    example_from_writing: str = Field(min_length=1)
    next_step: str = Field(min_length=1)


class PracticeOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    skill: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    steps: list[str] = Field(min_length=2, max_length=4)
    worked_example: str = Field(min_length=1)
    success_check: str = Field(min_length=1)


class SupportOutput(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    strengths: list[str] = Field(min_length=1, max_length=3)
    priorities: list[PriorityOutput] = Field(min_length=2, max_length=3)
    practice: PracticeOutput | None


@dataclass
class SupportResult:
    values: dict[str, Any]
    raw_response: str
    messages: list[dict[str, str]]


class InstructionalSupportAgent:
    def __init__(self, client: DeepSeekClient, version: str = "v1"):
        self.client = client
        self.version = version

    def _messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload = {
            "writing": state["writing"],
            "grade_level": state["grade_level"],
            "assignment_context": state.get("assignment_context", ""),
            "student_concerns": state.get("student_concerns", ""),
            "strengths_identified": state.get("strengths", []),
            "issues": state.get("issues", []),
            "skill_gaps": state.get("skill_gaps", []),
            "needs_feedback": state.get("needs_feedback", True),
            "needs_practice": state.get("needs_practice", False),
            "coordinator_rationale": state.get("coordinator_reasoning", ""),
        }
        return [
            {"role": "system", "content": PROMPTS[self.version]["support"]},
            {
                "role": "user",
                "content": "Provide the required support JSON for this assessment:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    @staticmethod
    def _format_feedback(output: SupportOutput) -> str:
        lines = ["## What is working well"]
        lines.extend(f"- {strength}" for strength in output.strengths)
        lines.append("\n## Your next revision steps")
        for index, priority in enumerate(output.priorities, start=1):
            lines.extend(
                [
                    f"### {index}. {priority.title}",
                    priority.why_it_matters,
                    f"**Example from your writing:** {priority.example_from_writing}",
                    f"**Try this:** {priority.next_step}",
                ]
            )
        return "\n\n".join(lines)

    @staticmethod
    def _format_practice(practice: PracticeOutput) -> str:
        lines = [
            f"## Targeted practice: {practice.skill}",
            practice.instructions,
        ]
        lines.extend(f"{index}. {step}" for index, step in enumerate(practice.steps, 1))
        lines.extend(
            [
                f"**Brief example:** {practice.worked_example}",
                f"**Check your attempt:** {practice.success_check}",
            ]
        )
        return "\n\n".join(lines)

    def run(self, state: WritingAssistantState) -> SupportResult:
        messages = self._messages(state)
        raw_response = self.client.chat_completion(messages, json_mode=True)
        try:
            output = SupportOutput.model_validate(parse_json_object(raw_response))
        except (ResponseValidationError, ValidationError) as exc:
            raise ResponseValidationError(
                "The Support Agent returned an invalid feedback structure."
            ) from exc
        if state.get("needs_practice") and output.practice is None:
            raise ResponseValidationError(
                "The Support Agent did not provide the requested practice exercise."
            )

        feedback = self._format_feedback(output)
        practice_exercises: list[dict[str, Any]] = []
        student_output = feedback
        if state.get("needs_practice") and output.practice is not None:
            practice_exercises = [output.practice.model_dump()]
            student_output += "\n\n" + self._format_practice(output.practice)

        return SupportResult(
            values={
                "feedback_type": "scaffolded",
                "feedback_content": feedback,
                "feedback_strengths": output.strengths,
                "feedback_priorities": [
                    priority.model_dump() for priority in output.priorities
                ],
                "practice_exercises": practice_exercises,
                "student_output": student_output,
            },
            raw_response=raw_response,
            messages=messages,
        )
