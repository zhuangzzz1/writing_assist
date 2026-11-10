import os
import sqlite3
import uuid
from typing import Any, Callable

import streamlit as st

from agents.utils import (
    MAX_DRAFT_CHARS,
    MAX_SOURCE_CHARS,
    APIError,
    AuthError,
    DeepSeekClient,
    InputValidationError,
    RateLimitError,
    ResponseValidationError,
    StorageError,
    WritingAssistantError,
)
from langgraph_core.graph import InvocationResult, WritingAssistantService
from langgraph_core.revision import build_text_diff, change_notification, locate_reference
from langgraph_core.state import GRADE_LEVELS, Genre, make_review_state
from storage.interface import CompositionRecord, RoundRecord
from ui.components import (
    GENRE_LABELS,
    format_hint,
    render_final_reflection,
    render_goal_feedback,
)
from ui.editor import goal_highlight_editor
from ui.observability import render_observability
from ui.scenarios import PracticeScenario, get_scenario, load_scenarios


STEPS = ("Draft", "Choose", "Revise", "Reflect")
STAGE_CSS = """
<style>
.block-container { max-width: 1500px; padding-top: 1.4rem; }
[data-testid="stSidebarHeader"] { display: none; }
.v3-step-status { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }
.v3-goal-strip { padding: 10px 14px; background: #f8faff; border-left: 4px solid #3157c8; color: #27364c; }
.v3-source-note { padding: 10px 14px; background: #fff7df; border-left: 4px solid #805600; }
.v3-workspace-footer { position: sticky; bottom: 0; background: white; padding: 8px 0; z-index: 5; }
@media (min-width: 1000px) {
  [data-testid="stHorizontalBlock"]:has(.draft-layout-marker) {
    display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 780px) minmax(0, 1fr);
    align-items: start;
  }
  [data-testid="stHorizontalBlock"]:has(.draft-layout-marker) > [data-testid="stColumn"],
  [data-testid="stHorizontalBlock"]:has(.workspace-marker) > [data-testid="stColumn"] {
    width: 100% !important; min-width: 0; justify-self: stretch;
  }
  [data-testid="stHorizontalBlock"]:has(.workspace-marker) {
    display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 1rem;
    align-items: start;
  }
}
@media (min-width: 1280px) {
  [data-testid="stHorizontalBlock"]:has(.draft-layout-marker) { max-width: 1400px; margin: auto; }
}
</style>
"""


def _debug_enabled() -> bool:
    return os.getenv("ENABLE_DEBUG_MODE", "false").strip().lower() == "true"


def _small_change_threshold() -> int:
    try:
        return max(0, int(os.getenv("SMALL_CHANGE_TOKEN_THRESHOLD", "8")))
    except ValueError:
        return 8


def _session_id() -> str:
    value = st.query_params.get("session_id")
    if isinstance(value, str):
        try:
            uuid.UUID(value)
            return value
        except ValueError:
            st.warning(
                "The session ID in the URL was not recognized. A new session has "
                "started and prior history is not visible."
            )
    value = uuid.uuid4().hex
    st.query_params["session_id"] = value
    return value


def _initialize_state() -> None:
    defaults = {
        "active_composition_id": None,
        "current_invocation": None,
        "current_step": "Draft",
        "show_history": False,
        "editor_text": "",
        "writing_input": "",
        "grade_level": "6th Grade",
        "genre_input": "auto",
        "assignment_prompt_input": "",
        "teacher_directions_input": "",
        "source_material_input": "",
        "student_concerns_input": "",
        "loaded_scenario_id": "",
        "loaded_fixture_version": "",
        "selected_goal_ids": [],
        "round_review_active": False,
        "less_feedback": False,
        "stuck_requested": False,
        "pending_scenario_id": None,
        "pending_revision_notice": None,
        "finish_dialog_open": False,
        "selection_warning": "",
        "developer_controls_visible": False,
        "agent_observability_visible": False,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _editor_key(composition_id: str) -> str:
    return f"essay_editor_{composition_id}"


def _set_editor(text: str, composition_id: str) -> None:
    st.session_state.editor_text = text
    st.session_state[_editor_key(composition_id)] = {"value": text}


def _clear_active() -> None:
    st.session_state.active_composition_id = None
    st.session_state.current_invocation = None
    st.session_state.current_step = "Draft"
    st.session_state.selected_goal_ids = []
    st.session_state.round_review_active = False
    st.session_state.less_feedback = False
    st.session_state.stuck_requested = False
    st.session_state.pending_revision_notice = None
    st.session_state.finish_dialog_open = False
    st.session_state.show_history = False


def _new_blank_composition() -> None:
    _clear_active()
    for key in (
        "writing_input",
        "assignment_prompt_input",
        "teacher_directions_input",
        "source_material_input",
        "student_concerns_input",
    ):
        st.session_state[key] = ""
    st.session_state.grade_level = "6th Grade"
    st.session_state.genre_input = "auto"
    st.session_state.loaded_scenario_id = ""
    st.session_state.loaded_fixture_version = ""


def _invocation_from_round(record: RoundRecord) -> InvocationResult | None:
    if record.status == "failed":
        return None
    pending = record.status == "awaiting_clarification"
    return InvocationResult(
        thread_id=record.thread_id,
        state=record.state,
        pending_question=record.state.get("clarification_question") if pending else None,
        pending_choices=record.state.get("clarification_choices", []) if pending else [],
    )


def _load_composition(service: WritingAssistantService, composition_id: str) -> None:
    composition = service.storage.get_composition(composition_id)
    if composition is None:
        raise StorageError("Saved history is unavailable.")
    snapshots = service.storage.list_snapshots(composition_id)
    if not snapshots:
        raise StorageError("Submitted draft history is unavailable.")
    latest_snapshot = snapshots[-1]
    latest_round = service.storage.get_latest_round(composition_id)
    reflection = service.storage.get_reflection(composition_id)
    _clear_active()
    st.session_state.active_composition_id = composition_id
    st.session_state.current_invocation = (
        _invocation_from_round(latest_round) if latest_round else None
    )
    _set_editor(latest_snapshot.writing, composition_id)
    st.session_state.writing_input = latest_snapshot.writing
    if reflection and reflection.status == "completed":
        st.session_state.current_invocation = InvocationResult(
            reflection.thread_id, reflection.state
        )
        st.session_state.current_step = "Reflect"
    elif reflection and reflection.status == "failed":
        st.session_state.current_invocation = None
        st.session_state.current_step = "Reflect"
    elif latest_round and latest_round.status == "awaiting_clarification":
        st.session_state.current_step = "Choose"
    elif composition.revision_number > 0 and latest_round:
        st.session_state.current_step = "Revise"
        st.session_state.round_review_active = latest_round.status == "completed"
        st.session_state.selected_goal_ids = [
            goal["goal_id"] for goal in latest_snapshot.selected_goals
        ]
    else:
        st.session_state.current_step = "Choose"


def _show_error(error: Exception) -> None:
    if isinstance(error, RateLimitError):
        st.warning("The AI service is busy. Wait a moment and try again.")
    elif isinstance(error, AuthError):
        st.error("API authentication failed. Check the DeepSeek key configuration.")
    elif isinstance(error, InputValidationError):
        st.warning(str(error))
    elif isinstance(error, ResponseValidationError):
        st.error("The feedback could not be completed. Your draft is still here; retry when ready.")
    elif isinstance(error, (StorageError, sqlite3.Error)):
        st.error(
            "Saved history is unavailable. Your current editor text is still in this "
            "workspace; copy it before starting a new composition."
        )
    elif isinstance(error, APIError):
        st.error(str(error))
        st.info("This may be temporary. Your draft is preserved; try again in a moment.")
    elif isinstance(error, WritingAssistantError):
        st.error(str(error))
    else:
        st.error("An unexpected error stopped the review. Your current editor text is preserved.")
    if _debug_enabled():
        st.caption(f"Debug: {error}")


def _action_failed(error: Exception) -> None:
    st.session_state.last_error = error
    st.session_state.current_invocation = None
    st.rerun()


def _run_with_status(
    initial_label: str,
    action: Callable[[Callable[[str], None]], InvocationResult],
) -> InvocationResult:
    with st.status(initial_label, expanded=False) as status:
        def update(label: str) -> None:
            status.update(label=label)

        result = action(update)
        status.update(label="Review complete", state="complete")
        return result


def _start_review(service: WritingAssistantService, session_id: str) -> None:
    composition_id = uuid.uuid4().hex
    round_id = uuid.uuid4().hex
    thread_id = uuid.uuid4().hex
    snapshot_id = uuid.uuid4().hex
    try:
        state = make_review_state(
            st.session_state.writing_input,
            st.session_state.grade_level,
            composition_id=composition_id,
            round_id=round_id,
            thread_id=thread_id,
            genre_selection=st.session_state.genre_input,
            assignment_prompt=st.session_state.assignment_prompt_input,
            teacher_directions=st.session_state.teacher_directions_input,
            source_material=st.session_state.source_material_input,
            student_concerns=st.session_state.student_concerns_input,
            scenario_id=st.session_state.loaded_scenario_id,
            fixture_version=st.session_state.loaded_fixture_version,
            debug_enabled=st.session_state.get("capture_debug", False),
        )
        st.session_state.active_composition_id = composition_id
        st.session_state.current_step = "Choose"
        _set_editor(state["writing"], composition_id)
        invocation = _run_with_status(
            "Saving draft…",
            lambda callback: service.start_composition(
                session_id, state, snapshot_id, callback
            ),
        )
    except Exception as exc:
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    st.session_state.current_step = "Choose"
    st.session_state.selected_goal_ids = []
    st.session_state.round_review_active = False
    st.session_state.pending_revision_notice = None
    st.rerun()


def _resume_review(service: WritingAssistantService, session_id: str) -> None:
    try:
        invocation = _run_with_status(
            "Saving your answer…",
            lambda callback: service.resume_clarification(
                session_id,
                st.session_state.active_composition_id,
                st.session_state.get("clarification_answer", ""),
                callback,
            ),
        )
    except Exception as exc:
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    st.session_state.clarification_answer = ""
    if not invocation.pending:
        st.session_state.current_step = (
            "Revise" if invocation.state.get("revision_number", 0) else "Choose"
        )
        st.session_state.round_review_active = bool(
            invocation.state.get("revision_number", 0)
        )
    st.rerun()


def _retry_review(service: WritingAssistantService, session_id: str, final: bool = False) -> None:
    try:
        action = service.retry_final if final else service.retry_round
        invocation = _run_with_status(
            "Retrying the saved review…",
            lambda callback: action(
                session_id, st.session_state.active_composition_id, callback
            ),
        )
    except Exception as exc:
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    if not final:
        st.session_state.round_review_active = bool(
            invocation.state.get("revision_number", 0)
        )
    st.rerun()


def _current_state(service: WritingAssistantService) -> dict[str, Any]:
    invocation = st.session_state.get("current_invocation")
    if invocation:
        return invocation.state
    composition_id = st.session_state.get("active_composition_id")
    if composition_id:
        latest = service.storage.get_latest_round(composition_id)
        if latest:
            return latest.state
        reflection = service.storage.get_reflection(composition_id)
        if reflection:
            return reflection.state
    return {}


def _latest_completed_round(service: WritingAssistantService) -> RoundRecord | None:
    composition_id = st.session_state.get("active_composition_id")
    if not composition_id:
        return None
    return service.storage.get_latest_round(composition_id)


def _selected_candidates(state: dict[str, Any]) -> list[dict[str, Any]]:
    selected = set(st.session_state.get("selected_goal_ids", []))
    return [
        candidate
        for candidate in state.get("revision_candidates", [])
        if candidate["goal_id"] in selected
    ]


def _toggle_goal(goal_id: str, round_id: str) -> None:
    key = f"select_goal_{round_id}_{goal_id}"
    selected = list(st.session_state.get("selected_goal_ids", []))
    checked = st.session_state.get(key, False)
    if checked and goal_id not in selected:
        selected.append(goal_id)
    if not checked and goal_id in selected:
        selected.remove(goal_id)
    if len(selected) > 3:
        st.session_state[key] = False
        selected.remove(goal_id)
        st.session_state.selection_warning = "Choose no more than three goals."
    else:
        st.session_state.selection_warning = ""
    st.session_state.selected_goal_ids = selected


def _start_editing() -> None:
    if not st.session_state.get("selected_goal_ids"):
        st.session_state.selection_warning = "Select at least one goal before revising."
        return
    st.session_state.current_step = "Revise"
    st.session_state.round_review_active = False
    st.session_state.pending_revision_notice = None


def _choose_next_round(state: dict[str, Any]) -> None:
    for candidate in state.get("revision_candidates", []):
        st.session_state[f"select_goal_{state['round_id']}_{candidate['goal_id']}"] = False
    st.session_state.selected_goal_ids = []
    st.session_state.current_step = "Choose"
    st.session_state.round_review_active = False
    st.session_state.less_feedback = False
    st.session_state.stuck_requested = False


def _submit_revision(
    service: WritingAssistantService,
    session_id: str,
    confirmed: bool = False,
) -> None:
    composition_id = st.session_state.active_composition_id
    composition = service.storage.get_composition(composition_id)
    if composition is None or composition.session_id != session_id:
        _show_error(StorageError("Saved history is unavailable."))
        return
    current_text = st.session_state.get("editor_text", "")
    snapshots = service.storage.list_snapshots(composition_id)
    original = snapshots[0]
    previous = snapshots[-1]
    notice = change_notification(
        previous.writing, current_text, _small_change_threshold()
    )
    if notice["needs_confirmation"] and not confirmed:
        st.session_state.pending_revision_notice = notice
        return
    review_state = _current_state(service)
    selected = _selected_candidates(review_state)
    if not 1 <= len(selected) <= 3:
        st.session_state.selection_warning = "Select one to three goals before submitting a revision."
        return
    revision_number = composition.revision_number + 1
    reports = {
        goal["goal_id"]: {
            "No answer": "",
            "I tried this goal": "attempted",
            "I intentionally deferred this goal": "deferred",
        }.get(
            st.session_state.get(
                f"goal_report_{composition_id}_{revision_number}_{goal['goal_id']}",
                "No answer",
            ),
            "",
        )
        for goal in selected
    }
    round_id = uuid.uuid4().hex
    thread_id = uuid.uuid4().hex
    snapshot_id = uuid.uuid4().hex
    try:
        state = make_review_state(
            current_text,
            composition.grade_level,
            composition_id=composition_id,
            round_id=round_id,
            thread_id=thread_id,
            original_writing=original.writing,
            previous_writing=previous.writing,
            genre_selection=composition.genre_selection,
            assignment_prompt=composition.assignment_prompt,
            teacher_directions=composition.teacher_directions,
            source_material=composition.source_material,
            student_concerns=composition.student_concerns,
            scenario_id=composition.scenario_id,
            fixture_version=composition.fixture_version,
            revision_number=revision_number,
            selected_goals=selected,
            goal_self_reports=reports,
            text_diff=build_text_diff(previous.writing, current_text),
            debug_enabled=st.session_state.get("capture_debug", False),
        )
        invocation = _run_with_status(
            "Saving revision snapshot…",
            lambda callback: service.submit_revision(
                session_id, state, snapshot_id, callback
            ),
        )
    except Exception as exc:
        st.session_state.current_invocation = None
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    st.session_state.current_step = "Revise"
    st.session_state.round_review_active = not invocation.pending
    st.session_state.pending_revision_notice = None
    st.session_state.less_feedback = False
    st.session_state.stuck_requested = False
    st.rerun()


def _correct_genre(service: WritingAssistantService, session_id: str, genre: Genre) -> None:
    composition_id = st.session_state.active_composition_id
    composition = service.storage.get_composition(composition_id)
    snapshots = service.storage.list_snapshots(composition_id)
    latest_round = service.storage.get_latest_round(composition_id)
    if composition is None or not snapshots or latest_round is None:
        _show_error(StorageError("Saved history is unavailable."))
        return
    current = snapshots[-1]
    previous = snapshots[-2] if len(snapshots) > 1 else None
    round_id = uuid.uuid4().hex
    thread_id = uuid.uuid4().hex
    try:
        state = make_review_state(
            current.writing,
            composition.grade_level,
            composition_id=composition_id,
            round_id=round_id,
            thread_id=thread_id,
            original_writing=snapshots[0].writing,
            previous_writing=previous.writing if previous else "",
            genre_selection=genre,
            assignment_prompt=composition.assignment_prompt,
            teacher_directions=composition.teacher_directions,
            source_material=composition.source_material,
            student_concerns=composition.student_concerns,
            scenario_id=composition.scenario_id,
            fixture_version=composition.fixture_version,
            revision_number=composition.revision_number,
            selected_goals=current.selected_goals,
            goal_self_reports=current.goal_self_reports,
            text_diff=(
                build_text_diff(previous.writing, current.writing) if previous else {}
            ),
            debug_enabled=st.session_state.get("capture_debug", False),
        )
        invocation = _run_with_status(
            "Saving genre correction…",
            lambda callback: service.reassess_genre(session_id, state, callback),
        )
    except Exception as exc:
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    st.session_state.selected_goal_ids = []
    st.session_state.round_review_active = composition.revision_number > 0
    st.session_state.current_step = "Revise" if composition.revision_number else "Choose"
    st.rerun()


def _request_finish() -> None:
    st.session_state.finish_dialog_open = True


def _finish(service: WritingAssistantService, session_id: str) -> None:
    composition_id = st.session_state.active_composition_id
    composition = service.storage.get_composition(composition_id)
    snapshots = service.storage.list_snapshots(composition_id)
    latest_round = service.storage.get_latest_round(composition_id)
    if composition is None or len(snapshots) < 1 or latest_round is None:
        _show_error(StorageError("Saved history is unavailable."))
        return
    original = snapshots[0]
    final = snapshots[-1]
    latest_state = latest_round.state
    revision_history = [
        {
            "revision_number": snapshot.revision_number,
            "selected_goals": snapshot.selected_goals,
        }
        for snapshot in snapshots[1:]
    ]
    try:
        state = make_review_state(
            final.writing,
            composition.grade_level,
            composition_id=composition_id,
            round_id=f"final_{composition_id}",
            thread_id=uuid.uuid4().hex,
            review_mode="final",
            original_writing=original.writing,
            genre_selection=composition.genre_selection,
            assignment_prompt=composition.assignment_prompt,
            teacher_directions=composition.teacher_directions,
            source_material=composition.source_material,
            student_concerns=composition.student_concerns,
            scenario_id=composition.scenario_id,
            fixture_version=composition.fixture_version,
            revision_number=composition.revision_number,
            selected_goals=final.selected_goals,
            text_diff=build_text_diff(original.writing, final.writing),
            debug_enabled=st.session_state.get("capture_debug", False),
        )
        state["working_genre"] = latest_state.get("working_genre", "")
        state["revision_history"] = revision_history
        st.session_state.current_step = "Reflect"
        invocation = _run_with_status(
            "Preparing the original/final comparison…",
            lambda callback: service.finish_composition(
                session_id,
                state,
                original.snapshot_id,
                final.snapshot_id,
                callback,
            ),
        )
    except Exception as exc:
        st.session_state.current_invocation = None
        _action_failed(exc)
        return
    st.session_state.current_invocation = invocation
    st.session_state.current_step = "Reflect"
    st.session_state.finish_dialog_open = False
    st.rerun()


@st.dialog("Finish revising?")
def _finish_dialog(service: WritingAssistantService, session_id: str) -> None:
    st.write("Are you sure you want to stop revising this essay?")
    st.write("We will compare your original and latest submitted drafts.")
    composition_id = st.session_state.active_composition_id
    if composition_id:
        snapshots = service.storage.list_snapshots(composition_id)
        if snapshots and st.session_state.editor_text != snapshots[-1].writing:
            st.caption("Unsubmitted edits stay in the editor but are not part of this comparison.")
    keep, confirm = st.columns(2)
    if keep.button("Keep revising", key="keep_revising", width="stretch"):
        st.session_state.finish_dialog_open = False
        st.rerun()
    if confirm.button(
        "Yes, finish and reflect", key="confirm_finish", type="primary", width="stretch"
    ):
        _finish(service, session_id)


def _request_scenario() -> None:
    scenario_id = st.session_state.practice_scenario
    has_content = bool(
        st.session_state.active_composition_id
        or any(
            st.session_state.get(key, "").strip()
            for key in (
                "writing_input",
                "assignment_prompt_input",
                "teacher_directions_input",
                "source_material_input",
                "student_concerns_input",
            )
        )
    )
    if has_content:
        st.session_state.pending_scenario_id = scenario_id
    else:
        _apply_scenario(get_scenario(scenario_id))


def _apply_scenario(scenario: PracticeScenario) -> None:
    _clear_active()
    st.session_state.writing_input = scenario.draft
    st.session_state.grade_level = scenario.grade_level
    st.session_state.genre_input = scenario.genre
    st.session_state.assignment_prompt_input = scenario.assignment_prompt
    st.session_state.teacher_directions_input = scenario.teacher_directions
    st.session_state.source_material_input = scenario.source_material
    st.session_state.student_concerns_input = scenario.student_concerns
    st.session_state.loaded_scenario_id = scenario.scenario_id
    st.session_state.loaded_fixture_version = scenario.fixture_version
    st.session_state.pending_scenario_id = None


def _render_scenario_loader() -> None:
    scenarios = load_scenarios()
    st.selectbox(
        "Load a practice scenario",
        options=[scenario.scenario_id for scenario in scenarios],
        format_func=lambda scenario_id: get_scenario(scenario_id).name,
        key="practice_scenario",
        help="All scenarios are synthetic and remain editable after loading.",
    )
    st.button("Load practice scenario", key="load_scenario", on_click=_request_scenario)
    pending_id = st.session_state.get("pending_scenario_id")
    if pending_id:
        st.warning("Replace the current inputs and active composition with this practice scenario? Saved history remains available.")
        replace, keep = st.columns(2)
        if replace.button("Replace inputs", key="confirm_scenario_overwrite"):
            _apply_scenario(get_scenario(pending_id))
            st.rerun()
        if keep.button("Keep my current work", key="cancel_scenario_overwrite"):
            st.session_state.pending_scenario_id = None
            st.rerun()


def _render_draft(service: WritingAssistantService, session_id: str) -> None:
    _, center, _ = st.columns([1, 3, 1])
    with center:
        st.markdown('<div class="draft-layout-marker"></div>', unsafe_allow_html=True)
        st.subheader("Start with your draft")
        st.caption("Only your grade and draft are required. Your ideas and words stay yours.")
        _render_scenario_loader()
        if st.session_state.loaded_scenario_id:
            st.caption(
                f"Loaded synthetic scenario: {st.session_state.loaded_scenario_id} "
                f"({st.session_state.loaded_fixture_version})"
            )
        active_id = st.session_state.active_composition_id
        if active_id:
            st.info("This is your current working text. Return to Revise to use your selected goals.")
        st.selectbox("Grade level", GRADE_LEVELS, key="grade_level")
        st.text_area(
            "Student draft",
            key="writing_input",
            height=330,
            max_chars=MAX_DRAFT_CHARS,
            placeholder="Paste a synthetic draft here…",
        )
        if active_id:
            st.session_state.editor_text = st.session_state.writing_input
            st.session_state[_editor_key(active_id)] = {"value": st.session_state.writing_input}
        with st.expander("Add assignment details", expanded=False):
            st.selectbox(
                "Genre",
                list(GENRE_LABELS),
                format_func=GENRE_LABELS.get,
                key="genre_input",
                help="Auto-detect is a correctable working inference, not a fact about your intent.",
            )
            st.text_area("Assignment prompt (optional)", key="assignment_prompt_input", height=100)
            st.text_area(
                "Teacher directions or required structure (optional)",
                key="teacher_directions_input",
                height=100,
                placeholder="For example: Use RACES and explain your evidence.",
            )
            st.text_area(
                "Source material (optional)",
                key="source_material_input",
                height=150,
                max_chars=MAX_SOURCE_CHARS,
                placeholder="Paste the supplied synthetic passage if the task depends on it.",
            )
            st.text_area(
                "Student concern or goal (optional)",
                key="student_concerns_input",
                height=90,
                placeholder="What would you like help with?",
            )
        st.warning(
            "Do not submit writing containing real names, schools, or personal information. "
            "This is a demo system — your input is sent to an external AI service."
        )
        if st.button(
            "Get writing feedback", key="analyze_writing", type="primary", width="stretch"
        ):
            _start_review(service, session_id)


def _render_steps(service: WritingAssistantService) -> None:
    state = _current_state(service)
    active = bool(st.session_state.active_composition_id)
    route = state.get("routing_decision")
    reflection = (
        service.storage.get_reflection(st.session_state.active_composition_id)
        if active
        else None
    )
    final_complete = bool(reflection and reflection.status == "completed")
    final_failed = bool(reflection and reflection.status == "failed")
    normal_review = (
        active
        and reflection is None
        and route in ("support_agent", "direct_response")
    )
    has_candidates = bool(state.get("revision_candidates"))
    has_selection = bool(st.session_state.selected_goal_ids)
    available = {
        "Draft": True,
        "Choose": normal_review,
        "Revise": normal_review and has_candidates and (has_selection or state.get("revision_number", 0) > 0),
        "Reflect": normal_review or final_complete or final_failed,
    }
    columns = st.columns(4)
    for index, (step, column) in enumerate(zip(STEPS, columns), start=1):
        current = st.session_state.current_step == step and not st.session_state.show_history
        if column.button(
            f"{index} {step}",
            key=f"step_{step}",
            type="primary" if current else "secondary",
            disabled=not available[step],
            width="stretch",
        ):
            if step == "Reflect" and not final_complete:
                _request_finish()
            else:
                st.session_state.show_history = False
                st.session_state.current_step = step
                if step == "Revise" and state.get("revision_number", 0) > 0:
                    st.session_state.round_review_active = True
                st.rerun()
    st.markdown(
        f'<span class="v3-step-status" aria-current="step">Current step: '
        f'{st.session_state.current_step}</span>',
        unsafe_allow_html=True,
    )


def _render_clarification(service: WritingAssistantService, session_id: str) -> None:
    invocation = st.session_state.current_invocation
    st.subheader("One question before writing feedback")
    st.info(invocation.pending_question)
    if invocation.pending_choices:
        st.caption("Possible answers: " + " | ".join(invocation.pending_choices))
    st.caption("No writing feedback is generated until this essential context is clear.")
    with st.form("clarification_form"):
        st.text_area(
            "Your answer",
            key="clarification_answer",
            height=110,
            placeholder="Choose one of the possibilities above or explain in your own words.",
        )
        submitted = st.form_submit_button(
            "Answer and resume", key="resume_clarification", type="primary"
        )
    if submitted:
        _resume_review(service, session_id)


def _render_source_limitations(state: dict[str, Any]) -> None:
    for limitation in state.get("source_limitations", []):
        st.warning(f"**Source limitation:** {limitation}")


def _render_genre(service: WritingAssistantService, session_id: str, state: dict[str, Any]) -> None:
    working = state.get("working_genre", "")
    if not working:
        return
    st.caption(
        f"Working genre: **{GENRE_LABELS[working]}** · "
        f"Basis: {state.get('genre_basis', 'Not supplied')} · "
        f"Confidence: {state.get('genre_confidence', '') or 'not supplied'}"
    )
    correction = st.selectbox(
        "Correct the working genre if needed",
        ["argument", "informational", "narrative"],
        index=["argument", "informational", "narrative"].index(working),
        format_func=GENRE_LABELS.get,
        key=f"genre_correction_{state['round_id']}",
    )
    if st.button(
        "Apply genre correction",
        key=f"apply_genre_{state['round_id']}",
        disabled=correction == working,
        help="Reassesses the latest submitted draft before showing feedback under the new criteria.",
    ):
        _correct_genre(service, session_id, correction)


def _render_candidate(candidate: dict[str, Any], selectable: bool, round_id: str) -> None:
    goal_id = candidate["goal_id"]
    if selectable:
        key = f"select_goal_{round_id}_{goal_id}"
        st.session_state.setdefault(key, goal_id in st.session_state.selected_goal_ids)
        st.checkbox(
            candidate["title"],
            key=key,
            on_change=_toggle_goal,
            args=(goal_id, round_id),
        )
    else:
        st.markdown(f"**{candidate['title']}**")
    st.markdown(candidate["why_it_matters"])
    st.caption(
        f"Paragraph {candidate['paragraph_number']}, occurrence {candidate['occurrence']}: "
        f"“{candidate['draft_reference']}”"
    )
    st.markdown(f"**Try this:** {candidate['revision_action']}")
    with st.expander("Show a hint", expanded=False):
        st.markdown(format_hint(candidate["hint"]))
    if st.session_state.stuck_requested:
        st.info(f"One next step: {candidate['stuck_step']}")
    st.divider()


def _render_editor(state: dict[str, Any]) -> None:
    composition_id = st.session_state.active_composition_id
    reviewing_submitted_goals = (
        st.session_state.round_review_active and state.get("revision_number", 0) > 0
    )
    selected = (
        state.get("selected_goals", [])
        if reviewing_submitted_goals
        else _selected_candidates(state)
    )
    if selected:
        st.info(
            "**Selected revision goals:** "
            + " · ".join(candidate["title"] for candidate in selected)
        )
    else:
        st.caption("Select one to three goals in the feedback panel.")
    value = goal_highlight_editor(
        composition_id=composition_id,
        initial_value=st.session_state.editor_text,
        selected_goals=selected,
    )
    stale = [
        goal["title"]
        for goal in selected
        if locate_reference(
            value,
            goal["draft_reference"],
            goal["paragraph_number"],
            goal["occurrence"],
        )
        is None
    ]
    if stale:
        st.caption("A referenced passage changed, so its old highlight was removed. No unrelated text was highlighted.")


def _render_revision_notice(service: WritingAssistantService, session_id: str) -> None:
    notice = st.session_state.get("pending_revision_notice")
    if not notice:
        return
    if notice["unchanged"]:
        message = "The submitted text is unchanged from the last snapshot."
    else:
        message = (
            f"Factual change summary: {notice['added_words']} words added and "
            f"{notice['removed_words']} words removed. This does not judge whether the "
            "change is meaningful."
        )
    st.warning(message)
    st.caption("Return to editing, continue with a whole-draft review, or finish instead.")
    edit, continue_review, finish = st.columns(3)
    if edit.button("Return to editing", key="return_to_editing"):
        st.session_state.pending_revision_notice = None
        st.rerun()
    if continue_review.button("Continue review", key="confirm_small_revision"):
        _submit_revision(service, session_id, confirmed=True)
    if finish.button("Finish and reflect", key="finish_after_change_notice"):
        st.session_state.pending_revision_notice = None
        _request_finish()
        st.rerun()


def _render_process(service: WritingAssistantService) -> None:
    composition_id = st.session_state.active_composition_id
    snapshots = service.storage.list_snapshots(composition_id)
    reflection = service.storage.get_reflection(composition_id)
    milestones = ["Draft submitted"]
    if st.session_state.selected_goal_ids or len(snapshots) > 1:
        milestones.append("Revision goals selected")
    milestones.extend(
        f"Revision {snapshot.revision_number} submitted" for snapshot in snapshots[1:]
    )
    if reflection and reflection.status == "completed":
        milestones.append("Final reflection complete")
    st.caption("Process milestones: " + " → ".join(milestones))


def _render_teacher(state: dict[str, Any]) -> None:
    st.warning("Simulated teacher review: no teacher has been notified.")
    st.markdown(state.get("student_output", ""))
    st.caption("Normal writing feedback and revision choices are paused for this submission.")


def _render_workspace(service: WritingAssistantService, session_id: str) -> None:
    state = _current_state(service)
    latest_round = _latest_completed_round(service)
    if latest_round and latest_round.status == "failed":
        st.error("This saved review could not be completed. Your submitted snapshot and editor text are preserved.")
        if _debug_enabled() and latest_round.error:
            st.caption(f"Debug: {latest_round.error}")
        if st.session_state.editor_text:
            st.caption("Copy your preserved editor text:")
            st.code(st.session_state.editor_text, language=None)
        st.button("Retry saved review", key="retry_round", on_click=_retry_review, args=(service, session_id))
        return
    if state.get("teacher_message"):
        _render_teacher(state)
        return
    if not state:
        _render_recovery()
        return

    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="workspace-marker"></div>', unsafe_allow_html=True)
        st.subheader("Your essay")
        st.caption(
            f"Grade: {state['grade_level']} · Revision {state.get('revision_number', 0)} · "
            + ("Source attached" if state["source_material_available"] else "No source attached")
        )
        with st.container(border=True, height=640):
            _render_editor(state)
    with right:
        st.subheader("Feedback")
        if state.get("routing_decision") == "direct_response":
            st.markdown(state.get("student_output", ""))
            render_goal_feedback(
                state.get("goal_feedback", []), state.get("selected_goals", [])
            )
            _render_source_limitations(state)
            st.button("Finish and reflect", key="finish_direct", on_click=_request_finish)
            _render_process(service)
            return
        review_active = st.session_state.round_review_active and state.get("revision_number", 0) > 0
        with st.container(border=True, height=510):
            if review_active:
                st.success(f"Revision {state['revision_number']} snapshot saved and reviewed.")
                render_goal_feedback(
                state.get("goal_feedback", []), state.get("selected_goals", [])
            )
            st.markdown("### What is already working")
            for strength in state.get("feedback_strengths", state.get("strengths", [])):
                st.markdown(f"- {strength}")
            _render_source_limitations(state)
            if st.session_state.current_step == "Choose":
                _render_genre(service, session_id, state)
                st.markdown("### Choose 1–3 revision goals")
                st.caption("You do not need to fix everything. Selection and hints do not make another AI call.")
                candidates = state.get("revision_candidates", [])
                if st.session_state.less_feedback:
                    candidates = candidates[:1]
                for candidate in candidates:
                    _render_candidate(candidate, True, state["round_id"])
            elif not review_active:
                st.markdown("### Your selected goals")
                candidates = _selected_candidates(state)
                if st.session_state.less_feedback or st.session_state.stuck_requested:
                    candidates = candidates[:1]
                for candidate in candidates:
                    _render_candidate(candidate, False, state["round_id"])
                if not st.session_state.less_feedback:
                    st.button("Show less feedback", key="show_less_feedback", on_click=lambda: st.session_state.update(less_feedback=True))
                else:
                    st.button("Show all selected feedback", key="show_all_feedback", on_click=lambda: st.session_state.update(less_feedback=False, stuck_requested=False))
                if not st.session_state.stuck_requested:
                    st.button("I’m stuck", key="im_stuck", on_click=lambda: st.session_state.update(stuck_requested=True, less_feedback=True))
                st.markdown("### Optional goal self-report")
                st.caption("Share what you tried or intentionally deferred. Skipping this makes no attempt assumption.")
                next_revision = state.get("revision_number", 0) + 1
                for candidate in _selected_candidates(state):
                    st.selectbox(
                        candidate["title"],
                        ["No answer", "I tried this goal", "I intentionally deferred this goal"],
                        key=f"goal_report_{st.session_state.active_composition_id}_{next_revision}_{candidate['goal_id']}",
                    )
            else:
                st.caption("New choices will appear here when you choose another round. You can also finish now.")
        st.markdown('<div class="v3-workspace-footer"></div>', unsafe_allow_html=True)
        if st.session_state.selection_warning:
            st.warning(st.session_state.selection_warning)
        if st.session_state.current_step == "Choose":
            st.caption(f"{len(st.session_state.selected_goal_ids)} of 3 goals selected")
            start, finish = st.columns(2)
            if start.button(
                "Start revising",
                key="start_revising",
                type="primary",
                disabled=not st.session_state.selected_goal_ids,
                width="stretch",
            ):
                _start_editing()
                st.rerun()
            finish.button("Finish and reflect", key="finish_choose", on_click=_request_finish, width="stretch")
        elif review_active:
            choose, finish = st.columns(2)
            if choose.button(
                "Choose goals for another round",
                key="choose_next_round",
                type="primary",
                width="stretch",
            ):
                _choose_next_round(state)
                st.rerun()
            finish.button("Finish and reflect", key="finish_review", on_click=_request_finish, width="stretch")
        else:
            submit, finish = st.columns(2)
            if submit.button(
                "Submit revision",
                key="submit_revision",
                type="primary",
                disabled=not 1 <= len(st.session_state.selected_goal_ids) <= 3,
                width="stretch",
            ):
                _submit_revision(service, session_id)
            finish.button("Finish and reflect", key="finish_revise", on_click=_request_finish, width="stretch")
        _render_revision_notice(service, session_id)
        _render_process(service)


def _render_reflection(service: WritingAssistantService, session_id: str) -> None:
    composition_id = st.session_state.active_composition_id
    reflection = service.storage.get_reflection(composition_id)
    if reflection is None:
        st.info("Confirm that you want to stop before the final comparison begins.")
        st.button("Finish and reflect", key="finish_reflect_view", on_click=_request_finish)
        return
    if reflection.status == "failed":
        st.error("The final reflection could not be completed. Your drafts are preserved.")
        if _debug_enabled() and reflection.error:
            st.caption(f"Debug: {reflection.error}")
        st.button("Retry final reflection", key="retry_final", on_click=_retry_review, args=(service, session_id, True))
        return
    invocation = st.session_state.current_invocation
    state = invocation.state if invocation and invocation.state.get("review_mode") == "final" else reflection.state
    snapshots = service.storage.list_snapshots(composition_id)
    original, final = snapshots[0], snapshots[-1]
    first, second = st.columns(2)
    with first:
        st.subheader("Original submission")
        st.text_area("Original submitted draft", original.writing, height=360, disabled=True, key=f"original_{composition_id}")
    with second:
        st.subheader("Latest submitted revision")
        st.text_area("Final submitted draft", final.writing, height=360, disabled=True, key=f"final_{composition_id}")
    diff = state.get("text_diff", {})
    st.caption(
        f"Deterministic comparison: {diff.get('added_words', 0)} words added and "
        f"{diff.get('removed_words', 0)} words removed across the original/final diff. "
        "These counts do not judge quality."
    )
    with st.expander("See the deterministic text diff"):
        st.code(diff.get("unified_diff", "No text difference."), language="diff")
    render_final_reflection(state["final_reflection"])
    _render_process(service)


def _render_history(service: WritingAssistantService, session_id: str) -> None:
    st.subheader("Submitted draft history")
    st.caption("Snapshots are read-only. Editing the current essay never overwrites them.")
    compositions = service.storage.list_compositions(session_id)
    if not compositions:
        st.info("No saved compositions in this session.")
        return
    options = {item.composition_id: item for item in compositions}
    selected_id = st.selectbox(
        "Composition",
        list(options),
        format_func=lambda value: (
            f"{options[value].scenario_id or 'Manual composition'} | "
            f"{options[value].revision_number} revisions | {options[value].status}"
        ),
        key="history_composition",
    )
    snapshots = service.storage.list_snapshots(selected_id)
    for snapshot in snapshots:
        label = "Original submission" if snapshot.revision_number == 0 else f"Revision {snapshot.revision_number}"
        with st.expander(label, expanded=snapshot.revision_number == snapshots[-1].revision_number):
            st.text_area(
                f"{label} text",
                snapshot.writing,
                height=240,
                disabled=True,
                key=f"history_{snapshot.snapshot_id}",
            )
            if snapshot.selected_goals:
                st.markdown("**Goals attached to this submission**")
                for goal in snapshot.selected_goals:
                    report = snapshot.goal_self_reports.get(goal["goal_id"], "")
                    suffix = f" — student self-report: {report}" if report else ""
                    st.markdown(f"- {goal['title']}{suffix}")
            st.caption(f"Saved at {snapshot.created_at}")
    if st.button("Open this composition", key="open_history_composition"):
        _load_composition(service, selected_id)
        st.rerun()


def _render_recovery() -> None:
    st.error("Saved history is unavailable. It has not been restored.")
    st.write(
        "Your current editor text may still be available in this runtime. Copy it before "
        "starting a new composition. The app will not claim that missing history was recovered."
    )
    current = st.session_state.get("editor_text") or st.session_state.get("writing_input", "")
    if current:
        st.code(current, language=None)
    st.button("Start a new composition", key="recovery_new_composition", on_click=_new_blank_composition)


def _render_developer_sidebar(client: DeepSeekClient) -> dict[str, bool]:
    st.sidebar.header("Developer controls")
    st.sidebar.markdown("**V3 Iterative Revision Coach**")
    st.sidebar.caption(
        f"Model: {client.model} | Thinking: {'on' if client.thinking else 'off'} | "
        f"Reasoning effort: {client.reasoning_effort if client.thinking else 'not used'}"
    )
    st.sidebar.caption(
        "V3 uses the explicitly configured model mode and never switches modes automatically."
    )
    options = {
        "show_state": st.sidebar.checkbox("Show final state", value=True, key="show_state"),
        "show_timing": st.sidebar.checkbox("Show timing and token use", value=True, key="show_timing"),
        "show_logs": st.sidebar.checkbox("Show logs", value=False, key="show_logs"),
        "show_prompts": False,
    }
    if _debug_enabled():
        options["show_prompts"] = st.sidebar.checkbox(
            "Show captured final prompts/responses", value=False, key="show_prompts"
        )
        st.sidebar.checkbox(
            "Capture final prompts/responses on new reviews", value=False, key="capture_debug"
        )
        st.sidebar.caption("Raw hidden reasoning is never captured or displayed.")
    else:
        st.session_state.capture_debug = False
    return options


def _render_data_controls(service: WritingAssistantService, session_id: str) -> None:
    with st.expander("Session and data", expanded=False):
        st.caption(
            "Bookmark the session URL to restore server-saved history while the SQLite store "
            "remains available. Anyone with that URL may access the same view; this is not authentication."
        )
        st.caption("Data is retained until manual deletion or local/cloud filesystem replacement.")
        st.checkbox("I understand deletion is permanent", key="confirm_delete")
        if st.button("Delete my data", key="delete_my_data", disabled=not st.session_state.confirm_delete):
            service.delete_session(session_id)
            st.query_params.clear()
            st.session_state.clear()
            st.rerun()


def render_dashboard(service: WritingAssistantService, client: DeepSeekClient) -> None:
    _initialize_state()
    session_id = _session_id()
    try:
        if "restore_initialized" not in st.session_state:
            st.session_state.restore_initialized = True
            records = service.storage.list_compositions(session_id)
            if records:
                _load_composition(service, records[0].composition_id)
        active_id = st.session_state.active_composition_id
        if active_id:
            composition = service.storage.get_composition(active_id)
            if composition is None or composition.session_id != session_id:
                _render_recovery()
                return
    except (sqlite3.Error, ValueError, StorageError) as exc:
        _show_error(exc)
        _render_recovery()
        return

    st.markdown(STAGE_CSS, unsafe_allow_html=True)
    title_column, new_column, history_column, developer_column, observability_column = st.columns([2.5, 0.9, 0.9, 1.4, 1.4])
    title_column.title("Writing Coach")
    title_column.caption("Your ideas. Your words. One revision at a time.")
    if new_column.button("New composition", key="new_composition", width="stretch"):
        _clear_active()
        st.rerun()
    if history_column.button("History", key="history_button", width="stretch"):
        st.session_state.show_history = True
        st.rerun()
    if developer_column.button(
        "Hide Developer Controls" if st.session_state.developer_controls_visible else "Show Developer Controls",
        key="toggle_developer_controls",
        width="stretch",
    ):
        st.session_state.developer_controls_visible = not st.session_state.developer_controls_visible
        st.rerun()
    if observability_column.button(
        "Hide Agent Observability" if st.session_state.agent_observability_visible else "Show Agent Observability",
        key="toggle_agent_observability",
        width="stretch",
    ):
        st.session_state.agent_observability_visible = not st.session_state.agent_observability_visible
        st.rerun()

    last_error = st.session_state.pop("last_error", None)
    if last_error is not None:
        _show_error(last_error)

    options = (
        _render_developer_sidebar(client)
        if st.session_state.developer_controls_visible
        else {
            "show_state": st.session_state.get("show_state", True),
            "show_timing": st.session_state.get("show_timing", True),
            "show_logs": st.session_state.get("show_logs", False),
            "show_prompts": False,
        }
    )
    if not st.session_state.developer_controls_visible:
        st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

    try:
        if st.session_state.show_history:
            if st.button("Back to workspace", key="back_to_workspace"):
                st.session_state.show_history = False
                st.rerun()
            _render_history(service, session_id)
        else:
            _render_steps(service)
            invocation = st.session_state.current_invocation
            if invocation and invocation.pending:
                _render_clarification(service, session_id)
            elif st.session_state.current_step == "Draft" or not st.session_state.active_composition_id:
                _render_draft(service, session_id)
            elif st.session_state.current_step == "Reflect":
                _render_reflection(service, session_id)
            else:
                _render_workspace(service, session_id)
        _render_data_controls(service, session_id)
        if st.session_state.finish_dialog_open:
            _finish_dialog(service, session_id)
        if st.session_state.agent_observability_visible:
            st.divider()
            render_observability(_current_state(service), options)
    except (sqlite3.Error, StorageError, ValueError) as exc:
        _show_error(exc)
        _render_recovery()
