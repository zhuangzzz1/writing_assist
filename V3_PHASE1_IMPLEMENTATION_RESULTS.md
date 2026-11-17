# V3 Phase 1 Implementation Results

## 1. Status and evidence boundaries

Phase 1 of `V3_PHASED_IMPROVEMENT_PLAN.md` is implemented as an **evaluation-only candidate**. The evaluator arm is `phase1`, with prompt `v3.9.2-phase1` and schema `v3.9.0`. The promoted student runtime remains `v3.8.3`/`v3.8.0`; no deployment or runtime promotion occurred.

The historical comparison reference remains `V3_8_3_COMPLETE_RUN_EXTERNAL_REVIEW.md` and its identified source records. No new historical-baseline calls are required or used as Phase 1 controls. Historical comparisons are semantic and draft-matched, never exact-output reproduction requirements. Probes outside that run have no historical control. Candidate runs use the same configured `deepseek-flash` thinking/`high` mode but add the Phase 1 schema/payload and, for later controlled revisions, different evaluator revision numbers as documented below. The pre-existing working-tree client change that omits `max_tokens` was preserved and applies to these candidate calls; it is not attributed to the Phase 1 prompt.

The complete mocked suite passes. This establishes implementation/contract coverage only. The Phase 1 semantic exit gate is **not yet passed**: the named owner or appointed reviewer must review complete development and held-out transfer outputs using `EDUCATOR_REVIEW_PROTOCOL.md`. LLM-assisted screening does not substitute for that review, educator approval, or learner-outcome evidence.

## 2. Implemented candidate contract

- Strengthened whole-draft triage after accuracy and supported student concerns: meaning-blocking clarity/missing reasoning links, organization/reader connection, recognizable language patterns, then optional polish. Meaning-obscuring language remains a clarity priority. The five-issue maximum and stable accuracy partition remain unchanged. Meaningful overflow belongs in concise Coordinator rationale and cannot justify direct response.
- Added independent `goal_outcome` and `narrowing` dimensions while retaining the existing text-observation status. Added exact previous-draft deletion evidence and assignment/teacher/framework requirement evidence.
- Added deterministic observation/outcome/narrowing/carry-forward/route checks, including same-ID live candidates, required task-alignment issues, framework links, direct-response restrictions, and discretionary closure without completion claims.
- Extended Support and direct response with exact preservation of status, outcome, narrowing, evidence, requirement basis, and carry-forward. Support may paraphrase only the observation.
- Added neutral student-facing outcome/narrowing labels and evidence. “Fully addressed” is explicitly bounded to the selected goal in this draft, not mastery.
- Distinguished no meaningful issue, meaningful work remaining with student-controlled Finish, and optional-only direct response. Optional polish is bounded to zero to three exact located current-draft entries, has no revision candidates, and is empty on other routes.
- Persisted the new fields in round JSON and matching revision-history records. Older records leave the fields missing/unknown rather than receiving inferred outcomes.
- Did not add Phase 2 multi-location batching or per-round bounded history, did not auto-select carried goals, and did not change Final prompts, interpretation, or deterministic Final consistency semantics.

Primary implementation locations are `agents/assessment_coordinator.py`, `agents/support_agent.py`, `agents/prompts.py`, `langgraph_core/state.py`, `langgraph_core/nodes.py`, `langgraph_core/revision.py`, and `ui/components.py`.

## 3. Evaluation setup and leakage controls

`test_cases/v3/phase1_development.json` (`v3.9.0-phase1-development.2`) contains 16 controlled initial/revision probes:

- The preserved garbage-system original and seven revisions, including transport deletion and both explicitly partial agreement revisions.
- Snapshot 7 as both a revision and an independent whole-draft probe.
- Corrected sentence-boundary and clarified-reference counterfactuals.
- Argument/source initial, independent discretionary narrowing, and independent required deletion cases.
- Informal narrative initial and revision cases.

`test_cases/v3/phase1_transfer.json` (`v3.9.0-phase1-transfer.1`) reserves eight unrelated cases: an informational process initial/revision pair, strong no-issue and optional-only informational controls, unrelated argument/source initial/revision cases, and unrelated narrative initial/revision cases. No historical control is claimed for these cases. The CLI requires `--candidate-frozen` for transfer. If transfer outputs drive candidate changes, the set must be reclassified as development data and new held-out cases are required.

Fixture annotations distinguish pending reviewer-confirmed issues, potential anchors requiring judgment, optional polish, and unsupported concerns. Empty reviewer-confirmed lists are intentional until named human review; potential anchors are not mandatory model findings or candidate quotas.

Later garbage-system controlled probes persist only the original and immediately previous draft, so evaluator `revision_number` differs from the historical workflow number. Fixture lineage records the corresponding historical snapshot and this payload difference. A read-only source-database check confirmed exact text for all eight `garbage_0`–`garbage_7` snapshots and exact selected-goal actions/references for every `.2` controlled garbage-system revision payload. The mutable database is not substituted for the stable review packet as historical evidence.

The mocked suite scans production prompts, routing/validation, nodes, and ordinary UI code for distinctive development/transfer vocabulary. A match is a leakage diagnostic, not a keyword-only semantic quality judgment.

## 4. Evaluator scope and diagnostics

`scripts/evaluate_v3.py` adds:

- `--experiment-arm phase1` with versioned candidate prompts/schema.
- `phase1_development` and `phase1_transfer` scenario sets.
- Required `--candidate-frozen` acknowledgement for reserved transfer.
- Explicit `--skip-final`, restricted to Phase 1 round-only regression runs and recorded in evidence.
- Descriptive goal-outcome, narrowing, carry-forward, optional-polish, and stopping/support-route counts.
- Existing deduplicated repair, invalid-response, exact-reference normalization, token, latency, and stable-database diagnostics.

The acceptance regression scope is scenarios 1–3, 10, 23, and 26 with `--skip-final`; it is not full acceptance and does not evaluate Phase 4 Final behavior. No full adaptive loop belongs to Phase 1.

Commands are documented in `README.md`.

## 5. Mocked verification

Final full-suite result:

```text
438 passed in 6.20s
```

Coverage includes the permitted/rejected outcome matrix, exact deletion and requirement evidence, framework links, carry-forward identity, direct-response prevention, optional polish validation and boundaries, Coordinator-to-Support preservation, direct-response bypass, neutral UI rendering, round/history persistence and reopen, older history records, no automatic goal selection, evaluator versions/diagnostics, fixture integrity, counterfactual support removal, and runtime fixture-leakage scanning.

The pre-existing edits in `agents/utils.py` and `tests/test_api_client.py` were preserved. They are separate from the Phase 1 candidate.

## 6. Real-model outcomes

### Development trial 1 — `.1` fixture, `v3.9.0-phase1`

Artifact: `data/evidence/v3_phase1_development_phase1_evaluation_20261117T052835Z.json`.

Configuration: `deepseek-flash`, thinking enabled, reasoning effort `high`, schema `v3.9.0`, fixture `v3.9.0-phase1-development.1`. The run recorded 16 scenarios, one API connection error, 29 attempted model calls with 28 successful-response logs, zero schema repairs, zero reference normalizations, 280,809 observed total tokens, and 700.878 seconds of recorded model latency. The Snapshot 7 independent whole-draft probe failed before assessment with `APIError: Could not connect to DeepSeek.` This operational failure is preserved rather than replaced by a fabricated output.

Positive observations requiring named-review confirmation:

- The transport deletion was represented as `specific_improvement` plus `not_addressed` and `discretionary`, with no carry-forward.
- Both explicitly partial agreement revisions received `partially_addressed` and same-ID live candidates.
- The corrected boundary counterfactual did not retain the corrected boundary anchors; the clarified-reference counterfactual did not retain the clarified dewatering/filter/leachate-reference anchors.
- Narrative probes preserved informal voice and did not demand citations, claims, or counterclaims.

Negative/mixed observations:

- Snapshot 7 revision returned optional-only `direct_response` after the selected agreement correction. It classified a remaining comma splice and repeated word-form patterns as polish and overlooked other potential meaningful whole-draft needs. This is not a Phase 1 semantic pass.
- The required survey deletion kept a live same-ID task-alignment issue but incorrectly returned `narrowing=none` with empty deletion/requirement evidence.
- The argument/source initial probe treated a student reason as unsupported because its wording was not stated in the source, without adequately recognizing source-supported student reasoning. This requires semantic correction, not a looser source-accuracy rule.
- Some bounded selected goals were broadened into whole-pattern outcomes. The `.1` controlled payloads omitted original revision actions, contributing to scope ambiguity.

Development response, not a claimed improvement: fixture `.2` restores every controlled garbage-system revision action/reference exactly from the preserved snapshots. Prompt `v3.9.1-phase1` adds generic selected-goal scope, required-deletion, source-bound student-reasoning, and final whole-draft/optional-polish audits. It explicitly prohibits downgrading recognizable language patterns or reader/meaning issues to optional polish merely to stop. The complete `.2` development run must establish actual outcomes; reserved transfer outputs were not used for these revisions.

### Development trial 2 — `.2` fixture, `v3.9.1-phase1`

Artifact: `data/evidence/v3_phase1_development_phase1_evaluation_20261117T054829Z.json`.

All 16 scenarios completed with 31 attempted/logged calls, zero errors, zero schema repairs, zero reference normalizations, 353,477 observed tokens, and 955.374 seconds of recorded model latency.

Positive observations requiring named-review confirmation:

- Snapshot 7 revision changed from optional-only direct response to Support; the independent Snapshot 7 probe returned two process-link issues and two language-pattern issues.
- The required survey deletion now has `not_addressed`, `required`, exact deleted-text evidence, exact assignment requirement evidence, and a same-ID live task-alignment candidate.
- The unsupported source-wording/task-alignment finding disappeared from the argument/source initial probe; the remaining finding concerns a bounded survey-to-claim warrant.
- Location-bounded sorting, recycling, and revision-5 goals were fully addressed with distinct current issues for other draft work. Both original multi-location partial-agreement scopes remained `partially_addressed` with same-ID carry-forward.
- Transport and friend-example deletions remained discretionary `not_addressed`, not full completion. Corrected counterfactuals again did not retain their corrected anchors.

Remaining negative/mixed observations:

- Snapshot 7 revision still returned only one sentence-boundary issue. Its rationale called non-count/word-form work overflow despite unused five-issue capacity and omitted supported process/referent concerns that the independent probe identified. This remains a whole-draft triage failure, not a semantic gate pass.
- The independent Snapshot 7 probe provides broader coverage but still requires reviewer judgment for potential anchors and any omitted meaningful work; four findings do not establish complete coverage.
- Early development aggregate route diagnostics include controlled no-call prefixes. The evaluator now filters states without a Coordinator execution log; per-record reviewed states remain authoritative, and subsequent artifacts use the corrected counts.

Development response, not a claimed improvement: prompt `v3.9.2-phase1` adds generic capacity and reasoning-coverage rules. Overflow is prohibited while issue capacity remains, and revisions must independently assess supported clarity/process/referent gaps before returning only lower-priority language findings. No transfer outputs were used.

### Development trial 3 and candidate freeze — `.2` fixture, `v3.9.2-phase1`

Artifact: `data/evidence/v3_phase1_development_phase1_evaluation_20261117T060732Z.json`.

All 16 scenarios completed with 29 calls, zero errors, zero schema repairs, zero reference normalizations, 390,679 observed tokens, and 1,187.233 seconds of recorded model latency.

Positive observations requiring named-review confirmation:

- Snapshot 7 revision broadened from one issue to four, including two process/development findings and two language-pattern findings, while preserving the fully addressed bounded agreement goal. The independent Snapshot 7 probe retained the unclear energy-recovery loop and sentence boundaries.
- Required deletion, discretionary narrowing, partial multi-location goals, and bounded location-specific goals retained the corrected contracts. Counterfactual probes did not restore the corrected boundary/reference anchors.
- The argument/source initial probe affirmed the draft without recreating the unsupported source-wording finding. The discretionary revision used optional-only direct response with one exact located optional entry; the named reviewer must judge whether that optional classification is appropriate.
- Narrative initial/revision behavior remained genre-sensitive and did not add citation, claim, or counterclaim demands.

Negative/mixed observations:

- Whole-draft coverage remains variable. Snapshot 7 revision omitted the unclear energy-recovery sequence identified by the independent probe and used one of its process findings on recyclable coverage instead; the independent probe returned three issues with a different process emphasis. Neither output establishes complete meaningful-issue coverage.
- Some process findings may demand more elaboration than the actual task requires, while other potential referent/boundary needs remain unaccounted for. These are substantive semantic-review questions, not repair-count successes.
- Operational cost increased across development revisions; no efficiency claim is made. Thinking-mode outputs also vary, so these differences are review observations rather than exact-reproduction targets.

The candidate was then frozen for acceptance/transfer review at `20261117T062845Z`. Freeze manifest: `data/evidence/v3_phase1_candidate_freeze_20261117T062845Z.json`; combined SHA-256: `fc219b427bae4df5566967d419b1799ec3446390828ab49ae963e99c6a9883fa`. The full mocked suite passed 438 checks in 6.20 seconds on this candidate. No further candidate tuning is authorized from acceptance or transfer outputs; any such tuning requires transfer reclassification and new held-out cases. Freeze does not pass the semantic gate.

### Acceptance regression subset — frozen-code match, `v3.9.2-phase1`

Artifact: `data/evidence/v3_acceptance_phase1_scenarios_01_02_03_10_23_26_evaluation_20261117T062831Z.json`.

Scenarios 1–3, 10, 23, and 26 completed with 12 calls, zero errors, zero schema repairs, zero reference normalizations, 97,511 observed tokens, and 176.267 seconds of recorded model latency. `final_explicitly_skipped=true`; no record contains `final_state`. Scenario 1 completed its initial/revision round scope without Final. This artifact used the same hashes later preserved in the freeze manifest; as a development regression, it did not use the transfer-only `--candidate-frozen` acknowledgement.

Positive/mixed observations requiring named-review confirmation:

- Source-mismatch #2 returned two accuracy-first source findings with specific source locations and a separate reasoning issue. Source-missing #3 returned internal reasoning/elaboration concerns rather than claiming source verification.
- Strong-draft #10 and long-informational #23 used direct response with empty issues/polish; the reviewer must inspect the complete long draft before accepting #23's no-issue judgment.
- Informal-narrative #26 returned one organization/development issue without citation, claim, or counterclaim requirements.
- Revision #1 retained a same-ID not-addressed/carry-forward goal and identified remaining reasoning work. Its newly introduced responsibility-warrant finding may be legitimate or may over-demand explanation; this remains a semantic-review question.

This is not full acceptance, Final evaluation, held-out transfer evidence, or semantic approval.

### Post-freeze transfer run

The reserved transfer artifact and outcomes are recorded below after the frozen run. No transfer output may drive candidate changes without reclassification and new held-out cases.

## 7. Named semantic review and open gate

**Named reviewer:** project owner or appointed semantic reviewer; appointment and review remain pending.

The reviewer must inspect complete current drafts and outputs, account for every reviewer-confirmed meaningful issue as a finding/coherent group/documented overflow, allow potential anchors to be rejected with textual rationale, and identify Critical/Major/Moderate/Minor findings using Meets / Needs refinement / Unacceptable. Development and transfer probes require no unresolved Critical or Major finding before the Phase 1 exit gate can pass. Historical provenance should be blinded where practical for draft-matched comparisons.

Open gates remain: named semantic review, corrected-counterfactual review, strong negative controls, held-out transfer review, and the owner’s separate promotion decision. Full acceptance, Final integration, educator review, accessibility review, deployment, and learner outcomes remain outside this implementation result.
