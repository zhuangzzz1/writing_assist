from langgraph_core.state import RoutingDecision, WritingAssistantState


VALID_ROUTES = {
    "ask_clarification",
    "support_agent",
    "teacher_review",
    "direct_response",
}


def route_from_assessment(state: WritingAssistantState) -> RoutingDecision:
    if state.get("flag_teacher"):
        return "teacher_review"
    decision = state.get("routing_decision")
    if decision in VALID_ROUTES:
        return decision
    return "ask_clarification"
