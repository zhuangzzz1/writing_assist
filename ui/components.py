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


def format_hint(hint: dict) -> str:
    lines = [f"**Look at:** \"{hint['passage_reference']}\""]
    lines.extend(f"{index}. {step}" for index, step in enumerate(hint["steps"], 1))
    lines.append(f"**Check your revision:** {hint['self_check']}")
    # if hint.get("vocabulary_options"):
    #     lines.append(
    #         "**Vocabulary to evaluate:** "
    #         + ", ".join(hint["vocabulary_options"])
    #         + ". Choose only what matches your meaning."
    #     )
    # if hint.get("sentence_starter"):
    #     lines.append(
    #         f"**Optional structural starter:** `{hint['sentence_starter']}` "
    #         "Supply your own idea for every blank."
    #     )
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
