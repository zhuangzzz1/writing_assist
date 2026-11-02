import uuid

from langgraph_core.state import make_initial_state
from storage.sqlite_storage import SQLiteStorage


def test_history_is_filtered_by_session_and_accumulates_duration(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    first_thread = uuid.uuid4().hex
    second_thread = uuid.uuid4().hex
    state = make_initial_state("Synthetic writing", "5th Grade")

    storage.create_run("session-a", first_thread, state)
    storage.create_run("session-b", second_thread, state)
    storage.save_result(first_thread, {"routing_decision": "direct_response"}, False, 25)
    storage.save_result(first_thread, {"routing_decision": "direct_response"}, False, 35)

    first = storage.get_run(first_thread)
    assert first.duration_ms == 60
    assert first.status == "completed"
    assert [run.thread_id for run in storage.list_runs("session-a")] == [first_thread]
    assert [run.thread_id for run in storage.list_runs("session-b")] == [second_thread]


def test_error_and_manual_deletion_are_persistent(tmp_path):
    database = str(tmp_path / "history.db")
    storage = SQLiteStorage(database)
    thread_id = uuid.uuid4().hex
    state = make_initial_state("Synthetic writing", "7th Grade")
    storage.create_run("session-a", thread_id, state)

    storage.record_error(thread_id, "Temporary failure", 10)
    assert storage.get_run(thread_id).status == "failed"
    assert storage.get_run(thread_id).error == "Temporary failure"

    reopened = SQLiteStorage(database)
    assert reopened.delete_session("session-a") == [thread_id]
    assert reopened.get_run(thread_id) is None


def test_delete_session_with_no_runs_returns_empty_list(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))

    assert storage.delete_session("missing-session") == []
