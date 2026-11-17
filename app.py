import os
import sqlite3

import streamlit as st
from dotenv import load_dotenv

from agents.assessment_coordinator import AssessmentCoordinator
from agents.prompts import (
    PHASE1_COORDINATOR_FINAL_PROMPT,
    PHASE1_COORDINATOR_ROUND_PROMPT,
    PHASE2_LEAN_SUPPORT_FINAL_PROMPT,
    PHASE2_LEAN_SUPPORT_ROUND_PROMPT,
)
from agents.utils import ConfigurationError, DeepSeekClient
from agents.support_agent import InstructionalSupportAgent
from langgraph_core.graph import create_writing_assistant_service
from ui.layout import render_dashboard


st.set_page_config(page_title="Writing Coach", page_icon=None, layout="wide")
load_dotenv()


@st.cache_resource
def get_runtime(database_path: str):
    client = DeepSeekClient.from_env(
        require_thinking=False,
        reasoning_effort=os.getenv("DEEPSEEK_REASONING_EFFORT", "low"),
    )
    support_client = DeepSeekClient.from_env(
        require_thinking=False,
        reasoning_effort=os.getenv("DEEPSEEK_SUPPORT_REASONING_EFFORT", "low"),
    )
    service = create_writing_assistant_service(
        client,
        database_path,
        require_thinking=False,
        coordinator=AssessmentCoordinator(
            client,
            round_prompt=PHASE1_COORDINATOR_ROUND_PROMPT,
            final_prompt=PHASE1_COORDINATOR_FINAL_PROMPT,
            phase1_contract=True,
        ),
        support_agent=InstructionalSupportAgent(
            support_client,
            round_prompt=PHASE2_LEAN_SUPPORT_ROUND_PROMPT,
            final_prompt=PHASE2_LEAN_SUPPORT_FINAL_PROMPT,
            phase1_contract=True,
            lean_contract=True,
        ),
    )
    return client, service


def main() -> None:
    database_path = os.getenv("DATABASE_PATH", "data/writing_assistant_v3.db")
    try:
        client, service = get_runtime(database_path)
    except ConfigurationError as exc:
        st.error(str(exc))
        st.info(
            "Copy .env.example to .env, add your DeepSeek API key, review the "
            "explicit model configuration, and restart the app."
        )
        return
    except (sqlite3.Error, OSError):
        st.error(
            "Saved history is unavailable. It has not been restored. Repair or replace "
            "the local database configuration, then restart the app."
        )
        current = st.session_state.get("editor_text") or st.session_state.get(
            "writing_input", ""
        )
        if current:
            st.write("Copy your current editor text before leaving this page:")
            st.code(current, language=None)
        return
    render_dashboard(service, client)


if __name__ == "__main__":
    main()
