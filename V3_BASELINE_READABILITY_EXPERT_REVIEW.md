# Expert Review: Baseline v3.7.x vs Readable Candidate v3.8.1

## Review purpose

This packet summarizes a synthetic-writing experiment for an iterative revision coach intended for grades 5–7 multilingual learners. It compares:

- **Control:** Coordinator prompt `v3.7.1`, application/model handoff schema `v3.7.0`, legacy Support prompt and output fields.
- **Candidate:** combined Coordinator/Support prompt `v3.8.1-baseline-readable`, schema `v3.8.0`, selected through the evaluation-only `baseline_readable` arm.
- An earlier candidate, **v3.8.0-baseline-readable**, is included only where it supplies a useful negative example.

The candidate is not deployed and is not the normal local-server prompt. The local server uses a separate v3.8.0 structural contract without the candidate's readability/grounding wording.

The primary evaluation framework is the project's educator rubric:

- Ratings: **Meets / Needs refinement / Unacceptable**.
- Severity: **Critical / Major / Moderate / Minor**.
- Dimensions: navigation independence, tone, density/proportionality, genre/task alignment, source responsibility, hint guidance, student authorship, revision accuracy, regression handling, Final reflection, accessibility, cross-field coherence, and multilingual-learner readability/tone.

The ratings in this packet are **LLM-assisted screening, not educator findings**. Please independently rate the evidence, identify disagreements, and leave uncertainty visible. Do not convert ratings into a numerical quality score. Calls, tokens, latency, and repair counts are not treated as measures of pedagogical quality.

## 1. Experimental design and boundaries

Both arms used the same synthetic fixtures, `deepseek-flash`, thinking mode, and high reasoning-effort configuration. One thinking run was performed per arm. Non-thinking candidate behavior and a full 32-scenario candidate run were not evaluated.

| Evaluation set | Control coverage | Candidate coverage |
| --- | --- | --- |
| 14 controlled Support handoffs | All 14 | All 14 |
| 12 Coordinator-targeted scenarios | All 12 | All 12 |
| Eight integrated scenarios: #7, #9, #10, #11, #15, #20, #24, #30 | All scripted paths ran | #15 and #20 did not complete their scripted revision/Final paths; details below |
| Two controlled Final-history probes | Both | Both |

Important comparison limitations:

1. The candidate differs in **both prompt wording and output schema**. It removes generated vocabulary options, sentence starters, and the Coordinator `reasoning_operation` field. Differences cannot be attributed to readability wording alone.
2. Both arms in this experiment use the **new shared Final-history service and deterministic guards**. The control uses legacy v3.7.x prompts/output contracts but is not a reproduction of an older runtime without those guards.
3. Candidate integrated #15/#20 are unexercised paths, not evidence of good or poor output quality.
4. No learner outcomes, educator approval, independent navigation, full-keyboard behavior, or actual screen-reader accessibility are established.

## 2. Corresponding prompt and application logic

### 2.1 Coordinator: control

The v3.7.1 control asks the Coordinator to:

- Check human-review needs before ordinary assessment.
- Infer or apply genre, assess meaningful issues, and route to clarification, Support, direct response, or simulated teacher review.
- Prioritize accuracy findings, then a draft-supported student concern, then remaining severity/pedagogical priority.
- Preserve exact draft references with paragraph and occurrence metadata.
- Avoid source-accuracy claims when no source is supplied.
- Classify every issue by `finding_severity` and also by `reasoning_operation` (`causal`, `sequential`, `source_based`, `concessive`, `summary`, `conditional`, or `none`). The latter guided sentence-starter selection.
- Use `direct_response` when no meaningful actionable issue remains, without intentionally forcing criticism.

### 2.2 Coordinator: candidate additions and removal

The candidate removes `reasoning_operation`, because its only consumer was sentence-starter selection. It adds an evaluation-only section with these rules:

> Use direct_response when the draft fulfills the task with understandable language and genre-appropriate support and no meaningful actionable issue remains. Do not create optional expansion, enrichment, or polish goals solely to provide revision candidates.

It also distinguishes classroom/shared context from external source verification:

> Do not mark a class discussion, survey, or shared classroom experience inaccurate or unusable merely because the task identifies it as synthetic or because no reading file is attached.

If vague attribution genuinely impairs the argument, the candidate permits a bounded development-level elaboration issue. It does not permit an accuracy finding solely from synthetic classroom context. Fabricated evidence, real-world factual misrepresentation, and supplied-source misrepresentation remain accuracy findings.

### 2.3 Support: control

The legacy Support contract creates one candidate per Coordinator issue and preserves its ID, exact reference, paragraph, occurrence, and order. It includes:

- A title, reader-focused rationale, revision action, hint, and stuck step.
- Three to five hint items: one concept restatement followed by two to four procedural steps.
- A self-check.
- `vocabulary_options`: up to four plain strings.
- `sentence_starter`: an empty or approved abstract frame; the first candidate normally receives a nonempty frame when `reasoning_operation` is not `none`.
- A rigid **CLAIM ANCHORING** rule that requires phrases such as “why this matters” to be completed with a clause naming the draft's specific claim.
- A long instruction-clarity example that separates locating, interpreting, and connecting into commands.

### 2.4 Support: candidate v3.8.1

The candidate removes vocabulary options and sentence starters from both the prompt and output schema. It retains exact-reference, authorship, source-limitation, hint-count, and one-repair protections.

Its approximate prompt guides—not deterministic validators—are:

- Title: 3–6 plain words.
- `why_it_matters`: 1–2 short sentences, approximately 25 words total.
- `revision_action`: one focused writing move in 2–3 short sentences, approximately 15 words per sentence and one action per sentence.
- Hint steps: existing 3–5 total items, approximately 18 words per step.
- `self_check`: one short question checking the same move.
- `stuck_step`: one immediate small action, approximately 18 words.

Other changes:

- Replace rigid claim anchoring with one concrete reader question or a short link to the student's claim, central idea/topic, or key moment. If the focus is unclear, refer to existing wording rather than inventing a claim.
- Give each field a distinct job: the action states the move; hints explain concept/process; the self-check inspects that move; the stuck step reduces it to a smaller action.
- Avoid ambiguous physical directions and unrelated optional additions in the main action.
- Use second-person instructions and self-checks while preserving first-person wording inside exact quotations.

V3.8.1 adds **source-bound elaboration** after a v3.8.0 failure:

> When source material is unavailable or source_limitations says claims cannot be checked, do not ask the student to supply a real-world function, mechanism, fact, or explanation that is not already in the draft.

For a relevance finding, the candidate should ask how the existing detail fits the student's central idea or invite a source, rather than request an unverifiable factual mechanism.

### 2.5 Shared revision and Final logic

For normal revisions, the Coordinator must return exactly one observation per selected goal: `specific_improvement`, `improvement_not_yet_evident`, or `uncertain`. These describe text evidence, not effort or a score.

At Finish, both arms use this shared service logic:

1. Compare the original and latest submitted immutable snapshots with a deterministic diff.
2. Build `revision_history` from snapshots and the latest successful Coordinator review matching each snapshot.
3. Include revision/snapshot/review IDs, a SHA-256 draft hash, exact selected-goal references and locations, and the authoritative Coordinator status, observation, evidence reference, and carry-forward value. Support paraphrases do not replace Coordinator observations.
4. Send this history and the final-draft hash to the Final Coordinator.

The candidate Final prompt explicitly instructs the model to inspect prior verdicts and verify the complete draft before deletion/weakening claims. The legacy control Final prompt does not contain that instruction, although the control still receives the history payload and uses the shared guards.

Shared deterministic Final guards:

- Reject an improvement only when the latest reviewed hash matches Final, the goal ID matches, the exact goal reference is unchanged, and the prior verdict was `improvement_not_yet_evident` or `uncertain`.
- A goal ID alone, partial wording, or an empty Final goal ID does not trigger inference/rejection. A genuine improvement elsewhere remains allowed.
- Reject a deletion-worded regression when its exact original reference remains verbatim in Final.
- Preserve exact-reference membership, changed-text overlap, unchanged-draft rejection, one bounded repair, and no Final quotation normalization.

## 3. Rubric-based performance summary

### 3.1 Candidate v3.8.1

**Overall LLM-assisted screening: Needs refinement.** No unresolved Critical issue was found in the reviewed v3.8.1 sample. This is not an educator gate result.

| Dimension | Screening | Evidence summary |
| --- | --- | --- |
| Student authorship | **Meets** | Students generate claims, explanations, narrative details, and the imaginative-system destination. No target response or generated vocabulary/frame remains. |
| Source responsibility | **Meets** | The corrected octopus output asks about relevance, not a heart mechanism. Missing sources are not verified; supplied survey counts/meaning remain bounded. |
| Hint guidance | **Meets** | Exact references, 3–5 concept/procedural items, and related self-checks remain intact. |
| Cross-field coherence | **Meets** | Reviewed action, hints, self-check, and stuck step address the same move. Automated overlap flags included benign paraphrases and were not treated as failures. |
| Multilingual readability/tone | **Needs refinement / Moderate** | Tone is respectful, but some action fields still combine locating, interpreting, and connecting. Longer action/hint/stuck text offsets some shorter rationales and fewer long-action flags. |
| Density, proportionality, meaningful selection | **Meets** | Strong-draft #10 and optional-language #24 receive direct responses. Returning two meaningful goals on #15 is not a reason to invent a third. |
| Revision observation accuracy | **Meets — exercised paths only** | Exercised observations are grounded and neutral. #15/#20 revision observations were not exercised. |
| Regression handling/Final reflection | **Needs refinement / Moderate** | Exact-verdict and retained-opening contradictions are resolved, but “less explicit link” regressions may be optional criticism rather than meaningful regressions. |
| Navigation independence | **Not assessed** | Model artifacts do not establish independent student navigation or keyboard usability. |
| Accessibility | **Not assessed** | Actual screen-reader/full-keyboard checks remain open. |

### 3.2 Control and paired interpretation

No overall control rating is assigned because the review was organized around paired anchors rather than a complete independent rating of every control dimension.

The defensible comparison is **targeted semantic improvement without demonstrated general readability or overall pedagogical superiority**:

- The candidate fixes the control's synthetic-discussion strong-draft failure.
- The candidate avoids the control's initial same-goal Final contradiction; the shared guard also repairs the control.
- The candidate's v3.8.1 source-bound correction matches the control's safer octopus relevance framing. The Critical octopus regression belonged to v3.8.0, not v3.8.1.
- Both arms remain **Needs refinement / Moderate** for readability.
- The candidate introduces a debatable source-present Final regression that the control did not report. This may be unnecessary criticism rather than a genuine regression.
- No candidate decrease was found in the reviewed authorship, source-responsibility, hint-grounding, or cross-field-coherence anchors.

## 4. Exact output anchors for expert review

### Anchor A — Strong draft with explicitly synthetic classroom context

**Assignment:** “Argue for one realistic reading routine at school.” Teacher directions ask for a claim, relevant reason, and explanation.

**Complete draft:**

> Our school should add a quiet reading period because it gives students time to practice choosing and enjoying books. During a recent synthetic class discussion, several students said interruptions made sustained reading difficult. A short scheduled period would protect that focus while still allowing teachers to offer help. This routine would support reading without replacing regular instruction.

**Control output — Unacceptable / Critical in the screening:**

> The draft's key evidence refers to a 'synthetic class discussion' while treating it as real student testimony. An explicitly synthetic discussion is not a real observation, so it cannot support a real school proposal; replace it with a real example or clearly label it as hypothetical and explain why it still matters.

The control routes to Support with an accuracy issue.

**Candidate output — Meets in the screening:**

- Route: `direct_response`; issues: none.
- Strength: “The draft uses the class discussion as relevant context and explains how a scheduled period would protect focus while still allowing teacher help.”
- Rationale: “The draft fulfills the assignment by stating a claim, giving a relevant reason, and explaining it in understandable language. No meaningful actionable issue remains for a support cycle.”

**Expert question:** Is the candidate's affirmation calibrated, or is there a meaningful actionable issue that both the screening and candidate missed?

### Anchor B — Survey explanation, readability, and removed scaffolds

**Draft:**

> Our school should start a garden.
>
> In the class survey, 62% of students said they would try garden vegetables. This supports our plan.

**Supplied synthetic source:** A survey of 50 students found that 31 would try vegetables. It measured interest, not health outcomes. The draft and source percentages differ. This controlled handoff's Coordinator finding targets explanation of the draft's existing wording; do not use this anchor alone to assess source-correction behavior.

**Control revision action:**

> Find the sentence with 62%. After it, write one or two sentences. First, say what the 62% result shows about students in your own words instead of repeating the number. Then, explain why that result supports your claim that our school should start a garden.

The control also generates four meaning notes (`interpret`, `connection`, `evidence`, `claim`) and the abstract starter `This evidence matters because ____.`

**Candidate revision action:**

> After the survey sentence, add one or two sentences in your own words. Say what you think the 62% shows about students and why that matters for the garden plan. Tie that thinking to your claim that the school should start a garden.

The candidate generates no vocabulary list or sentence starter. Its hint tells the student to check that the source measured interest, not health outcomes. Its self-check is:

> Does your added explanation tell readers what the 62% shows and how it connects to your garden claim, without only repeating the number?

**Screening:** Both arms remain **Needs refinement / Moderate** for readability. The candidate removes scaffold density but still combines interpretation and connection in one action field. Neither supplies the target interpretation.

**Expert questions:** Which action is more usable for a grades 5–7 multilingual learner? Does removing the vocabulary/frame reduce cognitive load or useful support? Does either field supply too much of the answer?

### Anchor C — Source-less octopus relevance

**Coordinator finding:** The three-hearts fact needs relevance/connection to the central idea; it does not request a biological mechanism. No source is supplied, and the handoff explicitly says factual claims cannot be checked.

**Control revision action — Meets:**

> Find the sentence about three hearts. After it, write one sentence. Tell readers why the three-hearts fact belongs with your point that octopuses are weird.

**First candidate v3.8.0 — Unacceptable / Critical:**

> Put your finger on your three-hearts sentence in paragraph one. Add one sentence right after it that tells the reader what those hearts do for the octopus. Say it in your own words.

This asked for an unprovided real-world mechanism despite the source limitation.

**Corrected candidate v3.8.1 — Meets:**

> Reread the sentence about the three hearts. Then add your own explanation of how that fact connects to your main idea about octopuses.

Its stuck step asks why the student chose the fact rather than asking what the hearts do.

**Expert question:** Does v3.8.1 fully restore the source boundary while preserving a useful elaboration task?

### Anchor D — Imaginative system: meaningful output gap or extra issue?

**Draft excerpts:** A turning wheel lifts out leaves and wrappers. Water moves through a filter into a storage tank. Clean water later flows to a small garden tank; students use the stored water for class plants. The draft does not say where the lifted litter goes next.

**Control:** Reports one reasoning issue about the storage-tank/garden-tank sequence and sensor-controlled gate. It does not create a litter-output goal.

**Candidate:** Reports a tank-order development issue and a second development issue for the missing litter-output step. Its student-facing litter action is:

> Find the turning wheel sentence in paragraph 3. Add one short step right after it that tells where the lifted leaves and wrappers go.

Its stuck step is:

> Say aloud one place the lifted wrappers could go in your system, then write only that step.

The candidate does not supply a destination or mechanism; the student invents it.

**Expert questions:** Is the additional litter-output goal meaningful and proportionate, or optional expansion? Does the guidance preserve authorship without being too vague?

### Anchor E — Final consistency for an unchanged reviewed goal

**Original:**

> Our class should have a reading corner. It would give students a place to read.
>
> Right now, readers have to sit at their desks.

**Latest reviewed and Final draft:**

> Our class should have a reading corner. It would give students a quiet place to read.
>
> Right now, readers have to sit at their desks.

**Authoritative prior Coordinator observation for goal 1:** `improvement_not_yet_evident`; adding “quiet” did not explain how the corner would help students focus. The exact goal reference is “It would give students a quiet place to read.”

**Control's initial Final response — Unacceptable / Critical:**

> The revision adds the adjective "quiet," making the proposed reading corner's benefit more specific than the original general "place to read."

This linked the improvement to goal 1 and the exact unchanged goal text, contradicting the latest verdict. The shared deterministic guard rejected it; the repaired control output has no improvements.

**Candidate's initial Final response — Meets:** no improvements and no regressions.

Both final reflections acknowledge the student's word-choice effort without listing a validated improvement. The candidate conclusion begins:

> You kept working with your argument draft and made a small word choice, going back to your sentence to try adding a describing word.

**Expert questions:** Is the no-improvement classification correctly calibrated? Do the reflections appropriately recognize effort without implying that the selected goal improved?

### Anchor F — Final regression restraint

#### F1. Source-present survey revision

The final replaces “This supports our plan.” with “This result shows interest among those surveyed rather than proving health benefits.”

- Both arms report source-accuracy and bounded-interpretation improvements.
- The control reports no regression.
- The candidate additionally reports:

> The final no longer explicitly states how the survey result supports the proposal; it replaces the direct support link with a limitation, leaving the argumentative connection implicit.

This is text-accurate but may be optional criticism, so it is screened **Needs refinement / Moderate** for meaningfulness.

#### F2. Source-missing later-start revision

The opening “Our school should start later.” remains in both original and Final. The final replaces “This supports our plan.” with the student's own interpretation that better concentration could help participation in class discussions.

Neither arm claims that the retained opening disappeared. The candidate reports no improvements and one regression:

> The final replaces the original direct statement that the evidence supports the plan with an interpretation that does not explicitly tie concentration to starting school later, making the support connection less explicit.

**Expert questions:** Are these meaningful regressions that help revision, or should the system affirm the more bounded/authorship-aware wording without adding a deficit? Is the candidate consistent when it reports both improvements and a regression for related text in F1?

## 5. Validation events and coverage—not quality scores

Validation events are included only to clarify what evidence reached review:

- The v3.8.1 candidate had **one successful bounded repair**: integrated #15's Support response was incomplete JSON, ending mid-string. The repaired response was valid and returned two candidates.
- No other v3.8.1 model-response repairs occurred in the reviewed Support, Coordinator-targeted, integrated, or controlled Final sets.
- The candidate had two deterministic paragraph-location normalizations in the imaginative-system scenario; exact references were preserved and these were not model repairs.
- The control's initial same-goal Final contradiction required a successful deterministic-guard repair.
- The control's integrated set also had invalid JSON on #7 and an unapproved legacy sentence starter on #11. These events do not determine rubric ratings.

### Why candidate #15/#20 did not complete their integrated paths

- **#15:** The frozen script requires three goals to test two deferred goals and one attempted goal. The repaired candidate response returned two meaningful candidates. The script cannot select three, so no revision snapshot or Final comparison was created.
- **#20:** The frozen script expects to select the first candidate and submit a prepared revision. The candidate returned `direct_response` with no candidate, so that revision could not start and no Final comparison was created.
- No route or candidate count was forced. These are **coverage gaps and fixture assumptions**, not proof that the model judgments were correct or incorrect. The controlled Final probe supplies targeted Final-history evidence but does not replace the unexercised integrated workflows.

## 6. Requested expert assessment

Please use the rubric independently on the anchors above and, where useful, on the complete artifacts listed below.

For each relevant dimension, record:

- **Rating:** Meets / Needs refinement / Unacceptable.
- **Severity:** Critical / Major / Moderate / Minor.
- Exact draft/output passage involved.
- Rationale and uncertainty.
- Whether the candidate is better, worse, mixed, or equivalent to the control for that anchor.
- Any disagreement with this packet's LLM-assisted screening.

Please specifically address:

1. Whether the candidate's shorter/removed scaffolds improve usability without reducing useful support.
2. Whether any action, hint, self-check, or stuck step supplies the student's target answer.
3. Whether the strong-draft affirmation and imaginative-system goals are meaningful and proportionate.
4. Whether the Final regressions are meaningful or unnecessary criticism.
5. Whether the candidate is calibratable for grades 5–7 multilingual learners, and what wording changes are needed.
6. Whether the missing #15/#20 coverage or mixed readability prevents any candidate promotion recommendation.

### Reviewer record template

```text
Reviewer role/experience:
Review date:
Anchor or scenario:
Arm reviewed: Control / Candidate / Paired
Exact passage:
Dimension:
Rating: Meets / Needs refinement / Unacceptable
Severity: Critical / Major / Moderate / Minor
Rationale:
Uncertainty or disagreement with screening:
Recommended change:
Candidate comparison: Better / Worse / Mixed / Equivalent / Cannot judge
```

## 7. Audit artifacts

The essential evidence is included above. For complete raw outputs and execution records, the source artifacts are:

- Control Support: `data/evidence/v3_support_prompt_evaluation_20261116T045506Z.json`
- First candidate v3.8.0 Support: `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T045953Z.json`
- Candidate v3.8.1 Support: `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T050701Z.json`
- Control Coordinator: `data/evidence/v3_coordinator_targeted_evaluation_20261116T051145Z.json`
- Candidate Coordinator: `data/evidence/v3_coordinator_targeted_baseline_readable_evaluation_20261116T051659Z.json`
- Control integrated: `data/evidence/v3_acceptance_scenarios_07_09_10_11_15_20_24_30_evaluation_20261116T052138Z.json`
- Candidate integrated: `data/evidence/v3_acceptance_baseline_readable_scenarios_07_09_10_11_15_20_24_30_evaluation_20261116T052528Z.json`
- Control Final probes: `data/evidence/v3_final_history_evaluation_20261116T065550Z.json`
- Candidate Final probes: `data/evidence/v3_final_history_baseline_readable_evaluation_20261116T065550Z.json`
- Rubric screening with scenario IDs and evidence: `data/evidence/v3_baseline_readability_rubric_screening_20261116T070407Z.json`

No deployment, candidate promotion, educator pass, accessibility pass, or learner-outcome claim is made by this packet.
