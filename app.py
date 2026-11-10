import os
import sqlite3

import streamlit as st
from dotenv import load_dotenv

from agents.utils import ConfigurationError, DeepSeekClient
from langgraph_core.graph import create_writing_assistant_service
from ui.layout import render_dashboard


st.set_page_config(page_title="Writing Coach", page_icon=None, layout="wide")
load_dotenv()


@st.cache_resource
def get_runtime(database_path: str):
    client = DeepSeekClient.from_env(require_thinking=False)
    service = create_writing_assistant_service(client, database_path, require_thinking=False)
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
