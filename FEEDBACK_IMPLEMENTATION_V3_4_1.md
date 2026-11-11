# Feedback Quality Implementation V3.4.1

**Implementation Date:** 2026-11-11
**Based on:** FEEDBACK_QUALITY_IMPROVEMENT_PLAN.md
**Track:** A (Support agent prompt constraints, no schema changes to Coordinator)
**Status:** Implemented

---

## Changes Implemented

### 1. Finding 11: Step 0 Concept Restatement (CONFIRMED systemic - 91% of corpus)

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, HINT AUTHORSHIP BOUNDARY section

**Change:** Every hint now requires a Step 0 sentence that re-grounds the underlying writing concept before the procedural chain.

**Implementation:**
```
Step 0 (concept restatement): Open with one sentence that re-grounds the underlying writing concept in plain terms before the procedural chain. This is not a rephrased finding title; explain the writing move itself. Example: "In an argument, stating the evidence isn't enough — the writer has to explain why it matters." Generate this sentence as the first step.
```

**Schema Impact:** Updated `HintOutput.steps` from `min_length=2` to `min_length=3` in `agents/support_agent.py` to enforce Step 0 + at least 2 procedural steps.

**Rationale:** Hints serve three types of confusion (conceptual, procedural, motivational). Students who click "Show a hint" because they didn't understand the revision suggestion need the concept explained, not just procedural steps. This was the strongest finding in the corpus analysis.

---

### 2. Finding 12: Concrete-First Procedural Steps (CONFIRMED systemic - 91% of corpus)

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, HINT AUTHORSHIP BOUNDARY section

**Change:** After Step 0, procedural chains must open with the most concrete, lowest-stakes first action instead of abstract "look at" or "reread" steps.

**Implementation:**
```
Procedural steps (2-4 steps): After Step 0, provide the linked thinking steps. Open the procedural chain with the most concrete, lowest-stakes first action, not the most abstract one. Instead of starting with "Look at the passage" or "Reread your draft," start with a concrete anchor like "Find the survey number in your draft" or "Locate the sentence with the percentage."
```

**Rationale:** For students in motivational avoidance (understands but is stuck), pointing them back at the passage they already read is not an encouraging first action. The most concrete action should come first.

---

### 3. Finding 13: Rank-1 Starter Requirement (CONFIRMED systemic - 57% lack starters)

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, HINT AUTHORSHIP BOUNDARY section

**Change:** Structural starters must be required (not optional) for rank-1 findings. Rank-1 findings were the LEAST likely to have starters (29% vs 59% for rank-2).

**Implementation:**
```
For the first candidate (rank 1, the most important revision suggestion), use a non-empty sentence starter when the reasoning operation would benefit from scaffolding — rank-1 findings should not be the ones with the least support.
```

**Rationale:** Students receiving their most critical revision suggestion should not get the least structural support. Rank is implicit from list position (index 0 = rank 1), so no schema change needed.

---

### 4. Finding 8: Claim Anchoring (CONFIRMED systemic - 58% of corpus)

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, new CLAIM ANCHORING section

**Change:** Any "why this matters" phrase must be completed with a prepositional phrase anchoring to the specific claim from the student's draft.

**Implementation:**
```
CLAIM ANCHORING: Any phrase equivalent to "why this matters" or "why that helps" in why_it_matters or revision_action must be completed with a prepositional phrase anchoring to the specific claim from the student's draft. You receive the full draft via current_draft and should extract the student's claim text directly from it. Never output "why that matters," "why this helps," or "why this is important" without a completing clause that names the specific claim, such as "why that supports your argument that the school should start a garden" or "why that connects to your point about students needing more activities."
```

**Rationale:** This was the most widespread quality gap in the corpus. Generic "why that matters" without a referent is not actionable for students who don't already know what it matters for. Support agent has access to full draft text via `state['writing']`.

---

### 5. Finding 1: Instruction Decomposition (scenario-specific but valid fix)

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, new INSTRUCTION CLARITY section

**Change:** Dense multi-operation instructions should be split into sequenced short commands with one action per sentence.

**Implementation:**
```
INSTRUCTION CLARITY: Keep revision_action steps short and concrete. When multiple cognitive operations are needed (locate, reason, connect), split them into sequenced short commands with one action per sentence. Remove gerund subjects from instructions. For example, instead of "After the survey sentence, add one or two sentences that explain what the 62% result suggests about students and why that supports starting a garden," use: "Find the sentence with 62%. After it, write one or two sentences. First: explain what 62% saying yes tells us about students at this school. Then: explain why that is a reason to start a garden."
```

**Rationale:** While only 4% of corpus showed this pattern (scenario-specific), splitting complex instructions into sequenced commands reduces cognitive load for EL students.

---

### 6. Starter Shape Alignment Guidance

**Location:** `agents/prompts.py` - SUPPORT_ROUND_PROMPT, HINT AUTHORSHIP BOUNDARY section

**Change:** Added explicit guidance on matching starter shape to reasoning operation type.

**Implementation:**
```
The starter must match the reasoning operation: causal/explanatory moves use '____ because ____.' or 'This evidence/detail matters because ____.'; conditional/temporal use 'When ____, ____.'; source-based use 'According to the passage, ____.'.
```

**Rationale:** While full implementation requires Track B Coordinator schema changes (reasoning operation type field), this prompt guidance prepares Support agent to select appropriate starters when that field becomes available.

---

## Token Cost Impact

Based on current Support agent outputs averaging 800-1200 tokens per round:

- **F11 (Step 0 addition):** +60-100 tokens/round
- **F8 (claim anchoring):** +30-60 tokens/round  
- **F12 (step reordering):** No net token change
- **F13 (rank-1 starter requirement):** +1-3 tokens/round average

**Total Track A increase:** +90-165 tokens per round (+8-14% over baseline)

At current evaluation scale (32 scenarios × 3 rounds = 96 rounds), Track A changes add ≈9-16K tokens total. At DeepSeek pricing, this is negligible cost increase.

---

## Testing Strategy

### Unit Tests Required
1. Validate `HintOutput` schema enforces minimum 3 steps
2. Validate sentence starters remain within approved list
3. Validate Support agent preserves Coordinator references exactly

### Integration Tests Required
1. Run against garden_source_accurate scenario to verify F11/F12 improvements
2. Run against acceptance scenarios with warrant gaps to verify F8 claim anchoring
3. Compare rank-1 vs rank-2/3 starter presence rates

### Evaluation Required
Before claiming pedagogical effectiveness:
1. Re-run `scripts/evaluate_v3.py --scenario-set acceptance --modes nonthinking`
2. Compare v3.4.1 outputs against v3.4.0 corpus for:
   - Step 0 presence (target: 100% vs baseline 0%)
   - Concrete-first steps (target: >50% vs baseline 9%)
   - Rank-1 starter presence (target: >70% vs baseline 29%)
   - Claim anchoring (target: >80% vs baseline 42%)

---

## Track B Dependencies (Not Yet Implemented)

The following findings require Coordinator schema changes and are NOT included in this implementation:

### F2: Source Accuracy Error Detection
**Requires:** Coordinator schema to distinguish warrant gap caused by source mischaracterization from pure warrant gap
**Status:** Deferred to Track B

### F6: Finding Severity Tiers
**Requires:** New Coordinator schema field `finding_severity` with values: `accuracy` > `reasoning` > `development`
**Status:** Deferred to Track B

### F7: Reasoning Operation Classification
**Requires:** New Coordinator schema field `reasoning_operation_type` with values: `causal`, `sequential`, `source_based`, `concessive`, `summary`, `conditional`
**Status:** Deferred to Track B - prompt guidance added as preparation

### F10: Conceptual Conflation Detection
**Requires:** New Coordinator finding subtype `concept_substitution` distinct from `missing_warrant`
**Status:** Hypothesis - needs more corpus evidence before implementation

---

## Hypotheses NOT Implemented (Pending Pilot Evidence)

### F3: Model Sentences for Structural Starters
**Status:** HYPOTHESIS - plausible for EL students but competing EL frameworks suggest topic-adjacent frames may be better for lower-proficiency students. Needs pilot with ELPAC 1-2 vs 3-4 students.

### F4: Vocabulary Sequencing
**Status:** HYPOTHESIS - likely a UI rendering order change rather than prompt change. Needs UI implementation.

### F9: Register Mismatch
**Status:** Scenario-specific, low priority. "Again and again" → "regularly" is a minor polish fix.

---

## Validation Criteria

### Success Metrics (from corpus analysis)
1. **Step 0 presence:** Increase from 0% to 100% of hints
2. **Concrete-first steps:** Increase from 9% to >70% of procedural chains
3. **Rank-1 starters:** Increase from 29% to >70% presence
4. **Claim anchoring:** Increase from 42% to >80% of "why it matters" phrases

### Regression Threshold
No more than 10% of acceptance scenarios (3/32) show quality degradation. Zero tolerance for accuracy-tier regressions.

### Simulation Consistency
Track A changes validated against simulation evidence (SIMULATION_EVIDENCE_REPORT.md):
- Jordan session: F7 mismatch consistent with corpus
- Sam session: F9 register issue consistent with corpus
- Maya/Jordan/Sam: F11 absence consistent with corpus (all three personas had no Step 0)

---

## Next Steps

1. **Immediate:** Run full test suite to validate schema changes don't break existing functionality
2. **Short-term:** Run acceptance evaluation to measure corpus-level improvements
3. **Medium-term:** Implement Track B Coordinator schema changes for F2/F6/F7
4. **Long-term:** Pilot F3 (model sentences) with actual students before adding to system

---

## Files Modified

1. `agents/prompts.py` - SUPPORT_ROUND_PROMPT updates
2. `agents/support_agent.py` - HintOutput schema update (min_length: 2→3)

---

## Commit Message

```
V3.4.1: Implement Track A feedback quality improvements

Based on corpus analysis of 68 candidates across 30 rounds (acceptance 
evaluation v3.4.0), implement Support agent prompt improvements with 
strongest systemic evidence:

- F11: Step 0 concept restatement (91% corpus gap)
- F8: Claim anchoring (58% corpus gap)
- F12: Concrete-first procedural steps (91% abstract-first pattern)
- F13: Rank-1 starter requirement (57% lack starters, 29% rank-1)
- F1: Instruction decomposition (scenario-specific but valid)

Schema: Increase HintOutput.steps min_length from 2 to 3 to enforce 
Step 0 + procedural chain.

Prompt: Add CLAIM ANCHORING and INSTRUCTION CLARITY sections, expand 
HINT AUTHORSHIP BOUNDARY with layered confusion-type guidance.

Token cost: +90-165 tokens/round (+8-14% over baseline).

Track B Coordinator schema changes (severity tiers, reasoning operation 
types) deferred pending validation of Track A improvements.

See FEEDBACK_IMPLEMENTATION_V3_4_1.md for full implementation notes.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
