from typing import Any

import streamlit as st

from ui.visualization import graph_dot


UNAUTHORIZED_DEBUG_KEYS = {"reasoning_content", "chain_of_thought", "thinking_process"}


def _authorized(value: Any, show_prompts: bool) -> Any:
    if isinstance(value, list):
        return [_authorized(item, show_prompts) for item in value]
    if not isinstance(value, dict):
        return value
    hidden = set(UNAUTHORIZED_DEBUG_KEYS)
    if not show_prompts:
        hidden.update({"prompt", "raw_response", "raw_responses"})
    return {
        key: _authorized(item, show_prompts)
        for key, item in value.items()
        if key not in hidden
    }


def render_observability(state: dict | None, options: dict) -> None:
    st.subheader("Agent observability")
    if not state:
        st.info("Run or load a review to inspect agent decisions.")
        return

    path = state.get("agent_path", [])
    route = (
        "teacher_review"
        if state.get("teacher_message")
        else state.get("routing_decision", "awaiting assessment")
    )
    st.markdown("**Routing decision**")
    st.code(route)
    st.caption(f"Review stage: {state.get('review_stage', 'unknown')}")
    if path:
        st.caption(" → ".join(path))
    if state.get("working_genre"):
        st.caption(
            f"Working genre: {state['working_genre']} | Confidence: "
            f"{state.get('genre_confidence', '') or 'not supplied'}"
        )
        if state.get("genre_basis"):
            st.caption(state["genre_basis"])
    if state.get("coordinator_reasoning"):
        with st.expander("Coordinator rationale", expanded=True):
            st.write(state["coordinator_reasoning"])
    if state.get("model_config"):
        with st.expander("Authorized model configuration", expanded=False):
            st.json(_authorized(state["model_config"], options["show_prompts"]))

    logs = state.get("execution_logs", [])
    visible_logs = _authorized(logs, options["show_prompts"])
    api_calls = sum(log.get("api_calls", 0) for log in logs)
    total_ms = sum(log.get("duration_ms", 0) for log in logs)
    if options["show_timing"]:
        metric_columns = st.columns(3)
        metric_columns[0].metric("Steps", len(logs))
        metric_columns[1].metric("API calls", api_calls)
        metric_columns[2].metric("Observed node time", f"{total_ms / 1000:.2f}s")
        for log in logs:
            for call in log.get("model_calls", []):
                usage = call.get("token_usage", {})
                st.caption(
                    f"{log.get('display_name')}: {call.get('model_name', '')}; "
                    f"thinking={call.get('thinking_enabled', '')}; "
                    f"total tokens={usage.get('total_tokens', 'not supplied')}; "
                    f"reasoning tokens={usage.get('reasoning_tokens', 'not supplied')}"
                )

    st.markdown("**Execution timeline**")
    for index, log in enumerate(visible_logs, start=1):
        label = (
            f"{index}. {log.get('display_name', log.get('node'))} "
            f"({log.get('duration_ms', 0)} ms)"
        )
        with st.expander(label, expanded=False):
            st.json(log.get("state_changes", {}), expanded=False)
            if options["show_prompts"]:
                if "prompt" in log:
                    st.markdown("**Final-request prompt**")
                    st.json(log["prompt"])
                    for response_index, response in enumerate(
                        log.get("raw_responses", []), start=1
                    ):
                        st.markdown(f"**Final raw response {response_index}**")
                        st.code(response)
                elif log.get("api_calls"):
                    st.caption("Prompt capture was disabled for this run.")

    if options["show_state"]:
        with st.expander("Final state and state changes"):
            st.json(_authorized(state, options["show_prompts"]), expanded=False)
    if options["show_logs"]:
        with st.expander("Execution logs"):
            st.json(visible_logs, expanded=False)

    if state.get("teacher_message"):
        with st.expander("Teacher-facing evidence (evaluator view)", expanded=True):
            st.markdown(state["teacher_message"])

    st.markdown("**LangGraph structure and executed path**")
    st.graphviz_chart(graph_dot(path), width="stretch")
