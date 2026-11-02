# Review Feedback: Parts 1 and 2 Draft

> **Historical review record:** This document evaluates an earlier draft revision. It is not a current statement of application behavior or evidence status.

## Scope and overall judgment

This review compares `submission/Part1_Part2_Draft.md` with the assignment tasks, submission requirements, and grading rubric in `EDUC_6192_Fall_2026_Syllabus.md`. I also cross-checked selected claims against the implementation, the four local screenshots, and the ten runs in `data/v1_official.db`. The automated suite currently passes all 48 checks. I did not rerun live model calls or test a deployment.

**Overall:** This is a strong, unusually well-documented Parts 1–2 draft. It addresses all ten Part 1 design elements and all six relevant Part 2 behavior areas. The two roles are distinct, agent-controlled routing is meaningful, and the discussion of clarification and simulated human review is substantive.

The draft is **not ready to use as final evidence yet**. Its main weakness is not the architecture; it is the gap between a few confident statements and what the implementation or captures actually establish. Correct those statements, reconcile the run metrics, and replace the screenshot plan with evidence that visibly supports the claims. Because this document intentionally covers only Parts 1–2, no overall assignment score is appropriate.

## What is already strong

- **Clear educational purpose and users.** The grade 5–7 formative-writing use case is specific, and the need for prioritized, actionable feedback is connected to the design.
- **Meaningful agent-controlled action selection.** The coordinator chooses among support, clarification, teacher review, and direct response rather than sending every submission through the same sequence.
- **Distinct and mostly well-justified roles.** Assessment and instructional support have different responsibilities, output contracts, and prompts. The safety override and separation of assessment from feedback are especially clear.
- **Specific responsibilities and boundaries.** The draft addresses prompt injection, no essay rewriting, no invented sources, synthetic writing, external-service disclosure, and simulated rather than real teacher notification.
- **Real clarification design.** The use of LangGraph interrupts, stable thread IDs, checkpoints, and a two-answer limit is much stronger than merely saying that the app “asks questions.”
- **Honest treatment of missing evidence.** The draft explicitly says that `direct_response` was implemented and unit-tested but did not occur in the real V1 scenario set. Preserve this distinction between implemented, tested, and observed behavior.
- **Useful V1 problem candidates.** The malformed reassessment, topic-matched worked example, and strong-narrative feedback volume are observed problems that can support a genuine Part 3 review and evidence-driven V2.

## Highest-priority revisions

### 1. Correct factual and internal inconsistencies

| Draft location | Issue | Recommended correction |
| --- | --- | --- |
| `Part1_Part2_Draft.md:44` | “Every submission” conflicts with local empty-input rejection, and the clarification-limit route is a deterministic override. | Say that the coordinator selects the route for every **nonempty** submission, subject to the teacher-flag and clarification-limit rules. |
| `Part1_Part2_Draft.md:62` | The retention wording is ambiguous and omits cloud filesystem replacement. | State that SQLite retains run data and checkpoints until **Delete my data** or cloud filesystem replacement; no automatic retention period applies. |
| `Part1_Part2_Draft.md:84` | The claim that clarification routes reach the model exactly once is false for a resumed clarification flow. The incomplete run used four calls. | Limit the one-call claim to teacher review and direct response. Explain that each clarification resume invokes the coordinator again and may later invoke Support Agent. |
| `Part1_Part2_Draft.md:102` | Coordinator parse/validation failure is described as terminal here but as recoverable clarification fallback at lines 69 and 76. Provider/support failures also do not automatically request human review. | Separate three cases: malformed coordinator output → clarification fallback; provider or Support Agent validation failure → error with no feedback and an option to retry; educational boundary → simulated human review. |
| `Part1_Part2_Draft.md:108` | The self-defined real-run success criterion requires all four routes, but no real `direct_response` run occurred. The same paragraph says the strong narrative avoided unnecessary changes, while line 198 reports three improvement priorities. | Either add a genuine real direct-response observation or explicitly mark that route unverified in real runs. Present the strong narrative as an observed open problem, not as unqualified success. |
| `Part1_Part2_Draft.md:118` | The graph is described as four-node. | Change to **five nodes: two LLM-agent nodes and three deterministic nodes**. The implementation registers assessment, clarification, support, teacher review, and direct response in `langgraph_core/graph.py:53-57`. |
| `Part1_Part2_Draft.md:144` | “Every model call” carries full clarification history is inaccurate. Support Agent does not receive that history directly. | Say that every **coordinator assessment** receives the listed context, including clarification history. Support Agent receives the original task context plus the coordinator handoff, but not `clarification_history` (`agents/support_agent.py:52-63`). |
| `Part1_Part2_Draft.md:82` | “The Support Agent consumes exactly those” omits the original writing, grade, assignment, concerns, and practice flag that it also receives. | Describe a coordinator handoff **plus original task context**, rather than exclusive consumption of coordinator fields. |
| `Part1_Part2_Draft.md:163` | Six steps and four API calls demonstrate the path length, not by themselves exact checkpoint resume. | Use the stable thread ID, saved checkpoint, and resumed graph position as the evidence for exact resume; retain step/API counts only as supporting metrics. |
| `Part1_Part2_Draft.md:167` | “The student never sees the evidence summary” implies role-based separation that the demo does not provide. The teacher-facing panel is visible in the same evaluator dashboard. | Say that student and evaluator/teacher outputs are **separately labeled**, not access-controlled. No real teacher receives a notification or record. |

Also change line 18 to “feedback plus targeted practice **when warranted**,” matching the actual optional-practice behavior.

### 2. Reconcile the evidence table and timing terminology

The table at lines 175–185 appears to mix total invocation duration with the UI’s “node time” sum. These are different metrics. Pick one, label it precisely, and use it consistently in the table, prose, captions, and PRD.

For the saved browser runs, the values are:

| Run | Steps | API calls | Node-time sum shown in UI | Total invocation duration, rounded |
| --- | ---: | ---: | ---: | ---: |
| Normal fixture | 2 | 2 | 6.36 s | 6.37 s |
| Boundary A | 2 | 1 | 2.24 s | 2.25 s |
| Boundary B | 2 | 1 | 2.78 s | 2.79 s |
| Clarification limit | **6** | **3** | **5.63 s** | **5.65 s** |

The clarification-limit row in the draft says 4 steps, 2 API calls, and 5.65 s. The saved path is Assessment Coordinator → Clarification → Assessment Coordinator → Clarification → Assessment Coordinator → Teacher Review: **6 steps and 3 API calls**. This is the most important numerical correction.

### 3. Turn the evidence plan into actual, claim-matched evidence

At present, Figures 1–12 are placeholders and the screenshot list is an internal production checklist. Only Figures 1, 3, 4, and 5 have existing local captures.

- **Embed the selected figures in the submission document.** A local path such as `data/evidence/v1_normal_ui.png` is not evidence accessible to a reader of the PDF.
- **Check what each figure actually shows.** The four existing screenshots clearly support route, path, and metric claims. They do not fully show all the content attributed to them at line 196: the normal screenshot does not show all three priorities and the exercise, and the incomplete screenshot does not show the full two-question history and final supported output. Add focused output captures or concise verbatim excerpts.
- **Include the representative normal interaction’s actual output.** The draft describes the input and summarizes the rationale, but a short real excerpt of strengths, one priority, and the practice exercise would more directly confirm that the main educational interaction works.
- **Use captions that make the evidence interpretable.** For each selected figure, identify the fixture, V1 configuration, actual route, and the one conclusion the figure supports. Do not use a screenshot as proof of model quality when it only proves control flow.
- **Remove the draft note and “How to reach it” screenshot-production table from the final submission.** Replace them with figures, captions, and, where useful, compact appendices. A smaller set of well-chosen artifacts is sufficient; the assignment does not require twelve screenshots.
- **Redact submission artifacts as needed** and include no API keys, secrets, real student writing, or personally identifying information.

### 4. Strengthen the architecture justification without overstating the alternative

Sections 1.7 and 1.10 give good reasons for the split: different output contracts, traceability, failure isolation, and a structural bypass of Support Agent during review. However, lines 84 and 110 imply that a single-agent design inherently cannot expose a validated intermediate decision or route. A single agent could still produce structured output that a graph validates and routes.

Frame the claim as a **comparative design advantage**, not an impossibility:

> The two-agent split is not required for routing, but it makes the assessment decision independently inspectable and allows feedback generation to be retried or revised without changing the assessment prompt. This benefit is weighed against an extra model call, shared-state overhead, and another failure point.

Explicitly connect the choice to **educational fit, reliability, complexity, cost, and maintainability**, the considerations named in the learning outcomes. Also distinguish “enables retry without reassessment” from an actually implemented automatic retry; V1 does not have automatic retry.

### 5. Make success educational as well as operational

Section 1.10 currently emphasizes routes, structured judgments, and dashboard metrics. Add student-facing success criteria: feedback is understandable for the selected grade, specific to the draft, limited to manageable priorities, actionable without rewriting the work for the student, and preserves opportunities for the student to practice the target skill.

Part 1 is approximately 1,800 words. There is no explicit word limit, but the syllabus asks for concise, essential design decisions. Reduce repeated architecture justification in Sections 1.7 and 1.10 and move low-level implementation detail to Part 2 or an evidence appendix. Replace the defensive phrasing at line 104 (“inventing one would be worse”) with a neutral scope statement: production use would require institution-approved, current, localized crisis-response protocols.

## Assignment-requirement coverage

### Part 1

| Requirement | Assessment |
| --- | --- |
| 1. Users, educational need, main task | Covered clearly; consider grounding or softening generalized claims about what is “common.” |
| 2. User-provided information | Covered, including required/optional inputs and clarification answers. |
| 3. Architecture | Covered; correct the five-node description in Part 2. |
| 4. Responsibilities and boundaries | Strong coverage of both agents and system boundaries. |
| 5. Actions, tools, resources | Covered; the decision not to add retrieval or other tools is explicit. |
| 6. Clarification | Strong coverage, including non-triggers and the two-answer limit. |
| 7. Multi-agent roles and coordination | Strong, but correct the handoff wording and soften the single-agent comparison. |
| 8. Completion | Covered for all terminal outcomes; pending clarification is correctly not treated as complete. |
| 9. Stopping and human assistance | Needs the error/fallback distinction described above. |
| 10. Success and simplest appropriate design | Partially strong; align success claims with observations and add educational outcomes. |

### Part 2

| Requirement | Assessment |
| --- | --- |
| Clear role and purpose instructions | Covered with selected prompt excerpts; embed the final instruction evidence. |
| Use of user information and task context | Covered conceptually, but the clarification-history claim must be corrected. |
| Appropriate action selection | Strong design and real observations across three routes; direct response remains honestly unobserved in real runs. |
| Clarification when information is missing/ambiguous | Strong real example; show the actual questions/answers and avoid using API count as proof of checkpointing. |
| Completion, stopping, human review | Covered, subject to the failure-behavior and audience-visibility corrections. |
| Distinct roles and coordination | Strong; the saved paths and structured handoff provide useful evidence. |
| One representative educational request | Present, but strengthen it with actual normal-case output and a claim-matched figure. |
| Label and save V1 evidence | The V1 label is clear. Evidence is not submission-ready until placeholders are replaced and numerical discrepancies are resolved. |

## Rubric readiness

This is a readiness assessment, not a predicted grade.

| Rubric criterion | Current assessment based on this draft |
| --- | --- |
| Educational Need and Agent Architecture — 20% | **Strong coverage.** The main remaining work is precision: failure behavior, success criteria, and a more balanced simplest-architecture argument. |
| Functional Agent-Based Application — 20% | **Promising V1 foundation, not finally assessable.** The criterion explicitly concerns Version 2. The current V1 evidence supports meaningful routing, but application access and final V2 functionality remain to be demonstrated. |
| Agent Behavior, Coordination, and Boundaries — 20% | **Strong V1 baseline with evidence gaps.** Normal, incomplete, and boundary runs exist; the final submission still needs accurate artifacts and appropriate final-version behavior across the same cases. |
| Iterative Testing and Improvement — 20% | **Not yet demonstrated, as expected at this stage.** Three observed V1 problems are a good start, but purposeful V2 revisions, identical-case retesting, and before-and-after evidence are still required. |
| Architecture Justification, Development Evidence, and Reflection — 20% | **Partial groundwork only.** Parts 5–6 must add two important revisions, critical review of an AI/tool-generated suggestion, a human-judgment example, and a 200–300-word reflection on learning, simplicity, limitations, risks, and oversight. |

## Preparing the observed problems for Part 3

The three candidates at line 198 are appropriate, but Part 3 requires more than a list. For the required normal, incomplete/ambiguous, and boundary cases, briefly document:

1. The actual input or task.
2. The actual action or decision.
3. The actual output or interaction.
4. Coordination, handoff, duplicated work, conflicting output, or information-sharing observations.

Then evaluate educational fit, action selection, clarification, completion, stopping, and role efficiency. Select the two or three most important problems based on that review. The current artifacts already reveal useful specifics:

- The incomplete run’s second question was the generic fallback: “Is this a complete draft you want feedback on, or an outline or idea you want help developing?”
- The normal practice’s worked example directly supplied a thesis answering the student’s own exercise.
- The strong narrative received three improvement priorities despite being near-perfect.

These are credible V2 candidates; do not present improvements until V2 has actually been changed and retested on the same fixtures.

## Final-submission reminders outside this draft’s scope

For the complete assignment, combine all eight required submission items in one document: Parts 1–6, application access, and an AI Use Acknowledgment identifying the tool, purpose, and contribution. Before finalizing V2, submit a draft to JeepyTA and review its suggestions with judgment. Provide a working link or the required application/configuration files, use the required `FirstName_LastName_Assignment_4.pdf` naming pattern, and submit the JeepyTA assignment link on Canvas. A localhost URL alone is not a working instructor-accessible deployment.

## Recommended revision order

1. Correct the factual statements and the clarification-limit metrics.
2. Reconcile timing definitions across the draft, screenshots, and PRD.
3. Replace placeholders with a small set of embedded, claim-matched figures and real output excerpts.
4. Refine the success criteria and architecture justification.
5. Use the corrected V1 record to complete Part 3 before making or claiming V2 improvements.
