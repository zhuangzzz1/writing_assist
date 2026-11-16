# V3 Baseline Readability and Semantic Improvement Implementation Plan

**Status:** Implementation and the authorized thinking-only targeted evaluation are complete. Full integrated diagnostics require a separate review after targeted results. No deployment or candidate prompt promotion is authorized. Gate A passes with 350 mocked checks; Gates B–E remain open as recorded in `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`.

**Successor status:** `V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` records the expert-informed next iteration. It is now implemented as a separate evaluation-only candidate; this completed plan did not adopt it.

**Current runtime:** Phase 1 baseline with thinking enabled, explicitly selected by the user. Non-thinking remains a controlled comparator, not the default. The local contract is being updated to `v3.8.0` as recorded below; this is not a deployment or a thinking-mode change.

**Starting versions:** Production prompt/schema `v3.7.1`/`v3.7.0`. The baseline-thinking Support artifact used `v3.7.0`; its Support text is byte-identical to the current baseline Support prompt. The targeted consolidated arm was `v3.7.1-consolidated`; the later full-run arm was `v3.7.2-consolidated`.

**Purpose:** Improve grades 5–7 multilingual-learner readability while preserving student authorship and fixing Final-history consistency, strong-draft handling, and deletion-regression grounding.

## 0. Confirmed Implementation Decisions

The user resolved the plan's open decisions through the `grill-me` review before behavioral implementation:

- Implement through targeted model evaluation, then stop for review. The user initially selected both modes but explicitly narrowed the billable matrix to thinking only before execution; new candidate non-thinking behavior remains unevaluated. Do not run the full 32-scenario diagnostic without a later decision.
- The authorized thinking-only matrix is all 14 Support handoffs for `current` and `baseline_readable`, all 12 Coordinator-targeted scenarios for the same two arms, and acceptance #7/#9/#10/#11/#15/#20/#24/#30 for the same two arms. Call caps are 35 per Support run and 75 per Coordinator/integrated run, with no token stop cap.
- Use the recommended readability budgets as prompt guides only, not deterministic length validators or quality scores.
- Remove vocabulary support throughout V3 because prior tests did not show enough writing-improvement value to offset its cognitive load. Remove its generation, output field, and any remaining display code rather than merely requiring an empty list.
- Remove sentence starters throughout V3 under the same local contract change. Also remove the Coordinator `reasoning_operation` classification because its only consumer was starter selection.
- Adopt these scaffold removals and the Final-history contract in local runtime prompt/schema `v3.8.0`. Preserve `v3.7.1`/`v3.7.0` prompts and contracts as evaluation controls and preserve old stored responses without deleting historical fields. Do not deploy.
- Keep readability and strong-draft/grounding prompt changes evaluation-only in the `baseline_readable` arm pending targeted review; do not promote those prompt changes into the local default with the structural contract update.
- Use the plan's meaningful-actionable-issue and synthetic-classroom-context rules as an evaluation-only Coordinator candidate, with educator calibration still open and no fixture-label routing.
- Apply deterministic Final guards only to unambiguous exact links: unchanged same-goal text after `improvement_not_yet_evident` or `uncertain`, and deletion regressions whose exact original reference remains in the Final draft. Leave semantic weakening and empty-goal-ID inference to model/human review.
- The pre-implementation mocked baseline is 325 passing checks.
- The first `v3.8.0-baseline-readable` Support run completed operationally but asked for an unsupported real-world octopus-heart mechanism despite a source limitation and used first person in one student self-check. Preserve that failed semantic artifact. The follow-up candidate is `v3.8.1-baseline-readable` with source-bound elaboration and second-person self-check guidance; its targeted rerun is covered by the same thinking-only scope with `--reruns-covered`.
- After candidate integrated #15/#20 produced explained fixture-selection incompatibilities, the user authorized a separate two-case controlled-prefix Final-history probe rather than forcing candidate counts or routes. Both arms ran `v3.8.0-final-history.1` in thinking mode with a 12-call cap per arm. The final mocked suite has 350 checks.
- The user's follow-up evaluation decision makes `EDUCATOR_REVIEW_PROTOCOL.md` the primary performance rubric. Use Meets / Needs refinement / Unacceptable with Critical / Major / Moderate / Minor and concrete evidence. Calls, tokens, latency, repairs, and surface heuristics are secondary diagnostics, not implementation-quality rankings. LLM-assisted rubric screening remains distinct from the pending educator gate.

## 1. Evidence and Current Constraints

The plan is based on the 14-handoff Support 2×2, targeted Coordinator scenarios, full 32-scenario diagnostics, repair-category analysis, and local workflow verification.

### Confirmed findings

- Baseline thinking was the strongest arm in the qualitative pedagogical review, mainly for authorship and grounding. This is not educator-confirmed evidence or proof of learning outcomes.
- Ten of 20 baseline-thinking `revision_action` fields exceeded 38 words. Long instructions combine locating, reasoning, connecting, and checking.
- `CLAIM ANCHORING` and the long example in `INSTRUCTION CLARITY` are plausible contributors to nested instructions.
- Consolidated non-thinking increased targeted repairs from three to five and introduced genuine authorship leaks. Consolidated thinking improved readability but still had vocabulary and authorship concerns.
- Zero Support echo mismatches occurred in the sampled historical calls and all four 2×2 arms. No Support echo-injection refactor is justified by this evidence.
- Final findings often have `goal_id=""`. `WritingAssistantState` does not declare `revision_history`, and the inspected Final prompt payload contained `revision_history: []` with no prior goal observations. A prompt-only instruction to inspect prior verdicts will not work.
- Strong-draft #10 continued to receive questionable issues. Thinking incorrectly treated an explicitly synthetic class discussion as an accuracy problem.
- Thinking reported a deletion regression although `Our school should start later.` remained in the Final draft.
- The final mocked suite passed 325 checks. Gates B and C are not passed; educator and accessibility gates remain open.

### Evidence boundaries

- Hidden reasoning was not collected. Do not claim that models actually drafted and simplified prose in a reasoning trace.
- One run per 2×2 cell does not prove that thinking is uniquely able to follow readability constraints.
- `cozy` occurred in the full integrated non-thinking #22 output, not in the targeted consolidated handoff set.
- No baseline-thinking student-facing instances of `warrant`, `articulate`, `substantiate`, or `mechanism` were found in the 20 reviewed candidates. The alleged 2-versus-4 action/self-check mismatch was not located and must not be cited as evidence without an exact scenario.
- Word budgets and readability grade levels are experimental guides, not validated learning or acceptance thresholds.

## 2. Objectives

1. Make student-facing instructions shorter, clearer, and easier to act on without supplying target ideas or prose.
2. Give `revision_action`, hint steps, `self_check`, and `stuck_step` distinct, coherent jobs.
3. Ensure Final findings do not contradict the latest review of the same submitted text.
4. Prevent manufactured accuracy issues for synthetic/shared classroom context while preserving genuine source limitations.
5. Require full-draft verification before reporting deleted or weakened ideas.
6. Evaluate operational reliability, readability, and semantic quality separately in thinking and non-thinking modes.

## 3. Non-Goals and Protected Behavior

- Do not promote `v3.7.1-consolidated` or `v3.7.2-consolidated`; preserve them as documented mixed/negative experiments.
- Do not rewrite Support output fields to inject Coordinator echoes. The sampled evidence does not show an echo-mismatch burden.
- Do not change the two-agent architecture or add a readability agent.
- Do not change the baseline-thinking default automatically after candidate evaluation. Any later default change requires a separate product decision.
- Do not restore non-thinking as the default merely to reduce latency. Keep it as an explicit comparator.
- Do not deploy as part of this plan. Deployment needs a separate explicit decision and exact-artifact retest.
- Do not use real student essays or confidential classroom records. New fixtures must be synthetic.
- Do not edit the four frozen root V1/V2 fixtures.
- Do not collect raw hidden reasoning.
- Do not force `direct_response` merely because a fixture is labeled “strong.”
- Do not treat every unattached classroom discussion as verified evidence.
- Do not adopt a universal ban on adjectives, emotions, or mechanism verbs. The boundary is supplying missing target content, not word category alone.
- Do not introduce an unvalidated numerical pedagogical-quality score or claim Grades 5–6 readability as an outcome.
- Do not weaken exact-reference, source, framework, human-review, sentence-frame, or one-repair protections.

## 4. Product Decisions Required Before Behavioral Changes

Record explicit decisions before implementation. Recommended starting points are candidates for evaluation, not established policy.

### 4.1 Readability budgets

Recommended candidate guidance:

- `title`: 3–6 plain words.
- `why_it_matters`: 1–2 short sentences, approximately 25 words total.
- `revision_action`: one focused writing move in 2–3 short sentences, approximately 15 words per sentence, one action per sentence.
- Hint steps: retain the existing 3–5 total items, with one concept restatement and 2–4 procedural steps; approximately 18 words per step.
- `self_check`: one short question checking the same writing move as `revision_action`; do not require yes/no form when a reflective question is more useful.
- `stuck_step`: one immediate small action, approximately 18 words.

These are prompt guides, not initial deterministic validators. Review whether the budgets are appropriate before making any hard limit.

### 4.2 Vocabulary policy

Recommended candidate rule:

- Use `vocabulary_options=[]` for goals whose main work is generating a claim, reason, mechanism, explanation, sensory detail, emotion, or narrative action.
- Permit general transition/linking words and brief meaning notes for difficult terms already present in the draft, prompt, or supplied source when useful.
- Permit careful word-choice support for language/register goals, but never words that supply the requested target content.
- Do not impose a four-entry quota. Empty is normal; add an entry only when it helps the student understand or complete the task.

This is a product-policy change and requires product/educator confirmation before production adoption.

### 4.3 Sentence-starter policy

Decide whether to relax the current rank-1 non-empty-starter requirement when the frame does not help the requested action. Require action–starter coherence rather than treating a starter as mandatory support.

### 4.4 Strong-draft threshold

Develop an educator-reviewed threshold for meaningful issues versus optional polish. Do not encode a blanket rule that all classroom discussions are valid evidence or that all strong-labeled fixtures must receive `direct_response`.

### 4.5 Final deterministic guard scope

Decide how much contradiction detection belongs in Python. Recommended: use deterministic rejection only for unambiguous links. Empty Final `goal_id` values require semantic review, not automatic quotation replacement or uncertain goal inference.

## 5. Versioning and Evaluation Arms

Use separately versioned candidates; do not edit the baseline in place.

- Support candidate: `v3.8.0-baseline-readable`
- Coordinator candidate: `v3.8.0`
- Application/model handoff schema: `v3.8.0` because Final history becomes an explicit contract
- Model-output field shapes may remain backward-compatible with `v3.7.0`; document that they did not change shape even though the overall handoff version increased.
- Evaluation fixtures: increment only when fixture content changes. Preserve original artifact versions and paths.
- Runtime control: current baseline thinking. Candidate arms: readability-tuned thinking and readability-tuned non-thinking. Do not change student defaults during comparison.

Every artifact must record the actual prompt, schema, fixture, model, mode, reasoning effort, calls, repairs, tokens, latency, and normalization counts.

## 6. Phase 1 — Build the Final-History Handoff

### Scope

1. Add a declared `revision_history` contract to `langgraph_core/state.py`. Do not rely on an undeclared key being dropped by graph validation.
2. Populate it from persisted snapshots and the latest reviewed revision, including:
   - revision number and snapshot ID where useful;
   - selected goal IDs and exact goal references;
   - each selected goal's `status`, `observation`, `evidence_reference`, and `carry_forward` from the authoritative Coordinator handoff;
   - the last reviewed current-draft identity or deterministic hash, so the Final coordinator can verify that it is reviewing the same text.
3. Include the authoritative observations in the Final model payload. Support goal feedback may be used for display, but must not replace the Coordinator's original observations.
4. Extend `COORDINATOR_FINAL_PROMPT` to require consistency with prior verdicts when the Final submitted draft is identical to the last reviewed revision.
5. Preserve existing exact-membership, unchanged-draft, changed-text-overlap, and no-quotation-normalization rules.

### Deterministic behavior

- Reject a Final improvement only when its link to a prior `improvement_not_yet_evident` or `uncertain` goal is unambiguous and the referenced text is the same unchanged goal text.
- A matching `goal_id` alone is insufficient evidence of contradiction; require matching goal text or a documented exact-reference link.
- Allow genuine improvements outside the prior goal.
- Do not infer a goal merely because a Final reference happens to share a few words with an earlier reference.
- Keep Final Support constrained to verified Coordinator IDs and references.

### Proposed Final prompt guidance

> Inspect the supplied revision_history before reporting improvements. If the final submitted draft is identical to the last reviewed revision draft, do not classify the same unchanged goal text as a specific improvement when its latest observation was improvement_not_yet_evident or uncertain. A different, genuine improvement elsewhere in the draft may still be reported. Before claiming that an idea was deleted or weakened, verify its absence or contradiction against the complete final draft, including opening and closing paragraphs.

### Tests

- Reproduce local workflow and integrated #20: prior `improvement_not_yet_evident` must not become `specific_improvement` for the same unchanged goal text.
- Allow a prior `specific_improvement` to remain an improvement.
- Allow a genuine unrelated improvement when one selected goal did not improve.
- Cover `uncertain` and empty Final `goal_id` cases without false deterministic rejection.
- Verify the deletion-regression fixture cannot report that the later-start proposal disappeared while its opening remains.
- Verify unchanged originals/finals still produce no improvements or regressions.
- Verify Final references remain exact and overlap actual changes; no reference normalization occurs.
- Verify older persisted rounds remain readable or receive an explicit compatible migration path.

## 7. Phase 2 — Coordinator Grounding and Strong-Draft Controls

### Round prompt changes

1. Strengthen the existing meaningful-issue threshold without forcing affirmation:
   - Use `direct_response` when the draft fulfills the task with understandable language and genre-appropriate support, and no meaningful actionable issue remains.
   - Do not create optional expansion goals solely to provide candidates.
2. Distinguish classroom/shared context from external source verification:
   - Do not mark a discussion inaccurate or unusable merely because it is synthetic in a synthetic task or has no attached reading file.
   - If attribution is too vague for the reader, use a development-level elaboration issue only when it genuinely impairs the argument.
   - Preserve `source_limitations` when external verification is actually needed. No-source accuracy claims remain prohibited.
3. Retain protection against fabricated evidence, real-world factual misrepresentation, and source-dependent findings without a supplied source.

### Final prompt changes

Require full-draft verification before any claim that an idea was deleted, weakened, or contradicted. The deterministic changed-text-overlap check remains necessary but is not semantic proof.

### Tests

- Strong-draft #10 is reviewed for actual meaningful issues rather than forced into either route.
- Synthetic classroom discussion alone cannot create an accuracy finding.
- Vague discussion attribution can receive a bounded development finding when meaningful.
- Genuine external-source misrepresentation remains an accuracy finding.
- The later-start deletion regression is rejected.
- Existing strong-draft, source-missing, and human-review behavior remains covered.

## 8. Phase 3 — Readability-Tuned Support Candidate

### Prompt changes

1. Add a `PLAIN-LANGUAGE DELIVERY` section using the confirmed candidate budgets. Preserve concept restatement and concrete-first process guidance.
2. Replace rigid nested `CLAIM ANCHORING` with plain-English grounding:
   - Use one concrete reader question or a short link to the student's claim, central idea/topic, or key moment.
   - If the focus is unclear, refer to the topic or existing wording rather than inventing a claim.
   - Avoid stacked `that` clauses and empty slogans such as `details make writing better`.
3. Give fields distinct responsibilities:
   - `revision_action`: state the focused writing move.
   - Hint steps: explain the concept and the process for attempting it.
   - `self_check`: inspect only the requested move, not a larger or smaller task.
   - `stuck_step`: reduce that same move to one smaller immediate action, not a duplicate of the whole process.
4. Require action–starter coherence. A source-reporting frame must not be attached to an evidence-interpretation task unless it genuinely helps. Allow an empty starter if the confirmed policy permits it.
5. Apply the confirmed selective-vocabulary rule. Do not use `context-compatible` as permission to invent target content.
6. Require physically clear instructions. Avoid ambiguous directions such as “circle the first tap.” Split unrelated optional context additions from the main revision action.
7. Prefer neutral, observable reader questions over repeated negative framing and abstract metaphors when a direct instruction is clearer.

### Descriptive evaluation metrics

Add scenario/arm-level surface metrics to the evaluation artifact:

- Mean and maximum words per sentence for `why_it_matters`, `revision_action`, hint steps, and `stuck_step`.
- Count of long actions using the documented 38-word review heuristic, explicitly not a quality score.
- Repetition across action, hint steps, self-check, and stuck step.
- Action–self-check scope mismatches flagged for human review, not automatically treated as failures.
- Optional Flesch–Kincaid analysis only if its limitations for JSON fragments, questions, and frames are documented. It must not be the primary acceptance metric and needs no new dependency without an explicit decision.

### Tests and static checks

- Argument, informational, imaginative informational, narrative, missing-claim, first-person, source-present/source-missing, and revision cases.
- Exact candidate IDs, references, locations, source limitations, and goal statuses remain unchanged.
- Abstract starters pass; on-topic/completed frames and completion placeholders outside starters still fail.
- Safe locating ellipses still pass; disguised completion instructions still fail.
- Action and self-check scope matches in targeted examples.
- No target-like vocabulary in the known `focus/concentrate`, `removed/stored`, `pump/supply`, `creak/glimpse/flutter/hush`, and `cozy` controls.
- The literal slash starter remains removed.
- No readability metric is treated as educator approval or learning evidence.

## 9. Phase 4 — Controlled Evaluation

### Stage A — Contract and mocked engineering

- Run focused tests after each phase and the full suite before any candidate model call.
- Preserve the current 325-check baseline and add new contract tests.
- Do not start billable evaluation with a red or incomplete implementation.

### Stage B — Targeted model evaluation

Run in this order:

1. **Support readability comparison:** current baseline thinking versus readability-tuned thinking, then readability-tuned non-thinking versus baseline non-thinking where useful. Use the same 14 frozen handoffs and output contracts.
2. **Coordinator targeted evaluation:** strong draft #10, synthetic discussion, prior-verdict #20/local workflow, Final deletion regression, source-present/source-missing cases, and clarification controls.
3. **Small integrated regression set:** #7, #9, #10, #11, #15, #20, #24, and #30 before the full set.

Use both modes for candidate evaluation, with baseline thinking as the control. Keep model, handoffs, output schema, validators, repair policy, and output settings constant within each pair. Non-thinking uses temperature 0; thinking omits temperature and records reasoning effort.

Add an evaluation-only `baseline_readable` runner arm for the combined candidate; keep `current` as the baseline control and do not change production prompt selection. Use the evaluator's existing `--authorization-id`, `--approver`, and `--max-model-calls` interface, establish run scope before execution, and record any token stop cap when chosen. No billable run is performed by this plan.

Assess performance primarily with the educator rubric's ratings, severity, and concrete output evidence. Report operational and surface diagnostics separately as secondary information; never use them as a quality ranking. Repeat paired runs when resources permit; small samples remain descriptive.

### Stage C — Full integrated diagnostic

Run all 32 scenarios in both modes only after targeted checks are reviewed. Distinguish application failures from fixture incompatibilities such as #9 and #15. Do not force a candidate count or revision path that the model appropriately does not produce.

### Stage D — Human and accessibility review

- Use the educator protocol's existing Meets / Needs refinement / Unacceptable ratings and Critical / Major / Moderate / Minor severity categories.
- Compare baseline thinking and readability-tuned thinking on a small blinded paired sample where feasible; include a non-thinking sample for calibration.
- Calibrate vocabulary and strong-draft anchors with educators before adopting those policies.
- Review authorship, cross-field coherence, grounding, genre fit, meaningfulness/priority, multilingual readability/tone, and revision/Final consistency.
- Record disagreements and uncertain cases; do not average them into a quality score.
- Complete full keyboard and actual screen-reader checks separately.

## 10. Acceptance and Progression Gates

### Gate A — Technical contracts

- Full mocked suite passes.
- Final history is populated and observable.
- Existing source/reference/human-review protections remain intact.

### Gate B — Targeted behavior

- Readability improves without target content or source/genre regressions.
- #20/local Final contradiction does not recur.
- The later-start deletion regression does not recur.
- Strong-draft and classroom-discussion behavior has no unresolved critical issue in reviewed outputs.
- Validator false positives and semantic failures are reported separately.

### Gate C — Integrated behavior

- Intended paths complete without unexplained fallback.
- Strong-draft, clarification, revision, and Final-comparison regressions are reviewed.
- Fixture incompatibilities are distinguished from application failures.
- Prior failed baselines remain preserved.

### Gate D — Human and accessibility review

- Educator review addresses readability, vocabulary, strong-draft judgments, and multilingual-learner tone.
- Full keyboard and actual screen-reader checks are completed or explicitly open.

### Gate E — Product/deployment decision

- Any prompt promotion, runtime-mode change, or deployment requires a separate explicit decision and exact-artifact retest.
- Baseline thinking remains the default unless that decision says otherwise.

## 11. Deliverables

- Declared Final-history state and payload contract with compatibility tests.
- New Coordinator and Support prompt candidates.
- Readability metrics and targeted comparison artifacts.
- Updated evaluation records separating operational, readability, and semantic outcomes.
- Updated PRD, README, changelog, coding guidance, and repository guidance for adopted behavior only.
- Educator-review records and explicit remaining accessibility/deployment gates.
- A rollback record identifying how to disable candidates without changing the baseline or deleting evidence.

## 12. Recommended First Implementation Slice

Start with **Final history**, not prompt polish:

1. Add and populate the Final-history contract.
2. Add #20/local and deletion-regression tests.
3. Implement the Final prompt consistency check and any approved deterministic guard.
4. Verify the actual Final payload contains prior verdicts and exact references.
5. Then build the readability candidate and its 14-handoff comparison.

This order prevents a readability improvement from hiding a structural cause of Final contradictions. It also ensures that prompt engineering addresses problems the model can actually see rather than asking it to inspect history it never received.
