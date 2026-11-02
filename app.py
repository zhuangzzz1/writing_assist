import os

import streamlit as st
from dotenv import load_dotenv

from agents.utils import ConfigurationError, DeepSeekClient
from langgraph_core.graph import create_writing_assistant_service
from ui.layout import render_dashboard


st.set_page_config(page_title="Writing Assistant", page_icon=None, layout="wide")
load_dotenv()


@st.cache_resource
def get_runtime(database_path: str, version: str):
    client = DeepSeekClient.from_env()
    service = create_writing_assistant_service(client, database_path, version)
    return client, service


def main() -> None:
    database_path = os.getenv("DATABASE_PATH", "data/writing_assistant.db")
    version = os.getenv("APP_VERSION", "v1")
    try:
        client, service = get_runtime(database_path, version)
    except ConfigurationError as exc:
        st.error(str(exc))
        st.info("Copy .env.example to .env, add your DeepSeek API key, and restart the app.")
        return
    render_dashboard(service, client)


if __name__ == "__main__":
    main()
