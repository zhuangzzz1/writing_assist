# Changelog

Notable changes to the V3 Iterative Revision Coach. Version labels below refer to the V3 prompt/schema and fixture series, not the historical V1/V2 coursework runtime.

For the complete evidence analysis, see `V3_OUTCOMES_REPORT.md`. Historical V1/V2 outcomes remain in `PRD.md`; V1 is preserved at commit `4eaa0ad` under the annotated `v1` tag.

## [Unreleased]

### Added

- Added explicit evaluation-goal selection by 1-based index or exact reference, with duplicate/unknown/out-of-range rejection and recorded selected IDs, titles, and references.
- Added the versioned `live_el_contrasts.json` experiment set, controlled no-call prefixes, Support-only handoffs, non-persistent GC experiment arms, and per-run authorization/call/token-stop records.
- Added evaluation-only SOTA relay support for `claude-opus-5-5` and `gemini-4-argon` using native Anthropic/Gemini thinking protocols, explicit scenario lists, provider-aware evidence filenames, and final-text-only capture without hidden reasoning. Student runtime remains unchanged.
- Added targeted failed-revision restoration/retry coverage and local mocked-browser evidence for revision, refresh, failed final reflection, retry, and final comparison.
- Added targeted synthetic `live_el` scenario #16 for an imaginative system explanation with a missing output path, no required scientific source, and an existing closing sentence.
- Added 14 frozen Support comparison handoffs, 12 Coordinator-targeted scenarios, the evaluation-only `support_consolidated` and isolated `coordinator_early_limit` arms, per-arm prompt-version metadata, and issue/framework normalization metrics.
- Added `scripts/analyze_repairs.py` for deduplicated field-level repair-cause analysis, including preserved failed-scenario attempts and separate API/empty-response failures.
- Added protocol-consistent educator anchors for authorship, cross-field coherence, and multilingual-learner readability/tone; educator calibration and review remain pending.
- Added declared Final `revision_history` built from persisted snapshots and authoritative Coordinator observations, draft hashes, exact-link consistency guards, and legacy-round compatibility.
- Added the evaluation-only `baseline_readable` Coordinator/Support candidate and descriptive scenario/arm readability metrics for sentence length, long actions, repetition, and action/self-check scope review. Added `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md` with evidence and rollback boundaries.
- Added the evaluation-only `regression_readable` arm and `v3.8.3-regression-readable` Final prompt, preserving v3.8.2 as a control while checking whether changed qualifications undermine an original step's purpose. The owner subsequently promoted the behavioral contract to local prompt `v3.8.3`; the evaluation control and v3.8.0 structural control remain preserved.

### Changed

- After the 2×2 pedagogical review, the user explicitly selected the Phase 1 baseline with thinking as the repository default (`DEEPSEEK_THINKING=true`). Thinking omits temperature and uses configured reasoning effort; explicit non-thinking comparisons remain available. No deployment occurred.
- Choose now presents one recommended goal with a choose-only action, reveals alternatives on request, and separates idea/reasoning/organization choices from optional sentence polishing. Revealing and hiding choices make no model calls.
- Coordinator and Support guidance now covers imaginative process/system explanations, observable reader-facing strengths and rationales, and concise pattern-based conventions instruction without replacement prose or formulaic transition/conclusion demands.
- Local prompt/schema are `v3.8.3`/`v3.8.0` after the owner's explicit promotion decision; the v3.8.0 structural prompts and v3.7.1/v3.7.0 contracts remain evaluation controls. The promoted prompt carries the readability, strong-draft, Final-credit, and contextual purpose-loss guidance with local-runtime labels. This product decision is not a Gate B pass or deployment. Hints consistently require one concept restatement plus 2–4 procedural steps (3–5 total); Coordinator output uses singular `regression`, restricted model flag categories, and explicit boundary-route defaults. Only the graph owns `clarification_limit`; `teacher_review` with `none` returns to clarification rather than being relabeled as concerning content.
- Ranking now applies accuracy-first stable partitioning on initial and revision routes while preserving the Coordinator's supported-concern and non-accuracy order. No `addresses_student_concern` field was added.
- Added evaluation-only consolidated Support prompt (targeted `v3.7.1-consolidated`; routing-fixed full-run `v3.7.2-consolidated`) with genre-neutral focus anchoring, consolidated authorship/frame rules, and clearer multi-action instruction guidance; the production default did not switch arms.
- Removed generated vocabulary options, sentence starters, and Coordinator `reasoning_operation` from the local v3.8.0 contract after the user's cognitive-load/product decision. Legacy v3.7.x evaluation controls retain separate prompts and validators; v3.8.2 readability/strong-draft wording remains evaluation-only, while v3.8.3 was subsequently promoted locally as recorded in this Unreleased section.
- Retained Coordinator finding-severity classification while removing the reasoning-operation classification whose only consumer was sentence-starter selection.
- Kept GC, FG, and CQ production behavior unchanged after mixed, null, or unresolved targeted experiments; no persistent prior-findings production path was adopted.

### Fixed

- Added recorded deterministic paragraph/occurrence recovery for exact issue references that occur exactly once in the full draft; repeated, missing, and cross-paragraph references still require bounded repair.
- Extended the same narrow recovery to unique `present` framework references within one block, with separate framework/component correction records and no Final-reference normalization.
- Before the v3.8.0 scaffold removal, removed the literal `This evidence/detail matters because ____.` starter from the legacy contract. Exact quoted draft ellipses used for locating do not trigger completion-placeholder repair; target frames and non-reference ellipses still fail.
- Prevented Final same-goal improvement contradictions and verbatim-text deletion regressions through exact-link deterministic guards without inferring empty goal IDs or semantic weakening.
- Preserved the Support schema after baseline analysis found zero echo mismatches: 17 validation-failure events yielded 19 field findings, including 12 genuine authorship leaks and three quoted-ellipsis false positives across 212 attempted calls in the two preserved acceptance artifacts.
- Fixed practice-scenario overwrite confirmation by applying widget updates in an `on_click` callback.
- Closed the Finish confirmation dialog when final reflection fails so the saved failure and retry remain visible without discarding drafts.
- Simplified optional assignment and goal self-report language while preserving custom frameworks and stable internal self-report values.
- Moved the four workflow steps into the header and added action-based completed states with textual markers.
- Grouped revision candidates in native bordered containers with selected-state styling and escaped, visually distinct draft quotes.
- Replaced the privacy alert styling with a readable neutral notice while retaining the complete synthetic-writing and external-AI-service warning.
- Added readable feedback typography and escaped, keyboard-focusable original/final snapshot panes.
- Added `SHOW_EVALUATION_CONTROLS` to omit evaluator reveal controls from the student header by default; developer controls and observability remain independently hidden when enabled, and raw debug capture remains separately controlled.
- Made page widths, Draft input, editor/feedback panels, and reflection snapshots scale with the browser viewport using bounded widths, heights, and flex sizing rather than fixed desktop dimensions.
- Applied Nunito+Lora paired typography, a `--v3-*` CSS token system with theme-aware light/dark palettes, responsive side gutters with safe-area support, keyed container targeting, and dynamic step-completion styling without layout-shifting DOM elements.
- Restored Deploy button and theme switcher visibility in the Streamlit toolbar menu.
- Fixed the Choose/Revise highlight editor dropping or scrambling characters during fast typing; the textarea now takes Session State only on first mount.
- Added a small footer showing the commit recorded in `version.txt`.

### Verification

- **372 mocked checks passed** for the promoted local v3.8.3 implementation. In `data/evidence/v3_final_regression_regression_readable_evaluation_20261116T154531Z.json`, all four matched thinking Final contrasts completed with eight calls, zero errors, and zero repairs; two #9 findings covered all three loss types, and F1/E remained intact. A later default-factory check in `data/evidence/v3_final_regression_runtime_default_scenario_04_evaluation_20261116T160207Z.json` confirmed `v3.8.3`/`v3.8.0` with two calls, zero errors, and zero repairs, but omitted the tracking-purpose regression. Regression handling is therefore mixed across runs. F2 still withholds improvement credit and Gate B remains not passed; local promotion is an explicit owner product decision, not semantic acceptance or deployment. See Sections 8–9 of `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`.
- **369 mocked checks passed** for the evaluation-only v3.8.2 implementation. It preserves the two-agent architecture and v3.8.0 schema, adds Final credit/regression-restraint prompt guidance and an internal Support delivery review, and introduces versioned Final/coverage fixtures. `all_available` selects one to three actual candidates; the versioned #20 successor can Finish after direct_response without manufacturing a revision. These are engineering contracts, not semantic acceptance. Targeted thinking rubric screening rates the candidate **Needs refinement** and does not pass Gate B: Support survey/octopus wording and F1 improve, but F2 credit, imaginative Coordinator selection, and complete #9 regression preservation remain unresolved. Zero targeted repairs does not erase these semantic failures. Integrated Gate C passes only for the seven-scenario versioned coverage set; #15/#20 adaptive and controlled paths completed without forced counts/routes, and integrated #15 revealed another Final-credit omission. Full acceptance, non-thinking, human, accessibility, promotion, and deployment gates remain separate. See `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`, `V3_8_2_READABILITY_AND_FINAL_EXPERT_REVIEW.md`, and `data/evidence/v3_8_2_targeted_rubric_screening_20261116T084042Z.json`.

- **350 mocked checks passed** for the earlier structural/readability implementation, including the controlled Final-history fixtures and payload tests. Educator-rubric screening rates v3.8.1 **Needs refinement** overall: no unresolved Critical issue in the reviewed sample, with Moderate multilingual-readability and Final-meaningfulness concerns. The earlier v3.8.0 octopus source-grounding leak was **Unacceptable / Critical** and was corrected. Operational calls/tokens/latency and surface heuristics are secondary diagnostics, not performance rankings. See `data/evidence/v3_baseline_readability_rubric_screening_20261116T070407Z.json` and `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`.
- External expert feedback on `V3_BASELINE_READABILITY_EXPERT_REVIEW.md` recommended against promoting v3.8.1, retaining its calibration/consistency gains while fixing Final-regression restraint and EL readability. The expert considered F2 potentially Major rather than merely Moderate. `V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` is now implemented as an evaluation-only candidate, not an adopted runtime or promoted pedagogical improvement.
- Thinking Coordinator-targeted arms each completed 12 scenarios with zero repairs. The v3.8.1 candidate affirmed strong-draft #10 and avoided the later-start deletion regression; a source-present Final meaningfulness caution remains. Integrated candidate #15/#20 produced explained fixture-selection incompatibilities without forced retries, so Gate C is not passed. Controlled Final-history probes verified exact-verdict repair and retained-opening behavior for both arms. See `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md` and the paired artifacts.
- **325 mocked checks passed** for Gate A of the earlier prompt/contract revision. The repair analyzer and baseline decision are preserved in `data/evidence/v3_repair_analysis_20261115T151252Z.json`; real-model targeted and integrated outcomes are recorded in `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md`.
- All four Support 2×2 arms completed 14 handoffs without scenario errors. Consolidation changed non-thinking repairs from three to five and kept thinking at one; it did not earn promotion. Target-like vocabulary and a mismatched passage frame remain semantic failures. Coordinator targets completed 12 scenarios per mode and motivated the `none`-category routing fix; controlled probes reached `clarification_limit` correctly in both modes. See `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md` for mixed/negative findings and open semantic gates.
- Full integrated `v3.7.2-consolidated` diagnostics completed 32 scenarios per mode. Non-thinking used 110 calls/four repairs with zero scenario errors; thinking used 97 calls/four repairs with two explained fixture-selection incompatibilities (#9/#15) and no empty API response. Strong-draft, authorship, and revision/final consistency concerns mean Gates B and C are not passed; operational completion is not semantic acceptance or deployment evidence.
- **260 mocked checks passed** after the one-goal-first Choose, speculative-process, unique-reference, and language-guidance changes. Targeted SA outputs improved after corrections, but the final non-thinking integrated `v3.6.5`/`v3.6.3` artifact has two scenario errors and ten repairs. The full thinking run in `data/evidence/v3_acceptance_evaluation_20261115T113518Z.json` avoided the earlier #1/#10 Support validation failures and reduced repairs to three, but recorded three scenario errors (#8/#15 fixture selection and #24 empty API response), premature #30 clarification escalation, and remaining semantic concerns. It used 488,010 observed tokens and 1,266.141 seconds of model latency. Neither integrated engineering nor clean semantic acceptance is passed; the repository default at that time was non-thinking and the separate local port-8501 process was explicitly switched to thinking. See `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` for all positive, null, mixed, and negative findings.
- A separately authorized exact-text check, outside the synthetic-only prototype workflow, used eight cumulative non-thinking calls and 37,801 tokens across four attempts. Final prompt `v3.6.8` delivered four candidates in two calls with no repairs and passed local Choose/Revise browser inspection; earlier title-location failures and final semantic scope/priority concerns are recorded in `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md` Section 14.
- Completed SOTA smoke checks and seven targeted thinking scenarios per model without total token stop caps. Claude Opus 5.5 recorded one scenario error/four repairs; Gemini 4 Argon recorded three timeout-ended scenarios/one repair. Both affirmed #10 and avoided the sampled #22 target-vocabulary issue, but Claude failed #8 occurrence validation and Gemini retained semantic concerns. Neither solved the targeted set; see Section 13 of `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md`.
- Educator review, actual screen-reader/full-keyboard verification, deployment, and production-readiness claims remain open.

## [V3.4.0] — 2026-11-10

### Added

- Added optional structured framework name/component inputs with CER, RACE, RACES, and MEAL presets, custom component lists, negation-aware compatibility detection, and additive SQLite persistence.
- Added Coordinator-owned, framework-neutral `framework_coverage` entries with exact present-component references and issue-goal mappings.
- Added final-comparison stages to #7, #9, and #15 and a controlled 58-word/404-word density pair as #31/#32.
- Added deterministic grouping for identical, nested, and transitively overlapping goal references with explanatory feedback labels.
- Added clean evaluation-database checkpoint/close and stable byte/SHA-256 metadata.

### Changed

- Updated the integrated prompt and schema versions to `v3.4.0`; practice and acceptance fixtures use `v3.4.0`.
- Made explicit `working_genre` assignment deterministic without mismatch-only repairs.
- Added draft-supported student-concern priority and deterministic Support candidate ordering.
- Replaced mechanics-description keyword matching with the structured `obscures_meaning` judgment and expanded conservative teacher-policy recognition.
- Clarified plain-string vocabulary entries and the no-source `source_dependent=false` rule.
- Limited Support source payloads to source-dependent findings/limitations and omitted empty clarification history on revisions.
- Passed final original strengths and future possibilities through validated Coordinator findings instead of regenerating them.
- Batched prompt/schema evidence generation into one integrated acceptance evaluation rather than full runs for individual substages.

### Fixed

- Corrected the prompt review's repair-category count, full-run repair attribution, final-coverage count, hint distribution, proportionality claims, and nested-reference recommendation.
- Preserved the optional regression-field default while requiring actual regression/final-comparison evidence rather than field-presence proxies.
- Documented why live WAL-mode databases are not stable byte-level integrity artifacts and supplied reproducible deduplication arithmetic.

### Verified

- **213 automated checks passed** using mocked models and temporary databases before the real-model run.
- Chrome verified structured RACES loading/coverage, revision/final confirmation, grouped overlap selection/deselection, and stale-reference removal in `data/evidence/v3_4_browser_verification.json`.
- The acceptance fixture set contains 32 scenarios, including three additional final-comparison cases and the controlled density pair.
- Completed the 32-scenario non-thinking run in `data/evidence/v3_acceptance_evaluation_20261110T194146Z.json`: 102 deduplicated calls, three repairs, 270,101 tokens, and 300.490 seconds of model latency. #15 returned only two goals; #24 exposed disputed mechanics judgments; #32 initially fell back after an invalid reference. This is mixed evidence, not a clean quality pass.
- Completed targeted #15 and two density repetitions. #31 returned 2/2/3 candidates and #32 returned fallback/2/3, showing run variability rather than a length-density rule. See `V3_OUTCOMES_REPORT.md` Sections 17.3–17.4.
- Educator review, actual screen-reader assessment, deployment, and other human/production gates remain open.

## [V3.3.0] — 2026-11-10

### Added

- Added `test_cases/v3/acceptance.json`, a versioned set of all 30 PRD scenarios with exact fixture requirements, staged revisions, genre correction, clarification answers, self-report plans, and final-reflection operations.
- Added evaluation-only repair diagnostics with invalid final JSON responses, validation errors, agent/scenario metadata, prompt/schema/fixture versions, and repair latency/token use. Raw hidden reasoning is never captured.
- Added separate model-call, graph-invocation, and service-operation timing, including snapshot creation and result persistence.
- Added targeted real-model reruns with `--scenario-number` so corrected scenarios do not require a full acceptance rerun.
- Added `EDUCATOR_REVIEW_PROTOCOL.md` with full-context review packets, scenario assignments, authorship checks, severity rules, reviewer templates, and an explicitly pending gate.
- Added browser timing, keyboard-navigation, 1440px/1920px, and zoom evidence in `data/evidence/v3_improvement_browser_20261110.json`.

### Changed

- Switched the local student runtime to explicit non-thinking, temperature-0 configuration. Thinking remains an explicit controlled comparator and neither mode switches automatically.
- Strengthened Coordinator guidance for author-versus-student claim ownership, unique goal IDs, revision regressions, and non-obscuring mechanics.
- Strengthened Support guidance so teacher-directed RACES feedback collectively addresses Restate, Answer, Cite, Explain, and Sum up without creating a five-goal quota.
- Made omitted optional clarification fields default safely and the optional regression field default to false, reducing unnecessary repairs.
- Updated prompt version to `v3.3.0`, schema version to `v3.2.1`, and the acceptance fixture to `v3.2.1`.

### Fixed

- Fixed the three-goal fixture by providing distinct claim, source-accuracy, and organization/elaboration issues rather than forcing a third weak goal.
- Added bounded rejection of non-obscuring language-mechanics goals when teacher directions explicitly mark language corrections as optional.
- Fixed negation handling for phrases such as “does not obscure meaning.”
- Preserved partial evaluation evidence after clarification, correction, revision, and reflection failures.
- Corrected repair diagnostics to retain the invalid first final response rather than the repaired response.

### Verified

- **151 automated checks passed**; dependency and scoped diff checks passed.
- Final non-thinking browser revision and reflection completed under prompt `v3.3.0` and schema `v3.2.0`.
- The corrected 30-scenario run reduced repairs from 27 to 2; its remaining three-goal fixture issue was corrected and rerun separately.
- Scenario #7 targeted rerun produced three genuine goals and three honest observations without repairs.
- Scenario #24 targeted rerun rejected a non-obscuring mechanics goal and correctly used direct response.
- The first new paired core completed without scenario errors and showed improved RACES carry-through in both modes.
- Accessibility evidence is limited: keyboard navigation was verified through entering Revise, 200% zoom was verified, a 400% request was capped at 3×, and no actual screen-reader walkthrough was performed.
- Educator recruitment, assessments, and the gate decision remain pending. V3 remains local and undeployed.

### Evidence

- `data/evidence/v3_acceptance_evaluation_20261110T160932Z.json`
- `data/evidence/v3_acceptance_scenario_07_evaluation_20261110T162320Z.json`
- `data/evidence/v3_acceptance_scenario_24_evaluation_20261110T162337Z.json`
- `data/evidence/v3_core_evaluation_20261110T161430Z.json`
- `data/evidence/v3_core_evaluation_20261110T162342Z.json`
- `data/evidence/v3_improvement_browser_20261110.json`

## [V3.1.0] — 2026-11-10

### Added

- Added a complete local iterative revision workflow: initial draft, goal selection, student editing, immutable revision snapshots, repeated whole-draft review, voluntary stopping, and original-to-final reflection.
- Added two LangGraph agents:
  - Assessment Coordinator for genre-sensitive assessment, source boundaries, selected-goal observations, routing, and comparison findings.
  - Instructional Support Agent for round feedback, bounded scaffolds, and final motivational reflection.
- Added argument, informational, and narrative support with correctable genre inference and material-ambiguity clarification.
- Added optional assignment prompts, teacher directions, source material, and student concerns. Teacher-supplied CER/RACES/MEAL terminology is passed to both agents.
- Added deterministic source availability and source-location validation for source-dependent findings.
- Added exact draft references with paragraph and occurrence metadata for goal-linked highlighting, including repeated-passage disambiguation.
- Added one-to-three goal selection and individual observations: specific improvement, improvement not yet evident, or uncertain.
- Added optional attempted/deferred goal self-reports without attempt inference from text diffs.
- Added passage-specific hints with two to four linked steps and self-checks, vocabulary considerations, approved abstract frames, and pregenerated stuck steps.
- Added **Show less feedback** and **I’m stuck** presentation actions without additional model calls, affect fields, emotion inference, or automatic teacher escalation.
- Added neutral unchanged/small-change confirmation before snapshot creation or model review.
- Added deterministic original/previous/current and original/final diffs without quality judgments.
- Added simulated teacher review with separate student/evaluator outputs and clarification-limit handling after two unclear answers.
- Added SQLite compositions, immutable snapshots, rounds, reflections, execution records, and LangGraph checkpoints. Snapshot updates are rejected by a database trigger.
- Added session restoration, read-only history, retry without duplicate snapshots, complete session deletion, and recovery for missing or corrupted storage.
- Added a student-focused Streamlit interface with Draft, Choose, Revise, Reflect, and History views; independently hidden developer controls and observability.
- Added a constrained initial editor and a 60/40 desktop workspace with independently scrolling containers.
- Added a Streamlit CCv2 editor with exact multiple-goal highlights, deselection, scrolling synchronization, and stale-highlight removal.
- Added finish confirmation from both the feedback footer and Reflect step.
- Added honest review-stage updates and end-to-end, per-agent, per-call, and schema-repair latency metadata.
- Added authorized model configuration, provider request IDs, and available token-use metadata without storing raw hidden reasoning.
- Added six versioned synthetic practice scenarios in `test_cases/v3/scenarios.json`.
- Added `scripts/evaluate_v3.py` for explicit representative thinking/non-thinking evaluation.
- Added comprehensive mocked, API, storage, graph, revision, and Streamlit AppTest coverage.
- Added `V3_OUTCOMES_REPORT.md` with implementation, evidence, content comparison, coverage inventory, limitations, and recommendations.

### Changed

- Replaced the old local V1/V2 runtime with V3 while preserving historical fixtures and evidence.
- Raised the Streamlit minimum to 1.66 for the CCv2 highlighted editor.
- Changed the student runtime to require thinking mode and omit temperature. Non-thinking remains available only through the explicit controlled evaluation runner.
- Increased the default model timeout to 120 seconds and added configurable reasoning effort.
- Added explicit draft/source/context length limits with no silent truncation.
- Restricted sentence starters to approved abstract frames; assigned-topic frames are rejected even when they contain blanks.
- Prohibited numeric evidence answers in vocabulary options and strengthened instructions against supplying target responses in revision actions.
- Made the representative garden evaluation select the first candidate in both modes for matched selected-goal comparison.
- Bumped prompt and schema versions from `v3.0.0` to `v3.1.0` after real-output scaffold review.
- Updated active project documentation while preserving V1/V2 as historical evidence.

### Fixed

- Corrected duplicate Streamlit percentage sizing that compressed the draft and feedback panes. The initial editor now measures 780px at 1280px and the workspace is approximately 60/40.
- Corrected initial model-failure navigation so users reach a saved-review retry view without losing editor text or duplicating snapshots.
- Corrected revision-word diff counting at whitespace boundaries.
- Preserved selected-goal titles and submitted-goal visibility during revision review.
- Preserved unsubmitted editor text during genre correction, step navigation, dialog cancellation, and failed reviews.
- Prevented final reflection restart from orphaning checkpoints; failed reflection uses explicit retry.
- Enforced exact references, source locations, per-goal observations, and final comparison references through bounded validation and repair.

### Verified

- **128 automated checks passed** across nine test files.
- Dependency validation, Python compilation, and the scoped Git diff check passed.
- Real `v3.1.0` browser loop verified at 1280px, including two simultaneous highlights, stale-highlight removal, two selected-goal observations, next-round navigation, finish confirmation, final reflection, and restoration.
- Six representative scenarios completed in both model modes without scenario errors.
- Thinking: 17 calls, two repairs, 68,407 total tokens, 246.2 seconds of cumulative model latency.
- Non-thinking: 15 calls, no repairs, 36,340 total tokens, 64.2 seconds of cumulative model latency.
- Evidence favored further validation of non-thinking as the likely default candidate. The runtime still required thinking at the time of V3.1.0; V3.3.0 later implemented the explicit non-thinking decision.

### Evidence

- `data/evidence/v3_browser_verification_20261110.json`
- `data/evidence/v3_paired_evaluation_20261110T094344Z.json`
- `data/evidence/v3_local_v3_1_final_reflection_1280.png`

## [V3.0.0] — 2026-11-10

### Added

- Added the initial V3 prompt/schema implementation and representative thinking/non-thinking evaluation pair.
- Added bounded schema repair, exact-reference validation, source contracts, and grounded final comparison.
- Added versioned synthetic scenario presets and the initial highlighted revision workspace.

### Issues identified during evaluation

- Some generated frames contained assigned-topic content despite placeholders.
- One vocabulary list supplied a numeric evidence answer.
- The garden comparison selected different goals across modes, weakening controlled comparison.
- The desktop grid applied Streamlit percentages twice and produced overly narrow panes.
- Initial model failures did not lead directly to the saved-review retry view.

These findings drove the V3.1.0 changes. The earlier artifact `data/evidence/v3_paired_evaluation_20261110T093315Z.json` is development evidence, not current-output evidence.

## [V3.0.0 planning record] — 2026-11-10

### Planning items at that time

These items preserve the early V3.0.0 planning context and are not current status. Later outcomes are recorded above and in `V3_OUTCOMES_REPORT.md`; current deployment and verification boundaries are in `README.md`.

- Decide the default model configuration after repeated matched runs and educator review. Non-thinking was favored by the representative evidence at that time.
- Complete the remaining exact Section 14.2 scenarios, including all-three-goal revision, meaningful organizational regression, long informational writing, language-error prioritization, middle-paragraph highlighting, register shifts, and repeated identical resubmissions.
- Capture invalid first responses during authorized debug evaluation to diagnose schema repairs.
- Complete the three-educator synthetic walk-through gate before any supervised student contact.
- Expand keyboard, zoom, focus, and assistive-technology checks beyond the desktop verification available then.
- Make deployment, durable-storage, privacy, consent, and institutional decisions separately. V3 was local and undeployed at this planning point.
