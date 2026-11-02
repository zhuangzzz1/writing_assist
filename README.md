# Writing Assistant

A two-agent writing assistant for students in grades 5–7, built with LangGraph, DeepSeek, Streamlit, and SQLite. It provides age-appropriate feedback and targeted practice, asks clarifying questions with exact graph resume, and routes boundary cases to a clearly simulated teacher-review view.

V2 adds learner-selected revision focuses, optional choice-specific practice, calibrated light-touch or standard feedback, an optional affect self-report, and one bounded schema-repair attempt per agent invocation. The two agents and four graph routes remain unchanged. Learner choices affect presentation only; they do not trigger another model call.

## Local setup

Requires Python 3.11 or newer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Add your DeepSeek API key to `.env` and set `APP_VERSION=v2`. Never commit this file. Use only synthetic writing: the demo sends submitted writing and metadata to an external AI service and stores run data in the configured SQLite database. The optional affect check-in is also sent and stored; it is self-reported, not an emotion diagnosis.

```bash
streamlit run app.py
```

The default database is `data/writing_assistant.db`, which is git-ignored. The dashboard filters history by a random session identifier in the URL; this is not authentication or secure multi-user isolation. Use **Delete my data** to remove the current session's history and checkpoints. Data is otherwise retained until manual deletion or cloud filesystem replacement.

## Tests

```bash
pytest
```

The current suite has **79 passing checks** using mocked model responses and temporary SQLite databases. Real DeepSeek calls are separate scenario evidence, not interchangeable with unit tests.

## Current V2 status

V2 is implemented and verified through the automated suite, real scenario runs, and browser checks of saved V2 runs. V1 is preserved at commit `4eaa0ad` under the annotated `v1` tag. The V1/V2 commits and local `v1` tag have not been pushed.

Authoritative evidence is in:

- `PRD.md` Section 7.5 for actual V1 results and Section 7.6 for final V2 results.
- `data/v1_official.db` and `data/v2_official.db` for saved runs and checkpoints.
- `data/evidence/v2_final_release_summary.json` for the consistent final eight-scenario V2 set.
- `data/evidence/v2_normal_choice_practice.jpg` and `v2_frustrated_light_ui.jpg` for local browser captures.

All databases and evidence files are git-ignored. The final V2 set covers the four frozen fixtures, the V1 strong narrative and clarification-limit inputs, and two supplementary affect checks. It shows design and output alignment only; it does not establish improved learner motivation, engagement, affect, or learning outcomes. One incomplete-case practice example still supplies an explanation similar to the requested attempt, so non-answer scaffolding is not fully reliable.

JeepyTA review, Parts 4–6, final application access, the AI Use Acknowledgment, deployment, and deployed-scenario verification remain incomplete.

## Configuration

Official V1 and V2 comparisons use `DEEPSEEK_THINKING=false` and temperature 0 with `deepseek-flash` and JSON mode. Keep that configuration fixed for deployment comparisons. Thinking mode ignores temperature, and temperature 0 does not guarantee identical output.

`ENABLE_DEBUG_MODE=false` is the default. Set it to `true` only for local evaluation to enable the prompt capture/display controls; capture remains opt-in for each new run. Raw prompt and response fields stay hidden from state and log views unless prompt display is selected.
