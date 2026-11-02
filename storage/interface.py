from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from langgraph_core.state import WritingAssistantState


@dataclass
class RunRecord:
    thread_id: str
    session_id: str
    status: str
    writing: str
    grade_level: str
    assignment_context: str
    student_concerns: str
    app_version: str
    started_at: str
    updated_at: str
    routing_decision: str | None = None
    state: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    error: str | None = None


class RunStorage(ABC):
    @abstractmethod
    def create_run(
        self, session_id: str, thread_id: str, state: WritingAssistantState
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_running(self, thread_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_result(
        self,
        thread_id: str,
        state: dict[str, Any],
        pending: bool,
        duration_ms: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_error(self, thread_id: str, error: str, duration_ms: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_run(self, thread_id: str) -> RunRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_runs(self, session_id: str, limit: int = 100) -> list[RunRecord]:
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_id: str) -> list[str]:
        raise NotImplementedError
