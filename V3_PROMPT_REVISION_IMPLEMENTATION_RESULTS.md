# V3 Prompt, Contract, and Evaluation Revision — Implementation Results

**Date:** 2026-11-15<br>
**Plan:** `V3_PROMPT_REVISION_AND_EVALUATION_PLAN.md`<br>
**Production prompt/schema:** `v3.7.1`/`v3.7.0`<br>
**Current evaluation-only Support prompt:** `v3.7.2-consolidated`<br>
**Preserved targeted Support candidate:** `v3.7.1-consolidated`<br>
**Runtime decision:** Phase 1 baseline with thinking, explicitly selected by the user after the 2×2 review; non-thinking remains a comparator and no automatic prompt-arm switch occurs<br>
**Deployment:** Not authorized and not performed

## 1. Scope and protected behavior

The user confirmed all three recommended product defaults and authorized the complete targeted and full evaluation in both thinking and non-thinking modes. The implementation preserves the two-agent architecture, frozen root V1/V2 fixtures, synthetic-writing boundary, source/authorship/human-review protections, one-repair limit, and deployment gate.

Implemented changes:

- Hints use one concept restatement plus 2–4 procedural steps, 3–5 total items; Coordinator prose uses singular `regression`.
- Initial and revision ranking uses stable accuracy partitioning. The Coordinator owns supported-concern identification and non-accuracy ordering; no `addresses_student_concern` field was added. Support preserves resulting candidate order.
- Clarification and teacher review reject nonempty ordinary assessment collections. Teacher review permits empty genre metadata.
- Coordinator model output excludes `clarification_limit`; only the graph creates it after the deterministic two-answer boundary. Model-selected values are neutralized, not relabeled as concerning content.
- Final prompts prohibit unsupported source/framework claims without changing Final exact-membership, unchanged-draft, or changed-text-overlap guards.
- Unique, single-block `present` framework references receive separate framework/component/location correction records. Other reference cases retain bounded repair; Final references are never normalized.
- The consolidated Support candidate is evaluation-only. The literal slash starter was removed from both prompts and the shared allowlist; separate detail/evidence forms remain.
- Exact quoted draft ellipses used for locating are distinguished from completion ellipses. Locating text cannot also contain a completion command.
- Added 14 Support-only handoffs, 12 Coordinator-targeted scenarios, an isolated adversarial early-limit arm, per-arm prompt-version metadata, normalization metrics, repair analysis, and protocol-consistent educator anchors.

## 2. Gate A — mocked engineering

The complete suite passed **318 checks** before real-model evaluation. Targeted review then added quoted-ellipsis and teacher-category edge cases, the deterministic clarification probe, and their regression tests. The final complete suite passed **325 checks**, including prevention of locating-plus-completion bypasses and correct `none`-category handling after two unclear answers.

The repair-analysis tests use synthetic artifacts rather than requiring git-ignored evidence files. Evaluation-arm tests verify the candidate prompt/version and ensure the adversarial early-limit arm cannot escalate after one answer.

## 3. Phase 4 — preserved repair analysis and schema decision

Evidence: `data/evidence/v3_repair_analysis_20261115T151252Z.json`, produced by `scripts/analyze_repairs.py` from the two preserved `v3.6.5`/`v3.6.3` full acceptance artifacts.

| Mode | Attempted calls | Successful-response logs | Validation-failure events | Field findings |
| --- | ---: | ---: | ---: | ---: |
| Non-thinking | 114 | 108 | 14 | 16 |
| Thinking | 98 | 97 | 3 | 3 |
| Total | 212 | 205 | 17 | 19 |

Field findings were 12 genuine authorship leaks, three structural-validator false positives, two JSON/schema mismatches, one Coordinator reference/location failure, one grounding/source-limit failure, and **zero Support echo mismatches**. One empty API response is separate from validation failures. The denominator includes six calls preserved only on the two failed non-thinking scenarios; the 108 execution-log calls alone would undercount attempts.

**Decision:** Defer the conditional Support schema refactor. Echo removal has no demonstrated operational burden in these artifacts. Address semantic authorship failures and quoted-ellipsis false positives directly. No Support schema injection or application-state migration was introduced.

## 4. Gate B — Support 2×2 targeted comparison

All four arms completed 14/14 frozen handoffs with no scenario errors. Non-thinking uses temperature 0; thinking omits temperature and records the configured reasoning effort. All arms use the same Phase 1-aligned schema, validators, handoffs, one-repair policy, and per-request output settings.

| Prompt arm | Mode | Calls | Repairs | Observed tokens | Model latency (s) |
| --- | --- | ---: | ---: | ---: | ---: |
| Phase 1 baseline | Non-thinking | 17 | 3 | 64,155 | 59.227 |
| Phase 1 baseline | Thinking | 15 | 1 | 87,561 | 219.153 |
| Consolidated | Non-thinking | 19 | 5 | 65,111 | 69.582 |
| Consolidated | Thinking | 15 | 1 | 76,451 | 209.202 |

Evidence:

- `data/evidence/v3_support_prompt_evaluation_20261115T152813Z.json`
- `data/evidence/v3_support_prompt_support_consolidated_evaluation_20261115T153252Z.json`
- `data/evidence/v3_support_prompt_repair_analysis_20261115T161001Z.json` categorizes the consolidated non-thinking repairs as three genuine authorship leaks and two schema mismatches; the consolidated thinking repair was one genuine authorship leak. No echo mismatches occurred in any Support arm.

Interpretation is mixed and limited to these 14 handoffs:

- Consolidation did **not** improve non-thinking operational reliability: repairs increased from three to five, with 10.355 seconds more recorded model latency. Thinking retained one repair and used 11,110 fewer tokens and 9.951 seconds less latency in this pair. These are descriptive results, not stable latency percentiles or a universal prompt-length rule.
- Consolidated non-thinking initial responses included target completion frames for the survey warrant and missing claim. Bounded repair caught them, but the prompt did not prevent them.
- Final repaired consolidated non-thinking outputs still supplied target-like vocabulary: `focus`/`concentrate` for a classroom-effect gap, `removed`/`stored` for an imaginative waste-path gap, `steady`/`loosen`/`warm` for an internal narrative detail, and `creak`/`glimpse`/`flutter`/`hush` for a requested sensory detail. These are semantic authorship concerns even though structural validation passed.
- The consolidated non-thinking strong-draft handoff selected `According to the passage, ____.` for a class-discussion finding without a supplied passage. Thinking avoided that mismatch and most sampled target-vocabulary issues, but still retained `pump`/`supply` for the octopus mechanism and long multi-action instructions in places.
- Baseline outputs also had concerns, including target-like vocabulary and long instructions. Thinking is not evidence of a fundamental capacity bottleneck or a reason to change runtime defaults.

**Gate B is not passed for the consolidated candidate.** It remains evaluation-only and is not promoted into production. Broader vocabulary-policy changes remain deferred for product/educator review rather than being silently adopted after this small sample.

## 5. Gate B — Coordinator-targeted behavior

Evidence: `data/evidence/v3_coordinator_targeted_evaluation_20261115T153731Z.json`.

| Mode | Scenarios | Calls | Repairs | Observed tokens | Model latency (s) | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Non-thinking | 12 | 38 | 0 | 133,229 | 114.471 | 0 |
| Thinking | 12 | 41 | 1 | 230,964 | 578.744 | 0 |

Confirmed:

- Non-thinking exercised two unclear answers followed by deterministic `clarification_limit`; teacher-review and clarification collections were empty in both modes.
- The isolated adversarial artifact, `data/evidence/v3_coordinator_targeted_coordinator_early_limit_scenario_03_evaluation_20261115T154905Z.json`, shows non-thinking selected `clarification_limit` after one answer and was neutralized to another clarification. Thinking did not select the internal category in this probe. Zero-answer adversarial behavior remains covered by mocked tests rather than demonstrated in this real-model sample.
- Accuracy findings ranked first. Thinking placed a supported development concern after two accuracy findings on initial review. The `.1` fixtures did not consistently produce a development-level concern on revision, so a `.2` bounded fixture rerun was added rather than forcing output.
- CER title-block locations were valid and unchanged. Non-thinking repeated-reference handling recorded two safe unique-issue corrections; no framework correction was needed. Ambiguous-recovery and title-off-by-one correction remain covered by mocked tests.
- Unchanged final comparisons produced no improvements or regressions in either mode.

Semantic concerns:

- Thinking's source-missing Final comparison claimed that the later-start proposal was no longer directly stated even though the final opening still says `Our school should start later.` This unsupported regression contradicts the complete drafts.
- Thinking classified the explicitly synthetic class discussion in the strong-draft fixture as unusable evidence because it was synthetic. That misreads the evaluation context and manufactures an accuracy concern. Both modes still produced issues rather than affirming the strong-draft control, so the strong-draft semantic gate remains unresolved.
- Non-thinking initially treated a vague but bounded survey summary as an accuracy error. This is a severity-classification concern, not evidence that the deterministic accuracy partition failed.

The fixture-`.2` rerun, `data/evidence/v3_coordinator_targeted_scenarios_01_02_04_evaluation_20261115T155458Z.json`, used nine calls per mode with no repairs or scenario errors. It exercised accuracy followed by a supported development concern on revision in both modes. Non-thinking reached the legitimate two-answer limit; thinking returned `teacher_review` with category `none`, which the original normalization incorrectly relabeled as concerning content. That real-output evidence motivated a bounded routing fix and version increment to production `v3.7.1`: an explicit `teacher_review` with `none` returns to clarification so the graph can own the boundary. Genuine `concerning_content` and `serious_discouragement` handling is unchanged.

The isolated probe `data/evidence/v3_coordinator_targeted_coordinator_clarification_probe_scenario_04_evaluation_20261115T160349Z.json` then exercised two unclear answers followed by `clarification_limit` in **both modes**, with three calls and no repairs/errors per mode. These fixes address the category/routing failure but do not erase the strong-draft, authorship, or Final semantic concerns above.

## 6. Local real-application workflow

An isolated non-thinking Streamlit process on port 8502 used `data/local_prompt_revision.db` and the synthetic `garden_source_accurate` preset. No deployment occurred.

Verified in the real browser/application:

- Draft submission through Coordinator and Support, one recommended goal, and alternative reveal/hide.
- A four-item hint with one concept restatement and three procedural steps; choose-only selection and Revise navigation.
- **Show less**, **Show all**, and **I’m stuck** presentation. After initial review and all presentation actions, persisted state still contained two model calls and one snapshot.
- Refresh/restoration preserved submitted drafts and completed feedback/reflection without new model calls. Unsaved goal selection returned to Choose and was reselected.
- The custom shadow-DOM editor received 127 characters individually through Chrome's trusted text-insertion channel after synthetic key events were not adopted. Exact resulting text was verified: 114 words, no scrambling. No `fill()` was used.
- Revision 1 created a second snapshot and two more model calls. Finish cancellation preserved state; confirmed Finish produced a completed reflection with two final model calls.
- A separate synthetic composition replaced only the final period with an exclamation mark. Before **Continue review**, it still had one snapshot and one completed round. The neutral prompt reported one word added/removed without a quality judgment; continuing produced exactly two snapshots and two completed rounds with a grounded no-improvement observation.
- Capture: `data/evidence/v3_prompt_revision_local_final_20261115.png`. Machine-readable snapshot/call records and the checkpointed database hash are in `data/evidence/v3_prompt_revision_local_workflow_20261115T163826Z.json`.

Semantic concern: the revision review said **Improvement not yet evident**, while the final reflection immediately called the same unchanged addition **Specific improvement**. This cross-stage contradiction remains a failure even though the workflow completed.

AppTest already covers unchanged confirmation, failed-review retry, failed-final retry, and no-duplicate-snapshot behavior; this browser run did not repeat the induced-failure paths. Full keyboard and actual screen-reader checks remain open human accessibility gates.

## 7. Gate C — full integrated diagnostic

Artifact: `data/evidence/v3_acceptance_support_consolidated_evaluation_20261115T160443Z.json`. This run used production Coordinator prompt `v3.7.1`, evaluation-only consolidated Support `v3.7.2-consolidated`, schema `v3.7.0`, and fixture `v3.4.0`. Both databases were checkpointed/closed with zero WAL bytes and recorded SHA-256 hashes.

| Mode | Scenarios | Calls | Repairs | Observed tokens | Model latency (s) | Scenario errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Non-thinking | 32 | 110 | 4 | 391,077 | 353.184 | 0 |
| Thinking | 32 | 97 | 4 | 502,048 | 1,156.213 | 2 |

Non-thinking recorded two Coordinator and two Support repairs, four unique-issue normalizations, and no framework normalizations. Thinking recorded one Coordinator and three Support repairs and no normalizations. There were no Support echo mismatches, no empty/API failures, and no required model-call or token cap was approached.

`data/evidence/v3_integrated_repair_analysis_20261115T163423Z.json` separates the eight validation-failure events: non-thinking had one genuine authorship leak, one source-limit violation, and two schema mismatches; thinking had one genuine authorship leak and three schema mismatches. Safe locating fields were not miscounted as failures under the new validator.

Thinking's two errors are harness/scenario incompatibilities, not unexplained application fallbacks:

- **#9:** the model appropriately returned `direct_response` for the ordered initial draft, but the fixture requires an initial candidate to select for the staged organizational regression.
- **#15:** the model returned two meaningful candidates, while the fixture rigidly requires three. The run did not force a third issue.

Those intended thinking revision/final paths were not exercised, so integrated path coverage is incomplete even though the errors are explained. Non-thinking exercised all 32 intended workflows without scenario errors. The historical `v3.6.5` failed baselines remain preserved; differences across prompt arms, code, and scenario paths do not support attributing the non-thinking operational improvement to prompt consolidation alone.

## 8. Integrated semantic review

AI-assisted complete-context screening found the following; it is not educator review or a numerical quality score:

- **Strong drafts:** both modes still returned two issues for #10 instead of affirming without manufactured work. Thinking's targeted run also misclassified an explicitly synthetic class discussion as an accuracy problem. The strong-draft semantic gate remains failed.
- **Clarification:** non-thinking reached `clarification_limit` after two unclear answers. Thinking returned support after one unclear answer; it did not prematurely escalate, but did not exercise the integrated two-answer boundary. The isolated controlled probe verified that boundary in both modes.
- **Final consistency:** non-thinking #20 said the quiet-to-reading link was not yet evident in the revision review, then called the same added focus clause an improvement in the final reflection. This repeats the local workflow contradiction and is not consistent with the immediately preceding review.
- **Authorship:** a repaired non-thinking #7 initial response contained an on-topic claim frame; thinking #21 contained an on-topic completion frame. Bounded repair prevented partial delivery of those invalid responses. Final outputs still need semantic review: non-thinking #22 offered `cozy` for the requested cushion-description detail, and the targeted 14-handoff set contained the broader target-vocabulary problems documented above.
- **Language priority:** thinking #24 correctly used `direct_response` with no non-obscuring mechanics goal; non-thinking returned reasoning/organization goals rather than a conventions catalogue. No narrative citation/counterclaim demand was found in the reviewed narrative outputs.
- **Source grounding:** source-missing limitations were retained, and unchanged final comparisons produced no findings. Source-present final comparisons used actual changed text. Some source limitations, such as thinking #31's decomposition-source notice, require educator judgment about whether verification was actually necessary.
- **Density:** non-thinking returned three candidates for the short control and two for the long control; thinking returned three for each. No candidate count is prescribed, and these samples do not establish length-only causation.

**Gate C is not passed semantically.** Operational completion in non-thinking does not erase the strong-draft, authorship, and cross-stage consistency failures. The consolidated prompt remains outside production. The evaluation itself did not authorize a mode change; the user's subsequent explicit baseline-thinking decision is recorded in Section 10.

## 9. Final gates and deliverables

- **Gate A — passed:** contracts and mocked engineering, with the final suite result recorded in Section 2.
- **Gate B — not passed:** targeted semantic authorship, strong-draft, and Final-grounding concerns remain.
- **Gate C — not passed:** integrated semantic acceptance failed; two thinking harness incompatibilities are explained but leave intended paths unexercised.
- **Gate D — open:** educator recruitment/review, anchor calibration, full keyboard review, and actual screen-reader review are not complete.
- **Gate E — closed:** no deployment or runtime-default promotion was authorized or performed.

Delivered implementation and evidence include aligned contracts, scoped reference recovery, an evaluation-only consolidated candidate, repair-category analysis, 14-handoff Support and 12-scenario Coordinator targeted artifacts, full integrated diagnostics, an anchored educator review guide, and local workflow evidence. `EDUCATOR_REVIEW_PROTOCOL.md` retains the required Meets/Needs refinement/Unacceptable ratings and Critical/Major/Moderate/Minor severity categories without an aggregate quality score.

## 10. Subsequent runtime decision

After the qualitative 2×2 comparison, the user explicitly selected the **Phase 1 baseline with thinking** as the new repository default. The comparison favored that arm for student authorship and grounding, while consolidated thinking remained preferable for readability. This is a product decision, not a claim that Gates B or C passed or that learner outcomes improved. The consolidated Support prompt remains evaluation-only, non-thinking remains an explicit comparator, and deployment remains unauthorized.
