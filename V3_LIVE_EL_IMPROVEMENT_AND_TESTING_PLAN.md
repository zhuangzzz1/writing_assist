# V3 Live EL Revision Review — Improvement and Testing Plan

**Date:** 2026-11-15<br>
**Revision:** Experiment-first plan refined after two external reviews<br>
**Status:** Engineering investigation implemented under separate user authorization; integrated acceptance and human gates remain open. No deployment occurred.<br>
**Primary evidence:** `data/evidence/v3_live_deployed_el_two_revision_rounds_20261114T181633Z.jsonl`<br>
**Reviewed deployment:** commit `04d61af`, V3 interface<br>
**Product contract:** `PRD_V3_ITERATIVE_REVISION.md`<br>
**Implementation results:** `V3_LIVE_EL_IMPLEMENTATION_RESULTS.md`

## 1. Purpose and Decision Rule

This plan converts a five-essay live review into a proportionate investigation and verification program. It is not a commitment to a broad architecture change. Its purpose is to determine which observed behaviors are actual contract failures, which are acceptable coaching judgments, and which require no production change.

The investigation covers:

1. One revision-submission workflow interruption with unconfirmed cause.
2. One disputed beach sequence in which a previously suggested run-on issue disappeared before `direct_response`.
3. Hints whose wording may cross the student-authorship boundary.
4. Grounding questions involving observation, inference, evidence, and source limitations.
5. Candidate rationales and partial-goal continuity.
6. Diagnostic and evaluation coverage gaps.

The default is the **null hypothesis**: the current behavior may be adequate, and an observed difference is not automatically a defect. Each workstream must include an acceptable no-change outcome. Implementation is justified only by a reproduced failure, a clear existing-contract violation, or a targeted experiment showing benefit without unacceptable regressions.

The objective is not to increase revision suggestions, make students polish every sentence, or preserve every old candidate indefinitely. The objective is accurate, grounded, student-controlled feedback and recoverable workflow behavior.

This document supplements existing feedback-quality and prompt-review plans. Current code and `PRD_V3_ITERATIVE_REVISION.md` remain authoritative. `EDUCATOR_REVIEW_PROTOCOL.md` remains a separate human-review process.

## 2. Evidence Base and Review Disposition

### 2.1 Observed session scope

The source JSONL records:

- Five synthetic sixth-grade essays: two arguments, two narratives, and one informational draft.
- Five completed initial reviews and ten completed revision submissions after recovery.
- Fifteen recorded review results: thirteen `normal_feedback` and two `direct_response`.
- Seventeen selected goals and seventeen expanded hints.
- Seventeen selected-goal observations, all labeled `specific_improvement`.
- One neutral small-change confirmation.
- One workflow interruption with no confirmed cause.
- No visible API errors, clarification screens, or final reflections.
- No assignment prompts or supplied source passages.

The persona intentionally made short, imperfect, hint-guided revisions and followed only selected goals. Uniformly positive observations are therefore expected sample behavior, not an estimate that the model always recognizes improvement.

This is a hypothesis-generating sample. It does not justify a predetermined number of additional cases. Begin with existing acceptance scenarios and a small set of targeted contrasts; expand only when failures recur, results are ambiguous, or reviewer disagreement prevents a decision.

### 2.2 Evidence labels

- **Observed output:** Text or workflow behavior directly present in the log.
- **Contract question:** A possible mismatch with the PRD that still requires review.
- **Code-backed hypothesis:** An implementation path could contribute, but causation is unproven.
- **Disputed case:** More than one pedagogical interpretation is plausible.
- **Proposed experiment:** A comparison that has not yet been run.
- **Adopted change:** A change supported by the applicable decision gate. No changes are adopted merely by appearing in this plan.

### 2.3 What the evidence cannot establish

This session cannot establish pedagogical effectiveness, learner motivation, English proficiency, writing achievement, educator approval, accessibility compliance, or performance at scale. It cannot provide token counts, repair counts, per-call latency, raw Coordinator JSON, or hidden reasoning.

The source log is a qualitative baseline only. Do not combine its visible-output counts with unrelated artifacts as though they were one controlled experiment. Do not infer operational baselines from it.

### 2.4 Relevant implementation facts

The relevant local implementation files had no diff from reviewed commit `04d61af` at analysis time. In that implementation:

- Revision Coordinator payloads include current, original, and immediately previous drafts, a deterministic diff, selected goals, and self-reports, but not earlier unselected findings (`agents/assessment_coordinator.py:189-221`).
- The Coordinator is instructed to review the whole current draft and may route to `direct_response` only when no meaningful actionable issue remains (`agents/prompts.py:29-37`).
- Support is prohibited from supplying assigned-topic explanations, narrative details, or other target responses (`agents/prompts.py:106-139`).
- Existing tests validate structure, exact references, and mocked routing; they do not establish real-output semantic quality.
- `scripts/evaluate_v3.py` is a service-level real-model runner, not a deployed-browser test.
- `scripts/simulate_personas_v3_5_0.py` is service-level persona evidence, not browser evidence.
- `tests/test_app.py` uses Streamlit AppTest and complements rather than replaces real-browser checks.
- Round input and result states are stored as JSON dictionaries (`storage/sqlite_storage.py:621-622`). Additive state fields may be rollback-compatible, but this must be tested rather than assumed.

### 2.5 External review decisions incorporated here

**Accepted:**

- Use experiment-first, proportionate changes.
- Do not make persistent state the first GC intervention.
- Decouple implementation and targeted testing across workstreams.
- Start accessibility review immediately and repeat it with UI changes.
- Define resources, authorization, semantic-review roles, and rollback tests.
- Treat beach and octopus as disputed cases with possible null outcomes.

**Rejected or narrowed:**

- No fixed requirement for 20–30 or 50 additional cases. Case count follows unresolved evidence, not an arbitrary quota.
- Do not ship GC first; it is currently more speculative than several prompt-only concerns.
- Do not require students to acknowledge unresolved issues before stopping.
- Do not remove human gates as a way to justify educator, accessibility, or pedagogical claims.
- Do not turn all semantic observations into universal zero-defect claims. Separate reviewed contract violations from quality monitoring.

## 3. Product Invariants and Stopping Policy

All work must preserve these requirements:

1. Keep the two model-driven agents. Do not add an agent to compensate for a context or prompt defect.
2. Preserve student-authored revision. No one-click insertion, automatic polishing, completed target explanation, or assigned-topic answer menu.
3. **Students may stop after any completed review, with or without unresolved candidates.** Finish must remain available during normal feedback as well as direct response (`PRD_V3_ITERATIVE_REVISION.md:365-369`).
4. `direct_response` is a routing statement that no meaningful actionable issue remains; it is not the mechanism by which a student chooses to stop (`PRD_V3_ITERATIVE_REVISION.md:421-423`).
5. A student choosing Finish with known optional issues is valid. It does not require acknowledgment, deferral tracking, or a no-issues claim.
6. Do not convert a round count, small change, support-button use, or imperfect revision into pedagogical completion or an emotional judgment.
7. Preserve whole-draft review, human-review boundaries, exact references, bounded repair, and immutable snapshots.
8. Keep source availability deterministic. Never claim source or factual verification without adequate evidence.
9. Hint display, goal selection, editing, and diff generation must not add model calls.
10. Use synthetic writing only. Do not expose hidden reasoning or add real student data to evaluation artifacts.

### Operational meaning of “meaningful”

Use `PRD_V3_ITERATIVE_REVISION.md:285-291`: a meaningful issue affects the central idea or task, genre or teacher requirements, reader understanding, or a recognizable pattern. A localized issue may matter when it affects a critical claim, source interpretation, or clarity. An isolated convention is not meaningful merely because it can be corrected.

Relative priority alone does not justify `direct_response`: lower-priority meaningful issues are still meaningful. A previously suggested issue may instead be dropped when the current text or context shows it is resolved or below that threshold, or when reviewer adjudication determines that the original candidate was too aggressive.

Meaningfulness remains interpretive. When a disputed judgment could justify persistent state or another architecture change, seek two independent educator reviews where feasible and adjudicate material disagreement under Section 7.3. If the judgment remains unresolved, label it `uncertain` and do not use that case alone to justify architecture work. Two reviewers reduce uncertainty; they do not make the judgment objective.

## 4. Proportionate Scope and Priorities

| ID | Investigation priority | Current classification | Initial scope | No-change condition |
|---|---|---|---|---|
| WF | P0, independent | One observed incident; cause unknown | Bounded reproduction and diagnostics | Unreproduced after bounded investigation; monitor without speculative rewrite |
| AX | P0, continuous | Existing open human gate | Baseline audit and per-UI-change checks | Not applicable; report actual status |
| EV | P0, enabling | Diagnostic infrastructure gap | Selection controls and evidence schema before controlled experiments | Existing controls suffice if they can select and verify intended goals |
| GC | P1 experiment | Disputed beach case; code-backed context hypothesis | Non-persistent three-arm comparison | Current or generic-prompt behavior is adequate, or history adds no benefit |
| SA | P1 targeted review | Observed hint wording; possible contract violations | Independent prompt and semantic-review experiments | Reviewers judge hints student-authored and sufficiently specific |
| FG | P1 targeted review | Cell-phone concern; disputed octopus case; source-consistency question | Independent grounding contrasts | Bounded inference is judged appropriate and no verification overclaim exists |
| CQ | P2 targeted review | Observed rationale concerns; possible moving-target feedback | Independent candidate-quality contrasts | Existing rationales and continued goals are judged accurate and clear |

P0 denotes investigation or prerequisite work, not confirmation of a production defect. Workstreams may proceed independently. No workstream other than WF requires a broad state or storage rewrite in its initial stage.

## 5. Resources, Authorization, and Cost Control

### 5.1 Required roles

Names and calendar commitments must be supplied by the project owner before the corresponding work is scheduled. This plan does not invent staff availability.

| Role | Responsibility | Current assignment status |
|---|---|---|
| Project owner | Approves scope, billable runs, deployment, and any claim language | Unassigned in this plan |
| Engineer | Reproduction, implementation, automated tests, AppTest, and browser setup | Unassigned in this plan |
| Accessibility reviewer | Baseline and UI-change keyboard/screen-reader review | Unassigned; existing gate remains open |
| Educator reviewer | Meaningfulness, grade appropriateness, authorship, and disputed-case review | Unassigned; existing gate remains open |
| Adjudicator | Resolves material reviewer disagreement | Required only when disagreement occurs |

One person may hold multiple roles if available, but a single reviewer must be reported as single-review evidence rather than consensus. Single-review findings may guide low-risk prompt experiments. A disputed judgment used to justify architecture or a release decision requires a second independent educator review where feasible; without it, label the conclusion provisional and leave the related human gate open. Do not adopt persistent state solely on one unresolved reviewer's judgment.

If educator or accessibility reviewers are unavailable, non-billable engineering investigation may continue; the corresponding human gate remains open and no related approval claim is made.

### 5.2 Billable-run authorization record

Every real-model run requires an explicit record before execution:

- Approver and authorization date.
- Experiment or release identifier.
- Exact scenario IDs and modes.
- Maximum scenario count.
- Maximum model-call count, total-token cap, or monetary cap.
- Output/evidence location.
- Whether targeted reruns are covered by the same authorization.

Use the existing explicit non-thinking, temperature-0 student runtime. Thinking is a separate comparator only when a specific authorized comparison requires it. Historical token counts may inform a cap but are not cost guarantees.

### 5.3 Proportionality checkpoints

Apply these questions when entering each workstream and again before every escalation:

1. What observed failure or contract question remains?
2. What is the smallest experiment that can resolve it?
3. Can existing fixtures and mocks answer it without model cost?
4. What is the expected benefit relative to state, repair, review, and maintenance cost?
5. What result would lead to no production change?

Record the entry answer before detailed implementation. Stop or defer work when the answer does not justify escalation.

### 5.4 Effort estimation and scheduling

A defensible calendar duration is not available until roles are assigned, fixture counts are known, authorization lead time is understood, and the scope of any reproduced WF or adopted GC change is determined. Do not describe the effort as two weeks, three months, or any other unsupported calendar commitment.

Use these relative planning estimates to allocate initial capacity:

| Work package | Relative engineering effort | External dependency |
|---|---|---|
| EV selection controls and review records | Small: localized runner/fixture changes and mocks | None for mocked work |
| WF bounded reproduction | Small: bounded local investigation | Browser availability; no model run required for mocks |
| WF targeted fix, only if reproduced | Small to medium depending on reproduced path | Browser and accessibility review for UI changes |
| GC three-arm experiment | Medium: harness, controlled outputs, and review records | Educator review and billable authorization |
| Each SA, FG, or CQ prompt experiment | Small to medium per independent change | Targeted semantic review and billable authorization |
| Integrated acceptance and browser verification | Medium | Authorization, browser, and relevant human reviewers |
| Persistent GC state, only if adopted | Additional medium scope including compatibility and rollback | Second-review/adjudication policy and deployment approval |

Here, **small** means a localized change with focused tests; **medium** means multiple coordinated files, real-output review, or compatibility coverage. These are relative sizing assumptions, not committed durations.

Before scheduling, the project owner must convert the applicable rows into calendar ranges using actual staff capacity, reviewer availability, scenario counts, and authorization delays. Record engineering time separately from waiting time and human-review time. Re-estimate only at a decision gate when scope changes.

## 6. WF — Independent Submission and Recovery Investigation

### 6.1 Evidence and desired outcome

**Observed output:** The first homework revision did not produce a review on initial attempts. A later pointer submission returned to Choose with zero selected goals and Review 1 displayed; the edited draft was no longer visible. A repeated submission succeeded after reselection and re-entry (source log lines 5–7).

**Desired outcome:** One deliberate revision submission produces one traceable snapshot and review lineage. Across reruns, failures, and retries, the student retains submitted text, unsubmitted editor text, selected goals, and an honest review status.

WF is independent of prompt and content experiments. An unreproduced WF incident must not block SA, FG, CQ, or non-persistent GC experiments.

### 6.2 WF-0: Bounded reproduction before behavior changes

The project owner and engineer define one bounded investigation cycle before starting. If the incident remains unreproduced at the end, do not extend the search indefinitely merely to justify a fix.

Record for each attempt:

- Browser, viewport, target, and commit.
- Pointer or keyboard activation.
- Draft and revision identifiers.
- Small-change notice behavior.
- Visible stage before and after submission.
- Snapshot count, round status, thread ID, and composition revision number.
- Whether a model call began and completed.
- Console or network error summary without secrets or hidden reasoning.

Run locally first:

1. Normal pointer submission.
2. Keyboard-only submission.
3. Rapid repeated activation during an active submission.
4. Streamlit rerun before and during submission.
5. Small-change confirmation followed by Continue review.
6. Model failure after snapshot creation.
7. Storage failure before snapshot creation.
8. Refresh after completed and failed reviews.

Classify results as:

- **No app event reached:** investigate harness or control availability.
- **Snapshot not created:** investigate pre-persistence state and error handling.
- **Snapshot created, review failed:** inspect failed-round recovery and retry.
- **Review completed, stale UI shown:** inspect invocation/session restoration.
- **Duplicate snapshot or review:** inspect submission identity and repeated events.

Automation timing alone does not establish an application defect.

### 6.3 WF-1: Change only an indicated path

Inspect and change only as the reproduced cause requires:

- `ui/layout.py`: callbacks, invocation state, editor state, selection, and restoration.
- `langgraph_core/graph.py`: snapshot-before-review and retry lifecycle.
- `storage/sqlite_storage.py`: recovery or idempotency only if evidence demonstrates a storage need.

Requirements for an adopted fix:

- Preserve stable identity for one logical submission through confirmation and retry.
- Never create a second snapshot merely to retry a saved review.
- Do not replace unsubmitted editor text with an older snapshot silently.
- Restore the latest completed or failed round rather than an earlier review.
- If no snapshot was saved, say so and preserve copyable editor text.
- Keep diagnostics bounded and free of hidden reasoning.

Do not add distributed locking, a new storage backend, or a broad session rewrite for one unreproduced event.

### 6.4 WF tests

**Mocked/unit:**

- WF-01: Normal revision creates one snapshot and one completed round.
- WF-02: Unchanged/small-change confirmation creates no snapshot before confirmation.
- WF-03: Model failure after revision snapshot creation preserves exact text and selected goals.
- WF-04: Retry reuses saved thread and snapshot without duplication.
- WF-05: Failed initial and revision submissions show their correct recovery states.
- WF-06: Restoration selects the latest completed or failed round.
- WF-07: Unsubmitted edits survive history and step navigation.
- WF-08: Existing databases and saved rounds restore without destructive migration.

**AppTest/browser:**

- WF-09: Pointer and keyboard submission preserve equivalent state.
- WF-10: Repeated activation cannot duplicate one logical submission.
- WF-11: Refresh after completion restores latest draft, goals, feedback, and review number.
- WF-12: Refresh after failure preserves copyable text and retry.
- WF-13: Successful retry displays exactly one new reviewed revision.

### 6.5 WF decision gate

- Every reproduced failure receives a classification and targeted regression test.
- An adopted fix must pass full mocked tests and the affected real-browser flow.
- No tested path may lose text or silently restore an earlier review.
- Retry must not duplicate snapshots or model work beyond the deliberate retry call.
- If unreproduced, keep the incident open with its original uncertainty, improve only justified diagnostics, and claim no fix.

## 7. EV — Enable Controlled Experiments Before New Model Runs

### 7.1 Goal-selection controls

The acceptance runner currently selects the first candidate or first three. Controlled unselected-goal experiments require deliberate subset selection.

Before new controlled revision experiments, extend the fixture/runner design if needed so it can:

- Select an explicit subset while preserving the one-to-three limit.
- Validate that the intended goals were actually selected.
- Record selected goal IDs, titles, and exact references.
- Reject duplicate, unknown, or out-of-range selections.
- Keep existing fixtures compatible.
- Fail rather than silently fall back to the first candidate.

Update `ui/scenarios.py`, `scripts/evaluate_v3.py`, and fixture-loading tests together if this capability is added. EV selection control is a prerequisite for GC controlled revision experiments and for any SA/FG/CQ experiment that needs a non-default goal subset. WF reproduction and the AX baseline do not depend on it. Other Track 0 activities are not a global gate for independent work.

This infrastructure is a prerequisite for the relevant new experiments, not a criticism that the original browser analysis should not have occurred.

### 7.2 Reuse first, then add targeted contrasts

First map the questions in this plan to existing acceptance scenarios. Add only missing contrasts. Candidate additions include:

1. Beach unchanged, unselected run-on with a fully resolved control.
2. Octopus bounded inference and an unqualified factual-overclaim control.
3. Octopus partial conclusion and a genuinely completed conclusion control.
4. Homework causal-hint authorship and a student-authored control.
5. Sarah personal-example hint authorship.
6. Sandcastle new-detail leakage and an existing-detail reminder control.
7. Cell-phone attributed motive and a checkable-evidence control.
8. Existing closing claims and a genuinely abrupt-ending control.
9. Existing clear narrative transitions and an unclear-sequence control.
10. Fully resolved and strong-draft `direct_response` controls.
11. Unchanged, unrelated, partial, deferred, and regressed revisions.
12. Final reflection after actual and no substantive changes.
13. No-source informational initial/revision consistency.
14. Source-present accuracy and exact-location controls.

Do not edit frozen root V1/V2 fixtures. Version new V3 fixtures and preserve old artifacts as historical evidence. Expand beyond targeted contrasts only when the decision remains unresolved; do not chase a predetermined sample size.

### 7.3 Semantic-review record and adjudication

Keep machine assertions separate from human judgments. For each reviewed output, record:

- Scenario, fixture, prompt/schema, model configuration, and experiment arm.
- Reviewer role and review date.
- Exact evidence span.
- Structural result, reported separately.
- `semantic_status`: `acceptable`, `critical_contract_violation`, `quality_concern`, or `uncertain`.
- Meaningfulness under Section 3.
- Candidate rationale accuracy.
- Hint authorship and whether content was already in the draft.
- Observation/inference/evidence classification.
- Source-limitation relevance and consistency.
- Selected-goal observation correctness.
- Positive, null, and negative findings.
- Disagreement and adjudication outcome.

A qualified educator owns pedagogical meaningfulness and grade-appropriateness judgments. Engineering reviewers may classify structural and explicit contract violations, but must not declare pedagogical consensus. Where feasible, disputed cases receive independent review before adjudication. A model-assisted judge may flag cases but cannot certify its own output or replace human review.

Apply Section 5.1 to single-review evidence. If two independent educators disagree on a decision that could justify architecture or release, use the adjudicator and record the rationale. If disagreement remains unresolved, retain `uncertain`; do not count the case as either a pass or a critical failure, and do not use it alone to justify architecture work.

Use the following examples to distinguish critical authorship violations from quality concerns:

- **Critical:** `Homework is harmful because ____` supplies the assigned-topic claim inside a frame even though the reason remains blank.
- **Critical:** `Was Sarah too tired or out of time?` names possible target explanations when producing that causal connection is the student's task. Question form does not remove the supplied content.
- **Acceptable authorship, possible quality concern:** `What did you notice in class when you were tired?` supplies no target answer but may be too generic without a useful linked follow-up.
- **Acceptable authorship, possible quality concern:** `What did the sandcastle look like?` introduces no new object or detail, although reviewers may still judge the procedure insufficiently specific.

Do not classify scaffolds by an estimated percentage of the answer supplied. Apply the PRD paste/paraphrase and target-content checks to the complete context. Label genuinely borderline cases `uncertain` and adjudicate them rather than forcing a binary decision.

### 7.4 Browser-visible diagnostic capture

Where authorized and available, extend JSONL-style capture with:

- Submission lifecycle events and timestamps.
- Composition, snapshot, round, and review identifiers.
- Selected goal IDs and carry-forward indicators.
- Route transitions and source notices.
- Review status before and after refresh or retry.
- Editor/submitted-draft preservation checks.
- Snapshot counts before and after retry.
- Visible error category and recovery action.

Do not collect hidden reasoning. Raw prompt/response capture remains subject to existing server-side controls and separate opt-in. Redact restorable session URLs; random session IDs are not authentication.

## 8. GC — Goal Continuity as a Three-Arm Experiment

### 8.1 Start with the disputed beach review

**Observed output:** The beach run-on was suggested initially and after revision 1 (lines 13 and 17), remained unchanged in revision 2, and was absent when the next response said no meaningful issue required action (lines 19–20).

This is not yet a confirmed bug. The reviewer must determine:

1. Does the unchanged run-on still meet the PRD meaningfulness threshold?
2. Did it materially affect reader understanding or represent a meaningful pattern?
3. Was the original candidate itself too aggressive?
4. Is `direct_response` defensible, or should meaningful optional candidates remain while Finish stays available?
5. Does dropping the issue reflect responsible reassessment or silent loss of continuity?

**Acceptable null outcome:** The sequence is judged reasonable and no GC production change occurs. If the issue remains meaningful, relative improvements elsewhere do not by themselves justify a no-issues route.

### 8.2 Three-arm non-persistent experiment

Use identical frozen drafts, selected goals, self-reports, and runtime configuration across arms:

- **Arm A — Current:** Current prompt and inputs, including the full current draft.
- **Arm B — Generic continuity prompt:** Add an instruction to reassess the whole draft and avoid manufacturing or silently dropping meaningful issues, but provide no historical issue list.
- **Arm C — Temporary history injection:** Have the evaluation harness add the immediately previous Coordinator findings to the user payload for the experiment only. Do not add persistent state, storage fields, or a new output schema.

Arm C uses a `prior_findings` payload containing only bounded fields needed for the hypothesis:

- `goal_id`.
- Category and severity.
- Concise description.
- Previous exact reference and location.
- Selected, deferred, or unselected status.

Arm C's model-visible field name, nesting, values, and serialization must exactly match the production payload proposed in Section 8.4. Only population and persistence differ: the harness constructs the field temporarily, while an adopted production path would derive it from the latest completed assessment. Define a shared payload builder or reference serializer before running Arm C, and reuse it if production state is adopted. Add a fixed-input equivalence test so a later production serializer cannot silently change the contract tested by the experiment.

Do not pass a growing transcript. Tag outputs with an experiment ID for evidence provenance; do not present experimental evidence as release-schema evidence.

### 8.3 GC decision rules

Write scenario-level expected outcomes before reviewing arm outputs. Do not use candidate count as a proxy for quality, and do not average away a critical failure.

Use these operational definitions:

- **Continuity failure:** Reviewer adjudication finds that a prior issue remains meaningful under Section 3, but the output drops it without current-text or context evidence that would justify reassessment.
- **Manufactured issue:** An arm presents an issue as meaningful when reviewers judge it resolved or below the meaningfulness threshold.
- **Nagging:** An arm repeatedly carries forward a resolved/below-threshold issue or presents optional historical findings as required work. Displaying a currently meaningful optional candidate while preserving Finish is not nagging.
- **Stale anchor:** A previous finding is retained despite current-text or corrected-context evidence that it is resolved or no longer relevant.
- **Better than Arm A:** The arm reduces adjudicated continuity failures in the targeted cases, with no new manufactured issues, forced revision, loss of stopping, or critical regressions in strong-draft and resolved controls.
- **Material improvement:** The arm corrects the specific continuity behavior the experiment was designed to test; more candidates, longer feedback, or stylistic differences alone are not material improvement.

Apply these rules:

- **A adequate:** No adjudicated continuity failure or net quality harm is found; keep current behavior.
- **B better under the definitions above:** Consider the prompt-only change.
- **C materially improves continuity without nagging, stale anchors, or loss of stopping:** Consider persistent bounded prior findings.
- **Mixed or uncertain:** Add only the contrasts needed to resolve the ambiguity; do not add state yet.
- **Any arm causes forced revision or manufactured issues:** Reject that arm regardless of candidate continuity.

Measure repair behavior and operational cost when applicable, but do not treat them as semantic quality scores. Record reviewer uncertainty and single-review limitations under Sections 5.1 and 7.3 rather than treating subjective agreement as objective proof.

### 8.4 Persistent state only after experimental support

If Arm C supports a production change, then design an optional `prior_findings` input using the exact model-visible shape already tested:

1. Add it through `langgraph_core/state.py` with an empty default for old state.
2. Populate only from the latest completed Coordinator assessment in `ui/layout.py` and `scripts/evaluate_v3.py`.
3. Reuse the Arm C payload builder or prove normalized JSON equivalence with it on fixed inputs.
4. Include current and previous drafts and require text/context-based reassessment.
5. Reuse a `goal_id` only for the same unresolved issue; do not mechanically revive old findings.
6. Keep `direct_response` available when all meaningful issues are resolved or no longer meaningful.
7. Keep Finish available when optional candidates remain.
8. Version and document the state/prompt contract together.

Do not make the mere existence of a prior issue a deterministic ban on `direct_response`; the student may have fixed it incidentally.

### 8.5 Disposition schema is a separate later decision

Do not add per-finding dispositions in the initial experiment or first persistent-state patch. Consider `resolved`, `carry_forward`, `no_longer_meaningful`, or `uncertain` only if the adopted bounded-history design still demonstrates silent omissions.

Before that escalation, define one-to-one coverage, route validation, issue mapping, repairs, cost, migration, and rollback. A possible future fallback is not part of the current implementation commitment.

### 8.6 GC tests

- GC-01: Beach disputed sequence is reviewed under Section 8.1 before expected routing is prescribed.
- GC-02: Fully resolved selected and unselected issues permit `direct_response`.
- GC-03: Intentional deferral receives neutral observation and optional carry-forward.
- GC-04: An unselected issue resolved incidentally is not revived because of history.
- GC-05: An issue no longer meaningful under corrected genre/directions is not revived mechanically.
- GC-06: A new meaningful regression remains visible even when the selected goal improves.
- GC-07: Three selected goals still receive exactly one observation each.
- GC-08: Finish remains available with or without candidates.
- GC-09: Experiment payloads are bounded and contain no transcript or hidden reasoning.
- GC-10: Strong drafts and fully resolved controls do not gain manufactured issues.

- GC-11: Arm C and the proposed production path produce equivalent normalized `prior_findings` JSON on fixed inputs.

If persistent state is adopted, execute this compatibility matrix:

| Executing code | Saved state | Required result |
|---|---|---|
| Old | Old | Baseline behavior and data remain intact |
| New | Old | Upgrade/read path works with the field defaulted |
| New | New | Current-version create/read/review path works |
| Rolled-back old | New | Extra field is handled safely without reset or data loss |

Then add:

- GC-12: Every compatibility-matrix cell passes its applicable read/restore path.
- GC-13: Mixed old/new sessions coexist in one database.
- GC-14: For an explicit old → new → rollback sequence, restore, retry, genre correction, and final reflection preserve text, goal identity, and review lineage.
- GC-15: Unknown fields are preserved where state is rewritten, and immutable snapshots remain unchanged.
- GC-16: Upgrade, rollback, and retry do not create duplicate snapshots or reviews.

### 8.7 GC adoption gate

Adopt only the simplest arm that meets the predefined scenario outcomes and Section 8.3 definitions without critical regressions. If no arm does so, record the null result and stop GC work. Persistent state additionally requires payload equivalence and all compatibility-matrix and rollback tests before deployment.

## 9. SA — Independent Scaffold-Authorship Experiments

### 9.1 Evidence and review posture

**Observed wording:**

- The homework hint lists focusing less, missing instructions, and making mistakes; the revision adds not listening and forgetting instructions (lines 9–10).
- The sandcastle hint introduces tower shape, sand texture, and water sounds; the revision adds lopsided towers and cold, squishy sand (lines 18–19).
- The Sarah hint proposes no time and tiredness before the student supplies the causal connection (line 4).

These examples justify targeted authorship review, not a predetermined finding that every question is prohibited. Apply the PRD checks: could the student paste or closely paraphrase the scaffold as the requested response, and does it name the target reason, evidence, explanation, or elaboration?

SA experiments are independent of GC and must not wait for a state decision.

### 9.2 Prompt-only intervention first

In `agents/prompts.py`, test clarifications that:

1. Anchor hints in words already present in the draft.
2. Ask students to recall, observe, imagine, or intend without listing likely target answers.
3. Avoid topic-specific menus of causes, evidence uses, objects, sensory details, or actions.
4. Permit reminders of existing content for synthesis while prohibiting new target content.
5. Keep structural starters abstract.
6. Preserve concept restatement, concrete-first steps, and two-to-four-step specificity.
7. Apply the same boundary to candidate actions, hint steps, self-checks, vocabulary, starters, and stuck steps.

Use unrelated synthetic prompt examples. The examples below are illustrative boundaries, not prescribed wording or a requirement that every student receive the same frame:

- Avoid an answer menu such as “Do you focus less, miss instructions, or make mistakes?”
- One acceptable process pattern is to ask for a moment the student noticed, what the student did, and what followed.
- Another acceptable pattern is to ask the student to identify a missing causal step and explain it in their own words.
- Avoid introducing “towers” when no towers are already present.
- Acceptable narrative prompts may ask which sense the student wants to use or where a chosen detail belongs, without selecting the new object or action for the student.

Do not optimize for matching these sentences exactly. Review the underlying authorship boundary and usefulness.

### 9.3 Validation

Do not use a keyword blacklist as semantic proof. Retain deterministic checks for exact references, step counts, forbidden fields, and prohibited score/readiness language. Add human semantic review using Section 7.3.

Review the intentional soft acceptance of on-topic starters in `tests/test_agents.py:246-270` against the PRD. Do not restore a brittle validator and call the problem solved. Document the boundary and evaluate actual outputs.

### 9.4 SA tests

- SA-01: Causal hints elicit the student's classroom experience without listing the target causal links.
- SA-02: Personal-example hints do not supply no-time or tiredness explanations.
- SA-03: Narrative hints do not introduce absent objects, textures, sounds, or actions as suggested answers.
- SA-04: Conclusion hints may remind students of existing traits for synthesis.
- SA-05: Abstract starters such as `____ because ____` remain allowed.
- SA-06: A completed on-topic frame is a critical authorship violation even if it contains blanks.
- SA-07: Hints retain exact references, two to four linked steps, and a useful self-check.
- SA-08: Hint expansion, Show less, and I'm stuck make no model calls.
- SA-09: Vocabulary remains optional consideration rather than supplied evidence or interchangeable replacements.
- SA-10: Stuck steps reduce the task without revealing the target response.
- SA-11: Multiple different process-oriented hint phrasings can pass; no exact wording is required.

### 9.5 SA decision gate

- Blocking within the reviewed targeted sample: adjudicated completed answers, assigned-topic target content, or other clear PRD authorship violations introduced by the change.
- Quality concerns such as borderline specificity or phrasing are documented and iterated rather than converted into a universal zero-defect claim.
- No adopted prompt change may make hints generic or add scaffold-reveal model calls.
- If current hints are adjudicated acceptable and alternatives offer no benefit, retain current behavior and record the null result.

## 10. FG — Independent Grounding and Source Experiments

### 10.1 Separate stronger and disputed evidence

**Cell-phone concern:** The revision attributes a texting concern to teachers, and the observation calls it a “checkable motive” without supplying a checkable basis (lines 37–38). This is a targeted wording/evidence concern.

**Octopus disputed case:** The student writes “so I think it was using camouflage to stay safe” (line 24). “I think” already marks an inference. The subsequent candidate asks the student to explain the connection (line 26); this may be a grade-appropriate reasoning request or may encourage an unsupported mechanism. Do not prescribe a defect before review.

**Source-consistency question:** The octopus initial review has no source limitation and both revisions do (lines 22, 25, and 29). Determine whether verification relevance changed or whether notice behavior is inconsistent. Do not require identical wording or a blanket source notice on every informational draft.

### 10.2 Review questions

For octopus, reviewers decide:

- Is the student's bounded inference acceptable as written?
- Does the follow-up prompt invite reasoning about an inference or pressure the student to assert an unsupported fact?
- Does the review actually claim verification, or only acknowledge a new connection?
- Is any correction meaningful for a sixth-grade informational draft without a source?

**Acceptable null outcome:** The bounded inference and follow-up are judged appropriate. No anti-inference rule is added.

For cell phone, distinguish clearer wording from evidence. A motive is not checkable merely because it is more specific.

### 10.3 Prompt-only changes if supported

If targeted review identifies a real problem, test Coordinator/Support clarifications independently of GC:

1. Distinguish observation, bounded inference, general assertion, and sourced evidence.
2. Do not convert a plausible inference into an established explanation.
3. Do not validate factual truth or source fidelity without adequate evidence.
4. Do not ask students to invent facts, evidence, motives, mechanisms, or source content.
5. Allow appropriately bounded student interpretation without demanding unnecessary correction.
6. When verification is relevant but impossible, give a brief limitation and invitation to add a source consistently across rounds.
7. Do not demand citations for personal narratives, opinions, or ordinary experience.
8. Preserve accuracy-tier priority for genuine fabricated evidence or source misrepresentation.

Support must not weaken Coordinator accuracy findings or turn them into verification praise. Preserve source limitations exactly. Keep deterministic no-source validation, but do not treat regex coverage as semantic proof. Review words such as “proves,” “checkable,” and “accurate” in context rather than banning them mechanically.

### 10.4 FG tests

- FG-01: “I think” or “I wondered whether” is recognized as bounded inference, not automatically treated as factual error.
- FG-02: A follow-up to an inference does not require the student to invent an unsupported mechanism.
- FG-03: An unqualified factual overclaim remains distinguishable from a bounded inference.
- FG-04: The attributed teacher motive is not called checkable without a checkable basis.
- FG-05: No-source informational notices are consistent in meaning when relevance is unchanged.
- FG-06: Personal narratives and opinion-only drafts receive no unnecessary citation demand.
- FG-07: No-source outputs make no unqualified source-accuracy claim.
- FG-08: Supplied-source mismatches retain accuracy priority and exact source locations.
- FG-09: Hints do not elicit invented surveys, quotations, facts, or motives.
- FG-10: Structural improvement does not erase a separate meaningful accuracy issue.

### 10.5 FG decision gate

- Blocking within the reviewed targeted sample: unqualified no-source verification claims, instructions to invent factual evidence, or suppression of a genuine source mismatch.
- Bounded age-appropriate inference is not a violation merely because it is uncertain.
- Source-notice consistency is judged by relevance and meaning, not exact text.
- If octopus is adjudicated acceptable, record the null outcome and do not use it to justify a prompt change.

## 11. CQ — Independent Candidate-Quality Experiments

### 11.1 Evidence and review posture

**Observed output:**

- Homework and cell-phone drafts end with position statements, but candidate rationales say the reader receives no final reminder (lines 3 and 31).
- Cake contains “When” and “Twenty minutes later,” yet receives a generic transition candidate (line 40).
- Octopus receives positive conclusion feedback followed by a more specific continuation of the conclusion goal (lines 25–26).

The first two are rationale/meaningfulness questions. The octopus continuation may be legitimate partial progress; do not assume it is a moving-target defect without review.

### 11.2 Prompt-only changes if supported

1. Check the whole draft before saying an element is absent.
2. If an element exists but is weak, acknowledge it and name only the remaining property.
3. Do not recommend a transition without an actual unclear relationship or sequence.
4. Do not impose conclusion formulas, transition quotas, or five-paragraph structure.
5. When a selected goal improves but remains unresolved, use text evidence, identify the remaining step, and reuse the same `goal_id` for the same issue.
6. When no meaningful issue remains, affirm without manufacturing a task.
7. Preserve exact references and overlap behavior.

Do not change `carry_forward` semantics in the first patch. Any later UI or semantic change must define its interaction with improvement and deferral and update tests/documentation together.

### 11.3 Review rubric

Reviewers record:

- **Meaningful:** Apply Section 3 rather than personal preference alone.
- **Rationale accurate:** Does it acknowledge what is already present?
- **Reference appropriate:** Is the exact passage correctly scoped?
- **Action manageable:** Is it bounded and student-authored?
- **Continuity clear:** Is remaining work distinguished from progress?
- **Voice preserved:** Does it avoid unnecessary formalization?

### 11.4 CQ tests

- CQ-01: Existing final claim restatement is recognized; any further goal names only a real remaining gap.
- CQ-02: Clear existing sequence words do not automatically trigger a transition goal.
- CQ-03: A genuinely abrupt ending can receive a conclusion goal.
- CQ-04: A strong complete draft can receive no candidates.
- CQ-05: A partially improved conclusion preserves goal identity and explains the remaining step.
- CQ-06: A genuinely completed conclusion needs no repeated goal.
- CQ-07: Specific improvement plus a remaining issue uses no failure framing.
- CQ-08: Rationale changes do not introduce replacement prose.
- CQ-09: Exact, nested, and overlapping references still highlight correctly.
- CQ-10: Accuracy/reasoning priority and optional-language suppression remain intact.

### 11.5 CQ decision gate

Blocking within the reviewed targeted sample applies to clear rationale falsehoods or manufactured issues introduced by the change. Partial-goal framing and relative usefulness remain human quality judgments. If existing continued-goal feedback is judged clear, record the null outcome rather than forcing identity or UI changes.

## 12. Verification Strategy Without Process Deadlock

### 12.1 Deterministic and mocked checks — every code/prompt stage

Run:

- State defaults and applicable compatibility checks.
- Payload construction and bounded experiment inputs.
- Exact reference and paragraph/occurrence validation.
- Selected-goal observation coverage.
- Route/schema validation and bounded repair.
- Source availability and source-location validation.
- Snapshot immutability and retry behavior.
- Goal-selection limits and no-extra-model-call controls.
- Neutral unchanged/small-change notices.
- Final-reflection grounding to deterministic diffs.

Mocked tests prove control flow and contracts, not real feedback quality. Prompt-string assertions alone are not behavioral evidence.

### 12.2 Streamlit AppTest — every UI-affecting stage

Exercise:

- Initial review through two revisions.
- Selection, deselection, hints, Show less, and I'm stuck.
- Unchanged and small-change confirmation.
- Submission failure, restoration, and retry.
- Goal continuity where applicable.
- Direct response and student-controlled Finish with candidates and without.
- Final reflection and milestones.

### 12.3 Accessibility — baseline and continuous

Start now rather than waiting for closeout:

1. Audit the current full keyboard revision/final loop and perform actual screen-reader checks.
2. Record existing failures before changing unrelated prompt code.
3. Repeat relevant checks for every UI-affecting change.
4. Run a final regression pass for integrated UI releases.

An accessibility failure blocks the affected UI release according to its severity; it does not automatically roll back independent prompt or storage improvements. The existing accessibility gate remains open until direct evidence closes it.

### 12.4 Authorized targeted real-model experiments

For each independent experiment:

1. Complete mocks and fixture validation first.
2. Obtain the Section 5.2 authorization record.
3. Run only the selected contrast scenarios and arms.
4. Review critical violations, quality concerns, and null outcomes separately.
5. Rerun only unresolved or corrected targeted cases under separate or covered authorization.
6. Record repairs, failures, tokens, and latency without treating them as quality scores.

Targeted success supports adoption of a specific change; it is not a full release gate.

### 12.5 One integrated full acceptance evaluation

Only after adopted changes pass targeted review, and with separate authorization:

- Run one integrated non-thinking acceptance evaluation for the versioned release.
- Include existing and adopted new scenarios.
- Require zero scenario errors and no persistent schema failure.
- Deduplicate execution logs by `(thread_id, node, timestamp)`.
- Report calls, repairs, tokens, per-call latency, graph duration, and service duration.
- Checkpoint/close databases before stable hashing.
- Compare against a compatible baseline.
- Report all quality degradations, even when aggregate counts improve.

Decoupling implementation does not require paying for a full run after every experiment. Batch adopted changes into one integrated evaluation unless an unresolved interaction requires separate diagnosis.

### 12.6 Real-browser verification

Test local UI changes before deployment. Repeat on a deployed commit only after explicit approval:

- Two-round loops for all three genres.
- Selected/unselected goal behavior where applicable.
- Hint display and output capture.
- Submission, refresh, failure, and retry.
- Neutral small-change flow.
- Direct response and Finish with unresolved optional candidates.
- Final original-to-final reflection.
- 1280px desktop and required responsive checks.
- Current keyboard and screen-reader status.

Service-level runs are not deployed-browser evidence. Do not describe public deployment as updated until deployment and retest occur.

### 12.7 Educator review

Use `EDUCATOR_REVIEW_PROTOCOL.md` with synthetic drafts and complete context. Begin with disputed beach and octopus cases before adopting related changes. Later review adopted outputs for:

- Grade appropriateness and cognitive load.
- Accuracy and source humility.
- Student authorship and scaffold usefulness.
- Continued-goal clarity.
- Stopping agency without hidden meaningful issues.
- Genre-sensitive quality.

Educator review remains pending until conducted. Schema compliance, synthetic revisions, and model self-review cannot substitute for it.

## 13. Execution Tracks and Integration Points

Dependencies are deliberately narrow:

- **EV selection controls → Track 2 GC controlled revision experiments.** Temporary Arm C payload construction must also satisfy Section 8.2.
- **EV selection controls → only those Track 3 experiments that require non-default goal subsets.** Initial-review hint or rationale experiments do not need revision-selection controls.
- **Educator review → adoption of GC/FG direction from disputed cases.** It is not a prerequisite for unrelated WF, EV, or accessibility implementation.
- **WF and AX are independent.** Neither waits for EV, GC, or content experiments.
- **Integration waits only for adopted changes and their applicable gates.** A null or deferred workstream does not block unrelated work.

### Track 0 — Baseline and enablement, non-billable first

- Preserve the JSONL and reviewed commit.
- Run bounded WF reproduction.
- Start the accessibility baseline.
- Inventory existing fixtures and tests.
- Add goal-selection controls if needed.
- Prepare semantic-review records and null outcomes.

**Exit:** Apply component by component: existing coverage is mapped; EV-dependent experiments are executable only after selection controls pass; WF has a classification or unreproduced status; and accessibility findings have an initial record. Track 0 is not an all-or-nothing gate for independent work.

### Track 1 — Independent WF remediation

- Implement only reproduced, evidence-indicated fixes.
- Run WF regression tests and relevant accessibility/browser checks.

**Exit:** WF decision gate passes, or the incident remains honestly unreproduced with no speculative fix. This track does not block content experiments.

### Track 2 — GC disputed-case review and non-persistent experiment

**Requires:** EV selection controls before controlled revision runs; educator review before adopting direction from the disputed beach case.

- Review beach under the PRD and Section 5.1 reviewer-confidence rules.
- Compare Arms A, B, and C when authorized, using the predefined Section 8.3 outcomes.
- Select current behavior, generic prompt, or bounded history according to evidence.

**Exit:** Null result, prompt-only candidate, or experimentally supported state proposal. No disposition schema is included. A provisional single-review result cannot by itself justify persistent state.

### Track 3 — Independent SA, FG, and CQ prompt experiments

**Requires:** EV selection controls only for fixtures that select a non-default goal subset; educator review before adopting direction from the disputed octopus case.

- Develop and mock each change separately.
- Run targeted contrasts separately or under one authorized batch while preserving arm/scenario identity.
- Record null results and quality concerns as well as violations.

**Exit:** Only changes with targeted support become release candidates. Do not ship GC first or use it as a prerequisite. Prompt experiments remain subject to applicable integrated gates before release.

### Integration — Version and verify selected changes

- Combine only adopted changes.
- Update state constructors, prompts, runner, tests, and version constants as applicable.
- Perform mixed-version rollback tests if state changed.
- Run the full mocked suite and integrated acceptance evaluation.
- Complete local browser and continuous accessibility checks.

**Exit:** Selected changes form one versioned release candidate with no unresolved critical regression.

### Deployment and closeout — Separate decisions

- Obtain explicit deployment approval and record the exact commit/configuration.
- Repeat affected and original flows on the deployed target.
- Complete or plainly report educator/accessibility gates.
- Reconcile current documentation, actual test count, evidence paths, and limitations.

**Exit:** Every deployment or quality claim is backed by its own evidence. Open gates remain open rather than being removed for convenience.

## 14. Gates and Monitoring

### 14.1 Blocking engineering gates

For adopted code changes:

- Full `pytest` suite passes.
- No integrated-evaluation scenario errors or persistent schema failures.
- Selected goals receive exactly one observation on normal revision routes.
- Issue references are exact and correctly located.
- Snapshot immutability and retry non-duplication hold.
- Editing, selection, hints, and diff generation make no model calls.
- Existing source, genre, framework, clarification, human-review, and final-grounding tests remain green.
- Adopted state changes pass mixed-version upgrade and rollback tests.

### 14.2 Blocking reviewed-contract gates

Within the defined targeted sample, adopted changes must not introduce or retain an adjudicated critical violation central to their purpose:

- Completed replacement responses or assigned-topic target content.
- Instructions to invent factual evidence.
- Unqualified no-source source-verification claims.
- Suppression of a meaningful regression or source mismatch.
- Work loss or dishonest recovery state in the tested workflow.

These are sample-specific conformance results, not claims of zero defects across all future outputs. If reviewers disagree on whether a behavior is a violation, use Section 7.3 adjudication rather than counting it automatically as either pass or failure.

### 14.3 Quality monitoring, not universal zero-defect gates

Track with denominators and exact examples:

- Candidate rationale concerns.
- Borderline hint specificity or usefulness.
- Continued-goal clarity.
- Relative issue importance and stopping language.
- Bounded inference handling.
- Repetition and style.
- Reviewer disagreement and uncertain cases.

A quality concern may block a particular prompt adoption when the experiment shows net harm, but monitoring does not imply a universal zero-tolerance guarantee.

### 14.4 Browser, accessibility, educator, and deployment gates

- Browser recovery and final reflection must work for affected UI releases.
- Accessibility is reviewed from baseline onward and remains open until direct checks close it.
- Educator approval remains unclaimed until educators complete review.
- Deployment requires separate approval and deployed retest.
- A failure in one gate scopes remediation to that component; it does not automatically roll back unrelated work.

### 14.5 Reporting gate

- Record positive, null, and negative outcomes.
- Report repairs, failures, tokens, and latency without treating them as pedagogical scores.
- Separate machine assertions, human semantic judgments, and operational measurements.
- Make no readiness, mastery, learner-outcome, accessibility, educator, or deployment claim beyond the evidence.

## 15. Evidence and Reporting Requirements

Each experiment or release bundle should identify as applicable:

- Experiment ID and arm.
- Fixture version and scenario IDs.
- Prompt/schema versions.
- Model, thinking setting, reasoning effort where applicable, temperature, and timeout.
- Local or deployed target and exact commit.
- Authorization and resource-cap record for billable calls.
- Automated result and actual test count.
- Scenario completion and errors.
- Calls, repairs, diagnostics, tokens, and latency.
- Semantic outcomes, reviewer roles, denominators, and exact evidence spans.
- Null results and no-change decisions.
- Browser workflow and recovery behavior.
- Accessibility and educator status.
- Checkpointed/closed database integrity information.
- Known limitations and open gates.

Keep raw evidence git-ignored according to repository policy. Use synthetic writing only. Redact restorable session URLs and personal information in shared artifacts. Never commit API keys, secrets, databases, evidence JSON/JSONL, or screenshots.

## 16. Standard Commands

Local, non-billable verification:

```bash
source .venv/bin/activate
pytest
streamlit run app.py
```

Authorized targeted real-model example after fixtures have assigned scenario numbers:

```bash
python scripts/evaluate_v3.py \
  --modes nonthinking \
  --scenario-set acceptance \
  --scenario-number <assigned_number>
```

Authorized integrated acceptance run:

```bash
python scripts/evaluate_v3.py \
  --modes nonthinking \
  --scenario-set acceptance
```

External calls are billable and require the Section 5.2 authorization record. Use non-thinking student runtime configuration. Do not add thinking runs without a separate authorized comparison question.

## 17. Risks, Rollback, and No-Change Paths

- **Historical context causes endless revision:** Prefer current/generic arms if adequate; bound any history, preserve Finish, and test strong/resolved controls.
- **History anchors stale issues:** Require current-text/context reassessment and incidental-resolution controls.
- **Hint restrictions become generic:** Require existing-text anchors and process specificity, not one prescribed phrasing.
- **Source caution becomes citation demand everywhere:** Preserve bounded inference, narrative, opinion, and personal-experience controls.
- **Candidate rules become formulas:** Evaluate actual reader effect rather than transition or conclusion counts.
- **New state increases repairs or cost:** Do not persist it unless Arm C shows material benefit; measure before adoption.
- **Semantic review overstates reliability:** Use explicit roles, evidence spans, disagreement/adjudication records, and null outcomes.
- **Accessibility appears late:** Prevent through baseline and per-stage checks; scope failures to affected UI changes.
- **Recovery changes damage history:** Preserve immutable snapshots and never reset a database as a fix.

If state is adopted and later rolled back:

1. Retain all databases and immutable snapshots.
2. Revert only the scoped code/prompt change.
3. Verify old code can read new JSON state with extra fields; do not assume compatibility.
4. Test mixed old/new sessions, restore, retry, genre correction, and final reflection.
5. Preserve unknown fields where state is rewritten.
6. Use a backward-compatible additive migration only if required; no destructive migration or data deletion.
7. Record any incompatible saved state as a blocker before deployment, not as a post-deployment cleanup task.

Prompt-only changes can be reverted to the prior version while retaining compatible state. Evaluation-only history injection must never become production state by accident.

## 18. Completion and Stop Criteria

This plan does not require every workstream to produce code. The investigation may legitimately conclude that current behavior is adequate.

The effort is complete when:

1. WF is reproduced and fixed with regression evidence, or bounded investigation records it as unreproduced with no false fix claim.
2. Accessibility baseline evidence exists and each adopted UI change receives relevant follow-up checks.
3. Controlled experiment infrastructure can select and verify intended goals before new targeted revision runs.
4. Beach has an educator-reviewed disposition: acceptable null, prompt-only need, or experimentally supported history need.
5. GC adopts the simplest supported option, or no option is adopted; persistent state, if any, passes mixed-version rollback tests.
6. SA, FG, and CQ changes are independently supported by targeted evidence or rejected with null results.
7. Octopus bounded inference is reviewed without assuming it is an error; cell-phone evidence wording receives a distinct result.
8. Only adopted changes enter one integrated, authorized acceptance evaluation.
9. Browser recovery, stopping with optional candidates, and final reflection are verified where applicable.
10. Deployment, educator, accessibility, and learner-outcome claims remain separately bounded by actual evidence.
11. Documentation reports what changed, what did not, actual test counts, costs/latency where measured, open gates, and remaining limitations.

A no-change conclusion supported by the relevant review or experiment is a completed result, not a failed investigation.
