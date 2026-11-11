# Feedback Quality Implementation V3.5.0 — Track B

**Implementation Date:** 2026-11-11
**Based on:** FEEDBACK_QUALITY_IMPROVEMENT_PLAN.md Track B
**Status:** Implemented
**Version:** v3.5.0 (schema + prompt)

---

## Overview

Track B adds Coordinator schema fields for finding severity classification and reasoning operation types, enabling:
1. **Severity-based ranking** — accuracy-tier findings (fabricated content, source errors) rank first
2. **Reasoning operation classification** — guides appropriate sentence starter selection by the Support agent
3. **Deterministic within-tier ordering** — preserves pedagogical priority when multiple findings share the same severity

Track A (v3.4.1) implemented Support prompt constraints without schema changes. Track B adds the upstream Coordinator schema fields that Track A prepared for.

---

## Changes Implemented

### 1. Finding Severity Classification (CONFIRMED systemic - Priority 3)

**Schema Change:** Added required `finding_severity` field to `IssueOutput` in `agents/assessment_coordinator.py`

```python
finding_severity: Literal["accuracy", "reasoning", "development"]
```

**Severity Tiers:**
- **accuracy**: factual errors, fabricated/invented content, source misrepresentation
- **reasoning**: warrant gaps, underdeveloped logic, missing connections
- **development**: elaboration, specificity, structure

**Ranking Implementation:**
Added `_rank_by_severity()` method to `AssessmentCoordinator` that sorts issues by severity tier while preserving within-tier order. Accuracy-tier findings rank first in Round 1 regardless of which goal they map to.

**Prompt Guidance:** Added FINDING SEVERITY AND RANKING section to `COORDINATOR_ROUND_PROMPT`:
```
Every issue requires a finding_severity classification: accuracy (factual errors, 
fabricated/invented content, source misrepresentation), reasoning (warrant gaps, 
underdeveloped logic, missing connections), or development (elaboration, specificity, 
structure). Accuracy-tier findings should rank first in Round 1 regardless of which 
goal they map to. When multiple findings share the same severity, order them by 
pedagogical priority within that tier. A student who completes selected goals without 
addressing fabricated evidence has not fixed the most serious problem.
```

**Rationale:** Corpus analysis showed no `issue_type` field and no distinction between fabricated content and simple warrant gaps. Both were categorized as `evidence_elaboration`. A student could complete all revision suggestions without addressing invented evidence. This was Finding 6 (Priority 3) in the improvement plan.

---

### 2. Reasoning Operation Classification (CONFIRMED systemic - Priority 4)

**Schema Change:** Added optional `reasoning_operation` field to `IssueOutput` with default value `"none"`

```python
reasoning_operation: Literal[
    "causal",
    "sequential", 
    "source_based",
    "concessive",
    "summary",
    "conditional",
    "none",
] = "none"
```

**Classification Types:**
- **causal**: explaining why/how something causes an effect
- **sequential**: ordering events or steps
- **source_based**: citing or interpreting passage content
- **concessive**: acknowledging counterarguments
- **summary**: concluding or synthesizing
- **conditional**: describing conditions and outcomes
- **none**: no structural starter needed

**Prompt Guidance:** Added REASONING OPERATION CLASSIFICATION section to `COORDINATOR_ROUND_PROMPT`:
```
When a finding would benefit from structural scaffolding, classify its 
reasoning_operation to guide appropriate sentence starter selection: causal 
(explaining why/how something causes an effect), sequential (ordering events or 
steps), source_based (citing or interpreting passage content), concessive 
(acknowledging counterarguments), summary (concluding or synthesizing), conditional 
(describing conditions and outcomes), or none (no structural starter needed). This 
classification helps match the starter shape to the reasoning move. For example, a 
causal explanation benefits from "____ because ____." while a source-based claim 
benefits from "According to the passage, ____."
```

**Support Agent Integration:** Updated `SUPPORT_ROUND_PROMPT` with STARTER SELECTION FROM REASONING OPERATION section that maps each reasoning operation type to appropriate sentence starters:

- **causal** → `____ because ____.` or `This evidence/detail matters because ____.`
- **sequential** → `After ____, ____.` or `Before ____, ____.`
- **source_based** → `According to the passage, ____.`
- **concessive** → `One concern is that ____; however, ____.` or `Although ____, ____.`
- **summary** → `In sum, ____.` or `In conclusion, ____.`
- **conditional** → `When ____, ____.`
- **none** → leave `sentence_starter` empty

**Rationale:** Corpus analysis confirmed 2 hard mismatches where causal/explanatory operations received `When ____, ____.` (conditional/temporal) starters in separate scenarios (acceptance_01, acceptance_21). The starter shape must encode the reasoning operation. This was Finding 7 (Priority 4) in the improvement plan.

---

## Test Coverage

Added 5 new tests in `tests/test_agents.py`:

1. **`test_accuracy_tier_findings_rank_first_regardless_of_goal`** - Verifies that accuracy findings rank first even when submitted in non-severity order (development, reasoning, accuracy)

2. **`test_reasoning_operation_classification_guides_starter_selection`** - Confirms that causal operations receive appropriate "because" starters

3. **`test_finding_severity_is_required_and_validated`** - Ensures missing `finding_severity` triggers repair and validates all three severity values

4. **`test_reasoning_operation_defaults_to_none_when_not_specified`** - Verifies default value of "none" when field is omitted

5. **`test_multiple_accuracy_findings_preserve_pedagogical_order`** - Confirms within-tier ordering is preserved when multiple findings share the same severity

All 219 tests pass (up from 214 baseline).

---

## Version Updates

Updated `agents/utils.py`:
```python
PROMPT_VERSION = "v3.5.0"
SCHEMA_VERSION = "v3.5.0"
```

Updated `tests/helpers.py` fixture factory to include new required fields:
```python
issue = {
    "goal_id": goal_id,
    "category": "evidence_elaboration",
    "finding_severity": "reasoning",  # NEW
    "reasoning_operation": "none",    # NEW
    "description": "The connection needs more explanation.",
    # ... rest of fields
}
```

---

## Backward Compatibility

**Breaking Change:** The `finding_severity` field is **required**. All Coordinator responses must classify every issue by severity tier.

**Migration Path:**
- Existing evaluation databases with v3.4.0/v3.4.1 schemas are incompatible
- Re-run evaluations with v3.5.0 to capture severity classifications
- The `reasoning_operation` field has a default value (`"none"`) for backward compatibility during repair

**Repair Behavior:**
- Missing `finding_severity` triggers bounded repair (one correction attempt)
- Missing `reasoning_operation` defaults to `"none"` without repair
- Invalid severity values trigger validation error and repair

---

## Token Cost Impact

Based on current Coordinator outputs averaging 1200-1500 tokens per assessment:

- **Severity classification**: +20-40 tokens per issue (requires categorical judgment + brief rationale in coordinator_reasoning)
- **Reasoning operation classification**: +10-20 tokens per issue when not "none"
- **Total per assessment**: +60-120 tokens for 2-issue rounds, +150-300 tokens for 5-issue rounds

At current acceptance evaluation scale (32 scenarios, average 2.1 issues per round):
- Baseline: ~40K tokens for 32 initial assessments
- Track B: +4-6K tokens (~10-15% increase)

At DeepSeek pricing this remains negligible. The pedagogical value of severity-based ranking (fabricated content surfaces first) justifies the small token increase.

---

## Validation Criteria

### Success Metrics (from improvement plan)
1. **Accuracy-tier ranking**: 100% of accuracy findings rank before reasoning/development findings
2. **Within-tier ordering**: Preserved for multiple findings in the same tier
3. **Reasoning operation classification**: No causal operations receive conditional starters
4. **Schema compliance**: Zero persistent validation failures on required `finding_severity` field

### Regression Threshold
- No more than 10% of acceptance scenarios (3/32) show quality degradation
- Zero tolerance for accuracy-tier findings ranked below development-tier findings
- Zero tolerance for causal findings receiving `When ____, ____.` starters

### Real-Model Validation Required
Run acceptance evaluation before claiming pedagogical effectiveness:
```bash
python scripts/evaluate_v3.py --scenario-set acceptance --modes nonthinking
```

Compare v3.5.0 outputs against v3.4.1 baseline for:
- Accuracy-tier ranking (target: 100% ranked first)
- Reasoning operation alignment with starter shapes (target: >90% correct)
- No regressions in scenarios where current order is pedagogically appropriate

---

## Known Limitations and Open Questions

### L1: Corpus evidence is from argument genre only
The corpus analysis that identified severity gaps and reasoning operation mismatches used mostly argument drafts. Narrative and informational findings may show different patterns.

**Mitigation:** Monitor v3.5.0 evaluation results across all three genres. If narrative conditional/temporal findings receive incorrect classification, add genre-specific guidance to the Coordinator prompt.

### L2: Reasoning operation classification accuracy depends on model judgment
Unlike exact reference validation, reasoning operation classification involves interpretive judgment. The Coordinator may misclassify operations.

**Mitigation:** Track classification accuracy in acceptance evaluation. If <90% correct, add explicit examples to the Coordinator prompt for each operation type.

### L3: Within-tier ordering is deterministic, not adaptive
When multiple accuracy findings exist, the current implementation preserves submission order. It does not distinguish fabrication from mischaracterization within the accuracy tier.

**Future work:** Consider adding `accuracy_subtype` if pilot evidence shows pedagogical value in ranking fabrication before mischaracterization.

### L4: Source accuracy detection still requires source material
Track B adds severity classification but does not solve Finding 2 (source accuracy error not surfaced when source is missing). That requires extending source availability detection.

**Future work:** Track C could add optional source passage input and compare it against draft claims, flagging mischaracterizations as accuracy-tier findings.

---

## Track B Dependencies Satisfied

Track A (v3.4.1) prepared for Track B by:
1. Adding claim anchoring prompt guidance (uses severity ranking output)
2. Adding rank-1 starter requirement (now informed by reasoning operation classification)
3. Adding starter shape alignment guidance (now driven by reasoning_operation field)

Track B delivers the upstream schema fields that enable those Track A features to work correctly.

---

## Relationship to Improvement Plan Findings

| Finding | Priority | Track B Implementation | Status |
|---------|----------|----------------------|--------|
| F6: Fabrication detection | 3 | `finding_severity` field with accuracy tier | ✅ COMPLETE |
| F7: Starter shape alignment | 4 | `reasoning_operation` field + Support prompt mapping | ✅ COMPLETE |
| F2: Source accuracy surfacing | 6 | Deferred - requires source comparison logic | ⏸️ NOT IMPLEMENTED |
| F10: Conceptual conflation | 11 | Hypothesis - needs more evidence | ⏸️ NOT IMPLEMENTED |

---

## Next Steps

1. **Immediate:** Run `pytest` to verify all 219 tests pass (✅ DONE)
2. **Short-term:** Run acceptance evaluation with v3.5.0 and compare against v3.4.1 baseline
3. **Medium-term:** Analyze evaluation outputs for severity ranking accuracy and reasoning operation classification quality
4. **Long-term:** Pilot Track B changes with actual students to validate pedagogical impact before claiming effectiveness

---

## Files Modified

1. `agents/assessment_coordinator.py`:
   - Added `finding_severity` and `reasoning_operation` fields to `IssueOutput` schema
   - Added `_rank_by_severity()` method
   - Updated `_round_values()` to apply severity-based ranking

2. `agents/prompts.py`:
   - Added FINDING SEVERITY AND RANKING section to `COORDINATOR_ROUND_PROMPT`
   - Added REASONING OPERATION CLASSIFICATION section to `COORDINATOR_ROUND_PROMPT`
   - Updated JSON schema documentation to include new fields
   - Updated STARTER SELECTION FROM REASONING OPERATION section in `SUPPORT_ROUND_PROMPT`

3. `agents/utils.py`:
   - Bumped `PROMPT_VERSION` and `SCHEMA_VERSION` to `v3.5.0`

4. `tests/helpers.py`:
   - Updated `issue_for()` factory to include `finding_severity` and `reasoning_operation` defaults

5. `tests/test_agents.py`:
   - Added 5 new tests for severity ranking and reasoning operation classification

---

## Commit Message

```
V3.5.0: Implement Track B feedback quality improvements (severity + reasoning operation)

Add Coordinator schema fields for finding severity classification and reasoning 
operation types, enabling severity-based ranking and appropriate sentence starter 
selection.

Schema changes:
- Add required `finding_severity` field: accuracy | reasoning | development
- Add optional `reasoning_operation` field with default "none"
- Implement `_rank_by_severity()` to rank accuracy findings first

Prompt updates:
- Add FINDING SEVERITY AND RANKING section to Coordinator prompt
- Add REASONING OPERATION CLASSIFICATION guidance for Coordinator
- Update Support prompt STARTER SELECTION to map operation types to starters

Tests:
- Add 5 new tests for severity ranking and reasoning operation classification
- All 219 tests pass (up from 214 baseline)

Based on corpus analysis (FEEDBACK_QUALITY_IMPROVEMENT_PLAN.md):
- F6: Fabrication detection (Priority 3) - no accuracy tier existed
- F7: Starter shape alignment (Priority 4) - causal moves got conditional starters

Breaking change: `finding_severity` is required. Re-run evaluations with v3.5.0.

Token cost: +60-300 tokens per assessment depending on issue count (+10-15%).

See FEEDBACK_IMPLEMENTATION_V3_5_0_TRACK_B.md for full implementation notes.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
