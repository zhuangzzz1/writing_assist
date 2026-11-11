import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from agents.prompts import SUPPORT_FINAL_PROMPT, SUPPORT_ROUND_PROMPT
from agents.utils import (
    NUMERICAL_SCORE,
    PROHIBITED_CLAIMS,
    UNVERIFIABLE_SOURCE_CLAIM,
    DeepSeekClient,
    ResponseValidationError,
    ensure_bounded_language,
    parse_json_object,
)
from langgraph_core.state import ObservationStatus, WritingAssistantState


ALLOWED_SENTENCE_STARTERS = {
    "",
    "____",
    "____ because ____.",
    "this detail matters because ____.",
    "this evidence matters because ____.",
    "according to the passage, ____.",
    "in sum, ____.",
    "one concern is that ____; however, ____.",
    "after ____, ____.",
    "when ____, ____.",
}


class HintOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    passage_reference: str = Field(min_length=1)
    steps: list[str] = Field(min_length=3, max_length=5)
    self_check: str = Field(min_length=1)
    vocabulary_options: list[str] = Field(max_length=4)
    sentence_starter: str

    @model_validator(mode="after")
    def check_scaffold_boundaries(self):
        normalized_starter = " ".join(self.sentence_starter.lower().split())
        if normalized_starter not in ALLOWED_SENTENCE_STARTERS:
            raise ValueError(
                "Sentence starters must be empty or an approved abstract frame that "
                "contains no assigned-topic claim, reason, evidence, or narrative detail."
            )
        if any(re.search(r"\d", option) for option in self.vocabulary_options):
            raise ValueError("Vocabulary options cannot supply numeric evidence answers.")
        if any(not step for step in self.steps):
            raise ValueError("Hint steps cannot be empty.")
        # Steps now require minimum 3 to account for Step 0 (concept restatement) + 2 procedural steps
        if len(self.steps) < 3:
            raise ValueError(
                "Hints must include Step 0 (concept restatement) followed by at least 2 procedural steps."
            )
        return self


class CandidateOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    draft_reference: str = Field(min_length=1)
    paragraph_number: int = Field(ge=1)
    occurrence: int = Field(ge=1)
    revision_action: str = Field(min_length=1)
    hint: HintOutput
    stuck_step: str = Field(min_length=1)


class GoalFeedbackOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    goal_id: str = Field(min_length=1)
    status: ObservationStatus
    observation: str = Field(min_length=1)
    carry_forward: bool


class RoundSupportOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    strengths: list[str] = Field(min_length=1, max_length=3)
    candidates: list[CandidateOutput] = Field(min_length=1, max_length=5)
    goal_feedback: list[GoalFeedbackOutput] = Field(max_length=3)
    source_limitations: list[str] = Field(max_length=3)


class FinalFindingOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    finding_id: str = Field(min_length=1)
    observation: str = Field(min_length=1)
    final_reference: str = ""


class FinalSupportOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    improvements: list[FinalFindingOutput] = Field(max_length=5)
    regressions: list[FinalFindingOutput] = Field(max_length=3)
    conclusion: str = Field(min_length=1)


@dataclass
class SupportResult:
    values: dict[str, Any]
    raw_response: str
    messages: list[dict[str, str]]
    raw_responses: list[str]
    model_calls: list[dict[str, Any]]


class InstructionalSupportAgent:
    def __init__(self, client: DeepSeekClient):
        self.client = client

    def _round_messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload: dict[str, Any] = {
            "current_draft": state["writing"],
            "grade_level": state["grade_level"],
            "working_genre": state.get("working_genre", ""),
            "assignment_prompt": state["assignment_prompt"],
            "teacher_directions": state["teacher_directions"],
            "source_material_available": state["source_material_available"],
            "student_concerns": state["student_concerns"],
            "strengths_identified": state.get("strengths", []),
            "issues": state.get("issues", []),
            "framework_coverage": state.get("framework_coverage", []),
            "source_limitations": state.get("source_limitations", []),
            "selected_goal_observations": state.get("selected_goal_observations", []),
            "goal_self_reports": state["goal_self_reports"],
            "coordinator_rationale": state.get("coordinator_reasoning", ""),
            "revision_number": state["revision_number"],
        }
        if any(
            issue.get("source_dependent") for issue in state.get("issues", [])
        ) or state.get("source_limitations"):
            payload["source_material"] = state["source_material"]
        if state["revision_number"] == 0 or state["clarification_history"]:
            payload["clarification_history"] = state["clarification_history"]
        if state["revision_number"] > 0:
            payload.update(
                {
                    "previous_draft": state["previous_writing"],
                    "text_diff": state["text_diff"],
                    "selected_goals": state["selected_goals"],
                }
            )
        return [
            {"role": "system", "content": SUPPORT_ROUND_PROMPT},
            {
                "role": "user",
                "content": "Provide the required round-feedback JSON for this handoff:\n"
                + json.dumps(payload, ensure_ascii=False),
            },
        ]

    def _final_messages(self, state: WritingAssistantState) -> list[dict[str, str]]:
        payload = {
            "grade_level": state["grade_level"],
            "working_genre": state.get("working_genre", ""),
            "original_strengths": state.get("original_strengths", []),
            "improvements": state.get("comparison_improvements", []),
            "regressions": state.get("comparison_regressions", []),
            "future_areas": state.get("future_areas", []),
            "text_diff": state["text_diff"],
            "revision_history": state.get("revision_history", []),
        }
        return [
            {"role": "system", "content": SUPPORT_FINAL_PROMPT},
            {
                "role": "user",
                "content": "Create the final reflection from these verified findings:\n"
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
    def _validate_round(output: RoundSupportOutput, state: WritingAssistantState) -> None:
        issues = {issue["goal_id"]: issue for issue in state.get("issues", [])}
        candidate_ids = [candidate.goal_id for candidate in output.candidates]
        if len(candidate_ids) != len(set(candidate_ids)) or set(candidate_ids) != set(issues):
            raise ValueError("Support must return exactly one candidate per Coordinator issue.")
        for candidate in output.candidates:
            issue = issues[candidate.goal_id]
            if (
                candidate.draft_reference != issue["draft_reference"]
                or candidate.paragraph_number != issue["paragraph_number"]
                or candidate.occurrence != issue["occurrence"]
                or candidate.hint.passage_reference != candidate.draft_reference
            ):
                raise ValueError("Candidate and hint references must preserve the Coordinator reference.")
        if output.source_limitations != state.get("source_limitations", []):
            raise ValueError("Support must preserve every Coordinator source limitation exactly.")

        expected_observations = {
            item["goal_id"]: item for item in state.get("selected_goal_observations", [])
        }
        actual_observations = {item.goal_id: item for item in output.goal_feedback}
        if len(actual_observations) != len(output.goal_feedback) or set(
            actual_observations
        ) != set(expected_observations):
            raise ValueError("Support must return exactly one feedback item per selected goal.")
        for goal_id, feedback in actual_observations.items():
            expected = expected_observations[goal_id]
            if (
                feedback.status != expected["status"]
                or feedback.carry_forward != expected["carry_forward"]
            ):
                raise ValueError("Support cannot change selected-goal status or carry-forward decisions.")
        ensure_bounded_language(
            output.model_dump(), state["source_material_available"]
        )

    @staticmethod
    def _validate_final(output: FinalSupportOutput, state: WritingAssistantState) -> None:
        for kind, expected_key in (
            ("improvements", "comparison_improvements"),
            ("regressions", "comparison_regressions"),
        ):
            actual_items = getattr(output, kind)
            expected_items = {item["finding_id"]: item for item in state.get(expected_key, [])}
            actual_ids = [item.finding_id for item in actual_items]
            if len(actual_ids) != len(set(actual_ids)) or set(actual_ids) != set(expected_items):
                raise ValueError(f"Final {kind} must match every Coordinator finding.")
            for item in actual_items:
                if item.final_reference != expected_items[item.finding_id]["final_reference"]:
                    raise ValueError("Final references must match the verified Coordinator references.")
        ensure_bounded_language(output.model_dump(), state["source_material_available"])

    def _round_values(self, raw_response: str, state: WritingAssistantState) -> dict[str, Any]:
        output = RoundSupportOutput.model_validate(parse_json_object(raw_response))
        self._validate_round(output, state)
        values = output.model_dump()
        issue_order = {
            issue["goal_id"]: index for index, issue in enumerate(state.get("issues", []))
        }
        values["candidates"].sort(key=lambda candidate: issue_order[candidate["goal_id"]])
        return {
            "feedback_strengths": values["strengths"],
            "revision_candidates": values["candidates"],
            "goal_feedback": values["goal_feedback"],
            "source_limitations": values["source_limitations"],
            "student_output": "Specific feedback and revision choices are available.",
        }

    def _final_values(self, raw_response: str, state: WritingAssistantState) -> dict[str, Any]:
        output = FinalSupportOutput.model_validate(parse_json_object(raw_response))
        self._validate_final(output, state)
        reflection = {
            "original_strengths": state.get("original_strengths", []),
            **output.model_dump(),
            "future_possibilities": state.get("future_areas", []),
        }
        return {
            "final_reflection": reflection,
            "student_output": reflection["conclusion"],
        }

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
                    "The previous Support response failed deterministic validation. Return only "
                    "a corrected complete JSON object with exactly the required fields. Preserve "
                    "the Coordinator handoff, exact references, selected-goal observations, and "
                    "source limitations. Keep valid content when possible and do not explain the "
                    f"correction. Validation error: {str(error)[:2000]}"
                ),
            },
        ]

    def run(self, state: WritingAssistantState) -> SupportResult:
        from time import perf_counter

        final_mode = state["review_mode"] == "final"
        messages = self._final_messages(state) if final_mode else self._round_messages(state)
        call_started = perf_counter()
        raw_response = self.client.chat_completion(messages, json_mode=True)
        initial_metadata = self._metadata()
        initial_metadata["latency_ms"] = max(0, round((perf_counter() - call_started) * 1000))
        raw_responses = [raw_response]
        model_calls = [initial_metadata]
        try:
            values = (
                self._final_values(raw_response, state)
                if final_mode
                else self._round_values(raw_response, state)
            )
        except (ResponseValidationError, ValidationError, ValueError) as exc:
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
                mode = "final reflection" if final_mode else "round feedback"
                raise ResponseValidationError(
                    f"The Support Agent could not produce valid {mode} after one correction."
                ) from repair_exc
        return SupportResult(
            values=values,
            raw_response=raw_response,
            messages=messages,
            raw_responses=raw_responses,
            model_calls=model_calls,
        )
