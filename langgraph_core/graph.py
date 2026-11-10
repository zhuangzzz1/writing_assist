import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import ConfigurationError, DeepSeekClient, InputValidationError
from langgraph_core.nodes import (
    clarification_node,
    direct_response_node,
    make_assessment_node,
    make_support_node,
    teacher_review_node,
)
from langgraph_core.routing import route_from_assessment
from langgraph_core.state import WritingAssistantState
from storage.interface import CompositionStorage
from storage.sqlite_storage import SQLiteStorage


StageCallback = Callable[[str], None]


@dataclass
class InvocationResult:
    thread_id: str
    state: dict[str, Any]
    pending_question: str | None = None
    pending_choices: list[str] | None = None
    service_duration_ms: int | None = None

    @property
    def pending(self) -> bool:
        return self.pending_question is not None


class WritingAssistantService:
    def __init__(
        self,
        client: DeepSeekClient,
        storage: CompositionStorage,
        checkpointer: SqliteSaver,
    ):
        self.storage = storage
        self.checkpointer = checkpointer
        self.client = client
        coordinator = AssessmentCoordinator(client)
        support_agent = InstructionalSupportAgent(client)

        builder = StateGraph(WritingAssistantState)
        builder.add_node("assessment_coordinator", make_assessment_node(coordinator))
        builder.add_node("clarification", clarification_node)
        builder.add_node("support_agent", make_support_node(support_agent))
        builder.add_node("teacher_review", teacher_review_node)
        builder.add_node("direct_response", direct_response_node)
        builder.add_edge(START, "assessment_coordinator")
        builder.add_conditional_edges(
            "assessment_coordinator",
            route_from_assessment,
            {
                "ask_clarification": "clarification",
                "support_agent": "support_agent",
                "teacher_review": "teacher_review",
                "direct_response": "direct_response",
            },
        )
        builder.add_edge("clarification", "assessment_coordinator")
        builder.add_edge("support_agent", END)
        builder.add_edge("teacher_review", END)
        builder.add_edge("direct_response", END)
        self.graph = builder.compile(checkpointer=checkpointer)

    @staticmethod
    def _extract_result(
        thread_id: str, result: dict[str, Any]
    ) -> InvocationResult:
        interrupts = result.get("__interrupt__", [])
        state = {key: value for key, value in result.items() if key != "__interrupt__"}
        pending_question = None
        pending_choices = []
        if interrupts:
            payload = interrupts[0].value
            if isinstance(payload, dict):
                pending_question = str(payload.get("question", ""))
                pending_choices = list(payload.get("choices", []))
            else:
                pending_question = str(payload)
        return InvocationResult(thread_id, state, pending_question, pending_choices)

    def start_composition(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        state["model_config"] = self.client.model_config()
        self.storage.create_composition(session_id, state, snapshot_id)
        if stage_callback:
            stage_callback("Draft saved")
        return self._invoke(
            state["thread_id"], state, stage_callback, operation_started
        )

    def submit_revision(
        self,
        session_id: str,
        state: WritingAssistantState,
        snapshot_id: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        state["model_config"] = self.client.model_config()
        self.storage.create_revision(session_id, state, snapshot_id)
        if stage_callback:
            stage_callback("Revision snapshot saved")
        return self._invoke(
            state["thread_id"], state, stage_callback, operation_started
        )

    def reassess_genre(
        self,
        session_id: str,
        state: WritingAssistantState,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        state["model_config"] = self.client.model_config()
        self.storage.create_reassessment(session_id, state)
        if stage_callback:
            stage_callback("Draft saved")
        return self._invoke(
            state["thread_id"], state, stage_callback, operation_started
        )

    def resume_clarification(
        self,
        session_id: str,
        composition_id: str,
        answer: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        composition = self.storage.get_composition(composition_id)
        if composition is None or composition.session_id != session_id:
            raise InputValidationError("Saved history is unavailable for this composition.")
        round_record = self.storage.get_latest_round(composition_id)
        if round_record is None or round_record.status != "awaiting_clarification":
            raise InputValidationError("This review is not waiting for a clarification answer.")
        if not answer.strip():
            raise InputValidationError("Write a short answer before resuming the review.")
        self.storage.mark_running(round_record.thread_id)
        return self._invoke(
            round_record.thread_id,
            Command(resume=answer.strip()),
            stage_callback,
            operation_started,
        )

    def retry_round(
        self,
        session_id: str,
        composition_id: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        composition = self.storage.get_composition(composition_id)
        if composition is None or composition.session_id != session_id:
            raise InputValidationError("Saved history is unavailable for this composition.")
        round_record = self.storage.get_latest_round(composition_id)
        if round_record is None or round_record.status != "failed":
            raise InputValidationError("There is no failed review to retry.")
        self.storage.mark_running(round_record.thread_id)
        return self._invoke(
            round_record.thread_id,
            round_record.input_state,
            stage_callback,
            operation_started,
        )

    def finish_composition(
        self,
        session_id: str,
        state: WritingAssistantState,
        original_snapshot_id: str,
        final_snapshot_id: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        state["model_config"] = self.client.model_config()
        self.storage.create_final(
            session_id, state, original_snapshot_id, final_snapshot_id
        )
        if stage_callback:
            stage_callback("Drafts saved")
        if state["revision_number"] == 0:
            latest = self.storage.get_latest_round(state["composition_id"])
            strengths = latest.state.get("strengths", []) if latest else []
            state.update(
                {
                    "routing_decision": "direct_response",
                    "flag_teacher": False,
                    "original_strengths": strengths,
                    "comparison_improvements": [],
                    "comparison_regressions": [],
                    "future_areas": [],
                    "final_reflection": {
                        "original_strengths": strengths,
                        "improvements": [],
                        "regressions": [],
                        "future_possibilities": [],
                        "conclusion": (
                            "You chose to stop before submitting a revision. Your original "
                            "draft is preserved, and you can return to it whenever you choose."
                        ),
                    },
                    "student_output": "No revised draft was submitted, so no improvement summary was generated.",
                    "review_stage": "complete",
                }
            )
            self.storage.save_final_result(state["thread_id"], state, 0)
            if stage_callback:
                stage_callback("Reflection complete")
            return InvocationResult(
                state["thread_id"],
                state,
                service_duration_ms=max(
                    0, round((time.perf_counter() - operation_started) * 1000)
                ),
            )
        return self._invoke(
            state["thread_id"], state, stage_callback, operation_started
        )

    def retry_final(
        self,
        session_id: str,
        composition_id: str,
        stage_callback: StageCallback | None = None,
    ) -> InvocationResult:
        operation_started = time.perf_counter()
        composition = self.storage.get_composition(composition_id)
        if composition is None or composition.session_id != session_id:
            raise InputValidationError("Saved history is unavailable for this composition.")
        reflection = self.storage.get_reflection(composition_id)
        if reflection is None or reflection.status != "failed":
            raise InputValidationError("There is no failed final reflection to retry.")
        self.storage.mark_running(reflection.thread_id)
        return self._invoke(
            reflection.thread_id,
            reflection.input_state,
            stage_callback,
            operation_started,
        )

    def _invoke(
        self,
        thread_id: str,
        graph_input: Any,
        stage_callback: StageCallback | None = None,
        operation_started: float | None = None,
    ) -> InvocationResult:
        timer_started = time.perf_counter()
        try:
            result = self.graph.invoke(
                graph_input,
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "stage_callback": stage_callback,
                    }
                },
            )
        except Exception as exc:
            duration_ms = max(0, round((time.perf_counter() - timer_started) * 1000))
            self.storage.record_error(thread_id, str(exc), duration_ms)
            raise
        duration_ms = max(0, round((time.perf_counter() - timer_started) * 1000))
        invocation = self._extract_result(thread_id, result)
        if invocation.state.get("review_mode") == "final":
            self.storage.save_final_result(thread_id, invocation.state, duration_ms)
        else:
            self.storage.save_round_result(
                thread_id,
                invocation.state,
                invocation.pending,
                duration_ms,
            )
        invocation.service_duration_ms = max(
            0,
            round(
                (time.perf_counter() - (operation_started or timer_started)) * 1000
            ),
        )
        return invocation

    def delete_session(self, session_id: str) -> None:
        thread_ids = self.storage.delete_session(session_id)
        for thread_id in thread_ids:
            self.checkpointer.delete_thread(thread_id)


def create_writing_assistant_service(
    client: DeepSeekClient,
    database_path: str,
    require_thinking: bool = False,
) -> WritingAssistantService:
    if require_thinking and not client.thinking:
        raise ConfigurationError(
            "This controlled evaluation requires thinking mode. Enable it explicitly "
            "for that run; the application will not switch modes automatically."
        )
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    storage = SQLiteStorage(str(path))
    connection = sqlite3.connect(str(path), check_same_thread=False, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=30000")
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return WritingAssistantService(client, storage, checkpointer)
