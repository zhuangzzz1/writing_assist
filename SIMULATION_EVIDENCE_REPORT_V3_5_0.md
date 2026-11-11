# V3.5.0 Persona Simulation Evidence Report

**Date:** 2026-11-11
**Prompt/schema version:** v3.5.0
**Model:** deepseek-flash (thinking=false, temperature=0)
**Runs:** Two sessions — 3 personas (2026-11-11T182835Z), 6 personas (2026-11-11T185740Z)
**Evidence files:**
- `data/evidence/persona_simulation_v3_5_0_20261111T182835Z.json` (Maya, Jordan, Sam)
- `data/evidence/persona_simulation_v3_5_0_20261111T185740Z.json` (Maya, Jordan, Sam, Alex, River, Devon)

---

## Personas

| Persona | Grade | Scenario | Confusion type | Revision |
|---------|-------|----------|---------------|----------|
| Maya | 6th | garden_source_accurate | Conceptual | surface_only (some → most, no warrant) |
| Jordan | 6th | garden_source_accurate | Procedural | complete (would use starters) |
| Sam | 6th | garden_source_accurate | Motivational | complete (concrete anchor unlocks) |
| Alex | 5th | short_grade5_argument | Procedural | partial (one because-sentence) |
| River | 7th | races_informational_pollination | Conceptual | partial (E-step missing) |
| Devon | 6th | garden_source_mismatch | Conceptual | partial (would re-read source) |

---

## Track B Findings (from second run)

### F6 — Severity-based ranking

| Persona | First severity | Accuracy ranked first |
|---------|---------------|----------------------|
| Maya | reasoning | false |
| Jordan | accuracy | true |
| Sam | reasoning | false |
| Alex | development | false |
| River | accuracy | true |
| Devon | accuracy | true |

Maya and Sam received `garden_source_accurate` in the same session as Jordan. Jordan's run
produced an accuracy finding; Maya's and Sam's did not. The same draft, the same session,
different Coordinator assessments. See Improvement 1 below.

### F7 — Reasoning operation classification

| Persona | First op | Starter |
|---------|----------|---------|
| Maya | causal | `This matters because ____.` |
| Jordan issue 1 | source_based | `According to the survey, ____.` |
| Jordan issue 2 | source_based | `This evidence matters because ____.` |
| Sam | source_based | `According to the survey, ____.` |
| Alex | causal | `This matters because ____.` |
| River | source_based | `According to the passage, ____.` |
| Devon | source_based | `According to the passage, ____.` |

No `when ____, ____.` appeared on a causal finding. The old pre-Track-B bug is gone.

---

## Improvement Opportunities

### I1 — Severity classification is inconsistent across same-draft runs (High)

**Evidence:** Maya and Sam both received `garden_source_accurate` in the same session at
temperature=0. Jordan got an accuracy finding (source overclaim); Maya and Sam did not.
All three drafts are identical.

**Root cause (probable):** The boundary between `accuracy` (draft states something the source
does not support) and `reasoning` (evidence present but not explained) is underspecified in the
Coordinator prompt. The same misuse of a survey result can be read either way depending on which
aspect the model focuses on first.

**Suggested fix:** Add a discriminator example to the Coordinator prompt. When the draft states
a fact that cannot be verified or is contradicted by the source, it is `accuracy`. When the draft
cites the evidence correctly but does not explain what it means or why it matters, it is
`reasoning`. The difference: *does the student need to go back to the source to fix it, or do
they need to reason about what the source already says?*

---

### I2 — `source_based` operation overused when the real gap is causal (High)

**Evidence:** Sam's first finding: "the number and the claim sit side by side without a bridge"
— a warrant gap. The `reasoning_operation` is `source_based` and the starter is
`"According to the survey, ____."`  That sends the student back to cite, but the student already
cited correctly. The fix needed is a because-sentence, not another citation.

Jordan's second finding is the counter-example done right: `evidence_elaboration`, `source_dependent: true`,
but `reasoning_operation: causal` → starter `"This evidence matters because ____."`

**Rule the Coordinator is missing:** When `category: evidence_elaboration` and
`source_dependent: true` but the description names a *missing warrant* (not a missing citation),
classify `reasoning_operation: causal`, not `source_based`. The question: does the student need
to go back to the source, or reason about what the source already shows?

---

### I3 — River's RACES feedback bundles two structurally distinct tasks into one candidate (Medium)

**Evidence:** River had four RACES components flagged (Restate, Cite, Explain, Sum up). The
third candidate bundled Restate (opening move) and Sum up (closing move) into a single revision
action with a single `draft_reference`.

A student following this candidate has to fix two locations at once. Restate is a new opening
sentence; Sum up is a new closing sentence. Neither is a revision of an existing sentence —
they are additions in different positions.

**Suggested fix:** When framework coverage has more than two issue components and any of them
are structural *additions* (not revisions of existing text), split into separate candidates by
location. One candidate per structural addition location is the right granularity.

---

### I4 — Alex (5th Grade, no source) produced the cleanest feedback in the set — use as quality bar (Informational)

**Evidence:** Alex's run: 1 issue, 1 candidate, 4-step hint, `causal` op,
`"This matters because ____."`  Step 0: "naming a reason is only part of the job — the writer
also explains why that reason matters." `stuck_step`: "Picture yourself reading at your desk
while classmates talk nearby. Write down one thing that gets harder for you."

No multi-candidate entanglement, no competing targets, the student's path is clear and concrete.

**Implication:** The system converges to clean, focused feedback when the draft is simpler and
there is no source. This confirms the earlier proposal to limit candidates to 1 when the
top-ranked finding is `accuracy / source_use` — the conditions that produce entanglement are
source-dependent accuracy violations where multiple issues share a paragraph.

---

### I5 — Devon: `source_based` op assigned to `source_dependent: false` finding (Medium)

**Evidence:** Devon's third finding: `finding_severity: development`,
`reasoning_operation: source_based`, `source_dependent: false`. The description is about the
responsibility reason being underdeveloped — the source does not cover responsibility at all.
If this finding were surfaced as a candidate (it ranked third and was not), the student would
receive "According to the passage, ____." on a finding where the passage is irrelevant.

**Constraint to add in the Coordinator prompt:** `reasoning_operation: source_based` requires
`source_dependent: true`. A `source_dependent: false` finding may not receive `source_based`
as its operation — use `causal`, `conditional`, `sequential`, or `none` based on the actual
reasoning move.

---

### I6 — `why_it_matters` quality is uneven (Low)

**Evidence — weak:** Devon candidate 1: "Readers trust evidence more when it matches what the
source actually measured, so this helps your argument that the school should start a garden stay
believable." This restates why accuracy matters rather than naming what a reader experiences.

**Evidence — strong:** Alex candidate 1: "Readers can follow your thinking better when you
explain why a quiet place would help students read, not just that it would be quiet." This
names a reader effect specifically.

**Prompt constraint to add:** `why_it_matters` must describe a *reader effect* — what a reader
will think, be able to do, or fail to understand — not restate the finding or the writing
principle. Test: does the sentence describe something the reader experiences?

---

### I7 — Maya's round 2 regression: surface-only fix worsened the accuracy tier (Informational)

**Evidence:** Maya changed "some students" to "most students." The Coordinator in round 2
flagged this as a new accuracy regression — `"most students are interested in fresh food"`
overgeneralizes the survey just as much as the original. The original round 1 accuracy issue
(take-home produce) went unaddressed. Round 2 had to restart with a new accuracy finding.

This is the multi-candidate entanglement pattern from the first run confirmed: Maya's intuitive
revision target (`"some" → "most"`) was different from the ranked-first candidate's anchor
(`"Students could take home tomatoes and lettuce."`). She fixed the wrong thing, and the fix
itself introduced a new error.

**This supports I4:** When the top-ranked finding is `accuracy / source_use` and the accuracy
anchor is in the same paragraph as a reasoning finding, present only the accuracy candidate.
The student fixing the reasoning finding first will introduce a regression.

---

## Open questions for the 100-evidence run

1. How often does `source_based` appear on `source_dependent: false` findings? (I5)
2. What is the accuracy/reasoning boundary miss rate across all scenarios? (I1)
3. Do `causal` findings in source-dependent contexts receive the right operation more reliably
   after a prompt fix? (I2)
4. How often do multi-candidate runs produce a revision that ignores the first candidate? (I7)
5. Does the RACES scenario consistently produce multi-issue bundling? (I3)

---

## Operational notes

- Sam persona hit `ResponseValidationError` on first attempt in the 3-persona run (unapproved
  sentence starter, pre-removal of allowlist). Retried successfully.
- Sentence starter allowlist removed from `HintOutput` schema validation after this run.
  See `agents/support_agent.py` and `tests/test_agents.py`.
- The comparison-with-baseline section of `simulate_personas_v3_5_0.py` should be replaced
  with an improvement-opportunity analysis function before the 100-evidence run.
