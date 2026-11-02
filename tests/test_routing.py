import pytest

from langgraph_core.routing import route_from_assessment


@pytest.mark.parametrize(
    "decision",
    ["ask_clarification", "support_agent", "teacher_review", "direct_response"],
)
def test_each_valid_route(decision):
    assert route_from_assessment({"routing_decision": decision}) == decision


@pytest.mark.parametrize("decision", ["ask_clarification", "support_agent", "direct_response"])
def test_teacher_flag_overrides_contradictory_route(decision):
    state = {"routing_decision": decision, "flag_teacher": True}
    assert route_from_assessment(state) == "teacher_review"


@pytest.mark.parametrize("state", [{}, {"routing_decision": None}, {"routing_decision": "bad"}])
def test_missing_or_malformed_route_uses_safe_fallback(state):
    assert route_from_assessment(state) == "ask_clarification"


def test_support_flags_do_not_affect_routing():
    state = {
        "routing_decision": "direct_response",
        "needs_feedback": True,
        "needs_practice": True,
    }
    assert route_from_assessment(state) == "direct_response"
