# CLAUDE.md

This file provides guidance to coding agents working in this repository.

## Project Overview

This is a two-agent writing assistant for 5th-7th grade students, built as an academic project for EDUC 6192 (LLM and Education) at UPenn GSE. LangGraph coordinates an Assessment Coordinator and an Instructional Support Agent. The rubric prioritizes educational fit, meaningful agent-controlled decisions, appropriate boundaries, observable behavior, and genuine V1-to-V2 improvement.

Use only synthetic writing. This is an educational demo, not production software for minors.

## Locked V1 Decisions

- Build V1 as a genuine best effort. Do not script failures or predetermine V2 changes.
- Normal support returns strengths, 2-3 revision priorities, and one targeted exercise when the coordinator identifies a gap that warrants practice. Practice does not replace feedback.
- The optional assignment input is one flexible **assignment type or prompt** field (`assignment_context`). Missing assignment context is not automatically a clarification trigger.
- Only empty input is rejected locally. Every nonempty submission goes to the coordinator so safety assessment precedes short/non-writing clarification rules.
- Clarification uses exact LangGraph `interrupt()`/`Command(resume=...)` with a stable thread ID and SQLite checkpoints. A reply loops back to the coordinator for reassessment.
- After two clarification answers remain ambiguous, escalate to non-safety teacher review with the clarification history.
- Teacher review bypasses the Support Agent and uses coordinator evidence plus reviewed category-specific templates. Do not add audience-specific agents without evidence and a separate architecture decision.
- Keep the two decision-making agents. Teacher review, clarification, and direct response are deterministic nodes.
- Use `deepseek-flash` through `requests`. Official V1 used non-thinking mode at temperature 0 after a real smoke comparison; keep that configuration fixed for V2 and deployment comparisons. Thinking mode ignores temperature.
- Preserve V1 with a Git tag before V2 work. Deploy only the active version; use saved runs and screenshots for comparison rather than a runtime V1/V2 selector.
- Build the full three-column dashboard in V1, including routing, timeline, state changes, graph visualization, debug controls, fixture loading, and persistent history.
- Store checkpoints and run history in SQLite locally and on Streamlit Cloud. Filter by random session IDs in URLs, but do not describe this as secure isolation or authentication.
- Retain data until the user chooses **Delete my data** or the cloud filesystem is replaced. No automatic retention period is applied.

## Architecture

```text
Input -> Assessment Coordinator -> conditional route
    |- ask_clarification -> interrupt -> answer -> Assessment Coordinator
    |- support_agent -> feedback + optional targeted practice -> END
    |- teacher_review -> separate student/teacher outputs -> END
    `- direct_response -> affirm without forced criticism -> END
```

`routing_decision` is authoritative: `ask_clarification`, `support_agent`, `teacher_review`, or `direct_response`. The router checks `flag_teacher` first, then the enum. Missing or malformed output falls back to `ask_clarification`, never `support_agent`. `needs_feedback` and `needs_practice` are Support Agent inputs only.

`langgraph_core/state.py` uses Python 3.11+ `TypedDict`/`NotRequired`. Initialize inputs and execution metadata in the initial state. Each node returns only fields it owns; downstream reads use `state.get()` for values that may be absent. Clarification history replaces lists rather than using additive reducers so node replay cannot duplicate entries.

## Code Organization

- `app.py`: Streamlit entry point and cached runtime setup
- `agents/`: DeepSeek client, coordinator/support logic, and separate versioned prompts
- `langgraph_core/`: state, node functions, routing, graph construction, and invocation helpers
- `ui/`: input/output components, dashboard layout, observability, and graph visualization
- `storage/`: run-history interface and SQLite implementation
- `test_cases/`: four frozen synthetic fixtures; do not edit them for official runs
- `tests/`: pytest unit/integration tests using mocked model calls and temporary databases

## Commands

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Add DEEPSEEK_API_KEY locally
pytest
streamlit run app.py
```

There is no separate formatter, linter, or type-checker configured. Run pytest after each implementation stage and exercise real fixture flows before calling V1 complete.

## Safety, Privacy, and Evidence

The UI warning is: "Do not submit writing containing real names, schools, or personal information. This is a demo system — your input is sent to an external AI service."

Writing, grade level, assignment context, student concerns, and clarification answers may be sent to DeepSeek and stored in SQLite. Session filtering is not secure multi-user isolation. Teacher handoff is simulated: no teacher is notified. Never promise otherwise, and do not improvise crisis keywords, hotline numbers, or localized crisis protocols.

Use byte-identical fixtures for V1/V2. Temperature 0 reduces variability only in non-thinking mode and never guarantees identical output. Record actual routes, concise final-output rationales, outputs, timing, and errors. Do not store or present hidden chain-of-thought as coordinator reasoning.

The assignment requires all eight submission items in `EDUC_6192_Fall_2026_Syllabus.md`, real V1 review, evidence-based V2 changes, JeepyTA feedback reviewed with judgment, application access, and an AI Use Acknowledgment. Keep `PRD.md`, `project_plan.md`, `AGENTS.md`, and this file consistent with actual behavior.
