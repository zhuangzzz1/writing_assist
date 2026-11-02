import json


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat_completion(self, messages, **kwargs):
        self.calls.append((messages, kwargs))
        if not self.responses:
            raise AssertionError("Unexpected model call")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def coordinator_payload(route="support_agent", **overrides):
    payload = {
        "writing_complete": route != "ask_clarification",
        "missing_context": route == "ask_clarification",
        "unclear_intent": route == "ask_clarification",
        "no_issues_found": route == "direct_response",
        "strengths": ["Clear main idea"],
        "issues": [],
        "skill_gaps": [],
        "routing_decision": route,
        "flag_teacher": route == "teacher_review",
        "teacher_flag_reason": "",
        "teacher_flag_category": "none",
        "teacher_evidence": [],
        "needs_feedback": route == "support_agent",
        "needs_practice": False,
        "coordinator_reasoning": "The submission needs the selected support.",
        "clarification_question": "",
    }
    if route == "support_agent":
        payload["issues"] = [
            {"type": "thesis", "severity": "high", "description": "The thesis is broad."}
        ]
        payload["skill_gaps"] = ["thesis"]
        payload["needs_practice"] = True
    elif route == "ask_clarification":
        payload["clarification_question"] = "Do you want outline help or draft feedback?"
    elif route == "teacher_review":
        payload["teacher_flag_reason"] = "The writer describes repeated bullying."
        payload["teacher_flag_category"] = "concerning_content"
        payload["teacher_evidence"] = ["They called me names"]
    payload.update(overrides)
    return json.dumps(payload)


def support_payload(include_practice=True):
    practice = None
    if include_practice:
        practice = {
            "skill": "thesis",
            "instructions": "Practice making a specific claim.",
            "steps": ["Name your topic.", "Add your position and reason."],
            "worked_example": "Our school should add a second recess because it improves focus.",
            "success_check": "Does your sentence state a claim and a reason?",
        }
    return json.dumps(
        {
            "strengths": ["You include relevant examples."],
            "priorities": [
                {
                    "title": "Make your thesis more specific",
                    "why_it_matters": "Readers need to know your exact claim.",
                    "example_from_writing": "Uniforms are good because they help students.",
                    "next_step": "Name two specific ways uniforms help.",
                },
                {
                    "title": "Connect your evidence",
                    "why_it_matters": "Explanation shows how evidence supports your claim.",
                    "example_from_writing": "The class vote is introduced in paragraph two.",
                    "next_step": "Explain what the vote shows and what it cannot show.",
                },
            ],
            "practice": practice,
        }
    )


def coordinator_payload_v2(route="support_agent", revision_need=None, **overrides):
    if revision_need is None:
        revision_need = "standard" if route == "support_agent" else "not_applicable"
    payload = json.loads(coordinator_payload(route))
    payload["revision_need"] = revision_need
    if route == "support_agent":
        payload["issues"].append(
            {
                "type": "evidence",
                "severity": "medium",
                "description": "The class vote needs explanation and limitations.",
            }
        )
        payload["skill_gaps"].append("evidence")
    if revision_need == "light_touch":
        payload["issues"] = [
            {
                "type": "word choice",
                "severity": "low",
                "description": "One generic phrase could be more vivid.",
            }
        ]
        payload["skill_gaps"] = ["word choice"]
        payload["needs_practice"] = False
    payload.update(overrides)
    return json.dumps(payload)


def support_payload_v2(include_practice=True, revision_need="standard"):
    base = json.loads(support_payload(include_practice=False))
    priorities = []
    for index, priority in enumerate(base["priorities"]):
        skill = "thesis" if index == 0 else "evidence"
        practice = None
        if include_practice and revision_need == "standard":
            practice = {
                "skill": skill,
                "instructions": f"Practice {skill} with a new idea.",
                "steps": ["Read the example.", "Write your own attempt.", "Use the self-check."],
                "worked_example": (
                    "Our library should open earlier because students need a quiet place to read."
                    if index == 0
                    else "A class survey about recess can show opinions in one class, not every school."
                ),
                "success_check": "Did you make your own attempt and explain your thinking?",
            }
        priorities.append({**priority, "skill": skill, "practice": practice})
    if revision_need == "light_touch":
        priorities = [
            {
                "title": "Make one phrase more vivid",
                "why_it_matters": "A precise detail can help readers picture the moment.",
                "example_from_writing": "The garden was nice.",
                "next_step": "Replace one general word with a detail you noticed.",
                "skill": "word choice",
                "practice": None,
            }
        ]
    return json.dumps(
        {
            "affect_acknowledgment": (
                "It makes sense to feel unsure; one small revision choice is enough for now."
            ),
            "strengths": base["strengths"],
            "priorities": priorities,
        }
    )
