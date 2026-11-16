# V3.8.2 Readability and Final-Reflection Improvement Plan

**Status:** Implemented for evaluation on 2026-11-16 after an explicit implementation decision. Gate A passed with 369 mocked checks. Targeted thinking review is complete: Gate B is not passed because F2 improvement credit, imaginative Coordinator selection, and complete #9 regression preservation remain unresolved. Versioned integrated Gate C passed for the seven-scenario successor set with actual alternate paths reported; integrated #15 supplied an additional Final-credit omission. Gates D–E remain open, and full acceptance is unevaluated. The candidate is not promoted or deployed. Full 32-scenario and non-thinking runs still require separate scope decisions.

**Primary evaluation rule:** Use `EDUCATOR_REVIEW_PROTOCOL.md` ratings, severity, and concrete output evidence. Calls, tokens, latency, repairs, and surface metrics are secondary diagnostics, not measures of pedagogical quality.

## 1. Starting Point and Expert Findings

The thinking-only comparison used a legacy v3.7.1/v3.7.0 control and the evaluation-only `v3.8.1-baseline-readable` candidate. An external expert reviewed the self-contained paired-output packet and recommended **not promoting v3.8.1**.

The expert-supported findings are:

- **Keep:** strong-draft calibration, synthetic-classroom-context handling, Final-verdict consistency, source-bound octopus guidance, and the imaginative litter-output goal.
- **Fix:** Final regression restraint, especially failure to credit genuine interpretation/source-bounded improvements when an explicit link remains incomplete.
- **Fix:** inconsistent multilingual readability, including stacked clauses, idiomatic instructions, repetition, and abstract nominalization.
- **Preserve as a bright spot:** concrete, short, orally rehearsed guidance in the imaginative-system example.
- **Do not resolve accidentally:** vocabulary and sentence-starter removal remains a separate product/ELD decision because prompt wording and schema changed together.

The candidate therefore remains evaluation-only. The local v3.8.0 structural runtime remains unchanged by this plan.

## 2. Objectives

1. Credit genuine gains in specificity, student interpretation, authorship ownership, and source-bounded wording at Final.
2. Reserve regressions for genuine losses of meaning, accuracy, necessary reasoning, or key structure rather than loss of vague boilerplate alone.
3. Make Support instructions consistently concrete and manageable for grades 5–7 multilingual learners.
4. Preserve student authorship, exact references, source limitations, meaningful issue selection, and Final-history consistency.
5. Close evaluation-coverage gaps without forcing candidate counts or model routes.
6. Separate readability wording effects from scaffold-removal effects where the available arms permit it.

## 3. Non-Goals and Protected Behavior

- Do not add a readability agent, editor agent, Final-review agent, or additional model-driven step.
- Do not change the two-agent architecture or add a runtime prompt selector.
- Do not restore vocabulary options or sentence starters in this iteration. Any future restoration requires a separate ELD/product decision and an isolated comparison.
- Do not implement a keyword-only idiom ban, universal word-category prohibition, hard sentence-length limit, or numerical pedagogical-quality score.
- Do not edit frozen historical fixtures or overwrite their evidence. Use versioned successors.
- Do not force three goals, a Support route, or a revision path when the Coordinator appropriately returns fewer goals or `direct_response`.
- Do not promote v3.8.1 or v3.8.2 automatically after evaluation.
- Do not claim educator approval, learner outcomes, target-age EL usability, accessibility completion, or production readiness from synthetic outputs alone.

## 4. Architecture Decision

Retain the existing separation of responsibility:

```text
Round:
Coordinator diagnosis -> Support delivery -> existing deterministic validation

Final:
Coordinator original/Final assessment -> Support reflection -> existing deterministic validation

Offline:
Actual outputs -> descriptive review aids -> educator-rubric assessment
```

Add a **delivery-review requirement inside the existing Support prompt**: Support drafts and checks its own JSON before returning it. This is not a new agent or additional model call. Do not collect or claim access to hidden reasoning; evaluate only the final structured response.

Add no model-driven post-processing after Support. A later readability-agent experiment is justified only if simpler prompt-only iterations repeatedly fail the same rubric anchors while preserving semantics, and that experiment requires a separate architecture decision.

## 5. Versioning and Experimental Arms

Versions:

- Candidate prompt: `v3.8.2-baseline-readable`.
- Application/model handoff schema: remain `v3.8.0`; no output-field shape change is planned.
- Local runtime: remain v3.8.0 structural with thinking.
- New or changed evaluation fixtures: increment to `v3.8.2-*`; preserve all v3.4.0, v3.8.0-final-history.1, and earlier artifacts.

Evaluation arms:

- `current`: preserved legacy v3.7.x control for historical anchors.
- `baseline_readable`: preserved v3.8.1 negative/mixed candidate, not edited in place.
- `baseline_readable_v2`: new v3.8.2 candidate.
- `structural_current`: evaluation-only selector for the local v3.8.0 structural prompts, providing a no-vocabulary/no-starter wording control without changing student runtime.

The v3.8.2-versus-structural comparison is the clearest wording-focused pair. The v3.7.x comparison remains useful for historical behavior but cannot isolate readability wording from scaffold removal.

## 6. Final Coordinator Changes

### 6.1 Credit genuine gains before identifying deficits

Add explicit Final guidance:

> Evaluate what the revision gains as well as what it leaves incomplete. Replacing vague boilerplate such as “This supports our plan” with a specific interpretation, causal explanation, or source-bounded qualification can be a genuine improvement even when the explicit link back to the main claim still needs work. Credit that gain with an exact Final reference.

Also:

> A prior improvement_not_yet_evident or uncertain verdict applies to its exact reviewed goal and text. It does not prevent recognition of a different genuine improvement elsewhere in the revision.

Preserve the existing deterministic guard for the same unchanged goal text after a negative/uncertain verdict.

### 6.2 Separate an incomplete next step from a regression

Add:

> Do not classify the loss of vague or formulaic wording as a regression when the replacement adds specific, accurate, student-authored reasoning or a justified limitation. If the main-claim connection remains incomplete but the revision has not lost meaning, accuracy, necessary reasoning, or key structure, place the remaining step in future_areas rather than regressions.

Require a genuine regression to identify the actual harm or loss in the text, not merely a less formulaic or less explicit phrase. A change may be both an improvement and a regression only when distinct, meaningful effects are supported by exact text; do not manufacture a trade-off to balance the reflection.

### 6.3 Required targeted interpretations

These are evaluation expectations, not hard-coded output text:

- **F1:** Replacing “This supports our plan.” with a source-bounded statement that the survey shows interest rather than health outcomes should receive credit for bounded interpretation. Loss of the boilerplate alone is not a regression.
- **F2:** Adding the student's own interpretation that better concentration could help class participation should receive credit for added reasoning and ownership. If the causal path from later start to concentration or the link back to the proposal remains incomplete, state that as an optional next step, not as proof of regression.
- **Organization regression #9:** Preserve genuine order and reasoning regressions when “Finally” precedes “First,” an audit-to-choice link is removed, or a tracking rationale is undercut.

### 6.4 Final Support and deterministic boundaries

- Final Support must preserve Coordinator finding IDs, references, and counts; it cannot add or hide findings.
- Keep exact-reference membership, actual-change overlap, unchanged-draft rejection, one bounded repair, and no Final-reference normalization.
- Do not add keyword-only boilerplate detection or automatic semantic regression removal. The new behavior is prompt/model guidance reviewed against exact outputs; existing guards remain limited to unambiguous contradictions.

## 7. Support Readability Changes

### 7.1 Internal delivery checklist

Before returning round feedback, Support must check the final JSON against all of these rules:

- Does each sentence ask for one manageable cognitive move?
- Are necessary multiple moves explicitly sequenced with words such as “First” and “Then,” without stacked clauses?
- Are instructions free of figurative or idiomatic phrasing such as “tie that thinking” or “bridge the gap”?
- Does the wording prefer concrete actions such as “Tell readers why” or “Show how” over abstract phrasing such as “add your own explanation of how”?
- Does any sentence repeat a claim, garden plan, or other idea without adding guidance?
- Do action, hints, self-check, and stuck step retain the Coordinator's finding and exact references?
- Can the student complete the next action without decoding the writing terminology first?

This checklist guides output generation; it is not a request to expose hidden reasoning and not a deterministic validator.

### 7.2 Sentence and field organization

Retain the approximate v3.8.1 budgets as prompt guides, with these clarifications:

- A `revision_action` may contain two short sequenced sentences when interpretation and connection are both necessary, but each sentence must contain one move.
- Do not combine two embedded `what`/`why` clauses in one instruction.
- Use the hint for process support rather than loading the complete process into `revision_action`.
- Keep `self_check` focused on the same move; do not enlarge it into a checklist of unrelated tasks.
- Keep `stuck_step` as one smaller immediate action, preserving oral rehearsal such as “Say aloud…” when useful.
- Split unrelated optional context additions away from the main action.

### 7.3 Targeted wording examples

For the survey anchor, prefer the structure—not mandatory verbatim text—of:

> First, say what the survey result shows about students. Then, explain how that supports your garden claim.

For the octopus anchor, prefer concrete wording such as:

> Tell readers why the three-hearts fact belongs with your point about octopuses.

Do not supply the student's interpretation, target mechanism, or replacement prose. Preserve the successful imaginative-system pattern:

> Find the turning wheel sentence. Say aloud one place the lifted wrappers could go in your system, then write only that step.

Avoid figurative uses of “tie” and “bridge” in student instructions. This is semantic prompt guidance, not a brittle runtime keyword ban.

## 8. Fixtures and Coverage Repair

### 8.1 Preserve historical evidence

Do not modify `test_cases/v3/acceptance.json` or prior evidence in place. Create a versioned successor set for changed evaluation behavior and retain scenario lineage to the original IDs/numbers.

### 8.2 Replace brittle goal-count assumptions

For the #15 successor:

- Add an `all_available` or equivalent evaluator selection mode that selects one to three actually produced candidates and applies the existing first/others self-report plan.
- Record the actual candidate count and selected IDs without treating a count below three as an application error.
- Do not claim that this exercises the original “two of three goals deferred” requirement if only two goals exist.
- Add a separate controlled three-goal prefix to exercise the original two-deferrals/one-attempt behavior independently of candidate generation.

For the #20 successor:

- If the initial review returns candidates, permit the staged first-goal revision and Finish flow.
- If it returns `direct_response`, exercise and record the valid no-revision Finish path instead of raising “no revision candidate.”
- Add a separate controlled reviewed-revision prefix when the experiment needs to test Final confirmation/history independently of the initial route.
- Never force Support or manufacture a candidate to preserve a script assumption.

### 8.3 Required targeted coverage

Include:

- Survey readability/authorship Anchor B.
- Source-less octopus Anchor C.
- Imaginative-system Anchor D.
- Strong-draft/synthetic-discussion Anchor A.
- Final source-present F1 and source-missing F2.
- Same-unchanged-goal Final Anchor E.
- Genuine organization regression #9.
- Optional-language #24.
- Versioned #15/#20 successors plus their controlled coverage fixtures.
- Clarification and human-review controls.

## 9. Evaluation Strategy

### Stage A — Engineering and mocked contracts

- Implement only after this plan receives an implementation decision.
- Add focused tests for Final credit/regression behavior, Support output contracts, versioned fixture selection, and controlled coverage paths.
- Run the complete mocked suite before any model call; preserve the current 350-check baseline and add new checks.
- Verify that no new agent/model node, hidden-reasoning field, or runtime prompt-arm selector is introduced.

### Stage B — Thinking targeted evaluation

- Run the same targeted handoffs for structural v3.8.0, v3.8.1, and v3.8.2 where useful, retaining v3.7.x for historical anchors.
- Review actual outputs with the educator rubric before any full diagnostic.
- Use exact paired excerpts and record Meets / Needs refinement / Unacceptable plus Critical / Major / Moderate / Minor.
- Record disagreements and uncertain cases without averaging them into a score.
- Treat calls, tokens, latency, repairs, and readability heuristics as secondary diagnostics.

### Stage C — Coverage and full diagnostics

- Run the versioned integrated successors only after targeted rubric review.
- A full 32-scenario run and any non-thinking comparison require a separate scope decision after Stage B.
- Distinguish model judgments, application failures, fixture incompatibilities, and deliberate alternate paths in the artifact.
- Preserve all failed and mixed artifacts.

### Stage D — Human and accessibility review

- Obtain independent educator/ELD review of the exact paired outputs, especially sentence-starter removal and Anchor B readability.
- Calibrate the Final regression anchors and strong-draft threshold with educators.
- Complete full-keyboard and actual screen-reader checks separately.
- Target-age EL comprehension/usability research and consent remain separate requirements before any student-contact or production decision.

## 10. Acceptance Gates

### Gate A — Technical contracts

- Full mocked suite passes.
- No architecture or schema-shape change occurs beyond the documented plan.
- Exact references, source limits, Final history, human review, and bounded repair remain intact.

### Gate B — Targeted pedagogical behavior

- F1/F2 credit genuine improvements and do not regress merely because boilerplate was replaced or a next step remains.
- Genuine #9 regressions remain visible.
- Anchor B/C readability concerns are addressed without target-content leakage.
- Anchor A/D/E improvements remain intact.
- No unresolved Critical or Major issue remains in reviewed v3.8.2 outputs; Moderate issues are addressed or explicitly documented for the promotion decision.

### Gate C — Integrated coverage

- Versioned #15/#20 paths and their controlled coverage fixtures complete without forced counts/routes.
- Actual coverage is reported; no intended behavior is silently left unexercised.
- Full diagnostic scope, if later authorized, distinguishes application failures from valid model-driven alternate paths.

### Gate D — Human and accessibility review

- Educator/ELD calibration is recorded using the existing protocol.
- Keyboard and actual screen-reader checks are complete or explicitly open.
- No learner-outcome claim is made without a separate appropriate study.

### Gate E — Product and deployment decision

- Candidate promotion, local-default changes, sentence-starter restoration, non-thinking adoption, and deployment each require separate explicit decisions and exact-artifact retesting.

## 11. Deliverables and Rollback

Deliverables after authorization:

- Versioned v3.8.2 Coordinator/Final and Support prompts.
- Focused mocked tests and versioned successor fixtures/evaluator support.
- Actual-output rubric screening and expert-review records.
- Updated results separating pedagogical findings from secondary diagnostics.
- A self-contained successor expert-review packet.

Rollback:

- Keep v3.8.2 disabled by default and select it only through its evaluation arm.
- Preserve v3.8.1 and earlier artifacts without editing or deleting them.
- Keep local v3.8.0 structural behavior unchanged unless a separate promotion decision is made.
- Do not use destructive history resets or delete evidence to roll back.

## 12. Explicitly Deferred Decisions

- Whether any sentence starter should return in a simpler, optional, non-generic form.
- Whether non-thinking evaluation is needed for a future product decision.
- Whether a full 32-scenario diagnostic is justified after targeted review.
- Whether repeated prompt-only failures justify a later readability-agent experiment.
- Whether and how to conduct consented target-age EL usability research.

These deferrals must not be resolved implicitly by implementing this plan.
