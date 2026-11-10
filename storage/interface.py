from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from langgraph_core.state import WritingAssistantState


@dataclass
class CompositionRecord:
    composition_id: str
    session_id: str
    status: str
    grade_level: str
    genre_selection: str
    assignment_prompt: str
    teacher_directions: str
    framework_name: str
    framework_components: list[str]
    source_material: str
    source_material_available: bool
    student_concerns: str
    scenario_id: str
    fixture_version: str
    revision_number: int
    active_round_id: str | None
    active_thread_id: str | None
    final_thread_id: str | None
    created_at: str
    updated_at: str


@dataclass
class SnapshotRecord:
    snapshot_id: str
    composition_id: str
    revision_number: int
    writing: str
    selected_goals: list[dict[str, Any]] = field(default_factory=list)
    goal_self_reports: dict[str, str] = field(default_factory=dict)
    created_at: str = ""


@dataclass
class RoundRecord:
    round_id: str
    composition_id: str
    revision_number: int
    thread_id: str
    kind: str
    status: str
    stage: str
    input_state: dict[str, Any]
    state: dict[str, Any]
    routing_decision: str | None
    duration_ms: int
    error: str | None
    started_at: str
    updated_at: str


@dataclass
class ReflectionRecord:
    composition_id: str
    original_snapshot_id: str
    final_snapshot_id: str
    thread_id: str
    status: str
    stage: str
    input_state: dict[str, Any]
    state: dict[str, Any]
    duration_ms: int
    error: str | None
    created_at: str


class CompositionStorage(ABC):
    @abstractmethod
    def create_composition(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_revision(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_reassessment(
        self, session_id: str, state: WritingAssistantState
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_final(
        self,
        session_id: str,
        state: WritingAssistantState,
        original_snapshot_id: str,
        final_snapshot_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_running(self, thread_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def mark_stage(self, thread_id: str, stage: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_round_result(
        self,
        thread_id: str,
        state: dict[str, Any],
        pending: bool,
        duration_ms: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_final_result(
        self, thread_id: str, state: dict[str, Any], duration_ms: int
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def record_error(self, thread_id: str, error: str, duration_ms: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_composition(self, composition_id: str) -> CompositionRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_compositions(
        self, session_id: str, limit: int = 100
    ) -> list[CompositionRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_snapshot(
        self, composition_id: str, revision_number: int
    ) -> SnapshotRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_snapshots(self, composition_id: str) -> list[SnapshotRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_round(self, round_id: str) -> RoundRecord | None:
        raise NotImplementedError

    @abstractmethod
    def get_round_by_thread(self, thread_id: str) -> RoundRecord | None:
        raise NotImplementedError

    @abstractmethod
    def get_latest_round(self, composition_id: str) -> RoundRecord | None:
        raise NotImplementedError

    @abstractmethod
    def list_rounds(self, composition_id: str) -> list[RoundRecord]:
        raise NotImplementedError

    @abstractmethod
    def get_reflection(self, composition_id: str) -> ReflectionRecord | None:
        raise NotImplementedError

    @abstractmethod
    def delete_session(self, session_id: str) -> list[str]:
        raise NotImplementedError
