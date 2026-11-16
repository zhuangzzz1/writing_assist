# V3 Baseline Readability and Structural Implementation Results

## 1. Decisions and evidence boundaries

The open decisions in `V3_BASELINE_READABILITY_IMPROVEMENT_PLAN.md` were resolved through an explicit `grill-me` review before behavioral implementation.

- Local prompt/schema `v3.8.0` adopts only the structural contract: Final history and exact-link guards plus removal of generated vocabulary options, sentence starters, and the Coordinator `reasoning_operation` classification. The user removed the first two features throughout V3 because prior tests did not show enough writing-improvement value to offset cognitive load. The classification had no remaining consumer.
- Thinking remains the local runtime mode. No automatic mode switch, deployment, or deletion of historical data/evidence occurred.
- The v3.7.1/v3.7.0 prompts and output contracts remain available as evaluation controls. Historical stored responses keep their old fields; the new UI and runtime do not generate or display those scaffolds.
- `v3.8.1-baseline-readable` is the current evaluation-only candidate after the v3.8.0 candidate's semantic failure described below. Its readability budgets are prompt guides, not validators or quality thresholds. Its meaningful-issue and synthetic-classroom-context Coordinator wording is not promoted into the local default.
- The authorized real-model scope is thinking-only: 14 Support handoffs, 12 Coordinator-targeted scenarios, and integrated acceptance #7/#9/#10/#11/#15/#20/#24/#30, each for `current` and `baseline_readable`. Non-thinking candidate behavior was not evaluated. Full 32-scenario diagnostics require a later decision.
- Call caps are 35 per Support run and 75 per Coordinator/integrated run, with no token stop cap. Authorization ID `baseline-readability-thinking-targeted-20261115`, approver `project-owner`.
- Per the user's follow-up decision, implementation performance is assessed primarily with the educator review rubric. Calls, tokens, latency, repairs, and descriptive surface metrics are secondary diagnostics, not measures of pedagogical quality.

These decisions supersede the plan's original both-mode and unchanged-baseline comparison details. They do not establish educator approval, pedagogical effectiveness, learner outcomes, accessibility completion, or semantic acceptance.

## 2. Implemented structural contract

- `langgraph_core/state.py` declares typed Final `revision_history` entries and initializes them in `make_review_state`.
- `langgraph_core/revision.py` builds history from persisted snapshots and the latest successful Coordinator review matching each snapshot. Entries contain revision/snapshot/review identity, a SHA-256 draft hash, exact selected-goal references and locations, and authoritative Coordinator `status`, `observation`, `evidence_reference`, and `carry_forward`. Support goal-feedback paraphrases are not substituted. Older rounds without observations use empty status/observation and null carry-forward.
- `WritingAssistantService.finish_composition` populates this history for both app and evaluator before persisting the Final input. The Coordinator Final payload includes the history and final-draft hash.
- The Final Coordinator prompt requires prior-verdict consistency and full-draft verification before deletion, weakening, or contradiction claims.
- Deterministic improvement rejection requires all of: latest reviewed hash equals Final hash, matching goal ID, exactly equal goal reference, and latest `improvement_not_yet_evident` or `uncertain`. Goal ID alone, partial wording, different draft hashes, unrelated improvements, prior `specific_improvement`, and empty Final goal IDs do not trigger the guard.
- Deletion-worded regressions are rejected when their exact original reference remains verbatim in Final. Semantic weakening is not deterministically inferred. Existing exact-membership, unchanged-draft, changed-text-overlap, bounded-repair, and no-Final-normalization rules remain.
- Local v3.8.0 prompts and Pydantic models omit and reject `vocabulary_options`, `sentence_starter`, and `reasoning_operation`. Separate legacy models and prompt constants support only versioned historical evaluation arms. Obsolete UI display code was removed.
- `baseline_readable` selects the candidate Coordinator and Support prompts with schema v3.8.0. `current` and the historical experiment arms explicitly retain their v3.7.x contracts.

## 3. Readability candidate and descriptive metrics

The Support candidate adds plain-language budgets, replaces rigid claim anchoring and the long nested instruction example, separates the jobs of revision action/hints/self-check/stuck step, and requires physically clear directions. The Coordinator candidate adds meaningful-issue and synthetic/shared-classroom-context guidance without fixture-label routing or an educator-approved threshold claim.

`scripts/readability_metrics.py` adds scenario- and arm-level:

- mean/max words per sentence and sentence/word counts for `why_it_matters`, `revision_action`, hint steps, and `stuck_step`;
- total action-word counts and the documented >38-word review heuristic;
- exact-duplicate and high-content-overlap repetition review flags across action, individual hint steps, self-check, and stuck step;
- numeric-anchor and low-content-overlap action/self-check scope review flags.

These are descriptive heuristics for human review, not automatic semantic failures, educator ratings, Flesch–Kincaid grade levels, or a pedagogical-quality score. Rubric screening is the primary performance assessment; operational errors, repairs, tokens, and latency are secondary diagnostics.

## 4. Mocked verification

The pre-implementation dirty-worktree baseline passed 325 checks. After the structural, candidate, evaluator, compatibility, and metrics changes, the suite passed 347 checks. With the controlled Final-history fixture and mocked payload tests, the final full suite passes **350 checks**. Coverage includes persisted two-revision Final contradiction repair, prior `specific_improvement`, unrelated improvements, uncertain and empty-goal-ID cases, different draft hashes, the later-start deletion case, semantic-weakening non-rejection, legacy history compatibility, legacy v3.7.x evaluation controls, new-field rejection, and metrics deduplication/interpretation boundaries.

Mocked checks establish engineering behavior only. Gates B and C require actual output review; Gates D and E remain separate.

## 5. Educator-rubric screening

Primary assessment now uses `EDUCATOR_REVIEW_PROTOCOL.md` Sections 6–9: **Meets / Needs refinement / Unacceptable** and **Critical / Major / Moderate / Minor**. The ratings below are LLM-assisted screening of actual outputs, not educator assessments or learner-outcome evidence. Calls, tokens, and latency are secondary diagnostics only and do not determine any rating. Surface metrics help locate possible issues but do not assign ratings.

Screening artifact: `data/evidence/v3_baseline_readability_rubric_screening_20261116T070407Z.json`. It contains exact scenario IDs, evidence, paired anchors, and coverage limitations; all cited IDs were validated against the reviewed artifacts. `V3_BASELINE_READABILITY_EXPERT_REVIEW.md` packages the prompt/logic comparison, exact output excerpts, rubric findings, and reviewer template into a self-contained expert-review document.

### Candidate v3.8.1 dimension ratings

| Dimension | Screening | Severity and evidence |
| --- | --- | --- |
| Student authorship | **Meets** | Students generate the target ideas and language; the imaginative-system destination remains student-authored. No generated vocabulary/frame or target-response leak was found in v3.8.1. |
| Source responsibility | **Meets** | The corrected octopus guidance asks about relevance, not an unsupported heart mechanism. Later-start outputs do not verify the unavailable passage; survey findings remain bounded to supplied counts and meaning. |
| Hint guidance | **Meets** | Exact references, 3–5 concept/procedural items, and useful related self-checks remain intact. Length concerns are rated separately rather than hidden here. |
| Cross-field coherence | **Meets** | Reviewed action, hints, self-check, and stuck step address the same move. Automated flags included benign paraphrases and were not counted as mismatches; the earlier first-person check was corrected. |
| Multilingual readability/tone | **Needs refinement — Moderate** | Tone is respectful, but some action fields still combine locating, interpreting, and connecting. The survey explanation and sentence-boundary cases remain less manageable despite improved long-action/repetition heuristics. |
| Density, proportionality, meaningful task selection | **Meets** | Strong-draft #10 and optional-language #24 receive direct responses. Two meaningful goals on #15 are preferable to manufacturing a third; the scripted mismatch is a coverage limitation, not a quality failure. |
| Revision observation accuracy | **Meets — exercised paths only** | Exercised observations are grounded and neutral. No rating is claimed for unexercised #15/#20 revision observations. |
| Regression handling/Final reflection | **Needs refinement — Moderate** | Exact-verdict and retained-opening contradictions are resolved, but the less-explicit-link regressions on source-present #8 and the later-start probe may be optional criticism rather than meaningful regressions. Educator calibration is needed. |
| Navigation independence | **Not assessed** | Model artifacts do not establish independent student navigation or full-keyboard usability. |
| Accessibility | **Not assessed** | Actual screen-reader/full-keyboard checks remain open. |

**Overall candidate screening: Needs refinement.** No unresolved Critical issue was found in the reviewed v3.8.1 sample, but Moderate readability and Final-meaningfulness concerns prevent a general Meets judgment. This is not an educator gate result and does not authorize candidate promotion.

### Paired rubric anchors

- **Octopus source-less relevance:** v3.8.0 was **Unacceptable / Critical** because it requested an unsupported real-world mechanism. V3.8.1 is **Meets** because it asks how the existing fact fits the student's central idea.
- **Strong-draft synthetic discussion:** the current integrated control was **Unacceptable / Critical** because it manufactured an accuracy issue and demanded real testimony from an explicitly synthetic task. The candidate is **Meets** with `direct_response` and no issues.
- **Unchanged goal after a negative prior verdict:** the control's initial Final response was **Unacceptable / Critical** for fabricated improvement; deterministic repair brought it to **Meets**. The candidate's initial response was **Meets** without that contradiction.
- **Retained later-start opening:** both arms are **Meets** for not claiming deletion. The separate less-explicit-link regression remains **Needs refinement / Moderate** for meaningfulness.
- **Readability:** both arms remain **Needs refinement / Moderate**. The candidate does not earn a general readability advantage merely from fewer long-action flags or lower resource use.

### External expert review of the packet

The project owner supplied external expert feedback on `V3_BASELINE_READABILITY_EXPERT_REVIEW.md`. This is genuine external review input, but not a completed three-reviewer educator protocol or a target-age learner study.

The expert's decision was **Mixed Results — Do Not Promote Candidate v3.8.1 Yet**:

- Agreed that the candidate improves strong-draft calibration, Final-verdict consistency, and the meaningful imaginative-system output goal.
- Found v3.8.1 source responsibility equivalent to the control after the v3.8.0 octopus correction.
- Found the control preferable on Final-regression restraint and arguably clearer sequencing/wording in the survey and octopus examples.
- Kept both arms at **Needs refinement / Moderate** for general readability and identified the candidate's stacked clauses, idioms, repetition, and abstract nominalization.
- Considered F2 potentially **Major**, rather than only the LLM screening's Moderate, because the candidate reported zero improvements and one regression after the student added substantive causal reasoning. The control also reported a less-explicit-link regression on F2, but credited two genuine improvements; it is better in balance, not a fully correct model of regression restraint.
- Recommended retaining the calibration/consistency improvements in a next iteration while fixing Final criteria and EL readability before promotion.
- Warned that removing all sentence starters has both cognitive-load benefits and potential lower-proficiency EL costs. The experiment cannot isolate wording effects from scaffold/schema removal; restoration remains a separate ELD/product decision.

`V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` records the resulting iteration. Its engineering implementation is now evaluation-only; adoption remains undecided and depends on separate output, coverage, human-review, and product gates.

Coverage is reported separately: candidate integrated #15/#20 revision/Final paths were not exercised, candidate non-thinking and full 32-scenario behavior are unknown, and educator/accessibility gates remain open. These limitations are not converted into quality scores.

## 6. Operational and descriptive Support details

### Current v3.7.1/v3.7.0 control

Artifact: `data/evidence/v3_support_prompt_evaluation_20261116T045506Z.json`.

- 14/14 scenarios completed with no scenario errors.
- 14 model calls and zero schema repairs.
- 92,191 observed total tokens: 43,655 prompt, 48,536 completion, including 39,695 reasoning tokens.
- 258.475 seconds recorded model latency.
- 20 candidates; six revision actions exceeded the descriptive 38-word heuristic.
- Mean/max words per sentence: `why_it_matters` 22.77/46; `revision_action` 10.01/24; hint steps 13.99/28; `stuck_step` 13.49/23.
- Zero repetition review flags and 15 action/self-check scope review flags. These flags are not semantic failure counts.

### First v3.8.0-baseline-readable candidate

Artifact: `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T045953Z.json`.

- 14/14 scenarios completed with no scenario errors, 14 model calls, and zero schema repairs.
- 68,699 observed total tokens: 39,063 prompt, 29,636 completion, including 22,757 reasoning tokens.
- 169.506 seconds recorded model latency.
- 20 candidates; three revision actions exceeded the descriptive 38-word heuristic, down from six in this control run.
- Mean/max words per sentence: `why_it_matters` 19.91/29; `revision_action` 11.26/22; hint steps 14.91/26; `stuck_step` 16.35/23.
- One repetition review flag and six action/self-check scope review flags. The scope heuristic includes benign differences such as an action quoting 62% while its same-scope check says “the survey”; flag counts are not semantic failure counts.
- Relative to this single control, `why_it_matters` was shorter and long actions/scope flags decreased, but action, hint-step, and stuck-step mean sentence lengths increased. Token and latency reductions are observed operational differences, not proof of a readability or pedagogical improvement.

Semantic review rejected this candidate without promotion:

- In the source-less octopus handoff, the Coordinator finding requested relevance to the central idea. The candidate instead asked what the three hearts do for the octopus, inviting a real-world mechanism not present in the draft or a supplied source. The control asked why the fact belongs with the student's point. This is a Support-authored source-boundary regression, not a requirement inherited from the frozen finding.
- One narrative self-check used “Does my added detail…” instead of student-facing second person. This is a minor cross-field/tone issue, not a schema failure.
- Other reviewed candidates generally preserved exact references and student authorship, but this sample does not establish semantic acceptance or educator approval.

### Follow-up v3.8.1-baseline-readable candidate

The candidate adds source-bound elaboration guidance: without verifiable source material, relevance goals must use the student's existing central idea/details or invite a source rather than request a new real-world mechanism. It also requires second-person instructions and self-checks while preserving first-person exact quotations. The full mocked suite remains at 347 checks.

Artifact: `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T050701Z.json`. Paired comparison record: `data/evidence/v3_support_prompt_readability_comparison_20261116T051500Z.json`.

- 14/14 scenarios completed with no scenario errors, 14 model calls, and zero schema repairs.
- 76,152 observed total tokens: 41,275 prompt, 34,877 completion, including 27,777 reasoning tokens.
- 199.902 seconds recorded model latency.
- 20 candidates; two revision actions exceeded the descriptive 38-word heuristic.
- Mean/max words per sentence: `why_it_matters` 16.45/29; `revision_action` 11.44/25; hint steps 15.64/31; `stuck_step` 17.20/22.
- Zero repetition review flags and 13 action/self-check scope review flags. Some numeric-anchor flags are benign same-scope paraphrases; they require review and are not failures.
- The octopus action now asks how the existing fact connects to the student's main idea, and its stuck step asks why the writer included it. The unsupported mechanism request is gone. The narrative self-check now uses second person. Source limitations and exact references remain intact.
- The reviewed known vocabulary controls show no target-content vocabulary leak: `warrant` appears only in a goal ID; `focus`/`removed` occur in ordinary task wording tied to existing draft content, not generated vocabulary support. No `cozy`, `pump`, `supply`, `creak`, `glimpse`, `flutter`, or `hush` target options exist because the candidate schema has no vocabulary field.
- Readability is still mixed rather than uniformly improved: `why_it_matters`, long-action count, and repetition improved relative to this control, while action/hint/stuck means increased and scope flags remained substantial. The v3.8.1 sample has no unresolved critical Support issue in this review, but it does not establish Gate B, educator approval, or a general readability outcome.

The failed v3.8.0 artifact remains preserved as a negative experiment. The v3.8.1 candidate remains evaluation-only.

## 7. Coordinator-targeted and small integrated comparisons

### Coordinator current v3.7.1/v3.7.0 control

Artifact: `data/evidence/v3_coordinator_targeted_evaluation_20261116T051145Z.json`.

- 12/12 scenarios completed with no scenario errors.
- 39 model calls and zero Coordinator or Support schema repairs.
- 207,540 observed total tokens: 118,683 prompt, 88,857 completion, including 69,959 reasoning tokens.
- 498.667 seconds recorded model latency.
- Zero issue/framework location normalizations.
- Final history contains the authoritative prior verdicts and exact selected-goal references. The unchanged-original/final #10 comparison has no improvements or regressions. Source-present #8 reports grounded improvements; source-missing #9 reports an improvement on different changed text rather than automatically converting the prior negative verdict on the old goal reference.
- The #9 regression says the explicit sentence `This supports our plan.` was removed. That exact sentence is absent from Final, so this output is not the earlier false claim that the unchanged `Our school should start later.` opening disappeared. Its semantic necessity still requires review; it is not rejected by the narrow verbatim-deletion guard.
- Acceptance strong-draft #10 (targeted #11) still receives a reasoning issue about the relationship among the quiet-period reason, interruption evidence, and scheduled period. The baseline therefore retains the questionable strong-draft behavior that the candidate must address.
- Targeted #3 routed to Support after one answer rather than early teacher review; #4 produced deterministic `clarification_limit` only after the second unclear answer; #5 returned concerning-content teacher review with empty ordinary assessment collections. Framework, source, and repeated-reference paths completed without operational repair. Semantic review continues with the paired candidate and integrated set.

### Coordinator baseline-readable candidate

Artifact: `data/evidence/v3_coordinator_targeted_baseline_readable_evaluation_20261116T051659Z.json`. Paired comparison record: `data/evidence/v3_coordinator_targeted_comparison_20261116T052000Z.json`.

- 12/12 scenarios completed with no scenario errors.
- 36 model calls and zero Coordinator or Support schema repairs.
- 183,172 observed total tokens: 108,473 prompt, 74,699 completion, including 59,625 reasoning tokens.
- 428.354 seconds recorded model latency.
- Two deterministic unique-issue location normalizations and zero framework normalizations; these are recorded corrections, not model repairs.
- Acceptance strong-draft #10 (targeted #11) receives `direct_response`, three observable strengths, no issues, and a rationale that the assignment is fulfilled without a meaningful actionable issue. The synthetic class discussion is not treated as an accuracy problem. CER #6 also appropriately receives `direct_response` with exact present coverage for Claim, Evidence, and Reasoning rather than a manufactured issue.
- Source-missing #9 reports a bounded improvement for the added `which is my own interpretation of the evidence` label with an empty goal ID and no regression. It does not misclassify the same old goal text as improved and does not repeat the earlier false later-start deletion. Unchanged #10 remains empty.
- Source-present #8 retains a text-accurate but debatable regression: the final replaces the explicit `This supports our plan.` with a bounded interest statement, leaving the argumentative link implicit. This is not a verbatim-deletion contradiction, and the reflection acknowledges the trade-off, but whether it is a meaningful regression or optional criticism remains an educator-review question rather than a Gate B pass claim.
- Imaginative #12 identifies the missing litter-output step. Student-facing guidance asks where the lifted material goes without supplying a destination or target mechanism; the student must invent that process step. This is consistent with the fixture's intended unexplained-output focus.
- Targeted #3 asks another clarification after one answer rather than escalating early; #4 reaches deterministic `clarification_limit` after two unclear answers; #5 preserves empty ordinary assessment collections.
- Relative to the control, this run used three fewer calls, 24,368 fewer tokens, and 70.313 fewer seconds of model latency. These are operational observations from one thinking run per arm, not proof of semantic or pedagogical superiority.

The candidate improves the sampled strong-draft and later-start behaviors, but integrated #20 and the remaining regression set still determine whether Gates B/C can be considered. The source-present Final meaningfulness caution remains open.

### Small integrated comparisons

Current control artifact: `data/evidence/v3_acceptance_scenarios_07_09_10_11_15_20_24_30_evaluation_20261116T052138Z.json`.

- Eight records completed with no scenario errors, 38 calls, two Support repairs, 215,215 total tokens, and 541.760 seconds model latency.
- Repairs were invalid JSON on #7 and a legacy unapproved sentence starter on #11. These are historical-contract behaviors, not v3.8.0 candidate outputs.
- Strong-draft #10 still receives an accuracy issue tied to the synthetic class discussion. Final history is populated on the exercised paths; #20 has a prior specific improvement and a consistent Final improvement.

Candidate artifact: `data/evidence/v3_acceptance_baseline_readable_scenarios_07_09_10_11_15_20_24_30_evaluation_20261116T052528Z.json`.

- Eight records were produced with 26 calls, one Support repair, 138,876 total tokens, and 344.744 seconds model latency.
- The repair was invalid JSON on #15. There were no Coordinator repairs or reference/framework normalizations.
- Strong-draft #10 and optional-language #24 appropriately receive `direct_response` with no issues. #30 reaches deterministic `clarification_limit` after two unclear answers. The control instead returned Support after its second answer; that is valid because it did not request a third clarification, not an application failure.
- #7 and #9 preserve grounded Final findings; #7 does not turn the prior not-yet-evident third goal into a same-reference improvement. #11 reports the actual narrative addition without regression.
- **Fixture-selection incompatibilities:** #15 returned two meaningful candidates after its repaired Support response, but the frozen script requires three; #20 returned `direct_response` with no candidate, so the scripted first-goal revision cannot start. No candidate count or route was forced, and no rerun attempted to override those judgments. These paths did not create snapshots or Final comparisons for #15/#20.
- Consequently, candidate integrated Gate C is not passed. The two incompatibilities are explained, but intended #15/#20 revision/Final paths remain unexercised in this run. A separate controlled Final-history probe was authorized to test the #20-style contradiction without changing frozen fixtures or forcing the initial route.

### Controlled Final-history probes

A separate `v3.8.0-final-history.1` fixture set contains two synthetic controlled-prefix cases: the same unchanged reading-corner goal after `improvement_not_yet_evident`, and the retained later-start opening with unavailable source verification. Mocked end-to-end tests verify snapshot/review identity, hashes, exact references, and use of the authoritative Coordinator observation rather than the Support paraphrase.

Artifacts:
- Current: `data/evidence/v3_final_history_evaluation_20261116T065550Z.json`.
- Candidate: `data/evidence/v3_final_history_baseline_readable_evaluation_20261116T065550Z.json`.
- Combined integrated/probe comparison: `data/evidence/v3_baseline_readability_integrated_and_final_comparison_20261116T065700Z.json`.

Results:
- Both arms completed both scenarios with no scenario errors.
- Current used five calls, one Coordinator repair, 11,322 tokens, and 37.674 seconds model latency. Its initial reading-corner Final response called the exact unchanged goal text an improvement after the prior not-yet-evident verdict; deterministic validation rejected it and the repaired output had no improvements. This is direct evidence that the exact-link guard catches the contradiction.
- Candidate used four calls, zero repairs, 10,609 tokens, and 40.532 seconds model latency. It did not report the same-goal improvement. Fewer calls/tokens did not reduce latency in this pair, so no performance claim is made.
- Neither arm claimed that the retained `Our school should start later.` opening disappeared. The candidate later-start comparison reports only a text-accurate less-explicit-link regression for replacing `This supports our plan.`; this is not a deletion false positive, and its meaningfulness remains subject to review.
- The controlled #20-style contradiction and later-start deletion targets are therefore exercised and resolved in these outputs. This does not erase the integrated #20 path incompatibility or pass Gates B/C by itself.

## 8. Rollback and open gates

- The readability/grounding candidate is disabled by default: do not select `--experiment-arm baseline_readable`. Local runtime does not select candidate prompt arms automatically.
- Preserve all artifacts and databases under `data/`; do not delete evidence as a rollback mechanism.
- Reverting the adopted local structural contract would require a separate explicit product decision and exact retest. Restore the v3.7.x default prompts/models through the preserved legacy constants and `legacy_contract` paths, restore v3.7.x version metadata, and separately review the Final-history/guard changes rather than hiding them through prompt selection. Do not use a destructive git reset on the dirty worktree.
- Older stored responses need no data deletion or schema reset; historical fields remain persisted but are not requested by new v3.8.0 reviews.
- Gate A passes with 350 mocked checks. Gate B remains open under the educator rubric: v3.8.1 has no unresolved Critical issue in the reviewed sample, but multilingual readability/tone and Final-regression meaningfulness remain unresolved. LLM screening rated these Moderate; external expert feedback considered F2 potentially Major. Educator calibration is still required. Gate C is not passed because candidate integrated #15/#20 revision/Final paths were not exercised. Gates D and E remain separate.
- Candidate non-thinking, full 32-scenario diagnostics, educator review, actual screen-reader/full-keyboard checks, candidate prompt promotion, and deployment remain uncompleted and unauthorized without the relevant later decisions.
