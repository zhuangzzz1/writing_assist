import json
from typing import Any


INITIAL_DRAFT = "Our school should start a garden.\n\nIt would teach responsibility."
DEFAULT_REFERENCE = "It would teach responsibility."


class FakeClient:
    thinking = True
    model = "deepseek-flash"
    reasoning_effort = "high"

    def __init__(self, responses, thinking=True):
        self.responses = list(responses)
        self.calls = []
        self.thinking = thinking
        self.last_response_metadata = {}

    def model_config(self):
        return {
            "model_name": self.model,
            "thinking_enabled": self.thinking,
            "reasoning_effort": self.reasoning_effort if self.thinking else "",
            "prompt_version": "v3.8.3",
            "schema_version": "v3.8.0",
        }

    def chat_completion(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        if not self.responses:
            raise AssertionError("Unexpected model call")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        self.last_response_metadata = {
            "provider_request_id": "fake-request",
            "model_name": self.model,
            "thinking_enabled": self.thinking,
            "reasoning_effort": self.reasoning_effort if self.thinking else "",
            "token_usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }
        return response


def _paragraph_for(text: str, reference: str) -> int:
    for number, paragraph in enumerate(text.split("\n\n"), start=1):
        if reference in paragraph:
            return number
    raise ValueError(f"Reference not found: {reference}")


def issue_for(
    writing: str,
    reference: str = DEFAULT_REFERENCE,
    goal_id: str = "goal_1",
    **overrides,
):
    issue = {
        "goal_id": goal_id,
        "category": "evidence_elaboration",
        "finding_severity": "reasoning",
        "description": "The connection needs more explanation.",
        "draft_reference": reference,
        "paragraph_number": _paragraph_for(writing, reference),
        "occurrence": 1,
        "source_dependent": False,
        "source_location": "",
        "regression": False,
    }
    issue.update(overrides)
    return issue


def observation_for(goal_id="goal_1", status="specific_improvement", **overrides):
    observation = {
        "goal_id": goal_id,
        "status": status,
        "observation": "The revised explanation makes the connection clearer.",
        "evidence_reference": "",
        "carry_forward": False,
    }
    observation.update(overrides)
    return observation


def coordinator_payload(
    state,
    route="support_agent",
    issues=None,
    observations=None,
    legacy=False,
    **overrides,
):
    if issues is None:
        issues = [issue_for(state["writing"])] if route == "support_agent" else []
    payload = {
        "working_genre": (
            state["genre_selection"] if state["genre_selection"] != "auto" else "argument"
        ),
        "genre_confidence": "high",
        "genre_basis": "The draft states a position and gives a reason.",
        "strengths": ["The draft has a clear position."],
        "issues": issues,
        "source_limitations": [],
        "selected_goal_observations": observations or [],
        "routing_decision": route,
        "flag_teacher": route == "teacher_review",
        "teacher_flag_reason": "Human review is needed." if route == "teacher_review" else "",
        "teacher_flag_category": (
            "concerning_content" if route == "teacher_review" else "none"
        ),
        "teacher_evidence": [],
        "coordinator_reasoning": "The route follows the available writing evidence.",
        "clarification_question": (
            "What would you like help with?" if route == "ask_clarification" else ""
        ),
        "clarification_choices": [],
    }
    if route in ("ask_clarification", "teacher_review"):
        payload.update(
            {
                "strengths": [],
                "issues": [],
                "framework_coverage": [],
                "source_limitations": [],
                "selected_goal_observations": [],
            }
        )
    if route == "teacher_review":
        payload.update(
            {"working_genre": "", "genre_confidence": "", "genre_basis": ""}
        )
    if legacy:
        for issue in payload["issues"]:
            issue.setdefault("reasoning_operation", "none")
    payload.update(overrides)
    return json.dumps(payload)


def candidate_for(issue, **overrides):
    candidate = {
        "goal_id": issue["goal_id"],
        "title": "Explain the connection",
        "why_it_matters": "Readers need to understand how your ideas connect.",
        "draft_reference": issue["draft_reference"],
        "paragraph_number": issue["paragraph_number"],
        "occurrence": issue["occurrence"],
        "revision_action": "Explain the connection in your own words.",
        "hint": {
            "passage_reference": issue["draft_reference"],
            "steps": [
                "In an argument, stating evidence isn't enough — you need to explain why it matters.",
                "Look at the action and the effect in this passage.",
                "Explain one missing link using your own idea.",
            ],
            "self_check": "Does your revision explain how one idea leads to the other?",
        },
        "stuck_step": "Write one question about the missing connection, then answer it in your own words.",
    }
    candidate.update(overrides)
    return candidate


def support_payload(state, candidates=None, legacy=False, **overrides):
    if candidates is None:
        candidates = [candidate_for(issue) for issue in state.get("issues", [])]
    if legacy:
        for candidate in candidates:
            candidate["hint"].setdefault("vocabulary_options", [])
            candidate["hint"].setdefault("sentence_starter", "")
    payload = {
        "strengths": ["You state your position clearly."],
        "candidates": candidates,
        "goal_feedback": [
            {
                "goal_id": item["goal_id"],
                "status": item["status"],
                "observation": item["observation"],
                "carry_forward": item["carry_forward"],
            }
            for item in state.get("selected_goal_observations", [])
        ],
        "source_limitations": state.get("source_limitations", []),
    }
    payload.update(overrides)
    return json.dumps(payload)


def final_coordinator_payload(state, changed=True, **overrides):
    final_reference = state["writing"].split("\n\n")[-1].strip()
    improvements = []
    if changed:
        improvements = [
            {
                "finding_id": "improvement_1",
                "summary": "The final draft adds a clearer connection.",
                "original_reference": "",
                "final_reference": final_reference,
                "goal_id": "goal_1",
            }
        ]
    payload = {
        "original_strengths": ["The original states a clear position."],
        "improvements": improvements,
        "regressions": [],
        "future_areas": ["Consider how each explanation helps its reader."],
        "coordinator_reasoning": "Findings are tied to the deterministic diff.",
    }
    payload.update(overrides)
    return json.dumps(payload)


def final_support_payload(state, **overrides):
    payload = {
        "improvements": [
            {
                "finding_id": item["finding_id"],
                "observation": item["summary"],
                "final_reference": item["final_reference"],
            }
            for item in state.get("comparison_improvements", [])
        ],
        "regressions": [
            {
                "finding_id": item["finding_id"],
                "observation": item["summary"],
                "final_reference": item["final_reference"],
            }
            for item in state.get("comparison_regressions", [])
        ],
        "conclusion": "You made your own revision choices and gave your ideas more attention.",
    }
    payload.update(overrides)
    return json.dumps(payload)
