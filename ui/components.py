import streamlit as st

from langgraph_core.state import ObservationStatus


GENRE_LABELS = {
    "auto": "Auto-detect",
    "argument": "Argument",
    "informational": "Informational",
    "narrative": "Narrative",
}
OBSERVATION_LABELS = {
    "specific_improvement": "Specific improvement",
    "improvement_not_yet_evident": "Improvement not yet evident in this revision",
    "uncertain": "Uncertain from the available text",
}
GOAL_OUTCOME_LABELS = {
    "fully_addressed": "Fully addressed for this selected goal in this draft",
    "partially_addressed": "Partially addressed; some of this selected goal remains",
    "not_addressed": "Not addressed for this selected goal in this draft",
    "uncertain": "Uncertain for this selected goal from the available text",
}
NARROWING_LABELS = {
    "none": "No scope narrowing identified",
    "discretionary": "Discretionary narrowing: material not required by the task was removed",
    "required": "Required narrowing: material needed for the task was removed",
}
REQUIREMENT_SOURCE_LABELS = {
    "assignment_prompt": "Assignment",
    "teacher_directions": "Teacher directions",
    "framework": "Requested writing structure",
}


def format_hint(hint: dict) -> str:
    lines = [f"**Look at:** \"{hint['passage_reference']}\""]
    lines.extend(f"{index}. {step}" for index, step in enumerate(hint["steps"], 1))
    lines.append(f"**Check your revision:** {hint['self_check']}")
    return "\n\n".join(lines)


def render_goal_feedback(
    goal_feedback: list[dict], selected_goals: list[dict] | None = None
) -> None:
    titles = {
        goal["goal_id"]: goal.get("title", goal["goal_id"])
        for goal in selected_goals or []
    }
    for item in goal_feedback:
        status: ObservationStatus = item["status"]
        if item["goal_id"] in titles:
            st.markdown(f"**Goal: {titles[item['goal_id']]}**")
        st.markdown(f"**{OBSERVATION_LABELS[status]}**")
        st.markdown(item["observation"])
        outcome = item.get("goal_outcome", "")
        narrowing = item.get("narrowing", "")
        if outcome:
            st.markdown(f"**Selected-goal outcome:** {GOAL_OUTCOME_LABELS[outcome]}")
        if outcome == "fully_addressed":
            st.caption(
                "This describes only this selected goal in this draft. "
                "It is not a claim of overall mastery."
            )
        if narrowing:
            st.markdown(f"**Scope change:** {NARROWING_LABELS[narrowing]}")
        if narrowing == "discretionary":
            st.caption(
                "Removing this material is not the same as solving the original goal. "
                + (
                    "The original target no longer applies, but any separate remaining work "
                    "stays listed."
                    if not item.get("carry_forward")
                    else "The remaining part of the goal stays available below."
                )
            )
        elif narrowing == "required":
            st.caption(
                "The deleted requirement still needs attention. Its live revision choice "
                "remains listed; another improvement does not erase it."
            )
        if item.get("narrowing_evidence_reference"):
            st.caption(
                f"Deleted from the previous draft: \"{item['narrowing_evidence_reference']}\""
            )
        requirement_source = item.get("requirement_source", "")
        if requirement_source:
            st.caption(
                f"{REQUIREMENT_SOURCE_LABELS[requirement_source]} requirement: "
                f"\"{item['requirement_reference']}\""
            )
        if item.get("carry_forward"):
            st.caption("You may carry this goal forward. That is a choice, not a failure.")


def render_final_reflection(reflection: dict) -> None:
    if reflection.get("original_strengths"):
        st.subheader("Strengths in your original draft")
        for strength in reflection["original_strengths"]:
            st.markdown(f"- {strength}")
    st.subheader("What changed")
    if reflection.get("improvements"):
        for item in reflection["improvements"]:
            st.markdown(f"**Specific improvement:** {item['observation']}")
            if item.get("final_reference"):
                st.caption(f"Final draft: \"{item['final_reference']}\"")
    else:
        st.info("No specific improvement is claimed from the submitted text changes.")
    for item in reflection.get("regressions", []):
        st.warning(f"**A change to review:** {item['observation']}")
        if item.get("final_reference"):
            st.caption(f"Final draft: \"{item['final_reference']}\"")
    if reflection.get("future_possibilities"):
        st.subheader("Optional future possibilities")
        st.caption("These are choices for another day, not new required tasks.")
        for possibility in reflection["future_possibilities"]:
            st.markdown(f"- {possibility}")
    st.success(reflection["conclusion"])
