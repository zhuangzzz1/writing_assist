# V3 Improvement Investigation Evidence Index

**Date:** 2026-11-10  
**Purpose:** Preserve a structured, reproducible evidence base for future V3 improvement investigation and analysis  
**Scope:** Local synthetic prototype only  
**Primary machine-readable artifact:** `data/evidence/v3_investigation_manifest_20261110.json`

## 1. What Was Collected

The manifest consolidates the latest outcomes without making new model calls:

- **40 integrity-hashed artifacts**, including evidence JSON, SQLite databases, screenshots, fixtures, the outcome report, the external improvement review, the educator protocol, and the changelog.
- **All 30 acceptance-scenario outcomes**, using the corrected full run and targeted correction artifacts for #7 and #24.
- **Three paired thinking/non-thinking artifacts**, including the original baseline and two later repetitions.
- **Per-scenario content evidence:** routes, genres, candidate titles/references, source limitations, selected-goal observations, regressions, final improvements, errors, and repair diagnostics.
- **Operational evidence:** calls, repairs, token usage, model latency, graph time, service time, and browser click-to-render time.
- **Browser/accessibility evidence:** keyboard steps, focus recovery, 1440px/1920px layouts, 200% zoom, the capped 400% attempt, and remaining screen-reader work.
- **Eight prioritized research leads** with evidence references and suggested next steps.

No raw hidden reasoning is included. The manifest contains final structured responses and evaluation-only final-response repair diagnostics with synthetic content.

## 2. Current Configuration

| Setting | Value |
| --- | --- |
| Model | `deepseek-flash` |
| Student runtime | Explicit non-thinking |
| Non-thinking temperature | 0 |
| Thinking comparator | Explicit controlled evaluation; temperature omitted |
| Prompt version | `v3.3.0` |
| Schema version | `v3.2.1` |
| Acceptance fixture | `v3.2.1` |
| Student presets fixture | `v3.1.0` |
| Deployment | None; local only |

## 3. Evidence Map

| Material | Primary paths |
| --- | --- |
| Consolidated investigation manifest | `data/evidence/v3_investigation_manifest_20261110.json` |
| Original matched baseline | `data/evidence/v3_paired_evaluation_20261110T094344Z.json` |
| New paired core 1 | `data/evidence/v3_core_evaluation_20261110T161430Z.json` |
| New paired core 2 | `data/evidence/v3_core_evaluation_20261110T162342Z.json` |
| Corrected 30-scenario run | `data/evidence/v3_acceptance_evaluation_20261110T160932Z.json` |
| Three-goal targeted correction | `data/evidence/v3_acceptance_scenario_07_evaluation_20261110T162320Z.json` |
| Non-obscuring-mechanics targeted correction | `data/evidence/v3_acceptance_scenario_24_evaluation_20261110T162337Z.json` |
| Browser/timing/accessibility evidence | `data/evidence/v3_improvement_browser_20261110.json` |
| Baseline outcomes and improvement addendum | `V3_OUTCOMES_REPORT.md` |
| Change history | `CHANGELOG.md` |
| Prepared educator gate | `EDUCATOR_REVIEW_PROTOCOL.md` |

Earlier artifacts remain in the manifest with explicit historical roles. They are not presented as current-output evidence.

## 4. High-Value Findings to Investigate

### 4.1 Model configuration and variability

Non-thinking used fewer tokens and substantially less cumulative model latency in all three pairs:

| Pair | Mode | Calls | Repairs | Total tokens | Model latency |
| --- | --- | ---: | ---: | ---: | ---: |
| Baseline | Thinking | 17 | 2 | 68,407 | 246.2s |
| Baseline | Non-thinking | 15 | 0 | 36,340 | 64.2s |
| Repetition 1 | Thinking | 16 | 1 | 65,479 | 190.3s |
| Repetition 1 | Non-thinking | 17 | 2 | 43,443 | 55.4s |
| Repetition 2 | Thinking | 16 | 1 | 61,719 | 173.4s |
| Repetition 2 | Non-thinking | 16 | 1 | 40,971 | 55.2s |

Neither mode had a stable zero-repair rate. Investigate content quality and repair causes separately rather than treating repairs as a quality score.

### 4.2 Teacher-framework consistency

Use scenario #4 across all three pairs to examine RACES carry-through. Non-thinking consistently addressed the full structure in the new pairs. Thinking covered it in one pair but omitted explicit Restate/Answer guidance in another.

### 4.3 Claim-ownership diagnosis

Use scenario #3 to compare whether each output distinguishes the author's position from the student's own claim. Thinking caught this in the baseline but not the first new pair; non-thinking caught it in the second new pair. It is not a reliable mode-specific advantage in this sample.

### 4.4 Revision honesty and carry-forward

The manifest includes structured observations for:

- Three-goal revision (#7)
- One goal across two rounds (#8)
- Organizational regression (#9)
- One-word and punctuation-only edits (#14)
- Two deferred goals (#15)
- Repeated identical submissions (#28)

Use these to investigate fabricated improvement, neutral carry-forward language, regression visibility, and attempt assumptions.

### 4.5 Semantic scaffold safety

Use scenarios #14, #16, and #21 plus repair diagnostics to investigate:

- Assigned-topic content in frames or revision actions
- Vocabulary that supplies content answers
- Structured vocabulary objects that trigger schema repairs
- Whether hints guide thinking without producing a paste-ready response

Use full student context and both PRD authorship checks. A model-generated self-assessment flag is not a substitute for review.

### 4.6 Grade, length, targeting, and register

Scenarios #22–#27 provide evidence for short grade-5 feedback, a 411-word informational essay, non-obscuring language errors, weak middle paragraphs, informal narrative voice, and register shifts. Compare candidate references and density rather than relying only on route success.

### 4.7 Accessibility and interaction recovery

The browser pass verified keyboard navigation through entering Revise, but not a complete keyboard-only final loop. It also verified 200% zoom; the 400% request was capped at 3×. Actual screen-reader output remains untested.

### 4.8 Educator gate

`EDUCATOR_REVIEW_PROTOCOL.md` is ready for three qualified educators. Recruitment, assessments, and the gate decision remain open. Passing the gate would not by itself authorize student contact.

## 5. Using the Manifest Programmatically

The manifest is ordinary JSON. Example:

```python
import json
from pathlib import Path

manifest = json.loads(
    Path("data/evidence/v3_investigation_manifest_20261110.json").read_text()
)

# Latest targeted evidence for scenario #7
scenario_7 = next(
    item
    for item in manifest["acceptance"]["scenario_outcomes"]
    if item["scenario_number"] == 7
)
print(scenario_7["candidate_titles"])
print(scenario_7["revision_observations"])

# Repair categories for future schema/prompt investigation
print(manifest["repair_patterns"]["counts_by_category"])

# Repeated model metrics
for pair in manifest["paired_core"]:
    print(pair["timestamp_utc"])
    for mode, result in pair["modes"].items():
        print(mode, result["token_usage"], result["model_latency_ms"])
```

The original evidence JSON remains necessary when full model prompts, structured states, or revision snapshots are needed. The manifest is an indexed analysis layer, not a replacement for those artifacts.

## 6. Integrity and Reproducibility

- Every artifact entry includes byte size and a SHA-256 hash of its contents at manifest generation.
- SQLite entries list available WAL/SHM sidecars separately. Use SQLite with available WAL state when inspecting a database.
- The manifest does not include its own hash in `artifacts`.
- Manifest size: **228,967 bytes**.
- Manifest SHA-256: `ffdb78e3ed878e773b67b17f9551d300a2e1cde9332c90a17bda376a882fc917`.
- The manifest is a snapshot, not an automatically updating index. Regenerate or rebuild it when new evidence is added.

To verify an artifact manually:

```python
import hashlib
from pathlib import Path

artifact = Path("data/evidence/v3_core_evaluation_20261110T162342Z.json")
print(hashlib.sha256(artifact.read_bytes()).hexdigest())
```

Compare the result with the corresponding entry in `manifest["artifacts"]`.

## 7. Evidence Boundaries

- All writing is synthetic. Do not add real student work or identifying information.
- All analysis is local and limited to the recorded scenarios.
- No pedagogical effectiveness, educator approval, learner outcome, motivation, engagement, or retention claim is supported.
- No V3 deployment or production-readiness claim is supported.
- The full set of 30 model scenarios is not equivalent to 30 complete browser walkthroughs.
- Future student contact requires separate privacy, safety, consent, institutional, and operational review.
