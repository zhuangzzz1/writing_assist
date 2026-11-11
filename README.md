# Writing Coach — V3 Iterative Revision

A local synthetic-classroom prototype for grades 5–7. Two LangGraph agents provide genre-sensitive assessment and bounded revision support while the student preserves authorship: choose one to three goals, edit the complete draft, submit immutable revision snapshots, repeat or stop, and finish with a grounded original-to-final reflection.

V3 supports argument, informational, and narrative writing; optional assignment/source context; structured CER/RACE/RACES/MEAL or custom framework requirements; Coordinator-owned framework coverage; correctable genre inference; exact and overlap-grouped goal highlights; pregenerated hints; neutral small-change handling; clarification and simulated teacher review; read-only history; session restoration/deletion; and opt-in developer observability. It does not assign grades, predict ELPAC/SBAC outcomes, write replacement responses, or claim that writing is ready to submit.

See `V3_OUTCOMES_REPORT.md` for baseline and improvement evidence, `V3_INVESTIGATION_EVIDENCE.md` for the consolidated evidence index, `CHANGELOG.md` for changes, and `EDUCATOR_REVIEW_PROTOCOL.md` for the pending educator gate.

## Local setup

Requires Python 3.11+; the project uses Python 3.12 locally.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Add your DeepSeek API key to `.env` and keep `DEEPSEEK_THINKING=false` for the selected local runtime. Never commit this file. Then run:

```bash
streamlit run app.py
```

The default database is `data/writing_assistant_v3.db`, which is git-ignored. Use only synthetic writing. Submitted text and context are sent to an external AI service and stored locally with execution details. Random session URLs filter history but are not authentication. **Delete my data** removes the current session's compositions, snapshots, reflections, execution records, and checkpoints.

## Tests

```bash
pytest
```

The current suite has **214 passing checks** using mocked model responses and temporary SQLite databases. The versioned student presets are in `test_cases/v3/scenarios.json`; the 32-scenario evaluation set is `test_cases/v3/acceptance.json`. The four root V1/V2 fixtures remain frozen.

## Real-model evaluation

With authorization for billable DeepSeek calls, run the paired core comparison and the non-thinking acceptance set:

```bash
python scripts/evaluate_v3.py --scenario-set core --modes nonthinking thinking
python scripts/evaluate_v3.py --scenario-set acceptance --modes nonthinking
```

The core comparison covers argument/source, source mismatch, missing source, RACES informational, narrative, human review, and a full garden revision/reflection loop. The acceptance set covers all 30 PRD scenarios plus a controlled short/long density pair. Outputs include structured responses, routes, errors, invalid final responses and validation errors for repairs, deduplicated model/graph/service timing and token usage, and stable database hashes after checkpoint/close in git-ignored files under `data/`. The student runtime uses explicit non-thinking mode and never switches modes automatically.

The current `v3.4.0` acceptance evidence is `data/evidence/v3_acceptance_evaluation_20261110T194146Z.json`, with targeted density artifacts and mixed findings documented in `V3_OUTCOMES_REPORT.md` Section 17. It is not a clean acceptance or pedagogical-quality claim.

The earlier completed pair used prompt/schema `v3.1.0` and is stored at `data/evidence/v3_paired_evaluation_20261110T094344Z.json`. All six scenarios completed in each mode. Thinking used 17 calls, including two schema repairs, 68,407 total tokens (24,926 reasoning tokens), and 246.2 seconds of cumulative model latency. Non-thinking used 15 calls, no repairs, 36,340 total tokens, and 64.2 seconds. These results supported the 2026-11-10 non-thinking runtime decision; they are not a general quality or learner-outcome conclusion.

A real browser walkthrough at 1280px verified the complete select–edit–review–next-round–finish loop, including exact highlights and stale-highlight removal. Captures are git-ignored under `data/evidence/v3_local_*`. These synthetic checks do not establish educator approval, pedagogical effectiveness, or learner outcomes.

`EDUCATOR_REVIEW_PROTOCOL.md` provides the full-context three-educator walk-through protocol. Recruitment, reviewer assessments, and the gate decision remain pending.

## Configuration

`.env.example` documents the model, explicit thinking flag, reasoning-effort, timeout, database, evaluator-control display, debug, and neutral small-change threshold settings. The student header omits developer/observability reveal controls unless `SHOW_EVALUATION_CONTROLS=true`; each panel then remains independently hidden until selected. Non-thinking runtime requests use temperature 0, while controlled thinking requests omit temperature. Prompt/schema/fixture versions and authorized model metadata are recorded with reviews; raw hidden reasoning is never stored or shown. Final prompt/response capture requires evaluator controls, server-side `ENABLE_DEBUG_MODE=true`, and separate opt-in for new reviews.

## Historical V1/V2 record

`PRD.md` remains the authoritative V1/V2 coursework and evidence record. V1 is preserved at commit `4eaa0ad` under the annotated `v1` tag. The historical post-JeepyTA V2 deployment is at `https://writingassist-zhuang.streamlit.app` from commit `7d94b58`; this local V3 implementation is not deployed. The authoritative coursework submission remains `submission/Applied_Assignment_4_Concise_user_edited.md` and its visually verified PDF.
