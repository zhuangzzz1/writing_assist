# Feedback Quality Improvement Plan
**Based on:** `garden_source_accurate` scenario + corpus analysis of 68 candidates across 30 rounds (acceptance evaluation v3.4.0)
**Date:** 2026-11-11
**Scope:** Support agent feedback generation — pedagogical quality, language complexity, and EL accessibility
**Evidence base:** acceptance DB `v3_acceptance_nonthinking_evaluation_20261110T160932Z.db`

---

## How to Read This Plan

Each principle is tagged with a **confidence level** derived from the corpus:

- **CONFIRMED (systemic)** — observed in ≥20% of corpus candidates, or directly contradicted a schema/data fact
- **CONFIRMED (scenario-specific)** — observed in the garden draft but not systemic across corpus; still valid as a targeted fix
- **HYPOTHESIS** — not yet testable from existing data; needs pilot evidence before schema changes
- **CONTRADICTED** — initial claim from two-finding analysis did not hold up in the corpus

Each principle is also tagged by **implementation track**:

- **Track A** — Support agent prompt constraint only (no schema changes)
- **Track B** — Coordinator schema change required

---

## Part 1: First Revision Suggestion — "Connect the survey result to your claim"

### Finding 1: "Try this" Instruction Complexity

**Confidence:** CONFIRMED (scenario-specific) — corpus shows only 4% of revision_action fields have the dense gerund+multi-clause pattern. This was specific to the garden draft, not systemic. Still valid to fix.

**Problem:** One sentence packs three cognitive operations (locate, reason, connect) with a gerund subject and two coordinated clauses:
> "After the survey sentence, add one or two sentences that explain what the 62% result suggests about students and why that supports starting a garden."

**Fix:** Split into sequenced short commands. One action per sentence, gerund subjects removed.
> Find the sentence with 62%. After it, write one or two sentences.
> First: explain what 62% saying yes tells us about students at this school.
> Then: explain why that is a reason to start a garden.

**Track:** A

---

### Finding 2: Source Accuracy Error Not Surfaced

**Confidence:** CONFIRMED (scenario-specific) — this specific garden draft contains the error; corpus shows the system correctly flags source mismatches in other scenarios (acceptance_02).

**Problem:** "This result shows that some students are interested in fresh food" contains two errors — "some students" understates 62% (a majority), and "interested in fresh food" drifts from what the survey actually measured (whether students would try vegetables from a school garden). The hint asks "what exactly did the survey ask students?" but doesn't name the inaccuracy directly. A student can revise the warrant while keeping the inaccurate characterization.

**Fix:** The passage reference framing should name both issues:
> This sentence has two things to fix: it says "some students" when the number is 62%, and it says "interested in fresh food" when the survey asked about trying vegetables from a school garden. After you correct those, connect the result to your claim.

**Track:** B (Coordinator needs to distinguish warrant gap caused by mischaracterization from a pure warrant gap)

---

### Finding 3: No Model Sentence for Structural Starters

**Confidence:** HYPOTHESIS — plausible for EL students; not directly testable from model outputs alone. Needs pilot with actual students before encoding as a system rule.

**Competing consideration:** Some EL frameworks (SIOP, GLAD) recommend topic-adjacent frames rather than fully generic models, because cross-topic transfer is hard at lower proficiency. A fully generic model sentence may help fluent writers and hurt lower-proficiency ELs. This tradeoff is unresolved.

**Tentative fix (pending pilot):** Add one generic model sentence per structural starter that shows the shape of a completed instance, using a topic different from the student's draft. Per CLAUDE.md, the sentence must not contain claims about the student's topic.

**Track:** A (but mark as low-confidence until piloted)

---

### Finding 4: Vocabulary Sequencing

**Confidence:** HYPOTHESIS — both suggestions define vocabulary after using the same words in the instructional block. Plausible that definitions should precede use, but the corpus shows 91% of candidates include vocabulary options (the system generates them reliably), and their placement is a UI/rendering order question as much as a generation question.

**Tentative fix:** Render vocabulary definitions above the "Try this" block in the UI, or link terms inline on first use. This may be a UI change rather than a prompt change.

**Track:** A (UI rendering order)

---

### Finding 5 (Revised): Negative Contrast Phrasing

**Confidence:** CONTRADICTED as systemic — corpus shows only 6/68 candidates (9%) use "not just" / "more than just" phrasing. This was specific to the garden draft.

**Revised status:** Keep as a targeted fix for the garden scenario, but remove from the generalizable principles list. Downgraded to low priority.

---

## Part 2: Second Revision Suggestion — "Explain how garden jobs build responsibility"

### Finding 6: Priority Ordering — Fabricated Evidence Skipped

**Confidence:** CONFIRMED (systemic) — corpus confirms the system has no distinct `issue_type` for fabricated/invented content. All 68 issues return `issue_type: none`. Fabricated content in acceptance_01 is categorized as `evidence_elaboration`, same as a simple warrant gap. The invented claim ("Students could take home tomatoes and lettuce") appears in acceptance_21's issue description only as a subordinate reference, not as a primary finding.

**Problem:** The system has no severity tier that distinguishes fabricated content from reasoning gaps. A student could complete all suggested revisions and never address invented evidence.

**Fix:** Coordinator schema needs a `finding_severity` field with at least: `accuracy` (factual/source errors, fabricated content) > `reasoning` (warrant gaps, underdeveloped logic) > `development` (elaboration, specificity). Accuracy-tier findings should rank first in Round 1 regardless of which goal they map to.

**Track:** B (Coordinator schema — new severity field)

---

### Finding 7: Structural Starter Shape Mismatch

**Confidence:** CONFIRMED (systemic) — corpus confirms 2 hard mismatches where "explain how X builds responsibility" (causal/explanatory operation) gets `When ____, ____.` (conditional/temporal shape). Both are in separate scenarios (acceptance_01 r0, acceptance_21 r0), confirming this is a recurring pattern, not a one-off.

**Problem:** "When ____, ____." does not scaffold a cause-effect explanation. The student fills the slot and misses the logic.

**Fix:** Coordinator should label each finding with a reasoning operation type. Support selects the starter shape from that label:
- Causal/explanatory → `...because ____.` or `This [evidence/detail] matters because ____.`
- Sequential → `After ____, ____.`
- Source-based → `According to the passage, ____.`
- Concessive → `One concern is that ____; however, ____.`
- Summary → `In sum, ____.`
- Conditional/temporal → `When ____, ____.` (this is correct for some narrative findings)

**Track:** B (Coordinator schema — reasoning operation type label)

---

### Finding 8: "Why that matters" Unanchored

**Confidence:** CONFIRMED (systemic) — corpus shows 58% of `why_it_matters` fields do not anchor to the specific thesis or claim. This is the most widespread quality gap in the corpus.

**Problem:** Generic phrases like "why that matters" or "why this helps" appear without reference to the student's specific claim. Students don't know what they're connecting to.

**Fix:** Any phrase equivalent to "why this matters" in the revision_action must be completed with a prepositional phrase anchoring to the specific claim from the student's draft. Support should use the claim text from the Coordinator's assessment. This should be a prompt constraint: never output "why that matters" without a completing clause.

**Track:** A

---

### Finding 9: Register Mismatch ("again and again")

**Confidence:** CONFIRMED (scenario-specific) — specific to one hint step. 6th graders are sensitive to register condescension; "again and again" reads as a younger-grade turn of phrase. Replace with "regularly" or "over time."

**Track:** A (low priority)

---

### Finding 10: Conceptual Conflation Not Named

**Confidence:** HYPOTHESIS — the "living things need care" sentence conflates empathy with responsibility. Naming the conflation is richer than asking for more sentences. However, it's unclear whether the Coordinator consistently detects concept substitution vs. warrant gap, and there's no corpus evidence yet of how often this pattern appears.

**Tentative fix:** When a passage reference contains a conceptual slippage (student used word A but needed concept B), the Coordinator should flag this as `concept_substitution` distinct from `missing_warrant`, and Support should respond with a naming move rather than an elaboration move.

**Track:** B (Coordinator — new finding subtype; uncertain until more data)

---

## Part 3: Hint Structure (Both Suggestions)

### Finding 11: Missing Concept Restatement (Step 0)

**Confidence:** CONFIRMED (systemic) — the strongest finding in the corpus. 91% of hints (62/68) open with a purely procedural step (look at / reread / find the). No hint in the corpus includes a concept-restatement sentence before the procedural chain. This is universal, not edge-case.

**Problem:** Hints assume the student understood the revision suggestion and jump straight to procedure. Students who click "Show a hint" because they didn't understand the suggestion get steps toward a goal they still can't see.

**Fix:** Every hint needs a one-sentence Step 0 that re-grounds the concept before the procedural chain:
> "In an argument, stating the evidence isn't enough — the writer has to explain why it matters. That's what this revision asks you to do."

The Step 0 sentence should explain the underlying writing move in plain terms, not rephrase the finding title. Since hints are pregenerated (no model call per CLAUDE.md), Step 0 must be generated by Support at pregeneration time.

**Track:** A (highest single impact change in the corpus)

---

### Finding 12: Hints Front-Load Abstract Steps

**Confidence:** CONFIRMED (systemic) — 91% of hint step 1s are procedural-locate ("look at", "reread", "find"). For a student in motivational avoidance (understands but is stuck), pointing them back at the passage they already read is not an encouraging first action.

**Problem:** "Look at: [passage]" re-encounters the material that may have already felt opaque. The most concrete, lowest-stakes first action should come first.

**Fix:** After the concept restatement (Step 0), open the procedural chain with the most concrete first action, not the most abstract one. For the garden scenario: "First, find the number in your draft" precedes "Now look at what the source says the survey actually measured."

**Track:** A

---

### Finding 13: Starter Absent from Rank-1 Findings

**Confidence:** CONFIRMED (systemic) — NEW finding from corpus analysis. 57% of all candidates have no structural starter. But rank-1 findings (the first suggestion the student sees) are the LEAST likely to have one: only 29% (11/38) vs. 59% for rank-2 and 63% for rank-3. The most important finding is most often the one with no scaffolding anchor.

**Problem:** Students receiving their most critical revision suggestion get the least structural support for executing it.

**Fix:** Structural starters should be required (not optional) for rank-1 findings. The Coordinator's ranking logic or Support's output template should enforce this.

**Track:** A/B (prompt constraint in Support; may need Coordinator to pass priority rank to Support)

---

## Generalizable Principles

Ordered by corpus confidence. Principles 1-5 are supported by systemic corpus evidence. Principles 6-9 are hypotheses needing further validation.

### Principle 1: Hint Layering by Confusion Type (CONFIRMED — systemic)

Hints currently serve only procedural confusion (91% step-1 procedural). They need to serve three types simultaneously since they are pregenerated and cannot ask which applies:

1. **Conceptual confusion** — student didn't understand the revision suggestion → needs Step 0 concept restatement
2. **Procedural confusion** — understood the suggestion but can't execute → needs step chain (current design serves this)
3. **Motivational avoidance** — understands but is stuck → needs a low-stakes concrete first action

Every hint needs a Step 0 concept restatement before the procedural chain. The chain should open with the most concrete action, not the most abstract.

**Applies to:** Track A — Support prompt constraint (output format)

---

### Principle 2: Finding Severity Tiers (CONFIRMED — systemic)

The Coordinator generates no `issue_type` field (all 68 return `none`). All categories collapse to `evidence_elaboration`, `organization`, `source_use`, `central_idea`, `task_alignment`, `language_conventions`. There is no `fabricated_content` or `invented_evidence` tier. Fabricated content gets ranked and treated the same as a thin warrant.

Needed tiers, highest to lowest:
1. `accuracy` — factual errors, fabricated/invented content, source misrepresentation
2. `reasoning` — warrant gaps, underdeveloped logic, missing connections
3. `development` — elaboration, specificity, structure

Accuracy-tier findings should rank first in Round 1 regardless of goal assignment.

**Applies to:** Track B — Coordinator schema (`finding_severity` field + ranking logic)

---

### Principle 3: Structural Starter Shape Alignment (CONFIRMED — systemic)

Starters are absent from 57% of candidates and misaligned with the reasoning operation in at least 2 confirmed cases. The "When ____, ____.` starter is used for causal/explanatory moves in both acceptance_01 and acceptance_21.

The starter's syntactic shape must encode the reasoning operation. The Coordinator should label each finding with a reasoning operation type; Support selects the starter from that label. See Finding 7 for the full mapping.

Starters should also be required for rank-1 findings (Finding 13).

**Applies to:** Track B — Coordinator schema (reasoning operation type) + Track A — Support starter selection

---

### Principle 4: Claim Anchoring (CONFIRMED — systemic)

58% of `why_it_matters` fields do not anchor to the student's specific thesis. "Why that matters" without a referent is not actionable for a student who doesn't already know what it matters for.

Any "why X matters" phrase must be completed with a clause tying it to the specific claim in the draft. Support should use the claim text supplied by the Coordinator.

**Applies to:** Track A — Support prompt constraint

---

### Principle 5: Fabrication Detection (CONFIRMED — systemic)

No schema field exists to distinguish invented content from other reasoning problems. This is an upstream Coordinator gap. Until a `finding_severity` field exists, the Support agent cannot know that an `evidence_elaboration` finding is actually about invented content.

**Applies to:** Track B — Coordinator schema (Principle 2 above)

---

### Principle 6: Instruction Decomposition (HYPOTHESIS — not systemic)

Initial finding from two-finding analysis: dense "Try this" instructions pack multiple operations into one sentence. Corpus shows only 4% of revision_action fields have this pattern. Not systemic — was specific to the garden draft.

**Status:** Valid targeted fix for the garden scenario. Not worth encoding as a system-wide prompt rule. Downgraded.

---

### Principle 7: Conceptual Conflation Naming (HYPOTHESIS)

When a student uses word A but needs concept B (e.g., "living things need care" vs. the concept of responsibility), naming the conflation is more valuable than asking for elaboration. This requires a `concept_substitution` Coordinator finding type.

**Status:** No corpus evidence for frequency. Test before implementing.

---

### Principle 8: Model Sentences for Structural Starters (HYPOTHESIS)

Generic model sentences showing completed starter shapes may help EL students. However, cross-topic transfer is hard at lower proficiency — some EL frameworks recommend topic-adjacent frames instead. The tradeoff is unresolved.

**Status:** Test with actual students before encoding as a requirement.

---

### Principle 9: Vocabulary Sequencing (HYPOTHESIS)

Vocabulary definitions should precede the instructional block that uses those terms. The corpus shows 91% of candidates already include vocabulary (good), but placement is a UI/rendering question not visible in the model output data.

**Status:** Likely a UI rendering order change, not a prompt change.

---

## Corrections to Initial Plan

The following claims from the original two-finding analysis did not survive corpus validation and have been downgraded:

| Original claim | Corpus verdict | Revised status |
|---|---|---|
| Negative contrast phrasing ("not just") is systemic | 6/68 = 9% prevalence | Scenario-specific. Low priority. |
| Dense "Try this" instructions are systemic | 3/68 = 4% prevalence | Scenario-specific. Low priority. |
| "again and again" register problem is systemic | Single occurrence | Scenario-specific. Lowest priority. |
| All hints lack Step 0 | 91% lack it = CONFIRMED | Upgraded to Principle 1, highest priority |
| Starter absence is a minor issue | 57% absent, rank-1 most affected = CONFIRMED | Upgraded to Principles 3 + 13 |

---

## Known Limitations and Open Questions

### L1: Simulation validated feedback properties, not student behavior

Personas 2 (Jordan) and 3 (Sam) had their feedback and hint content confirmed from live DOM reads. Neither persona completed a full revision loop — Streamlit's React checkbox state did not persist through reruns for programmatic interactions. Claims about what Jordan or Sam "would do" with their hints are inferences, not observations. Status of F7 and F12 should be read as "OBSERVED (feedback has this property)" not "CONFIRMED (students behave this way)."

Only Maya (Persona 1) completed a full revision loop, and that loop confirmed one prediction: the warrant gap persisted after a surface fix.

### L2: Confidence tiers conflate data counts and interpretive judgments

"CONFIRMED systemic" is used for two distinct evidence types:
- **Data counts** (objective): F11 — 62/68 hints lack Step 0; F13 — 71% of rank-1 findings have no starter. These are counts.
- **Pattern matching** (interpretive): F7 — revision_action language was classified as "causal/explanatory" and compared to starter shape using human judgment. This involves classification error risk.

Treat data-count confirmations as stronger evidence than pattern-match confirmations.

### L3: All evidence is from argument genre; narrative and informational findings may differ

The corpus is dominated by argument drafts. Finding 12 (hints front-load abstract steps) may not apply to narrative hints, where "reread your last sentence" is often the correct first step because the student's draft is the source of concrete detail. Principle 9 (hint layering) applies most clearly to source-dependent argument findings. Apply genre-boundary tags to each principle before shipping:

- F11 (Step 0): likely applies across genres — no hint has a concept restatement regardless of genre
- F12 (concrete first step): applies most strongly to source-dependent argument findings; validate separately for narrative
- F7 (starter alignment): "When ____, ____." confirmed wrong for causal argument moves; check whether it's correct for narrative temporal moves (acceptance_05, acceptance_26)
- F9 ("again and again"): only observed in garden-scenario responsibility hints; may not appear elsewhere

### L4: F4 (vocabulary sequencing) has a competing pedagogical position

The plan asserts "definitions should precede use." A counter-position from second language acquisition research ("meaning-before-label") holds that encountering a word in context first, then receiving a definition, produces better retention. This tension is unresolved. F4 should not be implemented as a prompt change until a pilot with actual EL students provides evidence for which approach works better for this population and this task type.

### L5: Finding 2 (source accuracy + warrant in one finding) may increase cognitive load

Naming two errors in the same passage reference — fix the accuracy error, then fix the warrant — may be too much for one revision round. The plan doesn't specify whether these should be sequential (accuracy in Round 1, warrant in Round 2) or simultaneous. Some pedagogy frameworks prioritize accuracy before reasoning. This is a policy decision that needs an explicit stance, not just a schema addition.

### L6: Finding 14 (partial-progress blindness) is a hypothesis

One round-2 session showed re-presentation of the same goal card after Maya's surface fix. The plan asserts this "may read as 'you got it wrong.'" There is no behavioral evidence for this interpretation — it is inferred from outside. Finding 14 should be treated as a hypothesis pending actual student feedback. Keep it listed but do not schedule schema work for it until a pilot provides evidence.

---

## Priority Table (Revised, Evidence-Backed)

| Priority | Finding/Principle | Confidence | Track | Effort | Impact |
|----------|------------------|------------|-------|--------|--------|
| 1 | Hint Step 0 — concept restatement (P1, F11) | CONFIRMED systemic | A | Low | High |
| 2 | Claim anchoring in why_it_matters (P4, F8) | CONFIRMED systemic | A | Low | High |
| 3 | Finding severity tiers — accuracy vs reasoning (P2, F6) | CONFIRMED systemic | B | Medium | High |
| 4 | Starter shape alignment (P3, F7) | CONFIRMED systemic | B | Medium | Medium-High |
| 5 | Starters required for rank-1 findings (F13) | CONFIRMED systemic | A/B | Low | Medium-High |
| 6 | Source accuracy surfaced in passage reference (F2) | CONFIRMED scenario | B | Medium | High |
| 7 | Hint step ordering — concrete action first (F12) | CONFIRMED systemic | A | Low | Medium |
| 8 | Structural starter for Suggestion 2 (causal not conditional) (F7) | CONFIRMED systemic | A | Low | Medium |
| 9 | Model sentences for starters (P8, F3) | HYPOTHESIS | A | Low | Unknown |
| 10 | Vocabulary sequencing (P9, F4) | HYPOTHESIS | A/UI | Low | Unknown |
| 11 | Conceptual conflation naming (P7, F10) | HYPOTHESIS | B | Medium | Unknown |
| 12 | Instruction decomposition for garden draft (P6, F1) | CONFIRMED scenario | A | Low | Low |
| 13 | Negative contrast phrasing (F5) | CONTRADICTED systemic | A | Low | Low |
| 14 | Register fix ("again and again") (F9) | CONFIRMED scenario | A | Low | Low |
| 15 | Tone bridge sentence | Preference | A | Low | Low |

---

## Implementation Strategy

### Track A — Support prompt constraints (no schema changes)

**Ship in order:** F11 (Step 0), F8 (claim anchoring), F12 (hint step ordering), F13 (require starters for rank-1), F7 (causal starter fix for responsibility findings).

Low risk. Validate each change against the 32-scenario non-thinking run (`V3_OUTCOMES_REPORT.md` Section 17). F11 is highest impact single change — 91% of hints are affected.

### Track B — Coordinator schema additions

**Three additions in dependency order:**
1. `finding_severity` field: `accuracy | reasoning | development` (enables F6, F13 ranking)
2. `reasoning_operation` field: `causal | sequential | source_based | concessive | summary | conditional` (enables F7 starter alignment)
3. `concept_substitution` finding subtype (enables F10 — do this last, after pilot evidence)

Regression test against acceptance set before shipping. The reasoning_operation label (item 2) is the most likely to affect existing scenarios — verify that scenarios where `When ____, ____.` is currently correct (some narrative findings in acceptance_05, acceptance_26) don't get reclassified incorrectly.

### Simulation Validation (2026-11-11)

Three student personas were run against the live app via Playwright automation (`SIMULATION_EVIDENCE_REPORT.md`). Results:

| Finding | Corpus status | Simulation verdict |
|---|---|---|
| F7: "When ____, ____." on causal move | CONFIRMED systemic | **CONFIRMED** — Jordan session, same mismatch as corpus |
| F9: "again and again" register | CONFIRMED scenario-specific | **CONFIRMED** — appeared in Sam's session independently |
| F11: No Step 0 concept restatement | CONFIRMED systemic | **CONFIRMED** — all three persona sessions, no hint opened with concept restatement |
| F12: Hints front-load abstract steps | CONFIRMED systemic | **CONFIRMED** — Hint 1 step 1 sent Sam to "reread source paragraph"; stuck_step provided better first action |
| Principle 9: Hint layering by confusion type | CONFIRMED systemic | **CONFIRMED** — Maya's warrant gap persisted through revision loop; Jordan's conditional starter misdirected; Sam's hint front-loaded the wrong step |

**New finding from simulation (F14):** When a student makes a correct partial fix (surface error), Round 2 re-presents the same goal card with the same rationale and instruction. There is no acknowledgment that partial progress was made. For a student already confused about the core concept, identical-looking feedback in Round 2 may read as "you did it wrong" rather than "you're closer, now finish." The system correctly identifies the remaining gap, but the feedback framing doesn't distinguish partial success from no progress.

### Validation before schema changes

Before committing to Track B schema work, the following hypotheses need evidence beyond model outputs:

1. Does Step 0 (concept restatement) actually help students who clicked for conceptual confusion? — requires think-aloud or click-pattern data from real students
2. Do generic model sentences help EL students or hurt lower-proficiency ones? — requires pilot with actual 6th graders, including EL students
3. How often does concept substitution appear across natural student writing vs. synthetic test cases? — run the acceptance evaluator on a broader scenario set that includes more varied student errors

### Constraints

- Hints are pregenerated and make no model call (per CLAUDE.md). All Principle 1 fixes must be pregeneration output format changes.
- Model sentences must be generic — no student topic, genre, or source material (per CLAUDE.md).
- Do not validate pedagogical effectiveness from model outputs alone. Mocked tests confirm structural compliance, not whether students learn from the feedback.
