# Writing Assistant

A two-agent writing assistant for students in grades 5–7, built with LangGraph, DeepSeek, Streamlit, and SQLite. It provides age-appropriate feedback and targeted practice, asks clarifying questions with exact graph resume, and routes boundary cases to a clearly simulated teacher-review view.

## Local setup

Requires Python 3.11 or newer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Add your DeepSeek API key to `.env`. Never commit this file. Use only synthetic writing: the demo sends submitted writing and metadata to an external AI service and stores run data in the configured SQLite database.

```bash
streamlit run app.py
```

The default database is `data/writing_assistant.db`, which is git-ignored. The dashboard filters history by a random session identifier in the URL; this is not authentication or secure multi-user isolation. Use **Delete my data** to remove the current session's history and checkpoints. Data is otherwise retained until manual deletion or cloud filesystem replacement.

## Tests

```bash
pytest
```

Unit and integration tests use mocked model responses and temporary SQLite databases. Real DeepSeek calls are run separately for scenario evidence.

## Current V1 status

V1 is implemented and verified through 48 automated checks, real DeepSeek scenario runs, and browser-based dashboard checks. Actual outcomes and human-review candidates are documented in `PRD.md` Section 7.5. Local evidence is in git-ignored `data/v1_official.db` and `data/evidence/`. Current Parts 1–3 drafts and nine cropped evidence figures are in `submission/`; see `PRD.md` Section 7.5 for evidence scope and provenance.

V1 has not been committed/tagged, deployed, or reviewed for V2 yet. Preserve the reviewed V1 with a Git tag before V2 changes begin. The deployed app will contain the active version only; before-and-after evidence will come from saved runs rather than a runtime version selector.

## Configuration

Official V1 used `DEEPSEEK_THINKING=false` and temperature 0 after a real smoke comparison of both modes. Keep that configuration fixed for V2 and deployment comparisons. Thinking mode ignores temperature.
