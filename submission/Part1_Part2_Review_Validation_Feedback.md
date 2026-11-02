# Feedback on `Part1_Part2_Review_Validation.md`

> **Historical review record:** This document evaluates an earlier draft revision. It is not a current statement of application behavior or evidence status.

## Overall verdict

The revised draft is substantially improved, and most technical corrections are properly implemented. However, `Part1_Part2_Review_Validation.md` **is not yet a reliable sign-off document**. It contains several incorrect claims about the earlier review and misses some remaining contradictions in the revised draft.

This assessment is based on a comparison of:

- `submission/Part1_Part2_Review_Validation.md`
- `submission/Part1_Part2_Draft.md`
- `submission/Part1_Part2_Review_Feedback.md`
- The saved runs in `data/v1_official.db`
- The existing screenshots in `data/evidence/`

## Significant corrections needed

### 1. The outline-context contradiction remains

`Part1_Part2_Draft.md:148` says the second outline question was built from the student's first answer. But lines 209–215 correctly identify that question as the generic validation fallback, not a refinement of the first answer.

Replace the line 148 example with the final Support Agent's use of the student's clarified main point. The current passage cannot simultaneously claim that the second question used the first answer and that it was the generic fallback.

### 2. The “partial disagreement” misattributes a claim to the review

`Part1_Part2_Review_Validation.md:82` says the review claimed the application did not render the history anywhere. The review actually said the **screenshot did not show the full history** (`Part1_Part2_Review_Feedback.md:60`).

The raw-JSON clarification is useful, but it should be presented as additional precision—not disagreement with a claim the review never made. The statement at validation line 16 that the review contains no fabricated findings can remain separate, but the validation itself should not introduce an unsupported attribution.

### 3. Four routes were not observed on real input

Validation line 113 says the coordinator “does take four distinct routes on real input.” The saved runs observed only:

- `support_agent`
- `ask_clarification`
- `teacher_review`

`direct_response` was implemented and unit-tested but not observed in a real V1 run.

Use: **“The coordinator can select four routes; three were observed in real V1 runs.”**

### 4. The claimed missing configuration evidence is incorrect

Validation line 92 says the smoke-comparison numbers previously existed only in the PRD. The pre-revision draft already contained the 6.60 s, 7.49 s, and 2.75 s comparison in Part 2 §1.

Remove this as a “finding the review missed.” It is accurate to say that the comparison remains supported by a small smoke set, but not that the original draft lacked the numbers.

### 5. The Boundary A screenshot still does not support the whole claim

Draft line 195 says the entire teacher panel fits on screen. The capture shows the category, reason, follow-up, and the **“Evidence:” heading**, but the actual evidence quotes are below the capture. The full student message is also not visible.

Attribute those details to the saved-run excerpt, not the screenshot. Revise the prose and caption so each artifact supports only what it visibly contains.

### 6. The teacher-review one-call generalization is too broad

Validation line 32 calls teacher review a one-call route. Initially selected teacher review uses one coordinator call, but the observed clarification-limit teacher-review run uses three coordinator calls.

The earlier review's recommendation on this point was also too broad. The precise statement should distinguish:

- **Direct response:** one coordinator call in the initial route.
- **Initially selected teacher review:** one coordinator call.
- **Teacher review reached through the clarification limit:** multiple coordinator calls may precede review; the observed run used three.

## Evidence and inventory issues

### Figure count

Validation line 103 has the wrong figure count. Four of the eight proposed figures exist, so **four are missing**, not five. The remaining-open-items table should reflect the complete inventory, while still identifying the pending-clarification and expanded-state captures as the highest-priority additions.

### Omitted tenth run

Validation line 90 correctly says the evidence table should include the second normal run or identify itself as a representative selection. The revised draft table still has nine rows without that explanation.

Either add the tenth run or introduce the table with wording such as: **“Selected results from nine of the ten saved V1 runs; the omitted run is a second normal-fixture pass.”**

### “Verbatim” labels

Draft lines 197–221 contain omissions and summarized evidence. In particular, parts of the normal-case next steps are shortened, and the Boundary A evidence list is summarized rather than reproduced in full.

Use **“Selected excerpts”** or **“Edited excerpts”**, or mark every omission explicitly. Reserve “verbatim” for text reproduced exactly except for clearly indicated omissions.

### Figure wording

- Draft line 193 says “five cases” when it means **five figures**.
- Figure captions should not claim that screenshots alone prove model-controlled routing or the absence of keyword matching. Those conclusions require the prompts and implementation as supporting evidence. A screenshot can document the displayed route, category, path, and metrics; the code and prompts establish how they were produced.

## Smaller validation and draft corrections

- Approximately 1,800 words is a reasonable approximation of 1,851, not a “quantitative slip” (`Part1_Part2_Review_Validation.md:16,94`). The concern about increased length remains valid, but the numerical criticism should be removed.
- The summary's counts of adopted recommendations do not match the nine-row broader-recommendations table. Reconcile the categories and totals.
- Validation line 115 should not call application access the “only remaining” potential blocker. Missing figures and Parts 3–8 also remain. A localhost URL is not instructor-accessible, but the syllabus permits either a working link or the required application/configuration files.
- Draft line 44 should say **“a further clarification request after two answers”**, not “a second unanswered clarification request.” The limit is triggered after two answers when the coordinator requests clarification again.
- Draft line 114 should say **malformed assessment output** falls back to clarification. A schema-valid but poor assessment can still lead to weak feedback; fail-safe routing does not convert every bad assessment into a question.

## What the validation gets right

The following revisions are supported by the implementation and saved evidence:

- The graph has five nodes: two LLM-agent nodes and three deterministic nodes.
- Support Agent receives original task context and the coordinator handoff, but not `clarification_history` directly.
- Coordinator validation failure uses clarification fallback, whereas provider and Support Agent failures stop without generating feedback or automatically requesting teacher review.
- Node-time and invocation-duration values have been separated more clearly.
- The clarification-limit run contains six recorded steps and three API calls.
- The normal-case worked-example problem appears in both saved normal-fixture runs, strengthening it as a Part 3 candidate.
- The revised architecture discussion more appropriately presents two agents as a comparative design choice rather than claiming a single agent cannot produce validated structured output.
- The revised draft more clearly distinguishes observed routes, mocked test coverage, and unobserved real `direct_response` behavior in its detailed sections.

## Recommended revision order

1. Fix the draft's outline-context contradiction and the Boundary A screenshot attribution.
2. Correct the validation's real-route count, configuration-history claim, and unsupported attribution to the earlier review.
3. Correct the figure inventory and mark the run table as a selection or add the tenth run.
4. Relabel edited excerpts and align figure captions with what each artifact proves.
5. Reconcile the smaller wording and recommendation-count issues before treating the validation as complete.

**Bottom line:** Keep the technical revisions, but correct the validation's unsupported claims and the remaining draft contradictions before treating the review process as complete.
