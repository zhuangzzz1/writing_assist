import os
import uuid

import streamlit as st

from agents.utils import (
    APIError,
    AuthError,
    DeepSeekClient,
    InputValidationError,
    RateLimitError,
    ResponseValidationError,
    WritingAssistantError,
)
from langgraph_core.graph import InvocationResult, WritingAssistantService
from langgraph_core.state import make_initial_state
from storage.interface import RunRecord
from ui.components import (
    FIXTURE_PATHS,
    load_fixture_into_session,
    render_student_result,
)
from ui.observability import render_observability


def _session_id() -> str:
    value = st.query_params.get("session_id")
    if isinstance(value, str):
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            pass
    value = uuid.uuid4().hex
    st.query_params["session_id"] = value
    return value


def _clear_active() -> None:
    st.session_state.current_invocation = None
    st.session_state.current_thread = None
    st.session_state.viewed_record = None


def _new_blank_analysis() -> None:
    _clear_active()
    st.session_state.writing_input = ""
    st.session_state.grade_level = "6th Grade"
    st.session_state.assignment_context_input = ""
    st.session_state.student_concerns_input = ""
    st.session_state.loaded_fixture = None


def _load_record(record: RunRecord) -> None:
    st.session_state.current_thread = record.thread_id
    if record.status == "awaiting_clarification":
        st.session_state.current_invocation = InvocationResult(
            thread_id=record.thread_id,
            state=record.state,
            pending_question=record.state.get(
                "clarification_question", "What kind of writing help do you need?"
            ),
        )
        st.session_state.viewed_record = None
    else:
        st.session_state.current_invocation = None
        st.session_state.viewed_record = record


def _show_error(error: Exception) -> None:
    if isinstance(error, RateLimitError):
        st.warning("The AI service is busy. Wait a moment and try again.")
    elif isinstance(error, AuthError):
        st.error("API authentication failed. Check the DeepSeek API key configuration.")
    elif isinstance(error, InputValidationError):
        st.warning(str(error))
    elif isinstance(error, ResponseValidationError):
        st.error(f"The AI returned an incomplete response: {error}")
        st.info("Try the analysis again. No writing feedback was generated.")
    elif isinstance(error, APIError):
        st.error(str(error))
        st.info("This may be temporary. Try again in a moment.")
    elif isinstance(error, WritingAssistantError):
        st.error(str(error))
    else:
        st.error("An unexpected error stopped the analysis.")
        if os.getenv("ENABLE_DEBUG_MODE", "false").lower() == "true":
            st.exception(error)


def _start_analysis(service: WritingAssistantService, session_id: str) -> None:
    try:
        initial_state = make_initial_state(
            writing=st.session_state.get("writing_input", ""),
            grade_level=st.session_state.get("grade_level", "6th Grade"),
            assignment_context=st.session_state.get("assignment_context_input", ""),
            student_concerns=st.session_state.get("student_concerns_input", ""),
            app_version=service.version,
            debug_enabled=st.session_state.get("capture_debug", False),
        )
        thread_id = uuid.uuid4().hex
        with st.spinner("Assessment Coordinator is analyzing the writing and selecting a route..."):
            invocation = service.start_run(session_id, thread_id, initial_state)
    except Exception as exc:
        _show_error(exc)
        return
    st.session_state.current_thread = thread_id
    st.session_state.current_invocation = invocation
    st.session_state.viewed_record = None
    st.session_state.clarification_answer = ""
    st.rerun()


def _resume_analysis(service: WritingAssistantService, session_id: str) -> None:
    thread_id = st.session_state.current_thread
    answer = st.session_state.get("clarification_answer", "")
    try:
        with st.spinner("Reassessing your answer and continuing the same graph..."):
            invocation = service.resume_run(session_id, thread_id, answer)
    except Exception as exc:
        _show_error(exc)
        return
    st.session_state.current_invocation = invocation
    st.rerun()


def _render_input(service: WritingAssistantService, session_id: str) -> None:
    st.subheader("Writing input")
    st.warning(
        "Do not submit writing containing real names, schools, or personal information. "
        "This is a demo system — your input is sent to an external AI service."
    )
    if st.session_state.get("loaded_fixture"):
        st.caption(f"Loaded synthetic fixture: {st.session_state.loaded_fixture}")
    with st.form("writing_analysis_form"):
        st.text_area(
            "Student writing",
            key="writing_input",
            height=300,
            placeholder="Paste a synthetic draft or outline here...",
        )
        st.text_input(
            "Assignment type or prompt (optional)",
            key="assignment_context_input",
            placeholder="For example: Persuasive Essay",
        )
        st.text_area(
            "Student concerns (optional)",
            key="student_concerns_input",
            height=90,
            placeholder="What would you like help with?",
        )
        submitted = st.form_submit_button(
            "Analyze Writing", key="analyze_writing", type="primary"
        )
    if submitted:
        _start_analysis(service, session_id)


def _render_clarification(service: WritingAssistantService, session_id: str) -> None:
    invocation = st.session_state.current_invocation
    st.subheader("One question before writing feedback")
    st.info(invocation.pending_question)
    st.caption(
        "Your answer resumes the same checkpoint. No feedback is generated while intent is unclear."
    )
    with st.form("clarification_form"):
        st.text_area(
            "Your answer",
            key="clarification_answer",
            height=110,
            placeholder="Tell us what kind of help you want...",
        )
        submitted = st.form_submit_button(
            "Answer and Resume", key="resume_clarification", type="primary"
        )
    st.button("Start a different analysis", key="different_analysis", on_click=_clear_active)
    if submitted:
        _resume_analysis(service, session_id)


def _render_main(service: WritingAssistantService, session_id: str) -> None:
    invocation = st.session_state.get("current_invocation")
    if invocation and invocation.pending:
        _render_clarification(service, session_id)
        return

    _render_input(service, session_id)
    viewed_record = st.session_state.get("viewed_record")
    if viewed_record and viewed_record.status == "failed":
        st.error(f"Saved run failed: {viewed_record.error or 'Unknown error'}")
        return

    state = invocation.state if invocation else viewed_record.state if viewed_record else None
    if state and not invocation_pending(invocation):
        st.divider()
        if viewed_record:
            st.caption(f"Viewing saved run {viewed_record.thread_id[:8]}")
        render_student_result(state)


def invocation_pending(invocation: InvocationResult | None) -> bool:
    return bool(invocation and invocation.pending)


def _render_sidebar(
    service: WritingAssistantService,
    client: DeepSeekClient,
    session_id: str,
) -> dict:
    st.sidebar.header("Controls")
    st.sidebar.markdown("**Agent-Based Application Version 1**")
    st.sidebar.caption(
        f"Model: {client.model} | Thinking: {'on' if client.thinking else 'off'}"
    )
    st.sidebar.selectbox(
        "Grade level",
        ["5th Grade", "6th Grade", "7th Grade"],
        index=1,
        key="grade_level",
    )

    st.sidebar.markdown("**Frozen synthetic test cases**")
    for name in FIXTURE_PATHS:
        st.sidebar.button(
            f"Load {name}",
            key=f"load_{name}",
            on_click=load_fixture_into_session,
            args=(name,),
            width="stretch",
        )

    st.sidebar.button(
        "New analysis (keep input)", key="new_analysis", on_click=_clear_active
    )
    st.sidebar.button(
        "New blank analysis", key="new_blank_analysis", on_click=_new_blank_analysis
    )

    st.sidebar.markdown("**Debug and observability**")
    options = {
        "show_state": st.sidebar.checkbox("Show final state", value=True, key="show_state"),
        "show_timing": st.sidebar.checkbox("Show timing", value=True, key="show_timing"),
        "show_logs": st.sidebar.checkbox("Show logs", value=False, key="show_logs"),
        "show_prompts": st.sidebar.checkbox(
            "Show captured prompts/responses", value=False, key="show_prompts"
        ),
    }
    st.sidebar.checkbox(
        "Capture prompts/responses on new runs", value=False, key="capture_debug"
    )

    st.sidebar.divider()
    st.sidebar.subheader("Run history")
    records = service.list_runs(session_id)
    if records:
        rows = [
            {
                "Run": record.thread_id[:8],
                "Status": record.status,
                "Route": record.routing_decision or "—",
                "Updated": record.updated_at[:19].replace("T", " "),
            }
            for record in records
        ]
        st.sidebar.dataframe(rows, hide_index=True, width="stretch")
        record_by_id = {record.thread_id: record for record in records}
        selected = st.sidebar.selectbox(
            "Saved run to load",
            options=[None, *record_by_id.keys()],
            format_func=lambda value: (
                "Select a run..."
                if value is None
                else f"{value[:8]} | {record_by_id[value].status}"
            ),
            key="history_selection",
        )
        st.sidebar.button(
            "Load saved run",
            key="load_saved_run",
            disabled=selected is None,
            on_click=_load_record,
            args=(record_by_id[selected],) if selected is not None else (),
        )
    else:
        st.sidebar.caption("No saved runs in this session.")

    st.sidebar.caption(
        "Bookmark the session URL to recover history and pending clarifications. "
        "Anyone with that URL may access the same view; use synthetic writing only."
    )
    st.sidebar.caption("Data is retained until manual deletion or cloud filesystem replacement.")
    confirm_delete = st.sidebar.checkbox(
        "I understand deletion is permanent", key="confirm_delete"
    )
    if st.sidebar.button(
        "Delete my data",
        key="delete_my_data",
        disabled=not confirm_delete,
        type="secondary",
    ):
        service.delete_session(session_id)
        st.query_params.clear()
        st.session_state.clear()
        st.rerun()
    return options


def _display_state():
    invocation = st.session_state.get("current_invocation")
    if invocation:
        return invocation.state
    record = st.session_state.get("viewed_record")
    return record.state if record else None


def render_dashboard(service: WritingAssistantService, client: DeepSeekClient) -> None:
    session_id = _session_id()
    if "restore_initialized" not in st.session_state:
        st.session_state.restore_initialized = True
        records = service.list_runs(session_id)
        if records:
            _load_record(records[0])
    st.title("Writing Assistant")
    st.caption("Two-agent formative writing support for grades 5–7")
    options = _render_sidebar(service, client, session_id)
    main_column, observability_column = st.columns([1.65, 1], gap="large")
    with main_column:
        _render_main(service, session_id)
    with observability_column:
        render_observability(_display_state(), options)
