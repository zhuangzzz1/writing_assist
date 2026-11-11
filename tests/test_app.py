import json
import sqlite3
import uuid
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from agents.utils import APIError, DeepSeekClient
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from storage.sqlite_storage import SQLiteStorage
from tests.helpers import (
    INITIAL_DRAFT,
    candidate_for,
    coordinator_payload,
    final_coordinator_payload,
    final_support_payload,
    issue_for,
    observation_for,
    support_payload,
)
from ui.scenarios import get_scenario


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture(autouse=True)
def stub_graphviz_frontend(monkeypatch):
    monkeypatch.setattr("ui.observability.st.graphviz_chart", lambda *args, **kwargs: None)


def configured_app(tmp_path, monkeypatch, debug=False, evaluation=False):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_THINKING", "false")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ui.db"))
    monkeypatch.setenv("SHOW_EVALUATION_CONTROLS", str(evaluation).lower())
    monkeypatch.setenv("ENABLE_DEBUG_MODE", str(debug).lower())
    return AppTest.from_file(APP_PATH, default_timeout=20)


def install_responses(monkeypatch, responses):
    responses = list(responses)
    calls = []

    def fake_completion(self, messages, **kwargs):
        calls.append((messages, kwargs))
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        self.last_response_metadata = {
            "provider_request_id": "app-test",
            "model_name": self.model,
            "thinking_enabled": self.thinking,
            "reasoning_effort": self.reasoning_effort if self.thinking else "",
            "token_usage": {"total_tokens": 30},
        }
        return response

    monkeypatch.setattr(DeepSeekClient, "chat_completion", fake_completion)
    return calls


def review_pair(state, route="support_agent", **overrides):
    coordinator = coordinator_payload(state, route=route, **overrides)
    if route != "support_agent":
        return [coordinator]
    handoff = {**state, **json.loads(coordinator)}
    return [coordinator, support_payload(handoff)]


def revision_pair(original, revised, status="specific_improvement"):
    selected = [candidate_for(issue_for(original))]
    state = make_review_state(
        revised,
        "6th Grade",
        original_writing=original,
        previous_writing=original,
        revision_number=1,
        selected_goals=selected,
        text_diff=build_text_diff(original, revised),
    )
    observation = observation_for(
        status=status,
        observation=(
            "The revised explanation adds a clearer connection."
            if status == "specific_improvement"
            else "The submitted text does not yet show a change to this selected goal."
        ),
        carry_forward=status != "specific_improvement",
    )
    return review_pair(state, observations=[observation])


def final_pair(original, revised):
    state = make_review_state(
        revised,
        "6th Grade",
        review_mode="final",
        original_writing=original,
        revision_number=1,
        text_diff=build_text_diff(original, revised),
    )
    coordinator = final_coordinator_payload(state, changed=original != revised)
    values = json.loads(coordinator)
    handoff = {
        **state,
        "original_strengths": values["original_strengths"],
        "comparison_improvements": values["improvements"],
        "comparison_regressions": values["regressions"],
        "future_areas": values["future_areas"],
    }
    return [coordinator, final_support_payload(handoff)]


def start_support(app):
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.button(key="analyze_writing").click().run()
    assert not app.exception
    assert app.session_state.current_invocation.state["revision_candidates"]
    return app.session_state.current_invocation.state


def goal_key(app, goal_id="goal_1"):
    round_id = app.session_state.current_invocation.state["round_id"]
    return f"select_goal_{round_id}_{goal_id}"


def enter_revision(app, goal_id="goal_1"):
    app.checkbox(key=goal_key(app, goal_id)).set_value(True).run()
    app.button(key="start_revising").click().run()
    assert app.session_state.current_step == "Revise"


def set_editor(app, value):
    composition_id = app.session_state.active_composition_id
    app.session_state[f"essay_editor_{composition_id}"] = {"value": value}
    app.run()
    assert app.session_state.editor_text == value


def test_student_default_ui_and_evaluation_controls_are_independently_gated(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch).run()

    assert not app.exception
    assert app.title[0].value == "Writing Coach"
    assert app.text_area(key="writing_input").label == "Student draft"
    assert app.selectbox(key="grade_level").label == "Grade level"
    assert app.text_input(key="framework_name_input").label == "Writing structure my teacher asked for (optional)"
    assert app.text_area(key="student_concerns_input").label == "What I want help with (optional)"
    assert all(item.key != "affect_check_in" for item in app.selectbox)
    assert all(item.key != "toggle_developer_controls" for item in app.button)
    assert all(item.key != "toggle_agent_observability" for item in app.button)
    assert all(item.key != "show_prompts" for item in app.checkbox)
    layout_css = next(
        item.value for item in app.markdown if ".block-container" in item.value and "<style>" in item.value
    )
    assert "max-width: min(96vw, 2000px)" in layout_css
    assert "clamp(680px, 62vw, 1100px)" in layout_css
    assert "height: clamp(280px, 42vh, 560px)" in layout_css
    assert "clamp(440px, calc(100vh - 380px), 780px)" in layout_css
    assert "height: clamp(280px, 40vh, 500px)" in layout_css
    assert "--v3-brand: #2f54c0" in layout_css
    assert "font-family: 'Lora', Georgia, serif" in layout_css
    privacy = next(
        item.value for item in app.markdown if "Do not submit writing containing real names" in item.value
    )
    assert 'class="v3-privacy-note"' in privacy
    assert "This is a demo system — your input is sent to an external AI service." in privacy

    monkeypatch.setenv("SHOW_EVALUATION_CONTROLS", "true")
    app.run()
    assert app.button(key="toggle_developer_controls").label == "Show Developer Controls"
    assert app.button(key="toggle_agent_observability").label == "Show Agent Observability"
    app.button(key="toggle_developer_controls").click().run()
    assert app.session_state.developer_controls_visible is True
    assert app.session_state.agent_observability_visible is False
    app.button(key="toggle_agent_observability").click().run()
    assert app.session_state.agent_observability_visible is True

    monkeypatch.setenv("SHOW_EVALUATION_CONTROLS", "false")
    app.run()
    assert app.session_state.developer_controls_visible is False
    assert app.session_state.agent_observability_visible is False


def test_app_records_nonthinking_as_the_explicit_runtime_configuration(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()

    start_support(app)

    state = app.session_state.current_invocation.state
    assert state["model_config"]["thinking_enabled"] is False
    assert all(
        call["thinking_enabled"] is False
        for log in state["execution_logs"]
        for call in log["model_calls"]
    )


def test_scenario_loading_is_complete_editable_and_overwrite_protected(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch).run()
    first = get_scenario("garden_source_accurate")

    app.button(key="load_scenario").click().run()

    assert app.text_area(key="writing_input").value == first.draft
    assert app.text_area(key="assignment_prompt_input").value == first.assignment_prompt
    assert app.text_area(key="teacher_directions_input").value == first.teacher_directions
    assert app.text_area(key="source_material_input").value == first.source_material
    assert app.session_state.loaded_fixture_version == "v3.4.0"

    app.text_area(key="writing_input").set_value("My active synthetic draft.")
    app.selectbox(key="practice_scenario").set_value("races_informational_pollination")
    app.button(key="load_scenario").click().run()

    assert app.session_state.pending_scenario_id == "races_informational_pollination"
    assert app.text_area(key="writing_input").value == "My active synthetic draft."
    app.button(key="cancel_scenario_overwrite").click().run()
    assert app.text_area(key="writing_input").value == "My active synthetic draft."
    app.button(key="load_scenario").click().run()
    app.button(key="confirm_scenario_overwrite").click().run()
    assert "Bees" in app.text_area(key="writing_input").value


def test_initial_review_selection_hints_and_support_actions_make_no_extra_calls(tmp_path, monkeypatch):
    writing = "A clear claim.\n\nA first reason.\n\nA second reason.\n\nRepeated wording here."
    state = make_review_state(writing, "6th Grade")
    references = ["A clear claim.", "A first reason.", "A second reason.", "Repeated wording here."]
    issues = [issue_for(writing, reference, f"goal_{index}") for index, reference in enumerate(references, 1)]
    calls = install_responses(monkeypatch, review_pair(state, issues=issues))
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(writing)
    app.button(key="analyze_writing").click().run()

    assert app.button(key="start_revising").disabled is True
    assert len(calls) == 2
    assert any('class="v3-goal-quote"' in item.value for item in app.markdown)
    for index in range(1, 4):
        app.checkbox(key=goal_key(app, f"goal_{index}")).set_value(True).run()
    assert len(calls) == 2
    app.checkbox(key=goal_key(app, "goal_4")).set_value(True).run()

    selected_cards = [
        item.value
        for item in app.markdown
        if 'class="v3-goal-card v3-goal-card-selected"' in item.value
    ]
    assert len(selected_cards) == 3
    assert app.session_state.selected_goal_ids == ["goal_1", "goal_2", "goal_3"]
    assert app.checkbox(key=goal_key(app, "goal_4")).value is False
    assert app.session_state.selection_warning == "Choose no more than three goals."
    assert any(item.label == "Show a hint" for item in app.expander)

    app.button(key="start_revising").click().run()
    app.button(key="show_less_feedback").click().run()
    assert app.session_state.less_feedback is True
    app.button(key="im_stuck").click().run()

    assert app.session_state.stuck_requested is True
    assert len(calls) == 2
    assert not app.session_state.current_invocation.state.get("teacher_message")
    assert any("One next step:" in item.value for item in app.info)


def test_complete_revision_next_round_and_final_reflection_loop(tmp_path, monkeypatch):
    revised = INITIAL_DRAFT + "\n\nStudents practice noticing what others need.<img src=x onerror=alert(1)>"
    responses = [
        *review_pair(make_review_state(INITIAL_DRAFT, "6th Grade")),
        *revision_pair(INITIAL_DRAFT, revised),
        *final_pair(INITIAL_DRAFT, revised),
    ]
    calls = install_responses(monkeypatch, responses)
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    assert app.button(key="step_Draft").label == "✓ Draft"
    assert app.button(key="step_Choose").label == "2 Choose"
    enter_revision(app)
    assert app.button(key="step_Choose").label == "✓ Choose"
    set_editor(app, revised)
    app.button(key="submit_revision").click().run()
    assert app.session_state.pending_revision_notice["needs_confirmation"] is True
    app.button(key="confirm_small_revision").click().run()

    assert not app.exception
    assert len(calls) == 4
    assert app.button(key="choose_next_round")
    assert app.button(key="step_Revise").label == "✓ Revise"
    assert app.session_state.current_invocation.state["goal_feedback"][0]["status"] == "specific_improvement"
    storage = SQLiteStorage(str(tmp_path / "ui.db"))
    snapshots = storage.list_snapshots(app.session_state.active_composition_id)
    assert [item.writing for item in snapshots] == [INITIAL_DRAFT, revised]

    app.button(key="choose_next_round").click().run()
    assert app.session_state.current_step == "Choose"
    assert app.session_state.selected_goal_ids == []
    app.checkbox(key=goal_key(app)).set_value(True).run()
    app.button(key="start_revising").click().run()
    assert app.button(key="submit_revision").label == "Submit revision"
    app.button(key="finish_revise").click().run()
    assert app.session_state.finish_dialog_open is True
    app.button(key="confirm_finish").click().run()

    assert app.session_state.current_step == "Reflect"
    assert app.button(key="step_Reflect").label == "✓ Reflect"
    assert len(calls) == 6
    reflection = app.session_state.current_invocation.state["final_reflection"]
    assert reflection["improvements"]
    assert reflection["future_possibilities"]
    assert "ready to submit" not in json.dumps(reflection).lower()
    snapshot_panes = [
        item.value for item in app.markdown if 'class="v3-snapshot-pane"' in item.value
    ]
    assert len(snapshot_panes) == 2
    assert all('tabindex="0"' in pane for pane in snapshot_panes)
    assert any("&lt;img src=x onerror=alert(1)&gt;" in pane for pane in snapshot_panes)
    assert all("<img src=x" not in pane for pane in snapshot_panes)


def test_plain_self_report_options_preserve_the_deferred_value(tmp_path, monkeypatch):
    revised = INITIAL_DRAFT + "\n\nStudents explain how their actions help others."
    install_responses(
        monkeypatch,
        [
            *review_pair(make_review_state(INITIAL_DRAFT, "6th Grade")),
            *revision_pair(INITIAL_DRAFT, revised, status="improvement_not_yet_evident"),
        ],
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    enter_revision(app)
    composition_id = app.session_state.active_composition_id
    report_key = f"goal_report_{composition_id}_1_goal_1"
    assert app.selectbox(key=report_key).value == ""
    app.selectbox(key=report_key).set_value("deferred").run()
    set_editor(app, revised)
    app.button(key="submit_revision").click().run()
    app.button(key="confirm_small_revision").click().run()

    snapshots = SQLiteStorage(str(tmp_path / "ui.db")).list_snapshots(composition_id)
    assert snapshots[-1].goal_self_reports == {"goal_1": "deferred"}
    app.button(key="history_button").click().run()
    assert any("I decided to skip this for now" in item.value for item in app.markdown)


def test_unchanged_revision_confirmation_preserves_snapshot_until_confirmed(tmp_path, monkeypatch):
    responses = [
        *review_pair(make_review_state(INITIAL_DRAFT, "6th Grade")),
        *revision_pair(INITIAL_DRAFT, INITIAL_DRAFT, status="improvement_not_yet_evident"),
    ]
    calls = install_responses(monkeypatch, responses)
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    enter_revision(app)

    app.button(key="submit_revision").click().run()

    assert len(calls) == 2
    assert app.session_state.pending_revision_notice["unchanged"] is True
    composition_id = app.session_state.active_composition_id
    storage = SQLiteStorage(str(tmp_path / "ui.db"))
    assert len(storage.list_snapshots(composition_id)) == 1
    app.button(key="return_to_editing").click().run()
    assert app.session_state.pending_revision_notice is None

    app.button(key="submit_revision").click().run()
    app.button(key="confirm_small_revision").click().run()

    assert len(calls) == 4
    assert len(storage.list_snapshots(composition_id)) == 2
    assert app.session_state.current_invocation.state["goal_feedback"][0]["status"] == "improvement_not_yet_evident"
    assert not app.session_state.current_invocation.state.get("teacher_message")


def test_punctuation_only_revision_uses_factual_change_summary(tmp_path, monkeypatch):
    revised = INITIAL_DRAFT.replace("garden.", "garden!")
    install_responses(
        monkeypatch,
        [
            *review_pair(make_review_state(INITIAL_DRAFT, "6th Grade")),
            *revision_pair(INITIAL_DRAFT, revised, status="improvement_not_yet_evident"),
        ],
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    enter_revision(app)
    set_editor(app, revised)
    app.button(key="submit_revision").click().run()

    notice = app.session_state.pending_revision_notice
    assert notice["needs_confirmation"] is True
    assert "trivial" not in str(notice).lower()
    assert any("Factual change summary" in item.value for item in app.warning)


def test_finish_dialog_cancellation_and_reflect_step_preserve_state(tmp_path, monkeypatch):
    calls = install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    state = start_support(app)
    app.button(key="finish_choose").click().run()
    app.button(key="keep_revising").click().run()

    assert app.session_state.current_step == "Choose"
    assert app.session_state.current_invocation.state == state
    assert len(calls) == 2

    app.button(key="step_Reflect").click().run()
    assert app.session_state.finish_dialog_open is True
    assert app.session_state.current_step == "Choose"
    app.button(key="keep_revising").click().run()
    assert app.session_state.current_invocation.state == state


def test_direct_response_and_stop_without_revision_do_not_invent_comparison(tmp_path, monkeypatch):
    state = make_review_state(INITIAL_DRAFT, "6th Grade")
    calls = install_responses(monkeypatch, review_pair(state, route="direct_response"))
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.button(key="analyze_writing").click().run()

    assert app.session_state.current_invocation.state["revision_candidates"] == []
    assert any("do not see a meaningful revision issue" in item.value for item in app.markdown)
    app.button(key="finish_direct").click().run()
    app.button(key="confirm_finish").click().run()

    assert len(calls) == 1
    final = app.session_state.current_invocation.state
    assert final["final_reflection"]["improvements"] == []
    assert "No revised draft was submitted" in final["student_output"]


def test_clarification_has_no_premature_feedback_and_resumes_same_thread(tmp_path, monkeypatch):
    state = make_review_state(INITIAL_DRAFT, "6th Grade")
    responses = [
        coordinator_payload(state, route="ask_clarification"),
        *review_pair(state),
    ]
    calls = install_responses(monkeypatch, responses)
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.button(key="analyze_writing").click().run()
    thread_id = app.session_state.current_invocation.thread_id

    assert app.info[0].value == "What would you like help with?"
    assert all("Choose 1–3" not in item.value for item in app.markdown)
    app.text_area(key="clarification_answer").set_value("I want help explaining my reason.")
    app.button(key="resume_clarification").click().run()

    assert app.session_state.current_invocation.thread_id == thread_id
    assert len(calls) == 3
    assert app.session_state.current_invocation.state["clarification_history"]


def test_genre_correction_reassesses_latest_snapshot_and_preserves_unsubmitted_edit(tmp_path, monkeypatch):
    state = make_review_state(INITIAL_DRAFT, "6th Grade", genre_selection="auto")
    corrected = make_review_state(INITIAL_DRAFT, "6th Grade", genre_selection="narrative")
    calls = install_responses(
        monkeypatch,
        [*review_pair(state), *review_pair(corrected)],
    )
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.button(key="analyze_writing").click().run()
    composition_id = app.session_state.active_composition_id
    set_editor(app, INITIAL_DRAFT + "\n\nAn unsubmitted sentence.")
    round_id = app.session_state.current_invocation.state["round_id"]

    app.selectbox(key=f"genre_correction_{round_id}").set_value("narrative").run()
    app.button(key=f"apply_genre_{round_id}").click().run()

    assert app.session_state.current_invocation.state["working_genre"] == "narrative"
    assert app.session_state.editor_text.endswith("An unsubmitted sentence.")
    assert len(calls) == 4
    snapshots = SQLiteStorage(str(tmp_path / "ui.db")).list_snapshots(composition_id)
    assert len(snapshots) == 1
    assert snapshots[0].writing == INITIAL_DRAFT


def test_model_failure_preserves_draft_and_retries_without_duplicate_snapshot(tmp_path, monkeypatch):
    state = make_review_state(INITIAL_DRAFT, "6th Grade")
    install_responses(
        monkeypatch,
        [APIError("Temporary failure"), *review_pair(state)],
    )
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.button(key="analyze_writing").click().run()

    assert app.session_state.editor_text == INITIAL_DRAFT
    assert any("preserved" in item.value for item in app.info)
    app.button(key="retry_round").click().run()

    assert not app.exception
    assert app.session_state.current_invocation.state["routing_decision"] == "support_agent"
    storage = SQLiteStorage(str(tmp_path / "ui.db"))
    assert len(storage.list_snapshots(app.session_state.active_composition_id)) == 1


def test_saved_composition_restores_in_a_new_app_runtime(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    session_id = app.query_params["session_id"]
    composition_id = app.session_state.active_composition_id

    restored = configured_app(tmp_path, monkeypatch)
    restored.query_params["session_id"] = session_id
    restored.run()

    assert not restored.exception
    assert restored.session_state.active_composition_id == composition_id
    assert restored.session_state.editor_text == INITIAL_DRAFT
    assert restored.session_state.current_invocation.state["revision_candidates"]


def test_delete_my_data_removes_all_session_compositions(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    session_id = app.query_params["session_id"]

    app.checkbox(key="confirm_delete").set_value(True).run()
    app.button(key="delete_my_data").click().run()

    assert SQLiteStorage(str(tmp_path / "ui.db")).list_compositions(session_id) == []


def test_missing_backend_produces_recovery_view_with_copyable_current_text(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    database = tmp_path / "ui.db"
    database.unlink()

    app.run()

    assert not app.exception
    assert any("Saved history is unavailable" in item.value for item in app.error)
    assert any("has not been restored" in item.value for item in app.error)
    assert any(INITIAL_DRAFT in item.value for item in app.code)


def test_corrupt_backend_state_uses_recovery_instead_of_uncaught_exception(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    with sqlite3.connect(tmp_path / "ui.db") as connection:
        connection.execute("UPDATE rounds SET state_json = 'broken'")

    app.run()

    assert not app.exception
    assert any("Saved history is unavailable" in item.value for item in app.error)


def test_source_limitations_are_student_visible(tmp_path, monkeypatch):
    state = make_review_state(INITIAL_DRAFT, "6th Grade")
    limitation = "I cannot check whether the quotation matches its source without the passage."
    install_responses(
        monkeypatch, review_pair(state, source_limitations=[limitation])
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)

    assert any(limitation in item.value for item in app.warning)


def test_debug_capture_and_display_are_separately_opt_in(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch, debug=True, evaluation=True).run()
    app.button(key="toggle_developer_controls").click().run()
    app.button(key="toggle_agent_observability").click().run()
    app.checkbox(key="capture_debug").set_value(True)
    app.checkbox(key="show_logs").set_value(True)
    start_support(app)

    assert "prompt" in app.session_state.current_invocation.state["execution_logs"][0]
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" not in serialized
    assert "reasoning_content" not in serialized

    app.checkbox(key="show_prompts").set_value(True).run()
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" in serialized
    monkeypatch.setenv("ENABLE_DEBUG_MODE", "false")
    app.run()

    assert app.session_state.capture_debug is False
    assert all(item.key != "show_prompts" for item in app.checkbox)
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" not in serialized


def test_history_and_step_navigation_preserve_current_editor_text(tmp_path, monkeypatch):
    install_responses(
        monkeypatch, review_pair(make_review_state(INITIAL_DRAFT, "6th Grade"))
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    enter_revision(app)
    revised = INITIAL_DRAFT + "\n\nUnsubmitted work is preserved."
    set_editor(app, revised)

    app.button(key="step_Draft").click().run()
    assert app.text_area(key="writing_input").value == revised
    app.button(key="step_Revise").click().run()
    assert app.session_state.editor_text == revised
    app.button(key="history_button").click().run()

    assert not app.exception
    assert app.session_state.editor_text == revised
    assert any(item.disabled for item in app.text_area if item.key.startswith("history_"))


def test_malformed_session_url_warns_once_and_starts_new_session(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch)
    app.query_params["session_id"] = "not-a-uuid"
    app.run()

    assert any("session ID in the URL" in item.value for item in app.warning)
    replacement = app.query_params["session_id"]
    assert uuid.UUID(replacement).hex == replacement
    app.run()
    assert all("session ID in the URL" not in item.value for item in app.warning)


def test_corrupted_database_at_startup_shows_safe_recovery(tmp_path, monkeypatch):
    (tmp_path / "ui.db").write_bytes(b"not a SQLite database")
    app = configured_app(tmp_path, monkeypatch)

    app.run()

    assert not app.exception
    assert any("Saved history is unavailable" in item.value for item in app.error)
    assert any("has not been restored" in item.value for item in app.error)


def test_failed_final_reflection_can_be_retried_after_session_restore(tmp_path, monkeypatch):
    revised = INITIAL_DRAFT + "\n\nStudents explain how their actions help others."
    install_responses(
        monkeypatch,
        [
            *review_pair(make_review_state(INITIAL_DRAFT, "6th Grade")),
            *revision_pair(INITIAL_DRAFT, revised),
            APIError("Temporary final failure"),
            *final_pair(INITIAL_DRAFT, revised),
        ],
    )
    app = configured_app(tmp_path, monkeypatch).run()
    start_support(app)
    enter_revision(app)
    set_editor(app, revised)
    app.button(key="submit_revision").click().run()
    app.button(key="confirm_small_revision").click().run()
    app.button(key="finish_review").click().run()
    app.button(key="confirm_finish").click().run()
    assert not app.exception
    session_id = app.query_params["session_id"]
    composition_id = app.session_state.active_composition_id
    storage = SQLiteStorage(str(tmp_path / "ui.db"))
    assert storage.get_reflection(composition_id).status == "failed"

    restored = configured_app(tmp_path, monkeypatch)
    restored.query_params["session_id"] = session_id
    restored.run()

    assert not restored.exception
    assert restored.session_state.current_step == "Reflect"
    assert restored.button(key="step_Choose").disabled is True
    restored.button(key="retry_final").click().run()

    assert not restored.exception
    assert restored.session_state.current_invocation.state["final_reflection"]["improvements"]
    assert storage.get_reflection(composition_id).status == "completed"


def test_structured_framework_input_reaches_review_and_persistent_history(tmp_path, monkeypatch):
    state = make_review_state(
        INITIAL_DRAFT, "6th Grade", framework_name="CER", framework_components=[]
    )
    coverage = [
        {
            "framework": "CER",
            "component": component,
            "status": "issue",
            "reference": "",
            "paragraph_number": None,
            "occurrence": None,
            "goal_id": "goal_1",
        }
        for component in state["framework_components"]
    ]
    install_responses(monkeypatch, review_pair(state, framework_coverage=coverage))
    app = configured_app(tmp_path, monkeypatch).run()
    app.text_area(key="writing_input").set_value(INITIAL_DRAFT)
    app.text_input(key="framework_name_input").set_value("CER")

    app.button(key="analyze_writing").click().run()

    assert not app.exception
    composition_id = app.session_state.active_composition_id
    saved = SQLiteStorage(str(tmp_path / "ui.db")).get_composition(composition_id)
    assert saved.framework_name == "CER"
    assert saved.framework_components == ["Claim", "Evidence", "Reasoning"]
    assert app.session_state.current_invocation.state["framework_coverage"] == coverage


def test_new_composition_clears_scenario_and_framework_metadata(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch).run()
    app.button(key="load_scenario").click().run()
    assert app.session_state.loaded_scenario_id

    app.button(key="new_composition").click().run()

    assert app.session_state.loaded_scenario_id == ""
    assert app.session_state.loaded_fixture_version == ""
    assert app.session_state.writing_input == ""
    assert app.session_state.framework_name_input == ""
    assert app.session_state.framework_components_input == ""
