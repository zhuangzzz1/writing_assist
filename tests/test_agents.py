import json

import pytest

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import ResponseValidationError
from langgraph_core.state import make_initial_state
from tests.helpers import (
    FakeClient,
    coordinator_payload,
    coordinator_payload_v2,
    support_payload,
    support_payload_v2,
)


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
    assert "**Brief example:**" in result.values["student_output"]
    assert "**Check your attempt:**" in result.values["student_output"]


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


def v2_support_state(revision_need="standard", affect="unsure"):
    state = make_initial_state(
        "A complete synthetic draft.",
        "6th Grade",
        app_version="v2",
        affect_check_in=affect,
    )
    state.update(
        {
            "revision_need": revision_need,
            "strengths": ["Clear main idea"],
            "issues": [],
            "skill_gaps": ["thesis", "evidence"],
            "needs_feedback": True,
            "needs_practice": revision_need == "standard",
            "coordinator_reasoning": "The selected level of support is appropriate.",
        }
    )
    return state


def test_v2_coordinator_repairs_invalid_output_once():
    client = FakeClient(["not json", coordinator_payload_v2()])
    state = make_initial_state("A complete draft.", "6th Grade", app_version="v2")
    coordinator = AssessmentCoordinator(client, "v2")

    result = coordinator.run(state)

    assert result.values["routing_decision"] == "support_agent"
    assert result.values["coordinator_repair_count"] == 1
    assert len(result.raw_responses) == 2
    assert len(client.calls) == 2
    assert "Validation error" in client.calls[1][0][-1]["content"]


def test_v2_coordinator_failed_repair_uses_clarification_history():
    client = FakeClient(["not json", "still not json"])
    state = make_initial_state("An outline.", "7th Grade", app_version="v2")
    state["clarification_history"] = [
        {"question": "What help do you want?", "answer": "I want thesis help."}
    ]
    coordinator = AssessmentCoordinator(client, "v2")

    result = coordinator.run(state)

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["coordinator_repair_count"] == 1
    assert "I want thesis help." in result.values["clarification_question"]
    assert "ideas" in result.values["clarification_question"]


def test_v2_safety_fallback_does_not_spend_repair_call():
    raw = json.dumps(
        {
            "flag_teacher": True,
            "routing_decision": "invalid",
            "teacher_flag_category": "concerning_content",
            "teacher_flag_reason": "The writer describes bullying.",
        }
    )
    client = FakeClient([raw])
    state = make_initial_state("A personal narrative.", "6th Grade", app_version="v2")

    result = AssessmentCoordinator(client, "v2").run(state)

    assert result.values["routing_decision"] == "teacher_review"
    assert result.values["flag_teacher"] is True
    assert result.values["revision_need"] == "not_applicable"
    assert result.values["coordinator_repair_count"] == 0
    assert client.responses == []


def test_v2_light_touch_disables_practice():
    raw = coordinator_payload_v2(revision_need="light_touch", needs_practice=True)
    state = make_initial_state("A strong draft.", "6th Grade", app_version="v2")

    result = AssessmentCoordinator(FakeClient([raw]), "v2").run(state)

    assert result.values["revision_need"] == "light_touch"
    assert result.values["needs_practice"] is False


def test_v2_support_returns_focus_specific_practice_and_affect_acknowledgment():
    support = InstructionalSupportAgent(FakeClient([support_payload_v2()]), "v2")

    result = support.run(v2_support_state())

    assert len(result.values["feedback_priorities"]) == 2
    assert len(result.values["practice_exercises"]) == 2
    assert {
        exercise["priority_index"] for exercise in result.values["practice_exercises"]
    } == {0, 1}
    assert all(
        "worked_example" not in exercise
        for exercise in result.values["practice_exercises"]
    )
    assert "practice" not in result.values["feedback_priorities"][0]
    assert "feel unsure" in result.values["feedback_content"]


def test_v2_support_discards_model_supplied_complete_worked_examples():
    output = json.loads(support_payload_v2())
    for priority in output["priorities"]:
        priority["practice"]["worked_example"] = "A complete response to copy."
    support = InstructionalSupportAgent(FakeClient([json.dumps(output)]), "v2")

    result = support.run(v2_support_state())

    assert all(
        "worked_example" not in exercise
        for exercise in result.values["practice_exercises"]
    )


def test_v2_light_touch_returns_one_optional_priority_without_practice():
    support = InstructionalSupportAgent(
        FakeClient([support_payload_v2(revision_need="light_touch")]), "v2"
    )

    result = support.run(v2_support_state("light_touch", affect="ready"))

    assert len(result.values["feedback_priorities"]) == 1
    assert result.values["practice_exercises"] == []
    assert "feel unsure" not in result.values["feedback_content"]


def test_v2_standard_support_rejects_single_light_touch_priority_after_one_repair():
    invalid = support_payload_v2(revision_need="light_touch")
    support = InstructionalSupportAgent(FakeClient([invalid, invalid]), "v2")

    with pytest.raises(ResponseValidationError, match="two or three"):
        support.run(v2_support_state())


def test_v2_support_repairs_missing_choice_practice_once():
    invalid_output = json.loads(support_payload_v2())
    invalid_output["priorities"][1]["practice"] = None
    client = FakeClient([json.dumps(invalid_output), support_payload_v2()])
    support = InstructionalSupportAgent(client, "v2")

    result = support.run(v2_support_state())

    assert len(result.values["practice_exercises"]) == 2
    assert len(result.raw_responses) == 2
    assert len(client.calls) == 2
    assert "Validation error" in client.calls[1][0][-1]["content"]


def test_v2_support_rejects_practice_missing_after_one_repair():
    output = json.loads(support_payload_v2())
    output["priorities"][1]["practice"] = None
    invalid = json.dumps(output)
    support = InstructionalSupportAgent(FakeClient([invalid, invalid]), "v2")

    with pytest.raises(ResponseValidationError, match="Each V2 revision choice"):
        support.run(v2_support_state())


def test_v2_support_requires_acknowledgment_after_one_repair():
    output = json.loads(support_payload_v2())
    output["affect_acknowledgment"] = ""
    invalid = json.dumps(output)
    support = InstructionalSupportAgent(FakeClient([invalid, invalid]), "v2")

    with pytest.raises(ResponseValidationError, match="acknowledge"):
        support.run(v2_support_state())


def test_v2_support_receives_clarified_goal_and_main_point():
    state = v2_support_state()
    state["clarification_history"] = [
        {
            "question": "What is your main point?",
            "answer": "Communities should reduce carbon emissions.",
        }
    ]
    client = FakeClient([support_payload_v2()])

    InstructionalSupportAgent(client, "v2").run(state)

    prompt = client.calls[0][0][1]["content"]
    assert "Communities should reduce carbon emissions." in prompt
    assert "clarification_history" in prompt


def test_v2_standard_support_allows_choices_without_practice():
    state = v2_support_state()
    state["needs_practice"] = False
    support = InstructionalSupportAgent(
        FakeClient([support_payload_v2(include_practice=False)]), "v2"
    )

    result = support.run(state)

    assert len(result.values["feedback_priorities"]) == 2
    assert result.values["practice_exercises"] == []


@pytest.mark.parametrize("reason", [None, " ", 42])
def test_safety_fallback_replaces_missing_or_invalid_teacher_reason(reason):
    raw = json.dumps({"flag_teacher": True, "teacher_flag_reason": reason})
    coordinator = AssessmentCoordinator(FakeClient([raw]))

    result = coordinator.run(make_initial_state("A personal narrative.", "6th Grade"))

    assert result.values["routing_decision"] == "teacher_review"
    assert result.values["flag_teacher"] is True
    assert "could not be validated" in result.values["teacher_flag_reason"]
