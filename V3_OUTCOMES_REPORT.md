# V3 Iterative Revision Coach — Outcomes Report

**Report version:** 1.0  
**Report date:** 2026-11-10  
**Implementation:** Local V3 Iterative Revision Coach  
**Baseline prompt/schema:** `v3.1.0`  
**Baseline scenario fixture:** `v3.1.0`  
**Baseline scope:** Original analysis; later improvement outcomes require separate evidence  
**Model evaluated:** `deepseek-flash`  
**Evaluation scope:** Mocked automated checks, local browser verification, and representative real-model synthetic scenarios  
**Release status:** Local implementation only; no V3 deployment, educator approval, or learner-outcome claim

## 1. Executive Summary

V3 replaces the previous local V1/V2 runtime with an iterative, student-authored revision coach. The implemented product supports argumentative, informational, and narrative writing; correctable genre inference; optional assignment and source context; one-to-three goal selection; exact goal-linked highlights; immutable submitted revisions; repeated whole-draft review; optional scaffolds; student-controlled stopping; and grounded original-to-final reflection.

The main outcomes are:

- **Local implementation delivered:** two LangGraph agents, deterministic revision services, composition/round/reflection storage, a Streamlit student workspace, versioned synthetic scenarios, and an explicit evaluation runner.
- **Automated verification:** **128 checks passed** across nine test files. Dependency validation, Python compilation, and the scoped Git diff check also passed.
- **Browser verification:** the final `v3.1.0` thinking-mode browser loop worked at 1280px, including two simultaneous highlights, per-goal observations, next-round navigation, finish confirmation, and final reflection.
- **Representative real-model evaluation:** all six scenarios completed in both thinking and non-thinking modes without scenario errors.
- **Thinking-mode outcome:** thinking used more tokens and substantially more latency and required two repairs. It showed isolated diagnostic strengths but did not demonstrate a consistent content-quality advantage.
- **Content outcome:** non-thinking was stronger on RACES alignment and whole-draft coverage in this sample. Thinking was stronger on selected nuanced diagnoses, especially distinguishing the student's claim from the author's claim, and sometimes supplied richer per-goal analytical guidance.
- **Baseline recommendation:** non-thinking was the stronger candidate for further validation. Section 16 records the later repeated comparisons and the implemented non-thinking runtime decision; neither is a general conclusion about model superiority.

The complete PRD evidence gates are **not** finished. The 30 Section 14.2 scenarios were not all exercised, educator review remains open, and no real-student usability or learning study has been conducted.

## 2. Scope, Status, and Evidence Provenance

### 2.1 Status terminology

This report uses four evidence categories:

- **Real model:** observed in the representative DeepSeek thinking/non-thinking pair.
- **Browser:** observed through the local Streamlit interface. Browser evidence includes multiple passes; the final full loop used `v3.1.0`.
- **Mocked/AppTest:** observed through unit, integration, storage, API, or Streamlit AppTest checks with mocked model responses and temporary databases.
- **Partial/not validated:** only some elements were exercised, or no matching output evidence exists.

Mocked tests establish application behavior under controlled responses. They do not establish real-model quality. Real synthetic outputs provide limited implementation and content evidence, not evidence of educator agreement, student usability, motivation, engagement, or learning outcomes.

### 2.2 Primary evidence artifacts

| Artifact | Purpose |
| --- | --- |
| `data/evidence/v3_paired_evaluation_20261110T094344Z.json` | Latest matched `v3.1.0` thinking/non-thinking structured outputs, routes, repairs, latency, and token usage |
| `data/v3_thinking_evaluation_20261110T094344Z.db` | Thinking-mode compositions, snapshots, rounds, reflection, and checkpoints |
| `data/v3_nonthinking_evaluation_20261110T094344Z.db` | Non-thinking-mode compositions, snapshots, rounds, reflection, and checkpoints |
| `data/evidence/v3_browser_verification_20261110.json` | Aggregated local browser verification summary and limitations |
| `data/v3_browser_verification.db` | Browser compositions and immutable original/revision snapshots |
| `data/evidence/v3_local_v3_1_final_reflection_1280.png` | Final `v3.1.0` reflection capture |
| `data/evidence/v3_local_goal_highlight_1280_fixed.png` | Corrected 60/40 workspace and exact goal highlight |
| `data/evidence/v3_paired_evaluation_20261110T093315Z.json` | Earlier `v3.0.0` pair used to identify scaffold and matched-selection issues; not current-output evidence |

Databases, evidence JSON, and screenshots are Git-ignored. They are local evidence artifacts, not committed source files.

## 3. Delivered Implementation

### 3.1 Agent and workflow architecture

V3 retains two model-driven agents:

1. **Assessment Coordinator**
   - Performs human-review assessment before writing-quality routing.
   - Resolves explicit or inferred genre and material genre ambiguity.
   - Applies genre-specific ELA-informed criteria without numerical scores.
   - Identifies meaningful issues, strengths, source limitations, regressions, and selected-goal observations.
   - Produces exact draft references and concise final-output rationale.
   - Produces grounded original/final comparison findings in final mode.
2. **Instructional Support Agent**
   - Converts Coordinator findings into warm, grade-appropriate feedback.
   - Produces revision choices, passage-specific hints, vocabulary considerations, approved abstract frames, and concrete stuck steps.
   - Preserves Coordinator source limitations and selected-goal statuses.
   - Produces final motivational reflection only from verified comparison findings.

Deterministic services handle clarification interrupts, direct response, teacher-review templates, snapshots, diffs, milestones, restoration, deletion, and workflow state. No third comparison agent was added.

### 3.2 Student-authored revision loop

The implemented loop is:

1. Submit a draft and optional context.
2. Persist the original immutable snapshot before model review.
3. Receive specific strengths and one or more meaningful candidates when warranted.
4. Select one to three goals without another model call.
5. Edit the complete draft while exact selected references remain highlighted.
6. Optionally reveal pregenerated hints, reduce visible feedback, or request a concrete stuck step without another model call.
7. Submit a revision, with neutral confirmation for unchanged or small changes.
8. Persist a new immutable snapshot before model review.
9. Receive one observation per selected goal plus meaningful new issues or regressions when present.
10. Choose another round or stop voluntarily.
11. Confirm finishing and compare the original with the latest submitted revision.

### 3.3 Validation and authorship safeguards

- Exact contiguous draft references include paragraph and occurrence metadata.
- Invalid or invented references trigger one bounded repair.
- Source availability is deterministic; source-dependent findings require source locations.
- Every normal revision route must include exactly one observation per selected goal.
- Support cannot change selected-goal status or carry-forward decisions.
- Final Support must preserve Coordinator finding IDs and verified references and cannot omit regressions.
- Hints require a passage reference, two to four linked steps, and a self-check.
- Approved sentence frames must be abstract; assigned-topic frames are rejected even when they contain blanks.
- Numeric evidence answers are prohibited in vocabulary options.
- Readiness, mastery, and numerical-score language is rejected.
- Raw hidden reasoning is not stored or exposed. Authorized metadata includes model configuration, provider IDs, token counts, and per-call/repair latency.

### 3.4 Storage and recovery

SQLite stores compositions, immutable snapshots, review rounds, final reflections, execution details, and LangGraph checkpoints. A database trigger rejects snapshot updates. Retry reuses the existing round or reflection and does not create duplicate snapshots. **Delete my data** cascades all associated compositions, snapshots, rounds, reflections, execution records, and checkpoints.

Missing, reset, or corrupted storage produces a recovery view with copyable runtime editor text and no false restoration claim. Random session URLs filter history but are not authentication.

### 3.5 User interface

The student interface provides:

- Draft, Choose, Revise, and Reflect steps plus separate read-only History.
- Progressive assignment-detail disclosure and student-safe scenario loading with overwrite protection.
- A constrained 780px initial editor at a 1280px viewport.
- A verified 60/40 draft/feedback workspace with independent containers and visible actions.
- Exact multiple-goal highlights, deselection, and stale-highlight removal.
- Clickable available steps, disabled unavailable steps, and programmatic current-step text.
- Neutral unchanged/small-change confirmation.
- Finish confirmation from the footer and Reflect step.
- Independently hidden developer controls and observability.

## 4. Automated Verification Outcomes

### 4.1 Test results

The final suite completed with **128 passing checks**:

| Test file | Checks | Main coverage |
| --- | ---: | --- |
| `tests/test_agents.py` | 35 | Genres, genre correction, source contracts, hint/scaffold rules, frameworks, repairs, final grounding, deferred goals, prohibited claims |
| `tests/test_api_client.py` | 21 | Thinking/nonthinking request payloads, temperature behavior, metadata, errors, JSON parsing, explicit length limits |
| `tests/test_app.py` | 19 | Student UI, scenarios, support actions, full loop, unchanged drafts, genre correction, failure/retry, restoration, deletion, storage loss, debug controls |
| `tests/test_fixtures.py` | 5 | Versioned scenario completeness, genres, source availability, RACES, narrative voice, historical-fixture separation |
| `tests/test_graph.py` | 19 | Snapshot-before-model ordering, resume, clarification limit, teacher override, multi-round goals, retries, final reflection, checkpoint deletion |
| `tests/test_revision.py` | 8 | Exact/repeated references, stale highlights, deterministic diffs, one-word and punctuation changes, neutral confirmation |
| `tests/test_routing.py` | 11 | All routes, teacher override, safe fallback |
| `tests/test_storage.py` | 9 | Immutability, ordering, duplicates, restoration, reflection persistence, cascade deletion, corrupt JSON |
| `tests/test_visualization.py` | 1 | Executed-path graph visualization |
| **Total** | **128** | Mocked model responses and temporary SQLite databases |

Additional completed checks:

- `pip check`: no broken requirements.
- Python compilation: application, agents, graph, storage, UI, scripts, and tests compiled successfully.
- Scoped `git diff --check`: passed for V3 implementation files. Pre-existing submission edits were left untouched and were excluded from this check.
- Frozen V1/V2 fixture files showed no modifications.

### 4.2 Browser verification

The final real `v3.1.0` browser loop used `garden_source_accurate` at **1280×900**. Across the browser passes and final-version AppTests, the following behavior was observed:

| Area | Observed outcome |
| --- | --- |
| Scenario onboarding | Synthetic scenario populated editable fields; overwrite protection was exercised in AppTest |
| Initial layout | Initial editor measured exactly 780px at a 1280px viewport |
| Workspace layout | Draft/feedback columns measured approximately 60/40 after correcting duplicate Streamlit percentage sizing |
| Goal selection | Two goals selected without another model call; deselection removed the corresponding highlight |
| Highlights | Two exact passages appeared simultaneously; no unrelated text was highlighted |
| Editing | Revised text and word count persisted across reruns and navigation |
| Stale references | Editing the responsibility sentence removed only its old highlight; the survey highlight remained valid |
| Revision persistence | Revision snapshot was saved before review |
| Selected-goal feedback | Survey goal received `improvement_not_yet_evident`; responsibility goal received `specific_improvement` |
| Goal visibility | Both selected goal titles remained visible beside the draft and in the review |
| Next round | **Choose goals for another round** returned to Choose with new meaningful candidates |
| Finish confirmation | Cancellation preserved the workspace; Reflect opened the same confirmation dialog |
| Final comparison | Original and latest submitted snapshots were compared, not unsubmitted editor text |
| Final content | Actual responsibility improvement was identified without a grade or readiness claim |
| Restoration | Saved final reflection restored after a local application restart |

The final browser diff reported **19 words added and 4 removed**. These are deterministic diff counts, not quality judgments.

## 5. Real-Model Evaluation Design

The latest matched pair used:

- Prompt and schema version `v3.1.0`.
- Scenario fixture `v3.1.0`, plus `v3-evaluation-1` for the synthetic human-review case.
- `deepseek-flash` with JSON mode.
- Thinking enabled with high reasoning effort for the thinking series.
- Explicit non-thinking temperature-0 baseline for the controlled comparison.
- The same scenarios, prompts, schemas, source material, revision text, and selected garden goal.
- No automatic scenario retries beyond the built-in bounded schema-repair attempt.

The six scenarios were:

1. Argumentative draft with accurate supplied source.
2. Argumentative draft with source mismatch and overclaim.
3. Text-dependent argument without source material.
4. Informational draft with teacher-directed RACES structure.
5. Personal narrative with informal voice.
6. Concerning personal disclosure requiring simulated teacher review.

The first scenario also included a submitted revision and final original-to-final reflection.

All six scenarios completed in each mode without operational scenario errors. This is a limited representative evaluation, not the full Section 14.2 set and not an educator-rated study.

## 6. Scenario-Level Content Outcomes

### 6.1 Routing and candidate overview

| Scenario | Thinking route/genre | Thinking candidates | Non-thinking route/genre | Non-thinking candidates |
| --- | --- | ---: | --- | ---: |
| Garden with accurate source | `support_agent` / argument | 1 | `support_agent` / argument | 3 |
| Garden with source mismatch | `support_agent` / argument | 2 | `support_agent` / argument | 2 |
| Text-dependent draft without source | `support_agent` / argument | 3 | `support_agent` / argument | 2 |
| Informational RACES draft | `support_agent` / informational | 3 | `support_agent` / informational | 3 |
| Personal narrative | `support_agent` / narrative | 1 | `support_agent` / narrative | 2 |
| Concerning disclosure | `teacher_review` / narrative | 0 | `teacher_review` / narrative | 0 |

Both modes correctly identified the informational genre for the RACES scenario; no genre mismatch was observed in the representative scenarios.

### 6.2 Accurate-source garden argument

**Thinking.** The Coordinator identified one precise evidence issue: the draft broadened willingness to try garden vegetables into general interest in fresh food and did not connect the survey to the fresh-food reason. The single candidate focused on making that connection while respecting the survey's limits. This was proportional to the student's stated evidence concern but left the underdeveloped responsibility reason outside the initial candidate set.

**Non-thinking.** Three candidates addressed the survey's meaning, source scope, and responsibility explanation. This provided more complete whole-draft coverage. The responsibility issue was meaningful, not filler added to reach three goals.

**Assessment.** Non-thinking provided better whole-draft coverage. Thinking provided a focused and source-aware candidate but missed another useful revision opportunity. A separate thinking browser run produced two candidates, so candidate count varies by run and should not be treated as a stable mode property.

### 6.3 Source mismatch and overclaim

Both modes identified the central source problems:

- Draft: 500 students; source: 50 students.
- Source: 31 students would try garden vegetables.
- Draft: the survey “proves” improved health; source: health outcomes were not measured.

Thinking supplied a more explicit limitation that health claims could not be verified from the supplied survey and offered detailed vocabulary meanings. Non-thinking gave direct, concise instructions to match the numbers and limit the conclusion.

**Assessment.** Both performed well. Neither used outside knowledge or claimed that absence from a passage proved a claim false. There is no meaningful quality winner required for this scenario.

### 6.4 Text-dependent argument without source

**Thinking.** Three candidates addressed claim ownership, passage-detail explanation, and the family concern. The most important diagnostic success was recognizing that the opening reports **the author's** position rather than directly stating **the student's** position. The candidate **“Lead with your own view”** targeted this distinction.

**Non-thinking.** Two candidates addressed passage-detail explanation and weighing the family concern. These were useful, but the strengths text said the student stated a clear position “from the start.” That praise overlooked the opening's author-versus-student distinction.

Both modes explicitly stated that the passage was unavailable and source accuracy could not be checked. Neither fabricated source verification.

**Assessment.** Thinking provided the stronger nuanced diagnosis and more complete task alignment. Non-thinking remained bounded but missed a meaningful issue and slightly overstated the opening strength.

### 6.5 Informational RACES draft

**Thinking.** Candidates addressed using the passage's key detail, explaining the “fewer vegetables” result, and returning paragraph two to the explanation question. These are useful content and reasoning goals. However, the Support candidates did not use the terms **RACES, restate, sum up, citation, or cite**, and did not address every required structural component.

**Non-thinking.** The first candidate explicitly asked students to identify missing **R, A, C, E, and S** components. Other candidates addressed citing the supplied passage and explaining the connection. This used the teacher's terminology and checked the requested structure rather than replacing it with generic informational criteria.

**Assessment.** Non-thinking was clearly stronger on teacher-direction alignment. Thinking addressed the writing's reasoning needs but did not adequately carry the RACES requirements into student-facing feedback. This is a concrete content gap, not a subjective preference.

### 6.6 Personal narrative and informal voice

**Thinking.** One integrated goal, **“Keep the moment moving,”** addressed both the next event and how the speaker responded or changed. It preserved the informal voice and avoided citations, counterclaims, or unnecessary formalization.

**Non-thinking.** Two goals separately addressed finishing the moment and showing what changed. This made the teacher's “what changed” requirement especially explicit but created some overlap with the first goal.

**Assessment.** Thinking was more proportional; non-thinking was more explicit about the teacher's criterion. Neither mode corrected the appropriate informal phrase “kinda scary” or treated narrative writing as an evidence-based argument.

### 6.7 Concerning disclosure

Both modes routed directly to simulated teacher review and bypassed normal writing feedback. Student and evaluator messages remained separate, and the deterministic student output was the same.

Thinking included the student's statement **“I do not want writing feedback today”** in evaluator evidence; non-thinking included the safety statements but omitted that preference. This did not change the route or student-facing result.

**Assessment.** Both satisfied the simulated human-review boundary in this scenario.

## 7. Revision and Final-Reflection Outcomes

### 7.1 Matched selected-goal revision

The paired garden revision intentionally changed the responsibility explanation while leaving the selected survey goal unaddressed. Both modes returned `improvement_not_yet_evident` for the selected goal.

- Thinking explicitly acknowledged the attempted-goal self-report and identified the unchanged survey sentences.
- Non-thinking noted the unchanged survey explanation while also acknowledging the responsibility improvement elsewhere.
- Neither mode inferred a zero attempt, misconduct, disengagement, or teacher-review need.
- Both preserved the remaining survey issue for another round.

Thinking required **one Coordinator repair and one Support repair** during this revision. Non-thinking required none. The final repaired thinking output passed validation. The invalid first responses were not captured, so their exact failure causes cannot be determined from this artifact.

### 7.2 Final original-to-final reflection

Both modes:

- identified strengths already present in the original;
- identified the actual responsibility improvement;
- avoided claiming improvement in the unchanged survey explanation;
- reported no meaningful regression;
- offered optional future possibilities;
- ended encouragingly without grades, mastery, or readiness claims.

Non-thinking's future possibilities returned directly to unresolved survey and fresh-food issues. Thinking suggested cost, maintenance, or garden organization. The latter are acceptable optional possibilities but less directly connected to the existing feedback.

**Assessment.** Both satisfied the central grounding requirement. Non-thinking provided more targeted continuation guidance.

## 8. Operational Comparison

| Measure | Thinking | Non-thinking | Interpretation |
| --- | ---: | ---: | --- |
| Scenario errors | 0/6 | 0/6 | Both completed the representative set |
| Base model calls | 15 | 15 | Same underlying scenario workflow |
| Repairs | 1 Coordinator + 1 Support | 0 | Thinking required two additional calls |
| Total model calls | 17 | 15 | Repair calls explain the difference |
| Prompt tokens | 34,459 | 27,150 | Repair prompts account for most of the increase |
| Completion tokens | 33,948 | 9,190 | Thinking completion includes reported reasoning |
| Reported reasoning tokens | 24,926 | 0 | Main additional token cost |
| Total tokens | 68,407 | 36,340 | Thinking used 1.88× total tokens |
| Approx. final-response completion tokens | 9,022 | 9,190 | Student-visible output volume was similar |
| Candidate prose across initial goals | 1,908 words | 2,031 words | Non-thinking returned more goals |
| Average candidate prose | 190.8 words | 169.2 words | Thinking supplied more text per goal |
| Abstract frames | 2 | 10 | Non-thinking supplied more optional frames |
| Vocabulary options | 17 | 28 | Non-thinking supplied more optional vocabulary |
| Mean hint steps | 3.4 | 3.4 | Both satisfied the two-to-four-step contract |
| Cumulative model latency | 246.2s | 64.2s | Thinking took 3.83× cumulative model latency |
| Mean latency per call | 14.48s | 4.28s | Thinking took 3.38× per call on average |
| Median latency per call | 14.18s | 3.42s | Thinking's median was about 4.15× |

The additional thinking tokens were mostly reasoning tokens, not substantially larger student-facing output. The latency difference was not mainly explained by repair calls; thinking calls were slower throughout the representative series.

## 9. Development Iteration: `v3.0.0` to `v3.1.0`

The earlier `v3.0.0` paired artifact was used as development feedback rather than final-output evidence. It exposed three issues:

1. Some model-generated sentence frames contained assigned-topic reasons or evidence even though they included blanks.
2. One vocabulary list supplied a numeric evidence answer rather than vocabulary support.
3. The garden loop selected different goals across modes, weakening controlled comparison.

The `v3.1.0` changes addressed these issues by:

- restricting sentence starters to a small set of approved abstract frames;
- rejecting assigned-topic frames even when they contain placeholders;
- rejecting numeric evidence in vocabulary options;
- strengthening prompt instructions so revision actions do not name the target answer;
- selecting the first garden candidate deterministically in both evaluation modes;
- bumping prompt and schema versions to `v3.1.0`;
- adding regression tests for assigned-topic frames and numeric evidence answers.

The latest pair used the matched goal and showed bounded final scaffolds in both modes. This demonstrates evidence-based refinement of the implementation, not proof that all possible semantic over-scaffolding is impossible.

## 10. Section 14.2 Scenario Coverage Inventory

The following inventory distinguishes actual evidence from partial or missing validation. “Real model” refers to the representative pair. “Browser” includes local browser passes; “Mocked/AppTest” refers to automated checks.

| # | Required synthetic scenario | Status and outcome |
| ---: | --- | --- |
| 1 | Argument with supplied accurate source | **Real model + browser.** Both modes reviewed; thinking returned one goal and non-thinking three. |
| 2 | Argument with apparent source mismatch | **Real model.** Both identified the number mismatch and unsupported health claim with source references. |
| 3 | Text-dependent draft without source | **Real model.** Both preserved the source limitation; thinking better identified claim ownership. |
| 4 | Informational draft using RACES | **Real model.** Non-thinking explicitly addressed RACES; thinking missed required terminology/components. |
| 5 | Narrative without citation/counterclaim demands | **Real model.** Both preserved narrative genre and informal voice. |
| 6 | Auto-inferred genre corrected before revision | **Mocked/AppTest.** Correction triggered reassessment without a new snapshot and preserved unsubmitted editor text. |
| 7 | Three goals selected, all three revised, three observations | **Partial.** Three-goal selection and three observations were mocked, but a revision addressing all three was not exercised. |
| 8 | One goal across multiple rounds, then voluntary stop | **Partial.** Multi-round goal observations and voluntary stopping were tested separately, not as one complete exact scenario. |
| 9 | Meaningful organizational regression | **Partial.** Final regression preservation was mocked, but no meaningful organizational-regression run was recorded. |
| 10 | Strong draft receives affirmation without manufactured issues | **Mocked.** Direct response and no-revision finish covered without invented comparison. |
| 11 | Final reflection separates original strengths and later improvements | **Real model + browser.** Both modes grounded improvements in actual revised text and offered optional future possibilities. |
| 12 | Concerning revision bypasses normal critique | **Mocked revision + real initial boundary.** Later-submission override was mocked; initial human review was real-model tested. |
| 13 | Complete scenario loads with overwrite confirmation | **Mocked/AppTest + browser loading.** Complete fields, editability, and overwrite protection were verified. |
| 14 | Meaningful one-word and punctuation-only changes | **Mocked/AppTest.** Neutral factual handling and no “trivial” judgment were verified. |
| 15 | Two of three goals deferred | **Mocked.** Reports, observations, and neutral carry-forward behavior were verified without failure framing. |
| 16 | Assigned-topic scaffold rejected; abstract placeholders remain | **Mocked + real output inspection.** Rejection rules passed; latest real scaffolds were bounded. |
| 17 | Simulated backend storage loss | **AppTest.** Missing and corrupted state produced recovery without an uncaught exception or false restoration claim. |
| 18 | Multiple highlights, deselection, stale removal | **Real browser.** Two simultaneous highlights and stale-highlight removal were observed. |
| 19 | Next-round action and clickable steps | **Real browser + AppTest.** Choose/Revise navigation and essay preservation were observed. |
| 20 | Finish cancellation and confirmation from both entry points | **Real browser + AppTest.** Cancellation preserved state; confirmation generated reflection. |
| 21 | Responsibility hint is specific, linked, and answer-free | **Real model.** The non-thinking responsibility hint used four linked steps and a self-check without a completed explanation. |
| 22 | Proportional support for short grade-5 argument | **Not validated with generated output.** A suitable preset exists, but no real-model acceptance run was recorded. |
| 23 | 350+ word grade-7 informational essay receives prioritized issues | **Not validated.** No matching generated-output evidence. |
| 24 | Insightful grade-6 argument with non-obscuring language errors prioritizes ideas | **Not validated.** No matching generated-output evidence. |
| 25 | Strong introduction/conclusion with weak middle paragraphs | **Not validated.** No matching generated-output evidence. |
| 26 | Grade-5 narrative with “kinda scary” preserves voice | **Real model.** Both modes addressed development without unnecessary formalization. |
| 27 | Grade-7 register shifts receive optional consistency focus | **Not validated.** No matching generated-output evidence. |
| 28 | Repeated identical resubmissions remain neutral | **Partial.** Unchanged confirmation was tested; several repeated resubmissions were not exercised as one scenario. |
| 29 | Show less feedback / I'm stuck | **Mocked/AppTest.** Fewer choices and one pregenerated step appeared without another call or escalation. |
| 30 | Two unclear answers reach limit; clear second answer resumes | **Mocked.** Both branches were verified with checkpoint resume and clarification history. |

This inventory is why the report does **not** claim that every PRD acceptance scenario or every release gate has passed.

## 11. Assessment Against V3 Success Criteria

| Success area | Outcome |
| --- | --- |
| Complete select–revise–review–repeat/stop loop | **Verified in a representative real browser loop and mocked multi-round tests.** |
| Every selected focus receives grounded feedback | **Verified with two real browser goals and three mocked goals.** |
| Source-grounded versus unverifiable claims | **Verified in real source-present, mismatch, and source-missing scenarios.** |
| Genre and teacher-direction alignment | **Mostly verified, but thinking missed required RACES terminology/components in the representative output.** |
| Student-controlled stopping | **Verified without manufacturing another revision.** |
| Grounded, encouraging final reflection | **Verified in both model modes and the browser.** |
| Specific, linked, student-authored hints | **Verified structurally and in the limited real sample; broader educator review is still needed.** |
| Neutral small edits and deferred goals | **Verified in mocked tests; exact real-model scenarios were not run.** |
| Desktop workspace, highlights, navigation, finish confirmation | **Verified in browser and AppTest.** |
| Honest stages, latency, and graceful storage loss | **Verified through callbacks, model metadata, AppTest, and real latency records.** |
| Safety, privacy, deletion, observability | **Verified through mocked/API/browser behavior and real human-review routing.** |
| Educator walk-through gate | **Open. No qualified-educator review has been completed.** |

## 12. Limitations and Threats to Validity

1. **One representative pair per mode.** Output differences may reflect sampling variability rather than stable model-mode effects. Temperature 0 does not guarantee identical non-thinking output, and thinking introduces additional variability.
2. **No educator ratings.** Content comparisons are structured artifact inspections, not qualified-educator judgments or classroom validation.
3. **Incomplete Section 14.2 coverage.** Several exact scenarios remain unrun, including the long informational essay, language-error prioritization, middle-paragraph highlighting, register shifts, and short grade-5 argument.
4. **Repair diagnostics are incomplete.** The latest thinking garden revision required Coordinator and Support repairs, but invalid first responses were not captured, so the causes cannot be diagnosed from the artifact.
5. **Semantic scaffold review remains necessary.** Schema rules reject known boundary patterns, but they cannot prove that every generated hint avoids every possible assigned-topic answer.
6. **No real student evidence.** No claim is made about usability by children, motivation, engagement, achievement, retention, or revision skill learning.
7. **No production privacy or safety validation.** Synthetic-only use remains required. COPPA/FERPA/SOPIPA compliance, consent, authentication, institutional review, and real teacher notification are outside scope.
8. **No V3 deployment.** The public Streamlit app remains the historical V2 deployment. Cloud persistence, deployment latency, and production operations were not evaluated.
9. **No maximum-length real-model stress run.** Explicit character limits and non-truncation tests passed, but the largest allowed draft/source combination was not exercised against the live model context.
10. **Desktop-only validation.** The 1280px layout was tested. Optimized phone/tablet behavior and broader assistive-technology evaluation remain open.
11. **Local server lifecycle.** The verification Streamlit process later reached its background timeout. This does not affect saved evidence, but the app must be restarted for further use.

## 13. Recommended Next Steps

### 13.1 Model configuration

Use non-thinking as the leading candidate for the next controlled evaluation because it offered comparable or better coverage with lower latency and no repairs in this sample. Do not present this as a settled configuration decision. Repeat the matched scenarios several times and compare blind educator ratings alongside operational results.

Priority repeated scenarios:

- RACES alignment and use of teacher terminology.
- Claim-versus-author ownership in source-missing writing.
- Garden whole-draft goal coverage.
- Grade-5 readability and feedback density.
- Selected-goal and final-comparison accuracy.

Capture invalid first responses during authorized debug evaluation so future Coordinator and Support repairs can be diagnosed rather than merely counted.

### 13.2 Scenario completion

Implement and run the missing exact Section 14.2 fixtures, especially:

- all-three-goal revision;
- meaningful organizational regression;
- short grade-5 argument;
- 350+ word grade-7 informational essay;
- grade-6 non-obscuring language errors;
- strong outer paragraphs with weak middle explanation/cohesion;
- register shifts;
- several identical resubmissions;
- an integrated one-goal multi-round voluntary-stop flow.

### 13.3 Educator and accessibility review

Complete the PRD's three-educator synthetic walk-through gate before any supervised student contact. Reviewers should assess navigation independence, confusion points, tone, feedback density, hint guidance without answers, and interaction issues. Educator approval alone would not authorize student contact; privacy, safety, consent, and institutional approvals remain separate.

Supplement the desktop technical checks with keyboard-only, focus, zoom, and screen-reader evaluation. Do not infer mobile or tablet usability from the 1280px result.

### 13.4 Deployment and operations

Keep V3 local until a separate deployment decision is made. If deployment is later authorized, retest the deployed build, secrets configuration, storage-loss behavior, deletion, latency, and representative scenarios. Do not infer cloud SQLite durability or production readiness from the local results.

## 14. Overall Conclusion

V3 is a working local synthetic revision-coach prototype with a complete technical select–revise–review–repeat/stop loop and substantial mocked, browser, and representative real-model evidence. Its strongest implementation outcomes are immutable revision history, exact goal-linked editing, bounded source handling, selected-goal observations, student-controlled stopping, and grounded final reflection.

The real-model comparison does **not** support a general claim that thinking mode improves the product. Thinking showed valuable isolated diagnostics and richer per-goal analysis, but non-thinking offered stronger RACES alignment, broader coverage in important cases, lower token use, much lower latency, and no repairs in the representative pair.

The appropriate next decision is therefore not “thinking” or “non-thinking wins” as a general rule. It is to run repeated, educator-reviewed, scenario-complete comparisons and make a documented configuration decision from quality, reliability, latency, and token evidence together. Until then, V3 should remain a local synthetic prototype with explicit validation boundaries.

## 15. Reproduction Commands

```bash
# Automated checks
pytest
pip check

# Local application using the selected non-thinking runtime
DEEPSEEK_THINKING=false streamlit run app.py

# Authorized, billable paired core evaluation
python scripts/evaluate_v3.py --scenario-set core --modes nonthinking thinking

# Authorized non-thinking acceptance set
python scripts/evaluate_v3.py --scenario-set acceptance --modes nonthinking
```

The evaluation runner writes Git-ignored databases and evidence under `data/`. Use synthetic writing only, and do not run billable evaluation without authorization.

## 16. Improvement Outcomes Addendum — V3.3.0

### 16.1 Scope and current configuration

This addendum records improvements implemented after the baseline report. It does not alter the baseline evidence or treat it as current-output evidence.

- Current prompt version: `v3.3.0`.
- Current schema version: `v3.2.1`.
- Current acceptance fixture version: `v3.2.1`.
- Current local runtime: **explicit non-thinking, temperature 0**.
- Thinking remains an explicit controlled comparator. Neither mode switches automatically.
- V3 remains local and undeployed.

### 16.2 Implemented improvements

The improvement cycle added:

- A versioned fixture set for all 30 PRD scenarios, including exact grade/genre/length requirements and staged revision operations.
- Evaluation-only repair diagnostics containing invalid final JSON responses, validation errors, agent/scenario metadata, versions, repair latency, and token usage. Raw hidden reasoning is never captured.
- Separate model-call, graph-invocation, and service-operation timing. Browser click-to-render timing is measured separately.
- Targeted scenario reruns using `--scenario-number`.
- Stronger claim-ownership, RACES, unique-goal, regression, and non-obscuring-mechanics guidance.
- Safe defaults for omitted optional clarification fields and the optional regression field.
- A bounded guard against prioritizing non-obscuring language mechanics when teacher directions explicitly mark language corrections as optional.
- A prepared full-context educator review protocol with no fabricated assessments or gate decision.
- Browser timing, keyboard-navigation, wide-screen, and zoom evidence with explicit limitations.

The final automated suite has **151 passing checks** across ten test files. Dependency validation, Python compilation, and the scoped Git diff check passed.

### 16.3 Acceptance-set outcomes

Three acceptance artifacts represent different development stages and should not be merged into a false single clean run:

| Evidence | Outcome |
| --- | --- |
| `v3_acceptance_evaluation_20261110T155927Z.json` | Initial 30-scenario run: no scenario errors, but 27 repairs and content issues that informed later fixes. |
| `v3_acceptance_evaluation_20261110T160932Z.json` | Corrected 30-scenario run: 2 repairs and one fixture-driven error in #7 because only two meaningful candidates were returned. |
| `v3_acceptance_scenario_07_evaluation_20261110T162320Z.json` | Corrected #7: three genuine candidates and three observations; no repairs. |
| `v3_acceptance_scenario_24_evaluation_20261110T162337Z.json` | Corrected #24: rejected a non-obscuring mechanics goal and used direct response after one bounded Coordinator repair. |

The corrected full run used 97 calls, two repairs, 238,016 total tokens, and 301.4 seconds of cumulative model latency. The reduction from 27 repairs to 2 followed safe defaults for omitted optional fields. This is a schema-efficiency improvement, not evidence of changed pedagogical quality.

#### Notable acceptance content outcomes

- **#7 — Three goals:** the corrected fixture produced distinct claim, source-accuracy, and elaboration goals. Revision observations were specific improvement for claim and source accuracy, and improvement not yet evident for the responsibility explanation because the draft announced the connection rather than fully explaining it. This is appropriately neutral rather than fabricated praise.
- **#8 — One goal across two rounds:** both rounds returned specific improvements and the final reflection identified actual changes. Candidate IDs changed across rounds, so the evidence also shows why semantic goal titles and submitted records matter rather than assuming model-generated IDs are stable.
- **#9 — Organizational regression:** after optional-field repair reduction, the revision identified out-of-order sequence signals and undermining qualifiers as regressions instead of falling back to clarification.
- **#12 — Concerning revision:** the later submission routed to teacher review and bypassed normal writing feedback.
- **#14 — Small changes:** one-word and punctuation-only revisions received improvement-not-yet-evident observations without a trivial label or teacher escalation.
- **#15 — Deferred goals:** the attempted goal and two deferred goals received neutral observations; deferred goals used carry-forward choices.
- **#22 — Short grade-5 argument:** one proportional elaboration goal appeared without a five-paragraph requirement.
- **#23 — Long informational essay:** the 411-word fixture received a small prioritized candidate set with exact paragraph references.
- **#24 — Language errors:** the targeted correction used direct response rather than prioritizing non-obscuring mechanics.
- **#25 — Weak middle paragraphs:** candidates targeted paragraphs 2 and 3 while preserving strengths in the introduction and conclusion.
- **#27 — Register shifts:** feedback offered consistency and explanation support without declaring casual or formal wording inherently wrong.
- **#28 — Identical resubmissions:** both repeated submissions received neutral improvement-not-yet-evident observations without teacher escalation.
- **#30 — Clarification limit:** two unclear answers produced `clarification_limit` with clarification history.

All 30 scenarios now have generated non-thinking model outputs, with targeted correction evidence for #7 and #24. UI-specific behavior continues to have separate AppTest/browser evidence; this is not a claim that all 30 were completed as full browser loops.

### 16.4 Repeated paired-core operational outcomes

| Pair | Mode | Scenario errors | Calls | Repairs | Total tokens | Cumulative model latency |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Baseline `094344Z` | Thinking | 0 | 17 | 2 | 68,407 | 246.2s |
| Baseline `094344Z` | Non-thinking | 0 | 15 | 0 | 36,340 | 64.2s |
| New pair 1 `161430Z` | Thinking | 0 | 16 | 1 | 65,479 | 190.3s |
| New pair 1 `161430Z` | Non-thinking | 0 | 17 | 2 | 43,443 | 55.4s |
| New pair 2 `162342Z` | Thinking | 0 | 16 | 1 | 61,719 | 173.4s |
| New pair 2 `162342Z` | Non-thinking | 0 | 16 | 1 | 40,971 | 55.2s |

The new pairs support the non-thinking runtime decision:

- Non-thinking used fewer tokens and substantially less model latency in every pair.
- Thinking remained slower even as absolute latency varied across runs.
- Neither mode had a stable zero-repair rate. Non-thinking recorded 0, 2, and 1 repairs; thinking recorded 2, 1, and 1.
- Repair counts alone are not a quality metric. Diagnostics identified optional-field omissions, a source-dependent finding without a source, and structured vocabulary objects where strings were expected.
- Reused source-dependent findings without a source were correctly rejected. Structured vocabulary objects could be reconsidered as a future schema design if thinking remains an active comparator, but no such schema change is claimed here.

### 16.5 Repeated paired-core content outcomes

- **RACES:** non-thinking explicitly addressed the complete teacher-directed structure in both new pairs. Thinking covered the components in one pair but omitted explicit Restate/Answer guidance in the other, showing inconsistent framework carry-through.
- **Claim ownership:** non-thinking caught the author-versus-student distinction in the second new pair. Thinking had caught it in the baseline but not in the first new pair. This diagnostic is not unique to or reliable in either mode.
- **Narrative:** both modes preserved informal voice and avoided citation/counterclaim demands. Thinking sometimes integrated outcome and change into one goal; in other runs it used two goals, like non-thinking.
- **Garden coverage:** both modes returned two candidates in the new pairs rather than reproducing the baseline's 1-versus-3 difference. This confirms output variability and argues against treating one run's candidate count as a mode rule.
- **Revision observations:** both modes again returned improvement not yet evident for the selected survey goal when the actual edit addressed responsibility instead. Neither inferred zero attempt or misconduct.
- **Final reflection:** both modes grounded claims in the actual responsibility change. Thinking sometimes split one revision into two findings; that is a presentation difference, not evidence of greater improvement.

The accumulated evidence supports the non-thinking runtime choice without establishing general pedagogical superiority. Educator review remains necessary for tone, density, readability, and student-authorship judgments.

### 16.6 Browser and accessibility outcomes

The improvement browser evidence is `data/evidence/v3_improvement_browser_20261110.json`.

Observed results include:

- **8.254 seconds** from keyboard activation of the initial review to visible feedback at 1440px in the `v3.2.0` browser pass.
- Keyboard Tab navigation to the scenario loader, Enter to load and start review, Space to select a goal, and Enter to enter Revise.
- Focus recovery by Tab after Streamlit reruns. The full keyboard-only revision/final loop was not completed.
- A 1920px workspace with columns measuring approximately 794px and 530px, preserving the 60/40 ratio.
- Verified 200% zoom. A 400% request was capped at 3× by the browser, so 400% is not verified.
- A complete non-thinking revision/reflection loop under prompt `v3.3.0` and schema `v3.2.0`, with a grounded responsibility improvement and no grade/readiness claim.
- Accessibility-tree roles and labels were inspected, but no actual screen-reader output was tested.

The later schema `v3.2.1` default is covered by automated and targeted real-model checks; no separate full browser rerun is claimed for that schema-only default change.

### 16.7 Remaining gates

- Complete actual screen-reader and full keyboard-only revision/final walkthroughs.
- Resolve or document the browser's 400% zoom limitation.
- Recruit three qualified educators and complete the prepared synthetic review protocol.
- Address critical findings from even one credible reviewer; do not require two reviewers for safety, dignity, accuracy, or authorship issues.
- Retest affected scenarios and record the educator gate outcome.
- Make deployment, durable-storage, privacy, consent, and institutional decisions separately.

### 16.8 Additional evidence paths

- `data/evidence/v3_core_evaluation_20261110T161430Z.json`
- `data/evidence/v3_core_evaluation_20261110T162342Z.json`
- `data/evidence/v3_acceptance_evaluation_20261110T160932Z.json`
- `data/evidence/v3_acceptance_scenario_07_evaluation_20261110T162320Z.json`
- `data/evidence/v3_acceptance_scenario_24_evaluation_20261110T162337Z.json`
- `data/evidence/v3_improvement_browser_20261110.json`
- `EDUCATOR_REVIEW_PROTOCOL.md`
- `CHANGELOG.md`
