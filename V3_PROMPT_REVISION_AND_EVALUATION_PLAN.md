# V3 Prompt, Contract, and Evaluation Revision Plan

**Status:** Phases 1–4 and Gate A are implemented with 325 passing mocked checks. The user explicitly authorized the recommended product defaults and complete targeted/full real-model evaluation in both modes; all targeted and full diagnostic runs and their AI-assisted semantic reviews are complete. Gates B and C are not passed, human/accessibility gates remain open, and no deployment is authorized or performed. Outcomes and remaining gates are recorded in `V3_PROMPT_REVISION_IMPLEMENTATION_RESULTS.md`. After the 2×2 pedagogical review, the user explicitly chose the Phase 1 baseline with thinking as the new repository default, superseding the earlier non-thinking default decision without promoting the consolidated prompt or deploying.

**Starting point:** Prompt/schema `v3.6.8`/`v3.6.3`.

**Evidence boundary:** The recorded baseline is 260 passing mocked checks and one technically successful but semantically mixed `v3.6.8` initial-review case. The historical full integrated acceptance artifacts used `v3.6.5`/`v3.6.3` and did not pass all engineering or semantic gates. This plan does not assume that prompt length, non-thinking mode, or any single code path is the established root cause.

## 1. Objectives

1. Align the prompts, model-output schemas, deterministic validation, routing behavior, PRD, and tests.
2. Remove contradictions and redundant prompt guidance without weakening authorship, source-grounding, or human-review protections.
3. Move deterministic metadata handling into code where evidence supports that change, while preserving repeated-reference disambiguation and observable corrections.
4. Evaluate operational reliability and semantic quality separately.
5. Use controlled comparisons before attributing improvements to prompt consolidation or model mode.

## 2. Non-goals and protected behavior

- Do not change the two-agent architecture.
- Do not switch the student runtime to thinking mode automatically.
- Do not weaken target-answer, target-vocabulary, sentence-frame, source, score, readiness, or human-review boundaries merely to reduce repairs.
- Do not normalize or replace Final comparison quotations automatically. Final findings have no paragraph/occurrence metadata; exact-membership and changed-text-overlap validation remain necessary.
- Do not edit the four frozen root V1/V2 fixtures.
- Do not use real student essays or confidential classroom records in the evaluation set.
- Do not treat mocked checks, LLM review, or synthetic outputs as evidence of educator approval, pedagogical effectiveness, or learner outcomes.
- Do not deploy as part of this revision without a separate explicit deployment and retest decision.

## 3. Product decisions to confirm before behavioral changes

### 3.1 Hint length

**Recommended starting point:** Keep the existing 3–5-item validator and define the contract as one concept-restatement item followed by 2–4 procedural items.

This avoids a schema-shape change and matches the current Step 0 design. Align the prompt prose, JSON example, PRD, and tests. A separate `concept_restatement` field remains a future option only if evidence shows that the combined list is confusing.

### 3.2 Ranking precedence and sorting mechanism

**Policy decision required:** Confirm the rule for a draft that has both an accuracy finding and a draft-supported student concern.

**Recommended policy for product/educator confirmation:**

1. Human-review routing overrides normal feedback.
2. Accuracy findings come first.
3. A supported student concern receives next priority.
4. Remaining issues use severity and pedagogical priority, preserving stable within-tier order.

**Recommended implementation mechanism:** Use the no-schema-change option. The Coordinator orders the complete issue list according to the confirmed policy. Python then performs only a stable accuracy partition: accuracy issues move to the front while preserving their relative order, and all non-accuracy issues retain the Coordinator’s relative order. This allows a supported development-level concern to remain ahead of an unrelated reasoning issue.

This deliberately stops deterministic enforcement of `reasoning → development` among non-accuracy issues. The Coordinator owns that semantic ordering, including identification of the supported concern. Do not add `addresses_student_concern` in this phase. An explicit concern flag remains a future schema-changing alternative if evaluation shows that Coordinator ordering is unreliable or a more auditable handoff is needed.

Apply the chosen policy and mechanism explicitly to initial and revision rounds. Do not silently preserve the current mismatch in which the prompt mentions Round 1 while Python severity-sorts every round. If another policy or mechanism is selected, encode and test it consistently instead.

### 3.3 Boundary-route field defaults

**Recommended starting point:** On `ask_clarification` and `teacher_review`, return empty ordinary assessment collections: `strengths`, `issues`, `framework_coverage`, `source_limitations`, and `selected_goal_observations`. Preserve the fields required for clarification or human review.

On `teacher_review`, `working_genre`, `genre_confidence`, and `genre_basis` may all be empty even when a genre might be inferable. The model need not perform genre inference solely to populate a human-review handoff. Apply this rule consistently in the prompt, normal validation, safety fallback, and tests.

On `ask_clarification`, retain the existing genre contract: `working_genre` and `genre_confidence` may be empty when essential genre clarification prevents a responsible working choice. Do not require empty genre fields for unrelated clarification questions.

Normal revision routes must still return exactly one observation per selected goal. A model-selected clarification limit must not bypass the application’s two-answer policy.

### 3.4 Sentence starters and vocabulary

Defer broad changes to formality, Rank-1 starter requirements, and vocabulary policy until targeted evaluation and educator review. Prompt-only starter edits are insufficient because a deterministic allowlist also exists.

Treat the literal `This evidence/detail matters because ____.` variant as a mechanical cleanup, not a broad pedagogical policy change. In Phase 3, remove that slash variant from the prompt and allowlist while retaining the already separate `This detail matters because ____.` and `This evidence matters because ____.` forms. Synchronize and test both changes.

Do not adopt a blanket prohibition on every corrected spelling without a product/educator decision; that is broader than the current routine-spelling and typo-list guidance.

## 4. Implementation phases

### Phase 1 — Align objective contracts and routing

#### Scope

1. **Hint contract**
   - State “3–5 total items: one concept restatement followed by 2–4 procedural steps” consistently in the Support prompt and JSON example.
   - Update the corresponding PRD requirements and acceptance descriptions.
   - Keep `HintOutput.steps` at 3–5 unless the confirmed product decision says otherwise.

2. **Regression field**
   - Change the Coordinator prose from `regressions=true` to `regression=true`.
   - Keep the schema field singular.

3. **Ranking**
   - Implement the confirmed precedence rule in the Coordinator prompt.
   - Replace strict all-tier deterministic sorting with the stable accuracy partition specified in Section 3.2: hoist accuracy issues and otherwise preserve Coordinator order.
   - Make clear that non-accuracy severity/pedagogical ordering and supported-concern identification are Coordinator responsibilities, not deterministic checks.
   - Apply the same confirmed policy to initial and revision rounds.
   - Preserve Coordinator-to-Support candidate ordering after the accuracy partition.
   - Do not add a concern-specific model-output field in this phase.

4. **Boundary outputs**
   - Document expected empty/default fields for clarification and teacher review.
   - Add deterministic validation only where it matches the confirmed contract.
   - Preserve human-review reasons, categories, and evidence without returning partial writing assessment.

5. **Clarification-limit ownership**
   - Separate Coordinator model-output flag categories from internal application categories.
   - Allow the model to select only `none`, `concerning_content`, or `serious_discouragement` as appropriate.
   - Retain `clarification_limit` internally for the deterministic graph node.
   - Reject or neutralize model-selected `clarification_limit` before safety fallback; do not relabel it as concerning content.
   - Ensure the safety fallback cannot preserve an early model-selected clarification limit.
   - Keep deterministic escalation after the application’s clarification boundary.
   - Increment both the prompt version and model-output schema version for the restricted Coordinator contract. Update affected Coordinator fixtures, retain internal graph tests for deterministic escalation, and preserve historical artifacts under their original versions.

6. **Final source grounding**
   - Add concise instructions to use only supplied source material, avoid source-accuracy claims without a source, avoid inventing framework requirements, and preserve uncertainty.
   - Retain existing exact-reference, unchanged-draft, and changed-text-overlap guards.
   - Do not add Final-reference location normalization.

#### Mocked tests

- Hint lists of 2 and 6 items fail; 3, 4, and 5 pass.
- Prompt and JSON examples describe the same 3–5-item contract.
- Mixed accuracy/concern cases follow the confirmed order on initial and revision rounds, including a development-level supported concern ahead of an unrelated reasoning issue.
- The deterministic sort hoists accuracy issues stably and otherwise preserves Coordinator order; it does not re-sort non-accuracy issues by severity.
- Unsupported concerns do not create issues or change ordering.
- Equal-severity ordering is stable, and Support preserves the resulting candidate order.
- The Coordinator issue schema does not gain an `addresses_student_concern` field in this phase.
- The prompt contains `regression=true` and not the plural field-name instruction.
- Clarification and teacher-review routes reject ordinary assessment collections when the contract requires them to be empty.
- Teacher review permits empty `working_genre`, `genre_confidence`, and `genre_basis`; unrelated clarification does not require empty genre fields.
- Normal revision routes still require every selected-goal observation.
- A direct model-selected `clarification_limit` after zero or one answer cannot trigger early teacher review.
- The deterministic boundary still produces `clarification_limit` after the required clarification history.
- Malformed responses containing genuine human-review flags still receive safe handling without misclassifying a clarification-limit request as concerning content.
- Final unchanged drafts cannot produce improvements or regressions.
- Final findings still require exact references and actual-change overlap.
- Missing-source Final outputs cannot make prohibited source-accuracy claims; supplied-source outputs remain bounded.

#### Exit criteria

- All new and existing mocked tests pass.
- Prompt, code, PRD, and tests describe the same contracts.
- No real-model call is needed to complete this phase.

### Phase 2 — Scope deterministic reference recovery

#### Scope

1. Retain the current unique-reference recovery for Coordinator issues.
2. Add analogous recovery for `framework_coverage` only when:
   - `status="present"`;
   - the exact reference occurs exactly once in the full draft;
   - the reference lies within one blank-line-separated block; and
   - the supplied location is invalid.
3. Record framework corrections separately with framework, component, old location, and new location.
4. Leave `status="issue"` entries, repeated references, missing references, cross-paragraph references, Support fields, and Final references unchanged.
5. Preserve the existing one-repair boundary for cases that cannot be recovered safely.

#### Mocked tests

- A unique present-framework reference with a title-block off-by-one error is corrected without a model repair.
- A valid present-framework location is unchanged.
- Repeated, missing, and cross-paragraph references still trigger bounded repair.
- Issue-status framework entries retain empty references and null locations.
- Corrections are logged once with the correct component identity.
- Highlighting and framework rendering use the corrected location.
- Final comparison outputs are not modified by this recovery.

#### Exit criteria

- Recovery is limited to unambiguous exact text.
- Every correction is observable in execution state/logs.
- No silent quotation replacement occurs.

### Phase 3 — Consolidate and clarify the prompts

#### Coordinator prompt

- Preserve the generalizable language principles: prioritize meaning, distinguish distraction from obscured meaning, use one recognizable pattern, and ensure the quoted reference exhibits the described error.
- Preserve speculative-process guidance and the distinction between invented proposals and real-world factual assertions.
- Remove duplicated or patch-like wording only where the remaining text still states the general principle.
- Keep source, routing, human-review, and revision-observation requirements explicit.
- Do not claim that semantic language-pattern compliance is deterministically enforced unless a corresponding validator actually exists.

#### Support prompt

- Make `CLAIM ANCHORING` genre-sensitive: use the draft’s claim, central idea/topic, or key moment as appropriate; if the focus is unclear, refer to the topic or existing wording rather than inventing a claim.
- Replace the inaccurate “gerund subjects” terminology with a direct instruction to avoid long, multi-action sentences and split locating, reasoning, and connecting into manageable steps.
- Retain concrete-first hints, concept restatement, reader-facing rationales, and the ban on generic-only guidance.
- Consolidate repeated authorship/frame rules in one clearly named section.
- Move the `stuck_step` opening-frame prohibition alongside the other frame rules rather than inside language-mechanics guidance.
- Keep Support focused on the Coordinator’s finding without assuming that one-pattern compliance has been deterministically validated.
- Retain permission for a brief rule or meaning note and the student-authorship boundary.
- Avoid introducing new assigned-topic vocabulary or target answers while clarifying the positive purpose of vocabulary options.
- Remove the literal `This evidence/detail matters because ____.` starter from the prompt and deterministic allowlist while retaining the separate detail and evidence forms.

#### Mocked tests and static checks

- Prompt tests cover genre-neutral claim/focus guidance, the corrected instruction terminology, and consolidated frame ownership.
- Mocked Support fixtures cover argument, informational, narrative, imaginative informational, missing-claim, and language-pattern cases.
- Candidate IDs and Coordinator issue coverage remain exact.
- Exact references and source limitations are preserved under the current schema unless Phase 4 changes it.
- Approved abstract starters pass; on-topic/completed frames and completion placeholders outside the starter still fail.
- The separate detail and evidence starters pass, the literal slash variant fails, and the prompt no longer advertises it.
- Existing drafts, source material, and teacher directions remain model inputs rather than instructions.

#### Exit criteria

- No protected behavior is removed without an explicit documented decision.
- The revised prompt is versioned independently from the baseline for comparison.
- The full mocked suite passes before any real-model evaluation.

### Phase 4 — Analyze repairs before changing Support’s schema

#### Existing-artifact analysis

Deduplicate cumulative logs by the established execution identity and categorize each attempted validation failure by agent, scenario, field, and root cause:

1. JSON/schema mismatch.
2. Coordinator reference/location mechanics.
3. Support echo mismatch.
4. Genuine authorship leak, including target frames and target-like vocabulary.
5. Structural validator false positive, such as a quoted ellipsis.
6. Grounding or source-limit violation.
7. API/empty-response failure separately from validation failure.

Report counts and denominators without treating repair count as a quality score. Preserve invalid-response evidence and do not collect hidden reasoning.

#### Decision rule

- If Support echo mismatches are a meaningful operational burden, prototype deterministic injection as a separately versioned schema change.
- If failures are predominantly semantic or validator false positives, defer the schema refactor and address those causes directly.
- Prompt simplification may still be evaluated without claiming that echo removal is the largest reliability gain.

#### Conditional Support schema refactor

If adopted:

1. The model returns only goal identity and pedagogical text.
2. Python injects candidate references/locations, hint passage reference, goal status/carry-forward, and source limitations by validated `goal_id`.
3. The application state delivered to storage/UI retains its existing shape.
4. Raw model output remains distinguishable from deterministic post-processing in logs.
5. Persistent Support validation failure still produces no partial feedback.
6. Update the model schema, prompt, Support-only evaluation handoffs, compatibility tests, and schema version together.

#### Conditional tests

- Missing, duplicate, or unknown goal IDs fail rather than receiving partial merges.
- Injected fields exactly match the Coordinator handoff.
- UI highlighting, goal feedback, source warnings, storage, restoration, and history retain their existing behavior.
- Raw and merged outputs are distinguishable in observability.
- Older persisted rounds remain readable or receive an explicit compatible migration path.

## 5. Testing strategy

### Automated mocked verification

Run the focused tests after each phase and the complete suite before model evaluation:

```bash
pytest tests/test_revision.py tests/test_agents.py tests/test_graph.py tests/test_app.py
pytest
```

Use mocked responses and temporary databases. Cover all genres, source-present/source-missing cases, known/custom frameworks, explicit genre correction, strong drafts, selected/deferred goals, clarification boundaries, human review, unchanged/small changes, overlap groups, storage restoration/deletion, and final grounding.

Do not treat a higher check count as evidence of better writing feedback. Record actual pass/fail results and any unrelated pre-existing failures separately.

### Local workflow verification

Exercise the real local application with synthetic inputs and the persisted review state:

1. Initial review through Coordinator and Support.
2. Recommended-goal selection and alternative reveal/hide.
3. Correct highlights after any deterministic normalization.
4. Student editing and revision submission.
5. Selected-goal feedback and new/regression handling.
6. Unchanged and small-change confirmation.
7. Finish confirmation and original-to-final reflection.
8. Refresh/restoration, failed-review retry, and failed-final retry without duplicate snapshots.
9. Full keyboard flow and actual screen-reader review remain separate human/accessibility checks, not inferred from automated accessibility-tree output.

Confirm that Choose, hints, Show less, I’m stuck, editing, and diff generation make no additional model calls.

## 6. Controlled real-model evaluation

### 6.1 General controls

- Use only versioned synthetic fixtures and frozen Coordinator handoffs for Support-only comparisons.
- Record model, prompt/schema/fixture versions, request settings, calls, repairs, observed tokens, per-call latency, graph/service latency, errors, fallbacks, and reference normalizations.
- Use the evaluator’s current authorization and budget interface. Establish run scope and resource limits before execution; this plan itself does not require or perform a billable run.
- Keep one bounded repair per agent where that is part of the production contract.
- Never collect raw hidden reasoning.
- Preserve positive, null, mixed, and negative findings.

### 6.2 Support 2×2 comparison

**Purpose:** Estimate prompt and mode effects on Support without Coordinator variance.

**Factors:**

- Prompt: the **Phase 1 contract-aligned baseline** versus the **Phase 3 consolidated/genre-neutral candidate**. Do not label the original `v3.6.8` prompt as the sole baseline if Phase 1 wording or contracts have changed.
- Mode: non-thinking versus thinking.

The original `v3.6.8` prompt may be retained as a separate descriptive historical comparator, but it is not part of the causal Phase 1-versus-Phase 3 comparison unless all shared contracts and validators are demonstrably identical.

**Handoffs:** Use an exploratory set of 12–18 frozen Coordinator handoffs covering argument, informational, imaginative informational, narrative, initial and revision rounds, language conventions, missing claims, first-person references, source-present/source-missing cases, and multi-action hints.

**Constants:**

- Same base model and frozen handoffs within each pair.
- Same Phase 1-aligned output schema, validators, and model-visible handoff representation within the comparison.
- Same repair policy and per-request output settings.
- Non-thinking uses temperature 0.
- Thinking omits temperature and uses the recorded fixed reasoning-effort setting; do not claim temperature 0 applies to thinking.
- Presentation and storage behavior remain unchanged.
- Do not introduce the conditional Phase 4 Support schema refactor into this comparison; evaluate that separately or hold it constant in an additional controlled arm.

Add an explicitly named evaluation-only consolidated-prompt arm rather than changing production automatically. Repeat paired runs when resources permit; with small samples, treat latency percentiles and variability as descriptive rather than stable population estimates.

### 6.3 Coordinator-targeted evaluation

Evaluate Coordinator changes separately from the Support comparison. Include:

- Accuracy/concern ranking conflicts on initial and revision submissions.
- Early model-selected clarification limit versus the legitimate two-answer boundary.
- Boundary-route empty-field behavior.
- Unique issue and present-framework locations, including title blocks and repeated passages.
- Imaginative informational drafts and real-world assertions.
- Strong drafts that should not receive manufactured issues.
- Final source-present/source-missing grounding and unchanged-draft reflection.

Do not use Support-only handoffs to claim validation of these Coordinator behaviors.

### 6.4 Integrated acceptance

After targeted checks, run the full versioned synthetic acceptance set on the integrated candidate using the student-runtime non-thinking configuration. A thinking run is a separate comparator, not an automatic default change.

Compare against the preserved `v3.6.5` failed baselines cautiously. Prompt, schema, fixture paths, and scenario paths may differ; do not attribute all differences to one prompt edit. If a fixture assumes a candidate count or revision path that the model appropriately does not produce, record a harness/scenario incompatibility rather than forcing model output.

### 6.5 Human semantic review

Use complete-context, blinded review where feasible, following the educator protocol. Separate automated structural checks from human judgments.

Before executing the comparison, extend the existing educator protocol with a lightweight anchored review guide. Reuse its **Meets / Needs refinement / Unacceptable** ratings and Critical/Major/Moderate/Minor severity categories; do not introduce a competing Pass/Borderline/Fail taxonomy. Retain the protocol’s existing authorship-failure checks and add concrete synthetic anchor examples for authorship boundaries, cross-field coherence, and multilingual-learner readability/tone. Develop and calibrate these anchors with educator input where feasible, record disagreements, and do not aggregate them into an unvalidated numerical quality score.

Review at least:

1. **Authorship:** target ideas, mechanisms, vocabulary, frames, replacement prose, or answer menus.
2. **Cross-field coherence:** consistent scope among revision action, hint steps, self-check, starter, and stuck step.
3. **Grounding:** exact quotations, supplied-source limits, and no invented claims or requirements.
4. **Genre appropriateness:** no claim invention in narratives or claim-less drafts and no narrative citation/counterclaim demands.
5. **Meaningfulness and priority:** no manufactured transition/conclusion/mechanics goals; appropriate treatment of strong drafts and student concerns.
6. **Readability and tone:** warmth, sentence complexity, repetition, and usefulness for the intended grades 5–7 multilingual learners.
7. **Revision/final consistency:** observations and reflections match actual text changes and do not contradict the immediately preceding review.

An LLM may assist with screening but cannot substitute for the pending educator gate. Disagreements and uncertain cases remain visible.

## 7. Metrics and interpretation

### Operational metrics

- Attempted and successful calls.
- Scenario completion and errors by cause.
- Repairs by category and agent.
- Persistent fallbacks and partial-output prevention.
- Deterministic normalization counts by reference type.
- Observed tokens and actual per-call/per-scenario latency.

### Semantic metrics

- Authorship violations and uncertain cases.
- Grounding/reference concerns.
- Cross-field consistency.
- Genre and task alignment.
- Age-appropriate tone/readability ratings.
- Candidate meaningfulness and ranking judgments.
- Final reflection consistency.

Do not convert these into an unvalidated numerical quality score. Fewer repairs do not necessarily mean better feedback; a structural pass can conceal a semantic violation.

### Interpretation rules

- Improvement under the consolidated prompt supports a prompt-design contribution in the sampled cases, not a universal prompt-length rule.
- A thinking advantage supports a mode-dependent difference under the tested conditions, not proof of a fundamental capacity bottleneck.
- Prompt and mode effects may coexist or interact.
- Small stratified samples do not support broad subgroup or P95 claims.
- Operational completion is not semantic acceptance, educator approval, or learner-outcome evidence.

## 8. Acceptance and progression gates

### Gate A — Contract and mocked engineering

- Contracts are internally consistent.
- Focused and full mocked tests pass.
- Corrections and routing decisions are observable.
- No protected safety/authorship behavior was weakened silently.

### Gate B — Targeted model behavior

- Intended targeted paths are exercised.
- No unresolved critical authorship, human-review, or source-grounding violation remains in the reviewed candidate.
- Validator false positives and semantic failures are reported separately.
- Null or mixed findings remain disclosed.

### Gate C — Integrated model behavior

- The full candidate run completes its intended paths without unexplained fallback or unreported scenario errors.
- Fixture incompatibilities are distinguished from application failures.
- Strong-draft, clarification, revision, and final-comparison regressions are reviewed.
- The prior failed baseline remains preserved.

### Gate D — Human and accessibility review

- Educator review addresses pedagogical and language-support decisions.
- Full keyboard and actual screen-reader checks are completed or explicitly remain open.
- No pedagogical-effectiveness or learner-outcome claim is made without suitable studies.

### Gate E — Deployment decision

- Deployment occurs only after a separate explicit decision and retest of the exact deployable artifact.
- The version/footer marker is not treated as proof that every flow is deployed or verified.

## 9. Versioning, documentation, and deliverables

For each implementation stage:

1. Increment the prompt version for prompt changes and the schema version for model-contract changes.
2. Record fixture and evaluation-arm versions.
3. Keep current and experimental production behavior separate until a decision is made.
4. Update the PRD, README, changelog, coding guidance, and repository guidance where actual behavior changes.
5. Preserve evidence artifacts under the established git-ignored data locations; do not commit databases, raw evidence, screenshots, credentials, or personal information.
6. Record adopted changes, rejected recommendations, null/mixed results, costs/usage, and remaining gates.

Expected implementation deliverables are:

- Aligned prompt and contract definitions.
- Focused and full mocked-test results.
- Scoped deterministic reference handling with observable corrections.
- A consolidated prompt candidate with protected boundaries intact.
- A repair-category analysis informing the Support-schema decision.
- Controlled Support and Coordinator evaluation artifacts.
- A protocol-consistent anchored review guide for authorship, cross-field coherence, and readability/tone.
- Full integrated acceptance and semantic-review records.
- Explicit remaining human, accessibility, and deployment gates.
