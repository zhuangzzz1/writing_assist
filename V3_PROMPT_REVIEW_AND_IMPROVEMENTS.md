# V3 Prompt and Validator Review — Findings and Improvement Opportunities

**Version:** 1.0
**Date:** 2026-11-10
**Basis:** `V3_INVESTIGATION_EVIDENCE.md`, `V3_OUTCOMES_REPORT.md` Section 16, `agents/prompts.py`, `agents/assessment_coordinator.py`, `agents/support_agent.py`, and the acceptance/paired artifacts in `data/evidence/`
**Relationship to prior work:** This document is a follow-on to [`V3_IMPROVEMENT_OPPORTUNITIES.md`](V3_IMPROVEMENT_OPPORTUNITIES.md). That report set the action sequence (scenario completion → model decision → educator review). **Most of its recommendations were implemented and are now closed.** This document records what that implementation produced, retracts the parts of the earlier analysis the new evidence does not support, and identifies the remaining opportunities — which are concentrated in the prompt/validator boundary rather than in the model.
**Scope:** Local synthetic prototype only. No pedagogical, learner-outcome, or deployment claim.

---

## 1. Summary

The improvement cycle moved V3 from a representative 6-scenario pair to full 30-scenario acceptance coverage, added repair diagnostics, and reached a documented non-thinking runtime decision at prompt `v3.3.0` / schema `v3.2.1`. That is substantial progress against [`V3_IMPROVEMENT_OPPORTUNITIES.md`](V3_IMPROVEMENT_OPPORTUNITIES.md) §4.

The new evidence supports four conclusions:

1. **The earlier model-mode quality claims do not survive repetition.** Candidate counts varied by run, the claim-ownership diagnostic appeared in both modes and neither consistently, and repairs occurred in both modes. Non-thinking's advantage is now properly framed as cost and latency, which is defensible.
2. **Five measured repair categories have different causes.** Vocabulary shape and missing-source dependency support clearer contracts; explicit genre can be deterministic; the mechanics guard caught a model judgment; regression-field omission is a serialization trade-off, not evidence of hidden regression.
3. **Prompt responsibility is split in a way that makes one requirement structurally unachievable.** RACES coverage is owned by the Support Agent, which is forbidden from adding issues. The observed #4 gap is a consequence of that design, not a reasoning failure.
4. **Feedback density is inconclusive from the current fixtures.** Candidate counts vary across scenarios with different acceptance goals. A controlled short/long fixture pair and educator review are needed instead of candidate-per-word conclusions.

Section 2 records the retractions. Sections 3–7 contain the findings. Section 8 lists what remains genuinely blocked on educator review.

---

## 2. Retractions from the Earlier Report

These should be treated as superseded by [`V3_IMPROVEMENT_OPPORTUNITIES.md`](V3_IMPROVEMENT_OPPORTUNITIES.md) §1.1–1.3.

| Earlier claim | Status after repetition | Correct statement |
| --- | --- | --- |
| "Non-thinking was stronger on whole-draft coverage (3 vs 1)" | **Retracted.** Both modes returned two candidates on the garden scenario in the two new pairs. | Candidate count is run-variable, not a mode property. |
| "Thinking caught the author-vs-student distinction" as a mode strength | **Retracted.** Thinking missed it in pair 1; non-thinking caught it in pair 2. | This diagnostic is not reliably mode-specific. |
| "Non-thinking had zero repairs" as a reliability advantage | **Retracted.** Non-thinking recorded 0, 2, and 1 repairs across the three runs. | Repair rate is unstable in both modes; repair count is not a quality metric. |
| "Non-thinking 3.83× faster" as a headline | **Qualified.** Still true in all three pairs, but the ratio narrowed (3.83× → 3.43× → 3.14×). | The cost/latency direction is stable; the magnitude is not. |

The runtime decision to use explicit non-thinking is still supported by the accumulated evidence. It rests on token and latency cost in every pair, which is the right basis.

---

## 3. Repair Categories: Five Categories With Different Causes

From `repair_patterns` in `data/evidence/v3_investigation_manifest_20261110.json`; these deterministic labels are not root-cause proof:

| Category | Count | Interpretation | Response |
| --- | ---: | --- | --- |
| omitted optional regression field | 2 | Serialization choice, not regression-detection evidence | Judgment call — see §4.7 |
| vocabulary option shape/type | 2 | Prompt permits meaning notes; schema requires `list[str]` | Prompt text (§4.4) |
| source-dependent finding without source | 2 | Prompt does not explicitly require the false converse | Prompt text (§4.6) |
| explicit genre correction mismatch | 1 | Enforceable in code, left to the model | Deterministic assignment (§4.5) |
| non-obscuring mechanics guard | 1 | Validator rejected a model judgment; keyword mechanism is fragile | Structured field plus review (§4.2) |

The two full-run repairs in `v3_acceptance_evaluation_20261110T160932Z.json` were one omitted regression field in #4 and one explicit-genre mismatch in #6, not two regression omissions. That run used schema `v3.2.0`; the `v3.2.1` default was covered by automated and targeted real-model checks rather than a full acceptance run. These historical observations do not establish repair frequency for later versions.

---

## 4. Prompt Findings, Ranked

### 4.1 RACES coverage is assigned to the agent that cannot deliver it

**Evidence:** `agents/prompts.py:16` requires the Coordinator to "account for Restate, Answer, Cite, Explain, and Sum up." `agents/prompts.py:89` requires the Support Agent to "make the candidate set collectively name RACES and check Restate, Answer, Cite, Explain, and Sum up… One candidate may cover several components."

**Conflict:** `agents/support_agent.py:190` requires Support's candidate set to equal the Coordinator's issue set exactly:

```python
raise ValueError("Support must return exactly one candidate per Coordinator issue.")
```

Support can only *render* components the Coordinator already raised. If the Coordinator returns issues covering Cite and Explain, Support cannot add a Restate goal, and doing so would violate the no-manufactured-issues rule in `agents/prompts.py:17`. The observed "thinking omitted explicit Restate/Answer guidance in one pair" is Support being asked to perform an action the validator forbids.

**Recommendation:** Move framework coverage to the Coordinator, which owns issue creation. Add a `framework_coverage` field to the Coordinator schema, mapping each teacher-required component to either an issue ID or a `present` marker with a reference:

```json
"framework_coverage": {
  "restate": {"status": "present", "reference": "exact draft excerpt"},
  "answer": {"status": "issue", "goal_id": "goal_1"},
  "cite": {"status": "issue", "goal_id": "goal_2"},
  "explain": {"status": "issue", "goal_id": "goal_2"},
  "sum_up": {"status": "present", "reference": "exact draft excerpt"}
}
```

Then validate that every commissioned component appears. Support's contract becomes purely rendering, which is what its responsibility boundary already says. This converts an unpredictable Support behavior into a checked Coordinator output and can be regression-tested.

### 4.2 The non-obscuring guard is a keyword whitelist

**Evidence:** `agents/assessment_coordinator.py:293-315`:

```python
optional_language = "language corrections are optional" in state["teacher_directions"].lower()
...
explicitly_nonobscuring = any(phrase in description for phrase in (
    "non-obscuring", "not obscure", "does not obscure", "do not obscure", "without obscuring"))
claims_obscured_meaning = any(phrase in description for phrase in (
    "obscur", "cannot understand", "unintelligible"))
if issue.category == "language_conventions" and (
    explicitly_nonobscuring or not claims_obscured_meaning):
    raise ValueError(...)
```

Three problems:

1. **False positives on correct judgment.** "Readers may lose track of who 'it' refers to" is a genuine comprehension-blocking finding. It contains none of the accepted substrings, so it fails validation and triggers a repair for correct behavior.
2. **The compliant path is a keyword, not a judgment.** The cheapest way to pass is to write "obscures" whether or not the error does. The validator's success signal is one word.
3. **The trigger is a literal substring on teacher directions.** `"language corrections are optional"` will not match "grammar fixes are optional," "don't focus on mechanics," or "mechanics are not graded." In those cases the guard is silently inactive — a false-negative path on precisely the scenario it was built for.

**Recommendation:** Replace behavior inference with a declared field. Have the Coordinator emit `obscures_meaning: bool` on each issue and validate on it: a `language_conventions` issue may proceed only when `obscures_meaning` is true. Separately, parse the teacher-direction flag deterministically at input time (or as an explicit fixture field) rather than substring-matching prose. Note that the current guard is also the one repair category that is *correct in intent* — the goal of preventing mechanics-as-goal remains right; only the mechanism is fragile.

### 4.3 `student_concerns` is transmitted to both agents but addressed by neither prompt

**Evidence:** `agents/assessment_coordinator.py:157` and `agents/support_agent.py:131` both include `"student_concerns"` in the payload. Neither `COORDINATOR_ROUND_PROMPT` nor `SUPPORT_ROUND_PROMPT` contains instruction for it; it appears only as one clause inside the list defining a "meaningful issue" (`agents/prompts.py:17`).

**Consequence:** The one input that directly states student intent has no defined effect on candidate ordering or selection. A student who writes "I'm worried my survey number doesn't match the article" receives feedback ordered by the system's own priority, not their stated concern. This weakens PRD §8.1 (RV-04, prioritizing meaningful candidates) and undercuts the student-agency premise of the whole product.

**Recommendation:** Add to the Coordinator prompt: *When `student_concerns` names a specific area and the draft evidence supports it, order `issues` so that area is first. Do not invent an issue to honor the concern; if the concern is unsupported by the draft, leave the ordering unchanged.* Mirror the ordering requirement in the Support prompt.

### 4.4 "Meaning notes" manufactures the vocabulary-shape repairs

**Evidence:** `agents/prompts.py:94` — "Vocabulary_options may contain up to four context-compatible words **or meaning notes**…" The schema is `vocabulary_options: list[str] = Field(max_length=4)` (`agents/support_agent.py:65`). Two thinking-mode repairs consisted of eight validation errors beginning `candidates.0.hint.vocabulary_options.0 — Input should be a valid string`.

**Recommendation:** Do not change the schema. State the shape in the prompt: *Each entry is one plain string. For a meaning note, write `word — meaning` as a single string.* This removes the repair class at zero implementation cost. The report's suggestion to reconsider the schema (§16.4) would also work but adds ambiguity where a one-line prompt edit does not.

### 4.5 Explicit genre selection is enforceable without the model

**Evidence:** `agents/prompts.py:9` — "A student genre correction is already reflected in `genre_selection`; reassess directly without asking the student to confirm it." The validator then requires `working_genre == genre_selection` when the selection is explicit (`agents/assessment_coordinator.py:~278`). Scenario #6 still produced the repair "The working genre must match the student's explicit selection."

**Recommendation:** When `genre_selection` is not `auto`, set `working_genre` in code before the call and let the model assess under it. There is nothing to infer, so leaving the field to the model creates a repair path with no corresponding benefit.

### 4.6 `source_dependent` has no explicit no-source rule

**Evidence:** `agents/prompts.py:20` states that source-dependent issues require `source_dependent=true` and a `source_location`, but never states the converse. Two repairs across the paired runs were "Source-dependent findings require supplied source material."

**Recommendation:** Add one sentence: *When `source_material_available` is false, set `source_dependent` to false for every issue and record the limitation in `source_limitations` instead.*

### 4.7 The silent `regression` default trades a visible cost for an invisible one

**Evidence:** The outcome report records that defaulting optional fields reduced the full run from 27 repairs to 2. That is a genuine efficiency win. But `regression` is the single field where a silent omission is pedagogically unacceptable — the PRD (§8.4, RV-26; §8.6) forbids hiding a regression, and `false` is indistinguishable from "model did not consider it."

**Recommendation:** Keep `regression` required and use a targeted single-field repair, or add a `regression_decided: bool` companion that must be present. This is a deliberate trade: two repair calls in exchange for making hidden-regression failures loud. The other defaulted fields (`source_location`, `clarification_choices`) carry no such risk and can stay optional.

**Validated disposition:** Do not adopt this recommendation. Required field presence or a self-declared companion does not prove the model reviewed the draft for regressions. Retain the false default, record omissions diagnostically without repair, and strengthen actual regression/final-comparison evidence. The two historical omissions do not establish that exactly two future repairs would occur.

### 4.8 Both payloads carry context that is not needed

Support's round payload includes the full `source_material` even when no issue is `source_dependent`, and the full `clarification_history` on every round rather than only when relevant. Neither causes a failure; both add prompt tokens to every revision review at a point where token cost is the deciding factor between the two modes.

**Recommendation:** Omit `source_material` when no Coordinator issue has `source_dependent=true` and no `source_limitations` are present. Omit `clarification_history` on `revision_number > 0` when no clarification occurred in the session.

---

## 5. Proportionality Requires Controlled Review

Candidate count against draft length, from the non-thinking acceptance run:

| Draft length | Scenarios | Candidates |
| --- | --- | --- |
| 8–22 words | #7, #14, #15, #18, #28, #29 | 2–3 each |
| 35–57 words | #2, #3, #4, #6, #10, #17, #19, #22 | 1–3 |
| 95–177 words | #1, #13, #21, #24, #25, #27 | 0–3 |
| **411 words** | **#23** | **1** |

These scenarios do not isolate length: #7 and #15 intentionally exercise three-goal behavior, while #23 requests a small prioritized issue set. Candidate-per-word ratios and the previously stated 25× difference are not validated quality or workload measures. Per-call token totals also include instructions and generated feedback, so they do not measure assessment effort by draft length.

**Validated recommendation:** Do not add fixed length-based candidate quotas. Add a matched same-grade, same-genre, same-assignment pair at approximately 60 and 400 words, with comparable writing quality and intentional issue categories and no prescribed candidate count. Use repeated non-thinking outputs and blinded educator review to assess candidate count, total feedback length, relevance, prioritization, and manageability. Even this better-controlled pair does not prove that length alone caused a difference.

**Related observation:** The manifest hint-step distribution is `[3,3]` in 12 scenarios, `[3,3,3]` in 7, `[3]` in 7, `[3,4,4]` in 1, `[4]` in 1, and no hints in 2. Nineteen scenarios have the two exact shapes previously named, not 27. Three-step hints dominate, but step count is not itself a quality measure.

**Fixture check resolved:** #23's questioned sentence does not appear literally in its assignment or teacher directions and is relevant to its subject of evidence-based informational writing. Literal task-language leakage is not confirmed; naturalness as student prose remains a fixture-design judgment.

---

## 6. Coverage Gaps the Manifest Under-Reports

### 6.1 Final comparison is exercised in 4 of 30 scenarios

The full run reached final reflection in #1, #8, #11, and #20. Final original-to-final reflection is success criterion #6 (PRD §15), and it is the mechanism that must never fabricate improvement. Four scenarios still provide limited coverage for high-risk output, especially regressions and partial progress.

**Recommendation:** Add final-comparison stages to at least #7, #9, and #15 — the three where the revision produced a regression, deferred goals, or a partial improvement. Preserve the existing four cases.

### 6.2 #24 returned `direct_response` with zero candidates

A 177-word argument with real language errors received no revision path at all. That is defensible under the optional-mechanics rule and the targeted correction shows the guard working. But an essay receiving no actionable feedback is a pedagogically significant outcome, not a clean pass. It should go to educator review explicitly rather than sit in the acceptance table as a success.

### 6.3 Candidate references nest in #14, #15, and #18

In #15:

- goal 2 → `"Students would water plants. This would help everyone."`
- goal 3 → `"This would help everyone."`

Selecting both highlights overlapping text, and the split looks like one issue divided into two goals — close to the quota-filling the PRD prohibits. #14 and #18 show the same pattern. Containment alone does not prove semantic duplication.

**Validated recommendation:** Group identical, nested, and transitively overlapping references into one union highlight with all goal IDs and an explicit feedback-panel explanation. Preserve each exact quote and remove the group when its last goal is deselected. Do not offset text or reject every nested reference as a manufactured issue; review semantic duplication separately.

---

## 7. Efficiency Opportunities Requiring No Additional Runtime Model Calls

| Opportunity | Expected effect | Effort |
| --- | --- | --- |
| Prompt fixes in §4.4–§4.6 | Fewer avoidable repairs; no numerical savings claim | Prompt text only |
| Deterministic `working_genre` (§4.5) | Removes mismatch-only repair path | Small code change |
| Nested-reference grouping (§6.3) | Defines existing UI behavior; no quality inference | UI code and tests |
| Conditional payload fields (§4.8) | Potential prompt-token savings; measure quality and cost | Small code change |
| Support final-mode pass-through | Avoids regenerating two verbatim fields | Small code change |

At the time of the review, Support validated `original_strengths` and `future_possibilities` as byte-identical to Coordinator input. Passing them through avoids unnecessary output tokens, provided bounded-language validation moves to the Coordinator boundary. The integrated prompt/schema work should share one authorized acceptance evaluation rather than paying for a full run per substage.

---

## 8. What Remains Genuinely Blocked

These cannot be resolved by prompt edits and require the educator gate (`EDUCATOR_REVIEW_PROTOCOL.md`):

1. **Tone and density by grade.** Whether three goals on a 17-word draft is overwhelming, and whether one goal on a 411-word essay is too thin, are educator judgments informed by the new controlled fixture pair.
2. **Hint specificity versus answer leakage.** Both PRD authorship checks (could the student paste it; does it name the target idea) require a human reading full context.
3. **#24's zero-candidate outcome.** Whether "no revision needed" is the right call for that essay is a classroom question.
4. **Feedback length.** Mean candidate prose is ~170–190 words per goal. Whether that is readable for a 10-year-old multilingual learner is not testable from tokens.
5. **Actual screen-reader output and a keyboard-only final loop** remain separate open checks.

---

## 9. Recommended Sequence

| Order | Action | Basis | Evidence cost |
| --- | --- | --- | --- |
| 1 | Correct report counts, documentation drift, aggregation rules, and evidence capture | §§3–7 | No model calls |
| 2 | Integrate Coordinator framework coverage, low-risk prompt contracts, explicit genre, and mechanics field | §§4.1–4.6 | Mocked tests during stages |
| 3 | Add final cases #7/#9/#15 and controlled density fixtures #31/#32 | §§5–6 | One full non-thinking run plus repeated density checks |
| 4 | Implement overlap grouping and measured payload/final pass-through optimizations | §§6.3–7 | Browser checks; targeted real checks only if needed |
| 5 | Conduct educator and accessibility gates | §8 | External human review |

The optional `regression=False` default remains in place. Required booleans are not used as a substitute for regression-quality evidence. Full real-model evaluation is batched after integration rather than repeated for each prompt/schema substage.

---

## 10. Boundaries

- All evidence is synthetic. No learner-outcome, motivation, engagement, retention, usability, or educator-approval claim is supported by this review.
- Findings in §4–§7 are code-and-artifact observations, not pedagogical judgments.
- Model-level scenario runs are not equivalent to complete browser walkthroughs. The current fixture set adds two controlled density scenarios to the original 30.
- The earlier documentation drift is resolved: current `CLAUDE.md` specifies explicit non-thinking runtime and the current test count. Historical 128/151-check statements should not be reused as current status.
