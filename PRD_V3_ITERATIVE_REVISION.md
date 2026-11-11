# Product Requirements Document: V3 Iterative Revision Coach

- **Product:** Academic Writing Coach for Multilingual Learners
- **Audience:** Grades 5–7, primarily higher-level English learners
- **Release target:** Synthetic classroom prototype
- **Document status:** Local implementation; limited synthetic technical validation complete; educator review pending
- **Version:** 0.6
- **Date:** 2026-11-10

## 1. Document Purpose and Relationship to the Existing PRD

This document defines **V3**, including its product requirements and technical contract. The local implementation and its limited synthetic validation are recorded separately in `README.md` and git-ignored evidence artifacts; this specification itself is not evidence of quality or effectiveness.

[PRD.md](PRD.md) remains the authoritative historical record of the implemented V1/V2 coursework application, its architecture, and its verification evidence. V3 replaces the old local runtime, user flow, state model, storage design, prompts, and routing rules. No V3 requirement may be described as deployed, pedagogically effective, or educator-approved until corresponding evidence exists.

Related design feedback is preserved in [RUBRIC_DIRECTION_FEEDBACK.md](RUBRIC_DIRECTION_FEEDBACK.md). The [interactive desktop HTML mockup](mockups/v3_iterative_revision.html) illustrates the proposed layout and navigation with synthetic content; it is a design reference, not evidence of working AI behavior. This PRD governs where the mockup and requirements differ.

## 2. Executive Summary

### 2.1 Problem

Students in grades 5–7 often receive writing feedback that is too generic, too extensive, or disconnected from the assignment and source material. Higher-level English learners may have strong ideas but need targeted support with academic organization, evidence explanation, cohesion, register, or sentence structure. Treating their writing primarily as a collection of language errors can lower the academic ceiling and obscure their thinking.

A single feedback event also does not show whether a student can use feedback to improve a draft. Students need an opportunity to choose a manageable goal, revise their own writing, review what changed, and decide when to stop.

### 2.2 Product Vision

V3 is an **iterative, student-authored revision coach**. It evaluates writing through grade- and genre-appropriate ELA criteria, uses multilingual-learner pedagogy to scaffold revision, and helps students reflect on their progress without assigning an unvalidated grade.

The core loop is:

1. Submit a draft and assignment context.
2. Receive specific strengths and meaningful revision choices.
3. Select **one to three** focus areas.
4. Revise the draft without AI-written replacement prose.
5. Submit the revision for another review.
6. Repeat or stop at any time.
7. Finish with an encouraging comparison of the original and final submitted drafts.

### 2.3 Product Positioning

V3 is an **academic writing coach for multilingual learners**, not:

- an ELPAC score predictor or reclassification tool;
- an automated grader;
- an essay writer;
- a guarantee that a draft is ready to submit;
- a teacher replacement or automated teacher-notification system.

## 3. Goals and Non-Goals

### 3.1 Product Goals

1. Help students make purposeful revisions while preserving their ideas, authorship, and voice.
2. Provide ELA-aligned, genre-specific feedback rather than treating ELPAC as a universal essay rubric.
3. Separate ideas and reasoning from language mechanics without assuming that every error is caused by English-learner status.
4. Ground evidence feedback in supplied source material and clearly state when source verification is impossible.
5. Let students control revision volume and session length.
6. Show specific improvement between the original and final drafts without numerical scores or readiness claims.
7. Maintain observable, testable agent decisions and explicit safety boundaries.

### 3.2 V3 Non-Goals

- Real student accounts or unsupervised public use by children
- COPPA/FERPA compliance claims or school-wide deployment
- Teacher dashboards, class rosters, or learning-management-system integration
- Automated grading, CAASPP/SBAC score prediction, or ELPAC level prediction
- Reclassification recommendations
- Prewriting or AI-generated thesis/paragraph workflows
- File uploads or a curated source-passage library
- Native-speaker, newcomer, or all-proficiency-market coverage claims
- Automated submission to a teacher
- Learner-outcome, motivation, engagement, or retention claims without suitable studies

## 4. Users and Usage Context

### 4.1 Primary Student

- Grade 5–7 student, approximately ages 10–13
- Primarily a higher-level English learner who can communicate ideas in English
- Needs specific academic-writing guidance without excessive correction or condescension
- May need optional support with academic phrasing, cohesion, vocabulary, or sentence combining

### 4.2 Teacher or Evaluator

- Supplies synthetic assignments, drafts, source passages, and classroom directions for prototype evaluation
- Reviews whether feedback is accurate, appropriately bounded, and aligned with the supplied task
- May inspect routing, evidence limitations, revision history, and model behavior through opt-in observability

### 4.3 Developer

- Needs structured outputs, revision snapshots, error logs, and prompt/response controls for debugging
- Must be able to distinguish observed system behavior from pedagogical hypotheses

### 4.4 Release Context

V3 is limited to synthetic or teacher-provided demonstration material. It does not support real student PII, authenticated accounts, or confidential classroom records. A supervised classroom pilot with real students would require a separate privacy, safety, consent, and operational review.

## 5. Scope and Priority

### 5.1 Must Have for V3

- Argumentative, informational, and narrative writing support
- Optional student genre selection with correctable system inference
- Assignment prompt, teacher directions, and optional source-material inputs
- Genre-specific, rubric-informed assessment without numerical scores
- Selection of one to three revision focus areas
- In-app student editing and immutable submitted revision snapshots
- Repeated whole-draft review after each submitted revision
- Feedback on every selected focus and meaningful new issues or regressions
- Optional scaffolds that do not supply completed target responses
- Student-controlled stopping
- Original-to-final comparison with specific improvements and future possibilities
- Process-based progress indicators
- Clarification, direct-response, and simulated teacher-review boundaries
- Session restoration and deletion of all associated drafts and history
- Graceful recovery when persisted history is unavailable
- Student-focused default UI with developer controls and observability hidden by default
- Curated synthetic scenario presets and progressively disclosed optional inputs
- Honest review-stage updates and per-stage latency measurement
- Explicit non-thinking runtime configuration for all model-driven agent calls, with controlled thinking comparisons and quality evidence recorded separately from V1/V2

### 5.2 Could Have After the Core Loop Is Verified

- Common classroom-framework presets such as CER or RACES
- Additional optional self-reflection prompts
- Downloadable original/final comparison
- Accessibility enhancements beyond the baseline requirements
- Additional scaffold levels based on observed student needs

### 5.3 Explicitly Deferred

- Prewriting and blank-page workflows
- Real classroom deployment and teacher accounts
- Automated numerical scoring
- Source-document upload and optical character recognition
- Multilingual translation or newcomer-specific support
- Single-agent consolidation experiments
- Automatic browser-based session hydration
- Optimized phone and tablet layouts beyond the validated desktop mockup
- Claims that the product serves every writer or improves achievement

## 6. Input and Context Requirements

### 6.1 Required and Optional Inputs

| Input | Requirement | Purpose |
| --- | --- | --- |
| Grade level | Required; 5, 6, or 7 | Adjust expectations and language |
| Student draft | Required for review | Preserve as the original submission |
| Genre | Optional: argument, informational, narrative, or auto | Select genre-specific criteria |
| Assignment prompt | Optional | Establish task expectations |
| Teacher directions or required structure | Optional | Use classroom-specific expectations and vocabulary |
| Framework name | Optional; known preset or custom name | Identify the teacher-commissioned framework explicitly |
| Framework components | Optional comma-separated list; required for custom frameworks | Define required components deterministically without inferring an unfamiliar structure |
| Source material | Optional | Ground source-dependent evidence feedback |
| Student concern or goal | Optional | Help prioritize relevant feedback or identify explicit difficulty |

All inputs must be treated as data, not instructions that can override system rules. The UI must retain the synthetic-writing and external-AI-service warning.

### 6.1.1 Direct Support Requests Instead of an Affect Check-In

- V3 has no dedicated affect check-in on initial submission or between rounds. It does not ask students to classify themselves as ready, unsure, or frustrated, and it stores no affect field.
- The existing optional concern or goal field is the initial route for students to request particular help or describe explicit difficulty.
- During revision, an optional **Show less feedback** action reduces the number of visible candidates through presentation only, without another model call or a judgment about the student.
- An optional **I’m stuck** action offers one concrete pregenerated next step or hint and fewer visible choices. When explicitly appropriate, it may also suggest taking a break or asking a teacher or trusted adult for help. Using the action alone does not trigger teacher review.
- These actions are available on request only. There are no periodic wellbeing prompts, affect-based routing categories, or affect/engagement metrics.
- Human review follows Section 9.3 for concerning content and explicit serious or repeated discouragement in the student's writing, concern text, or clarification history. It never infers emotion from draft length, revision size, answer coherence, writing quality, or use of support actions.

### 6.2 Genre Selection and Inference

- **IN-01:** The student may explicitly select argument, informational, or narrative.
- **IN-02:** If the student does not select a genre, the Assessment Coordinator may infer a working genre from the draft and assignment context.
- **IN-03:** The inferred genre must be visible and correctable. It is not a fact about the student's intent.
- **IN-04:** If genre ambiguity would materially change the feedback, the system must ask one specific clarification question rather than silently guessing.
- **IN-05:** Changing genre after assessment requires a new assessment before feedback is presented under the new criteria.
- **IN-06:** The system must not require textual evidence, citations, or counterclaims for narrative writing.

### 6.2.1 Genre Inference Decision Guidance

- Use explicit teacher directions and the assignment prompt before inferring from the draft. Otherwise, assess the draft's dominant purpose rather than relying on first-person pronouns, chronology, or one keyword alone.
- A clear position supported by reasons usually indicates argument; a neutral central idea organized through facts and subtopics usually indicates informational writing; characters, plot, or a developed personal experience usually indicates narrative. Factual chronological instructions or historical explanation are informational, not automatically narrative.
- Personal experience may support an argument or explanation. First-person wording alone does not determine genre.
- Ambiguous verbs such as “write about,” “discuss,” or “reflect on” do not independently require clarification. Clarify only when mixed features, an early indeterminate outline, or a prompt/draft conflict would materially change the assessment criteria.
- The clarification presents one main question with two or three likely genre choices plus **Something else / not sure**; it does not force a choice.
- Display the working genre and its basis, and record categorical confidence and observable evidence in observability rather than an unvalidated numerical probability. A student correction directly triggers reassessment under IN-05 and does not itself require another clarification answer.

### 6.3 Assignment and Classroom Frameworks

- **IN-07:** General feedback must remain available when no classroom framework is supplied.
- **IN-08:** When teacher directions explicitly specify CER, RACE/RACES, MEAL, or another structure, feedback must use that terminology and check the requested components. Known presets supply their usual components; custom frameworks require an explicit component list. The Coordinator returns one framework-neutral coverage entry per `(framework, component)` pair, using an exact present reference or an existing issue goal. Support renders that handoff and cannot add issues to complete a framework.
- **IN-09:** The system must not invent teacher requirements or force every essay into a named paragraph formula.
- **IN-10:** A classroom framework guides structure; it does not replace genre-specific assessment criteria.

### 6.4 Missing Source Material

- **IN-11:** Source material is optional because not all assignments are text-dependent.
- **IN-12:** Without source material, the system may assess the presence and internal coherence of reasoning and elaboration.
- **IN-13:** Without source material, the system must not claim that a quotation, fact, paraphrase, or citation is accurate or faithful to the source.
- **IN-14:** When source-dependent verification is relevant but impossible, feedback must state the limitation briefly and invite the student to add the passage.
- **IN-15:** With source material, the system may compare evidence against the supplied passage and identify apparent mismatches with a specific reference. Such findings remain fallible AI observations, not guaranteed verification.
- **IN-16:** The system must not invent missing source content or use supposed outside knowledge to override the supplied passage.

### 6.4.1 Source-Grounded Feedback Contract and Examples

- The application deterministically sets `source_material_available` from the actual input; the model does not infer it. Source-dependent findings require a `source_location` such as a paragraph or sentence reference. When no source-dependent finding is made, that field may be empty.
- With a supplied source, an acceptable mismatch observation is: “Your essay says the survey included 500 students. I see ‘50 students’ in paragraph 3 of the supplied passage. Double-check that number.”
- An acceptable absence observation is: “I do not see ‘improved test scores’ in the passage you provided. If this came from a different source or class discussion, consider identifying it; otherwise, check which passage you meant to use.” This does not prove that the claim is false.
- An acceptable interpretation prompt is: “Your essay calls the irrigation wasteful, while paragraph 4 describes drip irrigation as efficient. Reread that paragraph and check whether your interpretation matches.” Do not speculate about author intent or unprovided research methods.
- Without a source, an acceptable limitation is: “Your explanation of how the evidence supports your claim is clear. I cannot check whether the quotation or statistic matches its source without the passage.” “Your quotation looks correct” and “This statistic seems reasonable” are prohibited.
- Even with a source, avoid unqualified declarations such as “This evidence correctly represents the source.” Use bounded observations tied to the supplied text, and preserve Coordinator limitations in student-facing Support feedback.

### 6.5 Onboarding and Synthetic Scenario Presets

- **ON-01:** The initial view presents grade level and student draft as the primary inputs. Optional assignment details are grouped under a clearly labeled **Add assignment details** control rather than displayed as equally prominent required tasks.
- **ON-02:** A student-safe **Load a practice scenario** option provides curated synthetic scenarios without exposing developer controls or observability.
- **ON-03:** Each scenario populates every relevant field, including teacher directions and source material when the task is text-dependent. Scenarios cover all three genres and support source-present and source-missing evaluation.
- **ON-04:** Loading a scenario requires confirmation before replacing nonempty inputs or an active composition.
- **ON-05:** Loaded content remains editable, and the scenario identifier and fixture version are recorded with the composition for reproducible evaluation.
- **ON-06:** Scenario presets reduce prototype setup effort; their presence is not evidence that manual onboarding is effective for real students.

## 7. Pedagogical and Assessment Requirements

### 7.1 Assessment Approach

V3 uses **one ELA-informed assessment framework**, informed by grade- and genre-appropriate standards and Smarter Balanced-style categories, with ELD-informed revision support. It does not present separate ELPAC and 6+1 Traits scores.

Unless an official rubric is implemented faithfully, all descriptions must use **“rubric-informed”** or **“Smarter Balanced-inspired”**, not “official SBAC score” or equivalent wording.

### 7.2 Genre-Specific Criteria

**Argumentative writing**

- Clear claim or position and consistent purpose
- Organization and logical relationships
- Relevance and framing of reasons and evidence
- Explanation of how evidence supports the claim
- Counterclaims only when appropriate to the grade and assignment
- Academic language, cohesion, voice, and conventions

**Informational writing**

- Clear central idea and focus
- Logical grouping and transitions
- Relevant facts, details, examples, or supplied-source information
- Explanation and elaboration rather than unexplained listing
- Precise language, cohesion, voice, and conventions

**Narrative writing**

- Clear situation, purpose, and sequence
- Development of events, characters, setting, or experience as appropriate
- Relevant details and elaboration
- Pacing, connections, and closure appropriate to the task
- Language, voice, dialogue conventions where relevant, and general conventions

### 7.3 Feedback Priorities

Unless problems seriously obscure meaning, feedback normally prioritizes:

1. Central idea, claim, purpose, or narrative development
2. Evidence, details, and elaboration appropriate to the genre
3. Organization and connections
4. High-impact academic language and conventions

The system must not manufacture issues to fill a quota. A strong draft may receive affirmation and an optional refinement rather than forced criticism.

### 7.4 Multilingual-Learner Support

- Recognize ideas and reasoning separately from language mechanics.
- Do not infer English proficiency, emotion, or disability from writing.
- Preserve student voice and avoid unnecessary formalization.
- Offer optional support with cohesion, sentence combining, precise vocabulary, register, and explanation of ideas.
- Sentence frames must be suggestions, not required language.
- Higher-level learners should receive appropriately challenging analytical prompts rather than automatically simplified language.
- Do not add an English-proficiency label or a fixed “scaffolding level” slider in V3; Section 18 separately defers whether broader proficiency-differentiated support should be explored.

### 7.5 Scores and Completion Claims

- No numerical rubric scores, letter grades, or predicted standardized-test outcomes.
- No “Ready to Submit,” “Good Enough to Turn In,” or equivalent claims.
- No claim that the student has mastered a skill based on one revision.
- Descriptive feedback must identify observable text features and revision actions.

### 7.6 Operational Meaning of “Meaningful” and “Uncertain”

- A **meaningful issue** affects the central idea or task, genre or teacher requirements, reader understanding, or a recognizable pattern across the draft. A localized issue can be meaningful when it affects a critical claim, source interpretation, or clarity. An isolated convention or synonym choice is not meaningful merely because it can be corrected; it must obscure meaning, matter to the assignment, or be a student-selected concern.
- A **meaningful change** has an observable relationship to a selected goal or another important aspect of the writing. No word-count threshold applies: a one-word change to a critical claim may matter, while a large unrelated addition does not establish improvement in a selected goal.
- A **meaningful regression** introduces a contradiction, removes an essential claim or support without replacement, creates a new task/genre mismatch, or makes previously clear meaning harder to understand.
- Partial progress is described as progress with a remaining step, not as failure. When evidence is ambiguous, acknowledge student work separately from quality judgment; default toward recognizing effort without inventing improvement.
- **Uncertain** is appropriate only when relevant changes exist but their relationship to the selected goal cannot be judged responsibly, evidence conflicts, or a necessary reference is missing or ambiguous. It is not a generic hedge when the available text clearly shows improvement or clearly shows that improvement is not yet evident.

## 8. Core Iterative Revision Experience

### 8.1 Initial Assessment

- **RV-01:** The original submitted draft must be stored as an immutable snapshot.
- **RV-02:** Every nonempty initial submission goes to the Assessment Coordinator so human-review boundaries precede writing-quality feedback.
- **RV-03:** Normal feedback begins with genuine, specific strengths without exaggerated praise.
- **RV-04:** The system presents only meaningful revision candidates. Depending on the draft, this may be one candidate, several candidates, or no required revision.
- **RV-05:** Each candidate includes a student-friendly title, why it matters, a brief example or accurate reference from the draft, and one manageable revision action.
- **RV-06:** Candidates must not include a completed replacement claim, evidence explanation, paragraph, or other target response.

### 8.2 Focus Selection

- **RV-07:** When revision candidates exist, the student selects **at least one and no more than three** before starting a focused revision.
- **RV-08:** If only one meaningful candidate exists, the student may select that one; the system must not add weaker issues to reach three.
- **RV-09:** Selection changes the displayed guidance only and does not require another model call.
- **RV-10:** Selected goals remain visible beside or above the editing area.
- **RV-11:** The student may stop instead of revising. If no revision has been submitted, the system must not invent a before-and-after improvement summary.

### 8.3 Student Editing and Scaffolds

**Scaffolds** are all optional revision supports. **Hints** are the primary passage-specific, two-to-four-step thinking guidance described in RV-14; practice, vocabulary considerations, and sentence starters are supplementary scaffolds. “Support” may also describe human or instructional help generally and is capitalized only when referring to the Support Agent role.

- **RV-12:** The student edits the complete current draft in an editable writing area.
- **RV-13:** The application must not provide one-click AI insertion, replacement, or automatic polishing of student prose.
- **RV-14:** Optional hints must be specific to the selected goal and referenced passage rather than relying on a generic question alone. Each hint gives a short sequence of two to four linked thinking steps or guiding questions, directs attention to relevant student words or details, explains what to examine and how to attempt the revision, and includes a self-check when useful. Vocabulary considerations or incomplete sentence starters may supplement this guidance when appropriate.
- **RV-15:** A scaffold must require the student to supply the target idea or language. Specific guidance must not become a completed target response or an assigned-topic reason, piece of evidence, explanation, or replacement wording that the student could use as that response.
- **RV-16:** Optional practice uses abstract placeholders or a topic checked against the assignment and source material to ensure it is unrelated. It must not produce prose to paste into the essay; a fixed example topic is not automatically considered unrelated.
- **RV-17:** Revealing a pregenerated scaffold does not make another model call.
- **RV-18:** Editing and focus selection do not send text to the model. Model review occurs only after explicit submission or another deliberate AI action.

For the draft sentence **“This would help them become better citizens,”** an acceptable specific hint is: “Think about what students must remember or do without being reminded while watering and weeding. How could practicing that responsibility affect their classmates or school community? Write that connection in your own words, then check whether your sentence explains how the action leads to the effect.” In contrast, **“Why does this reason matter?”** alone is too generic to satisfy RV-14. The acceptable hint guides the student's thinking without supplying the explanation.

#### 8.3.1 Additional Hint Examples

- **Argument—counterclaim response:** For “Some people disagree,” ask: “Look back at your main claim. What is one specific concern a reader could have about it? State that concern in your own words, then respond using a reason or evidence already in your draft rather than inventing a fact. Check that your response addresses the concern instead of merely repeating your claim.” “Why might someone disagree?” alone is insufficient, and suggesting the counterclaim for the student violates RV-15.
- **Informational—elaboration with a source:** For “Bees help plants grow,” ask: “Find the part of your source that describes pollination. What does it say bees move from flower to flower, and what happens next? Explain that sequence in your own words, then check that each step is supported by the source and that a classmate could follow it.” “Add more details about bees” is insufficient; supplying the process for the student would be inappropriate.
- **Narrative—character development:** For “Maria was nervous. She went inside,” ask: “Picture the moment before Maria enters. What could she notice or do that would let readers infer her nervousness without naming it? Choose one action or sensory detail that fits what you imagine, add it before she enters, and check that it also makes sense with what happens next.” “Describe her feelings more” is insufficient; providing the detail for Maria would supply the student's elaboration.
- **Organization—cohesion:** When one paragraph discusses responsibility and the next discusses academic achievement, ask: “Is this an additional reason, a contrast, or an effect of the first paragraph? Revise the opening so it names that relationship for the reader. Then read the previous paragraph's final sentence and your new opening together to check that the connection is real, not just an added transition word.” “Add a transition” is insufficient.
- **Academic language—precision:** For “This thing helps students,” ask: “Look at the previous sentence. What exactly does ‘this thing’ refer to? Replace it with that specific noun, then decide what you mean by ‘helps’: does it teach, improve, require, or encourage something? Choose the word that matches your meaning and reread the sentence to check that it says exactly what you intend.” “Use better words” is insufficient, and the vocabulary choices are options to evaluate, not interchangeable replacements.

#### 8.3.2 Scaffold Boundary Edge Cases

Permitted scaffolds include:

- Abstract placeholders and structural sentence starters that leave the target idea entirely to the student
- Linked self-questioning and revision processes tied to the student's passage
- Process demonstrations on a topic checked as unrelated, without introducing facts into the student's assignment
- Context-compatible vocabulary options whose meanings the student must evaluate, not lists of supposedly interchangeable synonyms

Prohibited scaffolds include:

- Assigned-topic reasons, counterclaims, evidence, explanations, narrative details, or lists that effectively supply those target ideas
- Completed explanations or replacement prose for the student's assignment
- Fill-in frames containing the student's claim, reason, or required explanation; an abstract frame is acceptable only when the student must still generate the substance
- Examples on the same or a substantively equivalent topic presented as though they were unrelated

Use two checks: **(1)** Could the student paste the scaffold into the essay and obtain a coherent on-topic response? **(2)** Does the scaffold name a reason, piece of evidence, explanation, or elaboration that the student was asked to produce? A yes answer to either check prohibits the scaffold. Merely containing a blank does not make a scaffold acceptable, and merely being unrelated in wording does not make an example substantively unrelated.

### 8.4 Submitting a Revision

- **RV-19:** Each explicit revision submission creates and persists a new immutable snapshot linked to the same composition before model review begins.
- **RV-20:** The original draft remains unchanged throughout the session.
- **RV-21:** If the submitted text is unchanged, the UI asks whether the student wants to return to editing or continue before making a model call. A configurable small-change threshold may also trigger a neutral, factual change summary and the same choice. The threshold controls only the notification: it must not call a revision trivial, block submission, or infer whether a goal was attempted, and no fixed minimum word count establishes that a revision is meaningful.
- **RV-22:** Each revision submission receives a whole-draft review, not merely a check of isolated edited sentences.
- **RV-23:** Review compares the current draft with the immediately previous submitted draft and uses the original draft as session context.
- **RV-24:** Every selected focus receives an individual observation: specific improvement, improvement not yet evident in this revision, or uncertain. These are descriptive observations, not scores. “Improvement not yet evident” describes the available text evidence, not the student's effort, and the system must not infer a zero-attempt or “not attempted” status from the diff alone.
- **RV-25:** Before review, the student may optionally identify which selected goals they tried or intentionally deferred. Feedback uses that self-report to acknowledge effort and offer carry-forward choices without failure framing; if the student skips it, the system makes no attempt assumption. Feedback acknowledges meaningful improvement without declaring success when the text does not support that claim.
- **RV-26:** The review may identify meaningful new issues or regressions introduced during revision, but must not invent a new problem merely to continue the loop.
- **RV-27:** The student receives another set of one or more meaningful candidates when warranted and may select one to three for the next round.
- **RV-28:** If no actionable issue remains, the system says so and offers a student-controlled finish rather than endless polishing.

### 8.5 Student-Controlled Stopping

- **RV-29:** The student may stop after any completed review.
- **RV-30:** There is no fixed maximum round count in the product flow. Technical abuse limits may be introduced later but must not be presented as pedagogical completion.
- **RV-31:** The system never makes the student revise every suggested area.
- **RV-32:** Explicit serious or repeated discouragement in the student's writing, concern text, or clarification history follows the human-review boundary rather than another automatic revision cycle. Using **I’m stuck**, requesting less feedback, or showing limited revision progress does not itself establish that boundary.

### 8.6 Final Original-to-Final Comparison

When at least one revision has been submitted, stopping triggers a final comparison of the **original submission and latest submitted revision**.

The comparison includes:

1. Genuine strengths already present in the original draft, when relevant.
2. Specific improvements grounded in actual text changes.
3. Brief references to the selected focus areas and revision rounds where useful.
4. One to three optional future areas when meaningful, framed as possibilities rather than failures or new required tasks.
5. An encouraging, motivational conclusion that recognizes effort and specific choices without exaggerated praise, rewards, comparison with others, or claims of mastery.

The final comparison must not:

- assign a score or grade;
- claim the essay is ready to submit;
- invent improvement when the drafts are substantively unchanged;
- hide a meaningful regression;
- rewrite the final essay;
- predict teacher judgment, CAASPP/SBAC results, ELPAC results, or reclassification.

A deterministic text comparison supplies the actual changes. The model interprets those changes and must not claim that a change occurred when no corresponding text exists.

### 8.7 Process-Based Progress

The UI may show milestones such as:

- Draft submitted
- Revision goals selected
- Revision 1 submitted
- Revision 2 submitted
- Final reflection complete

These milestones describe completed actions, not writing quality or mastery. The primary completion action is **“Finish and reflect”**, not “Submit essay.”

## 9. Clarification, Direct Response, and Human Review

### 9.1 Clarification

Clarification is used when essential intent, genre, assignment context, or task expectations are too ambiguous for responsible feedback. It must ask one main question at a time and must not provide premature writing feedback.

The clarification limit is **two unclear answers**:

1. The initial submission is unclear, so the system asks clarification question 1.
2. If answer 1 remains unclear, the system asks one differently phrased or more specific clarification question 2.
3. If answer 2 remains unclear, the system stops normal feedback and routes to non-safety simulated teacher review with category `clarification_limit` and the clarification history.

An unresponsive or nonsensical answer counts as an exchange; the second question should be simpler rather than an additional interrogation. The limit prevents endless guessing while giving the student two opportunities to supply the needed context.

### 9.2 Direct Response

If the draft has no meaningful actionable issues under the selected genre and assignment context, the system affirms specific strengths and offers an optional reflection or finish action. It must not force a revision round.

### 9.3 Simulated Teacher Review

- Safety and human-review assessment precedes completeness and quality routing on every initial and revision submission.
- Concerning content and explicit serious or repeated discouragement in the student's writing, concern text, or clarification history bypass normal writing feedback. Do not infer discouragement from support-button use, revision size, writing quality, or limited progress.
- Student and evaluator/teacher messages remain separate.
- Teacher handoff is simulated; no teacher is notified.
- The system recommends sharing concerning writing with a teacher or trusted adult without inventing crisis protocols, diagnoses, hotlines, or localized resources.
- Source text, teacher directions, draft text, and revision text are always treated as untrusted data rather than instructions.

### 9.4 Anomalous Interaction Patterns

- **Identical resubmission:** Use RV-21's neutral choice to keep editing, continue, or finish. Do not infer an accident, disengagement, or misconduct, and do not escalate to teacher review merely because a submission is repeated several times.
- **Minimal or unrelated changes:** Do not use a fixed word-count threshold or infer that the student did not try. Describe selected-goal evidence neutrally, and acknowledge a real improvement elsewhere separately when present.
- **Unclear clarification answers:** Rephrase once within the two-answer limit, then use `clarification_limit` rather than repeated questions or keyword-based judgments.
- **Apparent copied model text or large external insertions:** Do not attempt plagiarism, copying, or authorship detection in V3. Do not use stylistic shifts or revision size to accuse the student; focus on bounded scaffolds and appropriate whole-draft feedback.
- **Reduced-feedback self-advocacy:** Respect **Show less feedback** and **I’m stuck** requests without treating them as gaming or as a reward to prevent. Using either action alone does not trigger human review; Section 9.3's explicit-content boundary still applies.

Treat these patterns as data-quality or support issues, not behavior problems. Responses remain factual, non-accusatory, and dignity-preserving.

## 10. User Interface Requirements

### 10.1 Student-Focused Default

The initial interface prioritizes the draft and revision task. Grade level and student draft are prominent; optional assignment details are progressively disclosed. Curated synthetic practice scenarios are available without exposing developer controls or agent observability. The student header omits evaluator reveal controls unless `SHOW_EVALUATION_CONTROLS=true`; when enabled, developer controls and agent observability remain independently hidden until selected. `ENABLE_DEBUG_MODE` separately governs raw prompt/response capture controls and does not replace the evaluator-display setting.

The initial essay editor uses a constrained, centered column that scales with viewport width and height, with minimum and maximum bounds for readability. It should use available desktop space without becoming an unbounded full-width editor.

### 10.2 Principal Views and Steps

The top-level steps are **Draft**, **Choose**, **Revise**, and **Reflect**. Round review and history are workspace states, not additional top-level steps.

1. **Draft:** constrained essay input, grade, an optional assignment-details section, and a **Load a practice scenario** action with overwrite protection.
2. **Choose:** strengths, revision candidates, source limitations, and selection of one to three goals.
3. **Revise:** current editable draft, selected goals, optional hints and scaffolds, optional **Show less feedback** and **I’m stuck** actions, optional attempted/deferred goal self-report, revision review, and revision submission.
4. **Reflect:** original/final comparison, specific improvements, optional future possibilities, and process summary after the student confirms completion.
5. **History:** read-only submitted snapshots and associated goals; no overwriting of prior submissions.

### 10.3 Desktop Draft-and-Feedback Layout

- After feedback is available, the desktop workspace uses approximately **60% width for the editable draft and 40% for feedback** as the initial proposed layout, not as evidence that this is the best arrangement for every draft or learner.
- The essay remains editable while its corresponding feedback stays visible, reducing whole-page scrolling and context switching.
- Draft and feedback panes scroll independently. Primary revision actions remain visible in a fixed or sticky feedback footer.
- New feedback replaces the previous feedback-panel content without replacing or scrolling the essay away from the student's current work.
- V3 validation targets this desktop layout at browser widths of 1280px and above with representative draft lengths. Alternative tabbed, collapsible, or full-width layouts require separate evaluation. Optimized phone and tablet behavior is deferred and must not be inferred from the desktop mockup; any real classroom pilot must revisit device access.

### 10.4 Goal-Linked Essay Highlights

- Each revision candidate includes an exact draft reference and enough location information to distinguish repeated passages, such as paragraph or occurrence metadata.
- Selecting a goal highlights its referenced passage in the essay and scrolls it into view when necessary; deselecting removes that highlight.
- Multiple selected goals may display multiple highlights simultaneously.
- Highlights remain synchronized with editor scrolling and are recalculated as the student edits.
- If the referenced passage can no longer be located reliably, the UI removes the stale highlight and does not highlight unrelated text. It may explain that the original reference changed.
- The system must not highlight invented or misquoted model references.
- Highlights are presentation metadata, not changes to the saved essay, deterministic diff, or model-visible draft text.
- Highlight meaning must also be available through text and accessible goal descriptions; color alone is insufficient.

### 10.5 Clickable Steps, Next-Round Action, and Finish Confirmation

- Available steps are keyboard-accessible buttons. Unavailable future steps are disabled rather than opening empty or invalid states.
- The four steps appear in the header. Step navigation preserves the current essay and existing feedback, and the current step is exposed visually and programmatically.
- Completed steps reflect actual submitted snapshots, goal selections, and completed reflection rather than assuming every earlier numbered step is complete. Completion uses a textual marker as well as color.
- After a revision review, the footer action changes from **Submit revision** to **Choose goals for another round**.
- Selecting **Choose goals for another round** returns the indicator to **Choose**, displays revision candidates, and restores the **Submit revision** action for the next submitted draft.
- **Finish and reflect** opens a confirmation dialog before final reflection. The dialog asks whether the student wants to stop revising and offers **Keep revising** and **Yes, finish and reflect**.
- Cancelling closes the dialog without changing the current draft, feedback, or step. Selecting the **Reflect** step opens the same confirmation dialog; final comparison begins only after confirmation.

### 10.6 Usability and Accessibility

- Use plain, grade-appropriate language and avoid academic jargon unless supplied by the teacher and explained.
- Do not rely on color alone to communicate improvement, concern, selection, or highlighted references.
- Preserve readable contrast, keyboard navigation, visible focus, and accessible labels.
- Keep guidance available during editing without covering the draft.
- Avoid confetti, rewards, streaks, comparative rankings, and manipulative engagement mechanics.
- Preserve the student's current draft across ordinary UI reruns, step navigation, dialog cancellation, and failed model calls.
- Prevent accidental duplicate submissions and clearly confirm that a revision snapshot has been saved before review begins.

### 10.7 Honest Review Progress and Latency

- Show deterministic stage updates such as **Draft saved**, **Reviewing your draft and selected goals**, and **Preparing feedback**.
- Do not display a stage before the corresponding work has begun or present structured model tokens, hidden reasoning, or fabricated progress as student feedback.
- Advance to **Preparing feedback** only after Coordinator output has been validated and the Support stage is ready to begin.
- Record end-to-end, Coordinator, Support, and schema-repair latency for evaluation and opt-in observability.
- Treat latency reduction as a measurement task; make no fixed response-time promise until representative runs establish a baseline.

## 11. Proposed Technical Architecture

### 11.1 Architecture Decision

V3 initially retains **two model-driven agents** plus deterministic workflow and comparison services. A third comparison agent is not justified by default because it would add cost, latency, and another opportunity for inconsistent judgment.

### 11.2 Agent 1: Assessment Coordinator

Responsibilities:

- Perform human-review assessment before other routing.
- Resolve or clarify essential context and working genre.
- Apply genre-specific assessment criteria.
- Identify source-verification limitations.
- Compare current and previous drafts and evaluate selected focus areas.
- Identify strengths, meaningful issues, regressions, and final-comparison findings.
- Produce structured routing and concise final-output rationale, not hidden chain-of-thought.

The coordinator does not produce open-ended student-facing prose or rewrite student writing.

### 11.3 Agent 2: Instructional Support Agent

Responsibilities:

- Convert coordinator findings into warm, specific, grade-appropriate feedback.
- Produce manageable revision actions and bounded optional scaffolds.
- Use teacher-supplied classroom terminology when available.
- Produce the final motivational reflection from verified draft changes and coordinator findings.
- Operate in distinct **round feedback** and **final reflection** modes without becoming a separate agent.

The Support Agent does not own routing, override source limitations, or introduce unrelated new issues.

### 11.4 Deterministic Services

- Session and composition lifecycle
- Immutable revision snapshots and selected-goal records
- Original/previous/current draft selection
- Text diff generation
- Process milestones
- Clarification interrupt/resume
- Teacher-review templates
- Session restoration and deletion
- Developer observability

### 11.5 Proposed Flow

```text
New composition or submitted revision
        -> Assessment Coordinator
            |- clarification (IN-04, Section 9.1) -> student answer -> Coordinator
            |- teacher_review (Section 9.3, RV-02) -> separate student/evaluator outputs
            |- direct_response (Section 9.2, RV-28) -> student-controlled finish
            `- support (RV-03 through RV-28) -> Instructional Support Agent
                           -> student selects 1–3 goals
                           -> student edits without a model call
                           -> explicit revision submission
                           -> Assessment Coordinator

Student confirms Finish and reflect
        -> deterministic original/final diff
        -> Coordinator comparison findings
        -> Support Agent final reflection
        -> completed session
```

### 11.6 Round and Composition Model

A **composition** is one complete writing session, identified by a stable `composition_id`. It includes the original submission, every revision, selected goals, and feedback across rounds. A **round** is one model-review cycle with a separate `round_id`; each explicit draft submission increments `revision_number`. A **session** is the browser/workspace view that may contain multiple compositions; its identifier filters history but is not authentication.

Core persisted fields include:

- Session and composition identifiers
- Original, previous, and current submitted drafts
- Immutable revision snapshots
- Grade, selected/inferred/final genre, prompt, teacher directions, framework name/components, Coordinator framework coverage, source material, and deterministic `source_material_available`
- Student concerns and optional support-request actions
- Selected focus IDs and corresponding feedback for each round
- Routing, clarification, source-limitation, and review status
- Final comparison and process milestones
- Timestamps, execution details, and error status

The model receives a bounded context: the original, immediately previous, and current drafts as needed, selected goals, concise prior findings, and relevant assignment/source context. Support receives full source text only when a Coordinator issue is source-dependent or a source limitation is present; empty clarification history is omitted on revisions. Final Support generates improvement/regression observations and the conclusion while original strengths and future possibilities pass through validated Coordinator findings. The model does not receive an ever-growing transcript of every UI event or all prior model prose by default.

### 11.7 Model-Call Boundaries

- Focus selection, scaffold reveal, **Show less feedback**, **I’m stuck** presentation of pregenerated guidance, editing, and deterministic diff generation make no model calls.
- Initial and revision reviews normally use one Coordinator call and one Support call.
- Final reflection normally uses one Coordinator comparison call and one Support call.
- Each agent invocation may retain one bounded schema-repair attempt.
- Persistent Support failure must not produce partial or fabricated feedback.
- A failed review must not overwrite the last valid snapshot or current editor text.

### 11.8 Model Configuration and Evaluation

- **MC-01:** Following the representative `v3.1.0` comparison and the 2026-11-10 product decision, the V3 local student runtime uses the configured DeepSeek model with **non-thinking mode** (`DEEPSEEK_THINKING=false`) for Coordinator, Support, bounded-repair, and final-comparison calls. V3 never switches modes automatically.
- **MC-02:** Non-thinking requests use temperature 0. Controlled thinking-comparison requests omit the temperature parameter. Observability must describe the actual configuration and must not call thinking mode “temperature 0.”
- **MC-03:** The V3 default configuration records the model name, actual thinking mode, configured reasoning effort when applicable, prompt version, schema version, and fixture version with each real evaluation run.
- **MC-04:** The design hypothesis was that thinking might improve genre-sensitive assessment, source-grounded observations, selected-goal comparison, and student-facing feedback, **or add latency and token-use costs without corresponding quality gains**. The representative `v3.1.0` pair favored non-thinking on operational cost, repair count, RACES alignment, and whole-draft coverage, while thinking showed isolated diagnostic strengths. Two later matched pairs confirmed lower non-thinking latency/token use and showed repair/content variability in both modes. The non-thinking runtime decision remains limited synthetic evidence, not a general model-quality claim; educator review remains open.
- **MC-05:** Thinking mode must not be used to justify longer waits without measurement. Record reasoning/final-response token usage when exposed by the API, schema-repair rates, failures, and model/graph/service/UI latency alongside feedback quality.
- **MC-06:** Raw hidden model reasoning is not student-facing feedback and is never an authorized debug field, including under the label of chain-of-thought or thinking process. Revision state and observability may contain only the final structured response, concise coordinator rationale, and authorized metadata: `model_name`, `thinking_enabled`, `reasoning_effort`, `prompt_version`, `schema_version`, `fixture_version`, provider request/response IDs, timestamps, latency, and token counts. Separately authorized server-side debug capture may retain the final raw response, never raw hidden reasoning.
- **MC-07:** V1/V2 evidence retains its frozen non-thinking, temperature-0 configuration. Thinking mode may be used as an explicit controlled V3 comparator, but neither mode is a student-facing runtime selector or an automatic fallback.

## 12. Privacy, Safety, and Data Requirements

### 12.1 Synthetic Data Only

All development, demonstration, and official V3 test fixtures use synthetic writing and synthetic or appropriately licensed source material. No real student essays or confidential classroom records are used.

### 12.2 Data Sent to the External Model

Depending on the round, prompts may contain:

- Original, previous, and current draft text
- Grade and genre context
- Assignment prompt and teacher directions
- Source material
- Student concerns and optional support-request actions
- Clarification history
- Selected revision goals and concise prior findings
- Deterministic text differences and coordinator handoff fields

Removing names does not necessarily de-identify prose. The UI must continue to warn users not to submit real names, schools, or personal information.

### 12.3 Storage and Deletion

- SQLite may store compositions, revision snapshots, model outputs, checkpoints, and execution details locally and on Streamlit Cloud.
- Random session identifiers filter history but are not authentication or secure isolation.
- Community Cloud does not guarantee local-file persistence; stored sessions may be erased without warning. The implementation must not assume that a particular sleep duration either preserves or erases the database.
- Missing, reset, or corrupted backend state must produce a student-safe recovery view rather than an unhandled exception. The view explains that saved history is unavailable, preserves any current editor text still available in the active runtime, and offers a way to copy that text or start a new composition without claiming that history was restored.
- Streamlit Session State is not a durable backup. Automatic browser-based session hydration is not part of V3; any future browser storage proposal requires separate shared-device, tampering, lifetime, and deletion review.
- Reliable cross-restart persistence beyond the synthetic prototype requires a separate durable server-side storage decision.
- **Delete my data** must delete every composition, revision snapshot, final comparison, checkpoint, and associated execution record in the current session.
- New databases, logs, screenshots, and evidence artifacts must not be committed.

### 12.4 Production Boundary

Real student use requires a separate approved plan for consent, privacy, security, retention, authentication, institutional review, and age-appropriate human escalation. V3 makes no COPPA, FERPA, SOPIPA, or production-compliance claim.

## 13. Error Handling and Operational Requirements

- Reject empty draft submissions locally while allowing safety review for every nonempty writing submission.
- Preserve available drafts and selected goals after timeout, connection, HTTP 429, authentication, malformed-response, and storage errors.
- If a revision snapshot cannot be persisted, stop before model review, preserve the current editor text where the runtime permits, and offer retry or copy actions rather than risking an untracked review.
- Use student-safe error messages; technical details remain in opt-in debug views.
- Do not silently retry in a way that duplicates revision snapshots or charges repeated model calls without user awareness.
- Prevent double-click duplicate submissions.
- Length limits for drafts and source material must be explicit and tested against model context limits; truncation must never be silent.
- Raw prompt/response capture remains separately opt-in and requires server-side debug mode.
- Measure actual end-to-end and per-stage review latency and model-token use before setting performance promises.

## 14. Validation and Evidence Strategy

### 14.1 Automated Tests

Mocked model tests and temporary databases must cover:

- All three genres and genre correction
- Ambiguous genre clarification
- Source-present and source-missing evidence behavior
- Deterministic `source_material_available` and required `source_location` only for source-dependent findings
- Genre inference from dominant purpose without keyword-only, first-person, chronology, or ambiguous-verb shortcuts
- No affect field or dedicated check-in; **Show less feedback** and **I’m stuck** reduce visible choices through pregenerated presentation without another model call, automatic human review, or emotion inference
- Qualitative meaningful-change judgments covering critical one-word edits and large unrelated additions without word-count thresholds
- Two unclear clarification answers followed by `clarification_limit`, with a clear second answer resuming normally
- Repeated identical submissions and large external insertions without punitive escalation or authorship detection
- Teacher-supplied CER/RACES/MEAL terminology
- Practice-scenario loading, progressive disclosure, and overwrite protection
- Selection limits of one minimum and three maximum
- One-candidate and no-actionable-issue drafts
- Immutable original and successive revision snapshots persisted before model calls
- Selected-goal observations across multiple rounds
- Optional attempted/deferred goal self-report and neutral carry-forward language
- Unchanged-draft detection and neutral small-change confirmation without quality inference
- Meaningful regression handling
- Student stop after any completed review
- Original-to-final comparison with no fabricated changes
- No numerical scores or readiness claims
- No complete target responses, assigned-topic replacement answers, or supposedly unrelated examples that match the assignment in scaffolds
- Hint structure with a valid passage reference and two to four linked thinking steps or guiding questions
- Constrained initial editor and 60/40 desktop workspace with independent pane scrolling
- Clickable available steps, disabled unavailable steps, and essay preservation during navigation
- Goal-highlight selection, deselection, multiple selections, repeated-passage disambiguation, and stale-highlight removal after edits
- Post-review **Choose goals for another round** action, restoration of **Submit revision**, and return to the **Choose** step
- Finish-dialog cancellation without state changes and confirmation before reflection from either the footer or **Reflect** step
- Honest stage ordering, including no **Preparing feedback** status before Coordinator validation
- Clarification resume and clarification limit
- Teacher-review override on initial and later submissions
- Restoration and complete session deletion
- Missing or reset backend state without an unhandled exception or false recovery claim
- Model failure without draft loss or duplicate snapshots
- Thinking-enabled requests across Coordinator, Support, repair, and final-comparison calls, with temperature omitted
- Accurate recording of model and thinking configuration without raw hidden reasoning in revision state or student views
- Explicit failure when thinking mode is unavailable rather than silent non-thinking fallback

Existing V1/V2 frozen fixtures must not be edited to create V3 evidence. V3 receives a separate versioned fixture set used by the student-safe scenario loader.

### 14.2 Required Synthetic Scenarios

1. Argumentative draft with supplied source and accurate evidence.
2. Argumentative draft with an apparent source mismatch and a specific passage reference.
3. Text-dependent draft without source material, demonstrating bounded claims.
4. Informational draft using teacher-specified RACES directions.
5. Narrative draft that receives development feedback without demands for citations or counterclaims.
6. Auto-inferred genre that the student corrects before revision.
7. Student selects three goals, revises all three, and receives three grounded observations.
8. Student selects one goal across multiple rounds and then stops voluntarily.
9. Revision introduces a meaningful organizational regression.
10. Strong draft receives affirmation without manufactured issues.
11. Final reflection distinguishes original strengths from later improvements and offers nonrequired future possibilities.
12. Concerning revision content routes to simulated teacher review without normal critique.
13. A curated practice scenario loads a complete text-dependent task and requires confirmation before replacing an active draft.
14. A substantively meaningful one-word revision and a minimal punctuation-only revision both receive neutral change handling without a “trivial” label or fabricated improvement.
15. A student reports deferring two of three selected goals; feedback acknowledges the attempted goal and offers the others as carry-forward choices without failure framing.
16. A scaffold response containing an assigned-topic replacement answer is rejected during evaluation, while abstract placeholders remain available.
17. Simulated backend storage loss during a composition produces a recovery view without an unhandled exception or a false restoration claim.
18. Selecting multiple goals highlights the correct passages; identical, nested, and transitively overlapping references share a union highlight with goal membership and textual labels. Deselecting removes only that goal's membership, and editing a referenced sentence removes its stale highlight without altering the essay.
19. After revision review, **Choose goals for another round** returns to **Choose**; clickable Draft, Choose, Revise, and Reflect steps preserve the essay and prevent unavailable-state navigation.
20. Cancelling the finish dialog preserves the current feedback and step, while confirming from either the footer or **Reflect** step opens the final comparison.
21. A responsibility-goal hint references the student's actual sentence, offers two to four linked thinking prompts and a self-check, and supplies no completed explanation; a generic “Why does this matter?” response alone fails the specificity review.
22. A coherent three-to-four-sentence grade-5 argument with a clear claim and one underdeveloped reason receives proportional elaboration support without demands for a full five-paragraph structure.
23. A 350-plus-word grade-7 informational essay with source material receives a small set of prioritized issues rather than an error catalogue, and highlights disambiguate references across multiple paragraphs.
24. A grade-6 argument with insightful ideas, relevant evidence, and clear reasoning but non-obscuring article, tense, and preposition errors prioritizes thinking and organization over conventions; language support remains optional.
25. A four-paragraph essay with a strong introduction and conclusion but weak middle-paragraph explanation and cohesion receives references and highlights for the correct middle paragraphs without forced changes to strong sections.
26. A grade-5 personal narrative using clear informal voice such as “kinda scary” receives narrative-development feedback without unnecessary formalization or correction of appropriate voice.
27. A grade-7 informational essay that shifts between casual and overly formal register receives an optional consistency focus that explains the purpose of register without declaring either phrasing inherently wrong.
28. Repeated identical resubmissions produce neutral editing/finish choices and never automatic teacher review based on repetition count.
29. A student selects **Show less feedback** or **I’m stuck** and receives fewer visible choices and one concrete next step without another model call, teacher escalation, or an inference about emotion or effort.
30. Two unclear clarification answers produce the explicit `clarification_limit` route with the clarification history, while a clear second answer resumes normal assessment.
31. The controlled density fixtures #31/#32 form a same-grade, same-genre, same-assignment informational pair at approximately 60 and 400 words with comparable writing quality and intentional issue categories and no prescribed candidate count. Repeated outputs and blinded educator review assess candidate count, total feedback length, relevance, prioritization, and manageability without claiming length-only causation.

Final-comparison evidence also covers #7, #9, and #15 in addition to #1, #8, #11, and #20, including multi-goal partial progress, organizational regression, and deferred goals grounded in actual text changes.

### 14.3 Evidence Gates

Before claiming technical completion:

- All V3 must-have acceptance scenarios pass.
- Original and revision snapshots survive reload and restoration when the backing store remains available.
- Simulated backing-store loss follows the specified recovery path.
- Source limitations and no-score rules are observable in real model runs.
- Honest stage transitions and end-to-end/per-stage latency are recorded for representative runs.
- The full loop works end to end in the browser, including scenario loading, independent pane scrolling, goal highlights, clickable steps, the next-round action, and finish-dialog cancellation/confirmation, not only in unit tests.

Before claiming pedagogical quality or classroom alignment:

- Qualified educators review representative synthetic interactions by grade and genre.
- Feedback inaccuracies, over-scaffolding, generic or insufficiently guided hints, unsupported improvement claims, and discouraging carry-forward language are recorded and addressed.
- Findings are reported as a limited synthetic evaluation, not evidence of learner outcomes.

Before claiming learner improvement, motivation, engagement, or retention:

- A separate appropriately approved study with real users and suitable measures is required.

Before any future supervised student contact, separate from synthetic-prototype technical completion:

- At least three qualified educators with grades 5–7 teaching experience each complete two or three representative scenarios. They assess whether a typical student could navigate independently, likely confusion points, feedback tone and density, hint guidance without answers, and interaction issues.
- At least two of the three reviewers must assess the prototype as **Ready for supervised student pilot**, with identified issues addressed or documented. This is necessary but not sufficient by itself; the separate privacy, safety, consent, and institutional approvals in Section 12.4 remain mandatory.
- Findings are reported as limited educator walk-throughs with synthetic material, not direct student usability evidence or automatic authorization for a pilot.

### 14.4 Thinking-Mode Evaluation

Thinking-mode evaluation uses controlled comparison to determine whether the configuration improves targeted outcomes enough to justify operational costs. It may result in keeping, modifying, or removing the thinking configuration, and positive, null, and negative findings carry equal reporting weight.

- Run the representative synthetic V3 scenario set using the selected non-thinking runtime and record the configuration required by MC-03.
- For a controlled comparison only, run the same fixtures, prompts, schemas, source material, and revision inputs with the V1/V2 non-thinking, temperature-0 baseline. Repeat runs as needed to observe variability; temperature 0 does not guarantee identical output.
- Compare schema-validity and repair rates, request failures, source-grounding accuracy, genre handling, selected-goal observations, hint specificity, scaffold-boundary violations, final-comparison accuracy, educator ratings, latency, and token usage when available.
- Report thinking and non-thinking outcomes separately. Do not claim better generation from intuition, reasoning length, a single preferred response, or mocked tests, and do not rationalize null or negative findings after the fact.
- If thinking mode does not improve the targeted outcomes, report that result and document the quality/latency trade-off without exaggeration. If it fails required behavior or operational gates, address the failure or explicitly revisit the V3 configuration rather than silently switching modes.

## 15. Success Criteria

V3 is a successful **synthetic classroom prototype** when:

1. A student can enter through a curated scenario or progressively disclosed manual inputs and complete the entire select–revise–review–repeat/stop loop without losing draft history while storage is available.
2. Every selected focus receives grounded feedback after revision.
3. The system distinguishes source-grounded observations from unverifiable evidence claims.
4. Feedback follows the selected or confirmed genre and supplied teacher directions.
5. The student can stop without the system manufacturing more work.
6. The final reflection identifies only actual changes and remains encouraging without grading or readiness claims.
7. Optional hints are passage-specific, provide linked thinking steps and useful self-checks, preserve student authorship, and do not supply assigned-topic replacement answers.
8. Small edits and deferred goals receive neutral treatment without unsupported effort judgments.
9. The desktop workspace keeps the draft and feedback visible, goal highlights remain accurate, step and next-round navigation work, and finishing requires confirmation.
10. Review progress is honest, representative latency is measured, and storage loss fails gracefully.
11. Safety, privacy, deletion, and observability requirements pass their tests.
12. Before any future supervised student contact, the educator walk-through gate in Section 14.3 is complete; this does not substitute for direct student usability research or the other pilot approvals.

Product metrics may describe prototype behavior—such as number of revision rounds, selected focus categories, completion of process milestones, errors, and latency—but these measurements must not be relabeled as learning or motivation outcomes.

## 16. Delivery Milestones

### Milestone 1: Context and Data Foundation

- Add a constrained initial editor and progressively disclosed assignment, teacher-direction, source, and genre inputs.
- Add curated student-safe scenario loading with overwrite protection.
- Define genre-specific structured assessment schemas.
- Implement composition and immutable revision storage with missing-store recovery.
- **Gate:** input validation, scenario loading, source-boundary, genre, restoration, deletion, and missing-store tests pass.

### Milestone 2: Initial Review and Focus Selection

- Configure the selected non-thinking mode consistently for Coordinator, Support, repair, and final-comparison calls, with temperature 0 and no automatic mode switching; controlled thinking comparisons omit temperature.
- Implement Coordinator assessment and Support feedback for all three genres.
- Add one-to-three selection, goal-linked essay highlights, and pregenerated passage-specific hints with linked thinking steps and useful self-checks.
- **Gate:** request tests confirm the actual configured mode, initial review works for all three genres without replacement prose, and educator review finds the hints sufficiently specific without supplying answers.

### Milestone 3: Iterative Revision Loop

- Add the 60/40 desktop workspace, independent pane scrolling, clickable steps, and the post-review next-round action that returns to **Choose**.
- Add editing, snapshots, neutral small-change confirmation, optional attempted/deferred self-report, selected-goal comparison, regression review, and next-round choices.
- Add honest stage updates and per-stage latency measurement.
- **Gate:** multiple browser rounds preserve the original, highlights and navigation remain accurate, feedback covers every selected goal, and deferred goals receive no unsupported effort judgments.

### Milestone 4: Final Reflection and History

- Add deterministic original/final diff, final Coordinator findings, Support reflection, and read-only history.
- Add finish confirmation from both the footer and **Reflect** step, with cancellation preserving the current state.
- **Gate:** comparison contains no fabricated improvements, grades, or readiness claims, and reflection cannot begin accidentally without confirmation.

### Milestone 5: Safety, Accessibility, and Evaluation

- Complete boundary, storage-failure, error-recovery, accessibility, privacy, and observability checks.
- Run the separate synthetic V3 scenario set and educator review using the selected non-thinking runtime.
- Complete the controlled non-thinking baseline comparison and document positive, null, or negative quality, reliability, latency, and token-use findings without claiming unsupported improvement.
- Before any future supervised student contact, complete the three-educator walk-through gate separately from synthetic-prototype technical completion.
- **Gate:** release claims match the actual evidence; unresolved limitations remain explicit, and student contact does not proceed from educator approval alone.

## 17. Principal Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| Optional context creates onboarding friction | Use progressive disclosure and curated scenarios with overwrite protection |
| Thinking mode increases latency or token use without better output | Measure stage latency, token usage, reliability, and quality against the frozen baseline; report trade-offs honestly |
| Thinking mode is assumed to be better without evidence | Use controlled real-model comparisons and educator review; report null and negative findings as readily as positive outcomes and do not infer quality from reasoning length or intuition |
| Thinking configuration drifts between calls or falls back silently | Require a consistent explicit configuration, omit temperature, record actual settings, and fail visibly when unavailable |
| Serial model calls feel unresponsive | Save first, prevent duplicates, show honest stages, and measure per-stage latency |
| AI verifies evidence without a source | Persist source availability, constrain prompts and schemas, and test source-missing behavior |
| Genre inference applies the wrong criteria | Show inference, allow correction, and clarify material ambiguity |
| Support requests become proxies for emotion, routing, or effort | Remove the dedicated check-in, treat button use as a presentation preference, and rely only on the explicit-content human-review boundary |
| Anomalous interactions are treated as misconduct | Use neutral data-quality responses, avoid repetition-based escalation and authorship heuristics, and preserve student dignity |
| Hints are too generic to guide revision | Require passage-specific linked thinking prompts and self-checks with educator review |
| Specific hints become AI-written answers | Prohibit completed target responses and assigned-topic replacement examples; inspect real outputs |
| Highlights become stale or point to the wrong passage | Use exact references with occurrence metadata, recalculate on edits, and remove unreliable highlights |
| Step navigation loses work or finishing is accidental | Preserve state, disable unavailable steps, and require explicit finish confirmation |
| Feedback volume overwhelms students | Limit selection to three and avoid manufactured issues |
| Endless revision creates fatigue | Student-controlled stopping, direct response, and process milestones |
| Minimal edits produce invented praise or wasted review | Use factual change notices and require text-grounded observations without a word-count quality judgment |
| Deferred goals feel like failed attempts | Use neutral text-evidence language and optional student self-report with carry-forward choices |
| New feedback contradicts earlier rounds | Use structured selected-goal findings and bounded comparison context |
| Final reflection invents improvement | Supply deterministic diffs and require text-grounded claims |
| Original draft or editor text is lost | Immutable snapshots, rerun preservation, missing-store recovery, and failure-injection tests |
| Context grows with every round | Store full history but send only bounded relevant context |
| Checklist becomes a hidden grading system | Measure actions rather than detected quality or readiness |
| Scope expands into a full classroom platform | Keep real accounts, prewriting, uploads, and dashboards out of V3 |
| Higher-level scaffolds feel condescending | Use optional analytical supports and educator review |

## 18. Deferred Product Decisions

The following require separate evidence or user research and are not prerequisites for V3:

- Whether prewriting should become a separate workflow
- Whether additional classroom-framework presets are warranted after structured inputs and free-text compatibility detection are evaluated
- Whether numerical scores can ever be validated sufficiently for limited teacher-facing use
- Whether broader proficiency support is desirable and feasible
- Whether a supervised real-classroom pilot should follow the synthetic prototype
- Whether split-pane, tabbed, collapsible, or full-width alternating layouts better support focused revision across representative draft lengths
- Whether phone and tablet layouts should be added after desktop validation, given device access in the intended classroom context
- Whether consolidating the two-agent pipeline or adding agents would improve quality enough to justify changed cost and complexity
- Whether any future browser-based recovery mechanism is safe and useful enough to justify its privacy and lifecycle trade-offs

## 19. References

- [Existing V1/V2 PRD and evidence record](PRD.md)
- [Rubric direction feedback](RUBRIC_DIRECTION_FEEDBACK.md)
- [Interactive V3 desktop HTML mockup](mockups/v3_iterative_revision.html)
- [Claude V3 improvement analysis](V3_PRD_IMPROVEMENT_ANALYSIS.md)
- [Official ELPAC writing rubrics](https://www.caaspp-elpac.org/s/docs/tech-report/ELPAC_Writing-Rubrics.pdf)
- [Smarter Balanced assessment design documentation](https://technicalreports.smarterbalanced.org/2024-25_interim-report/_book/test-design.html)
- [California reclassification guidance, February 2026](https://www.caaspp-elpac.org/training-and-communication/communication/email/02-02-26-elpac)
