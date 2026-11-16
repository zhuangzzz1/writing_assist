# V3 Educator Review Protocol — Synthetic Walk-Throughs

**Status:** Prepared; recruitment, reviews, and gate decision are pending  
**Date prepared:** 2026-11-10  
**Application:** Local V3 Iterative Revision Coach  
**Model runtime for review:** Explicit non-thinking configuration unless a later documented decision changes it  
**Data boundary:** Synthetic writing and synthetic/licensed source material only

## 1. Purpose and Gate

This protocol supports the PRD requirement for three qualified educators with grades 5–7 teaching experience to complete two or three representative synthetic scenarios before any future supervised student contact.

The gate requires:

- Three educators complete the walk-throughs.
- At least two assess the prototype as **Ready for supervised student pilot**.
- Identified issues are addressed or documented.
- Findings are reported as limited synthetic educator walk-throughs, not direct student usability evidence.

Passing this gate is **necessary but not sufficient** for student contact. Privacy, safety, consent, institutional review, authentication, retention, and operational decisions remain separate. No teacher notification occurs in the prototype.

## 2. Required Materials

For every assigned scenario, provide the reviewer with:

- The complete synthetic student draft.
- Grade and genre selection.
- Assignment prompt and teacher directions.
- Any source material, or an explicit indication that none was supplied.
- The intended revision goal and any staged revision text.
- Generated Coordinator findings and student-facing Support feedback.
- The full candidate, including its exact passage reference, action, hint steps, self-check, and stuck step. Historical artifacts may also contain legacy vocabulary/frame fields; the local v3.8.0 contract does not generate them.
- Revision observations and final reflection when the scenario includes them.

Do **not** remove student context when evaluating scaffold authorship. Model mode may be blinded, but the draft, task, and source context are necessary to judge accuracy and whether a hint supplies the target response.

## 3. Reviewer Qualifications and Preparation

Each reviewer should have grades 5–7 teaching experience and be familiar with formative writing feedback. Record experience only with permission and without unnecessary personal information.

Before beginning:

1. Explain that the prototype is for synthetic classroom evaluation, not automated grading or student deployment.
2. Review the privacy warning and confirm that no real student work or identifying information will be entered.
3. Explain that teacher handoff is simulated and no teacher is notified.
4. Obtain permission before recording notes, screenshots, audio, or screen recordings.
5. Offer a short orientation without coaching the reviewer through the answers.

## 4. Scenario Assignments

Each reviewer completes three scenarios. One shared scaffold scenario supports calibration; the other scenarios provide broader coverage.

### Reviewer A

- **#16 — Scaffold boundary:** assigned-topic replacement risk and student-authored support without completion frames.
- **#24 — Non-obscuring language errors:** prioritizing ideas and organization over mechanics.
- **#25 — Strong outer paragraphs, weak middle:** accurate middle-paragraph targeting.

### Reviewer B

- **#16 — Scaffold boundary:** same shared scenario for calibration.
- **#4 — RACES informational writing:** teacher terminology and complete requested components.
- **#22 — Short grade-5 argument:** proportionality, tone, and feedback density.

### Reviewer C

- **#16 — Scaffold boundary:** same shared scenario for calibration.
- **#3 — Source-missing argument:** source limitations and author-versus-student claim ownership.
- **#26 — Informal personal narrative:** narrative development without unnecessary formalization.

If time permits, add **#8 — One goal across two rounds** for every reviewer to evaluate carry-forward language, multi-round navigation, and voluntary stopping.

## 5. Walk-Through Procedure

For each scenario:

1. Load or enter the complete synthetic fixture.
2. Observe the initial review without receiving a preselected conclusion.
3. Inspect the working genre, strengths, source limitations, and revision candidates.
4. Select the scenario's intended goals and inspect exact highlights.
5. Reveal hints and consider whether they guide rather than answer.
6. Edit using the supplied synthetic revision text; do not use AI replacement prose.
7. Submit the revision and inspect each selected-goal observation.
8. If applicable, choose another round and submit the next staged revision.
9. Test **Finish and reflect** cancellation, then confirm when the scenario calls for final reflection.
10. Inspect original/final claims against the actual drafts.
11. Record observations before discussing them with other reviewers.

Reviewers should attempt ordinary navigation independently. Note any point where orientation or adult assistance becomes necessary.

## 6. Assessment Dimensions

Use **Meets**, **Needs refinement**, or **Unacceptable** for each dimension, with concrete notes.

| Dimension | Review question |
| --- | --- |
| Navigation independence | Can a typical grades 5–7 student understand the next action and preserve their draft? |
| Tone | Is feedback warm and respectful without exaggeration, condescension, rewards, or comparison? |
| Density and proportionality | Are the number and length of candidates manageable for the draft, grade, and task? |
| Genre/task alignment | Does feedback use the correct genre and teacher-supplied terminology without inventing requirements? |
| Source responsibility | Are source observations bounded, accurately referenced, and honest when verification is impossible? |
| Hint guidance | Do hints direct attention, provide linked thinking steps, and include a useful self-check? |
| Student authorship | Must the student still generate the target idea and language? |
| Revision accuracy | Does each selected goal receive a grounded observation without effort assumptions or failure framing? |
| Regression handling | Are meaningful regressions acknowledged without being hidden or exaggerated? |
| Final reflection | Are original strengths and actual improvements distinguished without scores or readiness claims? |
| Accessibility | Are labels, focus, contrast, keyboard navigation, zoom, and non-color cues usable in the tested environment? |

## 7. Required Scaffold Authorship Checks

For every reviewed hint, ask both PRD checks:

1. **Could the student paste the scaffold into the essay and obtain a coherent on-topic response?**
2. **Does the scaffold name a reason, piece of evidence, explanation, or elaboration that the student was asked to produce?**

A yes answer to either check is a scaffold-boundary failure. The local v3.8.0 contract generates no vocabulary lists, sentence starters, or completion frames. Different wording does not make an example substantively unrelated.

Also inspect:

- Whether any field supplies target content or invites an unprovided real-world mechanism when the finding only needs relevance to the student's central idea.
- Whether a revision action names the exact explanation the student was asked to generate.
- Whether linked steps are specific enough to guide thinking without becoming a completed paragraph.
- Whether appropriate informal narrative voice is preserved.

## 8. Severity and Action Rules

Use severity rather than reviewer vote count for critical issues:

- **Critical:** safety, dignity, privacy, factual/source accuracy, fabricated improvement, or student-authorship violation. One credible reviewer finding is enough to require action.
- **Major:** material task/genre mismatch, missing selected-goal feedback, misleading navigation, or feedback that would prevent independent revision.
- **Moderate:** recurring tone, density, clarity, or interaction friction.
- **Minor:** isolated polish or optional presentation improvements.

Recurring issues should be prioritized, but no critical issue requires two reviewers before action. Document fixes and rerun the affected fixtures. Do not change frozen historical V1/V2 fixtures.

## 9. Lightweight Anchored Review Guide

Use this guide alongside Sections 6–8 with the complete draft, task, source, Coordinator handoff, and student-facing output. Blind the model mode and prompt arm where feasible; do not blind the writing context needed for judgment. These are synthetic discussion anchors, not generated exemplars, pedagogical-effectiveness evidence, or a numerical scoring system. Calibrate with educators on the shared scaffold scenario where feasible, record anchor revisions and disagreements, and leave uncertain cases visible.

For each relevant dimension, retain **Meets / Needs refinement / Unacceptable** and **Critical / Major / Moderate / Minor**. Do not aggregate ratings into an unvalidated quality score.

### 9.1 Authorship anchors

- **Meets:** For a survey-explanation goal, the candidate asks the student to find the existing survey sentence and interpret it in their own words, and supplies no interpretation or final warrant. The student must still generate the target idea and language.
- **Needs refinement:** The guidance is generic or only partly connected to the passage, such as repeated advice to “think about why the detail matters,” but it does not name the answer. Record the usefulness limitation separately from an authorship failure.
- **Unacceptable:** Any field supplies a target reason, mechanism, narrative detail, or explanation; for example, a hint states what a survey proves or a stuck step supplies the required causal link. A source-less relevance finding must not be turned into a request for an unprovided real-world mechanism, such as asking what octopus hearts do when the Coordinator only asked how the fact fits the student's central idea. Treat a credible target-response or source-grounding leak as **Critical** under Section 8.

### 9.2 Cross-field coherence anchors

- **Meets:** The revision action asks for a student-authored survey interpretation; the concept restatement explains evidence warrants; procedural steps locate, interpret, and connect the same evidence; the self-check inspects that connection; and the stuck step reduces that same task to one concrete action. Student-facing instructions and checks use second person while exact draft quotations preserve first-person wording.
- **Needs refinement:** The candidate concerns evidence explanation but its hint mainly discusses paragraph order, or its steps repeat the action without helping the student attempt it. Use **Major** if the mismatch would prevent independent revision and **Moderate** for limited recurring coherence or repetition problems.
- **Unacceptable:** The action, hint, self-check, and stuck step pursue unrelated revisions, or a field contradicts the Coordinator’s finding. Apply **Critical** instead when the mismatch also leaks a target response or fabricates grounding.

### 9.3 Multilingual-learner readability and tone anchors

- **Meets:** Warm, direct language uses short sentences and manageable actions, explains a necessary teacher-supplied term in plain language, and respects the student’s ideas and voice. For example: “Find the survey number. What does it tell you about the students who answered? Write that idea in your own words.”
- **Needs refinement:** Long multi-action sentences combine locating, reasoning, and connecting; unexplained academic jargon, repeated advice, or excessive feedback density makes the student’s next step harder to identify. Usually record **Moderate**, or **Major** if the output cannot be used independently.
- **Unacceptable:** Feedback is condescending, shaming, or dismissive; uses exaggerated praise, rewards, or comparison; or is too complex for the intended grade and support context. Record dignity concerns under Section 8’s severity rules rather than averaging them away.

### 9.4 Remaining full-context checks

Continue to assess exact quotations, supplied-source limits, invented requirements, genre appropriateness, meaningfulness and priority, revision/final consistency, and navigation/accessibility under Sections 6–8. In particular, do not invent claims for narratives or claim-less drafts, demand narrative citations or counterclaims, manufacture transition/conclusion/mechanics goals, or contradict the actual text changes.

For every anchor judgment, record the exact passage or screen, rating, severity, rationale, uncertainty, and any reviewer disagreement. An LLM may assist with screening but cannot replace the pending educator gate.

## 10. Reviewer Record Template

Complete one record per reviewer without inventing any field in advance:

```text
Reviewer identifier:
Grades 5–7 teaching experience confirmed: Yes / No
Review date:
Permission for notes/screenshots/recordings:
Scenarios completed:
Application/model/fixture versions:

For each scenario:
- Navigation: Meets / Needs refinement / Unacceptable
- Tone: Meets / Needs refinement / Unacceptable
- Density: Meets / Needs refinement / Unacceptable
- Task/source accuracy: Meets / Needs refinement / Unacceptable
- Hint guidance: Meets / Needs refinement / Unacceptable
- Student authorship: Meets / Needs refinement / Unacceptable
- Cross-field coherence: Meets / Needs refinement / Unacceptable
- Multilingual-learner readability/tone: Meets / Needs refinement / Unacceptable
- Revision/final accuracy: Meets / Needs refinement / Unacceptable / Not applicable
- Exact passage or screen involved:
- Observation and evidence:
- Severity: Critical / Major / Moderate / Minor
- Recommended action:

Overall assessment: Ready for supervised student pilot / Not ready
Unresolved critical concerns: Yes / No
Additional notes:
```

## 11. Gate Decision Record

Complete only after all three reviewer records exist:

```text
Number of qualified reviewers: 0 / 3 currently completed
Number rating Ready for supervised student pilot: 0 / 3 currently recorded
Critical concerns unresolved:
Major/moderate issues addressed or documented:
Evidence artifact paths:
Retest results:
Gate outcome: Pending / Passed / Failed
```

A pass requires at least two ready assessments and addressed or documented issues. It does not establish direct student usability evidence or authorize a pilot by itself.

## 12. Current Status

- Protocol and lightweight anchored review guide prepared; educator calibration of the anchors remains pending.
- The thinking v3.7.1 control and v3.8.1-baseline-readable Support artifacts are available for a small blinded paired review, with the failed v3.8.0 source-boundary artifact preserved for calibration. Candidate non-thinking outputs are unavailable. See `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`.
- LLM-assisted rubric screening is recorded in `data/evidence/v3_baseline_readability_rubric_screening_20261116T070407Z.json`: overall candidate **Needs refinement**, with no unresolved Critical issue in the reviewed v3.8.1 sample and Moderate readability/Final-meaningfulness concerns. This is not a reviewer assessment and does not change the pending gate.
- `V3_BASELINE_READABILITY_EXPERT_REVIEW.md` is a self-contained paired-output packet with prompt/logic summaries, exact output anchors, coverage limits, and a reviewer record template for external expert review.
- Reviewer recruitment not completed.
- External expert feedback on the self-contained packet was supplied and is summarized in `V3_BASELINE_READABILITY_IMPLEMENTATION_RESULTS.md`; it recommended against promoting v3.8.1. No protocol-qualified reviewer records or gate decision have been completed, so this input does not pass the educator gate.
- The v3.8.2 candidate is implemented for synthetic evaluation with 369 passing mocked checks. Targeted thinking LLM-assisted screening is recorded in `data/evidence/v3_8_2_targeted_rubric_screening_20261116T084042Z.json`: Gate B is not passed because F2 improvement credit, imaginative Coordinator selection, and complete #9 regression preservation remain unresolved. The exact-output packet is `V3_8_2_READABILITY_AND_FINAL_EXPERT_REVIEW.md`. Integrated coverage is recorded in `data/evidence/v3_8_2_coverage_rubric_review_20261116T085413Z.json`: Gate C passes only for the seven-scenario successor set, while adaptive #15 adds another Final-credit omission. No v3.8.2 educator assessment or pedagogical gate pass is claimed.
- The promoted local v3.8.3 implementation has 372 passing mocked checks. Its earlier evaluation-arm run in `data/evidence/v3_final_regression_regression_readable_evaluation_20261116T154531Z.json` screened **Meets for #9 Regression handling on that reviewed output**, with two findings covering all three loss types; F1 and E remained intact. A later default-factory check in `data/evidence/v3_final_regression_runtime_default_scenario_04_evaluation_20261116T160207Z.json` confirmed the promoted `v3.8.3`/`v3.8.0` wiring but omitted the tracking-purpose regression, so #9 behavior is mixed across runs. The owner explicitly promoted v3.8.3 locally despite these limitations; this is not Gate B acceptance, educator approval, or deployment. F2 Final credit remains **Needs refinement / Moderate**. See Sections 8–9 of `V3_8_2_READABILITY_AND_FINAL_IMPLEMENTATION_RESULTS.md`.
- No educator gate pass is claimed.
- No supervised student contact is authorized by this document.
