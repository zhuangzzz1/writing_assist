import streamlit as st

from ui.visualization import graph_dot


def render_observability(state: dict | None, options: dict) -> None:
    st.subheader("Agent observability")
    if not state:
        st.info("Run or load an analysis to inspect agent decisions.")
        return

    path = state.get("agent_path", [])
    route = (
        "teacher_review"
        if state.get("teacher_message")
        else state.get("routing_decision", "awaiting assessment")
    )
    st.markdown("**Routing decision**")
    st.code(route)
    if path:
        st.caption(" → ".join(path))
    if state.get("coordinator_reasoning"):
        with st.expander("Coordinator rationale", expanded=True):
            st.write(state["coordinator_reasoning"])

    logs = state.get("execution_logs", [])
    visible_logs = logs
    if not options["show_prompts"]:
        visible_logs = [
            {
                key: value
                for key, value in log.items()
                if key not in {"prompt", "raw_response", "raw_responses"}
            }
            for log in logs
        ]
    api_calls = sum(
        log.get("api_calls", 1 if log.get("api_call") else 0) for log in logs
    )
    total_ms = sum(log.get("duration_ms", 0) for log in logs)
    if options["show_timing"]:
        metric_columns = st.columns(3)
        metric_columns[0].metric("Steps", len(logs))
        metric_columns[1].metric("API calls", api_calls)
        metric_columns[2].metric("LLM/node time", f"{total_ms / 1000:.2f}s")

    st.markdown("**Execution timeline**")
    for index, log in enumerate(logs, start=1):
        label = (
            f"{index}. {log.get('display_name', log.get('node'))} "
            f"({log.get('duration_ms', 0)} ms)"
        )
        with st.expander(label, expanded=False):
            st.json(log.get("state_changes", {}), expanded=False)
            if options["show_prompts"]:
                if "prompt" in log:
                    st.markdown("**Prompt**")
                    st.json(log["prompt"])
                    responses = log.get("raw_responses", [log.get("raw_response", "")])
                    for response_index, response in enumerate(responses, start=1):
                        st.markdown(f"**Raw model response {response_index}**")
                        st.code(response)
                elif log.get("api_call"):
                    st.caption("Prompt capture was disabled for this run.")

    if options["show_state"]:
        with st.expander("Final state and state changes"):
            st.json({**state, "execution_logs": visible_logs}, expanded=False)
    if options["show_logs"]:
        with st.expander("Execution logs"):
            st.json(visible_logs, expanded=False)

    if state.get("teacher_message"):
        with st.expander("Teacher-facing evidence (evaluator view)", expanded=True):
            st.markdown(state["teacher_message"])

    st.markdown("**LangGraph structure and executed path**")
    st.graphviz_chart(graph_dot(path), width="stretch")
