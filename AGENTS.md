# AGENTS.md

Guidance for AI coding agents working in this repository. Keep documentation and user-facing text in English.

## Project Overview

This is a synthetic-writing prototype for students in grades 5–7 (ages 10–13). V3 is an iterative academic revision coach for multilingual learners. Two LangGraph agents provide genre-sensitive assessment, student-authored revision guidance, clarification, simulated teacher review, and original-to-final reflection. It is not a grader, essay writer, ELPAC predictor, or production system for minors.

The detailed product contract is `PRD_V3_ITERATIVE_REVISION.md`. `PRD.md` preserves the authoritative V1/V2 coursework record and evidence.

## Current Repository Status

- V3 is the active local application. The old V1/V2 runtime paths were intentionally replaced; V1 remains available at commit `4eaa0ad` under the annotated `v1` tag.
- The current suite has **172 passing checks** using mocked model calls and temporary SQLite databases.
- A real prompt/schema `v3.1.0` thinking-mode browser walkthrough at 1280px covered scenario loading, initial review, two-goal selection/deselection, exact highlights, stale-highlight removal, two titled revision observations, next-round navigation, finish cancellation/confirmation, and final reflection. Evidence is `data/evidence/v3_browser_verification_20261110.json`, with git-ignored captures in `data/evidence/v3_local_*` and browser database `data/v3_browser_verification.db`.
- The completed prompt/schema `v3.1.0` paired evaluation is `data/evidence/v3_paired_evaluation_20261110T094344Z.json`. Six scenarios completed per mode with no scenario errors. Thinking used 17 calls/two repairs/68,407 tokens/246.2 seconds of cumulative model latency; non-thinking used 15 calls/no repairs/36,340 tokens/64.2 seconds. This limited sample shows higher thinking cost and no schema-reliability advantage, not a general pedagogical-quality conclusion.
- Current prompt/schema are `v3.3.0`/`v3.2.1` with explicit non-thinking runtime. Improvement evidence includes the 30-scenario set, targeted #7/#24 corrections, two additional paired cores, and `data/evidence/v3_improvement_browser_20261110.json`. See `V3_OUTCOMES_REPORT.md` Section 16 and `CHANGELOG.md`. The educator gate and actual screen-reader/full-keyboard final-loop checks remain open.
- The public Streamlit deployment remains the historical post-JeepyTA V2 app at commit `7d94b58`. Local V3 changes are not deployed and must not be described as deployed.
- V1/V2 outcomes remain in `PRD.md` Sections 7.5–7.7 and their preserved git-ignored evidence. The concise coursework submission remains `submission/Applied_Assignment_4_Concise_user_edited.md` and its verified PDF.

Do not claim pedagogical effectiveness, learner outcomes, educator approval, rubric completion, or performance targets without corresponding evidence. Design and synthetic-output evidence do not establish learner motivation, engagement, or achievement.

## Repository Map

- `PRD_V3_ITERATIVE_REVISION.md`: V3 product and technical requirements.
- `PRD.md`: Historical V1/V2 specification and authoritative evidence record.
- `project_plan.md`: Historical assignment strategy with a current-implementation note.
- `CLAUDE.md`: Detailed V3 coding guidance and historical evidence boundaries.
- `test_cases/`: Four frozen V1/V2 fixtures at the root; do not edit them. `test_cases/v3/scenarios.json` contains student presets and `test_cases/v3/acceptance.json` contains the 30-scenario evaluation set.
- `mockups/v3_iterative_revision.html`: Design reference only, not working behavior evidence.
- `scripts/evaluate_v3.py`: Explicit, billable real-model evaluation runner with final-response repair diagnostics.
- `V3_INVESTIGATION_EVIDENCE.md`: Index for the consolidated, hashed evidence manifest and prioritized investigation leads.
- `EDUCATOR_REVIEW_PROTOCOL.md`: Prepared full-context educator walk-through protocol; recruitment, assessments, and gate decision remain pending.
- `V3_IMPROVEMENT_OPPORTUNITIES.md`: External review input, not an authoritative current specification; validated corrections and resulting outcomes are in `V3_OUTCOMES_REPORT.md` Section 16 and the investigation manifest.
- `CODE_REVIEW.md`, `CORRECTED_FIX_LIST.md`, `FIX_APPLICATION_REVIEW*.md`, `PROMPT_*.md`, `REVIEW_*.md`, and `V3_PRD_IMPROVEMENT_ANALYSIS.md`: Historical development/design records only; current code and the V3 PRD supersede old behavior descriptions.
- `submission/`: Historical coursework artifacts; review records are not current V3 behavior evidence.

When architecture or development rules change, keep `PRD.md`, `project_plan.md`, `CLAUDE.md`, and this file consistent with actual code.

## Technology and Commands

Python 3.11+ is required; the local environment uses Python 3.12. LangGraph 1.2+, Streamlit 1.66+, Pydantic, direct `requests` HTTP calls, and SQLite are used. LangChain Core is transitive, not a separate agent wrapper.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Add DEEPSEEK_API_KEY locally
pytest
streamlit run app.py
```

Run pytest after each implementation stage. No formatter, linter, or type-checker is configured. The default API timeout is 120 seconds. Drafts and source material have explicit 16,000-character limits; no input is silently truncated.

## Agent and Graph Architecture

Preserve the two model-driven agents unless real evidence supports an architecture change:

1. **Assessment Coordinator**
   - Performs human-review assessment before other routing on every initial and revision submission.
   - Resolves explicit or working genre, applies genre-specific criteria, checks source boundaries, compares selected goals, and identifies meaningful issues/regressions.
   - Produces validated structured findings, exact draft references, concise final-output rationale, and routing.
   - In final mode, produces grounded original/final comparison findings from a deterministic diff.
2. **Instructional Support Agent**
   - Converts Coordinator findings into warm, specific, grade-appropriate feedback.
   - Pregenerates bounded hints, vocabulary considerations, abstract sentence starters, and stuck steps without supplying target responses.
   - Produces final motivational reflection only from verified Coordinator findings.
   - Does not own routing, add unrelated issues, or weaken source limitations.

```text
Initial or revision submission -> Assessment Coordinator -> conditional route
    |- ask_clarification -> interrupt -> answer -> Assessment Coordinator
    |- support_agent -> candidates + pregenerated scaffolds -> END
    |- teacher_review -> separate student/evaluator outputs -> END
    `- direct_response -> affirm without forced criticism -> END

Finish confirmation -> deterministic original/final diff -> Coordinator -> Support -> END
```

Clarification uses exact LangGraph interrupt/resume, stable thread IDs, and SQLite checkpoints. After two unclear answers, the next clarification request becomes non-safety teacher review with category `clarification_limit`. Clarification, direct response, teacher review, diffs, milestones, and workflow state are deterministic services/nodes, not additional agents.

### State and Routing Contract

The authoritative schema is `langgraph_core/state.py`.

- Routes are `ask_clarification`, `support_agent`, `teacher_review`, and `direct_response`. `flag_teacher` overrides the enum; malformed routes fall back to clarification.
- V3 has no affect field or dedicated affect check-in. Support-button use is presentation only and never emotion or effort evidence.
- `source_material_available` is set deterministically from actual input. Source-dependent findings require `source_location`; source-missing accuracy claims are prohibited.
- Every issue and candidate has an exact `draft_reference`, 1-based `paragraph_number`, and `occurrence` within that paragraph. Invalid references trigger bounded repair.
- Each normal revision route must include exactly one observation per selected goal: `specific_improvement`, `improvement_not_yet_evident`, or `uncertain`. Do not infer attempt from a diff.
- Lists replace prior lists during graph replay; they do not use additive reducers. `coordinator_reasoning` is concise final-output rationale, never hidden chain-of-thought.
- Each agent invocation permits one bounded schema repair. Persistent Support failure produces no partial feedback. Model-call logs include authorized configuration, token counts, and per-call/repair latency.

## Storage, UI, and Versioning

- SQLite stores compositions, immutable submitted snapshots, rounds, final reflections, execution details, and LangGraph checkpoints.
- A snapshot is persisted before its model review. Snapshot updates are rejected by a database trigger; session deletion intentionally cascades all associated data.
- Random session IDs filter history and support restoration but are not authentication or secure isolation.
- Missing, reset, or corrupted storage produces a recovery view with copyable runtime editor text and no false restoration claim.
- The student UI uses Draft, Choose, Revise, and Reflect steps; read-only History is separate. Developer controls and observability are independently hidden by default.
- The desktop workspace is 60/40 with independently scrolling containers and visible actions. The custom Streamlit CCv2 editor synchronizes exact goal highlights with editing and scrolling without changing model-visible text.
- Focus selection, hints, **Show less feedback**, **I’m stuck**, editing, and diff generation make no model calls.
- Unchanged or small changes require neutral confirmation before snapshot/model work. Finish requires confirmation and compares only original and latest submitted snapshots.
- Raw final prompt/response capture requires server-side `ENABLE_DEBUG_MODE=true` and separate opt-in for new reviews. Raw hidden reasoning is never an authorized field.
- There is no runtime V1/V2/V3 selector. Deploy only after a separate explicit deployment and retest decision.

## Testing and Evidence Strategy

- Use the root V1/V2 frozen fixtures unchanged. V3 uses `test_cases/v3/scenarios.json`, version `v3.1.0`, for student-safe presets.
- Cover all three genres, source-present/source-missing behavior, genre correction, selected-goal observations, neutral small changes, clarification limits, human review, storage failure, restoration, deletion, and final grounding.
- Automated tests use mocked model responses and temporary databases. Real DeepSeek runs and browser captures are separate evidence.
- For representative paired evaluation, run `python scripts/evaluate_v3.py --modes thinking nonthinking`. This makes billable external calls and writes git-ignored evidence under `data/`. Do not run it without authorization.
- Following the representative comparison and the 2026-11-10 product decision, V3 student runtime uses explicit non-thinking, temperature-0 configuration. Thinking remains an explicit controlled comparator; the app never switches modes automatically.
- Report positive, null, and negative findings equally. Record schema repairs, failures, actual latency, and token usage. Educator review and learner-outcome studies remain separate gates.

## Configuration and Deployment

`.env.example` defines `DEEPSEEK_API_KEY`, `DEEPSEEK_API_BASE`, `DEEPSEEK_MODEL`, `DEEPSEEK_THINKING=false`, `DEEPSEEK_REASONING_EFFORT`, `DEEPSEEK_TIMEOUT_SECONDS`, `LOG_LEVEL`, `ENABLE_DEBUG_MODE`, `DATABASE_PATH`, and `SMALL_CHANGE_TOKEN_THRESHOLD`.

The historical V2 deployment at `https://writingassist-zhuang.streamlit.app` is from commit `7d94b58`; it is not V3. Cloud SQLite durability ends when the filesystem is replaced. Reliable cross-restart persistence beyond this prototype requires a separate durable-storage decision.

## Privacy, Safety, and Security

- Use only synthetic writing. Never use real student essays or confidential classroom records.
- UI warning: "Do not submit writing containing real names, schools, or personal information. This is a demo system — your input is sent to an external AI service."
- Prompts may contain original/previous/current drafts, grade, genre, assignment/source context, concerns, clarification history, selected goals, self-reports, diffs, and Coordinator findings. SQLite stores drafts, outputs, routes, execution details, and checkpoints.
- Removing names does not necessarily de-identify prose. Redact evidence artifacts.
- Never commit API keys, `.env`, Streamlit secrets, databases, evidence JSON, screenshots, or personally identifying information.
- Teacher handoff is simulated; no teacher is notified. Recommend sharing concerning writing with a teacher or trusted adult. Do not improvise keyword-only crisis detection, diagnoses, hotline numbers, or localized resources.
- COPPA/FERPA compliance, consent, production retention/de-identification, authentication, and a real review queue are outside this demo's scope.
