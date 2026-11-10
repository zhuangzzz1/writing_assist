# V3 Prompt Review Validation and Action Plan

**Date:** 2026-11-10  
**Status:** Assessment and proposed plan; no implementation performed in this review pass  
**Subject:** `V3_PROMPT_REVIEW_AND_IMPROVEMENTS.md`  
**Scope:** Local synthetic V3 prototype only

## 1. Purpose and Evidence Base

This document validates the findings and recommendations in `V3_PROMPT_REVIEW_AND_IMPROVEMENTS.md` against the current implementation and preserved synthetic evidence. It resolves additional review comments concerning §4.1, §4.7, and §10, and incorporates a subsequent independent critique of evidence handling, schema generalization, highlight behavior, evaluation cost, and density-fixture design.

Sources inspected include:

- `agents/prompts.py`
- `agents/assessment_coordinator.py`
- `agents/support_agent.py`
- `agents/utils.py`
- `langgraph_core/revision.py`
- `scripts/evaluate_v3.py`
- `test_cases/v3/acceptance.json`
- `V3_INVESTIGATION_EVIDENCE.md`
- `V3_OUTCOMES_REPORT.md` Section 16
- `data/evidence/v3_investigation_manifest_20261110.json`
- The cited acceptance, paired-core, targeted-retest, and browser evidence artifacts
- `CLAUDE.md`, `AGENTS.md`, and the educator-review protocol

No real-model calls, new browser runs, deployments, or learner-outcome evaluations were performed.

## 2. Executive Assessment

The source report is a useful investigation, but it should not yet serve as an authoritative implementation specification.

Its strongest conclusion is correct: RACES coverage is assigned partly to an agent whose output contract prevents it from supplying missing issues. That is an architectural ownership conflict, not a prompt-tuning problem.

Other recommendations require qualification:

- A required `regression` boolean would prove field presence, not regression-detection quality.
- Candidate-per-word ratios do not establish inverted proportionality or inappropriate feedback density.
- Several evidence counts and historical statements are inaccurate or outdated.
- Some proposed validators would reject legitimate output rather than reliably improving it.
- Prompt and schema changes require new versioned evidence; existing artifacts remain historical.

The recommended direction is to move teacher-framework coverage to the Assessment Coordinator, preserve Support as a bounded renderer, make low-risk contract clarifications, and strengthen regression evidence without using schema repairs as a proxy for pedagogical quality.

## 3. Decisions on the Additional Review Comments

### 3.1 Section 4.1: Confirmed Design Conflict

The conflict is present in the current contracts:

- `agents/prompts.py:16` asks the Coordinator to account for Restate, Answer, Cite, Explain, and Sum up when RACES is explicit.
- `agents/prompts.py:89` asks Support to make the candidate set collectively cover those components.
- `agents/support_agent.py:186-190` requires exactly one Support candidate per Coordinator issue.

Support can render components already represented in Coordinator findings, but it cannot reliably supply an omitted component without adding or expanding an issue beyond its assigned handoff.

The `162342Z` thinking-mode artifact demonstrates the structural failure:

- The Coordinator raised Cite/Explain and Sum up.
- The Coordinator did not raise Restate/Answer.
- Support's resulting candidates did not supply explicit Restate/Answer guidance.

A different run in which Support compensated does not remove the underlying design defect.

**Decision:** Move framework assessment and coverage accountability to the Coordinator. Support should render the verified handoff, not own framework completeness.

### 3.2 Section 4.7: Do Not Require `regression` Solely to Make Failures Louder

`IssueOutput.regression` currently defaults to `False` in `agents/assessment_coordinator.py:46`.

Requiring the field would establish only that the model serialized a boolean. It would not establish that the model examined the whole revision, recognized a semantic regression, or reported it accurately. A `regression_decided: true` companion would also be model self-attestation rather than independent verification.

The louder failure described in the source report is therefore primarily a louder **schema-omission** failure, not necessarily a louder hidden-regression failure. Additional repair calls add cost and output variability without guaranteeing better detection.

**Decision:**

- Retain `regression=False` as the serialization default.
- Do not add `regression_decided` as a substitute for quality evidence.
- Optionally record omitted-field frequency as diagnostic metadata without triggering repair.
- Invest in genuine regression scenarios, final-comparison coverage, exact change grounding, and human output review.
- Keep the trade-off visible as a judgment call rather than claiming that either schema choice proves regression coverage.

### 3.3 Section 10: Documentation Drift Is Already Resolved

The statement that `CLAUDE.md` requires thinking mode and cites 128 checks is outdated.

Current documentation records:

- **172 checks** at `CLAUDE.md:64`.
- Explicit `DEEPSEEK_THINKING=false` student runtime at `CLAUDE.md:77`.
- Thinking as a controlled comparator rather than an automatic fallback.

**Decision:** Close §10 as resolved. Do not carry its 128/151-check statements into the new execution baseline.

## 4. Section-by-Section Validation

| Source section | Assessment | Recommended disposition |
| --- | --- | --- |
| §4.1 RACES ownership | Confirmed architectural conflict and supported by the weaker RACES artifact | Adopt; elevate to a structural priority |
| §4.2 Mechanics keyword guard | The fragile trigger and description-keyword matching are real; a declared boolean still does not prove the judgment | Adopt with qualifications and educator review |
| §4.3 Student concerns | The payload transmits concerns, but neither prompt defines a clear prioritization rule | Adopt; preserve Coordinator ordering deterministically |
| §4.4 Vocabulary shape | `list[str]` conflicts with observed structured meaning-note outputs | Adopt the plain-string prompt clarification |
| §4.5 Explicit genre | The model currently controls a field that is already deterministic | Adopt normalization without a mismatch-only repair |
| §4.6 No-source dependency | The converse rule for `source_dependent` is not explicit enough | Adopt the prompt clarification |
| §4.7 Required regression field | Field presence is not evidence of semantic regression review | Reject as proposed; strengthen evidence instead |
| §4.8 Conditional payload context | Potential token savings exist, but source removal may affect hint grounding; empty-history savings are negligible | Measure before adopting |
| §5 Proportionality | Feedback density deserves review, but the claimed inversion and 25× metric are not validated | Defer thresholds; use educator review |
| §6.1 Final coverage | Additional high-risk final cases are valuable, but existing coverage is four scenarios rather than two | Correct the count and expand coverage |
| §6.2 Zero candidates in #24 | Appropriately identified as a pedagogical review question, not an automatic defect | Retain for educator review |
| §6.3 Nested references | Nesting is observed, but containment does not prove duplicate or manufactured goals | Address UI ambiguity; do not impose a blanket semantic rejection |
| §7 Final pass-through | Exact regeneration spends tokens unnecessarily | Adopt only with bounded-language validation at the new boundary |
| §8 Human gates | Correctly separates educator and accessibility judgments from deterministic checks | Retain |
| §10 Documentation | Already corrected and now further updated | Close |

## 5. Evidence Corrections Required in the Source Report

### 5.1 Repair-Category Count

Section 3 says there are six repair categories, but its table contains five:

1. Omitted optional `regression` field.
2. Vocabulary-option shape/type.
3. Source-dependent finding without supplied source.
4. Explicit genre-correction mismatch.
5. Non-obscuring-mechanics guard.

The manifest itself labels these as deterministic validation-text categories, not established root-cause claims. In particular, the #24 mechanics repair involved the validator rejecting a model judgment; it should not automatically be classified as a validator defect.

### 5.2 Full-Run Repair Attribution

The corrected full acceptance artifact `v3_acceptance_evaluation_20261110T160932Z.json` contains two repairs:

- #4: omitted `regression` field.
- #6: explicit-genre mismatch.

They were not both regression-field omissions. Therefore, the estimate that the proposed prompt fixes would save approximately five repair calls **per acceptance run** is unsupported: the report combines repairs from different artifacts and model modes.

### 5.3 Final-Reflection Coverage

The full run contains final states for four scenarios:

- #1
- #8
- #11
- #20

The claim that only #1 and #11 reached final reflection is incorrect. Adding #7, #9, and #15 remains useful because they cover multi-goal partial progress, organizational regression, and deferred goals.

### 5.4 Hint-Step Distribution

The manifest's actual hint-step distribution is:

| Hint steps | Scenario count |
| --- | ---: |
| `[3, 3]` | 12 |
| `[3, 3, 3]` | 7 |
| `[3]` | 7 |
| `[3, 4, 4]` | 1 |
| `[4]` | 1 |
| `[]` | 2 |

Nineteen scenarios have the two exact list shapes named in the report, not 27. The narrower observation that three-step hints dominate is supported.

### 5.5 Proportionality and Scenario #23

Candidate count per draft word is not a validated feedback-quality or workload measure. The scenarios also have intentionally different acceptance goals:

- #7 and #15 intentionally exercise three-goal behavior.
- #23 asks for a small prioritized issue set rather than an error catalogue.

The claimed 25× difference is therefore not evidence of a defect. Short- and long-draft density should be reviewed by educators using complete context.

The questioned #23 sentence does not appear literally in the assignment prompt or teacher directions. It is relevant to the draft's subject of evidence-based informational writing. Literal task-language leakage is not confirmed. Whether the passage feels natural as student writing remains a fixture-design judgment.

### 5.6 Live WAL-Database Hashing

The manifest's own SHA-256 matches the value recorded in `V3_INVESTIGATION_EVIDENCE.md`. Of the 40 listed artifacts, 39 matched their recorded hashes; `data/v3_improvement_browser.db` did not.

The database observations are consistent with a normal SQLite WAL checkpoint and clean close:

- Recorded database size: 172,032 bytes, or 42 pages of 4,096 bytes.
- Current database size: 376,832 bytes, or 92 pages.
- Growth: exactly 50 pages.
- The recorded 568,592-byte WAL contains exactly 138 frames.
- The WAL and SHM sidecars are now absent.
- A read-only `PRAGMA integrity_check` returns `ok`.

These observations do not prove the historical event from byte sizes alone, but they provide no evidence of corruption or tampering. No corruption audit is indicated by this hash mismatch alone.

The correct conclusion is that **a live WAL-mode database is not a stable byte-level integrity artifact**. Future evidence capture should checkpoint and close the database before hashing, create an immutable SQLite backup, or freeze and hash a consistent database/WAL set. Hashing actively changing database and sidecar files is not a valid set-integrity procedure. The cited acceptance and paired JSON artifacts matched their hashes and are unaffected by this SQLite capture issue.

### 5.7 Historical Aggregate Metrics and Reproduction Rule

The reaggregation rule implemented in `scripts/evaluate_v3.py:120-137` is:

1. Collect execution logs from initial, genre-correction, final, clarification, and revision states.
2. Deduplicate logs by `(thread_id, node, timestamp)` so a cumulative state snapshot cannot repeat an earlier log.
3. Count each retained log's `model_calls` once.
4. For cumulative graph timing, retain the latest review per `round_id`.
5. Keep service-operation durations separate because they represent distinct invocations.

Scenario #30 accounts for the complete model-call, token, and model-latency correction. Its resumed states contain cumulative execution histories: the first Coordinator call was included twice extra, and the second was included once extra.

- Duplicate calls: `2 + 1 = 3`.
- Duplicate tokens: `2 × 2,202 + 2,235 = 6,639`.
- Duplicate model latency: `2 × 1,507 + 1,715 = 4,729 ms`.

The reproducible arithmetic is therefore:

- Calls: `97 − 3 = 94`.
- Tokens: `238,016 − 6,639 = 231,377`.
- Model latency: `301,410 − 4,729 = 296,681 ms`.

| Metric | Original derived value | Deduplicated historical value |
| --- | ---: | ---: |
| Model calls | 97 | 94 |
| Total tokens | 238,016 | 231,377 |
| Model latency | 301.410s | 296.681s |

These are corrected derived measurements from existing records, not new model runs. Future summaries should state the aggregation rule and distinguish original artifact values from later reaggregation.

## 6. Recommended Target Design

### 6.1 Coordinator-Owned Framework Coverage

Add a route-scoped, framework-neutral Coordinator `framework_coverage` list for explicitly teacher-required components. Do not key the schema to the five RACES component names: PRD IN-08 also covers CER, RACE, MEAL, and other teacher-defined structures.

Illustrative shape:

```json
{
  "framework_coverage": [
    {
      "framework": "RACES",
      "component": "restate",
      "status": "present",
      "reference": "exact draft excerpt"
    },
    {
      "framework": "RACES",
      "component": "cite",
      "status": "issue",
      "goal_id": "goal_2"
    },
    {
      "framework": "RACES",
      "component": "explain",
      "status": "issue",
      "goal_id": "goal_2"
    }
  ]
}
```

Required invariants:

- Coverage is required only when the teacher explicitly commissions the framework and the route is responsible for writing assessment.
- Framework and component names are nonempty and bounded.
- Every commissioned `(framework, component)` pair appears exactly once.
- `present` entries contain an exact, correctly located current-draft reference.
- `issue` entries reference an existing Coordinator `goal_id`.
- Multiple components may map to one meaningful issue.
- Missing components do not force a fixed number of goals.
- A fully present framework may still produce `direct_response`.
- Clarification and teacher-review routes do not manufacture premature framework coverage.
- Support receives the coverage handoff for rendering but cannot add new issues.
- Deterministic validation establishes structure and references; it does not claim to prove semantic quality by itself.

The list prevents component-name migrations when CER, MEAL, or another framework is introduced. It does not determine the required components of an unfamiliar framework; those requirements must come from explicit teacher context or a structured input shared by the UI and fixtures. Framework detection must avoid treating negated text such as “do not use RACES” as a requirement rather than claiming deterministic natural-language understanding.

### 6.2 Explicit Genre

When `genre_selection` is explicit:

- Treat it as authoritative before model assessment.
- Assign `working_genre` deterministically after parsing and before validation.
- Do not spend a schema repair solely because the model returned a conflicting genre.
- Preserve model-generated observable genre basis where valid.
- Retain inference and clarification behavior for `auto`.

### 6.3 Student-Concern Priority

When a concern names a specific, draft-supported area:

- Place the corresponding Coordinator issue first.
- Do not invent an issue to satisfy an unsupported concern.
- Render Support candidates deterministically in Coordinator issue order rather than repairing merely for ordering differences.

### 6.4 Mechanics Guard

Replace description-keyword dependence with a structured `obscures_meaning` assessment for language issues.

Limitations:

- The field improves the output contract, not the truth of the model's judgment.
- Teacher-direction activation must be conservative and tested for aliases and negation.
- Educators must still evaluate whether the claimed comprehension effect is real in #24 and related scenarios.

### 6.5 Regression Evidence

Do not rely on required serialization fields as a regression-detection mechanism.

Use:

- Whole-draft Coordinator review.
- Exact issue and observation references.
- Actual deterministic original/final differences.
- Regression preservation through Support.
- Real-model scenarios with known regressions and partial progress.
- Human review of whether reported regressions are accurate and complete.

### 6.6 Overlapping-Reference Highlight Behavior

The current editor drops a later range when `range.start < cursor` (`ui/editor.py:81-89`). Identical or nested selected references can therefore produce one visible highlight while two goals claim the same passage. The behavior must be defined rather than left as an ambiguous side effect.

Use presentation grouping:

1. Locate every selected goal's exact current-draft range.
2. Group ranges that overlap directly or transitively.
3. Render one highlight for each group, using the union of its ranges, and associate all grouped goal IDs with it.
4. In the feedback panel, state that the goals reference overlapping passages and preserve each goal's exact quote.
5. When one goal is deselected, retain the group highlight only while another grouped goal remains selected.
6. Scroll to the selected goal's associated passage without changing the draft.
7. Continue removing stale highlights when references can no longer be located exactly.

Do not offset a second highlight merely to make it visible; that would misrepresent the referenced text. Grouping solves presentation ambiguity only. Whether two goals are semantically duplicative remains a separate content-review question.

### 6.7 Controlled Density-Fixture Pair

The existing acceptance set cannot isolate draft-length effects because grade, genre, assignment, writing quality, and acceptance constraints vary across scenarios. Add a better-controlled fixture pair before educator density review:

- Same grade, genre, assignment, teacher directions, and source availability.
- One draft of approximately 60 words and one of approximately 400 words.
- Comparable writing quality and the same intentional issue categories.
- No acceptance-focus requirement prescribing candidate count.
- Repeated runs under the selected non-thinking configuration.
- Blinded educator assessment of candidate count, total feedback length, relevance, prioritization, and manageability.

This pair is a better-controlled comparison, not definitive proof that length alone caused a difference. Natural drafts can still differ in content and quality, so findings must remain limited to the fixtures and observed outputs.

## 7. Prioritized Action Plan

### Phase 0 — Correct the Evidence Baseline

Actions:

1. Correct the source report's category count, full-run repair attribution, final coverage, hint distribution, and §10 status.
2. Mark §4.7 as rejected in favor of evidence-based regression testing.
3. Replace live-database byte hashing with a checkpointed, closed, immutable-backup or consistently frozen-set capture procedure; do not initiate a corruption audit from the expected checkpoint delta alone.
4. Publish the reaggregation rule and arithmetic, and label reaggregated historical metrics separately from newly generated model evidence.

Exit criterion:

- The implementation baseline contains no known incorrect counts, stale configuration statements, unsupported repair-savings estimates, or unstable evidence-capture procedure.

### Phase 1 — Move Teacher-Framework Coverage to the Coordinator

Actions:

1. Implement route-scoped, framework-neutral `framework_coverage` in the Coordinator schema and state handoff.
2. Add deterministic `(framework, component)`, reference, and goal-ID validation.
3. Pass the structure to Support for rendering.
4. Remove Support's obligation to supply missing framework assessment.
5. Preserve no-manufactured-issues and student choice of one to three goals.
6. Define explicit behavior for direct, clarification, and teacher-review routes.
7. Coordinate the prompt/schema version change with Phases 2–3 as one integrated release rather than commissioning a full real-model run after each phase.

Tests:

- All components present.
- Each component missing in turn.
- Multiple components mapped to one issue.
- Invalid or mislocated references.
- Unknown or duplicate goal mappings.
- Direct response with complete coverage.
- Clarification and teacher-review routes.
- RACES, CER, MEAL, and a teacher-defined component list.
- Explicit non-framework and negated framework directions.

Exit criterion:

- #4 coverage is determined and validated in the Coordinator handoff, with Support unable to create or omit an unassigned revision issue silently, and the same schema accommodates other frameworks without component-name migration.

### Phase 2 — Apply Low-Risk Contract Improvements

Actions:

1. Require each vocabulary entry to be one plain string; document `word — meaning` for meaning notes.
2. State that every issue uses `source_dependent=false` when no source is supplied.
3. Add draft-supported student-concern prioritization.
4. Preserve candidate ordering deterministically.
5. Normalize explicit `working_genre` without mismatch-only repair.

Tests:

- Structured vocabulary objects fail without ambiguity in the revised prompt.
- No-source dependency is rejected and repaired only for substantive invalidity.
- Supported and unsupported student concerns.
- Candidate order.
- Explicit-genre mismatch without an additional model call.
- Unchanged auto-genre inference and clarification behavior.

Exit criterion:

- The full mocked suite passes and the targeted repair paths are covered without weakening existing source or genre boundaries.

### Phase 3 — Replace the Mechanics Keyword Guard Carefully

Actions:

1. Add structured `obscures_meaning` output for language issues.
2. Remove dependence on description keywords such as `obscur`.
3. Use conservative teacher-policy activation with alias and negation tests, or add a structured policy input.
4. Retain educator review of the underlying judgment.

Exit criterion:

- Genuine comprehension-blocking issues are accepted, non-obscuring mechanics are rejected, and neither decision depends on a wording whitelist.

### Phase 4 — Integrated Evidence and Acceptance Evaluation

Actions:

1. Keep the optional `regression=False` serialization contract.
2. Add final stages to #7, #9, and #15 while preserving #1, #8, #11, and #20.
3. Cover genuine regressions, unchanged drafts, partial improvement, deferred goals, and references overlapping actual changes.
4. Add the controlled approximately 60-word/400-word density pair defined in §6.7.
5. Record optional-field omissions diagnostically without triggering a model repair.
6. After Phases 1–4 are integrated and versioned, run **one** authorized non-thinking acceptance evaluation containing the existing and new fixtures.
7. Use targeted real-model reruns only for observed failures or unresolved diagnostics, not as a default for every implementation phase.
8. Report repair counts separately from quality and educator judgments.

Exit criterion:

- Regression and final-comparison claims are supported by targeted outputs and actual text changes, the density reviewers have controlled inputs, and the integrated release has one clearly versioned acceptance artifact rather than separate full runs for Phases 1–3.

### Phase 5 — Optimizations and Human Gates

Actions:

1. Pass through exact final fields only after moving their bounded-language validation to the Coordinator boundary.
2. A/B measure conditional source-payload removal before adopting it.
3. Implement the overlap-group behavior in §6.6 and test identical, nested, and transitively overlapping ranges, deselection, exact textual labels, stale-reference removal, and scrolling.
4. Conduct blinded educator review using the controlled density pair, and assess tone, readability, and scaffold authorship before adding length-based guidance.
5. Complete the full keyboard-only revision/final loop and actual screen-reader checks.

Exit criterion:

- Overlap behavior is deterministic and understandable, optimizations have measured cost and quality effects, and open human gates are recorded honestly rather than inferred from automated tests.

## 8. Items Not to Adopt as Written

- Do not require `regression` or add `regression_decided` merely to increase visible repairs.
- Do not add fixed short/long-draft candidate quotas or use candidate-per-word ratios as quality targets.
- Do not reject every nested reference as proof of a manufactured issue.
- Do not offset overlapping highlights in a way that misrepresents the referenced text.
- Do not treat a live WAL database as a stable byte-level integrity artifact or interpret a normal checkpoint delta as corruption evidence.
- Do not remove source context solely for token savings without checking hint quality and grounding.
- Do not commission separate full acceptance runs for each prompt/schema substage.
- Do not describe schema compliance as proof of pedagogical quality.
- Do not use old evidence artifacts as current-output evidence after prompt or schema changes.

## 9. Verification and Evidence Requirements

For every implementation stage:

1. Add or update mocked regression tests in the existing suite.
2. Run the full test suite and dependency/compilation checks.
3. Update prompt, schema, fixture, and test-count documentation when applicable.
4. Retest affected browser flows when UI behavior changes.

For the integrated prompt/schema release:

1. Keep real-model evaluation explicit, authorized, synthetic, and separately versioned.
2. Batch Phases 1–4 into one full acceptance run; do not pay for a full run after each substage.
3. Record positive, null, and negative findings, including repairs, failures, tokens, and latency.
4. Publish the deduplication and timing rules with derived metrics.
5. Capture immutable SQLite evidence using a checkpoint/close or consistent-backup procedure.
6. Preserve the educator, accessibility, privacy, consent, and deployment gates.

For scale, the deduplicated historical acceptance run contained **94 model calls**, **231,377 total tokens**, and **184,378 prompt tokens**. Batching avoids up to two full runs of roughly that historical order, but future cost must be measured rather than assumed identical.

## 10. Conclusion

The recommended priority is not to tune Support until it compensates for missing framework findings. Coverage responsibility belongs with the Coordinator, whose issue set determines what Support may render, and its schema must accommodate teacher-defined frameworks rather than RACES alone.

At the same time, stricter serialization should not be mistaken for better assessment. Keep the optional regression field, improve actual regression evidence, correct the historical report, use stable evidence-capture and reproducible aggregation procedures, and evaluate density through controlled fixtures and qualified educator review rather than word-count heuristics.
