import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from langgraph_core.state import WritingAssistantState
from storage.interface import RunRecord, RunStorage


class SQLiteStorage(RunStorage):
    def __init__(self, database_path: str):
        self.database_path = database_path
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    thread_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    writing TEXT NOT NULL,
                    grade_level TEXT NOT NULL,
                    assignment_context TEXT NOT NULL,
                    student_concerns TEXT NOT NULL,
                    app_version TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    routing_decision TEXT,
                    state_json TEXT NOT NULL DEFAULT '{}',
                    duration_ms INTEGER NOT NULL DEFAULT 0,
                    error TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS runs_session_updated "
                "ON runs(session_id, updated_at DESC)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=30000")
        return connection

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_run(
        self, session_id: str, thread_id: str, state: WritingAssistantState
    ) -> None:
        now = self._now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO runs (
                    thread_id, session_id, status, writing, grade_level,
                    assignment_context, student_concerns, app_version,
                    started_at, updated_at
                ) VALUES (?, ?, 'running', ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    thread_id,
                    session_id,
                    state["writing"],
                    state["grade_level"],
                    state["assignment_context"],
                    state["student_concerns"],
                    state["app_version"],
                    now,
                    now,
                ),
            )

    def mark_running(self, thread_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE runs SET status = 'running', updated_at = ?, error = NULL "
                "WHERE thread_id = ?",
                (self._now(), thread_id),
            )

    def save_result(
        self,
        thread_id: str,
        state: dict[str, Any],
        pending: bool,
        duration_ms: int,
    ) -> None:
        status = "awaiting_clarification" if pending else "completed"
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE runs
                SET status = ?, updated_at = ?, routing_decision = ?,
                    state_json = ?, duration_ms = duration_ms + ?, error = NULL
                WHERE thread_id = ?
                """,
                (
                    status,
                    self._now(),
                    state.get("routing_decision"),
                    json.dumps(state, ensure_ascii=False),
                    duration_ms,
                    thread_id,
                ),
            )

    def record_error(self, thread_id: str, error: str, duration_ms: int) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE runs
                SET status = 'failed', updated_at = ?, error = ?,
                    duration_ms = duration_ms + ?
                WHERE thread_id = ?
                """,
                (self._now(), error, duration_ms, thread_id),
            )

    @staticmethod
    def _to_record(row: sqlite3.Row) -> RunRecord:
        return RunRecord(
            thread_id=row["thread_id"],
            session_id=row["session_id"],
            status=row["status"],
            writing=row["writing"],
            grade_level=row["grade_level"],
            assignment_context=row["assignment_context"],
            student_concerns=row["student_concerns"],
            app_version=row["app_version"],
            started_at=row["started_at"],
            updated_at=row["updated_at"],
            routing_decision=row["routing_decision"],
            state=json.loads(row["state_json"]),
            duration_ms=row["duration_ms"],
            error=row["error"],
        )

    def get_run(self, thread_id: str) -> RunRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE thread_id = ?", (thread_id,)
            ).fetchone()
        return self._to_record(row) if row else None

    def list_runs(self, session_id: str, limit: int = 100) -> list[RunRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM runs WHERE session_id = ? "
                "ORDER BY updated_at DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [self._to_record(row) for row in rows]

    def delete_session(self, session_id: str) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT thread_id FROM runs WHERE session_id = ?", (session_id,)
            ).fetchall()
            thread_ids = [row["thread_id"] for row in rows]
            connection.execute("DELETE FROM runs WHERE session_id = ?", (session_id,))
        return thread_ids
