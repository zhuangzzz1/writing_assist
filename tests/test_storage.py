import json
import sqlite3
import uuid

import pytest

from agents.utils import InputValidationError
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from storage.sqlite_storage import SQLiteStorage
from tests.helpers import INITIAL_DRAFT, candidate_for, issue_for


def state_for(compaction="comp", revision=0, writing=INITIAL_DRAFT, previous=""):
    return make_review_state(
        writing,
        "6th Grade",
        composition_id=compaction,
        round_id=f"round-{revision}-{uuid.uuid4().hex}",
        thread_id=f"thread-{revision}-{uuid.uuid4().hex}",
        original_writing=INITIAL_DRAFT,
        previous_writing=previous,
        revision_number=revision,
        selected_goals=(
            [candidate_for(issue_for(INITIAL_DRAFT))] if revision else []
        ),
        text_diff=build_text_diff(previous, writing) if previous else {},
        scenario_id="manual-test",
        fixture_version="v3.1.0",
    )


def test_history_is_filtered_by_session_and_restored_after_reopen(tmp_path):
    database = str(tmp_path / "history.db")
    storage = SQLiteStorage(database)
    first = state_for("composition-a")
    second = state_for("composition-b")

    storage.create_composition("session-a", first, "snapshot-a")
    storage.create_composition("session-b", second, "snapshot-b")
    storage.save_round_result(
        first["thread_id"], {**first, "routing_decision": "direct_response"}, False, 25
    )

    reopened = SQLiteStorage(database)
    assert [item.composition_id for item in reopened.list_compositions("session-a")] == [
        "composition-a"
    ]
    assert [item.composition_id for item in reopened.list_compositions("session-b")] == [
        "composition-b"
    ]
    assert reopened.get_snapshot("composition-a", 0).writing == INITIAL_DRAFT
    assert reopened.get_latest_round("composition-a").duration_ms == 25


def test_original_and_successive_revision_snapshots_are_immutable(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    revised = INITIAL_DRAFT + "\n\nA new explanation."
    revision = state_for(revision=1, writing=revised, previous=INITIAL_DRAFT)

    storage.create_revision("session", revision, "snapshot-1")

    snapshots = storage.list_snapshots("comp")
    assert [item.writing for item in snapshots] == [INITIAL_DRAFT, revised]
    assert snapshots[1].selected_goals[0]["goal_id"] == "goal_1"
    with sqlite3.connect(storage.database_path) as connection:
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            connection.execute(
                "UPDATE snapshots SET writing = 'overwritten' WHERE snapshot_id = 'snapshot-0'"
            )


def test_revision_order_is_checked_before_snapshot_creation(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    wrong_order = state_for(revision=2, previous=INITIAL_DRAFT)

    with pytest.raises(InputValidationError, match="history changed"):
        storage.create_revision("session", wrong_order, "snapshot-2")
    assert len(storage.list_snapshots("comp")) == 1


def test_duplicate_snapshot_id_is_rejected_before_a_review(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    revision = state_for(revision=1, previous=INITIAL_DRAFT)

    with pytest.raises(sqlite3.IntegrityError):
        storage.create_revision("session", revision, "snapshot-0")
    assert storage.get_composition("comp").revision_number == 0


def test_final_reflection_and_process_state_survive_reopen(tmp_path):
    database = str(tmp_path / "history.db")
    storage = SQLiteStorage(database)
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for()
    final["review_mode"] = "final"
    final["thread_id"] = "final-thread"

    storage.create_final("session", final, "snapshot-0", "snapshot-0")
    storage.save_final_result(
        "final-thread", {**final, "final_reflection": {"improvements": []}}, 40
    )

    reopened = SQLiteStorage(database)
    reflection = reopened.get_reflection("comp")
    assert reflection.status == "completed"
    assert reflection.duration_ms == 40
    assert reflection.state["final_reflection"]["improvements"] == []


def test_existing_final_cannot_be_restarted_without_explicit_retry(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for()
    final["review_mode"] = "final"
    storage.create_final("session", final, "snapshot-0", "snapshot-0")

    with pytest.raises(InputValidationError, match="explicit retry"):
        storage.create_final("session", final, "snapshot-0", "snapshot-0")


def test_session_deletion_cascades_all_composition_data(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for()
    final["review_mode"] = "final"
    final["thread_id"] = "final-thread"
    storage.create_final("session", final, "snapshot-0", "snapshot-0")

    threads = storage.delete_session("session")

    assert set(threads) == {initial["thread_id"], "final-thread"}
    assert storage.list_compositions("session") == []
    assert storage.list_snapshots("comp") == []
    assert storage.get_reflection("comp") is None
    with sqlite3.connect(storage.database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM rounds").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM reflections").fetchone()[0] == 0


def test_delete_missing_session_is_safe(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))

    assert storage.delete_session("missing") == []


def test_corrupt_saved_json_raises_a_catchable_error(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    with sqlite3.connect(storage.database_path) as connection:
        connection.execute(
            "UPDATE rounds SET state_json = 'not-json' WHERE round_id = ?",
            (initial["round_id"],),
        )

    with pytest.raises(json.JSONDecodeError):
        storage.get_latest_round("comp")


def test_final_reflection_requires_original_and_latest_snapshot_ids(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for()
    final["review_mode"] = "final"

    with pytest.raises(InputValidationError, match="original and latest snapshots"):
        storage.create_final("session", final, "another-snapshot", "snapshot-0")

    assert storage.get_reflection("comp") is None


def test_final_reflection_rejects_unsubmitted_editor_text(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for(writing=INITIAL_DRAFT + "\n\nUnsubmitted text.")
    final["review_mode"] = "final"

    with pytest.raises(InputValidationError, match="must match"):
        storage.create_final("session", final, "snapshot-0", "snapshot-0")

    assert storage.get_reflection("comp") is None


def test_revision_cannot_move_past_an_existing_final_reflection(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    final = state_for()
    final["review_mode"] = "final"
    storage.create_final("session", final, "snapshot-0", "snapshot-0")
    revision = state_for(revision=1, previous=INITIAL_DRAFT)

    with pytest.raises(InputValidationError, match="already started"):
        storage.create_revision("session", revision, "snapshot-1")
    with pytest.raises(InputValidationError, match="already started"):
        storage.create_reassessment("session", state_for())

    assert len(storage.list_snapshots("comp")) == 1
    assert storage.get_composition("comp").genre_selection == "auto"


def test_framework_contract_survives_reopen(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    initial["framework_name"] = "CER"
    initial["framework_components"] = ["Claim", "Evidence", "Reasoning"]

    storage.create_composition("session", initial, "snapshot-0")
    reopened = SQLiteStorage(storage.database_path)
    composition = reopened.get_composition("comp")

    assert composition.framework_name == "CER"
    assert composition.framework_components == ["Claim", "Evidence", "Reasoning"]


def test_existing_composition_database_receives_additive_framework_columns(tmp_path):
    storage = SQLiteStorage(str(tmp_path / "history.db"))
    initial = state_for()
    storage.create_composition("session", initial, "snapshot-0")
    with sqlite3.connect(storage.database_path) as connection:
        connection.execute("ALTER TABLE compositions DROP COLUMN framework_name")
        connection.execute("ALTER TABLE compositions DROP COLUMN framework_components_json")

    reopened = SQLiteStorage(storage.database_path)
    composition = reopened.get_composition("comp")

    assert composition.framework_name == ""
    assert composition.framework_components == []
    assert reopened.list_snapshots("comp")[0].writing == INITIAL_DRAFT
