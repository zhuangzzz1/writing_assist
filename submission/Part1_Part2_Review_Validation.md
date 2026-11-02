# Validation of the External Review of Parts 1 and 2

> **Historical review record:** This document evaluates an earlier draft revision. It is not a current statement of application behavior or evidence status.

**Reviewed document:** `submission/Part1_Part2_Draft.md` (as it stood before revisions)
**Review input:** `submission/Part1_Part2_Review_Feedback.md`
**Validation method:** independent re-derivation from the implementation, the saved run database, and the assignment text
**Date:** 2026-11-02

---

## Summary judgment

The review is **substantively correct and worth acting on**. It proposes **thirteen specific corrections** — eleven about factual or internal consistency, two about timing and metrics — and **all thirteen are confirmed** by direct inspection of the code and the saved runs, including every one it ranked highest-priority. Of its nine broader recommendations, **seven were adopted as written**, one (the evidence plan) was adopted in modified form, and one (trimming Part 1) was not achieved.

Two of the review's own formulations were imprecise and are noted here rather than adopted unchanged: its "one-call route" characterization of teacher review holds only when review is selected on the initial assessment, and its estimate of "approximately 1,800 words" for Part 1 undercounts the actual 1,851 by a trivial margin that has no bearing on its point about length.

The review contains **no fabricated findings**: every source citation it gives resolves to what it describes, including `support_agent.py:52-63`, `langgraph_core/graph.py:53-57`, and the saved-path sequence it recomputes.

---

## Verification of the specific corrections

Each row was checked against the named source. "Evidence" cites what was actually inspected, not the review's assertion.

### Factual and internal inconsistencies

| # | Draft claim | Reviewer's finding | Evidence inspected | Verdict |
| --- | --- | --- | --- | --- |
| 1 | Route chosen "on every submission" | Conflicts with local empty-input rejection and the clarification-limit override | `state.py:76-79` calls `validate_writing_input` before the graph exists; `nodes.py:47-71` converts a third clarification request to `teacher_review` at `clarification_count >= 2` | **Confirmed.** Reworded to "every nonempty submission, subject to two deterministic overrides" |
| 2 | "Nothing is retained beyond the user's **Delete my data** action" | Ambiguous; omits cloud filesystem replacement | `layout.py:290-305` deletes on request only; no expiry job exists anywhere in `storage/` or `langgraph_core/` | **Confirmed, and it was simply false as written.** Replaced with the Delete-or-filesystem-replacement wording from `CLAUDE.md` |
| 3 | "teacher-review, clarification, and direct-response routes reach the model exactly once" | False for resumed clarification; the incomplete run used four calls | `data/v1_official.db`, thread `05335ea1`: 4 API calls. `nodes.py:73` returns to `assessment_coordinator` after clarification, and `graph.py:69` wires that edge | **Confirmed — the most serious error in the draft.** Claim deleted. Precisely: direct response and *initially selected* teacher review reach the model once, because those two nodes make no API call; teacher review reached through the clarification limit is preceded by multiple coordinator calls (thread `c4b9428e`: 3) |
| 4 | Coordinator parse failure described as terminal (line 102) but recoverable (lines 69, 76); provider and Support failures implied to trigger human review | Conflates three different behaviors | `assessment_coordinator.py:84-109,178-179` → `ask_clarification` fallback; `graph.py:119-122` re-raises provider errors and records them via `record_error`; `support_agent.py:109-116` raises `ResponseValidationError` with no route change; `layout.py:70-88` maps all of these to error/info banners | **Confirmed.** Rewritten as three separate cases: malformed coordinator output → recoverable clarification fallback; provider or Support Agent failure → error, no feedback, retry offered, no human review; educational boundary → simulated teacher review |
| 5 | Success criterion requires all four routes; strong narrative "supported without being told to change something unnecessary" | No real `direct_response` run; the same paragraph contradicts line 198 | The 10 saved runs contain zero `direct_response` rows; thread `1559a018` returned **three** priorities (`feedback_priorities` has 3 entries) | **Confirmed, and self-contradicting within one paragraph.** `direct_response` now marked unverified outside tests; the strong-narrative case is presented as an open problem |
| 6 | "four-node LangGraph state graph" | There are five | `graph.py:53-57` registers assessment, clarification, support, teacher review, direct response | **Confirmed.** Corrected to "five nodes — two LLM-agent nodes and three deterministic nodes" |
| 7 | "Every model call carries … the full clarification history" | False for the Support Agent | `support_agent.py:52-63` — the payload has no `clarification_history` key | **Confirmed.** Corrected: every *coordinator assessment* carries it; the Support Agent does not |
| 8 | "The Support Agent consumes exactly those" | Omits writing, grade, assignment, concerns | `support_agent.py:53-56` includes all four | **Confirmed.** Corrected to "original task context plus the coordinator's findings" |
| 9 | Six steps and four API calls *demonstrate* exact checkpoint resume | They demonstrate path length | `graph.py:104-110` gates resume on `record.status == "awaiting_clarification"` and passes `Command(resume=...)` with the stored thread ID; the checkpointer row is the mechanism | **Confirmed as an evidential overreach.** Rewritten to lead with thread ID, checkpoint, and recorded path; counts demoted to supporting metrics |
| 10 | "the student never sees the evidence summary" | Implies access control the demo lacks | `layout.py:327-331` and `observability.py` render both panels on the same page; `_session_id()` is a UUID filter, not a role | **Confirmed.** Reframed as separately *labeled*, not access-controlled, with the same-URL caveat stated |
| 11 | "feedback plus one targeted practice exercise" (line 18) | Practice is conditional | `support_agent.py:113-123`; `assessment_coordinator.py:152-153` sets `needs_practice=False` when no gaps are found | **Confirmed.** Corrected to "targeted practice when warranted" |

### Timing and metrics

| Claim | Reviewer's correction | Computed | Verdict |
| --- | --- | --- | --- |
| Draft mixes invocation duration with the UI's node-time sum | Standardize on one and label it | UI shows `sum(duration_ms)` over `execution_logs` (`observability.py:32-40`). Normal: node 6.358 s vs duration 6.367 s. Boundary A: 2.243 vs 2.251. Boundary B: 2.784 vs 2.790 | **Confirmed.** Table now labeled "LLM/node time (dashboard label)" with a footnote giving both figures |
| Clarification limit = 4 steps, 2 calls, 5.65 s | Should be **6 steps, 3 calls, 5.63 s** node / 5.65 s duration | `c4b9428e`: path `Assessment Coordinator → Clarification → Assessment Coordinator → Clarification → Assessment Coordinator → Teacher Review`; 6 logs, 3 with `api_call`, node sum 5.628 s, duration 5.651 s | **Confirmed — the most important numerical correction.** Fixed |

Full recomputation from `data/v1_official.db`, all ten runs:

| Thread | Route | Steps | API calls | Node time | Duration |
| --- | --- | ---: | ---: | ---: | ---: |
| `edb47657` | `support_agent` (normal fixture) | 2 | 2 | 6.36 s | 6.37 s |
| `0c302376` | `support_agent` (second normal pass) | 2 | 2 | 6.46 s | 6.47 s |
| `05335ea1` | ×2 clarify → `support_agent` | 6 | 4 | 9.58 s | 9.60 s |
| `885746a4` | `teacher_review` / concerning | 2 | 1 | 2.24 s | 2.25 s |
| `42f29e6a` | `teacher_review` / frustration | 2 | 1 | 2.78 s | 2.79 s |
| `6dbb206a` | `ask_clarification` (short) | 1 | 1 | 1.68 s | 1.68 s |
| `30b5d38b` | `ask_clarification` (non-writing) | 1 | 1 | 1.28 s | 1.29 s |
| `56daf665` | `teacher_review` / concerning (short) | 2 | 1 | 1.59 s | 1.60 s |
| `1559a018` | `support_agent` (strong narrative) | 2 | 2 | 5.87 s | 5.88 s |
| `c4b9428e` | `teacher_review` / clarification_limit | 6 | 3 | 5.63 s | 5.65 s |

### Broader recommendations

| Recommendation | Action taken | Notes |
| --- | --- | --- |
| Embed figures; stop treating the screenshot list as an internal checklist | **Adopted in modified form** | Restructured as an evidence appendix with claim-matched captions, cut from 12 figures to 5 core plus 3 optional. The list is retained rather than deleted, because a screenshot list was an explicit deliverable request; it is labeled production notes to remove before submission |
| Include the normal case's actual output, not a summary | **Adopted** | Added selected excerpts from `edb47657` (strengths, two priorities, the practice block, with omissions marked), the clarification exchange from `05335ea1` reproduced in full, and the teacher-review record from `885746a4` with its evidence list excerpted |
| Don't attribute to a figure more than it shows | **Adopted** | Three limitations are now stated where the relevant artifact is described: the normal capture does not show all priorities or the exercise; the incomplete capture shows path and metrics but not the Q/A exchange; and the Boundary A capture shows the category, reason, follow-up, and the "Evidence:" heading while the quotes themselves fall below the visible area |
| Single-agent comparison is overclaimed | **Adopted** | Recast as a comparative design advantage. Added the explicit statement that a single agent could emit structured output a graph validates |
| Distinguish "enables retry" from implemented retry | **Adopted** | `graph.py:112-131` has no retry path; the draft now says the separation is a design affordance, not a V1 capability |
| Add educational success criteria | **Adopted** | Five student-facing tests added ahead of the operational ones |
| Neutralize "inventing one would be worse" | **Adopted** | Replaced with an institution-approved-protocols scope statement |
| Soften "three failure modes are **common**" | **Adopted** | Changed to a claim about what this application is designed around, which needs no citation |
| Trim Part 1 (reviewer: ~1,800 words) | **Not achieved** | See open items |

---

## Additional precision on where the clarification history lives

The review's claim on this point is correct as written: `Part1_Part2_Review_Feedback.md:60` says the **incomplete-case screenshot** does not show the full two-question history and final supported output, and that is exactly right — the capture shows the resumed path and metrics, not the exchange. Nothing in the review asserts anything about the wider UI.

One further detail is worth recording, because it bears on how the draft cites the exchange. The application has no readable rendering of `clarification_history`; the only place it appears is inside the collapsed **"Final state and state changes"** JSON panel (`observability.py:52-54`), where it is buried in raw state rather than shown as a conversation. The draft therefore sources the questions and answers to the saved run in SQLite and labels them as selected excerpts, rather than implying a screenshot or a UI panel displays them.

---

## Two findings the review missed

**1. The evidence table is a selection, not a census, and did not say so.** There are ten saved runs in `data/v1_official.db`; the draft's table had nine rows, and the tenth (`0c302376`, a second pass over the normal fixture that also returned `support_agent` with three priorities and a thesis exercise) was omitted without explanation. Omitting it changes no conclusion, but a reader who counts will notice. The draft now opens the table by identifying it as selected results from nine of the ten runs and naming the omitted one. It also means the worked-example defect described in observation (b) is **reproducible across two independent runs**, which strengthens it as a Part 3 finding — that is now visible in the recomputed data above and worth carrying into Part 3.

**2. Part 1 exceeds its own length target, and the review's additions are what pushed it over.** The review's "approximately 1,800 words" is a fair approximation of the pre-revision 1,851. The substantive issue is not the estimate but the direction: the same review asks for added material (educational success criteria, the five named considerations in the learning outcomes) while also asking for reduction. After revision Part 1 is **2,207 words** and Part 2 is **2,227**. The syllabus sets no word limit — only "concise and focused on essential design decisions" — but `project_plan.md` targets 2–3 pages, and 2,207 words is roughly 4–5 typeset pages. The length is over the project's own target, not over any stated assignment requirement.

---

## Remaining open items

| Item | Status | Why it matters |
| --- | --- | --- |
| **Part 1 length** | Open | 2,207 words against a 2–3 page project target. The cheapest cut is section 4's enumeration of coordinator output fields, which duplicates the Part 2 field table. Estimated saving: 150–200 words. |
| **Actual figures** | Blocked | Four of the eight proposed figures exist as captures in `data/evidence/`; four are missing. The captions are written and claim-matched; the images need a browser session. Highest priority among the missing: the pending-clarification panel and the expanded coordinator `state_changes`. |
| **Part 1 success claims rest on V1 only** | By design | Everything in this document describes V1. The rubric's 20% "Functional Application" criterion concerns V2, and nothing here should be read as evidence for it. |

---

## What this means for the submission

The correction pass did not change the architecture, the evidence base, or any conclusion about V1's behavior. It changed what the draft **claims** to what the draft **can show**: five of the thirteen corrections were cases where the prose asserted something the system does not do — a route that reaches the model once when a clarification-route review reaches it three times, a graph with four nodes that has five, a history delivered to an agent that never receives it, a summary a viewer cannot actually be kept from seeing, and a success criterion requiring a route that never ran. Those are the errors worth catching before a grader catches them, and they are all now either fixed or restated with the limitation attached.

The substance the rubric cares about held up under the check: the coordinator **can select four routes, and three were observed in real V1 runs** (`support_agent`, `ask_clarification`, `teacher_review`; `direct_response` remains unobserved outside mocked tests), the clarification is a genuine checkpoint resume, the safety route structurally bypasses the feedback agent, the two agents have distinct output contracts, and the failure modes are real and recorded rather than hidden.

One delivery issue sits outside the scope of Parts 1 and 2 and should be resolved before submission: **`http://localhost:8765` is not instructor-accessible.** The syllabus accepts either a working link or the required application/configuration files, so a deployed URL is one route and a packaged submission is another. This is not the only remaining task — four figures, Parts 3–6, and the AI Use Acknowledgment are also outstanding — but it is the one that cannot be repaired by editing prose.
