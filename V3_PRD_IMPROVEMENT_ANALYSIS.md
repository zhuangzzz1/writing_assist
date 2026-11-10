# V3 PRD Improvement Analysis
**Document:** PRD_V3_ITERATIVE_REVISION.md  
**Review Date:** 2026-11-10  
**Reviewer Perspective:** Writing Coach + Learning Scientist

## Executive Summary

The V3 PRD is **remarkably thorough and pedagogically sound**. It demonstrates deep understanding of multilingual learner pedagogy, authentic writing instruction, and responsible AI design. The structure is clear, requirements are testable, and boundaries are explicit.

This analysis identifies **12 improvement opportunities** that would move the document from "thorough requirements" to "implementation-ready specification with minimal interpretation gaps." The pedagogical commitments are strong—the gaps are primarily operational clarity for implementers and evaluators.

---

## Key Strengths

1. **Pedagogically grounded**: Genre-specific criteria, student agency, revision-focused rather than error-focused
2. **Honest about limitations**: No false claims about readiness, mastery, or emotion detection  
3. **Student-centered design**: Student controls stopping, revision volume, and focus selection
4. **Evidence-based**: Requires validation before claims, synthetic scenarios, educator review
5. **Safety-conscious**: Clear boundaries, simulated teacher review, no crisis protocol invention
6. **Comprehensive**: Covers technical architecture, UI requirements, privacy, evaluation strategy

---

## Critical Improvements (Affects Pedagogical Validity)

### 1. Add Diverse Hint Examples

**Current Issue:**  
RV-14 provides one detailed example (citizenship/responsibility) but the general requirement ("specific to the selected goal and referenced passage... two to four linked thinking steps") may be interpreted inconsistently across genres and goal types.

**Location:** Section 8.3, RV-14

**Recommendation:**  
Add **Section 8.3.2: Hint Structure Examples** with 4-6 diverse worked examples:

**Example Set:**
1. **Argumentative - Evidence Explanation** (current citizenship example)
2. **Argumentative - Counterclaim Response**
   - Student sentence: "Some people disagree."
   - Acceptable hint: "Look at your main claim about school gardens in paragraph 1. What specific worry might someone have about cost, time, or safety? How would you show that worry is less important than your reasons? Draft a sentence that names the concern and responds to it, then check whether your response connects to evidence you already mentioned."
   - Unacceptable: "Why might someone disagree?" (too generic)

3. **Informational - Elaboration**
   - Student sentence: "Bees help plants grow."
   - Acceptable hint: "You mentioned that bees help plants grow. Look at your source paragraph about pollination. What exactly do bees carry from flower to flower, and what happens to the plant after that? Add 1-2 sentences explaining the process step by step, then reread to check if a classmate would understand how one action leads to the next."
   - Unacceptable: "Add more details about bees." (not specific)

4. **Narrative - Character Development**
   - Student passage: "Maria was nervous. She went inside."
   - Acceptable hint: "Find the moment when Maria goes inside. What did she notice, think, or feel that showed she was nervous? Did her hands shake, did she pause at the door, did she remember something? Pick one specific detail that would help your reader picture that nervousness, write it in the sentence before 'She went inside,' then check whether the detail matches what happens next."
   - Unacceptable: "Describe Maria's feelings more." (vague action)

5. **Organization/Transitions - Cohesion**
   - Two disconnected paragraphs about different reasons
   - Acceptable hint: "Look at where paragraph 2 starts. Your first paragraph discussed responsibility, and now you're discussing academic achievement. What word or phrase could show your reader this is your second reason supporting the same claim? Try starting with 'Another benefit is...' or 'In addition to building responsibility...' and see which connects the ideas more clearly, then check whether the link makes sense."
   - Unacceptable: "Add a transition." (no guidance)

6. **Academic Language - Precision**
   - Student sentence: "This thing helps students."
   - Acceptable hint: "You wrote 'this thing' — look back at the previous sentence. Are you referring to the garden, the watering schedule, the teamwork, or something else? Replace 'this thing' with the specific noun, then check whether 'helps' is precise enough. Could you say 'teaches,' 'requires,' 'improves,' or 'encourages'? Choose the verb that matches what you mean."
   - Unacceptable: "Use better words." (no direction)

**Pattern Requirements:**
- **Passage reference**: Points to specific student text
- **Thinking sequence**: 2-4 linked prompts that scaffold the cognitive work
- **Action direction**: What to write, where, and how to approach it
- **Self-check**: How to evaluate whether the revision addresses the goal
- **No completed answers**: Student must supply the target idea/language

**Learning Science Rationale:**  
Worked examples reduce cognitive load for implementers and increase inter-rater reliability during validation. Multiple examples across genres prevent single-case overfitting.

---

### 2. Operationalize "Meaningful"

**Current Issue:**  
The word "meaningful" appears 29 times (meaningful issues, meaningful changes, meaningful regression, meaningful new issues, meaningful future areas) without operational criteria. Coordinators may apply inconsistent thresholds.

**Locations:** Throughout (RV-04, RV-08, RV-26, RV-28, Section 8.6, others)

**Recommendation:**  
Add **Section 7.6: Operational Definition of "Meaningful"**

**Definition Framework:**

**Meaningful Issue (worthy of revision focus):**
- Affects 2+ paragraphs, multiple sentences, or the central claim/idea
- Obscures reader understanding or creates confusion about purpose
- Misaligns with genre-specific expectations (e.g., narrative demanding sources)
- Represents a pattern (3+ similar occurrences) rather than isolated instance

**Grade-Level Examples:**

| Issue | Meaningful for 5-7? | Rationale |
|-------|---------------------|-----------|
| Missing thesis statement | Yes | Central to argumentative/informational genres |
| One reason lacks evidence | Yes | Core requirement; 2+ sentences affected |
| Three body paragraphs lack transitions | Yes | Pattern affecting organization |
| Conclusion only restates claim | Depends | Not meaningful if grade-appropriate summary; meaningful if assignment requires synthesis |
| One comma splice in dialogue | No | Single convention error; doesn't obscure meaning |
| Informal "gonna" in appropriate narrative voice | No | Voice preservation takes priority |
| Using "good" instead of "beneficial" once | No | Synonym choice; meaning clear |
| Every paragraph begins "First," "Second," "Third" | Yes | Mechanical pattern; reduces cohesion |

**Meaningful Change (after revision):**
- Adds, revises, or removes 8+ words addressing a selected goal
- Alters the claim, central idea, sequence, or organizational structure
- Adds evidence, explanation, or elaboration where previously absent
- Resolves identified confusion or genre misalignment

**Not Meaningful (but still valid student work):**
- Punctuation-only edits when focus was evidence explanation  
- Synonym substitution without clarity improvement
- Reordering two sentences in the same paragraph without structural change
- Adding transition words without addressing organizational gaps

**Meaningful Regression:**
- Introduces contradiction with earlier statements
- Removes supporting evidence without replacement
- Creates new genre misalignment (e.g., removes claim from argumentative essay)
- Obscures previously clear meaning

**Uncertain Boundary Cases:**
- **Small change to critical element**: Revising 5 words in the thesis statement → Treat as meaningful
- **Large change to non-selected goal**: Adding 50 words of description when goal was evidence explanation → Acknowledge work but note selected goal not yet evident
- **Partial completion**: Added evidence but no explanation → Note progress and identify remaining step

**Implementation Rule:**  
When uncertain whether an issue or change is meaningful, **default toward recognition**. It is better to acknowledge student work than to dismiss genuine effort as insufficient.

**Learning Science Rationale:**  
"Meaningful" is where over-correction happens. Clear thresholds protect student voice and prevent the system from manufacturing work or dismissing legitimate revision attempts.

---

### 3. Add Source-Grounded Feedback Examples

**Current Issue:**  
IN-15 describes what the system "may" do with source material but doesn't show what responsible source-grounded feedback looks like vs. overconfident verification.

**Location:** Section 6.4

**Recommendation:**  
Add **Section 6.4.1: Source-Grounded Feedback Examples**

**When Source Material Is Provided:**

✅ **Acceptable - Observation with specific reference:**
- "Your quotation 'students learn responsibility' appears in paragraph 2 of the source, in the sentence about daily watering routines. The source explains this happens through consistent practice. Your essay could connect the quotation more directly to that routine."
- "I found 'reduces stress' in the source's conclusion (last paragraph). The source attributes this to outdoor exposure. Your paragraph doesn't mention the outdoor element—consider whether that's part of your argument."
- "Your essay says the study included 500 students. I see '50 students' in the source (paragraph 3). Double-check that number."

✅ **Acceptable - Acknowledging absence:**
- "I don't see 'improved test scores' in the source you provided. If this fact came from a different source or class discussion, consider noting that. If you meant something else from this source, let me know which paragraph."

✅ **Acceptable - Bounded interpretation check:**
- "You wrote that gardens 'waste water.' The source (paragraph 4) discusses water usage but calls it 'efficient drip irrigation.' These seem to point in different directions—reread that paragraph and see whether your interpretation matches."

❌ **Unacceptable - False verification:**
- "This quotation is accurate." (claims verification without qualification)
- "Your evidence correctly represents the source." (confident judgment)
- "This is properly cited." (citation format ≠ content accuracy)

❌ **Unacceptable - Invented source knowledge:**
- "The source says X" when source wasn't provided
- "According to the author's other work..." (scope violation)
- "This misrepresents the study's methods" when methods aren't in the provided passage

❌ **Unacceptable - Over-interpretation:**
- "This misrepresents the author's intent" (intent claim)
- "The author would disagree with your conclusion" (speculation)
- "This evidence is weak because the study was biased" (outside editorial judgment)

**When Source Material Is Missing:**

✅ **Acceptable - Bounded observation:**
- "Your essay includes a quotation and statistics. I can't verify these without the source passage. If you add it, I can help check whether your evidence matches."
- "You explained how the evidence supports your claim. That reasoning is clear. I can't confirm whether the evidence itself is accurate to the source without seeing it."

❌ **Unacceptable - False confidence:**
- "Your quotation looks correct." (no basis)
- "This statistic seems reasonable." (guess)

**Prompt/Schema Requirements:**
- Coordinator schema must include `source_material_available: boolean`
- When `false`, evidence-accuracy findings are prohibited
- When `true`, findings must include `source_location` (paragraph/sentence reference)
- Support Agent must preserve Coordinator's source limitations without weakening them

**Learning Science Rationale:**  
Source-based writing is central to grades 5-7 ELA. Concrete examples prevent both under-use (avoiding useful observations) and over-claiming (false verification). Bounded observations teach students to check their own evidence use.

---

### 4. Define Genre Inference Decision Rules

**Current Issue:**  
IN-02 allows inference, IN-04 requires clarification "when ambiguity would materially change feedback," but no criteria specify what constitutes material ambiguity.

**Location:** Section 6.2

**Recommendation:**  
Add **Section 6.2.1: Genre Inference Decision Tree**

**Clarification Required (ambiguity materially affects feedback):**
- Draft contains **both** narrative elements (first-person experience, chronological events) **and** an arguable claim with reasons
- Assignment prompt uses ambiguous verbs: "write about," "discuss," "explore," "reflect on"
- Teacher directions specify one genre but draft structure strongly suggests another (e.g., directions say "argument" but draft is chronological first-person experience with no claim)
- Draft is an outline or very early stage where structure is indeterminate

**Clarification Question Format:**
- "Your writing includes [narrative elements / a claim and reasons / informational explanations]. Are you writing a [genre A] or [genre B]? This helps me give you the right feedback."
- Offer 2-3 radio button options, not open-ended

**Default Inference Rules (when clarification not triggered):**

| Draft Feature | Inferred Genre | Confidence |
|---------------|----------------|------------|
| Clear position/claim + reasons/evidence | Argumentative | High |
| Neutral central idea + facts/details organized by subtopic | Informational | High |
| Chronological first-person experience with sensory/emotional detail | Narrative | High |
| Chronological sequence of factual events (how-to, historical account) | Informational | Medium |
| Third-person story with characters and plot | Narrative | High |
| "I think X because..." + reasons | Argumentative | High |
| "This essay will explain..." + informational content | Informational | Medium |

**Boundary Cases:**
- **Personal narrative supporting a claim** (e.g., "My experience with my grandmother's garden taught me that school gardens improve learning"): Default to **argumentative** if claim is prominent; clarify if the experience dominates and claim is only in intro/conclusion
- **Informational writing with "I"** (e.g., "I will explain three types of renewable energy"): Default to **informational**; first person is acceptable for this genre
- **Very short drafts** (1-2 paragraphs): Rely more heavily on assignment prompt; clarify if prompt is also ambiguous

**Implementation:**
- Show inferred genre prominently: "I read this as [argumentative] writing. [Change genre]"
- Genre correction requires no clarification answer; it immediately triggers reassessment with the corrected genre
- Record inference confidence in observability (high/medium/low)

**Learning Science Rationale:**  
Transparent decision rules make system behavior predictable and debuggable. Clear thresholds reduce student confusion and wasted clarification rounds.

---

## High Priority Improvements (Affects Implementation Consistency)

### 5. Specify Affect Check-In Implementation

**Current Issue:**  
Section 4.1 and IN-07 mention optional affect self-reports (ready/unsure/frustrated) but don't specify when/how often students see this prompt, what tone adjustments correspond to each value, or how "frustrated" escalates to Boundary B.

**Locations:** Section 4.1, Section 6.1 table

**Recommendation:**  
Add **Section 6.1.1: Affect Check-In Implementation**

**Placement and Frequency:**
- Optional radio buttons appear **below the grade and draft input** on initial submission
- Label: "How are you feeling about this writing?" (optional)
- Options: Empty/skipped (default), "Ready to improve it", "A little unsure", "Pretty frustrated"
- **Not repeated** on revision rounds unless student stops making progress for 2+ rounds
- Re-prompt text after 2 stalled rounds: "Still working on this? How's it going?" with same options

**Tone and Support Adjustments:**

| Self-Report | Support Agent Tone Adjustment | Feedback Adjustment |
|-------------|-------------------------------|---------------------|
| Empty/Ready | Standard warm, supportive tone | 2-3 revision candidates as warranted |
| Unsure | Add brief meta-comment: "Let's focus on one clear step you can take." | Prioritize 1-2 candidates; ensure hints are especially clear |
| Frustrated | Acknowledge difficulty: "I can see you've been working hard on this." Reduce length. | Offer 1 candidate with the most concrete guidance; consider suggesting a break or teacher check-in |

**Escalation to Simulated Teacher Review:**
- **Trigger**: "Frustrated" self-report across **2+ consecutive rounds** AND one of:
  - Submitted revisions show minimal/no change to selected goals
  - Clarification answers become shorter or less coherent
  - Draft length decreases significantly without completion
- **Action**: Route to teacher review with context: "This student has been working for [N] rounds and reported feeling frustrated. Consider checking in about the assignment expectations or offering additional support."
- **Student message**: "It looks like this assignment might need some extra support. Try talking with your teacher about what's feeling hard."

**Important Constraints:**
- Affect is **self-reported only**; never infer emotion from writing quality, errors, or draft length
- "Frustrated" is not a behavior problem; it's a signal to reduce load or seek human support
- Do not use affect to influence routing (clarification, direct response, teacher review) unless the escalation threshold is met
- Do not record affect as a performance metric or use it to judge student engagement

**Learning Science Rationale:**  
Self-reported affect is valuable for adaptive support but only if responses are consistent, helpful, and non-punitive. Vague implementation risks performative check-ins that don't actually adapt instruction.

---

### 6. State Clarification Limit Explicitly

**Current Issue:**  
Section 9.1 mentions "bounded clarification limit" but doesn't specify the number. V1/V2 used 2.

**Location:** Section 9.1

**Recommendation:**  
Replace "A bounded clarification limit remains necessary" with:

> **Clarification limit**: After **two clarification exchanges** produce answers that remain too ambiguous for responsible feedback, the system stops normal feedback and routes to simulated teacher review with the clarification history.
>
> **Rationale**: Two attempts balance patience with efficiency. Persistent ambiguity after two exchanges suggests the task itself needs teacher clarification, not additional AI attempts. This prevents endless loops while giving students a reasonable opportunity to provide needed context.

**Add to RV-02 area or Section 11.5:**
- First unclear submission → Clarification question 1
- Still unclear after answer 1 → Clarification question 2
- Still unclear after answer 2 → Teacher review route
- Each clarification must ask **one specific question**, not multiple questions

**Learning Science Rationale:**  
Explicit limits prevent frustration loops. Two rounds is pedagogically defensible and consistent with V1/V2 evidence.

---

### 7. Add Scaffold Boundary Edge Case Examples

**Current Issue:**  
RV-15 prohibits "completed target response" but edge cases remain ambiguous: sentence frames with blanks, strong/weak examples from different essays, vocabulary lists with example sentences.

**Location:** Section 8.3, RV-15

**Recommendation:**  
Add **Section 8.3.3: Scaffold Boundary Edge Cases**

**Permitted Scaffolds:**

✅ **Abstract placeholder** (unrelated topic):
- "Think of another reason someone might disagree with [your claim]. How would you respond to show your position is stronger?"
- "In an essay about **recycling programs**, a student might write: 'This benefits the community by reducing landfill waste and lowering collection costs.' Try a similar explanation structure for your school garden argument."

✅ **Process demonstration** (different content):
- "Here's how to connect evidence to a claim: [Evidence about **recess**] → [Because explanation] → [Therefore claim]. Now try that pattern with your **homework** evidence."

✅ **Vocabulary expansion**:
- "Academic alternatives to 'get': obtain, acquire, secure, gain"
- "Instead of 'a lot', try: numerous, substantial, considerable, significant"
- "Transition words for adding reasons: Furthermore, Additionally, Moreover, In addition"

✅ **Sentence-combining technique** (generic example):
- "Two short sentences: 'The study was conducted. It involved 50 schools.' Combined: 'The study, which involved 50 schools, was conducted over two years.' Now try combining your two sentences about the survey."

✅ **Self-questioning frame**:
- "Ask yourself: What exactly does this evidence show? How does that connect to my claim? Why does that connection matter to my reader?"

**Prohibited Scaffolds:**

❌ **Assigned-topic reason** (their essay content):
- "A good reason against school gardens is they cost too much money to maintain." (This is a counterclaim **for their essay**; they must generate it)

❌ **Completed explanation** (their evidence):
- "Your evidence about watering plants supports the claim because it shows responsibility leads to better citizenship." (This is **their** explanation task)

❌ **Sentence frame for their specific content**:
- "Gardens teach students _____ which helps them _____." (Fill-in-the-blank for their actual argument is a completion task)
- "This evidence shows _____ because _____." (Too close to doing the thinking)

❌ **Example using their assignment topic**:
- Essay about school gardens → Example about community gardens (appears unrelated but is substantively the same)
- Essay about homework benefits → Example about homework policies (not actually different)

❌ **Replacement prose**:
- "You could write: 'Through daily watering and weeding, students practice responsibility that extends beyond the garden.'" (This is their target sentence)

**Boundary Case: Sentence Starters**

✅ **Acceptable** (structural scaffold):
- "Try starting your explanation with: 'This evidence is important because...'"
- "Connect your reason to your claim: 'This shows that [claim] by...'"

❌ **Unacceptable** (content completion):
- "Complete this sentence: 'School gardens improve learning because they teach _____'"
- "Fill in: 'Watering plants helps students become better citizens by _____'"

**Test for Prohibition Violation:**
1. Could a student copy/paste this scaffold text into their essay and have it read as a coherent, on-topic response to the assignment?
2. Does this scaffold name a specific reason, piece of evidence, explanation, or elaboration that **their essay** needs?

If **yes** to either: it's prohibited.

**Learning Science Rationale:**  
Scaffolding vs. doing the thinking is the central tension in writing instruction. Edge case examples prevent drift toward AI completion of student cognitive work.

---

### 8. Add Anomalous Interaction Handling

**Current Issue:**  
No requirements address students submitting identical revisions repeatedly, copying model examples verbatim, making unrelated edits, or providing nonsense clarification answers.

**Location:** New section needed

**Recommendation:**  
Add **Section 9.4: Anomalous Interaction Patterns**

**Identical Resubmissions:**
- **Detection**: Submitted revision text is byte-identical to the immediately previous submission (excluding whitespace normalization)
- **Response**: "You submitted the same draft again. Would you like to keep working on it, or are you ready to finish and reflect?"
- **No inference**: Do not assume accidental click, giving up, or technical error
- **Limit**: After 3 identical submissions in one composition, route to teacher review

**Minimal/No Response to Selected Goals:**
- **Detection**: Student selected 2-3 goals, submitted revision, but text diff shows <5 words changed and none near the referenced passages
- **Response**: Already covered by RV-21 (neutral small-change confirmation)
- **No inference**: Do not label as "didn't try" or "ignored feedback"
- **Feedback**: Selected-goal observations describe text evidence only ("Improvement not yet evident in this revision")

**Nonsense or Unresponsive Clarification Answers:**
- **Detection**: Clarification answer is keyboard mashing ("asdfgh"), completely off-topic, or repeats the question
- **First occurrence**: Rephrase the clarification question more simply
- **Second occurrence**: Route to teacher review with history: "Student provided unclear responses to clarification questions. Assignment expectations may need teacher discussion."

**Apparent Model-Text Copying:**
- **No detection attempted**: The system does not try to identify whether a student copied from hints, practice examples, or external sources
- **Rationale**: Detection is unreliable and potentially discouraging; if scaffolds are properly bounded (no assigned-topic replacement answers), copying them won't complete the student's task anyway

**Copy-Paste of Large External Text:**
- **Detection**: Revision increases by 200+ words and new text is stylistically inconsistent (detectable via sudden register shift, but heuristic only)
- **Response**: None in V3; focus on ensuring feedback addresses the whole draft appropriately
- **Future consideration**: If this becomes a pattern, consider revision-size change notification, but do not accuse students of cheating

**Repeated Unrelated Edits:**
- **Scenario**: Student selected "Add evidence explanation" but only revised the conclusion's transition words
- **Response**: Selected-goal observation notes "Improvement not yet evident in this revision." Feedback may acknowledge the transition improvement as work done, separate from selected goals
- **No punishment**: Student may realize the mismatch on their own or via carry-forward choices

**Gaming Through Affect Reports:**
- **Scenario**: Student reports "frustrated" immediately to reduce feedback
- **Response**: No detection or prevention; if student wants less feedback, respect that preference
- **Rationale**: Self-advocacy is a valid skill; tone adjustment is not a reward to be gamed

**General Principle:**
Treat anomalous patterns as **data quality issues requiring clarification or teacher support**, not behavior problems requiring punishment. The system responds matter-of-factly and preserves student dignity.

**Learning Science Rationale:**  
Students will test boundaries. Systems that respond punitively or make accusatory inferences damage trust. Matter-of-fact responses and clear escalation paths preserve the learning relationship.

---

## Medium Priority Improvements (Improves Evaluation Rigor)

### 9. Add Edge-Case Evaluation Scenarios

**Current Issue:**  
Section 14.2 has 21 scenarios but misses critical edge cases that reveal whether the system truly prioritizes ideas over mechanics and handles draft-length variability.

**Location:** Section 14.2

**Recommendation:**  
Add scenarios 22-27 to the required synthetic scenario set:

**22. Very Short Coherent Draft**
- **Setup**: 3-4 sentence argumentative draft with clear claim and one reason, but underdeveloped
- **Grade**: 5
- **Expected behavior**: System identifies development need without calling the draft wrong; offers elaboration focus; does not demand structure that's inappropriate for length
- **Tests**: Proportional feedback, development vs. error prioritization

**23. Long Multi-Paragraph Draft (350+ words)**
- **Setup**: 5-paragraph informational essay about renewable energy with source material
- **Grade**: 7  
- **Expected behavior**: Feedback prioritizes 1-2 meaningful issues rather than cataloging everything; highlights accurately identify passages across multiple paragraphs
- **Tests**: Feedback prioritization, highlight accuracy with repeated content, whole-draft coherence

**24. Strong Ideas + Surface Errors (Multilingual Learner Focus)**
- **Setup**: Argumentative draft with insightful claim, relevant evidence, clear reasoning, but ESL-marked syntax (article errors, verb tense shifts, preposition choices) that doesn't obscure meaning
- **Example sentence**: "The student who participate in garden learn about responsibility because they must remember water the plants every day."
- **Grade**: 6
- **Expected behavior**: System prioritizes evidence explanation or organization over grammar; optional language support is offered, not foregrounded; feedback recognizes strong thinking
- **Tests**: **Core V3 value**: Treats multilingual writers as thinkers first

**25. Middle-Paragraph Revision Need**
- **Setup**: 4-paragraph essay where introduction and conclusion are strong, but paragraph 2 lacks evidence explanation and paragraph 3 has weak transitions
- **Expected behavior**: Revision candidates reference paragraphs 2 and 3 specifically; highlights point to the correct middle paragraphs; feedback doesn't force changes to strong introduction
- **Tests**: Passage-specific references, accurate highlighting, avoids manufactured issues

**26. Appropriate Informal Voice (Narrative)**
- **Setup**: Personal narrative about a family tradition, using informal but clear language ("We'd always go to Grandma's," "It was super fun," "kinda scary")
- **Grade**: 5
- **Expected behavior**: System does not flag informal language as errors requiring revision; feedback focuses on narrative development (events, details, pacing); respects student voice
- **Tests**: Genre-appropriate voice preservation, avoids over-formalization

**27. Mixed-Register Draft Needing Consistency**
- **Setup**: Informational essay that shifts between "I think it's cool that..." and "Research demonstrates the significance of..."
- **Grade**: 7
- **Expected behavior**: System identifies register inconsistency as an optional focus without declaring either register wrong; explains why consistency matters for academic informational writing
- **Tests**: Context-sensitive language feedback, explains "why" not just "fix this"

**Learning Science Rationale:**  
These edge cases directly test the multilingual learner focus (Scenario 24), proportional feedback (22, 23), voice preservation (25, 26), and genre-specific expectations (26, 27). Scenario 24 is particularly critical—it's where deficit-focused systems fail.

---

### 10. Neutralize Thinking-Mode Hypothesis Framing

**Current Issue:**  
MC-04 frames thinking mode as potentially improving outcomes but Section 14.4 acknowledges it may not. The optimistic framing could bias evaluation toward confirming the hypothesis.

**Location:** Section 11.8 (MC-04), Section 14.4

**Recommendation:**  
**Replace MC-04** with:

> **MC-04:** The design hypothesis is that thinking mode may improve genre-sensitive assessment, source-grounded observations, selected-goal comparison, and student-facing feedback quality, **or it may introduce latency and token-use costs without corresponding quality gains**. Quality, reliability, schema-repair rates, token usage, and end-to-end/per-stage latency will be measured against the frozen V1/V2 non-thinking baseline. The configuration will be **retained, revised, or removed based on this evidence**.

**Add to Section 17 (Risks table):**

| Risk | Mitigation |
|------|------------|
| Thinking mode assumed valuable without evidence | Measure quality (educator ratings, accuracy), reliability (schema success, failures), and efficiency (latency, tokens) against non-thinking baseline; report null or negative results as readily as positive outcomes; do not rationalize post-hoc or inflate subjective preferences into quality evidence |

**Revise Section 14.4 opening:**

> Thinking-mode evaluation uses **controlled comparison** to determine whether the configuration improves the targeted outcomes enough to justify operational costs. This evaluation may result in **keeping, modifying, or removing** the thinking-mode configuration.

**Learning Science Rationale:**  
Confirmation bias is a real risk in educational technology evaluation. Neutral hypothesis framing and explicit "may remove" language protect against motivated reasoning.

---

### 11. Add Educator Walk-Through to Success Criteria

**Current Issue:**  
Section 15 defines success through technical and pedagogical measures but doesn't include student experience indicators, even at the prototype level.

**Location:** Section 15

**Recommendation:**  
Add to Section 15 success criteria:

> **12. Prototype Usability Validation**  
> At least 3 qualified educators (with 5-7 grade teaching experience) complete 2-3 representative scenarios each and report:
> - Whether a typical student at that grade level could navigate the interface and complete the revision loop independently
> - Specific points where language, instructions, navigation, or feedback density would likely cause confusion
> - Whether feedback tone reads as encouraging vs. overwhelming, condescending, or discouraging
> - Whether hints provide sufficient guidance without supplying answers
> - Technical or interaction issues that disrupted focus or flow
> - Overall assessment: "Ready for supervised student pilot," "Needs revision before student contact," or "Significant redesign required"

**Add to Section 14.3 (Evidence Gates):**

Before claiming readiness for supervised student contact:
- Educator walk-through validation is complete with at least 2 of 3 reviewers assessing the prototype as "Ready for supervised student pilot"
- Identified usability issues are addressed or documented as known limitations
- Findings are reported as limited synthetic evaluation by educators, not direct student feedback

**Learning Science Rationale:**  
Adult-designed "student-facing" interfaces often miss the mark. Educator walk-throughs catch egregious issues (confusing vocabulary, overwhelming density, unclear navigation, patronizing tone) before any student contact. This is a minimal gate, not a substitute for actual usability testing.

---

## Low Priority Improvements (Reduces Future Risk)

### 12. Soften Desktop Layout Mandate

**Current Issue:**  
Section 10.3 prescribes a specific 60/40 draft/feedback split with independent scrolling. This is a strong design assumption without user research backing.

**Location:** Section 10.3

**Observation:**
- Long drafts (300+ words) may make side-by-side feel cramped
- Students may prefer full-width draft with collapsible/expandable feedback
- Side-by-side significantly reduces available draft width (especially on smaller screens)
- The mockup validates one approach but shouldn't become doctrine

**Recommendation:**  
**Revise Section 10.3 opening:**

> After feedback is available, the desktop workspace uses **approximately 60% width for the editable draft and 40% for feedback** as the **initial validated layout**. The essay remains editable while its corresponding feedback stays visible, reducing whole-page scrolling and context switching.
>
> Draft and feedback panes scroll independently. Primary revision actions remain visible in a fixed or sticky feedback footer. New feedback replaces the previous feedback-panel content without replacing or scrolling the essay away from the student's current work.
>
> **V3 validation targets this specific desktop layout.** Alternative layouts (tabbed, collapsible sidebar, full-width alternating) require separate evaluation with representative drafts and educator feedback before adoption.

**Add to Section 18 (Deferred Decisions):**

> - Whether split-pane, tabbed, collapsible, or full-width alternating layouts better serve focused revision after initial desktop validation with real draft lengths and educator walk-throughs

**Add footnote about mobile:**

> V3 validation uses desktop browser width (1280px+). Optimized phone and tablet behavior is deferred and must not be inferred from the desktop layout. Many 5-7th grade students access schoolwork on tablets or shared family devices; stating "desktop only" as a product constraint should be reconsidered for any real classroom pilot.

**Learning Science Rationale:**  
Layout significantly affects cognitive load and revision behavior. The mockup shouldn't become unquestioned doctrine. Preserving flexibility allows evidence-based iteration.

---

## Additional Minor Clarifications

### Terminology Consistency

**Observation:**
- "Composition" vs. "session" used somewhat interchangeably
  - Section 11.6: "composition_id links the full writing session"  
  - They appear to be synonyms, but could confuse implementers
- "Scaffold" vs. "hint" vs. "support" used for similar concepts
  - RV-14 uses "hints" and "scaffolds"
  - Section 8.3 header says "scaffolds"
  - "Optional support" appears in multiple places

**Recommendation:**
- Define clearly in Section 11.6: "A **composition** is one complete writing session, identified by a stable `composition_id`. It includes the original submission, all revisions, selected goals, and feedback across multiple rounds."
- Standardize on **"scaffold"** as the umbrella term and **"hint"** as the specific guidance type:
  - Scaffolds = all optional supports (hints, practice, vocabulary, sentence starters)
  - Hints = the primary 2-4 step thinking guidance with self-checks
  - Reserve "support" for the Support Agent role name only

---

### Undefined Terms Needing Specification

**RV-24 "Uncertain" observation:**
- Section 8.4 says selected goals receive "specific improvement, improvement not yet evident, or uncertain"
- What triggers "uncertain"? Examples needed:
  - ✅ Student made changes but in different paragraphs than referenced?
  - ✅ Student made changes but introduced new ambiguity?
  - ❌ Never use "uncertain" as a hedge when the text clearly shows no improvement

**MC-06 "Explicitly authorized debug fields":**
- Says raw reasoning isn't stored "except explicitly authorized debug fields"
- Which fields are authorized? Recommend listing:
  - `model_name`, `thinking_enabled`, `reasoning_effort`, `prompt_version`, `schema_version`
  - NOT: raw reasoning tokens, hidden chain-of-thought, thinking process
  - Clarify whether request/response IDs, latency, token counts are "debug fields"

---

### Cross-Reference Gaps

**Section 7.4 → Section 18:**
- Section 7.4 says "Do not add an English-proficiency label or a fixed 'scaffolding level' slider in V3"
- Section 18 (Deferred Decisions) discusses "broader proficiency support"
- Recommend adding explicit cross-reference: "See Section 18 for discussion of whether proficiency-differentiated support should be explored post-V3"

**Section 11.5 Flow Diagram:**
- Could reference specific requirement IDs for each decision point:
  - clarification → (IN-04, Section 9.1)
  - teacher_review → (Section 9.3, RV-02)
  - direct_response → (Section 9.2, RV-28)
  - support → (RV-03 through RV-28)

---

## Summary: Recommendations by Priority

### **Critical** (Affects Pedagogical Validity)
1. ✅ Add diverse hint examples across genres and goal types (Section 8.3.2)
2. ✅ Operationalize "meaningful" with grade-level thresholds (Section 7.6)
3. ✅ Add source-grounded feedback examples (Section 6.4.1)
4. ✅ Define genre inference decision rules (Section 6.2.1)

### **High** (Affects Implementation Consistency)
5. ✅ Specify affect check-in placement and responses (Section 6.1.1)
6. ✅ State clarification limit explicitly (Section 9.1 revision)
7. ✅ Add scaffold boundary edge cases (Section 8.3.3)
8. ✅ Add anomalous interaction handling (Section 9.4)

### **Medium** (Improves Evaluation Rigor)
9. ✅ Add edge-case scenarios, especially multilingual learner focus (Section 14.2, scenarios 22-27)
10. ✅ Neutralize thinking-mode hypothesis framing (MC-04, Section 17, Section 14.4)
11. ✅ Add educator walk-through to success criteria (Section 15.12, Section 14.3)

### **Low** (Reduces Future Risk)
12. ✅ Soften desktop layout mandate (Section 10.3, Section 18)
13. Clean up terminology consistency (composition/session, scaffold/hint/support)
14. Define undefined terms (RV-24 "uncertain", MC-06 authorized fields)
15. Add cross-references (Section 7.4 ↔ 18, Section 11.5 flow → requirements)

---

## Implementation Path

**Immediate (before V3 implementation begins):**
- Items 1-4 (critical): These define what quality feedback looks like
- Items 5-6 (high): These prevent inconsistent interpretation during build

**During Implementation:**
- Items 7-8 (high): Add as requirements are translated to code
- Item 13-15 (low): Clean up during PRD revision pass

**Before Technical Validation:**
- Item 9 (medium): Scenarios must exist before claiming V3 is testable
- Item 12 (low): Soften layout language to preserve flexibility

**Before Quality Claims:**
- Item 10-11 (medium): Evaluation framing and educator validation gates

---

## Final Assessment

This PRD represents **exceptional foundational work**. The improvements identified here would:

1. **Reduce implementation ambiguity**: Concrete examples and operational definitions prevent inconsistent interpretation
2. **Protect pedagogical values**: Multilingual learner focus, voice preservation, and idea-first feedback are made testable
3. **Enable rigorous evaluation**: Edge cases, neutral hypothesis framing, and educator validation requirements
4. **Preserve flexibility**: Softer design mandates allow evidence-based iteration

The core vision—student-controlled iterative revision with genre-appropriate, source-grounded, voice-preserving feedback—remains sound. These improvements operationalize that vision for builders and evaluators.

**The PRD is ready for V3 implementation** once Critical and High-priority clarifications are integrated.