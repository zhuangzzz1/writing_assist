# Changelog

Notable changes to the local V3 Iterative Revision Coach. Version labels below refer to the V3 prompt/schema and fixture series, not the historical V1/V2 coursework runtime.

For the complete evidence analysis, see `V3_OUTCOMES_REPORT.md`. Historical V1/V2 outcomes remain in `PRD.md`; V1 is preserved at commit `4eaa0ad` under the annotated `v1` tag.

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

## [Unreleased]

### Planned validation and decisions

- Decide the default model configuration after repeated matched runs and educator review. Non-thinking is currently favored by the representative evidence.
- Complete the remaining exact Section 14.2 scenarios, including all-three-goal revision, meaningful organizational regression, long informational writing, language-error prioritization, middle-paragraph highlighting, register shifts, and repeated identical resubmissions.
- Capture invalid first responses during authorized debug evaluation to diagnose schema repairs.
- Complete the three-educator synthetic walk-through gate before any supervised student contact.
- Expand keyboard, zoom, focus, and assistive-technology checks beyond the current desktop verification.
- Make any deployment, durable-storage, privacy, consent, and institutional decisions separately. V3 remains local and is not deployed.
