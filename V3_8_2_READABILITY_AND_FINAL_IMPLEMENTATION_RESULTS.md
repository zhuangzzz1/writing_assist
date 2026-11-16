# V3.8.2 Readability and Final-Reflection Implementation Results

## 1. Decision and evidence boundaries

The project owner explicitly authorized implementation of `V3_8_2_READABILITY_AND_FINAL_IMPROVEMENT_PLAN.md` on 2026-11-16. The candidate remains evaluation-only. This implementation does not promote or deploy it, change the local v3.8.0/v3.8.0 prompt/schema runtime, add an agent or model-driven node, restore vocabulary options or sentence starters, or authorize full 32-scenario/non-thinking diagnostics.

The authorized real-model scope is the plan's targeted thinking evaluation across `structural_current`, preserved `baseline_readable`, and `baseline_readable_v2`: 14 controlled Support handoffs, four controlled-history Final contrasts, and Coordinator-targeted strong-draft/imaginative scenarios #11/#12. Authorization ID is `v3-8-2-readability-targeted-20261116`, approver `project-owner`, with no total-token stop cap. Integrated coverage successors are considered only after targeted rubric review. Existing v3.7.x artifacts remain historical controls.

Primary performance assessment uses `EDUCATOR_REVIEW_PROTOCOL.md`: Meets / Needs refinement / Unacceptable and Critical / Major / Moderate / Minor with exact output evidence. Calls, tokens, latency, repairs, and surface readability metrics are secondary diagnostics. LLM-assisted screening is not educator approval or learner-outcome evidence.

## 2. Versioned implementation

### Prompt arms

- `baseline_readable_v2` selects `v3.8.2-baseline-readable` with schema `v3.8.0`.
- Its round Coordinator prompt preserves the v3.8.1 strong-draft and synthetic-classroom-context guidance unchanged.
- Its Final Coordinator adds guidance to credit specific interpretation, causal reasoning, authorship ownership, and source-bounded qualification; distinguish incomplete next steps from genuine regressions; and preserve real order/reasoning/structure losses. No boilerplate keyword detector or semantic regression remover was added.
- Its Support prompt adds an internal final-JSON delivery review inside the same model call: one cognitive move per sentence, explicit First/Then sequencing when needed, concrete verbs, non-idiomatic wording, non-repetition, exact-reference preservation, and usable next actions. The checklist is prompt guidance, not hidden-reasoning output or a deterministic readability validator.
- `structural_current` selects the unchanged local v3.8.0 prompts and schema for a no-vocabulary/no-starter wording control.
- `baseline_readable` and all legacy contracts remain preserved. No output-field shape changed.

### Fixtures and evaluator behavior

- `test_cases/v3/final_regression_contrasts.json`, version `v3.8.2-final-regression.1`, contains controlled-history F1 source-present, F2 source-missing, same-unchanged-goal E, and genuine organization-regression #9 anchors. Each records its source-fixture lineage.
- `test_cases/v3/readability_coverage.json`, version `v3.8.2-readability-coverage.1`, contains seven versioned successors for #15, #20, optional-language #24, clarification, and human review.
- `all_available` selects one to three actually produced candidates, applies the existing first/others self-report plan, and records available candidate count, selected IDs/references, and selection mode. Fewer than three candidates is not an application error in this mode and is not represented as two deferrals when only two goals exist. The adaptive #15 successor also uses the explicit no-revision Finish path if the Coordinator appropriately returns direct_response with no candidates.
- A separate controlled three-goal #15 prefix exercises one attempted/two deferred goals independently of candidate generation.
- The versioned #20 successor uses staged first-goal revision when a candidate exists. After `direct_response` with no candidates, its explicit `allow_direct_response_finish` contract records an alternate path and finishes without a revision snapshot. A separate controlled reviewed-revision prefix exercises Final confirmation/history independently.
- Historical fixtures and evidence were not edited in place, and no route or candidate count is forced.

## 3. Gate A — engineering verification

The focused agent/evaluator/fixture run passed **215 checks**. The complete mocked suite passed **369 checks**, up from the preserved 350-check structural baseline. `git diff --check` and JSON parsing passed for both new fixture files.

Tests cover:

- Candidate prompt selection and unchanged schema/runtime boundaries.
- Final credit for a distinct genuine improvement after a prior negative verdict, while retaining genuine organization regressions.
- Support handoff/reference preservation under the internal delivery-review prompt.
- Adaptive two-goal and controlled three-goal workflows, authoritative Final history, and self-report plans.
- Both #20 branches: direct-response Finish with one original snapshot, and staged revision/Final with two snapshots when a candidate exists.
- Fixture lineage, controlled prefixes, optional language, clarification, and human-review coverage.

Gate A establishes technical contracts only. It does not establish readability, pedagogical effectiveness, educator approval, accessibility, or semantic acceptance.

## 4. Targeted output review

Targeted thinking evaluation and rubric review are complete. The Gate B decision is recorded in Section 4.3: not passed.

### Structural v3.8.0 control

Artifacts:

- `data/evidence/v3_support_prompt_structural_current_evaluation_20261116T082209Z.json`
- `data/evidence/v3_final_regression_structural_current_evaluation_20261116T082548Z.json`
- `data/evidence/v3_coordinator_targeted_structural_current_scenarios_11_12_evaluation_20261116T082707Z.json`

All 20 targeted scenarios completed without scenario errors or schema repairs. Initial inspection shows that the structural control already uses clear First/Then sequencing in some survey actions but retains abstract connection wording and multi-step actions elsewhere. Its Final F1 output credits bounded source interpretation without regression, E preserves the unchanged-goal verdict, and #9 retains three genuine organization/reasoning regressions. F2 reports no validated improvement even though its rationale and student conclusion recognize the added interpretation, leaving a Final-credit concern.

The structural Coordinator again treats the strong draft's explicitly synthetic class discussion as an accuracy failure and requires real/hypothetical reframing. This is an Unacceptable / Critical calibration/source-responsibility failure under the reviewed anchor. It also returns only a storage/garden-tank link for the imaginative system and does not identify the missing litter-output step.

### Preserved v3.8.1 candidate

Artifacts:

- `data/evidence/v3_support_prompt_baseline_readable_evaluation_20261116T082814Z.json`
- `data/evidence/v3_final_regression_baseline_readable_evaluation_20261116T083136Z.json`
- `data/evidence/v3_coordinator_targeted_baseline_readable_scenarios_11_12_evaluation_20261116T083258Z.json`

All 20 targeted scenarios completed without scenario errors. The Support run required one bounded repair for an instructional ellipsis in a source-locating hint; this is a secondary operational diagnostic. The survey action still combines interpretation and connection in one sentence. The octopus action preserves the source-less relevance boundary, and the controlled imaginative-system handoff keeps the next step student-authored.

The Final run still adds a less-explicit-link regression on F1 despite crediting bounded interpretation. F2 has no regression but also no validated improvement; its conclusion recognizes the student's own interpretation while the Coordinator withholds improvement credit by extending the prior negative verdict to the changed goal text. E remains consistent and #9 retains the genuine regressions.

Strong-draft #10 correctly receives direct_response. In this fresh run, imaginative #12 also receives direct_response with no issues, so the earlier litter-output goal was not reproduced. Because the missing material destination can leave an important process output unexplained, this is a meaningful-selection concern for review, not something to override with a forced route or rerun. The controlled Support handoff still exercises delivery of that goal independently.

### v3.8.2 candidate and Gate B decision

Artifacts:

- `data/evidence/v3_support_prompt_baseline_readable_v2_evaluation_20261116T083313Z.json`
- `data/evidence/v3_final_regression_baseline_readable_v2_evaluation_20261116T083714Z.json`
- `data/evidence/v3_coordinator_targeted_baseline_readable_v2_scenarios_11_12_evaluation_20261116T083841Z.json`
- Rubric record: `data/evidence/v3_8_2_targeted_rubric_screening_20261116T084042Z.json`

All 20 targeted scenarios completed without scenario errors or schema repairs. This operational result does not determine quality.

**Positive targeted findings:**

- Support Anchor B separates survey interpretation and connection into two short sentences; Anchor C uses a concrete why-included task without an unsupported mechanism; Anchor D controlled Support preserves concrete oral rehearsal and student authorship. All 20 reviewed Support candidates preserve authorship, source limitations, exact references, and cross-field coherence. Screening rates targeted Support action readability **Meets**, with residual Minor concerns about some longer hint sentences and terminology such as “sensory detail.”
- F1 credits exact source/count and bounded-interpretation improvements, reports no regression, and places the incomplete claim link in future_areas: **Meets**.
- E preserves the unchanged-goal verdict with no improvement or regression: **Meets**.
- Strong-draft A receives direct_response without treating synthetic classroom context as an accuracy failure: **Meets**.

**Negative/mixed targeted findings:**

- F2 still reports zero validated improvements. Its rationale explicitly says the added interpretation is not reported because goal_1 remains `improvement_not_yet_evident`, even though the added interpretation differs from the exact old goal reference. The Final Support conclusion recognizes the student's own thinking informally, but this does not satisfy the planned improvement-credit requirement: **Needs refinement / Moderate** in screening, subject to educator severity calibration.
- Imaginative Coordinator D returns direct_response and calls the process sequence complete despite the unexplained destination of lifted leaves/wrappers. The earlier litter-output goal was not reproduced in this fresh v3.8.1/v3.8.2 pair. Controlled Support delivery remains successful but does not prove Coordinator selection: **Needs refinement / Moderate**.
- #9 retains sequence and audit-to-choice regressions but adds an improvement for the tracking causal caveat and omits the separate tracking-purpose regression expected by the fixture. This may be a defensible distinct gain, but it leaves the planned regression-preservation expectation unmet and requires expert review: **Needs refinement / Moderate**.

**Gate B is not passed.** V3.8.2 improves the targeted Support wording and F1, but does not satisfy F2 credit, Anchor D selection, or complete #9 regression preservation. No Critical/Major issue was assigned in this LLM screening; three Moderate concerns remain and the explicit behavioral requirements fail. This is not educator approval or a promotion recommendation. The candidate remains evaluation-only.

## 5. Secondary operational diagnostics

Across the 20 targeted scenarios per arm:

| Arm | Calls | Schema repairs | Observed total tokens | Recorded model latency |
| --- | ---: | ---: | ---: | ---: |
| Structural v3.8.0 | 26 | 0 | 121,161 | 364.305 s |
| V3.8.1 | 25 | 1 | 112,520 | 297.066 s |
| V3.8.2 | 24 | 0 | 123,843 | 345.032 s |

There were no targeted reference/framework normalizations. V3.8.2 Support had 20 candidates, no >38-word actions, mean/max action sentence lengths of 11.93/19 words, one exact hint/stuck repetition flag, and five action/self-check review flags. These surface flags were manually reviewed and did not determine ratings. Resource differences are single-run observations, not quality improvements. Exact per-call details and token composition remain in the nine artifacts.

## 6. Integrated coverage successors

Coverage runs began after targeted rubric review and do not override Gate B.

### Structural v3.8.0

Artifact: `data/evidence/v3_readability_coverage_structural_current_evaluation_20261116T084144Z.json`

Seven scenarios completed without scenario errors. Adaptive #15 produced and selected one actual goal, completed revision/Final, and recorded one attempted report without claiming two deferrals. Controlled #15 supplied three goals and exercised one attempted/two deferred reports with three authoritative observations and Final history. Generated #20 produced a candidate and completed staged revision/Final; controlled reviewed-revision #20 also completed Final with authoritative history. Optional-language #24 returned direct_response with no issues. Human review returned concerning_content with empty ordinary assessment and bypassed revision/Final.

Clarification #30 asked a second question and then validly routed to Support after the second unclear answer because the Coordinator no longer requested clarification. It did not exercise `clarification_limit`; the deterministic boundary remains covered by mocked tests and previous controlled probes. No route was forced.

One controlled-#15 Support response was incomplete JSON and repaired successfully. This is a secondary diagnostic. Exercised revision observations were text-grounded and deferred goals retained neutral carry-forward. These limited path findings do not erase structural Anchor A/D/F2 failures.

### V3.8.1 and v3.8.2

Artifacts:

- `data/evidence/v3_readability_coverage_baseline_readable_evaluation_20261116T084532Z.json`
- `data/evidence/v3_readability_coverage_baseline_readable_v2_evaluation_20261116T084915Z.json`
- Coverage rubric review: `data/evidence/v3_8_2_coverage_rubric_review_20261116T085413Z.json`

Both arms completed all seven scenarios without scenario errors or reference/framework normalizations. Each had one bounded repair: v3.8.1 clarification #30 initially returned Support with an empty working genre; v3.8.2 adaptive #15 revision Coordinator returned valid JSON followed by trailing ` clarify: undefined`. These are secondary diagnostics, not quality scores.

Adaptive #15 produced two candidates in both readability arms and correctly recorded one attempted/one deferred report rather than requiring three. Controlled #15 exercised one attempted/two deferred goals and authoritative Final history. Generated #20 returned direct_response in both readability arms and used the explicit no-revision Finish path with an unchanged, empty Final comparison; controlled reviewed-revision #20 independently completed Final and credited the exact added focus benefit. Structural's generated #20 exercised the alternate staged-revision branch. All arms returned direct_response without mechanics goals for #24 and simulated concerning-content human review without revision/Final.

All three clarification runs asked twice and then validly selected Support after the second unclear answer; none exercised real-model `clarification_limit` because the Coordinator no longer requested clarification. The deterministic boundary remains covered by mocked tests and prior controlled probes. Adaptive #15 did not exercise its direct-response option because candidates existed; that generic logic is mocked, and both readability arms exercised it on #20.

**New v3.8.2 semantic finding:** adaptive #15 revision accurately retains goal_1 as not-yet-evident for the unresolved garden-benefit connection while noting the separate new opening reason. Final then reports zero improvements and says the opening change is part of that negative reviewed goal text, even though the actual selected reference is the later garden-benefit sentences. Structural and v3.8.1 both credit the exact opening improvement. This repeats F2's over-application of prior negative verdicts to different text and is **Needs refinement / Moderate** under Final reflection. It is a candidate decrease relative to both controls on this path.

V3.8.2 controlled #15/#20 Final outputs are otherwise grounded, revision observations are goal-specific and neutral, and no-source/human-review controls remain intact. None of these positives erases the Final-credit failure or targeted Gate B failures.

**Gate C passes for this seven-scenario versioned coverage set only.** Actual paths and unexercised alternatives are recorded, no counts/routes were forced, and controlled three-goal/reviewed-revision coverage completed. This is not full 32-scenario acceptance, semantic Gate B acceptance, educator approval, or promotion.

## 7. Open gates and rollback

- **Gate B:** not passed; targeted F2 credit, imaginative Coordinator selection, and complete #9 regression preservation remain unresolved, and integrated #15 adds another Final-credit omission under the educator rubric.
- **Gate C:** passed only for the seven-scenario versioned successor set, with explicit alternate paths and limitations; full 32-scenario acceptance remains unevaluated.
- **Gate D:** open; educator/ELD calibration, target-age EL research, and actual keyboard/screen-reader checks remain separate.
- **Gate E:** open; promotion, local-default changes, non-thinking adoption, full diagnostics, sentence-starter restoration, and deployment each require separate decisions.
- Rollback is to leave `baseline_readable_v2` unused. Local v3.8.0 behavior is unchanged. Preserve all successful, mixed, and failed artifacts; do not delete evidence or reset the dirty worktree.

## 8. Targeted v3.8.3 regression follow-up

The project owner requested a targeted revision for the Regression handling gap after comparing v3.8.0, v3.8.1, and v3.8.2. The evaluation-only `regression_readable` arm selects `v3.8.3-regression-readable` with schema `v3.8.0`. It preserves v3.8.2 as a control, keeps its round Coordinator and Support prompts unchanged, and adds only a Final Coordinator contextual purpose-loss check. The guidance distinguishes a reasonable causal qualification from wording that undermines an original monitoring, evidence-gathering, or reasoning step. It explicitly prevents credit for a valid caution from suppressing a distinct purpose-loss regression. No keyword detector, output-field change, additional agent, runtime promotion, or deployment was added.

The focused prompt/arm tests and full mocked suite pass **371 checks**, up from the preserved 369-check v3.8.2 baseline. These checks establish prompt selection and unchanged schema/round/Support contracts, not semantic improvement.

Matched thinking artifact: `data/evidence/v3_final_regression_regression_readable_evaluation_20261116T154531Z.json`. The four controlled-history Final scenarios completed with eight calls, zero scenario errors, and zero schema repairs. It recorded 23,494 total tokens and 71.142 seconds of model latency; these are secondary single-run diagnostics, not quality scores.

| Anchor | Preserved v3.8.2 result | v3.8.3 result | Targeted screening |
| --- | --- | --- | --- |
| #9 genuine regressions | Preserved sequence and audit-to-choice losses but omitted the separate tracking-purpose loss | Two findings cover all three loss types: the first combines reversed sequence and audit-to-choice reasoning, and the second preserves the tracking-to-choice purpose loss. The valid causal caution remains a separate improvement, and Support renders both regression findings. | **Meets for Regression handling on this reviewed anchor**; semantic coverage matters rather than requiring three separate findings |
| F1 bounded interpretation | Two improvements, no regression, incomplete claim link in future areas | Preserves the same substantive behavior with exact source/count and bounded-interpretation improvements and no regression | **Meets** |
| E unchanged goal | No improvements or regressions | No improvements or regressions; exact negative-verdict consistency remains | **Meets** |
| F2 student interpretation | Zero validated improvements despite added interpretation | Still zero validated improvements, although the rationale acknowledges the more specific student interpretation | **Needs refinement / Moderate**; unresolved Final-credit failure |

This is an observed improvement in the matched #9 regression output, not proof of stable causal attribution from one thinking run per arm. F2 remains unresolved, imaginative Coordinator selection was not rerun, integrated #15 Final credit was not rerun, and full 32-scenario/non-thinking behavior remains unevaluated. **Targeted Regression handling improved on this reviewed run, but Gate B remained not passed and v3.8.3 was evaluation-only at that stage.** Section 9 records the later promotion decision and the default-runtime result that did not reproduce the tracking-purpose finding.

## 9. Local v3.8.3 promotion and default-runtime verification

After reviewing the version comparison, the project owner explicitly chose to promote v3.8.3 as the best current option despite its unresolved limitations. Local prompt/schema are now **`v3.8.3`/`v3.8.0`**. The default Coordinator round, Coordinator Final, and Support round prompts carry the v3.8.3 behavioral guidance with `LOCAL RUNTIME CONTRACT` labels. The byte-preserved `v3.8.3-regression-readable` evaluation arm retains its original `EVALUATION CANDIDATE` labels, and `structural_current` explicitly selects the preserved v3.8.0 prompts. V3.8.2 remains an evaluation control. This is a local product promotion, not a Gate B pass, educator approval, full acceptance, or deployment.

The promoted default-agent contract is covered by the full mocked suite: **372 checks pass**. `PROMPT_VERSION` is `v3.8.3`; the schema remains `v3.8.0`.

A separate real-model check used `create_writing_assistant_service` without Coordinator or Support prompt overrides on controlled Final #9. Artifact: `data/evidence/v3_final_regression_runtime_default_scenario_04_evaluation_20261116T160207Z.json`. It confirms default-runtime metadata `v3.8.3`/`v3.8.0`, two calls, zero scenario errors, and zero schema repairs. The output credits the causal caution and reports sequence and audit-to-choice regressions, but **omits the tracking-purpose regression** found in the earlier v3.8.3 evaluation-arm run. The student-facing reflection preserves only the two reported regressions.

The positive evaluation-arm result and negative default-runtime result must both be preserved. Regression handling is therefore **mixed across runs**, not stably Meets. The promotion decision remains in effect per the owner's explicit choice, but it does not resolve F2, establish stable #9 behavior, pass Gate B, or authorize deployment. No additional rerun was used to overwrite this negative evidence.
