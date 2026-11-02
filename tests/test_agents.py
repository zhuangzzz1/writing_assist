import json

import pytest

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import ResponseValidationError
from langgraph_core.state import make_initial_state
from tests.helpers import FakeClient, coordinator_payload, support_payload


def test_coordinator_preserves_safety_flag_when_other_fields_are_malformed():
    raw = json.dumps(
        {
            "flag_teacher": True,
            "routing_decision": "not-valid",
            "teacher_flag_category": "concerning_content",
            "teacher_flag_reason": "The writer describes bullying.",
        }
    )
    coordinator = AssessmentCoordinator(FakeClient([raw]))
    result = coordinator.run(make_initial_state("A personal narrative.", "6th Grade"))

    assert result.values["routing_decision"] == "teacher_review"
    assert result.values["flag_teacher"] is True
    assert result.values["teacher_flag_reason"] == "The writer describes bullying."


def test_coordinator_malformed_output_falls_back_to_clarification():
    coordinator = AssessmentCoordinator(FakeClient(["not json"]))
    result = coordinator.run(make_initial_state("An outline.", "7th Grade"))

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["clarification_question"]
    assert result.values["flag_teacher"] is False


def test_coordinator_caps_extra_strengths_without_rejecting_assessment():
    raw = coordinator_payload(strengths=["one", "two", "three", "four"])
    coordinator = AssessmentCoordinator(FakeClient([raw]))

    result = coordinator.run(make_initial_state("A complete draft.", "6th Grade"))

    assert result.values["routing_decision"] == "support_agent"
    assert result.values["strengths"] == ["one", "two", "three"]


def test_support_returns_feedback_and_practice_together():
    state = make_initial_state("A complete draft.", "6th Grade")
    state.update(
        {
            "strengths": ["Clear main idea"],
            "issues": [],
            "skill_gaps": ["thesis"],
            "needs_feedback": True,
            "needs_practice": True,
            "coordinator_reasoning": "Support is appropriate.",
        }
    )
    support = InstructionalSupportAgent(FakeClient([support_payload()]))
    result = support.run(state)

    assert len(result.values["feedback_priorities"]) == 2
    assert len(result.values["practice_exercises"]) == 1
    assert "Targeted practice" in result.values["student_output"]


def test_support_rejects_missing_required_practice():
    state = make_initial_state("A complete draft.", "6th Grade")
    state.update({"skill_gaps": ["thesis"], "needs_practice": True})
    support = InstructionalSupportAgent(
        FakeClient([support_payload(include_practice=False)])
    )

    with pytest.raises(ResponseValidationError, match="practice"):
        support.run(state)


def test_support_does_not_return_practice_when_coordinator_disabled_it():
    state = make_initial_state("A complete draft.", "6th Grade")
    state.update({"skill_gaps": [], "needs_practice": False})
    support = InstructionalSupportAgent(FakeClient([support_payload()]))

    result = support.run(state)
    assert result.values["practice_exercises"] == []
