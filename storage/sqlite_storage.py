import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agents.utils import InputValidationError
from langgraph_core.state import WritingAssistantState
from storage.interface import (
    CompositionRecord,
    CompositionStorage,
    ReflectionRecord,
    RoundRecord,
    SnapshotRecord,
)


class SQLiteStorage(CompositionStorage):
    def __init__(self, database_path: str):
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS compositions (
                    composition_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    grade_level TEXT NOT NULL,
                    genre_selection TEXT NOT NULL,
                    assignment_prompt TEXT NOT NULL,
                    teacher_directions TEXT NOT NULL,
                    framework_name TEXT NOT NULL DEFAULT '',
                    framework_components_json TEXT NOT NULL DEFAULT '[]',
                    source_material TEXT NOT NULL,
                    source_material_available INTEGER NOT NULL,
                    student_concerns TEXT NOT NULL,
                    scenario_id TEXT NOT NULL,
                    fixture_version TEXT NOT NULL,
                    revision_number INTEGER NOT NULL DEFAULT 0,
                    active_round_id TEXT,
                    active_thread_id TEXT,
                    final_thread_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS compositions_session_updated
                    ON compositions(session_id, updated_at DESC);

                CREATE TABLE IF NOT EXISTS snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    composition_id TEXT NOT NULL REFERENCES compositions(composition_id)
                        ON DELETE CASCADE,
                    revision_number INTEGER NOT NULL,
                    writing TEXT NOT NULL,
                    selected_goals_json TEXT NOT NULL DEFAULT '[]',
                    goal_self_reports_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    UNIQUE(composition_id, revision_number)
                );
                CREATE TRIGGER IF NOT EXISTS snapshots_are_immutable
                BEFORE UPDATE ON snapshots
                BEGIN
                    SELECT RAISE(ABORT, 'Submitted snapshots are immutable.');
                END;

                CREATE TABLE IF NOT EXISTS rounds (
                    round_id TEXT PRIMARY KEY,
                    composition_id TEXT NOT NULL REFERENCES compositions(composition_id)
                        ON DELETE CASCADE,
                    revision_number INTEGER NOT NULL,
                    thread_id TEXT NOT NULL UNIQUE,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    input_state_json TEXT NOT NULL,
                    state_json TEXT NOT NULL DEFAULT '{}',
                    routing_decision TEXT,
                    duration_ms INTEGER NOT NULL DEFAULT 0,
                    error TEXT,
                    started_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS rounds_composition
                    ON rounds(composition_id, revision_number);

                CREATE TABLE IF NOT EXISTS reflections (
                    composition_id TEXT PRIMARY KEY REFERENCES compositions(composition_id)
                        ON DELETE CASCADE,
                    original_snapshot_id TEXT NOT NULL,
                    final_snapshot_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    input_state_json TEXT NOT NULL,
                    state_json TEXT NOT NULL DEFAULT '{}',
                    duration_ms INTEGER NOT NULL DEFAULT 0,
                    error TEXT,
                    created_at TEXT NOT NULL
                );
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(compositions)")
            }
            for name, definition in (
                ("framework_name", "TEXT NOT NULL DEFAULT ''"),
                ("framework_components_json", "TEXT NOT NULL DEFAULT '[]'"),
            ):
                if name not in columns:
                    connection.execute(
                        f"ALTER TABLE compositions ADD COLUMN {name} {definition}"
                    )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    def create_composition(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
    ) -> None:
        if state["revision_number"] != 0 or state["review_mode"] != "round":
            raise ValueError("A new composition must start with round review zero.")
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO compositions (
                    composition_id, session_id, status, grade_level, genre_selection,
                    assignment_prompt, teacher_directions, framework_name,
                    framework_components_json, source_material, source_material_available,
                    student_concerns, scenario_id, fixture_version, revision_number,
                    active_round_id, active_thread_id, created_at, updated_at
                ) VALUES (?, ?, 'running', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?)
                """,
                (
                    state["composition_id"],
                    session_id,
                    state["grade_level"],
                    state["genre_selection"],
                    state["assignment_prompt"],
                    state["teacher_directions"],
                    state["framework_name"],
                    self._json(state["framework_components"]),
                    state["source_material"],
                    state["source_material_available"],
                    state["student_concerns"],
                    state["scenario_id"],
                    state["fixture_version"],
                    state["round_id"],
                    state["thread_id"],
                    now,
                    now,
                ),
            )
            connection.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, composition_id, revision_number, writing,
                    selected_goals_json, goal_self_reports_json, created_at
                ) VALUES (?, ?, 0, ?, '[]', '{}', ?)
                """,
                (snapshot_id, state["composition_id"], state["writing"], now),
            )
            self._insert_round(connection, state, "initial", now)

    def create_revision(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
    ) -> None:
        now = self._now()
        with self._connect() as connection:
            composition = connection.execute(
                "SELECT revision_number, status FROM compositions "
                "WHERE composition_id = ? AND session_id = ?",
                (state["composition_id"], session_id),
            ).fetchone()
            if composition is None:
                raise InputValidationError("Saved history is unavailable for this composition.")
            final_exists = connection.execute(
                "SELECT 1 FROM reflections WHERE composition_id = ?",
                (state["composition_id"],),
            ).fetchone()
            if final_exists:
                raise InputValidationError(
                    "Final reflection has already started. Retry it or start a new composition."
                )
            if composition["revision_number"] + 1 != state["revision_number"]:
                raise InputValidationError(
                    "This revision was already submitted or the draft history changed. "
                    "Reload the composition before trying again."
                )
            connection.execute(
                """
                INSERT INTO snapshots (
                    snapshot_id, composition_id, revision_number, writing,
                    selected_goals_json, goal_self_reports_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot_id,
                    state["composition_id"],
                    state["revision_number"],
                    state["writing"],
                    self._json(state["selected_goals"]),
                    self._json(state["goal_self_reports"]),
                    now,
                ),
            )
            self._insert_round(connection, state, "revision", now)
            connection.execute(
                """
                UPDATE compositions
                SET status = 'running', revision_number = ?, active_round_id = ?,
                    active_thread_id = ?, updated_at = ?
                WHERE composition_id = ?
                """,
                (
                    state["revision_number"],
                    state["round_id"],
                    state["thread_id"],
                    now,
                    state["composition_id"],
                ),
            )

    def create_reassessment(
        self, session_id: str, state: WritingAssistantState
    ) -> None:
        now = self._now()
        with self._connect() as connection:
            composition = connection.execute(
                "SELECT revision_number FROM compositions "
                "WHERE composition_id = ? AND session_id = ?",
                (state["composition_id"], session_id),
            ).fetchone()
            if composition is None:
                raise InputValidationError("Saved history is unavailable for this composition.")
            final_exists = connection.execute(
                "SELECT 1 FROM reflections WHERE composition_id = ?",
                (state["composition_id"],),
            ).fetchone()
            if final_exists:
                raise InputValidationError(
                    "Final reflection has already started. Retry it or start a new composition."
                )
            if composition["revision_number"] != state["revision_number"]:
                raise InputValidationError("The draft changed before genre correction.")
            self._insert_round(connection, state, "genre_correction", now)
            connection.execute(
                """
                UPDATE compositions
                SET status = 'running', genre_selection = ?, active_round_id = ?,
                    active_thread_id = ?, updated_at = ?
                WHERE composition_id = ?
                """,
                (
                    state["genre_selection"],
                    state["round_id"],
                    state["thread_id"],
                    now,
                    state["composition_id"],
                ),
            )

    @staticmethod
    def _insert_round(
        connection: sqlite3.Connection,
        state: WritingAssistantState,
        kind: str,
        now: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO rounds (
                round_id, composition_id, revision_number, thread_id, kind,
                status, stage, input_state_json, started_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'running', 'draft_saved', ?, ?, ?)
            """,
            (
                state["round_id"],
                state["composition_id"],
                state["revision_number"],
                state["thread_id"],
                kind,
                json.dumps(state, ensure_ascii=False),
                now,
                now,
            ),
        )

    def create_final(
        self,
        session_id: str,
        state: WritingAssistantState,
        original_snapshot_id: str,
        final_snapshot_id: str,
    ) -> None:
        if state["review_mode"] != "final":
            raise ValueError("Final reflection requires final review mode.")
        now = self._now()
        with self._connect() as connection:
            composition = connection.execute(
                "SELECT revision_number FROM compositions "
                "WHERE composition_id = ? AND session_id = ?",
                (state["composition_id"], session_id),
            ).fetchone()
            if composition is None:
                raise InputValidationError("Saved history is unavailable for this composition.")
            existing = connection.execute(
                "SELECT status FROM reflections WHERE composition_id = ?",
                (state["composition_id"],),
            ).fetchone()
            if existing:
                raise InputValidationError(
                    "Final reflection already exists. Use the explicit retry action if it failed."
                )
            snapshots = connection.execute(
                "SELECT snapshot_id, revision_number, writing FROM snapshots "
                "WHERE composition_id = ? ORDER BY revision_number",
                (state["composition_id"],),
            ).fetchall()
            if (
                not snapshots
                or original_snapshot_id != snapshots[0]["snapshot_id"]
                or final_snapshot_id != snapshots[-1]["snapshot_id"]
            ):
                raise InputValidationError(
                    "Final reflection must use the original and latest snapshots from "
                    "this composition."
                )
            original = snapshots[0]
            final = snapshots[-1]
            if (
                composition["revision_number"] != state["revision_number"]
                or final["revision_number"] != state["revision_number"]
                or state["original_writing"] != original["writing"]
                or state["writing"] != final["writing"]
            ):
                raise InputValidationError(
                    "Final reflection input must match the saved original and latest drafts."
                )
            connection.execute(
                """
                INSERT INTO reflections (
                    composition_id, original_snapshot_id, final_snapshot_id,
                    thread_id, status, stage, input_state_json, created_at
                ) VALUES (?, ?, ?, ?, 'running', 'draft_saved', ?, ?)
                """,
                (
                    state["composition_id"],
                    original_snapshot_id,
                    final_snapshot_id,
                    state["thread_id"],
                    self._json(state),
                    now,
                ),
            )
            connection.execute(
                """
                UPDATE compositions
                SET status = 'final_running', final_thread_id = ?, updated_at = ?
                WHERE composition_id = ?
                """,
                (state["thread_id"], now, state["composition_id"]),
            )

    def mark_running(self, thread_id: str) -> None:
        now = self._now()
        with self._connect() as connection:
            round_row = connection.execute(
                "SELECT composition_id FROM rounds WHERE thread_id = ?", (thread_id,)
            ).fetchone()
            if round_row:
                connection.execute(
                    "UPDATE rounds SET status = 'running', stage = 'reviewing', "
                    "error = NULL, updated_at = ? WHERE thread_id = ?",
                    (now, thread_id),
                )
                connection.execute(
                    "UPDATE compositions SET status = 'running', updated_at = ? "
                    "WHERE composition_id = ?",
                    (now, round_row["composition_id"]),
                )
                return
            reflection = connection.execute(
                "SELECT composition_id FROM reflections WHERE thread_id = ?", (thread_id,)
            ).fetchone()
            if reflection:
                connection.execute(
                    "UPDATE reflections SET status = 'running', stage = 'reviewing', "
                    "error = NULL WHERE thread_id = ?",
                    (thread_id,),
                )
                connection.execute(
                    "UPDATE compositions SET status = 'final_running', updated_at = ? "
                    "WHERE composition_id = ?",
                    (now, reflection["composition_id"]),
                )

    def mark_stage(self, thread_id: str, stage: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE rounds SET stage = ?, updated_at = ? WHERE thread_id = ?",
                (stage, self._now(), thread_id),
            )
            connection.execute(
                "UPDATE reflections SET stage = ? WHERE thread_id = ?",
                (stage, thread_id),
            )

    def save_round_result(
        self,
        thread_id: str,
        state: dict[str, Any],
        pending: bool,
        duration_ms: int,
    ) -> None:
        route = state.get("routing_decision")
        if pending:
            status = "awaiting_clarification"
        elif route == "teacher_review":
            status = "teacher_review"
        else:
            status = "active"
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE rounds
                SET status = ?, stage = ?, routing_decision = ?, state_json = ?,
                    duration_ms = duration_ms + ?, error = NULL, updated_at = ?
                WHERE thread_id = ?
                """,
                (
                    "awaiting_clarification" if pending else "completed",
                    "awaiting_clarification" if pending else "complete",
                    route,
                    self._json(state),
                    duration_ms,
                    now,
                    thread_id,
                ),
            )
            connection.execute(
                """
                UPDATE compositions SET status = ?, updated_at = ?
                WHERE composition_id = (
                    SELECT composition_id FROM rounds WHERE thread_id = ?
                )
                """,
                (status, now, thread_id),
            )

    def save_final_result(
        self, thread_id: str, state: dict[str, Any], duration_ms: int
    ) -> None:
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE reflections
                SET status = 'completed', stage = 'complete', state_json = ?,
                    duration_ms = duration_ms + ?, error = NULL
                WHERE thread_id = ?
                """,
                (self._json(state), duration_ms, thread_id),
            )
            connection.execute(
                """
                UPDATE compositions SET status = 'completed', updated_at = ?
                WHERE composition_id = (
                    SELECT composition_id FROM reflections WHERE thread_id = ?
                )
                """,
                (now, thread_id),
            )

    def record_error(self, thread_id: str, error: str, duration_ms: int) -> None:
        now = self._now()
        with self._connect() as connection:
            round_row = connection.execute(
                "SELECT composition_id FROM rounds WHERE thread_id = ?", (thread_id,)
            ).fetchone()
            if round_row:
                connection.execute(
                    """
                    UPDATE rounds SET status = 'failed', stage = 'failed', error = ?,
                        duration_ms = duration_ms + ?, updated_at = ?
                    WHERE thread_id = ?
                    """,
                    (error, duration_ms, now, thread_id),
                )
                connection.execute(
                    "UPDATE compositions SET status = 'failed', updated_at = ? "
                    "WHERE composition_id = ?",
                    (now, round_row["composition_id"]),
                )
                return
            reflection = connection.execute(
                "SELECT composition_id FROM reflections WHERE thread_id = ?", (thread_id,)
            ).fetchone()
            if reflection:
                connection.execute(
                    """
                    UPDATE reflections SET status = 'failed', stage = 'failed', error = ?,
                        duration_ms = duration_ms + ?
                    WHERE thread_id = ?
                    """,
                    (error, duration_ms, thread_id),
                )
                connection.execute(
                    "UPDATE compositions SET status = 'final_failed', updated_at = ? "
                    "WHERE composition_id = ?",
                    (now, reflection["composition_id"]),
                )

    @staticmethod
    def _composition(row: sqlite3.Row) -> CompositionRecord:
        return CompositionRecord(
            composition_id=row["composition_id"],
            session_id=row["session_id"],
            status=row["status"],
            grade_level=row["grade_level"],
            genre_selection=row["genre_selection"],
            assignment_prompt=row["assignment_prompt"],
            teacher_directions=row["teacher_directions"],
            framework_name=row["framework_name"],
            framework_components=json.loads(row["framework_components_json"]),
            source_material=row["source_material"],
            source_material_available=bool(row["source_material_available"]),
            student_concerns=row["student_concerns"],
            scenario_id=row["scenario_id"],
            fixture_version=row["fixture_version"],
            revision_number=row["revision_number"],
            active_round_id=row["active_round_id"],
            active_thread_id=row["active_thread_id"],
            final_thread_id=row["final_thread_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def get_composition(self, composition_id: str) -> CompositionRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM compositions WHERE composition_id = ?",
                (composition_id,),
            ).fetchone()
        return self._composition(row) if row else None

    def list_compositions(
        self, session_id: str, limit: int = 100
    ) -> list[CompositionRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM compositions WHERE session_id = ? "
                "ORDER BY updated_at DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [self._composition(row) for row in rows]

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> SnapshotRecord:
        return SnapshotRecord(
            snapshot_id=row["snapshot_id"],
            composition_id=row["composition_id"],
            revision_number=row["revision_number"],
            writing=row["writing"],
            selected_goals=json.loads(row["selected_goals_json"]),
            goal_self_reports=json.loads(row["goal_self_reports_json"]),
            created_at=row["created_at"],
        )

    def get_snapshot(
        self, composition_id: str, revision_number: int
    ) -> SnapshotRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM snapshots WHERE composition_id = ? AND revision_number = ?",
                (composition_id, revision_number),
            ).fetchone()
        return self._snapshot(row) if row else None

    def list_snapshots(self, composition_id: str) -> list[SnapshotRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM snapshots WHERE composition_id = ? "
                "ORDER BY revision_number",
                (composition_id,),
            ).fetchall()
        return [self._snapshot(row) for row in rows]

    @staticmethod
    def _round(row: sqlite3.Row) -> RoundRecord:
        return RoundRecord(
            round_id=row["round_id"],
            composition_id=row["composition_id"],
            revision_number=row["revision_number"],
            thread_id=row["thread_id"],
            kind=row["kind"],
            status=row["status"],
            stage=row["stage"],
            input_state=json.loads(row["input_state_json"]),
            state=json.loads(row["state_json"]),
            routing_decision=row["routing_decision"],
            duration_ms=row["duration_ms"],
            error=row["error"],
            started_at=row["started_at"],
            updated_at=row["updated_at"],
        )

    def get_round(self, round_id: str) -> RoundRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM rounds WHERE round_id = ?", (round_id,)
            ).fetchone()
        return self._round(row) if row else None

    def get_round_by_thread(self, thread_id: str) -> RoundRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM rounds WHERE thread_id = ?", (thread_id,)
            ).fetchone()
        return self._round(row) if row else None

    def get_latest_round(self, composition_id: str) -> RoundRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM rounds WHERE composition_id = ? ORDER BY rowid DESC LIMIT 1",
                (composition_id,),
            ).fetchone()
        return self._round(row) if row else None

    def list_rounds(self, composition_id: str) -> list[RoundRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM rounds WHERE composition_id = ? ORDER BY rowid",
                (composition_id,),
            ).fetchall()
        return [self._round(row) for row in rows]

    @staticmethod
    def _reflection(row: sqlite3.Row) -> ReflectionRecord:
        return ReflectionRecord(
            composition_id=row["composition_id"],
            original_snapshot_id=row["original_snapshot_id"],
            final_snapshot_id=row["final_snapshot_id"],
            thread_id=row["thread_id"],
            status=row["status"],
            stage=row["stage"],
            input_state=json.loads(row["input_state_json"]),
            state=json.loads(row["state_json"]),
            duration_ms=row["duration_ms"],
            error=row["error"],
            created_at=row["created_at"],
        )

    def get_reflection(self, composition_id: str) -> ReflectionRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM reflections WHERE composition_id = ?", (composition_id,)
            ).fetchone()
        return self._reflection(row) if row else None

    def delete_session(self, session_id: str) -> list[str]:
        with self._connect() as connection:
            composition_ids = [
                row["composition_id"]
                for row in connection.execute(
                    "SELECT composition_id FROM compositions WHERE session_id = ?",
                    (session_id,),
                ).fetchall()
            ]
            if not composition_ids:
                return []
            placeholders = ",".join("?" for _ in composition_ids)
            round_threads = connection.execute(
                f"SELECT thread_id FROM rounds WHERE composition_id IN ({placeholders})",
                composition_ids,
            ).fetchall()
            final_threads = connection.execute(
                f"SELECT thread_id FROM reflections WHERE composition_id IN ({placeholders})",
                composition_ids,
            ).fetchall()
            connection.execute(
                "DELETE FROM compositions WHERE session_id = ?", (session_id,)
            )
        return list(
            dict.fromkeys(
                [row["thread_id"] for row in round_threads]
                + [row["thread_id"] for row in final_threads]
            )
        )
