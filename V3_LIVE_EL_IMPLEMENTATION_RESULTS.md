# V3 Live EL Improvement — Implementation and Investigation Results

**Date:** 2026-11-15<br>
**Base commit:** `cc4ca35`; evaluated code was an uncommitted working tree<br>
**Original investigation prompt/schema:** `v3.6.5` / `v3.6.3`; Section 14 separately records the later `v3.6.6`–`v3.6.8` exact-text check<br>
**Original investigation fixtures:** student presets and acceptance `v3.4.0`; live-EL contrasts `v3.6.0-live-el.1`<br>
**Status:** Engineering implementation and bounded investigation completed. The integrated acceptance and human gates are not all passed. No deployment of the investigated working tree occurred.

## 1. Implemented scope

- EV: revisions can select one to three goals by explicit 1-based indices or exact candidate references. Duplicate, unknown, ambiguous, and out-of-range selections fail without fallback. Evidence records requested and actual IDs, titles, and exact references.
- Evaluation harness: added `live_el` fixtures, controlled initial/first-revision prefixes persisted without setup calls, Support-only controlled handoffs, six explicit experiment arms, authorization metadata, per-mode call/token stop caps, stable database hashes, and bounded failed-scenario final prompt/response capture. No hidden reasoning is collected.
- SA: strengthened target-content guidance; added structural validation for approved abstract sentence starters and completion placeholders in other instructional fields. Generic abstract forms such as `This matters because ____` and `According to the survey, ____` are allowed after repeated repair evidence. On-topic or completed frames remain prohibited.
- WF: added failed-revision refresh/retry coverage. If final reflection fails, the Finish dialog now closes so the saved failure and retry are visible. Scenario overwrite confirmation now updates widgets in an `on_click` callback.
- GC, FG, and CQ production prompts/state were not changed. No persistent production history, disposition schema, new agent, storage backend, or deployment was introduced.

The active product contract is updated in `PRD_V3_ITERATIVE_REVISION.md` Section 8.3.2. Structural validation is not semantic proof and does not replace the review records below.

## 2. Authorization and resource record

All real calls in Sections 1–13 used synthetic drafts. Section 14 records a separate, explicitly authorized exact-text exception outside the synthetic-only prototype workflow. The initial investigation used non-thinking, temperature 0. The explicitly authorized mode comparison and full thinking acceptance run omitted temperature and used configured reasoning effort. The pre-run records are gitignored under `data/evidence/`:

- `v3_live_el_targeted_authorization_20261115T080408Z.json`
- `v3_integrated_acceptance_authorization_20261115T083659Z.json`
- `v3_starter_correction_authorization_20261115T085022Z.json`
- `v3_scaffold_boundary_authorization_20261115T085304Z.json`
- `v3_placeholder_guard_authorization_20261115T085530Z.json`
- `v3_acceptance_15_diagnostic_authorization_20261115T090654Z.json`
- `v3_integrated_acceptance_authorization_20261115T091024Z.json`
- `v3_sa_thinking_comparison_authorization_20261115T100932Z.json`
- `v3_sa_thinking_full_acceptance_authorization_20261115T113446Z.json`
- `v3_sota_targeted_authorization_20261115T122058Z.json` (smoke calls; original targeted caps superseded before scenario runs)
- `v3_sota_targeted_uncapped_authorization_20261115T122330Z.json` (targeted runs without total token stop caps)

Observed totals across these records, including covered targeted reruns, failed setup attempts, corrective runs, all three non-thinking integrated runs, the controlled mode comparison, the full thinking run, and the SOTA smoke/targeted runs:

| Authorization | Runs | Attempted calls | Observed tokens | Scenario errors | Logged repairs |
|---|---:|---:|---:|---:|---:|
| Targeted experiments | 46 | 84 | 339,604 | 3 setup/selector errors | 1 |
| Integrated `v3.6.1`, non-thinking | 1 | 109 | 361,308 | 0 | 1 |
| Integrated `v3.6.4`, non-thinking | 1 | 108 | 368,088 | 1 | 4 |
| Integrated `v3.6.5`, non-thinking | 1 | 114 | 399,368 | 2 | 10 |
| Corrective/diagnostic batches | 11 | 36 | 121,070 | 0 | 5 |
| Controlled SA mode comparison | 6 | 8 | 44,697 | 0 | 2 |
| Integrated `v3.6.5`, thinking | 1 | 98 | 488,010 | 3 | 3 |
| SOTA smoke calls | 2 | 2 | 336 | 0 | 0 |
| SOTA targeted Claude/Gemini runs | 2 | 52 | 181,231 | 4 | 5 |
| **Total** | **71** | **611** | **2,303,712** | **13** | **31** |

Attempted calls can exceed deduplicated successful-call logs when validation fails after a model response. The DeepSeek thinking run's empty API response has no usage metadata, so its 98 attempted calls and 97 successful-response logs differ by one without recorded token usage for that failed call. Gemini's targeted run has 23 attempted calls but 18 response logs because of one failed validation and four API timeouts; its observed 76,090 tokens include the failed-validation response but exclude timeout usage. Token counts are provider observations, not a monetary estimate.

## 3. Automated and browser verification

- Original investigation mocked suite after the evaluation-only SOTA adapters and scenario-list support: **251 passed** with `pytest -q`. Section 14 records the later 260-check suite.
- WF revision failure: exact revised text, selected goals, latest failed round, refresh restoration, and retry passed without duplicate snapshots or rounds in `test_failed_revision_restores_latest_snapshot_goals_and_retries_without_duplication`.
- Scenario overwrite: the previous `StreamlitWidgetAlreadyInstantiatedError` is fixed and its AppTest passes.
- Final failure: AppTest verifies that the Finish dialog closes and the failed reflection can be retried after restoration.
- Local mocked Chrome flow: initial review, goal selection, small-change confirmation, one revision, refresh restoration, failed final reflection, recovery after restart, and final reflection completed. The final database contained exactly two snapshots, two completed rounds, and one completed reflection. `PRAGMA integrity_check` returned `ok`; WAL size after checkpoint/close was zero. Database: `data/browser_verification_20261115T083659Z.db`; SHA-256: `95407f37bd4b4d7b8cea089a3f74b856e9dffc5d94d44d011f62a2e7c0534599`.
- `data/evidence/v3_local_verification_1280.png` shows the final original/latest comparison at 1280×900. Accessibility-tree snapshots exposed named step controls, editor, goal checkbox, support actions, Finish dialog, and named original/latest regions.
- Keyboard/screen-reader limitation: a separate headless Chrome run verified Tab focus order and exact per-character initial-draft input, but synthetic button activation never reached the app, so the full keyboard loop was not verified. No actual screen-reader walkthrough occurred. See `data/evidence/v3_headless_keyboard_20261115T091024Z.json`. The accessibility gate remains open.

The original deployed homework interruption was not reproduced as an application defect. The local browser final failure was traced to the disposable mock's final-handoff mapping; it also exposed the real failed-Finish modal recovery issue fixed above. No speculative revision-submission rewrite was made.

## 4. Semantic-review method and limitations

**Reviewer role:** engineering review with model assistance, 2026-11-15. This is single-review engineering evidence, not educator consensus. Structural results are reported separately from semantic judgments. No independent educator disagreement or adjudication occurred because reviewers were unavailable.

`acceptable` below is sample-specific engineering conformance, not proof of pedagogical quality. Disputed meaningfulness and grade appropriateness remain `uncertain` until educator review. Positive, null, negative, and mixed outcomes are retained.

## 5. GC — goal continuity: mixed/uncertain; no adoption

Controlled prefixes made drafts, selected goals, self-reports, and prior findings identical across arms. Arm C's model payload was verified to contain the same bounded `prior_findings` produced by the shared serializer. An earlier Arm C artifact with an empty model payload was invalidated by a LangGraph unknown-field defect and is not used for semantic conclusions.

### Beach disputed revision 2

- **Arm A — current:** `data/evidence/v3_live_el_scenario_01_evaluation_20261115T081111Z.json`; structurally valid, two calls/no repairs. It returned `support_agent`, recognized `goal_sandcastle` improvement, and raised a different sentence-boundary issue at `my family went to the beach and it was really fun`. It did not reproduce the historical direct-response sequence.
- **Arm B — generic:** `data/evidence/v3_live_el_gc_generic_scenario_01_evaluation_20261115T081118Z.json`; structurally valid, two calls/no repairs. It introduced dolphin-transition and generic-ending issues, including `After that we saw dolphins swimming in the ocean!`, rather than the prior run-on.
- **Arm C — temporary history:** `data/evidence/v3_live_el_gc_history_scenario_01_evaluation_20261115T081414Z.json`; structurally valid, two calls/no repairs. It retained `goal_run_on` for `The waves were really big and loud and my little brother started crying because he was scared but my dad held him.` No forced-revision language was added.

**Semantic status:** `uncertain`. Whether that run-on remains meaningful is an educator judgment. C shows continuity in this case, but A did not reproduce the original omission and B shifted to new issues.

### Resolved and strong controls

- Beach resolved controls: current `...081136Z`, generic `...081144Z`, and history `...081421Z` all supplied exactly three selected-goal observations. Current and generic added new elaboration candidates; history returned `direct_response` with no issues. No stale selected issue was revived.
- Strong draft: current `data/evidence/v3_acceptance_scenario_10_evaluation_20261115T081159Z.json`, generic `...081205Z`, and history `...081213Z` all returned candidates rather than direct response; B and C each returned two. These are quality concerns, not a universal manufactured-issue proof.

**Disposition:** no simplest arm met the adoption rule without uncertainty or potential regressions. Keep current production behavior; no persistent state or disposition schema. Educator review of the exact beach sentence remains required.

## 6. SA — scaffold authorship: targeted improvement, but integrated gate failed

Controlled Support-only runs held the Coordinator handoff fixed. Each reviewed run used one Support call unless repair is noted.

### Controlled targets

- **Homework, current:** `data/evidence/v3_live_el_scenario_10_evaluation_20261115T083026Z.json`; `critical_contract_violation`. The tired-to-grades hint listed `listening, focusing, finishing work`, supplying possible classroom links.
- **Homework, SA arm:** `data/evidence/v3_live_el_sa_authorship_scenario_10_evaluation_20261115T083032Z.json`; `acceptable` in this sample. It asked for one classroom moment without the menu and retained abstract starters and linked steps.
- **Homework, final production target:** `data/evidence/v3_live_el_scenario_10_evaluation_20261115T085551Z.json`; `acceptable` after one bounded starter repair. Exact final guidance includes `Picture a class where a student is tired. Name one thing you have noticed or can imagine happening in that class.` No target menu or disguised placeholder remained.
- **Sandcastle, current/SA:** `...083016Z` and `...083021Z`; both anchored in existing sandcastle/moat content without naming towers or new sensory answers. Final `v3.6.3` production check `...085344Z` retained that boundary. `acceptable` in this sample.
- **Cake, current/SA:** `...083037Z` and `...083043Z`; current asked for the student's sugar link and mother detail without the earlier full-run sugar menu; SA preserved the same boundary. Final `...085359Z` removed a previously observed on-topic stuck frame. `acceptable` in this sample.

Earlier production candidates `v3.6.1`–`v3.6.3` still contained on-topic frames such as `This connects to becoming a better citizen because ____`, `The challenge was ____`, and `Sarah had so much homework that...`. They are preserved as negative findings and motivated the structural corrections and prompt clarification; they are not hidden by the later acceptable targets.

### Integrated SA result

The final integrated artifact `data/evidence/v3_acceptance_evaluation_20261115T091103Z.json` had **two scenario errors and ten repairs**. Acceptance #1 and #10 failed Support after one correction. Captured invalid spans included:

- #1: `That means more than half of students would...` in a stuck step.
- #10: `During our class discussion, ____` as an on-topic starter.
- Other repaired frames included `The hard part was ____` and `Doing that helps someone become a better citizen because…`.

These are genuine authorship concerns, not harmless abstract variants. **Semantic status for the integrated SA candidate: `critical_contract_violation` in the reviewed sample.** The integrated engineering gate is not passed, and no deployment or clean-semantic-quality claim is authorized. Further SA work should review why the model repeatedly generates target frames despite the clarified prompt; do not weaken the boundary merely to reduce repair counts.

## 7. FG — grounding: null and unresolved findings; no adoption

- **Octopus revision, current/FG:** `data/evidence/v3_live_el_scenario_04_evaluation_20261115T082132Z.json` and `...fg_grounding...082144Z`. Both recognized the added aquarium connection and preserved a no-source limitation. The `I think` inference was not automatically treated as a factual error. Current Support asked for observed color/surroundings; it also suggested possible three-heart mechanisms in an earlier output, a quality concern. FG did not show a sufficient net benefit. `uncertain` for pedagogical usefulness; no anti-inference rule.
- **Cell-phone motive, current/FG:** `data/evidence/v3_live_el_scenario_08_evaluation_20261115T082156Z.json` and `...fg_grounding...082207Z`. Both called the revision a clearer or more specific attributed reason, not a `checkable motive`. `acceptable` null result for the historical wording concern; no prompt change.
- **Support-only mechanism control:** `data/evidence/v3_live_el_scenario_12_evaluation_20261115T083249Z.json` and `...fg_grounding...083253Z`. Both asked what the three hearts do without listing a specific mechanism, but both still requested factual explanation without a supplied source. `quality_concern`; no clear FG benefit.
- **Initial source notice:** `data/evidence/v3_live_el_scenario_13_evaluation_20261115T083257Z.json` and `...fg_grounding...083307Z`. Both initial outputs had `source_limitations=[]`, while related revision outputs contained a limitation. `quality_concern` for consistency when verification relevance is unchanged; the FG suffix did not fix it. No FG production change was adopted.

Bounded inference remains allowed. No citation requirement was added to personal narratives or opinions.

## 8. CQ — candidate quality: mixed; no adoption

- **Homework:** current `data/evidence/v3_live_el_scenario_03_evaluation_20261115T081447Z.json` included `End with a wrap-up sentence` even though the last sentence already states the position; this is a rationale/meaningfulness concern. CQ `...cq_quality...082240Z` omitted that conclusion goal but added a bridge before the existing `Also homework causes too much stress.`; the latter needs educator judgment.
- **Cake:** current `...081511Z` had three candidates and one repair; CQ `...cq_quality...082302Z` had two/no repairs and no generic transition candidate despite clear `When`/`Twenty minutes later` markers. Positive targeted finding.
- **Partial octopus conclusion:** current `...082132Z` acknowledged the general conclusion but used a new issue ID for the remaining conclusion gap. CQ `...cq_quality...082252Z` omitted the conclusion issue rather than clearly continuing it. `quality_concern`, not a clean continuity improvement.
- **Completed octopus conclusion:** current `...082229Z` continued the conclusion with `Make your ending pull the traits together` even after the revision named three traits; CQ `...cq_quality...082310Z` did not repeat that goal and instead identified the separate call to action. Positive targeted finding, but it does not erase the partial-goal concern.

**Disposition:** mixed results do not support the CQ arm wholesale. No production prompt or `carry_forward` semantics changed. Rationale accuracy, meaningfulness, and continued-goal clarity remain educator-review items.

## 9. Integrated operational results and comparison boundaries

### Final non-thinking `v3.6.5` / schema `v3.6.3`

Artifact: `data/evidence/v3_acceptance_evaluation_20261115T091103Z.json`

- 32 scenarios attempted; two scenario errors (#1 and #10).
- 108 deduplicated successful-response logs; 114 attempted calls including the failed validations.
- Ten logged repairs.
- 373,606 tokens in deduplicated successful-response logs; 399,368 observed tokens including failed-validation attempts.
- 361.689 seconds of recorded model latency; 362.167 seconds graph invocation time; 362.308 seconds service time.
- Database checkpointed/closed; WAL zero; SHA-256 `c79eabedc92411c67082be3b7b9422977a7c485e5c0a2d08995ee010648ebf4a`.

### Earlier integrated attempts

- `data/evidence/v3_acceptance_evaluation_20261115T083722Z.json` (`v3.6.1`): 32 scenarios/zero errors, 109 calls, one repair, 361,308 tokens, 394.292 seconds model latency. Semantic review found on-topic frames despite operational success.
- `data/evidence/v3_acceptance_evaluation_20261115T085735Z.json` (`v3.6.4`): one error (#15), four repairs, 368,088 observed tokens. Targeted #15 rerun `data/evidence/v3_acceptance_scenario_15_evaluation_20261115T090714Z.json` completed with one repair and three deferral observations. This targeted recovery does not erase the integrated error.

### Historical comparison caution

The historical full acceptance baseline `data/evidence/v3_acceptance_evaluation_20261111T173847Z.json` used prompt/schema `v3.4.0` and had 32 scenarios, zero errors, 110 calls, four repairs, and 330,528 tokens. Current output differences cannot be attributed to SA alone because intermediate prompt/schema versions also changed. Candidate-count and route differences are reported for review, not treated as quality scores.

## 10. Follow-up controlled thinking comparison

The project owner explicitly authorized a thinking experiment. Authorization: `data/evidence/v3_sa_thinking_comparison_authorization_20261115T100932Z.json`. The comparison used Support-only controlled handoffs, identical current prompt/schema `v3.6.5`/`v3.6.3`, and identical validation. No Coordinator output or routing changed within a pair. Thinking omitted temperature and used the configured reasoning effort; non-thinking used temperature 0. Raw hidden reasoning was not collected.

Evidence bundles:

- Homework causal scaffolds: `data/evidence/v3_live_el_scenario_10_evaluation_20261115T101006Z.json`.
- Acceptance #1 garden handoff: `data/evidence/v3_live_el_scenario_14_evaluation_20261115T101030Z.json`.
- Acceptance #10 strong-draft handoff: `data/evidence/v3_live_el_scenario_15_evaluation_20261115T101108Z.json`.

| Mode | Attempted calls | Repairs | Scenario errors | Total tokens | Reasoning tokens | Model latency |
|---|---:|---:|---:|---:|---:|---:|
| Non-thinking | 5 | 2 | 0 | 21,629 | 0 | 24.017 s |
| Thinking | 3 | 0 | 0 | 23,068 | 11,771 | 75.863 s |

Semantic review:

- **Homework:** both modes avoided the earlier target-cause menus and retained linked, student-authored steps. `acceptable` in this sample.
- **Garden/source handoff:** both final outputs preserved exact references and source limits without target frames. The non-thinking repair was triggered by the quoted phrase `The survey measured...`, an ellipsis in source-navigation text rather than a target answer; this is a structural false-positive concern. Thinking required no repair. `acceptable` final output in both, with a validation-quality concern for the placeholder rule.
- **Strong-draft handoff:** non-thinking first emitted `when the room is quiet, a reader can ____`, an on-topic completion frame, and repaired successfully. Thinking emitted no completion frame, preserved the no-source limitation, and instructed the student to add only truthful details or bound the claim. `acceptable` final output in both; thinking showed clearer grounding in this case. Its repeated claim wording was somewhat verbose, a quality concern rather than a contract violation.

**Disposition:** thinking resolved the targeted SA blocker in these three matched handoffs, with zero errors and zero repairs. This is promising targeted evidence, not proof that thinking resolves the broader SA problem. One run per cell provides no variability estimate, and thinking used about **3.16× the model latency** with 11,771 reasoning tokens. Do not switch student runtime automatically. A broader decision requires separate review and verification; the failed integrated gate and educator/accessibility gates remain open.

After these runs, the owner authorized future runs without a token stop cap. The runner now makes `--max-total-tokens` optional while retaining required authorization and model-call limits and recording actual usage. The completed comparison used its original recorded caps and was not rerun.

Separately, the local port-8501 process was explicitly launched with `DEEPSEEK_THINKING=true` on 2026-11-15. That operational override did not change the non-thinking repository default, deploy the working tree, or supply broader quality evidence.

## 11. Full thinking acceptance run

The project owner explicitly authorized all 32 acceptance scenarios in thinking mode with no token stop cap. Authorization: `data/evidence/v3_sa_thinking_full_acceptance_authorization_20261115T113446Z.json`. Artifact: `data/evidence/v3_acceptance_evaluation_20261115T113518Z.json`. The run used `deepseek-flash`, thinking enabled, configured reasoning effort `high`, omitted temperature, retained prompt/schema `v3.6.5`/`v3.6.3` and fixture `v3.4.0`, and kept the 160-attempted-call cap. Raw hidden reasoning was not collected.

### Operational and resource results

| Measure | Non-thinking integrated | Thinking integrated |
|---|---:|---:|
| Scenario errors | 2 | 3 |
| Attempted calls | 114 | 98 |
| Deduplicated successful-response logs | 108 | 97 |
| Logged repairs | 10 | 3 |
| Observed tokens | 399,368 | 488,010 |
| Reasoning tokens | 0 | 167,817 |
| Estimated final-response tokens | — | 53,068 |
| Recorded model latency | 361.689 s | 1,266.141 s |

Thinking graph/service times were 1,266.654/1,266.793 seconds. It used about **3.50× the total recorded model latency** and **1.22× the observed tokens** of the non-thinking run. This is a single run with different scenario paths, not a controlled latency or variability estimate. The database was checkpointed/closed with zero WAL bytes; SHA-256 is `7a266b415a2554b7f504a1c79609478a83c3890f55e5a7f295179105efc4cd2d`.

The three scenario errors have different causes:

- **#8, harness/scenario compatibility:** the first revised draft received a grounded `specific_improvement` and `direct_response`. The fixture then required a first candidate for a second revision, but none existed. Voluntary stopping was appropriate in this output; the planned second-revision path was not exercised, and the final reflection compared the original with only the first revision.
- **#15, harness/scenario compatibility:** the initial review returned two meaningful candidates, while the fixture required three. No revision or deferred-goal observations were exercised. The unchanged-draft final fallback correctly claimed no improvement. A two-candidate result is not by itself evidence of an application defect or a reason to manufacture a third goal.
- **#24, API failure:** DeepSeek returned an empty response during the initial review. No state or model output was produced. The client raises before saving response metadata (`agents/utils.py:224-250`), and the evaluation runner only retains attempts after a completed API response (`scripts/evaluate_v3.py:127-147`), so this artifact has no final prompt/response attempt or usage metadata for that empty response. This observability gap remains open.

The runner exited 1 because these scenario errors were present. No rerun is covered by this authorization.

### Repairs and SA authorship review

The earlier #1/#10 persistent Support validation failures did **not** recur. All final starters passed the approved abstract-form validator. Three bounded repairs succeeded:

- #7 and #20 were false positives for quoted navigation fragments containing `...` (`These steps connect...` and `It would give students...`), not completion tasks.
- #12 initially used the unapproved but abstract `In the end, ____.` and repaired to an allowed frame. No on-topic starter appeared in the three invalid responses.

This is improved SA **validation** evidence, not clean semantic authorship acceptance:

- #16 retained linked, student-authored garden/citizenship guidance without a completed target response.
- #22 supplied `focus` and `concentrate` as vocabulary for what quiet makes possible. Those are likely target links the student was asked to generate, so the vocabulary remains an assigned-topic authorship concern despite passing structural validation.
- #21 produced a bounded survey scaffold, not the named responsibility-hint target; that specific focus was not exercised.
- #10 again returned two candidates for the strong-draft control rather than direct affirmation. Whether each is meaningful requires educator judgment, but the intended no-forced-criticism control did not pass in this sample.

### Other semantic and routing findings

- **Positive:** all 11 completed normal revision routes returned exactly one Coordinator observation and one Support feedback item per selected goal. #7 recognized two genuine improvements and one not-yet-evident connection; #9 retained the organizational regressions; #14 and #28 described small/identical changes neutrally; #12 correctly bypassed normal critique for concerning content. RACES coverage mapped all five requested components, and #23 appropriately affirmed the strong long informational draft. Automated flags found no prohibited score/readiness language or narrative citation/counterclaim demands.
- **Source grounding concern:** #3 preserved a no-source limitation but then repeatedly told the student to look back at and copy from the unavailable passage. #2 corrected the health overclaim but also requested a link to the health point; that needs review against the source's explicit limits.
- **Clarification regression:** #30 routed directly to `teacher_review`/`clarification_limit` after the **first** unclear answer with `clarification_count=1`, instead of asking a second question. The Coordinator made this routing choice directly; the deterministic guard in `langgraph_core/nodes.py:75-99` only intercepts another `ask_clarification` at count two. Non-thinking completed the expected two-answer sequence in the comparison artifact. This is a real contract failure even though the runner recorded no exception.
- **Incomplete genre path:** #6 asked for genre/assignment clarification after the explicit correction, so the intended corrected-genre reassessment was not completed.
- **Reflection concern:** #7's final reflection praised `These steps connect...` as a direct connection although the immediately preceding review said that sentence named rather than explained the connection. This requires semantic review even though final references passed deterministic grounding checks.

**Disposition:** thinking improved the targeted SA validation behavior and reduced repairs, but the integrated engineering gate and clean semantic gate remain failed. The results do not support changing the repository default, claiming that thinking resolves SA generally, or deploying this working tree. No rerun, runtime-default change, commit, or deployment occurred.

## 12. Open gates and next decisions

1. **Integrated engineering gate:** failed for both final non-thinking and thinking candidates. The thinking run needs explicit disposition of the #8/#15 fixture assumptions, the premature #30 clarification limit, and the empty #24 response before a separately authorized verification decision.
2. **Model-configuration decision:** open. Thinking's validation improvement comes with routing/semantic concerns and substantially higher latency in this single full run; the non-thinking default remains unchanged.
3. **Educator gate:** unchanged and open. Review beach meaningfulness, octopus inference/conclusion judgments, strong-draft candidates, source-missing instructions, target-like vocabulary, final reflection consistency, and SA outputs with complete context.
4. **Accessibility gate:** open. The accessibility tree and 1280px rendering are evidence only of those checks; complete actual keyboard activation and screen-reader review with an appropriate harness/reviewer.
5. **WF monitoring:** original deployed revision interruption remains unreproduced. Preserve the existing log and use bounded lifecycle diagnostics if it recurs.
6. **Deployment:** not approved and not performed. The public footer `v04d61af` does not represent this working tree.
7. **Claims:** no learner-outcome, pedagogical-effectiveness, production-readiness, accessibility-compliance, or educator-approval claim is supported by this investigation.

## 13. SOTA thinking targeted comparison

The project owner supplied separate relay credentials and explicitly requested `claude-opus-5-5` and `gemini-4-argon` with thinking. The evaluation-only adapter uses native Anthropic Messages for Claude and native Gemini `generateContent` for Gemini. The actual endpoint came from the user-configured `SOTA_BASE_URL`; public RelayRouter protocol documentation was only compatibility guidance. No application runtime default changed.

Smoke authorization: `data/evidence/v3_sota_targeted_authorization_20261115T122058Z.json`. Before the targeted runs, the owner directed no token budget; `data/evidence/v3_sota_targeted_uncapped_authorization_20261115T122330Z.json` superseded the targeted token caps. Both targeted runs omitted `--max-total-tokens`, retained a 40-call cap per model, and covered acceptance #1, #3, #8, #10, #15, #22, and #30. No reruns or full SOTA acceptance runs were authorized.

Protocol-required per-request fields remained: `max_tokens=8000`, Claude thinking `budget_tokens<=4000`, and Gemini `thinkingLevel=HIGH` with no thinking-token budget. Gemini used `includeThoughts=false`; both adapters retain final text and metadata while filtering provider thinking blocks. Thinking was requested, but neither smoke response reported reasoning-token usage. Claude does not separate reasoning in the recorded usage, and Gemini supplied no thought-token count in these artifacts. Do not interpret aggregate zero/unavailable reasoning fields as proof that reasoning did or did not occur.

### Connectivity and resource evidence

Smoke artifact: `data/evidence/v3_sota_thinking_smoke_20261115T122304Z.json`. Both models returned the requested synthetic JSON on the configured host. Claude took 5.428 seconds and used 76 recorded tokens; Gemini took 76.905 seconds and used 260 recorded tokens. These tiny calls are protocol checks, not quality or representative-latency evidence.

| Measure | Claude Opus 5.5 | Gemini 4 Argon |
|---|---:|---:|
| Targeted scenarios | 7 | 7 |
| Scenario errors | 1 | 3 |
| Attempted calls | 29 | 23 |
| Deduplicated response logs | 29 | 18 |
| Logged repairs | 4 | 1 |
| Coordinator repairs | 3 | 0 |
| Observed tokens, including available failed-validation usage | 105,141 | 76,090 |
| Tokens in deduplicated response logs | 105,141 | 71,880 |
| Recorded model latency | 1,115.833 s | 803.131 s |

Claude artifact: `data/evidence/v3_acceptance_sota_claude-opus-5-5_scenarios_01_03_08_10_15_22_30_evaluation_20261115T122359Z.json`; database WAL zero and SHA-256 `2b9a8b5d35e534583d32b8a112258888dc873cfa7881cf050314bd05eb7b9307`.

Gemini artifact: `data/evidence/v3_acceptance_sota_gemini-4-argon_scenarios_01_03_08_10_15_22_30_evaluation_20261115T122359Z.json`; database WAL zero and SHA-256 `b99bc43f1ccf5b47347d37c03f8de96fd5c5a949af7d050af7c080cbcd6c09fb`. Its four timeout attempts have no response usage; one additional failed-validation attempt explains the remaining attempted/log difference. Visible-response tokens cannot be separated reliably from reasoning usage for these runs, so the summary field remains null.

### Claude findings

- **Positive targeted routing:** #10 returned direct affirmation with no candidates; #30 asked again after the first unclear answer and reached `clarification_limit` only after the second. #15 supplied three candidates, completed the revision, and returned three neutral observations with the two deferred goals carried forward. #22 avoided the earlier target-like vocabulary and retained an abstract starter.
- **Source-missing improvement:** #3 did not direct the student to an unavailable passage. It used the existing alertness claim for reasoning support and preserved a no-source verification limitation.
- **SA validation:** no Support repair occurred in these seven scenarios, and the reviewed final candidate fields did not contain the earlier on-topic completion frames. This is targeted evidence only.
- **#8 persistent Coordinator failure:** the revision response used ordinal `occurrence` values 3 and 4 for unique references instead of occurrence 1. Its correction still used invalid values 2 and 4, causing the safe clarification fallback and the fixture's no-candidate error. The intended second revision was not exercised. A separate final comparison initially omitted `coordinator_reasoning` and repaired successfully.
- **Other repairs:** #1 and #3 initially returned malformed non-JSON Coordinator content before bounded correction. These failures count against operational reliability even though later outputs completed.

### Gemini findings

- **Positive targeted routing:** #10 and #22 both returned direct affirmation without manufactured candidates. #3 preserved a no-source limitation, invited the student to add the passage, and distinguished the author's position from the student's own claim. #15 completed its revision with three grounded observations and neutral deferral language.
- **Timeout boundaries:** #8 timed out before its first revision result; #15 timed out during final reflection after a completed revision; #30 timed out while reassessing the first unclear answer. The multi-round, final-reflection, and two-answer clarification outcomes for those paths are unevaluated, not passes.
- **Repair:** #15 had one Support repair triggered by an ellipsis in quoted navigation text (`Students could water plants...`), another false-positive placeholder concern rather than an on-topic frame.
- **Semantic concerns:** #1 supplied likely target applications such as how garden habits affect actions around other people or school property, despite the target-content boundary. It also steered the 62% interest result toward garden use, which requires bounded interpretation. In #15, the later review dropped the still-relevant no-source limitation, and the transition candidate paired an `After ____, ____` starter with an additional-reason relationship. Structural validation did not catch these semantic issues.

### Disposition

Neither model solved the targeted problem set cleanly. Claude completed more paths and fixed the sampled strong-draft, clarification-limit, source-missing, and target-vocabulary behaviors, but its occurrence-validation fallback and malformed responses remain significant. Gemini fixed the sampled strong-draft/grade-5 routing but had three timeout-ended scenarios and remaining semantic concerns. One targeted run per model does not establish general superiority, stability, pedagogical effectiveness, or learner outcomes. No SOTA full acceptance run, runtime-default change, deployment, commit, or rerun occurred.


## 14. User-requested exact-essay coaching check

### Scope and authorization

A user explicitly requested implementation and a review of the exact essay supplied in the conversation. The text was not added to a repository fixture or tracked source file. The initial authorization permitted one review with at most four calls and 50,000 observed tokens. A follow-up answer authorized additional calls as needed; the implementation retained explicit per-attempt caps and kept cumulative observed tokens below 50,000. Four initial-review attempts used eight calls and 37,801 observed tokens in total. No revision prose, revision submission, final reflection, deployment, or hidden-reasoning capture was included.

### Failures and deterministic correction

- Prompt `v3.6.6`, artifact `data/evidence/v3_exact_essay_initial_evaluation_20261115T132748Z.json`: two calls, 8,945 tokens, one Coordinator repair, then safe clarification fallback. Exact unique issue quotations were assigned incorrect paragraph locations because the standalone title was not counted consistently.
- Prompt `v3.6.7`, artifact `data/evidence/v3_exact_essay_initial_evaluation_20261115T133017Z.json`: two calls, 9,207 tokens, one repair, then the same fallback despite explicit title-block prompt guidance. Two unique references remained one paragraph too low; a repeated reference with a valid supplied location was not the failure.
- A deterministic `locate_unique_reference` recovery now corrects paragraph/occurrence metadata only when the exact quotation occurs once in the full draft and lies within one blank-line-separated block. It records `coordinator_reference_normalizations`. Repeated, missing, and cross-paragraph references still require bounded repair. Replaying the second failed response locally produced a Support route with two recorded corrections and no model repair call.
- The `v3.6.7` follow-up in `data/evidence/v3_exact_essay_initial_evaluation_20261115T133632Z.json` completed through Coordinator and Support in two calls, 9,796 tokens, 15.048 seconds model latency, and no repairs. Semantic review still found a spelling-answer list and an instruction to capitalize an already-capitalized word in the optional language candidate, so this was not a clean quality pass.

### Final `v3.6.8` result

Artifact `data/evidence/v3_exact_essay_initial_evaluation_20261115T134018Z.json` completed in two non-thinking calls, 9,853 tokens, 13.669 seconds model latency, and no repairs or reference normalizations. The route was `support_agent`, working genre was informational, and four candidates had valid exact locations. The feedback gave specific sequence/detail strengths, process and elaboration choices, a reader-facing conclusion option, and one comma-splice pattern instead of a spelling catalogue. It contained no source-verification claim, replacement paragraph, grade, or readiness claim.

Semantic limitations remain. The recommended sorting candidate asks for two trash-type connections in its action but its self-check refers to all four. It also requests explicit station handoffs that a reader may already infer from later paragraphs; the squeezed-out-water question from the comparison feedback was not selected as the recommended goal. The result therefore demonstrates successful technical delivery with mixed semantic quality, not clean pedagogical acceptance.

### Browser and mocked verification

The final persisted review was opened in the normal local Streamlit UI. Choose initially rendered one recommended goal and `See other choices (3)`; revealing alternatives displayed idea/reasoning/organization goals separately from optional sentence polishing. Show less collapsed alternatives, Choose just this goal left exactly one selection, and Revise showed that goal with its correct highlight and an enabled Submit revision action. The persisted round still contained two model calls after these interactions. Captures are `data/evidence/v3_exact_essay_choose_20261115T134018Z.png` and `data/evidence/v3_exact_essay_revise_20261115T134018Z.png`. No revision or final comparison was submitted.

The full mocked suite passed 260 checks after the UI, speculative-process, unique-reference, and language-guidance changes. This exact-text check is separate from the synthetic acceptance set and does not erase its open engineering, semantic, educator, accessibility, or learner-outcome gates.
