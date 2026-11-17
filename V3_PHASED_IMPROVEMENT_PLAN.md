# V3 Phased Improvement Plan

**Status:** Phase 0 is complete by owner decision using the preserved historical thinking-mode run. Phase 1 now has an evaluation-only `phase1` implementation (`v3.9.2-phase1`/`v3.9.0`) under the user's separate implementation authorization; its real-model and named semantic-review gates remain open, and it is not promoted or deployed. Phases 2–4 remain proposed for implementation review. This revision incorporates independent-review clarifications while preserving student-controlled stopping, meaningful-issue limits, semantic review, and honest limits on historical comparisons.

## Guiding priority

The order should be:

**Assessment integrity → honest progress tracking → pattern batching → better scaffolds → final consistency and integrated evaluation.**

We should not start by making the loop cheaper. **Batching the wrong goals would only produce a faster, cheaper version of the same shallow coaching.** The first task is to ensure the Coordinator assesses the whole draft and interprets revision outcomes correctly.

Implementation should proceed one gated phase at a time. Semantic quality is primary; calls, tokens, latency, repair counts, and other operational measurements are secondary diagnostics.

Cross-phase guardrails:

- Do not manufacture candidates to reach a quota.
- Do not impose a fixed pedagogical revision-round cap or infer tiredness from round count, writing, or support-button use.
- Do not require transitions merely because guide words are absent.
- Do not use keyword-only checks as proof of answer-free guidance or pedagogical quality.
- Keep fixture-specific vocabulary, paragraph locations, expected findings, and scenario-dependent branches out of production prompts, routing, validation logic, and ordinary UI copy. Scenario IDs may remain metadata, and fixture loaders may load student-safe presets, but runtime behavior must never branch on a fixture identity. Fixture-derived examples in this plan are evaluation illustrations, not production few-shot examples.
- Do not require a model finding to match a predetermined anchor, phrase, location, or candidate count. A potential fixture anchor may be rejected as unsupported or not meaningful through text-based human review.
- Do not certify scientific validity, learner outcomes, educator approval, or deployment readiness from synthetic implementation checks.

---

## Phase 0 — Preserve the historical test-run reference — Complete

**Completion decision:** The owner accepts Phase 0 as complete using the existing thinking-mode test run as the historical comparison reference. No new baseline-rerun or exact-reproduction gate is required. Creating derived development fixtures, counterfactuals, and held-out transfer cases is Phase 1 setup work and does not reopen Phase 0.

### Preserved historical reference

- Primary stable record: `V3_8_3_COMPLETE_RUN_EXTERNAL_REVIEW.md`, a self-contained reconstruction of the application logs. It is not independent external review, educator approval, or learner-outcome evidence.
- Source records: `data/writing_assistant.db`, composition `d09cc8fb8042467aa3fa20ec2d50d247`, when that database remains available and unchanged. The review packet remains the stable reference if the mutable database later changes.
- Configuration: `deepseek-flash`, thinking enabled, reasoning effort `high`, prompt `v3.8.3`, schema `v3.8.0`.
- Scope: one synthetic grade-5 informational workflow with an initial review, seven submitted revisions, and a completed Final reflection.
- Recorded operational reference:
  - Complete run: 20 calls, 166,945 tokens, 371.463 seconds.
  - Revisions 3–7: 10 calls, 78,591 tokens, 165.490 seconds.
  - Coordinator/Support repairs, invalid references, and deterministic reference normalizations where available.
- Context limits: assignment prompt, teacher directions, framework/components, source material, student concerns, and preset scenario/fixture ID were empty. The run supports workflow and draft-feedback comparisons, not a complete task-context or source-dependent evaluation.

Preserve the historical packet and source records without rewriting their outputs to match later expectations.

### Historical comparison contract

- Thinking-mode outputs can vary across runs. Do not require exact reproduction of findings, candidate counts, wording, ordering, routes, repairs, or latencies, and do not rerun the historical baseline merely to seek a preferred result.
- Compare new outputs with the historical record through human semantic review: supported remaining issues, partial-progress interpretation, narrowing/requirement handling, scaffold quality, stopping honesty, and unsupported findings. Differences are review observations, not automatic improvements or regressions.
- Make direct historical comparisons only where the draft/snapshot and relevant task context correspond. Record configuration and contract differences. For new argument, narrative, counterfactual, acceptance, or held-out cases absent from the historical run, mark the historical control unavailable and use candidate-only semantic review rather than fabricating a baseline.
- Compare calls, tokens, repairs, and latency only for like-for-like scopes. Do not compare a Phase 1 single-turn probe with the historical 20-call complete workflow. Full-loop operational comparisons wait for the corresponding adaptive replay.
- Keep historical `v3.8.3`/`v3.8.0` artifacts immutable as the reference. Phase 1 defines new candidate prompt/schema versions and evaluator selectors without requiring new baseline calls.

### Historical garbage-system observations — evaluation only

These observations belong only in fixture definitions and evaluation records. They are hypotheses for human review, not required Coordinator findings or exact-reproduction targets, and must not be copied into production prompts, deterministic rules, or ordinary UI copy.

Using application paragraph numbering, which includes the title:

- Paragraph 2: remaining opening sentence-boundary problems.
- Paragraph 5: ambiguous dewatering references.
- Paragraph 6: unclear filter pronoun.
- Paragraph 7: overloaded leachate/methane sequence and additional boundaries.
- Paragraph 8: conclusion comma splice.
- Transport deletion: scope narrowed, not transport problem answered.
- Partial agreement revisions: genuine improvement with remaining work.
- Cohesion: the relationship between the earlier `wet trash` category and the later “trashes that have too much water” wording is a potential reader-connection issue, not automatic proof that canned transitions are required.

---

## Phase 1 — Fix whole-draft assessment and goal interpretation

This is the most fundamental phase. Phase 0 is complete. Perform the evaluation setup below before changing behavior; no new historical-baseline calls are required.

### Objective

Ensure the system identifies meaningful remaining problems, ranks them responsibly, and interprets what a revision actually accomplished before it routes, stops, or declares a goal closed.

### Evaluation setup

- Add a versioned synthetic **development fixture** derived from the preserved garbage-system run without modifying frozen historical fixtures or artifacts. Include the original draft, seven revisions, transport-deletion revision, both explicitly partial agreement revisions, and Snapshot 7 as a whole-draft probe.
- Add counterfactual variants that correct the targeted sentence boundaries and clarify the targeted references, so unsupported persistence of those findings can be checked. These remain same-essay development probes, not evidence of transfer.
- Add two lightweight synthetic **development probes** for early schema verification:
  - One argument with a realistic synthetic assignment and source, including both a discretionary narrowing case and deletion of a required assignment component.
  - One narrative with an initial assessment and one revision-outcome probe, preserving informal voice without inventing claims, citations, counterclaims, or formalization requirements.
- Reserve a small versioned **held-out transfer set** from iterative output review and candidate revision:
  - An unrelated informational process/system draft and revision with different subject matter, vocabulary, paragraph structure, and reasoning needs.
  - Strong informational negative controls, including one draft with no meaningful actionable issue and one with only optional polish.
  - Unrelated argument/source and narrative initial/revision cases that do not reuse the garbage-system structure or expected findings.
- Evaluate the transfer set only after the candidate prompt, schema, and deterministic logic are frozen for Phase 1 review. Do not use its outputs or expected findings to tune that candidate. If they are used for subsequent revision, reclassify the set as development data and require new held-out cases before claiming transfer.
- For each development fixture, distinguish reviewer-confirmed meaningful issues, potential anchors requiring judgment, optional polish, and unsupported concerns. Do not require an exact number of model-generated issues or candidates.
- Define new candidate prompt/schema versions and an evaluator selector before behavior changes. Use the default thinking configuration for candidate probes and record any configuration or payload differences from the historical run. Historical controls come only from the preserved run; no new baseline calls are a Phase 1 requirement.

### 1.1 Strengthen whole-draft review and triage

The current prompt already requests a review of the whole current draft. This phase must strengthen compliance, triage, outcome semantics, and regression evidence rather than claim to introduce whole-draft review for the first time. The Coordinator must assess more than the currently edited passage before returning `direct_response`.

It should distinguish:

- Accuracy and source-responsibility concerns.
- Explicit teacher/task requirements and supported student concerns.
- Meaning-blocking clarity problems and missing reasoning/process links.
- Organization and meaningful cohesion needs.
- Recognizable language patterns across the draft.
- Optional polish suitable for inline spelling support or future work.

Preserve the existing accuracy-first, supported-concern-next, and teacher-requirement coverage rules. For the remaining pedagogical choices, use this default triage:

1. Meaning-blocking clarity and missing reasoning/process links.
2. Organization and genuine reader-connection needs.
3. Recognizable cross-draft language patterns.
4. Optional polish.

The Coordinator continues to own supported-concern identification and non-accuracy ordering. Python performs only the existing stable accuracy partition; do not replace semantic triage with keyword-only deterministic classification.

A language problem that obscures meaning belongs at the clarity level; it must not be deprioritized merely because its category is `language_conventions`.

For every draft, the Coordinator must base findings on that draft’s actual task, meaning, reasoning, organization, and language. For speculative process/system explanations, important referents, missing process links, category-to-detail connections, and claim-to-benefit reasoning are genre-sensitive review dimensions, not a checklist of expected findings. The Coordinator must not:

- Invent a factual or scientific contradiction.
- Certify that an invented design works.
- Require transitions merely because guide words are absent.
- Manufacture additional candidates to fill a quota.
- Treat any development-fixture anchor as a mandatory finding for that draft or transfer it to another draft without independent textual support.

The existing five-issue maximum remains. Return every genuinely meaningful issue that fits after responsible triage. When meaningful issues exceed capacity, group them only when they form one pedagogically coherent finding, and record lower-priority overflow in `coordinator_reasoning` for reviewer accountability. Overflow remains meaningful, must be reconsidered during later whole-draft reviews, and never by itself justifies `direct_response` or a resolution claim.

For every fixture, account for each reviewer-confirmed meaningful issue as a returned issue, part of a genuinely coherent grouped issue, or explicitly documented lower-priority overflow. A potential anchor may instead be rejected as unsupported or not meaningful with a text-based reviewer rationale; it must not be promoted to a finding merely to satisfy the fixture. When multiple meaningful issues exist across different categories, preserve them as distinct student choices where appropriate. Do not force two or three candidates, manufacture a group to fit the cap, or collapse genuine alternatives merely because a single convention goal is easier to generate.

### 1.2 Separate text observation, goal outcome, and narrowing

Retain the existing text-observation dimension:

- `specific_improvement`
- `improvement_not_yet_evident`
- `uncertain`

Add a distinct goal-outcome dimension:

- `fully_addressed`
- `partially_addressed`
- `not_addressed`
- `uncertain`

Add a separate narrowing dimension:

- `none`
- `discretionary`
- `required`

This avoids treating `specific_improvement` as mastery and allows a revision to preserve partial improvement while also recording a deletion. `goal_outcome` describes only the selected goal in the submitted text; it is not an overall essay judgment. Narrowing describes a scope change without assuming the writer’s intention and never by itself means that the original problem was solved. Do not use `scope_narrowed` as a goal-outcome value.

Examples:

| Revision | Text observation | Goal outcome | Narrowing |
| --- | --- | --- | --- |
| Two targeted agreement errors are corrected, but a third instance remains | `specific_improvement` | `partially_addressed` | `none` |
| A discretionary example is deleted while the introduction becomes clearer | `specific_improvement` in introduction focus | `not_addressed` | `discretionary` |
| No relevant textual change | `improvement_not_yet_evident` | `not_addressed` | `none` |
| Genuinely ambiguous goal evidence | `uncertain` | `uncertain` | `none` |
| Some goal improvement, but a required assignment component is deleted | `specific_improvement` | `partially_addressed` | `required` |

Ground every non-`none` narrowing classification with structured evidence:

- `narrowing_evidence_reference`: an exact contiguous previous-draft quotation of the deleted segment. Validate that it exists in the previous draft and is absent verbatim from the current draft; quote only the deleted segment when the surrounding passage remains.
- `requirement_source`: empty for discretionary narrowing, or one of `assignment_prompt`, `teacher_directions`, or `framework` for required narrowing.
- `requirement_reference`: empty for discretionary narrowing; for required narrowing, the exact relevant assignment/teacher-direction text or commissioned framework component.

When `narrowing=none`, all three narrowing/requirement evidence fields must be empty. When narrowing is discretionary, the requirement fields must be empty. When narrowing is required, both requirement fields are required. If several required components are affected, retain coverage for each; establishing one requirement does not erase the others. The deterministic diff or a model rationale alone is not sufficient evidence for either the deletion or its required/discretionary classification.

**Discretionary narrowing** may close the original goal as no longer applicable, but must not mark it as answered. **Required narrowing** must retain or create a live task-alignment concern and preserve every affected framework component. A separate improvement elsewhere in the draft does not erase an unmet requirement.

### 1.3 Make carry-forward reflect remaining work

Define and test an explicit observation/outcome/narrowing/carry-forward/route consistency matrix, including permitted and rejected combinations. Apply at least these invariants:

- `fully_addressed` requires `narrowing=none` and `carry_forward=false`; do not recreate the same goal as an unresolved candidate or classify a deletion as goal completion.
- Partial improvement must remain visible as improvement. A meaningful remainder requires `carry_forward=true` and a current issue/candidate with the same `goal_id`.
- For `not_addressed` or `uncertain` without narrowing, a meaningful selected concern that remains open requires `carry_forward=true` and a same-ID live candidate. Do not infer student effort or non-attempt from these outcomes.
- Discretionary narrowing may set `carry_forward=false` only when the original goal is genuinely no longer applicable. If a meaningful remainder still applies, keep it visible through a same-ID live candidate. Closing a goal because its scope disappeared is not completion.
- Required narrowing always requires a live task-alignment issue and candidate. If this is the same unresolved selected goal, reuse its `goal_id` and set `carry_forward=true`. If it is a distinct requirement concern, use a new `goal_id`; the original goal may close only as no longer applicable, never as answered, while the new requirement remains visible. Framework coverage must link to a live issue and cannot substitute for that candidate.
- Whenever `carry_forward=true` for the same unresolved selected goal, deterministically require a current issue/candidate with the same `goal_id`. `direct_response` cannot contain an unresolved carry-forward goal or any required-narrowing concern.
- Preserve the existing student-controlled Choose flow. Carry-forward does not auto-select a goal for the next round.
- No mandatory student-authored explanation or reflection is needed.

### 1.4 Preserve and display the new outcome contract

- Implement the new contract under the candidate prompt/schema versions defined in the evaluation setup; do not overwrite the preserved historical reference.
- Extend Coordinator selected-goal observations with goal outcome, narrowing, narrowing evidence, and requirement basis.
- Extend Support goal feedback to carry those fields. Support may paraphrase the bounded observation, but must preserve the observation status, goal outcome, narrowing classification, evidence, requirement basis, and carry-forward decision exactly. Apply the same contract on `direct_response`, which bypasses Support.
- Render neutral student-facing outcome and narrowing labels in both support and direct-response feedback. “Fully addressed” must be bounded to the selected goal in this draft, not presented as mastery. Discretionary narrowing must say that the original goal no longer applies without saying it was solved; required narrowing must make the remaining requirement visible.
- Extend persisted round state and the existing revision-history records so Phase 2 and Phase 4 can consume the new fields. Older records with missing fields remain empty/unknown rather than receiving inferred outcomes.
- Reconcile the current V3 PRD, `CLAUDE.md`, `AGENTS.md`, evaluator documentation, and affected current-implementation notes with the candidate contract. Clearly distinguish the preserved historical reference, evaluation-only candidate, and any later explicitly promoted runtime.
- Phase 1 does not inject bounded history into every round; that remains Phase 2 work. Do not change Final prompt interpretation or Final consistency semantics until Phase 4.

### 1.5 Correct stopping semantics and use the existing off-ramp

Distinguish:

1. **No meaningful actionable issue remains.**
2. **Issues remain, but stopping is a reasonable student-controlled choice.**
3. **Only optional future polish remains.**

Do not use the first message for the second or third situation.

For mode 1, retain `direct_response` with empty issues and empty optional polish. For mode 2, retain `support_agent` and the remaining candidates; neutral copy may say that the student can finish with work still available, without claiming the issues are gone. For mode 3, extend `direct_response` with a bounded `optional_polish` collection containing one to three entries, each with a concise description and an exact located current-draft reference; the schema may allow zero to three entries so mode 1 uses an empty list. Keep `issues` and revision candidates empty, validate every polish reference, and use distinct copy that describes optional future work rather than claiming that no textual improvement is possible. `optional_polish` must be empty on clarification, teacher-review, and support routes; optional polish must not become a manufactured coaching candidate.

Mode 2 or 3 stopping language must be based on the remaining work, not assumed fatigue or a round threshold. The existing **Finish and reflect** action remains the student-controlled off-ramp after any completed review; no new model route is required merely to let the student stop.

Do not infer tiredness from revision count, writing quality, or support-button use, and preserve the prohibition on a fixed pedagogical round cap. If meaningful or required issues remain, the student may still finish, but the message must not claim that those issues do not exist.

### Verification

- Run the complete existing and new mocked suite. Cover the full permitted outcome/route matrix, rejected combinations, deferrals, narrowing evidence, requirement references, carry-forward identity, direct-response restrictions, optional polish, and student-controlled rather than automatic goal selection.
- Test exact Coordinator-to-Support preservation, direct-response behavior, neutral UI rendering, round/history persistence, and older history records with missing outcome fields.
- Scan production prompts, routing, validation logic, and ordinary UI copy for distinctive development-fixture vocabulary and scenario-dependent branches. Flag matches for removal or explicit justification. This is a leakage diagnostic, not a keyword-only semantic quality check; scenario metadata and fixture loaders are permitted.
- Use candidate single-turn real-model development probes with versioned payloads and the default thinking configuration. Where the preserved run contains a corresponding draft/snapshot and context, compare semantically with that historical output without requiring identical findings. Mark the historical control unavailable for other probes. Report the candidate prompt/schema versions and preserve positive, null, negative, failed, and repeated-run outcomes without cherry-picking.
- Include the Snapshot 7 whole-draft probe reviewed against the complete draft. Account for reviewer-confirmed meaningful issues using the triage/overflow rule, but allow potential anchors to be rejected with a text-based rationale. In the corrected counterfactual variants, unsupported boundary/reference findings must disappear; any remaining finding must cite independently supported residual text.
- Include the early argument/source and narrative development probes, with initial assessment and revision-outcome checks for each. Assess the argument’s discretionary and required narrowing cases independently, even when they share a controlled fixture.
- Run a targeted existing acceptance regression subset using compatible initial/revision single-turn payloads: source-present, source-mismatch, and source-missing cases (`acceptance_01`–`acceptance_03`), the strong draft (`acceptance_10`), long informational draft (`acceptance_23`), and informal narrative (`acceptance_26`). These are development regressions, not held-out transfer evidence. Full acceptance remains in Phase 4.
- After candidate prompt/schema/logic freeze, run candidate probes on the reserved transfer set. Include the unrelated informational process/system initial/revision pair, both strong-informational negative controls, and unrelated argument/source and narrative cases. These cases are outside the preserved reference run and use candidate-only semantic review; do not create a new baseline merely to manufacture a pair. Review for unsupported findings transferred from the development essay, manufactured issues on strong drafts, appropriate optional-only stopping, and assessment grounded in each current draft. If these outputs drive further candidate changes, repeat the gate on new held-out cases.
- Test partial improvement, uncertain evidence, discretionary closure, required deletion, carry-forward, direct-response prevention, optional-only stopping, and meaningful cohesion without mandatory transition wording.
- Track Coordinator/Support repairs, invalid references, and deterministic normalizations as secondary reliability diagnostics.
- Name the owner or appointed semantic reviewer. Using the existing Meets / Needs refinement / Unacceptable and Critical / Major / Moderate / Minor protocol, review complete current drafts and outputs rather than only route labels, anchor recall, or similarity to the historical run. When corresponding historical outputs exist, blind historical/candidate provenance labels where practical. Every reviewer-confirmed meaningful issue must be addressed, coherently grouped, or explicitly justified as lower-priority overflow; potential anchors need not produce findings. Allow no unresolved Critical or Major finding on either development or held-out transfer probes. LLM-assisted screening may support this review but cannot substitute for the named reviewer or constitute educator approval.
- Do not run a full adaptive loop before Phase 2 batching is available.

A temporary increase in potential round count after stronger whole-draft assessment is not itself a Phase 1 semantic failure. Full adaptive replay waits for Phase 2 so stronger assessment does not intentionally produce an extended sequence of single-location rounds.

### Exit gate

The complete mocked suite passes. On both development and held-out transfer probes, there is no `direct_response` that overlooks a reviewer-confirmed meaningful issue; partial, uncertain, discretionary-narrowing, and required-deletion outcomes are accurate; optional-only stopping is distinct; and no unsupported finding is copied or transferred from a development fixture. Corrected counterfactuals do not retain unsupported findings, and strong negative controls do not acquire manufactured science, transition, cohesion, or candidate-quota findings. Every reviewer-confirmed meaningful issue is accounted for, while potential anchors may be rejected through documented review. There are no unresolved Critical or Major semantic-review findings. Historical semantic comparisons, unavailable-control decisions, configuration differences, and negative outcomes are recorded without requiring exact reproduction. Transfer evidence remains limited to these synthetic fixtures; it is not educator approval or evidence of learner outcomes, and operational savings are not expected from this phase.

---

## Phase 2 — Introduce bounded history and same-pattern batching

### Objective

Once assessment and goal interpretation are reliable, eliminate repetitive single-location review cycles.

### 2.1 Add reusable multi-location storage with constrained batching

The reference container should be reusable across candidate categories so later patterns do not require a conventions-only schema redesign. Actual batching, however, must still represent **one coherent pedagogical pattern across several exact locations**, not merely repeated surface wording or unrelated reasoning tasks.

For example, several instances of the same non-count-noun pattern may form one batch when they require the same concept and revision action. Ambiguous pronouns in different process steps must not automatically be grouped merely because they all contain `it` or `them`; their reader problems and required reasoning may differ. These generic examples describe batching principles, not text patterns to detect with keywords.

Each batched candidate needs:

- A primary exact reference.
- Additional exact references with paragraph and occurrence metadata.
- One pattern explanation.
- One revision action covering the set.
- One self-check covering the set.
- Per-location review outcomes after submission.

Support and storage must preserve every location without silently dropping, duplicating, or replacing it. Extend existing exact-reference validation and bounded repair behavior to every additional reference before any location is shown to the student.

### 2.2 Batch conservatively

Start with an experimental default of **2–4 representative locations**, selecting the clearest and most disruptive examples across the draft. This is a location-count experiment, not a candidate-count quota.

Examples:

- Sentence boundaries: several clear and disruptive instances across the opening, middle, and conclusion.
- Subject–verb agreement: several locations supported by the same agreement concept and revision action.

Guardrails:

- Do not combine unrelated grammar, spelling, and capitalization patterns.
- Do not turn every comma into a period; allow an appropriate period or joining word.
- Include both newly created and existing lowercase sentence starts in the sentence-boundary self-check rather than creating a separate capitalization goal.
- If more locations remain, report them honestly rather than claiming the whole pattern is resolved.
- Do not impose a fixed total revision-round cap.

### 2.3 Add per-location outcomes

Use outcomes such as:

- `addressed`
- `remaining`
- `uncertain`

The overall Phase 1 `goal_outcome` is `partially_addressed` when only some locations are corrected; per-location outcomes do not replace that separate goal-level contract. Student-facing feedback can say, for example:

> “Two spots are clearer. Check the remaining sentence in the middle paragraph.”

Validate the mapping between every location and its outcome so one corrected instance cannot hide the rest.

### 2.4 Supply bounded relevant history

Give each round a compact record of:

- Goal/pattern type.
- Latest text observation, goal outcome, and narrowing classification.
- Remaining locations.
- Discretionary and required narrowing evidence, including previous-draft deleted-text references.
- Assignment/framework requirement source, exact requirement reference, and coverage status where relevant.
- Recent partial progress.

Do not inject the complete growing transcript. Measure the additional prompt-token cost against the saved review cycles.

### 2.5 Update highlighting and editing

- Highlight every location belonging to the batched goal.
- Preserve existing overlap-union behavior.
- Remove stale highlights independently as the student edits.
- Keep selection, editing, and scaffold reveal free of model calls.

### Verification

- Mocked multi-location validation, storage, highlighting, and per-location outcome tests.
- Identical, repeated, nested, missing, and edited-reference cases.
- Tests proving that surface repetition alone does not create an invalid multi-concept batch.
- Controlled pattern-batching replay compared with the preserved historical run where draft and workflow scopes correspond. Do not rerun the old loop solely to manufacture a new baseline or require the same sequence of findings.
- Coordinator/Support repair rates, invalid-reference rates, deterministic normalizations, missing/duplicate locations, and per-location outcome/reference mismatches.
- Review full-draft coverage, semantic quality, and actual calls/tokens/latency. Low repair or call counts do not establish quality.

### Exit gate

Fewer fragmented cycles **without** losing meaningful locations, weakening observations, introducing forced goals, or accepting unresolved reference/outcome integrity failures. Four total rounds and any latency target remain hypotheses to measure, not predetermined acceptance claims.

---

## Phase 3 — Redesign hints for reusable, age-appropriate learning

### Objective

Replace the oscillation between abstract terminology and direct answers with concise, reusable instruction.

### 3.1 Use a consistent micro-scaffold

Each hint should contain:

1. A plain-language concept restatement.
2. A reusable physical or spoken test.
3. Application to the selected locations.
4. A matching self-check.
5. A smaller answer-free stuck step.

Examples of reusable tests:

- “Read each side. Could each side stand alone as its own sentence?”
- “Is this one thing or more than one? Check the action word that belongs to it.”

### 3.2 Remove default answer leakage

Avoid directly supplying:

- `has, not have`
- The exact replacement punctuation for one location.
- The actor or mechanism missing from a student’s process explanation.
- Replacement sentences or paragraphs.

Any explicit-answer fallback after repeated difficulty requires a separate product decision; it is not included in the default design.

### 3.3 Resolve the worked-example contract conflict with a bounded experiment

The PRD permits checked unrelated process demonstrations, while the current Support prompt broadly prohibits worked examples.

Before implementation, make an explicit contract decision. The proposed initial experiment is:

- Allow a short, completely unrelated contrastive example only for a `language_conventions` pattern.
- Keep worked examples prohibited for content and reasoning goals in this initial experiment, where examples are more likely to steer the student’s ideas or supply target logic.
- Use a genuinely unrelated context that does not share the student’s topic, objects, or intended reasoning.
- Limit the example to one or two brief lines and assess its cognitive load.
- Never provide a full model essay or a target response to the student’s prompt.
- Reconcile the PRD, prompt, tests, and project documentation before enabling the experiment.

This conventions-only split is a cautious experimental policy, not a claim that unrelated examples can never be appropriate for other goals.

### 3.4 Improve student-facing readability and verify inline support

- Prefer everyday language and short sentences.
- Explain necessary terminology rather than imposing an absolute jargon ban.
- Preserve informal grade-appropriate voice and inventive naming.
- Keep spelling and spacing out of multi-step model coaching goals where lightweight editor support is sufficient.
- Use the existing native browser spellcheck capability, while verifying its actual behavior for invented and conventional technical terms from development fixtures and at least one unrelated held-out draft. Do not add term-specific correction rules.
- Do not assume that native spellcheck provides spacing cleanup. If dedicated spacing feedback is needed, add a small UI work item and evaluate it separately.
- Do not silently auto-correct student writing.

### Verification

Review every action, hint step, self-check, and stuck step for:

- Grade appropriateness.
- Usefulness without adult decoding.
- Cross-field coherence.
- Answer leakage.
- Student authorship.
- Unnecessary density.

Track Support repairs and structural validation failures as secondary diagnostics. Literal answer-leak strings may be flagged for human inspection where useful, but must not serve as a keyword-only semantic pass/fail check. Verify native spelling and any new spacing support in the browser rather than inferring it from a textarea attribute alone.

### Exit gate

Independent pedagogical review finds the scaffolds usable and appropriately bounded, and the worked-example policy is explicitly reconciled across the contract and implementation. A readability formula, low repair count, or keyword scan alone cannot pass this gate.

---

## Phase 4 — Align Final reflection and complete integrated evaluation

### Objective

Ensure the final summary accurately represents the same draft, requirement status, and revision history used by the round Coordinator.

### Work

- Reconcile Final improvements, regressions, and future areas with the latest round assessment, goal outcomes, narrowing classifications, and requirement coverage.
- Do not reclassify previously meaningful unresolved issues as optional without explanation.
- Preserve narrowing as distinct from goal outcome and problem completion, including the difference between discretionary narrowing and an unmet required deletion. Retain the grounded deleted-text and requirement evidence used by the round contract.
- Avoid comma-prefixed or otherwise confusing evidence fragments; use a complete meaningful excerpt or omit the reference display.
- Retain the concise automatically generated reflection.
- Do not add a required student-authored reflection.
- Keep spelling limitations and source uncertainty honest; do not certify scientific performance.

### Integrated evaluation

Run:

1. The complete mocked suite.
2. Targeted real-model fixtures for:
   - Whole-draft remaining issues.
   - Partial multi-location progress.
   - Discretionary and required narrowing, including their grounded evidence.
   - Sentence boundaries.
   - Agreement and other language patterns.
   - Stopping/Final consistency.
3. An adaptive development replay of the garbage-system essay after batching is available, compared semantically and operationally with the preserved historical run without expecting the same findings or sequence.
4. An adaptive replay of an unrelated held-out informational draft after batching is available, using candidate-only semantic review because it is outside the preserved reference run. If its outputs drive further candidate changes, use new held-out cases before claiming transfer.
5. Representative argument and narrative scenarios with realistic synthetic assignment context, building on the early Phase 1 development and transfer probes.
6. Source-present and source-missing cases.
7. Browser verification of highlights, editing, storage, navigation, native spelling support, any new spacing support, and Finish behavior.
8. Full versioned acceptance evaluation before any promotion decision.

Where corresponding historical data exists, compare against the preserved test run for the dimensions below; otherwise record that no historical control is available and use candidate-only semantic review. Treat output differences as hypotheses for review, not automatic improvements or regressions:

- Semantic accuracy and whole-draft coverage rather than exact-findings reproduction.
- Partial/deletion interpretation and required-assignment/framework coverage.
- Scaffold quality and authorship.
- Review rounds, calls, tokens, and latency for like-for-like workflow scopes.
- Coordinator/Support repairs, invalid references, normalizations, and multi-location integrity.
- Positive, null, and negative outcomes, including configuration and contract differences.

### Exit gate

Technical checks pass, targeted semantic review is acceptable, reference and outcome integrity is preserved, and no known contradiction remains between stopping and Final. Full acceptance and promotion remain separate owner decisions.

Educator review is still required for pedagogical approval; this plan does not establish learner outcomes or authorize student contact.

---

## Recommended first implementation slice

**Phase 0 is complete.** Use `V3_8_3_COMPLETE_RUN_EXTERNAL_REVIEW.md` and its identified source records as the historical comparison reference; no new baseline run is required. Begin **Phase 1** by preparing the versioned development fixtures, reserved held-out transfer set, and candidate prompt/schema selectors. Then:

1. Introduce separate text-observation, goal-outcome, and narrowing contracts, including grounded deleted-text and requirement evidence.
2. Strengthen explicit whole-draft triage without candidate quotas, fixture-derived runtime rules, or mandatory anchor findings, using the five-issue overflow and reviewer-confirmed issue-accountability rules.
3. Add the outcome/route consistency matrix, same-ID live carry-forward candidates, and distinct handling for discretionary closure and required deletion coverage.
4. Preserve and display the new fields through Coordinator, Support, direct response, UI, round state, and history records without auto-selecting carried goals or changing Final interpretation.
5. Distinguish no-issue, work-remaining, and optional-only stopping. Add validated optional-polish output to `direct_response` while retaining the existing student-controlled Finish action.
6. Add mocked contract/UI/history tests and a runtime fixture-leakage scan. Run candidate single-turn development probes, corrected counterfactuals, the existing acceptance regression subset, and post-freeze held-out transfer probes, with repair/reference diagnostics and named protocol-based semantic review. Compare with historical outputs only where corresponding data exists and without requiring exact reproduction. Do not run a full adaptive replay before Phase 2.

That addresses the fundamental problem first: **what the app notices, how it prioritizes meaningful work, and how it judges revision**. Pattern batching should follow immediately afterward, building on that reliable foundation rather than compensating for its absence.
