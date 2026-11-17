# Writing Coach — V3 Iterative Revision

A synthetic-classroom prototype for grades 5–7. Two LangGraph agents provide genre-sensitive assessment and bounded revision support while the student preserves authorship: choose one to three goals, edit the complete draft, submit immutable revision snapshots, repeat or stop, and finish with a grounded original-to-final reflection.

V3 supports argument, informational, and narrative writing; optional assignment/source context; structured CER/RACE/RACES/MEAL or custom framework requirements; Coordinator-owned framework coverage; correctable genre inference; one recommended revision goal with on-demand alternatives and separate optional sentence polishing; exact and overlap-grouped goal highlights; pregenerated hints; neutral small-change handling; clarification and simulated teacher review; read-only history; session restoration/deletion; and opt-in developer observability. It does not assign grades, predict ELPAC/SBAC outcomes, write replacement responses, or claim that writing is ready to submit.

See `V3_OUTCOMES_REPORT.md` for baseline and improvement evidence, `V3_INVESTIGATION_EVIDENCE.md` for the consolidated evidence index, `CHANGELOG.md` for changes, and `EDUCATOR_REVIEW_PROTOCOL.md` for the pending educator gate. `V3_LIVE_EL_IMPROVEMENT_AND_TESTING_PLAN.md` is the experiment-first follow-up to the 2026-11-14 deployed EL review; `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` records adopted changes, null/mixed outcomes, evidence, and open gates. `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md` preserves the earlier prompt/contract revision and diagnostics. `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md` records the structural contract, v3.8.1 candidate, targeted evaluation, and rollback path. `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md` is the authoritative latest experiment record; `V3_8_2_READABILITY_AND_FINAL_EXPERT_REVIEW.md` is its self-contained review packet. `V3_PHASED_IMPROVEMENT_PLAN.md` defines the current phased work; `V3_PHASE1_IMPLEMENTATION_RESULTS.md` records the evaluation-only Phase 1 implementation, verification, evidence, and open semantic gates.

## Local setup

Requires Python 3.11+; the project uses Python 3.12 locally.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Add your DeepSeek API key to `.env`. The repository default is now `DEEPSEEK_THINKING=true`, explicitly selected by the user after the 2×2 pedagogical review. If your local `.env` pins `DEEPSEEK_THINKING=false`, that override takes precedence and must be changed to `true` to use the new default. Never commit this file. Then run:

```bash
streamlit run app.py
```

The default database is `data/writing_assistant_v3.db`, which is git-ignored. Use only synthetic writing. Submitted text and context are sent to an external AI service and stored locally with execution details. Random session URLs filter history but are not authentication. **Delete my data** removes the current session's compositions, snapshots, reflections, execution records, and checkpoints.

## Tests

```bash
pytest
```

The current working tree passes **476 mocked checks**, including the evaluation-only Phase 1 contract and preserved default tests. The promoted local v3.8.3 implementation historically passed **372 mocked checks**; the pre-promotion targeted implementation passed 371, the preserved v3.8.2 implementation passed 369, the earlier structural/readability baseline passed 350, and the earlier prompt/contract Gate A baseline passed 325. Tests use mocked model responses and temporary SQLite databases. The versioned student presets are in `test_cases/v3/scenarios.json`; the 32-scenario evaluation set is `test_cases/v3/acceptance.json`, and targeted live-EL experiments use `test_cases/v3/live_el_contrasts.json`. The prompt-revision comparison adds 14 frozen Support handoffs and 12 Coordinator-targeted scenarios through `prompt_revision_support.json`, `prompt_revision_coordinator.json`, and the preserved strong-draft/imaginative fixtures. Versioned v3.8.2 successors add four Final-regression contrasts and seven adaptive/controlled coverage scenarios without editing historical fixtures. The four root V1/V2 fixtures remain frozen.

## Real-model evaluation

The project owner gives standing authorization for billable runs, including thinking and SOTA comparisons, without separate per-run approval or a required token stop cap. Actual usage is still recorded. The evaluator requires `--authorization-id` and `--approver`. `--max-model-calls` is now optional: when omitted, the runner estimates base calls from selected fixtures and adds `--repair-headroom` (default 2), recording the effective budget. An explicit maximum remains a hard cap. For controlled `phase2_lean` DeepSeek thinking comparisons, `--support-reasoning-effort low|high|max` keeps Coordinator at high and records the selected Support effort. The current student default instead uses the latest lean contract with low effort for both agents. Non-thinking remains an explicitly selected comparator.

```bash
python scripts/evaluate_v3.py \
  --scenario-set acceptance --modes nonthinking \
  --authorization-id <record-id> --approver <project-owner> \
  --max-model-calls 160 --max-total-tokens 1500000

python scripts/evaluate_v3.py \
  --scenario-set live_el --scenario-number 10 --experiment-arm current \
  --authorization-id <record-id> --approver <project-owner> \
  --max-model-calls 4 --max-total-tokens 50000

# Phase 1 baseline versus evaluation-only consolidated Support prompt, both modes.
python scripts/evaluate_v3.py \
  --scenario-set support_prompt --modes nonthinking thinking \
  --experiment-arm current \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 40
python scripts/evaluate_v3.py \
  --scenario-set support_prompt --modes nonthinking thinking \
  --experiment-arm support_consolidated \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 40

# v3.7.1 control versus the reviewed v3.8.1 readability candidate; thinking-only targeted review.
python scripts/evaluate_v3.py \
  --scenario-set support_prompt --modes thinking --experiment-arm current \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 35
python scripts/evaluate_v3.py \
  --scenario-set support_prompt --modes thinking --experiment-arm baseline_readable \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 35

# Controlled Final-history probes; use --reruns-covered when the targeted authorization includes reruns.
python scripts/evaluate_v3.py \
  --scenario-set final_history --modes thinking --experiment-arm current \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 12
python scripts/evaluate_v3.py \
  --scenario-set final_history --modes thinking --experiment-arm baseline_readable \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 12

# v3.8.2 targeted wording/Final review and, only after rubric review, coverage successors.
python scripts/evaluate_v3.py \
  --scenario-set support_prompt --modes thinking --experiment-arm structural_current \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 32
python scripts/evaluate_v3.py \
  --scenario-set final_regression --modes thinking --experiment-arm baseline_readable_v2 \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 20
python scripts/evaluate_v3.py \
  --scenario-set readability_coverage --modes thinking --experiment-arm baseline_readable_v2 \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 48

# v3.8.3 targeted contextual purpose-loss regression follow-up; v3.8.2 remains the control.
python scripts/evaluate_v3.py \
  --scenario-set final_regression --modes thinking --experiment-arm regression_readable \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 20

# Coordinator targets; the adversarial early-limit arm is valid only for scenario 3.
python scripts/evaluate_v3.py \
  --scenario-set coordinator_targeted --modes nonthinking thinking \
  --experiment-arm current \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 90
python scripts/evaluate_v3.py \
  --scenario-set coordinator_targeted --scenario-number 3 \
  --modes nonthinking thinking --experiment-arm coordinator_early_limit \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 4
python scripts/evaluate_v3.py \
  --scenario-set coordinator_targeted --scenario-number 4 \
  --modes nonthinking thinking --experiment-arm coordinator_clarification_probe \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 6

# Phase 1 whole-draft/outcome candidate: controlled development single turns.
python scripts/evaluate_v3.py \
  --scenario-set phase1_development --modes thinking --experiment-arm phase1 \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 64

# Lean Support structural candidate on the same development inputs; automatic base + 2 repair slots.
python scripts/evaluate_v3.py \
  --scenario-set phase1_development --scenario-number 2 \
  --modes thinking --experiment-arm phase2_lean --repair-headroom 2 \
  --authorization-id <record-id> --approver <project-owner>

# Exploratory split effort: Coordinator high, Support low; no runtime change.
python scripts/evaluate_v3.py \
  --scenario-set phase1_development --scenario-number 2 \
  --modes thinking --experiment-arm phase2_lean --support-reasoning-effort low \
  --repair-headroom 2 --authorization-id <record-id> --approver <project-owner>

# Targeted development branches; real execution requires available provider balance.
python scripts/evaluate_v3.py \
  --scenario-set phase2_branches --modes thinking --experiment-arm phase2_lean \
  --repair-headroom 4 --authorization-id <record-id> --approver <project-owner>

# Existing acceptance regressions 1-3, 10, 23, and 26; Final is explicitly skipped for this round-only check.
python scripts/evaluate_v3.py \
  --scenario-set acceptance --scenario-numbers 1 2 3 10 23 26 \
  --modes thinking --experiment-arm phase1 --skip-final \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 24

# Reserved transfer set: use only after freezing the candidate prompt, schema, and deterministic logic.
python scripts/evaluate_v3.py \
  --scenario-set phase1_transfer --modes thinking --experiment-arm phase1 \
  --candidate-frozen \
  --authorization-id <record-id> --approver <project-owner> --max-model-calls 32

# Deduplicated repair-cause analysis, separately from quality judgments.
python scripts/analyze_repairs.py <preserved-artifact.json> [<artifact-2.json> ...] \
  --output data/evidence/<repair-analysis.json>

# Separately authorized native-protocol SOTA comparison; omit the token cap only when authorized.
python scripts/evaluate_v3.py \
  --provider sota --model claude-opus-5-5 --modes thinking \
  --scenario-set acceptance --scenario-numbers 1 3 8 10 15 22 30 \
  --authorization-id <record-id> --approver <project-owner> \
  --max-model-calls 40
```

The `phase1` arm selects the `v3.9.5-phase1` prompt and `v3.9.0` schema; its Coordinator contract is also incorporated into the current lean student default. `phase1_development` contains 16 controlled initial/revision probes derived from the preserved garbage-system run plus independent argument/source and narrative cases. `phase1_transfer` contains eight unrelated synthetic cases and requires `--candidate-frozen`; if its outputs drive candidate changes, it becomes development data and new held-out cases are required. `--skip-final` is restricted to Phase 1-family (`phase1` and `phase2_lean`) round-only acceptance regressions and is recorded in evidence. Phase 1 outputs add descriptive goal-outcome, narrowing, carry-forward, optional-polish, and stopping-route diagnostics alongside repairs and exact-reference diagnostics. These counts are not semantic quality scores. No adaptive multi-round replay or completed Final-semantic evaluation has yet validated this candidate. V3.9.5 adds bounded unattributed-claim accuracy rules, revision concern rechecks, and a normal one-to-three issue density target with accuracy/requirement exceptions. Its candidate-only Final prompts still require full real-model evaluation and named semantic review beyond the recorded smoke.

The promoted `phase2_lean` arm selects the current default prompt `v3.10.1-phase2-lean` and schema `v3.10.0`. Support returns only IDs and student-facing prose; Python deterministically attaches all exact Coordinator references, source limitations, observation state, and Final references before full validation and persistence. Raw model outputs are lean, while stored/UI outputs retain their existing full shape. Use `--experiment-arm phase2_lean` with the same development or acceptance inputs for matched evaluation. This structural arm does not implement Phase 2 batching or bounded history.

The core comparison covers argument/source, source mismatch, missing source, RACES informational, narrative, human review, and a full garden revision/reflection loop. The acceptance set covers all 30 PRD scenarios plus a controlled short/long density pair. The `live_el` set supports explicit goal subsets, controlled prefixes, Support-only handoffs, and current/GC/SA/FG/CQ experiment arms. `support_prompt` holds the 14-handoff Phase 1-versus-consolidated 2×2 comparison; `coordinator_targeted` holds 12 routing/location/final-grounding scenarios, with the early-limit adversarial probe restricted to scenario 3. `final_history` holds two controlled-prefix unchanged-goal/later-start Final probes in `final_history_contrasts.json`. `final_regression` adds four v3.8.2 controlled-history anchors for F1/F2 credit, unchanged-goal consistency, and genuine organization regression. `readability_coverage` holds seven versioned #15/#20/#24/clarification/human-review successors; `all_available` selects one to three actual candidates, and #20 explicitly permits a no-revision Finish after direct_response without forcing a route. `baseline_readable_v2` selects v3.8.2, `regression_readable` selects the v3.8.3 contextual purpose-loss Final follow-up while preserving v3.8.2's round/Support prompts, and `structural_current` selects the preserved v3.8.0 prompts as a wording control. The current consolidated arm records `v3.7.2-consolidated` without changing the production prompt; the targeted comparison preserved `v3.7.1-consolidated` artifacts. Outputs include structured responses, routes, errors, invalid final responses and validation errors for repairs, deduplicated model/graph/service timing and token usage, issue/framework normalization counts, descriptive sentence-length/38-word-action/repetition/action-self-check readability metrics, authorization/budget records, and stable database hashes after checkpoint/close in git-ignored files under `data/`. Implementation performance is assessed primarily with `EDUCATOR_REVIEW_PROTOCOL.md` ratings and severity, using concrete output evidence. Readability flags and calls/tokens/latency/repairs are secondary diagnostics, not quality scores or educator approval. The current student runtime uses prompt `v3.10.1-phase2-lean` with schema `v3.10.0` and thinking after the owner's latest-default decision; v3.7.1/v3.7.0 remain evaluation controls, `v3.8.1-baseline-readable` is preserved, `v3.8.2-baseline-readable` remains evaluation-only, and `v3.8.3-regression-readable` remains available as a preserved evaluation control. Thinking omits temperature; explicit non-thinking comparisons use temperature 0. The owner-selected current default uses low reasoning effort for both Coordinator and Support (`DEEPSEEK_REASONING_EFFORT=low` and `DEEPSEEK_SUPPORT_REASONING_EFFORT=low`). The app never switches modes automatically. A separate local process on port 8501 was explicitly launched with `DEEPSEEK_THINKING=true` on 2026-11-15; this process override does not change the default or deployed app.

The targeted v3.8.3 Final follow-up is recorded in `data/evidence/v3_final_regression_regression_readable_evaluation_20261116T154531Z.json`: four matched thinking scenarios completed with eight calls, zero errors, and zero repairs. Its two #9 regression findings cover all three loss types—sequence and audit-to-choice reasoning combined, plus tracking purpose—where v3.8.2 omitted the tracking-purpose loss. F1 restraint and E consistency remain intact; F2 still withholds genuine improvement credit. The owner subsequently promoted v3.8.3 to the local default. A separate default-factory check in `data/evidence/v3_final_regression_runtime_default_scenario_04_evaluation_20261116T160207Z.json` confirmed `v3.8.3`/`v3.8.0` with two calls, zero errors, and zero repairs, but omitted the tracking-purpose regression. Regression handling is therefore mixed across runs, and Gate B remains not passed. See Sections 8–9 of `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`.

The current integrated diagnostic is `data/evidence/v3_acceptance_support_consolidated_evaluation_20261115T160443Z.json`: arm `v3.7.2-consolidated`, schema `v3.7.0`, and 32 scenarios per mode. Non-thinking recorded zero scenario errors, 110 calls, four repairs, 391,077 tokens, and 353.184 seconds of model latency. Thinking recorded two explained fixture-selection incompatibilities (#9/#15), 97 calls, four repairs, 502,048 tokens, and 1,156.213 seconds of model latency, with no empty API response. Intended thinking revision/final paths for #9/#15 were not exercised. **Gates B and C are not passed:** strong-draft, authorship, and revision/final consistency concerns remain, so the consolidated prompt stays evaluation-only; the user subsequently selected the Phase 1 baseline with thinking as the new repository default. See `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md`.

The historical full acceptance artifact is `data/evidence/v3_acceptance_evaluation_20261115T113518Z.json`: prompt/schema `v3.6.5`/`v3.6.3`, thinking mode, 32 scenarios, three scenario errors (#8/#15 fixture selection and #24 empty API response), 98 attempted calls, 97 successful-response logs, three repairs, 488,010 observed tokens, and 1,266.141 seconds of model latency. The earlier #1/#10 Support validation failures did not recur, but #30 escalated after one unclear answer and semantic review found source-grounding, target-vocabulary, and strong-draft concerns. **Neither integrated engineering nor clean semantic acceptance is passed.** The latest non-thinking baseline remains `data/evidence/v3_acceptance_evaluation_20261115T091103Z.json`: two scenario errors (#1/#10), 114 attempted calls, ten repairs, and 399,368 observed tokens. `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` records all positive, null, mixed, and negative findings. Operational completion is not a pedagogical-quality claim.

A separate user-authorized exact-text initial check is recorded in Section 14 of the implementation results. Four attempts used eight cumulative non-thinking calls and 37,801 tokens. The final `v3.6.8` artifact, `data/evidence/v3_exact_essay_initial_evaluation_20261115T134018Z.json`, delivered four candidates in two calls with no repairs and passed a local one-goal Choose/Revise browser check. Earlier attempts failed location validation, and the final output retains semantic scope/priority concerns. This exact-text check was an explicitly authorized exception outside the synthetic-only prototype workflow, not a new general usage permission. It is not synthetic acceptance, educator review, deployment, or learner-outcome evidence.

A separate controlled Support-only comparison used three matched SA handoffs. Thinking resolved the targeted blocker with zero errors/repairs; non-thinking required two repairs. Thinking used 23,068 total tokens and 75.863 seconds of model latency, versus 21,629 tokens and 24.017 seconds for non-thinking. The full run limits that targeted finding and does not justify a runtime-mode change or a broad quality claim. See Sections 10–11 of the implementation results.

The evaluation-only SOTA comparison ran seven targeted scenarios with native thinking requests for Claude Opus 5.5 and Gemini 4 Argon, without total token stop caps. Claude recorded one scenario error/four repairs; Gemini recorded three timeout-ended scenarios/one repair. Both affirmed the #10 strong draft and avoided the sampled #22 target-vocabulary issue, but Claude failed #8 occurrence validation and Gemini retained semantic concerns. Neither solved the targeted set. Smoke and artifact paths, actual usage, output review, and protocol limitations are in Section 13 of `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md`. No full SOTA acceptance run or runtime-default change occurred.

The current thinking Support comparison used the same 14 frozen handoffs and is assessed with the educator rubric in `data/evidence/v3_baseline_readability_rubric_screening_20261116T070407Z.json`. The v3.8.1 candidate is **Needs refinement** overall: it meets the screened authorship, source-responsibility, hint-guidance, coherence, and meaningful-selection anchors, but multilingual readability/tone and Final-regression meaningfulness remain **Needs refinement / Moderate**. The earlier v3.8.0 candidate's unsupported octopus-heart mechanism request was **Unacceptable / Critical** and was fixed in v3.8.1. Calls, tokens, latency, repairs, and surface metrics are secondary diagnostics in the detailed artifacts. The candidate remains evaluation-only; see `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`.

The thinking Coordinator-targeted arms each completed 12 scenarios with zero repairs; the candidate affirmed strong-draft #10 and avoided the later-start deletion regression. In the eight-scenario integrated set, the candidate produced explained fixture-selection incompatibilities at #15 (two goals instead of the scripted three) and #20 (direct response with no selectable goal), so those revision/Final paths remain unexercised and Gate C is not passed. Separate controlled Final-history probes verified the exact-verdict guard and retained-opening behavior in both arms. Gate B remains open because readability is mixed and Final meaningfulness/educator review are unresolved. No candidate non-thinking run, full candidate diagnostic, prompt promotion, or deployment occurred.

External expert review of `V3_BASELINE_READABILITY_EXPERT_REVIEW.md` independently recommended **not promoting v3.8.1**, while preserving its calibration and Final-consistency gains. The expert considered the F2 misclassification potentially Major and identified unresolved EL readability friction. `V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` is implemented as the resulting evaluation-only iteration; its 369-check Gate A passes, but it is not promoted or adopted. `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md` records current engineering/output evidence and open gates, while `V3_8_2_READABILITY_AND_FINAL_EXPERT_REVIEW.md` packages the prompt logic and exact-output review. Targeted thinking LLM-assisted screening rates v3.8.2 **Needs refinement** and does not pass Gate B: Support survey/octopus wording and F1 improve, but F2 still lacks validated improvement credit, the imaginative Coordinator misses the litter-output gap in this run, and #9 retains only two expected regressions while treating the tracking caveat as an improvement. Integrated Gate C passes only for the seven-scenario versioned successor set: actual #15/#20 routes and controlled paths completed without forced counts/routes, while clarification resolved to Support rather than exercising real-model clarification_limit. Integrated #15 supplied another v3.8.2 Final-credit omission, so Gate B remains failed. No educator gate is passed.

The earlier completed pair used prompt/schema `v3.1.0` and is stored at `data/evidence/v3_paired_evaluation_20261110T094344Z.json`. All six scenarios completed in each mode. Thinking used 17 calls, including two schema repairs, 68,407 total tokens (24,926 reasoning tokens), and 246.2 seconds of cumulative model latency. Non-thinking used 15 calls, no repairs, 36,340 total tokens, and 64.2 seconds. These results supported the 2026-11-10 non-thinking runtime decision; they are not a general quality or learner-outcome conclusion.

Local mocked-browser checks at 1280px covered selection, revision, small-change confirmation, refresh restoration, failed final reflection, retry, and final comparison. `data/evidence/v3_local_verification_1280.png` is the final comparison capture. Full keyboard activation and actual screen-reader review remain open; see `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` for the bounded null result. Earlier browser walkthroughs are indexed in `V3_OUTCOMES_REPORT.md`. These synthetic checks do not establish educator approval, pedagogical effectiveness, or learner outcomes.

`EDUCATOR_REVIEW_PROTOCOL.md` provides the full-context three-educator walk-through protocol. Protocol-qualified recruitment, reviewer records, and the gate decision remain pending; the external expert input summarized above does not complete that gate.

## Configuration

`.env.example` documents the model, explicit thinking flag, reasoning-effort, timeout, database, evaluator-control display, debug, neutral small-change threshold, and evaluation-only `SOTA_API_KEY`/`SOTA_BASE_URL`/`SOTA_TIMEOUT_SECONDS` settings. SOTA evaluation supports only the explicitly selected Claude Opus 5.5 native Anthropic and Gemini 4 Argon native Gemini thinking paths; provider thinking blocks are filtered from logs and available reasoning-token counts are recorded separately. The student header omits developer/observability reveal controls unless `SHOW_EVALUATION_CONTROLS=true`; each panel then remains independently hidden until selected. Non-thinking runtime requests use temperature 0, while controlled thinking requests omit temperature. Prompt/schema/fixture versions and authorized model metadata are recorded with reviews; raw hidden reasoning is never stored or shown. Final prompt/response capture requires evaluator controls, server-side `ENABLE_DEBUG_MODE=true`, and separate opt-in for new reviews.

## Deployment and historical V1/V2 record

`PRD.md` remains the authoritative V1/V2 coursework and evidence record. V1 is preserved at commit `4eaa0ad` under the annotated `v1` tag. The historical post-JeepyTA V2 deployment used commit `7d94b58`. The canonical URL `https://writingassist-zhuang.streamlit.app` now serves V3 for synthetic testing only; a 2026-11-15 live initial-surface check verified the V3 workflow and footer `v04d61af`. The footer comes from `version.txt` and does not prove that current HEAD or every live flow has been verified. On 2026-11-16, a direct canonical-URL request returned a 303 redirect to Streamlit authentication, so the current deployed UI is not reverified. A pre-existing local port-8501 process started on 2026-11-15 returns HTTP 200 but predates the current structural changes; restart it before treating local testing as current-code evidence. The authoritative coursework submission remains `submission/Applied_Assignment_4_Concise_user_edited.md` and its visually verified PDF.
