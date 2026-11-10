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
2. **Six of six measured repair categories are prompt or validation defects, not model failures.** Each is eliminable in prompt text or deterministic code without another model call.
3. **Prompt responsibility is split in a way that makes one requirement structurally unachievable.** RACES coverage is owned by the Support Agent, which is forbidden from adding issues. The observed #4 gap is a consequence of that design, not a reasoning failure.
4. **Proportionality is inverted.** A 17-word draft receives three revision goals; a 411-word grade-7 essay receives one. Nothing in either prompt calibrates issue count to draft length or grade band.

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

## 3. Repair Categories: All Six Are Prompt or Validator Defects

From `repair_patterns` in `data/evidence/v3_investigation_manifest_20261110.json`:

| Category | Count | Root cause | Fix |
| --- | ---: | --- | --- |
| omitted optional regression field | 2 | Contract ambiguity (see §4.7) | Judgment call — see §4.7 |
| vocabulary option shape/type | 2 | Prompt permits objects; schema requires `list[str]` | Prompt text (§4.4) |
| source-dependent finding without source | 2 | Prompt never states the no-source rule | Prompt text (§4.6) |
| explicit genre correction mismatch | 1 | Enforceable in code, left to the model | Deterministic assignment (§4.5) |
| non-obscuring mechanics guard | 1 | Keyword whitelist; see §4.2 | Structured field (§4.2) |

No repair observed in this set required judgment the model could not have supplied with clearer instructions. The two full-run repairs in `v3_acceptance_evaluation_20261110T160932Z.json` both fall into the first row; the corrected run used schema `v3.2.0`, so the `v3.2.1` default has not itself been exercised by a full acceptance run.

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

### 4.8 Both payloads carry context that is not needed

Support's round payload includes the full `source_material` even when no issue is `source_dependent`, and the full `clarification_history` on every round rather than only when relevant. Neither causes a failure; both add prompt tokens to every revision review at a point where token cost is the deciding factor between the two modes.

**Recommendation:** Omit `source_material` when no Coordinator issue has `source_dependent=true` and no `source_limitations` are present. Omit `clarification_history` on `revision_number > 0` when no clarification occurred in the session.

---

## 5. Proportionality Is Inverted

Candidate count against draft length, from the non-thinking acceptance run:

| Draft length | Scenarios | Candidates |
| --- | --- | --- |
| 8–22 words | #7, #14, #15, #18, #28, #29 | 2–3 each |
| 35–57 words | #2, #3, #4, #6, #10, #17, #19, #22 | 1–3 |
| 95–177 words | #1, #13, #21, #24, #25, #27 | 0–3 |
| **411 words** | **#23** | **1** |

Per-call cost is comparable across these (#23 ≈ 2,800 tokens/call; #15 ≈ 3,270 tokens/call), so the system spends roughly the same effort regardless of how much student text it is assessing. Marginal feedback per word of student writing is roughly 25× lower on the 411-word essay than on the 17-word draft.

Two causes:

1. **No length or grade calibration in either prompt.** "Grade-appropriate" is the only guidance, and it is not a quantity.
2. **`issues` is flat at `max_length=5`.** The prompt says "identify one to five issues" with nothing that turns the 1–5 range into a function of draft size or grade band.

**Recommendation (calibration, not quota — a quota would violate the no-manufactured-issues rule):** Add to the Coordinator prompt: *For drafts under roughly 60 words, prefer one or two issues; a short draft rarely supports more. For drafts over roughly 250 words, sweep claim, evidence explanation, paragraph-level cohesion, and closure before concluding that a single issue is all that matters. A single issue on a long draft is acceptable only when the rest genuinely holds.*

**Related observation:** 27 of 30 scenarios returned hint step counts of exactly `[3, 3]` or `[3, 3, 3]`. The "two to four linked steps" range (`agents/prompts.py:94`) is being used as a constant. If step count was meant to scale with passage complexity, that is not happening; if a constant three is intended, the range is decoration.

**Fixture check needed:** #23's draft contains "Students should identify which claims came from the supplied passage, which came from observation, and which remain uncertain." That reads as instruction rather than student prose, and the model's single candidate references that sentence. Verify the fixture is not leaking task language into the draft.

---

## 6. Coverage Gaps the Manifest Under-Reports

### 6.1 Final comparison is exercised in 2 of 30 scenarios

Only #1 and #11 reached a final reflection. #7, #9, #12, #14, #15, #19, and #28 ran revision rounds with no final findings in the evidence. Final original-to-final reflection is success criterion #6 (PRD §15), and it is the mechanism that must never fabricate improvement. Two scenarios is thin coverage for the highest-risk output in the product.

**Recommendation:** Add final-comparison stages to at least #7, #9, and #15 — the three where the revision produced a regression, deferred goals, or a partial improvement. These are the cases where fabrication is most likely.

### 6.2 #24 returned `direct_response` with zero candidates

A 177-word argument with real language errors received no revision path at all. That is defensible under the optional-mechanics rule and the targeted correction shows the guard working. But an essay receiving no actionable feedback is a pedagogically significant outcome, not a clean pass. It should go to educator review explicitly rather than sit in the acceptance table as a success.

### 6.3 Candidate references nest in #14, #15, and #18

In #15:

- goal 2 → `"Students would water plants. This would help everyone."`
- goal 3 → `"This would help everyone."`

Selecting both highlights overlapping text, and the split looks like one issue divided into two goals — close to the quota-filling the PRD prohibits. #14 and #18 show the same pattern.

**Recommendation:** Add a deterministic check that no candidate reference contains or is contained by another within a round, and route failures to repair. This is cheap, needs no prompt change, and removes an ambiguity that will surface as a confusing UI state.

---

## 7. Efficiency Opportunities Requiring No Model Calls

| Opportunity | Saves | Effort |
| --- | --- | --- |
| Prompt fixes in §4.4–§4.6 | ~5 repair calls per acceptance run | Prompt text only |
| Deterministic `working_genre` (§4.5) | 1 repair category | Small code change |
| Nested-reference check (§6.3) | Repairs currently undetected | Small code change |
| Conditional payload fields (§4.8) | Prompt tokens on every revision round | Small code change |
| Support final-mode pass-through | 2 of 4 output fields generated verbatim | Small code change |

On the last item: `agents/support_agent.py:224` and `:226` validate that `original_strengths` and `future_possibilities` are byte-identical to Coordinator input. Support is spending tokens regenerating text that must match exactly. Pass them through and let Support produce only `improvements`, `regressions`, and `conclusion`.

---

## 8. What Remains Genuinely Blocked

These cannot be resolved by prompt edits and require the educator gate (`EDUCATOR_REVIEW_PROTOCOL.md`):

1. **Tone and density by grade.** Whether three goals on a 17-word draft is overwhelming, and whether one goal on a 411-word essay is too thin, are educator judgments.
2. **Hint specificity versus answer leakage.** Both PRD authorship checks (could the student paste it; does it name the target idea) require a human reading full context.
3. **#24's zero-candidate outcome.** Whether "no revision needed" is the right call for that essay is a classroom question.
4. **Feedback length.** Mean candidate prose is ~170–190 words per goal. Whether that is readable for a 10-year-old multilingual learner is not testable from tokens.
5. **Actual screen-reader output and a keyboard-only final loop** remain untested per §16.7.

---

## 9. Recommended Sequence

| Order | Action | Basis | Cost |
| --- | --- | --- | --- |
| 1 | Prompt fixes: vocabulary string shape, no-source rule, `student_concerns` priority | §4.4, §4.6, §4.3 | Prompt edit, no code |
| 2 | Deterministic `working_genre` for explicit selection | §4.5 | Small code |
| 3 | Replace keyword guard with `obscures_meaning` field | §4.2 | Schema + prompt |
| 4 | Move RACES coverage to Coordinator `framework_coverage` | §4.1 | Schema + prompt |
| 5 | Nested-reference validation check | §6.3 | Small code |
| 6 | Length/grade calibration in Coordinator prompt | §5 | Prompt edit, needs educator read |
| 7 | Add final comparison to #7, #9, #15 | §6.1 | Fixture + one run |
| 8 | Educator gate | §8 | External |
| 9 | Decide `regression` default | §4.7 | Judgment call |

Steps 1–5 are mechanical and independently testable. Step 6 changes behavior and should be reviewed by an educator before it is treated as an improvement. Step 9 is the only item here where I would recommend *deliberately accepting a worse repair count* in exchange for a louder failure mode.

---

## 10. Boundaries

- All evidence is synthetic. No learner-outcome, motivation, engagement, retention, usability, or educator-approval claim is supported by this review.
- Findings in §4–§7 are code-and-artifact observations, not pedagogical judgments.
- The 30 acceptance scenarios are model-level runs, not 30 browser walkthroughs.
- `CLAUDE.md` currently states `DEEPSEEK_THINKING=true` is required and cites 128 checks. The current state is explicit non-thinking and 151 checks. That drift should be corrected so the repository contract matches the implementation.
