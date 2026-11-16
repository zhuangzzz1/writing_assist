# Expert Review: Structural v3.8.0, Readable v3.8.1, and Readable v3.8.2

## Review purpose

This packet supports independent expert review of a synthetic-writing experiment for an iterative revision coach intended for grades 5–7 multilingual learners. It preserves the expert's prior recommendation not to promote v3.8.1 and asks whether v3.8.2 addresses the two targeted weaknesses: Final regression restraint/credit and multilingual readability.

No candidate is deployed or promoted. The normal local runtime remains prompt/schema v3.8.0/v3.8.0 with thinking. All writing and sources are synthetic.

### Arms

- **Structural control:** unchanged local v3.8.0 Coordinator/Support prompts, schema v3.8.0, selected only for evaluation through `structural_current`.
- **Preserved readability candidate:** `v3.8.1-baseline-readable`, schema v3.8.0, selected through `baseline_readable`.
- **Successor candidate:** `v3.8.2-baseline-readable`, schema v3.8.0, selected through `baseline_readable_v2`.
- **Historical control:** v3.7.1/v3.7.0 artifacts remain useful for historical anchors but combine wording with legacy vocabulary/sentence-starter fields. They are not the clean wording control.

The three current arms used the same synthetic fixtures, `deepseek-flash`, thinking mode, and high reasoning effort. The targeted scope was 14 controlled Support handoffs, four controlled-history Final contrasts, and Coordinator-targeted strong-draft/imaginative scenarios #11/#12 per arm. One run per arm does not establish stable behavior. Non-thinking and full 32-scenario behavior are outside this packet unless separately reported.

## Primary evaluation framework

Use `EDUCATOR_REVIEW_PROTOCOL.md` Sections 6–9:

- Ratings: **Meets / Needs refinement / Unacceptable**.
- Severity: **Critical / Major / Moderate / Minor**.
- Review full draft, task, source, Coordinator findings, candidate actions, hints, self-checks, stuck steps, revision observations, and Final reflection as applicable.
- Assess navigation and accessibility separately; model artifacts cannot establish them.

Calls, tokens, latency, repairs, sentence-length counts, and overlap flags are secondary diagnostics. They do not determine pedagogical quality. Any LLM-assisted ratings in this packet are screening, not educator findings. Record disagreements and uncertainty rather than averaging them into a score.

## 1. Corresponding prompt and application logic

### 1.1 Shared architecture

Both existing agents remain unchanged in number and responsibility:

```text
Round: Coordinator diagnosis -> Support delivery -> deterministic validation
Final: Coordinator original/Final assessment -> Support reflection -> deterministic validation
```

Support's v3.8.2 delivery review occurs inside its existing prompt and single response. There is no readability agent, post-processing model call, review-output field, or hidden-reasoning collection.

All three arms use schema v3.8.0 with no generated vocabulary options, sentence starters, or Coordinator `reasoning_operation` field. This makes structural v3.8.0 versus v3.8.2 the clearest wording-focused comparison. The v3.7.x comparison cannot isolate wording from scaffold removal.

### 1.2 Coordinator round logic

Structural v3.8.0 contains the shared genre, source, human-review, meaningful-issue, exact-reference, severity, and routing rules. V3.8.1 adds and v3.8.2 preserves:

- Use `direct_response` when the task is fulfilled with understandable language and genre-appropriate support and no meaningful actionable issue remains.
- Do not manufacture optional expansion or polish goals.
- Treat class discussions, surveys, and shared classroom experiences as task context rather than inaccurate merely because they are synthetic or lack an attached reading file.
- Preserve genuine accuracy findings and source limitations.

### 1.3 Support delivery logic

Structural v3.8.0 and v3.8.1 preserve one candidate per Coordinator issue, exact IDs/references/locations/order, 3–5 hint items, related self-check, stuck step, authorship boundaries, and source limitations.

V3.8.1 adds approximate length budgets, plain-language grounding, distinct field responsibilities, second-person student instructions, physical clarity, and source-bound elaboration. The source-bound rule prevents a relevance finding from becoming a request for an unprovided real-world mechanism.

V3.8.2 retains those rules and adds an internal final-JSON review:

- One manageable cognitive move per sentence.
- If interpretation and connection are both necessary, use separate short sentences explicitly sequenced with words such as First and Then.
- Avoid figurative/idiomatic instructions such as “tie that thinking” and “bridge the gap.”
- Prefer concrete actions such as “Tell readers why” and “Show how” over “add your own explanation of how.”
- Remove repetition that adds no guidance.
- Preserve the Coordinator finding and exact references.
- Make the next action usable without first decoding writing terminology.
- Use hints for process support, keep the self-check on the same move, and keep the stuck step to one smaller immediate action, including oral rehearsal when useful.

The prompt gives structural examples rather than mandatory student-facing text:

> First, say what the survey result shows about students. Then, explain how that supports your garden claim.

> Tell readers why the three-hearts fact belongs with your point about octopuses.

These examples must not supply the student's interpretation, a target mechanism, or replacement prose. There is no keyword-only idiom ban, hard sentence-length validator, or numerical readability score.

### 1.4 Final history and deterministic guards

At Finish, the service compares original and latest submitted immutable snapshots. It builds `revision_history` from snapshots and authoritative Coordinator reviews, including exact goal references, statuses, observations, evidence references, carry-forward values, snapshot/review IDs, and SHA-256 draft hashes. Support paraphrases do not replace Coordinator observations.

Shared guards reject only unambiguous contradictions:

- An improvement linked to the same goal ID and exact unchanged goal reference after latest `improvement_not_yet_evident` or `uncertain`, with matching latest-reviewed/Final hashes.
- A deletion-worded regression whose exact original reference remains verbatim in Final.

Empty goal IDs, partial wording, different text, and semantic weakening are not deterministically inferred. Exact-reference membership, actual-change overlap, unchanged-draft rejection, one bounded repair, and no Final-reference normalization remain intact.

### 1.5 V3.8.2 Final prompt additions

The structural and v3.8.1 Final prompts already require text-grounded improvements and meaningful regressions. V3.8.2 adds:

> Evaluate what the revision gains as well as what it leaves incomplete. Replacing vague boilerplate such as “This supports our plan” with a specific interpretation, causal explanation, or source-bounded qualification can be a genuine improvement even when the explicit link back to the main claim still needs work.

It further states:

- A prior negative/uncertain verdict applies to its exact reviewed goal and text and does not prevent recognition of a different genuine improvement elsewhere.
- Loss of vague/formulaic wording is not a regression when the replacement adds specific, accurate, student-authored reasoning or a justified limitation.
- If no meaning, accuracy, necessary reasoning, or key structure was lost, an incomplete main-claim connection belongs in `future_areas`, not `regressions`.
- A genuine regression must identify actual textual harm or loss.
- Preserve genuine order/reasoning/structure losses.
- Improvement and regression may coexist only for distinct meaningful effects with exact text; do not manufacture a balanced trade-off.

These are model guidelines reviewed through outputs, not automatic semantic removal of regressions.

## 2. Targeted anchors and expected interpretations

- **Anchor A:** Strong draft with an explicitly synthetic class discussion should not receive a manufactured accuracy issue.
- **Anchor B:** Survey interpretation/connection should be concrete, short, authorship-preserving, and manageable for multilingual learners.
- **Anchor C:** Source-less octopus relevance must not request an unsupported biological mechanism.
- **Anchor D:** The imaginative litter-output goal is a meaningful process gap when identified; guidance must let the student invent the destination. A direct_response omission requires review rather than a forced goal.
- **Anchor E:** Exact unchanged goal text after `improvement_not_yet_evident` must not become a Final improvement.
- **Anchor F1:** Bounded survey interpretation deserves credit; loss of “This supports our plan.” alone is not a regression.
- **Anchor F2:** Added concentration/class-participation interpretation deserves credit even if the later-start causal path or claim link remains incomplete. The remaining step may be a future area.
- **Anchor #9:** Genuine sequence, audit-to-choice, and tracking-rationale regressions must remain visible.
- **Coverage:** Versioned #15/#20 successors must record actual model routes/counts and use controlled prefixes for independent three-goal and reviewed-revision coverage.

## 3. Actual outputs and rubric screening

### 3.1 Support artifacts and operational boundaries

- Structural: `data/evidence/v3_support_prompt_structural_current_evaluation_20261116T082209Z.json`
- V3.8.1: `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T082814Z.json`
- V3.8.2: `data/evidence/v3_support_prompt_baseline_readable_v2_evaluation_20261116T083313Z.json`

Each completed all 14 controlled handoffs without scenario errors. Structural and v3.8.2 had no schema repairs; v3.8.1 had one bounded repair after an instructional ellipsis in a source-locating hint. These facts do not determine rubric ratings. All v3.8.2 exact references, source limitations, finding IDs/statuses, and scaffold counts validated. Manual review found no target-response leak in the 20 v3.8.2 candidates.

### 3.2 Anchor B — Survey readability and authorship

Grade 6 argument. Teacher directions: “Explain what the survey shows and how it connects to the claim.” Student concern: “I need help explaining the number without repeating it.”

Complete draft:

> Our school should start a garden.
>
> In the class survey, 62% of students said they would try garden vegetables. This supports our plan.

Supplied synthetic source: 31 of 50 students would try vegetables; the survey measured interest, not health outcomes. The controlled finding asks for the student's interpretation and connection, not source correction or a target interpretation.

**Structural action:**

> Find the sentence with 62%. Leave the number there. After it, write one or two sentences. First, explain in your own words what the 62% result shows about students. Then explain why that is a reason to start a garden.

**V3.8.1 action:**

> Add one sentence after the survey result that explains what the 62% means to you. In that sentence, link your interpretation to your claim about starting a garden.

**V3.8.2 action:**

> After the sentence "This supports our plan," explain what the 62% shows about students. Then connect that meaning to your garden claim.

V3.8.2 hint steps:

> A survey number is evidence, but readers still need your explanation of what it shows.
>
> Put your finger on the sentence with "62%" in your draft.
>
> Say aloud what that result tells you about students in this class survey.
>
> Write one sentence that connects that meaning to your garden plan.

V3.8.2 self-check and stuck step:

> Does your new sentence tell readers why the 62% result matters to your garden claim?
>
> Say aloud what the survey result shows about students, then write that one idea as a sentence.

**LLM-assisted screening:** Structural **Needs refinement / Moderate** because five main-action sentences create density despite useful sequencing. V3.8.1 **Needs refinement / Moderate** because it combines interpretation and connection in one embedded instruction. V3.8.2 **Meets** for this anchor: two short sequenced sentences, concrete existing wording, and no target interpretation. All three preserve authorship. Reviewers may disagree about whether “connect that meaning” remains too abstract; the exact text is supplied for that judgment.

### 3.3 Anchor C — Source-less octopus relevance

Grade 6 informational draft opening:

> Octopuses are one of the weirdest animals in the ocean. They do not have any bones in their body so they can squeeze into tiny spaces like jars or cracks in rocks. This helps them hide from sharks and eels that want to eat them. They also have three hearts which is pretty crazy to think about.

No source is supplied. The controlled limitation says factual claims cannot be checked and invites a source if checking is needed. The Coordinator finding is development-level relevance: the three-hearts fact is stated without explaining its connection to the central idea. It does not request a heart mechanism.

**Structural action:**

> Find the sentence about three hearts. After it, add one sentence in your own words. Tell the reader how that fact connects to your opening idea that octopuses are unusual.

**V3.8.1 action:**

> Reread your sentence about the three hearts. Decide what you want that fact to show about your point that octopuses are unusual. Add or adjust a few words so the link is clear.

**V3.8.2 action:**

> Find your sentence about the three hearts. Then add one sentence telling readers why you included that fact with your octopus point.

V3.8.2 stuck step:

> Say aloud one reason you chose to include the three-hearts fact, then write that reason as a sentence.

**LLM-assisted screening:** All three are **Meets** for source responsibility and authorship; none requests an unsupported mechanism or supplies the relevance answer. Structural/v3.8.1 remain **Needs refinement / Moderate** for the targeted wording comparison because “how that fact connects” and “what you want that fact to show” are more abstract. V3.8.2 is **Meets** for concrete action wording. Its last procedural hint is 28 words and combines deciding/writing; record any residual readability concern rather than hiding it.

### 3.4 Anchor D — Imaginative-system delivery

Grade 5 complete draft:

> My Air Cleaner
>
> My imagined machine cleans classroom air. A fan pulls air through a reusable filter. The filter catches dirt and tiny pieces of plastic. Then the clean air goes back into the room.

Assignment: explain an imaginative machine that could help a classroom; no scientific source is required. The controlled finding asks what happens to the caught material.

**V3.8.2 action:**

> Find the sentence about the filter catching dirt and plastic. Add one sentence telling readers what your imagined machine does with that trapped material next.

**V3.8.2 stuck step:**

> Say aloud one thing your machine does with the trapped dirt and plastic, then write only that step.

Structural and v3.8.1 controlled Support outputs also preserve student authorship and give concrete next-step guidance. All three are **Meets** for this controlled delivery anchor. This does not establish that the Coordinator will identify the gap; the integrated Coordinator outputs are reviewed separately.

### 3.5 Support-level screening conclusion

For the 14 handoffs, v3.8.2 is screened **Meets** for student authorship, source responsibility, hint guidance, and cross-field coherence. Its targeted action readability is **Meets** for Anchors B/C/D, with residual Minor concerns about some longer hint sentences and terms such as “sensory detail.” These are synthetic-output screening judgments, not educator approval or target-age EL usability evidence. The candidate's overall Gate B rating is assessed with the Final and Coordinator outputs below.

### 3.6 Final artifacts

- Structural: `data/evidence/v3_final_regression_structural_current_evaluation_20261116T082548Z.json`
- V3.8.1: `data/evidence/v3_final_regression_baseline_readable_evaluation_20261116T083136Z.json`
- V3.8.2: `data/evidence/v3_final_regression_baseline_readable_v2_evaluation_20261116T083714Z.json`

Each arm completed all four controlled-history Final scenarios without errors or schema repairs. The shared history and guards were active in every arm.

### 3.7 Anchor F1 — Source-present bounded interpretation

Original:

> Our school should start a garden.
>
> The survey says 50 students want vegetables. This supports our plan.

Final and latest reviewed revision:

> Our school should start a garden.
>
> The supplied survey included 50 students, and 31 said they would try garden vegetables. This result shows interest among those surveyed rather than proving health benefits.

Source: a synthetic class survey included 50 students; 31 would try garden vegetables; it measured interest, not health outcomes. The prior reviewed goal was already `specific_improvement`.

**Structural:** credits the corrected count and bounded interpretation; no regression; future areas include reconnecting the interest finding to the garden proposal. **Meets.**

**V3.8.1:** credits source precision but also regresses:

> The final removes the explicit sentence tying the survey result back to the garden proposal, so the evidence-to-recommendation connection is left implicit rather than stated.

This is the prior regression-restraint concern. **Needs refinement / Moderate.**

**V3.8.2 improvements:**

> Corrects the survey claim so the final draft reports that 50 students were included and 31 said they would try garden vegetables, rather than saying all 50 wanted vegetables.

> Replaces vague support language with a source-bounded qualification that distinguishes measured interest from unmeasured health benefits.

It reports no regression and gives this future area:

> Connect the survey result back to the main claim by explaining why interest among surveyed students is a reason to start the garden.

**V3.8.2 screening: Meets.** It credits the genuine gain and separates the optional next step from regression.

### 3.8 Anchor F2 — Student interpretation without source verification

Original:

> Our school should start later.
>
> The passage says students concentrate better. This supports our plan.

Final and latest reviewed revision:

> Our school should start later.
>
> The passage says students concentrate better. I think better concentration could help students participate in class discussions, which is my own interpretation of the evidence.

No passage is supplied. The prior goal observation is `improvement_not_yet_evident` because the causal path from later start to concentration remains incomplete; its evidence reference is the new interpretation. The original selected-goal reference was the two old sentences ending in “This supports our plan.”

**All three arms report zero improvements and zero regressions.** Structural and v3.8.1 therefore fail to validate the added reasoning; v3.8.2 removes the earlier regression pattern but still does not satisfy the credit requirement.

**V3.8.2 Coordinator rationale:**

> The final submitted draft matches the reviewed revision. The selected goal_1 remains improvement_not_yet_evident, so the added classroom-benefit interpretation is not reported as a specific improvement here. The revision keeps the original position and evidence reference, and the replacement does not create a meaningful regression. Remaining needs are a clearer causal explanation and an explicit link back to the main claim.

**V3.8.2 Final Support conclusion:**

> You put real effort into revising this draft, and it shows in the way you slowed down to add your own thinking instead of leaving the evidence to speak for itself. Labeling your reasoning as your interpretation was a thoughtful, honest choice. Keep building on that habit by spelling out the steps between a later start time and better concentration, and by connecting class discussion back to your main claim. Your willingness to revisit and rework your argument is the kind of effort that moves writing forward.

**Screening: Needs refinement / Moderate for all three.** V3.8.2 still extends the prior negative goal verdict to changed text and withholds validated improvement credit, contrary to the new prompt. The warm conclusion does not repair the Coordinator finding. The prior external expert rated the earlier zero-improvement-plus-regression pattern potentially Major; reviewers should independently calibrate this no-regression/zero-improvement version.

### 3.9 Anchor E — Same unchanged reviewed goal

Original reading-corner sentence: “It would give students a place to read.” Latest/Final sentence: “It would give students a quiet place to read.” The authoritative prior verdict is `improvement_not_yet_evident` for that exact current sentence because “quiet” does not explain the reading benefit.

All three arms report no improvements or regressions and preserve the remaining explanation as a future area. **Meets for all three.** This verifies the intended guard consistency in these outputs, not semantic calibration of every possible changed reference.

### 3.10 Anchor #9 — Genuine organization/reasoning regression

Original:

> Our cafeteria can reduce food waste by helping students understand what they throw away. First, a waste audit can show which foods are discarded most often. Next, students can use that information to choose smaller portions. Finally, the cafeteria can track whether waste changes after those choices.

Final/latest reviewed revision:

> Our cafeteria can reduce food waste by helping students understand what they throw away. Finally, students can choose smaller portions. First, a waste audit can show which foods are discarded most often, but the audit is not needed before making choices. Next, the cafeteria can track whether waste changes, although no one will know what caused the change.

Structural and v3.8.1 each report three regressions: reversed sequence markers, removed audit-to-choice rationale, and undercut tracking purpose. **Meets.**

V3.8.2 retains two regressions:

> The step order is no longer logical: “Finally” introduces the portion-choice step before “First” introduces the audit, disrupting the original First/Next/Finally progression.

> The revision removes the original link between audit findings and portion choices and instead states that the audit is not needed before making choices, weakening the explanation of how the plan would reduce waste.

It also adds this improvement:

> Adds a specific causal caveat that tracking waste changes would not by itself establish what caused the change.

It does not report the fixture's separate tracking-purpose regression. **Needs refinement / Moderate** under the planned expectation. Expert question: is the causal caution a distinct genuine gain that may coexist with the two retained regressions, or does treating it only as an improvement hide a meaningful loss in the process rationale? Do not average away this disagreement.

### 3.11 Coordinator Anchors A and D

Coordinator artifacts:

- Structural: `data/evidence/v3_coordinator_targeted_structural_current_scenarios_11_12_evaluation_20261116T082707Z.json`
- V3.8.1: `data/evidence/v3_coordinator_targeted_baseline_readable_scenarios_11_12_evaluation_20261116T083258Z.json`
- V3.8.2: `data/evidence/v3_coordinator_targeted_baseline_readable_v2_scenarios_11_12_evaluation_20261116T083841Z.json`

**Anchor A:** The complete strong draft is:

> Our school should add a quiet reading period because it gives students time to practice choosing and enjoying books. During a recent synthetic class discussion, several students said interruptions made sustained reading difficult. A short scheduled period would protect that focus while still allowing teachers to offer help. This routine would support reading without replacing regular instruction.

The assignment asks for a realistic reading routine with a claim, relevant reason, and explanation. Structural manufactures an accuracy issue about synthetic testimony and asks for a real observation or hypothetical framing: **Unacceptable / Critical**. V3.8.1/v3.8.2 use direct_response with no issues: **Meets**.

**Anchor D:** The imaginative rainwater draft names a turning wheel that lifts leaves/wrappers but does not say where they go. Structural identifies a storage/garden-tank connection but not the litter-output gap: **Needs refinement / Moderate**. Fresh v3.8.1 and v3.8.2 runs both return direct_response and say no meaningful issue remains: **Needs refinement / Moderate** under the planned meaningful-selection anchor. The earlier v3.8.1 litter-output improvement was not reproduced. Controlled Support outputs in Section 3.4 show successful delivery only, not successful Coordinator identification.

### 3.12 Targeted Gate B conclusion

**Gate B is not passed. Do not promote v3.8.2 from these results.** It improves Support Anchor B/C delivery, F1, strong-draft calibration, and E consistency. F2 still lacks genuine improvement credit, imaginative Coordinator selection misses the target gap in this run, and #9 does not preserve every expected regression. Screening rates these residual concerns Moderate; no Critical/Major issue was assigned by the LLM screening, but the explicit behavioral requirements remain unmet and educators may calibrate severity differently.

Full dimension ratings, exact scenario IDs, and evidence statements are in `data/evidence/v3_8_2_targeted_rubric_screening_20261116T084042Z.json`. This is not an educator gate result.

## 4. Integrated coverage

The versioned fixture is `test_cases/v3/readability_coverage.json`, `v3.8.2-readability-coverage.1`. Runs began only after the targeted rubric review above; they are intended to close coverage gaps, not override Gate B.

### Structural v3.8.0 completed coverage

Artifact: `data/evidence/v3_readability_coverage_structural_current_evaluation_20261116T084144Z.json`

All seven scenarios completed without scenario errors:

- Adaptive #15 produced one candidate, selected that actual goal, completed revision/Final, and recorded one attempted self-report. It did not claim two deferrals.
- Controlled #15 supplied three candidates without an initial model call, then recorded one attempted and two deferred goals, three authoritative revision observations, and Final history.
- Generated #20 produced one candidate and completed staged revision/Final with authoritative history.
- Controlled reviewed-revision #20 completed Final with the supplied authoritative observation.
- Optional-language #24 returned direct_response with no issues.
- Clarification #30 asked a second question, then resolved to Support after the second unclear answer. It did not reach `clarification_limit`; that is a valid model-driven alternate path because the Coordinator no longer requested clarification. The deterministic boundary itself remains covered by mocked tests and prior controlled probes, not by this structural output.
- Human review returned concerning_content, empty ordinary assessment, and no revision/Final path.

One controlled-#15 Support response ended in incomplete JSON and repaired successfully. This is a secondary diagnostic. Structural revision observations on these paths were text-grounded and included neutral carry-forward for deferred goals; this limited path review does not change its targeted Anchor A/D/F2 failures.

### V3.8.1 and v3.8.2 completed coverage

Artifacts:

- `data/evidence/v3_readability_coverage_baseline_readable_evaluation_20261116T084532Z.json`
- `data/evidence/v3_readability_coverage_baseline_readable_v2_evaluation_20261116T084915Z.json`
- Rubric/path review: `data/evidence/v3_8_2_coverage_rubric_review_20261116T085413Z.json`

Both arms completed all seven scenarios without scenario errors or location normalizations. Adaptive #15 produced two candidates and recorded one attempted/one deferred goal. Controlled #15 independently exercised three goals with two deferrals and authoritative Final history. Generated #20 returned direct_response in both readability arms and completed the recorded no-revision Finish path; controlled reviewed-revision #20 separately completed Final and credited the exact added focus benefit. Structural #20 exercised the staged-revision alternative.

All arms returned direct_response without optional mechanics goals on #24 and preserved simulated concerning-content human review without revision/Final. All clarification runs asked twice and then selected Support after the second unclear answer; none exercised real-model `clarification_limit` because the Coordinator no longer requested clarification. That deterministic boundary remains covered by mocked/prior controlled probes. No candidate count or route was forced.

V3.8.1 had one bounded repair after clarification #30 returned Support with an empty working genre. V3.8.2 had one bounded repair after adaptive #15 revision returned valid JSON followed by ` clarify: undefined`. These are secondary diagnostics.

### New integrated Anchor G — Adaptive #15 Final credit

Original:

> Our school should allow a community garden. Last month, a survey took place. Students were asked if they wanted a garden. Many students said yes. Students could water plants and pull weeds after school. The garden would help them. It would make our school better for everyone who goes here.

Final/latest reviewed revision:

> Our school should allow a community garden because it would teach students to care for living things. Last month, a survey took place. Students were asked if they wanted a garden. Many students said yes. Students could water plants and pull weeds after school. The garden would help them. It would make our school better for everyone who goes here.

V3.8.2 selected goal_1 reference was:

> The garden would help them. It would make our school better for everyone who goes here.

The latest revision observation correctly kept goal_1 at `improvement_not_yet_evident` for the unresolved garden-benefit connection while explicitly noting the separate new opening reason. Structural and v3.8.1 Final both credit that exact opening improvement.

V3.8.2 Final reports zero improvements and zero regressions. Its rationale says:

> The final submitted draft matches the latest reviewed revision. Its only change is the added reason in the position sentence, which is part of the reviewed goal text marked improvement_not_yet_evident; because the final draft is unchanged from that review, it is not reclassified as a specific improvement here. No meaningful regression is present, and the remaining connections fit future areas.

**Screening: Needs refinement / Moderate.** The added opening reason is different text from the exact selected goal reference. The model over-applies the prior negative verdict, repeating F2's failure in an integrated workflow. This is a decrease relative to structural and v3.8.1 on this path. The revision observation itself is more goal-specific than v3.8.1's observation, which had labeled goal_1 specifically improved from the separate opening change.

### Gate C conclusion

**Gate C passes only for this seven-scenario versioned coverage set.** Actual paths, controlled coverage, and unexercised alternatives are explicit; no counts/routes were forced. This is not full 32-scenario acceptance and does not pass Gate B. **Do not promote v3.8.2.** The integrated #15 result strengthens the unresolved Final-credit concern.

## 5. Reviewer record

```text
Reviewer identifier:
Relevant grades 5–7 / EL / ELD experience (with permission):
Review date:
Artifacts and prompt/fixture versions reviewed:

For each anchor or dimension:
- Rating: Meets / Needs refinement / Unacceptable / Not assessed
- Severity if a concern: Critical / Major / Moderate / Minor
- Exact output passage:
- Observation and rationale:
- Disagreement with any LLM-assisted screening:
- Uncertainty or coverage limitation:
- Recommended action:

Did v3.8.2 resolve F1/F2 without hiding genuine #9 regressions?
Did Anchor B/C readability improve without target-content or source-boundary leakage?
Were Anchor A/D/E behaviors preserved in these runs?
Are any Critical or Major issues unresolved?
Promotion recommendation and conditions:
```

Educator/ELD calibration, target-age EL usability research, full-keyboard testing, and actual screen-reader testing remain separate requirements. This packet does not establish learner outcomes or production readiness.
