from dataclasses import dataclass
from pathlib import Path
from typing import cast

import streamlit as st

from langgraph_core.state import GradeLevel


FIXTURE_PATHS = {
    "Normal case": "normal_case.txt",
    "Incomplete case": "incomplete_case.txt",
    "Boundary A: concerning content": "boundary_case_a.txt",
    "Boundary B: revision frustration": "boundary_case_b.txt",
}


@dataclass(frozen=True)
class WritingFixture:
    name: str
    writing: str
    grade_level: GradeLevel
    assignment_context: str
    student_concerns: str


def load_fixture(name: str) -> WritingFixture:
    path = Path(__file__).resolve().parents[1] / "test_cases" / FIXTURE_PATHS[name]
    text = path.read_text(encoding="utf-8")
    header, separator, writing = text.partition("Writing:\n")
    if not separator:
        raise ValueError(f"Fixture {name} has no Writing section.")
    metadata: dict[str, str] = {}
    for line in header.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    grade_level = metadata.get("Grade Level", "")
    if grade_level not in ("5th Grade", "6th Grade", "7th Grade"):
        raise ValueError(f"Fixture {name} has an invalid grade level.")
    assignment_context = metadata.get("Assignment Type", "")
    if assignment_context == "Not provided":
        assignment_context = ""
    return WritingFixture(
        name=name,
        writing=writing,
        grade_level=cast(GradeLevel, grade_level),
        assignment_context=assignment_context,
        student_concerns=metadata.get("Student Concern", ""),
    )


def load_fixture_into_session(name: str) -> None:
    fixture = load_fixture(name)
    st.session_state.writing_input = fixture.writing
    st.session_state.grade_level = fixture.grade_level
    st.session_state.assignment_context_input = fixture.assignment_context
    st.session_state.student_concerns_input = fixture.student_concerns
    st.session_state.affect_check_in = ""
    st.session_state.loaded_fixture = name
    st.session_state.current_invocation = None
    st.session_state.current_thread = None
    st.session_state.viewed_record = None


def format_practice(practice: dict) -> str:
    lines = [practice["instructions"]]
    lines.extend(f"{index}. {step}" for index, step in enumerate(practice["steps"], 1))
    if practice.get("worked_example"):
        lines.append(f"**Brief example:** {practice['worked_example']}")
    lines.append(f"**Check your attempt:** {practice['success_check']}")
    return "\n\n".join(lines)


def _render_v2_support(state: dict, result_id: str) -> None:
    st.success("Feedback and your revision choice")
    st.markdown(state.get("feedback_content", ""))
    priorities = state.get("feedback_priorities", [])
    if not priorities:
        st.info("No revision choices were returned.")
        return

    selected = st.radio(
        "Which focus would be most useful to you?",
        options=list(range(len(priorities))),
        format_func=lambda index: priorities[index]["title"],
        index=None,
        key=f"revision_focus_{result_id}",
    )
    if selected is None:
        st.caption("Select one focus to see its scaffold. This does not start another AI call.")
        return

    priority = priorities[selected]
    st.markdown(f"### Your choice: {priority['title']}")
    st.markdown(priority["why_it_matters"])
    st.markdown(f"**Example from your writing:** {priority['example_from_writing']}")
    st.markdown(f"**Try this:** {priority['next_step']}")

    practice = next(
        (
            item
            for item in state.get("practice_exercises", [])
            if item.get("priority_index") == selected
        ),
        None,
    )
    if practice is None:
        if state.get("revision_need") == "light_touch":
            message = (
                "You can revise on your own with this one suggestion. No practice exercise "
                "is needed for this light-touch response."
            )
        else:
            message = (
                "You can revise on your own using this suggestion. "
                "No practice exercise is included for this focus."
            )
        st.info(message)
        return
    continuation = st.radio(
        "How would you like to continue?",
        options=["revise", "practice"],
        format_func={"revise": "Revise on my own", "practice": "Try a short practice"}.get,
        index=0,
        horizontal=True,
        key=f"practice_choice_{result_id}",
    )
    if continuation == "practice":
        st.markdown(f"#### Optional practice: {practice['skill']}")
        st.markdown(format_practice(practice))
        st.caption("This is for your own practice. It is not submitted or graded.")


def render_student_result(state: dict, result_id: str = "current") -> None:
    if state.get("teacher_message"):
        st.warning("Simulated teacher review: no teacher has been notified.")
        st.markdown(state.get("student_output", ""))
        return
    route = state.get("routing_decision")
    if route == "support_agent" and state.get("app_version") == "v2":
        _render_v2_support(state, result_id)
    elif route == "support_agent":
        st.success("Feedback and next steps")
        st.markdown(state.get("feedback_content", ""))
        for practice in state.get("practice_exercises", []):
            with st.expander(f"Targeted practice: {practice['skill']}", expanded=True):
                st.markdown(format_practice(practice))
    elif route == "direct_response":
        st.success("Your draft is ready")
        st.markdown(state.get("student_output", ""))
    elif state.get("student_output"):
        st.markdown(state["student_output"])
