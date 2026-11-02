from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from agents.utils import DeepSeekClient
from tests.helpers import coordinator_payload, support_payload


APP_PATH = str(Path(__file__).resolve().parents[1] / "app.py")


@pytest.fixture(autouse=True)
def stub_graphviz_frontend(monkeypatch):
    monkeypatch.setattr("ui.observability.st.graphviz_chart", lambda *args, **kwargs: None)


def configured_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "ui.db"))
    monkeypatch.setenv("ENABLE_DEBUG_MODE", "true")
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
