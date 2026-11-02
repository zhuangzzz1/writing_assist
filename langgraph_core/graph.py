import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from agents.assessment_coordinator import AssessmentCoordinator
from agents.support_agent import InstructionalSupportAgent
from agents.utils import DeepSeekClient, InputValidationError
from langgraph_core.nodes import (
    clarification_node,
    direct_response_node,
    make_assessment_node,
    make_support_node,
    teacher_review_node,
)
from langgraph_core.routing import route_from_assessment
from langgraph_core.state import WritingAssistantState
from storage.interface import RunRecord, RunStorage
from storage.sqlite_storage import SQLiteStorage


@dataclass
class InvocationResult:
    thread_id: str
    state: dict[str, Any]
    pending_question: str | None = None

    @property
    def pending(self) -> bool:
        return self.pending_question is not None


class WritingAssistantService:
    def __init__(
        self,
        client: DeepSeekClient,
        storage: RunStorage,
        checkpointer: SqliteSaver,
        version: str = "v1",
    ):
        self.storage = storage
        self.checkpointer = checkpointer
        self.version = version
        coordinator = AssessmentCoordinator(client, version)
        support_agent = InstructionalSupportAgent(client, version)

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
        if interrupts:
            payload = interrupts[0].value
            if isinstance(payload, dict):
                pending_question = str(payload.get("question", ""))
            else:
                pending_question = str(payload)
        return InvocationResult(thread_id, state, pending_question)

    def start_run(
        self,
        session_id: str,
        thread_id: str,
        initial_state: WritingAssistantState,
    ) -> InvocationResult:
        self.storage.create_run(session_id, thread_id, initial_state)
        return self._invoke(thread_id, initial_state)

    def resume_run(
        self, session_id: str, thread_id: str, answer: str
    ) -> InvocationResult:
        record = self.storage.get_run(thread_id)
        if record is None or record.session_id != session_id:
            raise InputValidationError("This clarification run is not available in your session.")
        if record.status != "awaiting_clarification":
            raise InputValidationError("This run is not waiting for a clarification answer.")
        if not answer.strip():
            raise InputValidationError("Write a short answer before resuming the analysis.")
        self.storage.mark_running(thread_id)
        return self._invoke(thread_id, Command(resume=answer.strip()))

    def _invoke(self, thread_id: str, graph_input: Any) -> InvocationResult:
        timer_started = time.perf_counter()
        try:
            result = self.graph.invoke(
                graph_input,
                config={"configurable": {"thread_id": thread_id}},
            )
        except Exception as exc:
            duration_ms = max(0, round((time.perf_counter() - timer_started) * 1000))
            self.storage.record_error(thread_id, str(exc), duration_ms)
            raise
        duration_ms = max(0, round((time.perf_counter() - timer_started) * 1000))
        invocation = self._extract_result(thread_id, result)
        self.storage.save_result(
            thread_id,
            invocation.state,
            invocation.pending,
            duration_ms,
        )
        return invocation

    def get_run(self, thread_id: str) -> RunRecord | None:
        return self.storage.get_run(thread_id)

    def list_runs(self, session_id: str) -> list[RunRecord]:
        return self.storage.list_runs(session_id)

    def delete_session(self, session_id: str) -> None:
        thread_ids = self.storage.delete_session(session_id)
        for thread_id in thread_ids:
            self.checkpointer.delete_thread(thread_id)


def create_writing_assistant_service(
    client: DeepSeekClient,
    database_path: str,
    version: str = "v1",
) -> WritingAssistantService:
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    storage = SQLiteStorage(str(path))
    connection = sqlite3.connect(str(path), check_same_thread=False, timeout=30)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=30000")
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()
    return WritingAssistantService(client, storage, checkpointer, version)
