# CLAUDE.md

Guidance for coding agents working in this repository.

## Project Overview

V3 is a two-agent iterative writing coach for grades 5–7, built with LangGraph, explicitly configured DeepSeek non-thinking mode, Streamlit CCv2, Pydantic, and SQLite. Students select one to three goals, edit their own complete draft, submit immutable revisions, and stop voluntarily with an original-to-final reflection. Use only synthetic writing. This is not production software for minors.

`PRD_V3_ITERATIVE_REVISION.md` is the active product contract. `PRD.md` and the annotated `v1` tag preserve historical V1/V2 coursework and evidence; the old runtime paths have been replaced.

## Current V3 Decisions

- Keep two model-driven agents. The Coordinator owns assessment, genre, source limits, selected-goal observations, comparison findings, human-review flags, and routing. Support owns student-facing round feedback, bounded scaffolds, and final reflection.
- Teacher review, clarification, direct response, diffs, milestones, and lifecycle operations are deterministic. Do not add a comparison agent or audience-specific agents without a separate architecture decision.
- Every nonempty draft goes to the Coordinator. Empty drafts are rejected locally. Explicit length limits reject oversized input without truncation.
- Genre selection is `auto`, `argument`, `informational`, or `narrative`. Explicit student correction triggers a new assessment of the latest submitted snapshot, not a new revision snapshot or clarification confirmation.
- V3 has no affect field or check-in. **Show less feedback** and **I’m stuck** only reveal pregenerated presentation content; they make no model call and never infer emotion, effort, or teacher review.
- Source availability is deterministic. Source-dependent findings require locations; no-source accuracy claims and invented source content are invalid.
- Every candidate reference must be an exact current-draft substring with correct paragraph/occurrence metadata. Support must preserve Coordinator references and source limitations exactly.
- Hints contain a passage reference, two to four linked steps, and a self-check. Optional sentence starters use `____` and leave all substance to the student. V3 does not generate optional practice exercises in round feedback.
- Revision observations cover every selected goal and use descriptive statuses, not scores or attempt assumptions. Optional attempted/deferred self-reports are stored with the revision snapshot.
- Final reflection uses deterministic original/latest-submitted diffs and Coordinator finding IDs. Support cannot omit regressions, add improvements, or change verified references.
- Each agent invocation permits one bounded repair. Coordinator failure after repair falls back to safe clarification; Support/final failure produces no partial feedback. API and thinking-mode failures propagate rather than silently switching modes.

## Architecture

```text
Submitted draft -> Assessment Coordinator -> conditional route
    |- ask_clarification -> interrupt -> answer -> Coordinator
    |- support_agent -> candidates + pregenerated scaffolds -> END
    |- teacher_review -> separate student/evaluator outputs -> END
    `- direct_response -> no manufactured revision -> END

Finish confirmation -> deterministic original/final diff
    -> Coordinator comparison -> Support final reflection -> END
```

`langgraph_core/state.py` uses `TypedDict`/`NotRequired`. Initialize inputs, IDs, model configuration, and execution metadata together. Each node returns only fields it owns. Replacement lists prevent duplicate history during interrupt replay.

`langgraph_core/revision.py` owns exact reference location, word-level diffs, and neutral change notifications. It makes no quality judgments.

## Code Organization

- `app.py`: Streamlit entry point and cached V3 runtime.
- `agents/`: DeepSeek HTTP client, V3 prompts, structured Coordinator/Support validation, repair, and authorized model metadata.
- `langgraph_core/`: V3 state, nodes, routing, graph/service operations, and deterministic revision utilities.
- `storage/`: Composition, snapshot, round, reflection, restoration, and deletion persistence.
- `ui/`: Student workflow, scenario loading, CCv2 highlighted editor, and opt-in observability.
- `test_cases/v3/scenarios.json`: Separate versioned V3 synthetic presets. Root fixture files remain frozen historical V1/V2 evidence.
- `scripts/evaluate_v3.py`: Explicit representative paired real-model evaluation.
- `tests/`: Mocked unit/integration/AppTest coverage with temporary SQLite databases.

## Commands

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
pytest
streamlit run app.py
```

No formatter, linter, or type-checker is configured. Run pytest after each implementation stage. The current suite has 172 checks. Browser and real-model evidence are separate from unit tests.

For authorized billable evaluation:

```bash
python scripts/evaluate_v3.py --scenario-set core --modes nonthinking thinking
python scripts/evaluate_v3.py --scenario-set acceptance --modes nonthinking
```

The runner writes git-ignored databases and a JSON summary under `data/`, including invalid final responses and validation errors for repair diagnosis. It never stores raw hidden reasoning and never switches modes automatically. Inspect actual outputs before making quality claims. The earlier completed `v3.1.0` evidence is `data/evidence/v3_paired_evaluation_20261110T094344Z.json`: all six scenarios completed per mode; thinking used 17 calls/two repairs/68,407 tokens/246.2 seconds of model latency, while non-thinking used 15 calls/no repairs/36,340 tokens/64.2 seconds. This limited result supported the 2026-11-10 non-thinking runtime decision, not a general pedagogical-quality claim. Current improvement evidence is `V3_OUTCOMES_REPORT.md` Section 16, with acceptance set `data/evidence/v3_acceptance_evaluation_20261110T160932Z.json`, targeted #7/#24 corrections, and paired cores `data/evidence/v3_core_evaluation_20261110T161430Z.json` and `data/evidence/v3_core_evaluation_20261110T162342Z.json`.

## Model Configuration

- Student runtime uses `DEEPSEEK_THINKING=false` and temperature 0. Controlled thinking comparisons omit temperature and include configured reasoning effort.
- Record `model_name`, actual `thinking_enabled`, applicable `reasoning_effort`, prompt/schema/fixture versions, provider IDs, latency, and available token counts.
- Raw hidden reasoning is never stored or displayed. Evaluation diagnostics may retain final prompts and invalid final JSON responses; student debug capture remains separately opt-in.
- Neither mode is a student-facing selector or an automatic fallback.

## Storage and UI Invariants

- Persist original and every revision snapshot before model review. Snapshot updates are prohibited by SQLite trigger; deletion intentionally cascades for **Delete my data**.
- Retry uses the existing round/reflection and never creates a duplicate snapshot.
- Session IDs filter history but are not authentication. Missing/corrupt storage produces a safe recovery view and preserves any runtime editor text for copying.
- Keep the initial editor constrained and the desktop workspace 60/40. Marked grid rows must override Streamlit child column widths to 100% to avoid applying percentages twice.
- The CCv2 editor keeps text synchronized with Session State, highlights exact selected references, recalculates on edits, and drops stale highlights rather than relocating them.
- Step navigation and dialog cancellation preserve the editor and existing feedback. The final comparison uses submitted snapshots, never unsubmitted editor text.

## Safety, Privacy, and Evidence

The UI warning is: "Do not submit writing containing real names, schools, or personal information. This is a demo system — your input is sent to an external AI service."

Writing, assignment/source context, concerns, clarification answers, selected goals, self-reports, and diffs may be sent to DeepSeek and stored in SQLite. Session filtering is not secure multi-user isolation. Teacher handoff is simulated: no teacher is notified. Never invent crisis resources or diagnose students.

Historical V1 evidence is at commit `4eaa0ad` under the `v1` tag. Historical V1/V2 outcomes are in `PRD.md` Sections 7.5–7.7; the old V2 public deployment is commit `7d94b58`. Local V3 is not deployed. Do not claim learner outcomes, educator approval, or pedagogical effectiveness from mocked tests or synthetic model outputs.
