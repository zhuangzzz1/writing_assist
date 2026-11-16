# AGENTS.md

Guidance for AI coding agents working in this repository. Keep documentation and user-facing text in English.

## Project Overview

This is a synthetic-writing prototype for students in grades 5–7 (ages 10–13). V3 is an iterative academic revision coach for multilingual learners. Two LangGraph agents provide genre-sensitive assessment, student-authored revision guidance, clarification, simulated teacher review, and original-to-final reflection. It is not a grader, essay writer, ELPAC predictor, or production system for minors.

The detailed product contract is `PRD_V3_ITERATIVE_REVISION.md`. `PRD.md` preserves the authoritative V1/V2 coursework record and evidence.

## Current Repository Status

- V3 is the active application. Current local `main` is `cc4ca35`; local prompt/schema are `v3.8.3`/`v3.8.0` after the owner's explicit promotion decision, with v3.7.1/v3.7.0 preserved as evaluation controls, evaluation-only consolidated Support prompt `v3.7.2-consolidated`, preserved `v3.8.1-baseline-readable`, evaluation-only `v3.8.2-baseline-readable`, the preserved `v3.8.3-regression-readable` evaluation control, and an evaluation-only `structural_current` v3.8.0 wording control. The historical full acceptance artifacts used `v3.6.5`/`v3.6.3`. Student presets/acceptance fixtures are `v3.4.0`; the comparison uses 14 Support handoffs and 12 Coordinator-targeted scenarios with their recorded source-fixture versions. Track A feedback-quality and Track B severity changes remain; v3.8.0 removes the reasoning-operation classification together with its sentence-starter consumer. The old V1/V2 runtime paths were intentionally replaced; V1 remains at commit `4eaa0ad` under the annotated `v1` tag.
- The promoted local v3.8.3 implementation passes **372 mocked checks**; the pre-promotion targeted implementation passed 371 and the preserved v3.8.2 implementation passed 369 checks, including versioned Final-regression and adaptive-coverage fixtures. The earlier structural/readability baseline passed 350 checks, and the earlier prompt/contract Gate A baseline passed 325 on 2026-11-15. These counts do not erase real-model or human-review failures or establish semantic acceptance.
- Preserve the historical failed baselines `data/evidence/v3_acceptance_evaluation_20261115T091103Z.json` and `data/evidence/v3_acceptance_evaluation_20261115T113518Z.json`. Earlier real-model, exact-text-exception, SOTA, and Support-only outcomes are in `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` and `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md`; do not attribute operational differences to one prompt change or erase negative evidence.
- Historical consolidated/prompt-revision candidates have not passed Gates B and C: targeted and integrated semantic review found target-like vocabulary, strong-draft failures, an unsupported targeted Final regression, and a repeated revision/final consistency contradiction. The consolidated Support prompt remains evaluation-only. After the 2×2 pedagogical review, the user explicitly selected the Phase 1 baseline with thinking; the later v3.8.0 structural adoption removed vocabulary/starter generation locally without promoting readability or strong-draft candidate wording. Current outcomes and the external expert's do-not-promote decision are in `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`. V3.8.2 targeted Gate B is also not passed: F2 credit, imaginative Coordinator selection, and complete #9 regression preservation remain unresolved despite improved Support wording/F1; see `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`. V3.8.2 Gate C passes only for the seven-scenario versioned coverage set; integrated #15 adds another Final-credit omission, and full acceptance is unevaluated. The targeted v3.8.3 Final follow-up preserves F1/E and covers all three #9 loss types in one matched thinking run, using two findings with sequence/audit reasoning combined; F2 credit remains unresolved and Gate B remains not passed. The owner subsequently promoted v3.8.3 to the local default as an explicit product decision, not a semantic gate pass. A default-factory real-model check confirmed `v3.8.3`/`v3.8.0` with two calls and no repairs but omitted the tracking-purpose regression, so #9 behavior is mixed across runs. See Sections 8–9 of `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`. Full acceptance remains unevaluated; educator and actual screen-reader/full-keyboard checks remain open.
- The canonical Streamlit URL serves V3 for synthetic testing. A 2026-11-15 live initial-surface check verified footer marker `v04d61af` and the Draft–Choose–Revise–Reflect interface. The 2026-11-14 deployed browser log `data/evidence/v3_live_deployed_el_two_revision_rounds_20261114T181633Z.jsonl` covers five initial reviews and two revisions per essay, with one unconfirmed workflow interruption and no final reflection. Current working-tree changes are not deployed; do not infer that every live flow has been reverified. On 2026-11-16, a direct canonical request returned a 303 Streamlit-auth redirect, so current deployed behavior is unverified. A separate local process on port 8501 was explicitly launched with `DEEPSEEK_THINKING=true` on 2026-11-15 and still returns HTTP 200, but it predates the current structural changes; restart before current-code testing. The repository default is now local prompt `v3.8.3` with schema `v3.8.0` and thinking, following the owner's explicit promotion decision; the thinking-mode selection followed the 2×2 review.
- `V3_LIVE_EL_IMPROVEMENT_AND_TESTING_PLAN.md` is the implemented experiment-first investigation arising from that log. `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` records adopted changes, null/mixed outcomes, costs, and open gates.
- `V3_PROMPT_REVISION_AND_EVALUATION_PLAN.md` and `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md` preserve the earlier prompt/contract revision and its evidence. `V3_BASELINE_READABILITY_IMPROVEMENT_PLAN.md` and `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md` record the completed structural/readability experiment, external expert feedback, open gates, and rollback. `V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` is implemented as an evaluation-only candidate; its pedagogical, coverage, human-review, promotion, and deployment gates remain separate.
- V1/V2 outcomes remain in `PRD.md` Sections 7.5–7.7 and their preserved git-ignored evidence. The historical V2 deployment used commit `7d94b58`. The concise coursework submission remains `submission/Applied_Assignment_4_Concise_user_edited.md` and its verified PDF.

Do not claim pedagogical effectiveness, learner outcomes, educator approval, rubric completion, or performance targets without corresponding evidence. Design and synthetic-output evidence do not establish learner motivation, engagement, or achievement.

## Repository Map

- `PRD_V3_ITERATIVE_REVISION.md`: V3 product and technical requirements.
- `PRD.md`: Historical V1/V2 specification and authoritative evidence record.
- `project_plan.md`: Historical assignment strategy with a current-implementation note.
- `CLAUDE.md`: Detailed V3 coding guidance and historical evidence boundaries.
- `test_cases/`: Four frozen V1/V2 fixtures at the root; do not edit them. `test_cases/v3/scenarios.json` contains student presets, `test_cases/v3/acceptance.json` contains the 32-scenario evaluation set, and `test_cases/v3/live_el_contrasts.json` contains the versioned targeted experiment set with controlled prefixes and Support-only handoffs. `prompt_revision_support.json` adds eight handoffs to six preserved Support handoffs for the 14-case 2×2; `prompt_revision_coordinator.json` adds ten scenarios to the preserved strong-draft and imaginative cases for the 12-case Coordinator set. `final_history_contrasts.json` contains two versioned controlled-prefix Final-history probes. `final_regression_contrasts.json` adds four v3.8.2 Final credit/consistency/regression anchors; `readability_coverage.json` adds seven v3.8.2 successors with adaptive goal selection, a valid direct-response Finish alternative, and independent controlled coverage.
- `mockups/v3_iterative_revision.html`: Original design reference. `mockups/v3_redesign.html`: Redesign mockup produced during the UI/UX improvement pass; the implemented changes are in `ui/layout.py`. Neither is working behavior evidence.
- `scripts/evaluate_v3.py`: Real-model evaluation runner with usage/cost records, explicit goal selectors, evaluation-only GC/SA/FG/CQ arms, consolidated Support, `baseline_readable`, `baseline_readable_v2`, `regression_readable`, `structural_current`, adaptive/controlled coverage selectors, isolated clarification probes, final-response repair diagnostics, deduplicated operational and descriptive readability metrics, normalization counts, and stable database hashes after checkpoint/close. `scripts/readability_metrics.py` implements sentence-length, 38-word-action, repetition, and action/self-check human-review heuristics without a quality score. `scripts/analyze_repairs.py` categorizes deduplicated validation failures and preserved failed attempts without treating repair counts as a quality score.
- `V3_INVESTIGATION_EVIDENCE.md`: Index for the historical consolidated evidence manifest and prioritized investigation leads; live WAL databases require stable capture before hashing.
- `V3_PROMPT_REVIEW_VALIDATION_AND_ACTION_PLAN.md`: Historical validated design/action record for the implemented V3.4.0 changes; not the current open investigation plan.
- `V3_LIVE_EL_IMPROVEMENT_AND_TESTING_PLAN.md`: Experiment-first investigation from the 2026-11-14 deployed EL review. `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` records implementation, positive/null/mixed outcomes, and open human gates.
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
   - Produces validated structured findings, framework-neutral coverage for explicit teacher requirements, exact draft references, concise final-output rationale, and routing.
   - In final mode, produces grounded original/final comparison findings from a deterministic diff.
2. **Instructional Support Agent**
   - Converts Coordinator findings into warm, specific, grade-appropriate feedback.
   - Pregenerates bounded hints and stuck steps without supplying target responses. The local v3.8.3 runtime retains the v3.8.0 schema and does not generate vocabulary lists or sentence starters.
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

Clarification uses exact LangGraph interrupt/resume, stable thread IDs, and SQLite checkpoints. The Coordinator model may select only `none`, `concerning_content`, or `serious_discouragement`; a model-selected `clarification_limit` is neutralized rather than honored or relabeled. An explicit `teacher_review` with category `none` returns to clarification instead of being misclassified as concerning content. Only the deterministic graph creates `clarification_limit` after two unclear answers. Clarification, direct response, teacher review, diffs, milestones, and workflow state are deterministic services/nodes, not additional agents.

### State and Routing Contract

The authoritative schema is `langgraph_core/state.py`.

- Routes are `ask_clarification`, `support_agent`, `teacher_review`, and `direct_response`. `flag_teacher` overrides the enum; malformed routes fall back to clarification.
- Clarification and teacher review return empty `strengths`, `issues`, `framework_coverage`, `source_limitations`, and `selected_goal_observations`. Teacher review may leave `working_genre`, `genre_confidence`, and `genre_basis` empty; unrelated clarification need not empty genre fields.
- On initial and revision routes, the Coordinator owns accuracy-first, supported-concern-next, then severity/pedagogical ordering. Python performs only a stable accuracy partition and otherwise preserves Coordinator order; no concern-specific field was added. Support preserves the resulting candidate order.
- V3 has no affect field or dedicated affect check-in. Support-button use is presentation only and never emotion or effort evidence.
- `framework_name` and `framework_components` are deterministic optional inputs. Coordinator `framework_coverage` maps every commissioned `(framework, component)` pair to an exact present reference or existing issue goal; Support only renders the handoff.
- Explicit genre selections are normalized deterministically without mismatch-only repair.
- `source_material_available` is set deterministically from actual input. Source-dependent findings require `source_location`; source-missing accuracy claims are prohibited.
- Every issue and candidate has an exact `draft_reference`, 1-based `paragraph_number`, and `occurrence` within that paragraph. An invalid location for an exact globally unique issue reference receives a recorded deterministic correction; analogous recovery applies only to unique, single-block `present` framework references and records framework/component identity separately. Ambiguous, repeated, missing, or cross-paragraph references trigger bounded repair. Final references are never normalized.
- Optional-language mechanics goals use a structured `obscures_meaning` judgment rather than description keywords.
- Each normal revision route must include exactly one observation per selected goal: `specific_improvement`, `improvement_not_yet_evident`, or `uncertain`. Do not infer attempt from a diff.
- Hints contain 3–5 total items: one concept restatement followed by 2–4 procedural steps.
- Lists replace prior lists during graph replay; they do not use additive reducers. `coordinator_reasoning` is concise final-output rationale, never hidden chain-of-thought.
- Optional `prior_findings` exists only for the evaluation-only Arm C round graph path. Production constructors do not populate or inject it. Separately, the v3.8.0 Final path declares and populates `revision_history` from persisted snapshots and matching successful Coordinator reviews, with exact goal references, authoritative observations, snapshot/review IDs, and draft hashes. Older missing observations remain empty rather than inferred.
- Final deterministic consistency rejection requires a matching latest draft hash, goal ID, and exact unchanged goal reference after `improvement_not_yet_evident` or `uncertain`; goal ID alone and empty Final goal IDs are not inferred. Deletion-worded regressions are rejected only when their exact original reference remains verbatim in Final. Semantic weakening requires model/human review.
- Local v3.8.3 retains the v3.8.0 removals of `vocabulary_options`, `sentence_starter`, and Coordinator `reasoning_operation` from prompts and output models. Versioned v3.7.x evaluation controls retain separate legacy contracts. Completion placeholders in instructional fields trigger bounded repair; exact quoted draft ellipses used only for locating are not completion placeholders. These structural checks do not replace semantic authorship review.
- Each agent invocation permits one bounded schema repair. Persistent Support failure produces no partial feedback. Model-call logs include authorized configuration, token counts, and per-call/repair latency.

## Storage, UI, and Versioning

- SQLite stores compositions, immutable submitted snapshots, rounds, final reflections, execution details, framework fields, and LangGraph checkpoints. Existing databases receive additive framework columns without resetting history.
- A snapshot is persisted before its model review. Snapshot updates are rejected by a database trigger; session deletion intentionally cascades all associated data.
- Random session IDs filter history and support restoration but are not authentication or secure isolation.
- Missing, reset, or corrupted storage produces a recovery view with copyable runtime editor text and no false restoration claim.
- The student UI uses header-based Draft, Choose, Revise, and Reflect steps with action-based completed states; read-only History is separate. Evaluator reveal controls require `SHOW_EVALUATION_CONTROLS=true`, and developer controls and observability then remain independently hidden until selected.
- The desktop workspace is 60/40 with independently scrolling containers and visible actions. Page, editor, feedback, and reflection sizes use viewport-relative bounds rather than fixed desktop-only dimensions; minimum and maximum limits preserve readability. The custom Streamlit CCv2 editor synchronizes exact goal highlights with editing and scrolling without changing model-visible text. Identical, nested, and transitively overlapping references share a union highlight with goal membership and textual labels; this is not semantic duplication evidence.
- Choose initially presents one recommended goal with a choose-only action; alternatives are revealed on request and grouped into idea/reasoning/organization and optional sentence polishing. Focus selection, choice reveal/hide, hints, **Show less feedback**, **I’m stuck**, editing, and diff generation make no model calls.
- Unchanged or small changes require neutral confirmation before snapshot/model work. Finish requires confirmation and compares only original and latest submitted snapshots. If final reflection fails, close the Finish dialog and expose the saved failed reflection and retry without losing drafts or creating snapshots.
- Raw final prompt/response capture requires server-side `ENABLE_DEBUG_MODE=true` and separate opt-in for new reviews. Raw hidden reasoning is never an authorized field.
- There is no runtime V1/V2/V3 selector. Deploy only after a separate explicit deployment and retest decision.

## Testing and Evidence Strategy

- Use the root V1/V2 frozen fixtures unchanged. V3 uses `test_cases/v3/scenarios.json`, version `v3.4.0`, for student-safe presets.
- Cover all three genres, source-present/source-missing behavior, genre correction, known/custom frameworks, negated directions, selected-goal observations, neutral small changes, overlap groups, clarification limits, human review, storage failure/migration, restoration, deletion, final grounding, and controlled density fixtures.
- Automated tests use mocked model responses and temporary databases. Real model runs and browser captures are separate evidence.
- The project owner gives standing authorization for billable real-model calls, including thinking and SOTA comparisons, without separate per-run approval or a required token stop cap. On 2026-11-15, the owner also chose to remove mandatory model-call caps, but that code change is pending: the current evaluator still requires `--authorization-id`, `--approver`, and `--max-model-calls`. Use the existing flags until the runner changes. For representative paired evaluation, use `scripts/evaluate_v3.py` with `--modes thinking nonthinking`; see `README.md` for current command-line syntax. Runs write git-ignored evidence under `data/`. Deduplicate cumulative execution logs by `(thread_id, node, timestamp)` and checkpoint/close databases before stable hashing. Failed validations retain bounded final prompt/response attempts without hidden reasoning; empty/API failures can occur before that capture and require the observability limitations recorded in the results.
- Evaluation-only `--provider sota` supports `claude-opus-5-5` through native Anthropic Messages thinking and `gemini-4-argon` through native Gemini `generateContent` thinking. It uses `SOTA_API_KEY`, `SOTA_BASE_URL`, and `SOTA_TIMEOUT_SECONDS` and filters provider thinking blocks. Protocol-required per-request output fields remain supported. This path does not change student runtime.
- Following the user's explicit decision after the 2×2 pedagogical review, V3 student runtime defaults to the v3.8.0 structural contract with thinking, omitting temperature and using configured reasoning effort. Non-thinking remains an explicit controlled comparator with temperature 0. The app never switches modes automatically or falls back after errors. The earlier non-thinking runtime decision is superseded; local `.env` overrides still take precedence.
- Report positive, null, and negative findings equally. Assess implementation performance primarily with `EDUCATOR_REVIEW_PROTOCOL.md`: Meets / Needs refinement / Unacceptable, Critical / Major / Moderate / Minor, and concrete output evidence. Calls, tokens, latency, repairs, and surface metrics are secondary diagnostics, not quality rankings. LLM-assisted rubric screening is not educator approval. Record operational diagnostics for reproducibility. Educator review and learner-outcome studies remain separate gates.

## Configuration and Deployment

`.env.example` defines `DEEPSEEK_API_KEY`, `DEEPSEEK_API_BASE`, `DEEPSEEK_MODEL`, `DEEPSEEK_THINKING=true`, `DEEPSEEK_REASONING_EFFORT`, `DEEPSEEK_TIMEOUT_SECONDS`, evaluation-only `SOTA_API_KEY`, `SOTA_BASE_URL`, `SOTA_TIMEOUT_SECONDS`, `LOG_LEVEL`, `SHOW_EVALUATION_CONTROLS`, `ENABLE_DEBUG_MODE`, `DATABASE_PATH`, and `SMALL_CHANGE_TOKEN_THRESHOLD`.

The canonical URL `https://writingassist-zhuang.streamlit.app` serves V3 for synthetic testing. Its initial V3 surface and footer `v04d61af` were live-verified on 2026-11-15; the marker comes from `version.txt` and does not prove that current HEAD or every flow is deployed and verified. The historical V2 deployment used commit `7d94b58`. Cloud SQLite durability ends when the filesystem is replaced. Reliable cross-restart persistence beyond this prototype requires a separate durable-storage decision.

## Privacy, Safety, and Security

- Use only synthetic writing. Never use real student essays or confidential classroom records.
- UI warning: "Do not submit writing containing real names, schools, or personal information. This is a demo system — your input is sent to an external AI service."
- Prompts may contain original/previous/current drafts, grade, genre, assignment/source context, concerns, clarification history, selected goals, self-reports, diffs, and Coordinator findings. SQLite stores drafts, outputs, routes, execution details, and checkpoints.
- Removing names does not necessarily de-identify prose. Redact evidence artifacts.
- Never commit API keys, `.env`, Streamlit secrets, databases, evidence JSON, screenshots, or personally identifying information.
- Teacher handoff is simulated; no teacher is notified. Recommend sharing concerning writing with a teacher or trusted adult. Do not improvise keyword-only crisis detection, diagnoses, hotline numbers, or localized resources.
- COPPA/FERPA compliance, consent, production retention/de-identification, authentication, and a real review queue are outside this demo's scope.
