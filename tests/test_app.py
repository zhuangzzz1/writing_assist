from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from agents.utils import DeepSeekClient
from tests.helpers import (
    coordinator_payload,
    coordinator_payload_v2,
    support_payload,
    support_payload_v2,
)


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture(autouse=True)
def stub_graphviz_frontend(monkeypatch):
    monkeypatch.setattr("ui.observability.st.graphviz_chart", lambda *args, **kwargs: None)


def configured_app(tmp_path, monkeypatch, version="v1", debug=True):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ui.db"))
    monkeypatch.setenv("ENABLE_DEBUG_MODE", str(debug).lower())
    monkeypatch.setenv("APP_VERSION", version)
    return AppTest.from_file(APP_PATH, default_timeout=15)


def test_app_renders_dashboard_and_loads_frozen_fixture(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch)
    app.run()

    assert not app.exception
    assert app.title[0].value == "Writing Assistant"
    app.button(key="load_Normal case").click().run()

    assert not app.exception
    assert "School uniforms" in app.text_area(key="writing_input").value
    assert app.text_input(key="assignment_context_input").value == "Persuasive Essay"
    assert all(item.key != "affect_check_in" for item in app.selectbox)


def test_developer_controls_can_hide_and_show(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch)
    app.run()

    assert not app.exception
    assert app.selectbox(key="grade_level").label == "Grade level"
    assert any(
        item.value == "developer controls (for testing and debugging)"
        for item in app.header
    )

    app.button(key="hide_developer_controls").click().run()

    assert not app.exception
    assert app.session_state.developer_controls_visible is False
    assert app.button(key="show_developer_controls").label == "Show Developer Controls"
    assert all(item.key != "load_Normal case" for item in app.button)

    app.button(key="show_developer_controls").click().run()

    assert not app.exception
    assert app.session_state.developer_controls_visible is True
    assert any(item.key == "hide_developer_controls" for item in app.button)
    assert any(item.key == "load_Normal case" for item in app.button)


def test_agent_observability_can_hide_and_show(tmp_path, monkeypatch):
    app = configured_app(tmp_path, monkeypatch)
    app.run()

    assert not app.exception
    assert any(item.value == "Agent observability" for item in app.subheader)

    app.button(key="hide_agent_observability").click().run()

    assert not app.exception
    assert app.session_state.agent_observability_visible is False
    assert (
        app.button(key="show_agent_observability").label
        == "Show Agent Observability"
    )
    assert all(item.value != "Agent observability" for item in app.subheader)

    app.button(key="show_agent_observability").click().run()

    assert not app.exception
    assert app.session_state.agent_observability_visible is True
    assert any(item.key == "hide_agent_observability" for item in app.button)
    assert any(item.value == "Agent observability" for item in app.subheader)


def test_app_normal_flow_displays_feedback_and_practice(tmp_path, monkeypatch):
    responses = iter([coordinator_payload(), support_payload()])
    monkeypatch.setattr(
        DeepSeekClient,
        "chat_completion",
        lambda self, messages, **kwargs: next(responses),
    )
    app = configured_app(tmp_path, monkeypatch)
    app.run()
    app.button(key="load_Normal case").click().run()
    app.button(key="analyze_writing").click().run()

    assert not app.exception
    assert any("Feedback and next steps" in item.value for item in app.success)
    assert any("What is working well" in item.value for item in app.markdown)
    assert not app.error


def test_app_clarification_answer_resumes_to_feedback(tmp_path, monkeypatch):
    responses = iter(
        [
            coordinator_payload("ask_clarification"),
            coordinator_payload(),
            support_payload(),
        ]
    )
    monkeypatch.setattr(
        DeepSeekClient,
        "chat_completion",
        lambda self, messages, **kwargs: next(responses),
    )
    app = configured_app(tmp_path, monkeypatch)
    app.run()
    app.button(key="load_Incomplete case").click().run()
    app.button(key="analyze_writing").click().run()

    assert not app.exception
    assert any(
        "Do you want outline help or draft feedback?" in item.value
        for item in app.info
    )

    app.text_area(key="clarification_answer").set_value(
        "I want help turning the outline into a draft."
    )
    app.button(key="resume_clarification").click().run()

    assert not app.exception
    assert any("Feedback and next steps" in item.value for item in app.success)
    assert not app.error


def test_app_restores_latest_saved_run_for_session_url(tmp_path, monkeypatch):
    import uuid

    from langgraph_core.state import make_initial_state
    from storage.sqlite_storage import SQLiteStorage

    session_id = uuid.uuid4().hex
    thread_id = uuid.uuid4().hex
    storage = SQLiteStorage(str(tmp_path / "ui.db"))
    initial = make_initial_state("Synthetic saved draft", "6th Grade")
    storage.create_run(session_id, thread_id, initial)
    storage.save_result(
        thread_id,
        {
            **initial,
            "routing_decision": "direct_response",
            "student_output": "Restored synthetic result",
            "agent_path": ["Assessment Coordinator", "Direct Response"],
        },
        False,
        1,
    )
    app = configured_app(tmp_path, monkeypatch)
    app.query_params["session_id"] = session_id
    app.run()

    assert not app.exception
    assert any("Restored synthetic result" in item.value for item in app.markdown)


def test_v2_app_lets_learner_choose_focus_and_optional_practice_without_new_calls(
    tmp_path, monkeypatch
):
    responses = iter([coordinator_payload_v2(), support_payload_v2()])
    calls = []

    def fake_completion(self, messages, **kwargs):
        calls.append(messages)
        return next(responses)

    monkeypatch.setattr(DeepSeekClient, "chat_completion", fake_completion)
    app = configured_app(tmp_path, monkeypatch, version="v2")
    app.run()
    app.button(key="load_Normal case").click().run()
    app.selectbox(key="affect_check_in").set_value("unsure")
    app.button(key="analyze_writing").click().run()

    assert not app.exception
    assert any("Feedback and your revision choice" in item.value for item in app.success)
    invocation = app.session_state.current_invocation
    assert invocation.state["affect_check_in"] == "unsure"
    focus = next(item for item in app.radio if item.key.startswith("revision_focus_"))
    focus.set_value(0).run()

    assert not app.exception
    assert any(
        "Name two specific ways uniforms help." in item.value for item in app.markdown
    )
    practice = next(item for item in app.radio if item.key.startswith("practice_choice_"))
    practice.set_value("practice").run()

    assert not app.exception
    assert any("Our library should open earlier" in item.value for item in app.markdown)
    assert len(calls) == 2


def test_v2_standard_support_without_practice_uses_standard_message(tmp_path, monkeypatch):
    responses = iter(
        [
            coordinator_payload_v2(needs_practice=False),
            support_payload_v2(include_practice=False),
        ]
    )
    monkeypatch.setattr(
        DeepSeekClient,
        "chat_completion",
        lambda self, messages, **kwargs: next(responses),
    )
    app = configured_app(tmp_path, monkeypatch, version="v2")
    app.run()
    app.button(key="load_Normal case").click().run()
    app.button(key="analyze_writing").click().run()
    focus = next(item for item in app.radio if item.key.startswith("revision_focus_"))
    focus.set_value(0).run()

    assert not app.exception
    assert any(
        "No practice exercise is included for this focus." in item.value
        for item in app.info
    )
    assert all("light-touch response" not in item.value for item in app.info)


def test_malformed_session_url_warns_once_and_starts_a_new_session(tmp_path, monkeypatch):
    import uuid

    app = configured_app(tmp_path, monkeypatch)
    app.query_params["session_id"] = "not-a-uuid"
    app.run()

    assert not app.exception
    assert any("session ID in the URL was not recognized" in item.value for item in app.warning)
    replacement = app.query_params["session_id"]
    assert uuid.UUID(replacement).hex == replacement

    app.run()
    assert all(
        "session ID in the URL was not recognized" not in item.value
        for item in app.warning
    )


def test_validation_errors_hide_schema_details_from_current_and_saved_runs(
    tmp_path, monkeypatch
):
    invalid = support_payload_v2(revision_need="light_touch")
    responses = iter([coordinator_payload_v2(), invalid, invalid])
    monkeypatch.setattr(
        DeepSeekClient,
        "chat_completion",
        lambda self, messages, **kwargs: next(responses),
    )
    app = configured_app(tmp_path, monkeypatch, version="v2", debug=False)
    app.run()
    app.button(key="load_Normal case").click().run()
    app.button(key="analyze_writing").click().run()

    assert not app.exception
    assert any(
        "The feedback could not be completed. Please try the analysis again."
        == item.value
        for item in app.error
    )
    assert all("Standard support must contain" not in item.value for item in app.error)
    assert all("Standard support must contain" not in item.value for item in app.caption)

    session_id = app.query_params["session_id"]
    restored = configured_app(tmp_path, monkeypatch, version="v2", debug=False)
    restored.query_params["session_id"] = session_id
    restored.run()

    assert not restored.exception
    assert any(
        "This saved analysis could not be completed. Please try the analysis again."
        == item.value
        for item in restored.error
    )
    assert all(
        "Standard support must contain" not in item.value for item in restored.error
    )
    assert all(
        "Standard support must contain" not in item.value for item in restored.caption
    )

    debug_view = configured_app(tmp_path, monkeypatch, version="v2", debug=True)
    debug_view.query_params["session_id"] = session_id
    debug_view.run()

    assert not debug_view.exception
    assert any(
        "Debug: Standard support must contain" in item.value
        for item in debug_view.caption
    )


def test_raw_prompt_controls_and_log_views_require_debug_mode(tmp_path, monkeypatch):
    import json

    responses = iter([coordinator_payload("direct_response")])
    monkeypatch.setattr(
        DeepSeekClient,
        "chat_completion",
        lambda self, messages, **kwargs: next(responses),
    )
    app = configured_app(tmp_path, monkeypatch, debug=True)
    app.run()
    app.checkbox(key="capture_debug").set_value(True)
    app.checkbox(key="show_logs").set_value(True)
    app.button(key="load_Normal case").click().run()
    app.button(key="analyze_writing").click().run()

    assert not app.exception
    assert "prompt" in app.session_state.current_invocation.state["execution_logs"][0]
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" not in serialized
    assert '"prompt"' not in serialized

    app.checkbox(key="show_prompts").set_value(True).run()
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" in serialized

    monkeypatch.setenv("ENABLE_DEBUG_MODE", "false")
    app.run()

    assert not app.exception
    checkbox_keys = {item.key for item in app.checkbox}
    assert "show_prompts" not in checkbox_keys
    assert "capture_debug" not in checkbox_keys
    assert app.session_state.capture_debug is False
    serialized = json.dumps([item.value for item in app.json])
    assert "raw_response" not in serialized
    assert '"prompt"' not in serialized
