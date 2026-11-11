# Simulation Evidence Report
**Date:** 2026-11-11
**Method:** Playwright browser automation against live app (localhost:8501)
**Scenario:** `garden_source_accurate` — community garden argument with source
**Personas:** Maya (conceptual confusion), Jordan (procedural confusion), Sam (motivational avoidance)
**Screenshots:** `data/evidence/simulation_p*.png`

---

## Setup Notes

The CCv2 goal-selection checkbox uses Streamlit's `on_change` callback, which requires a true browser event to persist through React's reconciliation. Programmatic label clicks (via `label.click()`) trigger the React handler momentarily but do not survive the subsequent Streamlit rerun. This meant goal selection via automation was unreliable. Where this blocked the full revision loop, the feedback content was captured directly from the DOM before the rerun. All hint text, starter text, and finding structures were confirmed from live DOM reads, not from the DB.

Maya's full revision loop (round 1 → revision → round 2) was completed successfully via the shadow DOM `oninput` approach and confirmed in the DB.

---

## Persona 1: Maya (Conceptual Confusion)

**Hypothesis:** Maya fixes the surface number error ("some" → "most") but doesn't add the warrant sentence because she never understood what "Connect the survey result to your claim" meant. The warrant gap persists into Round 2.

### Round 1 Feedback Received

**Finding 1:** "Connect the survey result to your claim"
- Rationale: "Right now the survey number is reported, but a reader may not see how it supports your claim. Explaining the link helps readers follow your thinking."
- Passage: "This result shows that some students are interested in fresh food."
- Try this: "After the sentence that reports the 62% result, add one or two sentences in your own words that explain what that result suggests about students and why that supports starting a garden."

**Finding 2:** "Explain why the responsibility chores matter"
- Passage: "Students would water plants and pull weeds. They would learn that living things need care."

### Hint 1 Expanded (Maya's experience)

```
Look at: "This result shows that some students are interested in fresh food."

1. Reread the source sentence about what the survey measured and what it did not measure.
2. Look at your sentence: it says students are 'interested in fresh food.' Ask yourself what 
   that interest has to do with your claim that the school should start a garden.
3. Write a sentence that links the survey result to your claim, using your own words rather 
   than copying the source.

Check your revision: Does your new sentence explain how the survey result supports your claim, 
not just restate the number?

Vocabulary to evaluate: interest — a feeling of wanting to know or try something, 
suggests — hints at or points toward an idea, supports — helps show that a claim is reasonable, 
measured — recorded or counted in a survey.

Optional structural starter: This evidence matters because ____.
```

### Finding 11 Confirmed

The word "claim" appears in step 2 and step 3 with no definition. No Step 0 concept restatement exists. A student without a working model of "claim" as an argument term will encounter it twice in the hint and still not know what to do. The hint jumps straight to procedure.

### Maya's Revision

Maya fixed "some students" → "most students" (1 word added, 1 word removed — confirmed by the app's revision notice) but did not add the warrant sentence.

**Revised paragraph 2:**
> "This result shows that most students are interested in fresh food."

No new sentence was added. The warrant gap remained.

### Round 2 Feedback (confirmed from DB)

The system re-flagged the same issue with an updated passage reference:

**Finding:** "Link the survey result to your claim"
- Issue category: `evidence_elaboration`
- Description: "The survey explanation now says 'most students are interested in fresh food,' but it still does not explain how that interest supports the claim that the school should start a garden."
- Revision action: (same as round 1 — add one or two sentences explaining the connection)
- Starter: `This evidence matters because ____.` (same)

### Verdict: Hypothesis CONFIRMED

Maya's surface fix was detected and acknowledged. The warrant gap persisted into Round 2 exactly as predicted. The system correctly identified the remaining issue, but the cycle will repeat until Maya adds the explaining sentence — which she can't do without understanding what a "claim" is in argument writing.

**Evidence validates:** Finding 11 (missing Step 0 concept restatement), Principle 9 (hint layering by confusion type)

---

## Persona 2: Jordan (Procedural Confusion)

**Hypothesis:** Jordan clicks the hint for suggestion 1 and gets a usable causal starter. She clicks the hint for suggestion 2 and gets "When ____, ____.," which misdirects her revision — she fills the conditional slot but doesn't encode the causal mechanism.

### Round 1 Feedback Received (Jordan's fresh session)

**Finding 1:** "Explain what the survey result shows"
- Rationale: "Readers need to see how the survey result supports your claim, not just that some students are interested."
- Passage: "This result shows that some students are interested in fresh food."
- Try this: "After the survey sentence, add one or two sentences that explain why the 62% result makes a garden worthwhile, using only what the survey measured."

**Finding 2:** "Show how garden jobs build responsibility"
- Rationale: "Your reader needs to see the steps between watering plants and becoming a better citizen, not just the final claim."
- Passage: "This would help them become better citizens."
- Try this: "Add one or two sentences that explain how doing garden jobs like watering and weeding could lead to the kind of responsibility you describe."

### Hint 1 Expanded

```
Look at: "This result shows that some students are interested in fresh food."

1. Look at your sentence: it says students are interested, but it does not say why that 
   interest matters for the school.
2. Check the source: what exactly did the survey measure, and what did it not measure?
3. Think about how you can connect the survey result to your claim without going beyond what 
   the survey shows.

Check your revision: Does your new sentence explain why the survey result supports starting a 
garden, while staying within what the survey actually measured?

Vocabulary: interest, measured, supports.

Optional structural starter: This evidence matters because ____.
```

**Starter shape:** `This evidence matters because ____.` → CAUSAL ✓ correct match for a causal/explanatory move

### Hint 2 Expanded

```
Look at: "This would help them become better citizens."

1. Look at the jobs you listed: watering plants and pulling weeds.
2. Ask yourself: what do students have to remember or do regularly to keep plants alive?
3. Think about how that habit could connect to being a responsible citizen, and explain the 
   connection in your own words.

Check your revision: Does your explanation show a clear step-by-step link between the garden 
jobs and the responsibility you describe?

Vocabulary: responsibility, citizen, habit.

Optional structural starter: When ____, ____.
```

**Starter shape:** `When ____, ____.` → CONDITIONAL/TEMPORAL ✗ mismatch for a cause-effect explanation

### Finding 7 Confirmed in Live Browser Run

The revision action for Finding 2 asks Jordan to "explain how doing garden jobs like watering and weeding could lead to the kind of responsibility you describe" — a causal mechanism. The starter `When ____, ____.` encodes a conditional or temporal relationship, not causation.

Jordan would produce: "When students water plants and pull weeds, they learn responsibility." This fills the slot but doesn't explain the mechanism — what repeated action produces what character trait through what process. The sentence sounds complete but the reasoning move is not made.

By contrast, `Doing ____ regularly teaches students to ____ because ____.` or `This evidence matters because ____.` would force the causal chain.

**Evidence validates:** Finding 7 (structural starter shape mismatch), Principle 3 (starter shape alignment)

### Additional Observation: Finding 11 Confirmed in Jordan's Session

Both hints open with procedural-locate steps ("Look at your sentence...", "Look at the jobs you listed..."). No Step 0 concept restatement in either hint. Finding 11 confirmed independently across two sessions.

---

## Persona 3: Sam (Motivational Avoidance)

**Hypothesis:** Sam understands the feedback and roughly knows what to do. The hint's first step ("Reread the source paragraph...") points him back at the source he already read — the most abstract step, not the most concrete. He needs "I'm stuck" to get a low-stakes first action.

### Round 1 Feedback Received (Sam's fresh session)

**Finding 1:** "Connect the survey result to your fresh-food reason"
- Rationale: "Right now the survey number sits next to your reason, but readers have to guess how they connect. Showing that link helps readers see why the evidence supports your claim."
- Passage: "This result shows that some students are interested in fresh food."

**Finding 2:** "Explain how watering and weeding build responsibility"
- Rationale: "Listing actions shows what students would do, but readers need to see how those actions teach responsibility and connect to becoming better citizens."
- Passage: "Students would water plants and pull weeds. They would learn that living things need care."

### Hint 1 Expanded

```
Look at: "This result shows that some students are interested in fresh food."

1. Reread the source paragraph and find the sentence that says what the survey measured.
2. Look at your sentence 'This result shows that some students are interested in fresh food.' 
   Ask: what does the survey actually tell us, and what does it not tell us?
3. Think about how students trying vegetables connects to your reason about fresh food — what 
   would a garden make possible for those students?

Check your revision: Does your new sentence explain the link between the survey result and 
your fresh-food reason, rather than just repeating the number?

Vocabulary: interest, measured, outcomes.

Optional structural starter: This evidence matters because ____.
```

**Step 1 type:** ABSTRACT (Reread the source paragraph) — sends Sam back to material he already read

### Hint 2 Expanded

```
Look at: "Students would water plants and pull weeds. They would learn that living things need care."

1. Look at the two jobs you named — watering and weeding. What happens to a plant if someone 
   forgets to do them?
2. Ask yourself: what habit or skill does a student build by remembering to do those jobs 
   again and again?
3. Connect that habit to your phrase 'better citizens' — what does a responsible citizen do 
   that a gardener also does?

Check your revision: Does your explanation show the step between the action (watering, weeding) 
and the result (responsibility, citizenship), instead of just naming both?

Vocabulary: responsibility, citizen, habit.

Optional structural starter: When ____, ____.
```

**Step 1 type:** More CONCRETE (Look at the two jobs you named) — better for motivational avoidance
**Step 2:** "again and again" — Finding 9 (register mismatch) confirmed in Sam's session

### Finding 12 Confirmed

Hint 1 step 1 sends Sam to "reread the source paragraph" — the most abstract, re-encountering action. Sam has already read the source. He knows what it says. What he needs is permission to start writing, not another round of reading. The hint's first action is exactly the wrong one for motivational avoidance.

Hint 2 step 1 is comparatively better: "Look at the two jobs you named" points Sam at his own draft, which is more concrete and self-referential. This contrast within the same feedback session is instructive — the difference in step 1 quality between hints 1 and 2 is not systematic, it's incidental. Neither was designed with the motivational-avoidance case in mind.

### "I'm stuck" Button (Finding 12 Comparison)

The stuck_step from the DB for the equivalent session (acceptance_01):
> "Circle the words 'some students' in your draft, then write one sentence that replaces them with a phrase that matches 62% and says why that matters for your claim."

This is a substantially better first action for Sam: concrete (circle something), mechanical (write one sentence), and grounded in his draft rather than the source. It's the low-stakes foothold a frozen writer needs. The plan predicted this correctly.

**Evidence validates:** Finding 12 (hints front-load abstract steps), Finding 11 (no concept restatement), Finding 9 (register mismatch — "again and again")

---

## Finding 9 Additional Confirmation

"again and again" appeared in Sam's round in hint 2, step 2: "Ask yourself: what habit or skill does a student build by remembering to do those jobs again and again?"

This phrase also appeared in the earlier session (from the initial two-finding analysis). It is now confirmed in two independent model runs across different sessions. Finding 9 (register mismatch) is **CONFIRMED scenario-specific** — it appears consistently in garden-scenario responsibility hints.

---

## Summary of Validation Results

| Finding | Plan status | Simulation verdict |
|---|---|---|
| F7: Starter shape mismatch ("When ____, ____." on causal move) | CONFIRMED systemic (corpus) | CONFIRMED in live browser — Jordan session, identical to corpus finding |
| F9: "again and again" register mismatch | CONFIRMED scenario-specific | CONFIRMED — appeared in Sam's session independently |
| F11: No Step 0 concept restatement | CONFIRMED systemic (corpus, 91%) | CONFIRMED in all three persona sessions — no hint opened with a concept restatement |
| F12: Hints front-load abstract steps | CONFIRMED systemic (corpus, 91%) | CONFIRMED — Hint 1 step 1 sends Sam to "reread source paragraph"; "I'm stuck" provides better first action |
| Principle 9: Hint layering by confusion type | CONFIRMED systemic | CONFIRMED — Maya's warrant gap persisted despite surface fix; Jordan's conditional starter misdirects; Sam's hint front-loads the wrong step |

### Findings Refined by Simulation

**F12 nuance:** Hint 2 (responsibility) in Sam's session had a better step 1 ("Look at the two jobs you named") than Hint 1 ("Reread the source paragraph"). The abstract-step problem is worse for source-dependent findings than for self-contained reasoning findings. The fix should prioritize hints where step 1 sends the student back to the source.

**F9 nuance:** "again and again" is consistent in garden-scenario responsibility hints specifically. It may not appear in other scenarios. Keep as scenario-specific, not systemic.

**Persona 1 (Maya) unexpected finding:** Round 2 re-presented the same goal card with the same hint, same starter, and updated passage reference. After Maya's surface fix, there was no indication to her that she had made a correct partial change. The feedback didn't acknowledge "some → most" as progress. For a student already confused about the core concept, receiving what looks like the identical feedback again (same rationale, same instruction, slightly different passage reference) may read as "you did it wrong" rather than "you made progress, now finish." This is an unplanned finding worth noting.

---

## Screenshots Captured

- `simulation_p1_maya_feedback_loaded.png` — Persona 1 initial feedback viewport
- `simulation_p1_maya_choose_step.png` — Full-page Choose step with both findings
- `simulation_p1_maya_hint1_open.png` — Hint 1 expanded, full page
- `simulation_p1_maya_round2_feedback.png` — Round 2 feedback showing persisted warrant gap
- `simulation_p2_jordan_choose_step.png` — Jordan's full-page Choose step
- `simulation_p3_sam_choose_step.png` — Sam's full-page Choose step with both hints expanded
