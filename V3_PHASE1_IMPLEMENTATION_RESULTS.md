# V3 Phase 1 Implementation Results

## 1. Status and evidence boundaries

Phase 1 of `V3_PHASED_IMPROVEMENT_PLAN.md` is implemented as an **evaluation-only candidate**. The current evaluator arm is `phase1`, with prompt `v3.9.5-phase1` and schema `v3.9.0`. Earlier `v3.9.2-phase1` and `v3.9.3-phase1` artifacts and freezes remain historical controls for their exact candidates, not evidence for the refactored v3.9.4 prompts. The promoted current default and `phase2_lean` evaluator selector use prompt `v3.10.1-phase2-lean` and schema `v3.10.0` for deterministic lean-Support handoffs. The current promoted student runtime is `v3.10.1-phase2-lean`/`v3.10.0` with low effort for both agents; no deployment or live-surface update occurred.

The historical comparison reference remains `V3_8_3_COMPLETE_RUN_EXTERNAL_REVIEW.md` and its identified source records. No new historical-baseline calls are required or used as Phase 1 controls. Historical comparisons are semantic and draft-matched, never exact-output reproduction requirements. Probes outside that run have no historical control. Candidate runs use the same configured `deepseek-flash` thinking/`high` mode but add the Phase 1 schema/payload and, for later controlled revisions, different evaluator revision numbers as documented below. The pre-existing working-tree client change that omits `max_tokens` was preserved and applies to these candidate calls; it is not attributed to the Phase 1 prompt.

The complete mocked suite passes. This establishes implementation/contract coverage only. The Phase 1 semantic exit gate is **not yet passed**: the named owner or appointed reviewer must review complete development and held-out transfer outputs using `EDUCATOR_REVIEW_PROTOCOL.md`. LLM-assisted screening does not substitute for that review, educator approval, or learner-outcome evidence.

## 2. Implemented candidate contract

- Strengthened whole-draft triage after accuracy and supported student concerns: meaning-blocking clarity/missing reasoning links, explicit task requirements, organization/reader connection, recognizable language patterns, then optional polish. Meaning-obscuring language remains a clarity priority. The five-issue maximum and stable accuracy partition remain unchanged. Meaningful overflow belongs in concise Coordinator rationale and cannot justify direct response.
- Added independent `goal_outcome` and `narrowing` dimensions while retaining the existing text-observation status. Added exact previous-draft deletion evidence and assignment/teacher/framework requirement evidence.
- Added deterministic observation/outcome/narrowing/carry-forward/route checks, including same-ID live candidates, required task-alignment issues, framework links, direct-response restrictions, and discretionary closure without completion claims.
- Extended Support and direct response with exact preservation of status, outcome, narrowing, evidence, requirement basis, and carry-forward. Support may paraphrase only the observation.
- Added neutral student-facing outcome/narrowing labels and evidence. “Fully addressed” is explicitly bounded to the selected goal in this draft, not mastery.
- Distinguished no meaningful issue, meaningful work remaining with student-controlled Finish, and optional-only direct response. Optional polish is bounded to zero to three exact located current-draft entries, has no revision candidates, and is empty on other routes.
- Persisted the new fields in round JSON and matching revision-history records. Older records leave the fields missing/unknown rather than receiving inferred outcomes.
- Did not add Phase 2 multi-location batching, per-round bounded history, or lean Support output merging, and did not auto-select carried goals. Deterministic Final validation and default Final prompts remain unchanged; v3.9.3 adds candidate-only Final calibration and plain-language prompts.

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
476 passed in 6.42s
```

Coverage includes the permitted/rejected outcome matrix, exact deletion and requirement evidence, framework links, carry-forward identity, direct-response prevention, optional polish validation, unique-location recovery, and boundaries, Coordinator-to-Support preservation, direct-response bypass, neutral UI rendering, round/history persistence and reopen, older history records, no automatic goal selection, evaluator versions/diagnostics, automatic/explicit call budgets, split-effort metadata, targeted branch fixture loading, syntactically valid evaluated JSON examples, lean Support deterministic round/Final merging and tamper rejection, a complete five-call candidate service flow, fixture integrity, counterfactual support removal, and runtime fixture-leakage scanning.

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

## 7. Owner-supplied prompt-review refactor — `v3.9.3-phase1`

The refactored candidate replaces the stacked Coordinator round base/suffixes with one contract and one schema, and likewise replaces the Support base plus goal-feedback override with one contract and one schema. It adopts the clearer empty-string examples, explicit severity mapping, safety/task-frustration distinction, multilingual voice calibration, Support payload-use rules, content-free ELD connector permission, and reordered JSON examples. Reordered keys do not change the Pydantic schema or parser contract, and coordinator reasoning remains a concise final-output rationale rather than hidden reasoning.

Phase 1 now has distinct candidate Final prompts. Coordinator Final adds grades 5–7/optional-conventions calibration; Support Final adds plain-language delivery, verified-finding-only use of diff/history, deletion-regression wording, and zero-improvement conclusion guidance. The evaluator passes both explicitly. The student runtime and its default Final prompts remain unchanged. No Final safety-routing change is claimed or introduced.

The proposed standalone `coach_validation_merge.py` was **not** added. It would duplicate and weaken existing behavior, including `flag_teacher` route overrides, exact selected-goal/requirement evidence checks, optional-mechanics enforcement, source-location consistency, bounded-language checks, Final changed-span validation, exact unchanged-goal consistency, and deletion-regression rejection. Its broader Final substring-overlap rule and lean-output defaults are not current contracts. Existing Pydantic models and validators remain authoritative.

The refactored prose that permitted `partially_addressed + discretionary + carry_forward=false` was not adopted. Every partial outcome still requires a meaningful same-ID remainder and carry-forward. Discretionary closure uses `not_addressed` or `uncertain`, never full or partial completion. The lean Support schemas and deterministic merge are deferred as Phase 2 design proposals, not silently introduced under schema `v3.9.0`.

One additive deterministic improvement was integrated into the existing Coordinator path: an exact optional-polish reference that occurs globally once within one blank-line-separated block can receive corrected paragraph/occurrence metadata, recorded in `coordinator_optional_polish_normalizations`. Missing, repeated, ambiguous, or cross-paragraph references still require bounded repair. Evaluator diagnostics report these corrections separately.

The fixture files' `candidate_prompt_version` now identifies v3.9.3; their scenario data and fixture versions are unchanged. The v3.9.2 candidate freeze, development/acceptance outcomes, and any v3.9.2 transfer artifact remain historical evidence for v3.9.2 only. No transfer output was used for this owner-supplied prompt refactor. V3.9.3 requires a new freeze and real-model/semantic evaluation; no transfer or semantic acceptance is claimed.

### V3.9.3 real-model smoke checks — not acceptance

Development scenario 2 used `data/evidence/v3_phase1_development_phase1_scenario_02_evaluation_20261117T074516Z.json`. Its controlled prefix was persisted without a model call; the revision completed with three calls, zero scenario errors, one Support schema repair, zero Coordinator repairs, zero reference normalizations, 29,577 observed tokens, and 61.942 seconds of recorded model latency. The first Support response gave one candidate six hint steps; the bounded repair returned five steps for each candidate. The final revision output retained `not_addressed + discretionary + carry_forward=false`, exact deleted-text evidence, and the same fields through Support. This fixture does not request Final and has no `final_state`, so this artifact does not verify the new Final prompts.

Acceptance scenario 1 then ran without `--skip-final`, using `data/evidence/v3_acceptance_phase1_scenario_01_evaluation_20261117T074750Z.json`. Initial review, revision, and Final completed with six calls, zero scenario errors, zero schema repairs, zero reference normalizations, 36,081 observed tokens, and 76.449 seconds of recorded model latency. `final_explicitly_skipped=false`, a `final_state` exists, and its execution path contains both Final Coordinator and Final Support. The revision retained the same-ID survey goal as not addressed with carry-forward; Final separately credited the changed responsibility explanation, reported no regression, and retained the survey warrant as a future possibility. Support Final used that verified improvement rather than adding a change claim from the raw diff.

These are limited operational and output observations, not named semantic approval. The one-repair development outcome is preserved rather than erased by the later zero-repair run. Neither smoke is full development evaluation, full acceptance, held-out transfer evidence, or a candidate freeze. Final wording, pedagogical calibration, and all complete outputs still require review under `EDUCATOR_REVIEW_PROTOCOL.md`.

## 8. Validated follow-up patch — `v3.9.4-phase1`

V3.9.4 applies the validated portions of the external review while retaining the v3.9.3 architecture and schema. Coordinator round now explicitly completes an independent clarity/reasoning audit before returning only organization/language findings or direct response, and prohibits omitting a supported higher-priority reasoning issue in favor of lower-priority language patterns. It does **not** adopt the proposed fewer-than-five-issues trigger; whole-draft review remains evidence-based rather than a candidate quota.

Coordinator descriptions must remain anchored to their exact references, with recurrence noted briefly rather than converted into a mandatory multi-paragraph checklist. Support action, hint steps, and self-check must share one passage scope; an intentionally broader recurring-pattern scope must be explicit and consistent across all three fields. The three-to-five-item hint cap is reinforced without changing the Pydantic contract.

Coordinator and Support grammar guidance must fit every named example and distinguish agreement, irregular forms, and lexical/structural usage. Regular and irregular third-person forms may remain in one agreement finding when taught accurately. The patch does not include fixture-specific vocabulary, infer language-background transfer, or prescribe one structural correction without considering intended meaning.

All four evaluated prompt JSON examples are parsed as JSON in focused tests. Representative values replace malformed nested quotes; prose remains authoritative for allowed values and boundary-route empty strings. Existing unique-location recovery for issues and present framework references remains in place alongside the v3.9.3 optional-polish recovery; no redundant resolver was added. Final prompts, deterministic Final validation, Final routing, schema `v3.9.0`, and the student default remain unchanged.

The matched development-scenario-2 and acceptance-scenario-1 smoke checks are recorded below. Broader paired evaluation remains necessary for true regressions/Final deletion, required narrowing with commissioned framework coverage, clarification/teacher routes, strong negative controls, and optional-only direct response. Potential clarity findings remain human-review hypotheses rather than mandatory anchors. No transfer output, freeze, promotion, or semantic acceptance is claimed.

### V3.9.4 matched real-model smoke outcomes — not acceptance

Development scenario 2 used `data/evidence/v3_phase1_development_phase1_scenario_02_evaluation_20261117T083729Z.json`. The revision completed with two calls, zero scenario errors, zero schema repairs, zero reference normalizations, 24,296 observed tokens, and 68.248 seconds of recorded model latency. The Coordinator returned three findings: a reasoning-level ambiguous `collect them` process reference, subject-verb agreement, and sentence boundaries. The grammar finding did not repeat the prior `equips` agreement error, and all Support hints contained four steps with no repair. Exact discretionary narrowing and Support handoff fields were preserved. The output did **not** return v3.9.2's toxic-powder finding; it found a different potential clarity gap, so exact reasoning coverage remains a semantic-review question rather than an anchor match. This fixture does not request Final.

Acceptance scenario 1 used `data/evidence/v3_acceptance_phase1_scenario_01_evaluation_20261117T083729Z.json`. Initial review, revision, and Final completed with six calls, zero scenario errors, zero schema repairs, zero reference normalizations, 37,585 observed tokens, and 81.058 seconds of recorded model latency. Initial review returned an opening source-accuracy finding and a survey-warrant finding rather than v3.9.2's survey-plus-responsibility findings. The opening claim is not explicitly attributed to the survey, so classifying it as source misrepresentation may be over-strong and requires review. More importantly, the revision retained only the opening issue and omitted the unchanged survey-warrant concern that the same run had identified initially and the student had named as a concern. Final later retained both the opening precision and survey warrant as future areas. This within-run coverage inconsistency remains a negative/mixed outcome despite zero repairs.

Final again credited the actual responsibility improvement, reported no regression, and did not fabricate an improvement for the unchanged selected opening goal. Support Final used the verified finding. These limited smoke results do not establish restored whole-draft coverage, general zero-repair behavior, an efficiency advantage, or semantic acceptance. No further prompt tuning from these outputs is claimed as part of the validated-review patch.

## 9. Evaluation-only lean Support structural upgrade — `phase2_lean`

The `phase2_lean` arm introduces prompt `v3.10.0-phase2-lean` and schema `v3.10.0` without replacing `phase1` or the student default. Coordinator round/Final prompts are the v3.9.4 constants. Support round and Final prompts retain their pedagogical/authorship contracts but replace copied output fields with ID/prose-only schemas through section replacement, not appended overrides.

`LeanRoundSupportOutput` permits only strengths, candidate goal IDs and instructional prose, and goal-feedback goal IDs/observations. `LeanFinalSupportOutput` permits finding IDs, observations, and conclusion. Extra copied fields fail validation. Python merges candidate `draft_reference`, `paragraph_number`, `occurrence`, `hint.passage_reference`, Coordinator source limitations, all eight immutable goal-feedback state/evidence fields, and Final `final_reference`. It restores Coordinator candidate/finding order and reconstructs the existing full Pydantic outputs. The same authorship, ellipsis, bounded-language, exact-reference, observation-preservation, and Final-reference validators run after merging, before state persistence or UI rendering. Deletion regressions retain an empty Final reference.

Lean-specific bounded-repair instructions request only IDs and prose and explicitly prohibit reintroducing copied fields. Raw model responses remain lean in execution logs; persisted round/reflection state remains full, so no SQLite migration or UI change is required. The existing Phase 1 fixtures remain input-compatible; each run's explicit arm/prompt/schema configuration is authoritative.

Focused coverage is in `tests/test_phase2_lean.py`: complete round/Final merging, Coordinator ordering, rejection of copied/tampered fields at every protected location, unknown IDs, post-merge instructional validation, deletion regressions, lean repair behavior, constructor constraints, prompt schema shape, and evaluator wiring. Matched real-model outcomes are recorded below. No token-reduction percentage, repair reduction, semantic improvement, transfer, freeze, promotion, or deployment is assumed from the structural change alone.

This implements only the requested lean Support upgrade. Phase 2 multi-location batching, per-location outcomes, bounded relevant history, and highlighting changes remain unimplemented.

### Phase 2 lean matched real-model outcomes — not acceptance

Development scenario 2 used `data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T085542Z.json`. The revision completed with two calls, zero scenario errors, zero schema repairs, zero reference normalizations, 28,362 observed tokens, and 92.379 seconds of recorded model latency. Coordinator returned five findings, so Support generated five candidates; this output-volume difference prevents a like-for-like efficiency claim against v3.9.4's three-candidate output. Raw Support JSON contained only the lean keys, while persisted candidates contained every exact Coordinator reference/location and hint passage reference. Goal-feedback outcome, narrowing, evidence, requirement, and carry-forward fields matched Coordinator state. Compacting the actual raw lean JSON and the reconstructed full model-equivalent JSON with identical values showed a 25.5% byte omission share. Total tokens/latency nevertheless exceeded the v3.9.4 smoke because candidate and reasoning volume differed.

The first acceptance run, `data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T085542Z.json`, is preserved as a failed operational outcome. One revision Support response used a completion ellipsis; the existing post-merge full-output validator rejected it and the lean-specific repair succeeded without adding copied fields. The authorized six-call cap was then exhausted before Final completion, leaving no `final_state`. The artifact records five successful-response calls, one schema repair, 40,183 observed tokens, and 86.324 seconds of recorded model latency. This was a budget-bound incomplete evaluation, not a merge exception or completed Final result.

A separately identified retry with eight-call headroom completed acceptance scenario 1 in `data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T085819Z.json`: six calls, zero scenario errors, zero schema repairs, zero reference normalizations, 42,573 observed tokens, and 116.507 seconds of recorded model latency. Initial review returned survey and responsibility reasoning findings; revision retained the survey goal without adding the earlier responsibility nitpick. Final completed both agents, credited the actual responsibility improvement, and retained future areas. Raw round responses contained no reference/state fields and raw Final responses contained no `final_reference`; persisted state contained the exact merged values. The retry's zero repairs do not erase the preceding failed run or establish general repair reliability.

For the successful retry, compact lean-vs-reconstructed-full byte omission shares were 28.0% for initial Support, 27.6% for revision Support, and 20.2% for Final Support. Actual visible Support tokens (completion minus reasoning tokens) totaled 953 versus 1,230 in the v3.9.4 smoke, a 22.5% reduction across different outputs. In development, visible Support tokens increased from 1,170 to 1,579 because the lean run returned five candidates rather than three. End-to-end totals also increased in both lean smokes, driven by different reasoning/candidate volumes. These are descriptive single-run comparisons, not proof of a 40% token reduction, a latency improvement, or a causal prompt effect.

The structural guarantee is narrower and directly verified: protected copied fields cannot drift because they are absent from the model schema and reconstructed from Coordinator state. Instructional/authorship errors can still occur and require the existing validators/repair. Semantic quality, full acceptance, held-out transfer, freeze, promotion, and deployment remain open.

## 10. Accuracy, concern continuity, density, and evaluation follow-up

V3.9.5 Phase 1 and v3.10.1 Phase 2 lean preserve the deterministic schemas and lean merge while adding bounded prompt refinements. Unattributed statements are not source misrepresentation merely because they are absent from or not entailed by a source; accuracy requires contradiction, fabrication, or actual source misreporting. Broad premises may instead warrant bounded development/reasoning feedback, and acceptable hooks need no issue. Revision routes independently recheck draft-supported student concerns even when selected goals differ, without reviving resolved or unsupported concerns.

A normal one-to-three issue target addresses feedback density without a candidate quota. Fourth/fifth issues are reserved for distinct accuracy/source-responsibility or explicit task/teacher/framework requirements. Other meaningful lower-priority overflow remains documented for later review and cannot justify direct response or a resolution claim. The schema maximum remains five and student-controlled stopping is unchanged.

The confirmed acceptance ellipsis trace was a true completion frame, not a regex false positive. Both full-copy and lean Support prompts now explicitly prohibit supplying a stuck-step sentence opening or quoted fragment for completion, with or without an ellipsis. Existing post-merge validation remains authoritative.

Evaluator `--max-model-calls` is optional. Explicit values remain hard caps; omission selects an estimated base-call budget plus `--repair-headroom` (default 2). Acceptance scenario 1 therefore receives an eight-call automatic budget (six base plus two repair slots), while explicit six remains six. Authorization/evidence records include the mode, base estimate, headroom, and effective maximum. The estimate is a conservative fixture-based upper bound, not a prediction of route-specific calls.

Evaluation-only `--support-reasoning-effort low|high|max` supports DeepSeek thinking `phase2_lean` runs. A wrapper shares the Coordinator's budget, keeps Coordinator at high, applies the selected Support effort only during Support calls, restores the shared raw client afterward, and records actual per-call metadata. It does not change student runtime or automatically adopt low effort.

Four new focused checks cover automatic versus explicit budgets, shared-budget effort restoration/metadata, split-effort evaluator configuration, and the observed completion-ellipsis pattern. Repeated-anchor, low-effort, and targeted-branch attempted outcomes and their external provider blocker are recorded below. No freeze, semantic gate pass, promotion, or deployment is implied.

The earlier suggestion that over 90% of total tokens were hidden reasoning is not supported by the cited successful acceptance artifact: 17,092 reasoning tokens were 87.9% of completion tokens but 40.1% of the 42,573 total; 23,126 prompt tokens were 54.3% of total. Latency is recorded per call but is not decomposed into reasoning versus visible-output time. Low Support effort is therefore an experiment, not an established dramatic end-to-end optimization.

### Repeated anchors and Support-low experiment — externally blocked

Three high-effort development repeats were attempted with automatic four-call budgets (two estimated base calls plus two repair slots). All three returned DeepSeek HTTP 402 `Insufficient Balance` before a successful model call: `data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T095312Z.json`, `data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T095358Z.json`, and `data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T095359Z.json`. They contain no usable candidate output and do not verify the accuracy, concern-continuity, or density changes.

Three high-effort acceptance repeats were attempted with automatic eight-call budgets (six base plus two repair slots). Repeat 1 recorded two calls and 20,561 tokens before HTTP 402; repeats 2 and 3 failed before a successful call. Artifacts are `data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T095312Z.json`, `data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T095414Z.json`, and `data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T095415Z.json`. None contains a revision or Final result. The automatic budgets and authorization metadata were exercised, but k=3 output consistency remains unevaluated.

The exploratory Support-low batch did not produce a valid A/B. Its development process hit a same-second shared-database lock before model review, and its acceptance path collided with the high-effort run started at the same timestamp. Provider HTTP 402 failures independently blocked the series. Effort-specific database/evidence filenames now separate `support_low` runs from default/high runs, but no low-effort output, token saving, latency improvement, or quality claim is available. The failed high-effort artifacts remain preserved; no low artifact is presented as evidence.

No further billable retries or branch runs were launched after the provider balance failure was confirmed. Repeats and the low-effort comparison require a restored provider balance and should use the new effort-specific filenames. This is an external evaluation blocker, not a semantic pass/fail or a mocked-test failure.

### Initial targeted branch preparation — mocked coverage, followed by funded execution below

`test_cases/v3/phase2_branches.json` now contains six targeted synthetic development probes: required narrowing with commissioned `Survey evidence` and `Explanation of evidence` framework components, optional-only direct response, ordinary `This is hard` task frustration, explicit serious discouragement, and two Final deletion scopes. The evaluator exposes `phase2_branches`, computes a 12-call base estimate for all six (eight for the initial four) plus configurable repair headroom, and restricts the set to Phase 1-family arms. Existing `acceptance` #30 remains the clarification-limit probe and `final_regression` #4 the genuine Final-regression probe.

Focused tests verify fixture integrity, commissioned framework input, evaluator loading, and budget construction. The full suite also retains the established mocked contracts for required framework narrowing/linking, optional polish and unique-location recovery, clarification limits, teacher review, true Final regressions, and lean deletion-reference merging. **473 mocked checks pass.** Real-model execution was initially blocked by HTTP 402; the funded branch outcomes are recorded below.

### Funded repeated anchors — operational completion with continued semantic variance

After the owner restored provider balance, all three high-effort development repeats completed with two calls, zero errors, zero repairs, and exactly three candidates: repeat 1 (`data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T100329Z.json`) used 21,842 tokens/54.838 seconds; repeat 2 (`data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T100456Z.json`) used 24,283/69.404; repeat 3 (`data/evidence/v3_phase1_development_phase2_lean_scenario_02_evaluation_20261117T100606Z.json`) used 33,096/116.065. All preserved `not_addressed + discretionary + carry_forward=false`, documented lower-priority overflow, and kept hints within their bounds. Finding sets varied substantially. In particular, repeat 3 claimed that dewatered trash lacked a next burning-system destination even though the following draft text explicitly supplies that destination. This unsupported finding prevents treating the repeats as semantic acceptance despite consistent density.

All three high-effort acceptance repeats completed six calls with zero errors/repairs and completed Final: repeat 1 (`data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T100456Z.json`) used 39,137 tokens/89.081 seconds; repeat 2 (`data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T100626Z.json`) used 38,520/88.090; repeat 3 (`data/evidence/v3_acceptance_phase2_lean_scenario_01_evaluation_20261117T100754Z.json`) used 38,461/81.592. None repeated the false opening `accuracy` classification, every revision retained the student's evidence concern with same-ID carry-forward, and every Final credited the actual responsibility improvement without a fabricated regression. Initial coverage still varied: repeat 1 returned survey and responsibility warrants, while repeats 2 and 3 returned only the survey warrant. These runs support operational repeatability of the accuracy/concern fixes, not stable complete coverage or educator approval.

The exploratory Support-low development run (`data/evidence/v3_phase1_development_phase2_lean_support_low_scenario_02_evaluation_20261117T100456Z.json`) completed with three calls and one **Coordinator** repair for optional polish on a support route; the low-effort Support call itself required no repair. It used 32,996 tokens/67.810 seconds and returned three candidates. This does not show universal low-effort savings or reliability.

The exploratory Support-low acceptance run (`data/evidence/v3_acceptance_phase2_lean_support_low_scenario_01_evaluation_20261117T100604Z.json`) completed six calls with zero repairs, 35,204 tokens, and 69.585 seconds; per-call logs confirm `low` on all three Support calls and `high` on all Coordinator calls. Against the three high-effort acceptance repeats, total tokens were 8.5–10.0% lower and latency was 14.7–21.9% lower. Its Coordinator selected one initial issue rather than repeat 1's two, so output content is not controlled. The result is promising operational evidence only; low effort is not automatically adopted and quality equivalence is unestablished.

### Support-low n=3 follow-up — viable comparator, no general efficiency win

Two additional low-effort repeats per anchor completed the matched three-run sample. New artifacts are development repeats 2/3 (`data/evidence/v3_phase1_development_phase2_lean_support_low_scenario_02_evaluation_20261117T103727Z.json`, `data/evidence/v3_phase1_development_phase2_lean_support_low_scenario_02_evaluation_20261117T103955Z.json`) and acceptance repeats 2/3 (`data/evidence/v3_acceptance_phase2_lean_support_low_scenario_01_evaluation_20261117T103827Z.json`, `data/evidence/v3_acceptance_phase2_lean_support_low_scenario_01_evaluation_20261117T104052Z.json`). All four completed without scenario errors; both new development runs returned three candidates with zero repairs, and both new acceptance runs completed Final with zero repairs.

Across all three low development runs, median tokens/latency were 22,892/60.119 seconds versus 24,283/69.404 for high effort (5.7% and 13.4% lower medians). Ranges overlapped substantially, and low repeat 1 still required the previously documented Coordinator repair. Across all three low acceptance runs, median tokens/latency were 38,729/87.362 seconds versus 38,520/88.090 for high effort: approximately 0.5% more tokens and 0.8% less latency, effectively tied in this small sample. The first low run's apparent 8.5–10.0% token and 14.7–21.9% latency advantage did not persist across repeats. Low-effort Support itself required no repairs in any of the 12 Support calls across the six low runs.

All three low acceptance runs avoided the false opening accuracy classification, retained the student's evidence concern on revision, and credited the actual Final improvement. Initial issue counts were 1/2/1, compared with high effort's 2/1/1, so coverage remained variable rather than consistently narrower or broader. Low development finding sets also varied but did not reproduce high repeat 3's explicit false missing-link claim in these outputs. Minor concerns remain: low development repeat 1 used an oversimplified verb-suffix rule, and low development repeat 3 broadened its boundary action to another sentence while keeping a local self-check.

Readability was mixed rather than uniformly worse. Median low acceptance revision-action length was shorter than high (11.0 versus 12.5 words), but hint steps and stuck steps were longer (15.1 versus 12.6 and 17.67 versus 15.0 words). Development readability medians were close. The expanded screening therefore rates low effort comparable to high on multilingual readability with reservations, rather than penalizing only the first low outlier.

The n=3 evidence supports keeping low effort as an evaluation comparator: it is operationally viable and semantically comparable in these synthetic anchors, but it does not establish a general token/latency advantage, superior coverage, or equivalent quality across other scenarios. No automatic runtime adoption, freeze, promotion, or educator-gate pass follows.

### Funded targeted branch outcomes

The initial four-probe branch run (`data/evidence/v3_phase2_branches_phase2_lean_evaluation_20261117T100934Z.json`) completed six calls with zero errors/repairs, 42,033 tokens, and 69.587 seconds. Required narrowing retained exact deleted/requirement evidence, same-ID carry-forward, a live task-alignment candidate, and both commissioned framework components through lean Support. Ordinary `This is hard` frustration received two writing-support candidates rather than teacher review; explicit hopelessness routed to `serious_discouragement` with empty ordinary assessment collections. The first strong-draft version used direct response with no optional entries, so an explicit optional-entry follow-up was added rather than claiming that path.

`data/evidence/v3_acceptance_phase2_lean_scenario_30_evaluation_20261117T101044Z.json` completed three calls with zero repairs and exercised one initial clarification, one resumed clarification, then deterministic `clarification_limit` after the second unclear answer. `data/evidence/v3_final_regression_phase2_lean_scenario_04_evaluation_20261117T101105Z.json` completed two Final calls with zero repairs and retained one genuine improvement plus three meaningful regressions; its rewritten passages used nonempty Final references, so it did not exercise the empty-deletion-reference case.

The expanded optional/deletion follow-up (`data/evidence/v3_phase2_branches_phase2_lean_scenarios_02_05_evaluation_20261117T101425Z.json`) completed three calls with zero errors/repairs. Optional-only direct response returned one exact located spelling-polish entry and no meaningful issue; its location was already correct, so no deterministic normalization was needed or claimed. The first deletion scope produced two meaningful regressions with surviving Final anchors, leaving the empty-reference case to the final probe.

The whole-paragraph deletion probe (`data/evidence/v3_phase2_branches_phase2_lean_scenario_06_evaluation_20261117T101701Z.json`) completed two calls with zero errors/repairs. Coordinator returned the exact original paragraph and `final_reference=""`; raw lean Support returned only finding ID/observation, and the persisted reflection preserved the empty Final reference while explaining the loss from the original text. This directly exercises the requested lean Final deletion merge path. Empty-reference and optional-location normalization also remain covered by mocked contracts; no real optional-polish correction occurred because the model's location was valid.

These funded runs close the requested operational branch coverage while preserving semantic concerns. Full acceptance, held-out transfer, named educator review, freeze, promotion, deployment, and learner-outcome claims remain separate and open.

## 11. Intermediate runtime decision — Support-only low/full-copy, superseded

Following the matched n=3 Support-low evaluation, the owner explicitly selected `DEEPSEEK_SUPPORT_REASONING_EFFORT=low` as the student-runtime default. Coordinator remains `DEEPSEEK_REASONING_EFFORT=high`. This decision changes only model configuration: default prompts/schema remain full-copy `v3.8.3`/`v3.8.0`, and `phase2_lean` remains evaluation-only. The owner decision is not represented as educator approval, semantic acceptance, or deployment.

`app.py` constructs separate DeepSeek clients for Coordinator and Support, and `DeepSeekClient.from_env(reasoning_effort=...)` validates `low`, `high`, and `max`. An absent Support variable defaults to low; a local override remains explicit. Non-thinking configuration is unchanged and does not use reasoning effort. Per-call observability continues to record actual agent-specific effort without hidden reasoning.

Focused tests verify the override request/metadata, invalid-effort rejection, actual app runtime construction, default prompt preservation, and non-promotion of lean merging. The actual student-default acceptance smoke is recorded below after execution. The repeated evaluation evidence remains limited synthetic output evidence; this promotion is an owner product decision and does not close the educator gate.

## 12. Current owner-selected default — latest lean prompt/schema, low effort for both agents

The owner subsequently selected the latest `v3.10.1-phase2-lean`/`v3.10.0` prompt/schema with reasoning effort `low` for **both Coordinator and Support**, superseding Section 11's intermediate Support-only-low/full-copy configuration. The current app explicitly constructs the v3.9.5 Phase 1 Coordinator and lean Phase 2 Support contracts; `agents/utils.py` reports the latest prompt/schema markers. Both `DEEPSEEK_REASONING_EFFORT` and `DEEPSEEK_SUPPORT_REASONING_EFFORT` default to low with explicit local overrides. Persisted round/reflection state and UI highlighting remain full and unchanged after deterministic merging; no database migration is needed. Full Phase 2 batching, per-location outcomes, bounded history, and highlighting changes remain unimplemented.

The exact current-default real smoke is `data/evidence/v3_runtime_latest_low_all_agents_acceptance_01_evaluation_20261117T122927Z.json`. Acceptance scenario 1 completed six calls with zero errors, zero repairs, 35,704 observed tokens, and 68.331 seconds of recorded model latency. Every Coordinator and Support call records `low`; the runtime configuration records the latest prompt/schema and named prompt constants. Initial and revision each returned one focused reasoning issue; revision retained the selected survey goal as not addressed with carry-forward. Final credited the actual responsibility improvement and reported no regression. Lean raw Support output was reconstructed into the full persisted handoff without copied-field drift.

The earlier `v3_runtime_default_support_low_acceptance_01_evaluation_20261117T121818Z.json` remains historical evidence for Section 11's intermediate Support-only-low/full-copy configuration and is not the current default proof. The current default is **implemented and locally real-model verified**. It is not deployed or live-verified at the canonical URL, and this owner decision does not pass the educator or semantic gates.

## 13. Named semantic review and open gate

**Named reviewer:** project owner or appointed semantic reviewer; appointment and review remain pending.

The reviewer must inspect complete current drafts and outputs, account for every reviewer-confirmed meaningful issue as a finding/coherent group/documented overflow, allow potential anchors to be rejected with textual rationale, and identify Critical/Major/Moderate/Minor findings using Meets / Needs refinement / Unacceptable. Development and transfer probes require no unresolved Critical or Major finding before the Phase 1 exit gate can pass. Historical provenance should be blinded where practical for draft-matched comparisons.

Open gates remain: named semantic review, corrected-counterfactual review, strong negative controls, held-out transfer review, and the owner’s separate promotion decision. Full acceptance, Final integration, educator review, accessibility review, deployment, and learner outcomes remain outside this implementation result.
