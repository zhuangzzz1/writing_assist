# Writing Assistant Multi-Agent System - Project Plan

## Overview

**Course**: EDUC 6192 - LLM and Education (UPenn GSE)  
**Assignment**: Applied Assignment 4 - Agent-based Educational Application  
**Due**: November 3, 2026  
**Framework**: LangGraph (Multi-Agent System)  
**Target Users**: 5th-7th grade students (ages 10-13)

---

## Core Design Philosophy

**Goal**: Build a 2-agent system that's justifiable, demonstrates meaningful coordination, and produces genuine V1→V2 improvement based on observed testing.

**Key insight**: The assignment grades on *iteration and improvement*, not perfection. Build V1 as a genuine best effort, observe what actually goes wrong during testing, and fix those real problems in V2.

---

## Proposed Multi-Agent Architecture

### **2-Agent System with LangGraph Coordination**

**Agent 1: Assessment Coordinator**
- **Role**: Analyzes student writing, makes routing decisions, enforces boundaries
- **Responsibilities**: 
  - Initial analysis of writing quality and completeness
  - Decides what the student needs (clarification, feedback, scaffolding, practice, teacher review)
  - Routes to appropriate agent or stops the process
  - Tracks interaction state
- **Key decisions**: When to ask clarification, when to route to Support Agent, when to flag teacher

**Agent 2: Instructional Support Agent**  
- **Role**: Provides scaffolded feedback, revision suggestions, and practice materials
- **Responsibilities**:
  - Generates age-appropriate feedback (5th-7th grade level)
  - Creates scaffolding when students need step-by-step help
  - Generates targeted practice exercises when gaps are identified
- **Key decisions**: What type of support to provide based on assessment, how to scaffold

**Why this is justifiable as multi-agent**:
1. **Decision traceability**: Assessment decisions are isolated from intervention. When feedback is inappropriate, it is clear whether the coordinator misjudged the need or the Support Agent generated poor content.
2. **Failure isolation**: A bad Support Agent response doesn't invalidate the assessment — the coordinator's analysis can be reused for a retry.
3. **Modular prompt engineering**: Assessment requires structured JSON output; intervention requires warm, student-facing prose. Separate agents allow each prompt to be optimised independently.
4. **Clear handoff for documentation**: Part 5 asks for coordination explanation — two agents provide a concrete, documentable handoff point.
5. **Future expansion**: Specialised agents can be added without rewriting core assessment logic.

**Note**: The assignment permits a single agent and emphasises the simplest adequate architecture. Multi-agent is a deliberate design choice for the learning goal and the observable benefits above — not an assignment mandate.

**LangGraph Flow**:
```
Input → Assessment Coordinator → (conditional routing) →
                                ├─→ Ask Clarification (missing info)
                                │   └─→ interrupt → student answer → Coordinator reassessment
                                ├─→ Support Agent (normal case)
                                │   └─→ Feedback + one targeted exercise when warranted
                                ├─→ Teacher Review (boundary case)
                                └─→ Direct Response (no actionable issues)
```

Clarification uses an exact LangGraph interrupt/resume with a SQLite checkpoint and stable thread ID. If two clarification answers still leave intent unclear, the system routes to non-safety teacher review with the clarification history. Teacher review uses coordinator evidence and reviewed templates, not additional audience-specific agents.

---

## Assignment Part-by-Part Strategy

### **Part 1: Define Educational Need and Agent Architecture** 
*(Addresses Rubric Criterion 1: 20%)*

**What to document**:

1. **Intended users**: 5th-7th grade students (ages 10-13) working on persuasive or analytical writing assignments

2. **Educational need**: Students need formative feedback on writing but often receive feedback that's too advanced, too sparse, or lacks actionable next steps

3. **Main task**: Analyze student writing drafts and provide developmentally-appropriate feedback with scaffolding

4. **User input**: Writing draft, one flexible assignment type or prompt field (optional), grade level, specific concerns (optional), and clarification answers when requested

5. **Architecture choice**: **2-agent system with LangGraph state graph**

6. **Agent responsibilities**:
   - **Assessment Coordinator**: Analyzes writing, decides intervention type, enforces boundaries (no harsh criticism, no doing work for student)
   - **Instructional Support**: Generates feedback, scaffolding, or practice based on coordinator's routing decision

7. **Available resources**: Writing rubrics, grade-level writing standards, example scaffolds, practice exercise templates

8. **Clarification triggers**: Missing grade level, unclear what assignment asks for, submission is not actually writing (image, single sentence)

9. **Coordination approach**: LangGraph conditional edges route from Assessment Coordinator to Support Agent only when intervention is needed; state tracks what's been provided

10. **Completion conditions**: Feedback provided + student has clear next steps, OR system determines teacher review needed

11. **Stop/human assistance conditions**: Concerning content, clear revision frustration, or intent remains ambiguous after two clarification answers; the last case uses non-safety teacher review with the clarification history

12. **Success criteria**: Student receives clear, kind, actionable feedback appropriate to grade level; system avoids fixed workflow by routing based on writing needs

**Strategic note**: Keep this section to 2-3 pages. Be specific about the coordination and decision points (this addresses the "fixed workflow" trap).

---

### **Part 2: Agent-Based Application Version 1** 
*(Addresses Rubric Criterion 2: 20%)*

**Implementation strategy**:

**Version 1 approach**:
- Build V1 as a genuine best effort with reasonable design choices
- Do not deliberately introduce deficiencies
- Test against the frozen test cases and observe what actually goes wrong
- Document the real problems found (there will be some — LLM behaviour is not perfectly controllable)

**Test with one representative request**: 
"Here's my persuasive essay about why we should have longer recess. [5-paragraph draft with weak thesis and good supporting details]"

**Evidence to save**:
- LangGraph architecture diagram
- Agent prompts/instructions
- State schema
- Screenshot of test run showing Assessment → Support Agent routing
- Key decision points in the logs

**Strategic note**: Version 1 should *work*. The problems you'll fix in V2 are the ones you *observe* during testing, not ones you script in advance.

---

### **Part 3: Review Version 1 & Identify Problems** 
*(Sets up Rubric Criterion 4: 20%)*

**Test case design** (these are critical for showing improvement):

**Case 1: Normal case**
- **Input**: Complete 6th-grade persuasive essay with identifiable issues (weak thesis, some grammar errors, good evidence) — frozen fixture in `test_cases/normal_case.txt`
- **Expected behavior**: Assessment Coordinator analyzes → routes to Support Agent → feedback provided
- **What to document**: The actual routing decision, the coordinator's reasoning, and the feedback generated
- **Problems to look for**: Does feedback feel overwhelming? Is the tone appropriate for a 6th grader? Are routing decisions consistent?

**Case 2: Incomplete/ambiguous case**
- **Input**: Outline only — frozen fixture in `test_cases/incomplete_case.txt`
- **Expected behavior**: Assessment Coordinator detects incomplete draft → asks specific clarification
- **What to document**: What clarification question was generated and how specific it was
- **Problems to look for**: Is the clarification question generic ("I need more info") or targeted to what's actually missing?

**Case 3: Boundary case**
- **Input**: Essay with concerning content or frustrated student — frozen fixtures in `test_cases/boundary_case_a.txt` and `test_cases/boundary_case_b.txt`
- **Expected behavior**: Assessment Coordinator flags for teacher review; teacher-review node generates response (not Support Agent)
- **What to document**: Whether safety routing fires before context checks; what student-facing and teacher-facing messages look like
- **Problems to look for**: Does the flag message clearly separate student-facing from teacher-facing content? Is the handoff labelled as simulated?

**Problems to identify for V2**: Document the 2-3 most significant problems actually observed — do not script them in advance.

---

### **Part 4: Version 2 with Before-and-After Evidence** 
*(Addresses Rubric Criterion 3 & 4: 40%)*

**Revisions to make** (apply only to problems actually observed in V1 testing):

**Target Area 1: Feedback volume and priority**
- **If observed**: V1 Support Agent generates too many feedback points at once
- **V2 fix**: Progressive disclosure — generate all feedback in one response, but surface 2-3 priority items prominently and place additional detail in a collapsible expander in the UI
- **Why**: Less overwhelming for 5th-7th graders; mirrors how teachers scaffold feedback. This is not multi-turn — all content is generated in one LLM call.

**Target Area 2: Clarification specificity**
- **If observed**: V1 clarification questions are generic ("I need more information")
- **V2 fix**: Improve the Assessment Coordinator prompt to identify *what specifically* is missing and ask about it ("I see you've shared an outline. Are you looking for help turning this into paragraphs, or feedback on your thesis statement?")
- **Why**: Models good questioning; helps students understand what "complete" means

**Target Area 3: Teacher-flagging transparency**
- **If observed**: V1 teacher-flag messages lack clear reasoning
- **V2 fix**: Restructure the teacher-review node output into two distinct parts: a student-facing supportive message and a teacher-facing evidence summary
- **Why**: Transparency for students and teachers; builds trust

**Before-and-after evidence**:
- Rerun the identical frozen test case fixtures on both V1 and V2
- Side-by-side comparison of actual V1 vs V2 outputs
- Document what changed and why with real screenshots

**JeepyTA feedback loop**:
- Submit V2 draft PDF to JeepyTA before finalizing (required by Part 4)
- Document one suggestion you accepted and one you rejected with reasoning (Part 5 requirement)
- Review suggestions with judgment — you are not required to accept every suggestion

**Strategic note**: This section is worth 40% combined. Show clear, evidence-based improvement. The problems fixed should be the ones you actually observed, not ones you scripted in advance.

---

### **Part 5: Explain Architecture & Development Process** 
*(Addresses Rubric Criterion 5: 20%)*

**What to document**:

1. **Major instructions/configuration**: 
   - Assessment Coordinator prompt (analytical, decision-making focus)
   - Support Agent prompt (empathetic, scaffolding focus)
   - LangGraph state schema and conditional edge logic

2. **Two important revisions** (from V1→V2):
   - [To be filled with the two most significant revisions actually made after V1 testing — e.g., progressive disclosure if feedback volume was an observed problem, or clarification specificity if generic questions were observed]

3. **Why multi-agent coordination is necessary**:
   - Assessment and intervention require different "mindsets" (analytical vs. supportive)
   - Conditional routing means Support Agent only runs when needed (not a fixed workflow)
   - State management tracks conversation context across agents
   - Clear handoff: Assessment determines *what* student needs → Support determines *how* to provide it

4. **AI suggestion example**:
   - **Accepted**: [To be filled with an actual JeepyTA suggestion you accepted and why]
   - **Rejected**: [To be filled with an actual JeepyTA suggestion you rejected and why]

5. **Your judgment example**:
   - [To be filled with a real decision you made during development — e.g., why you kept 2 agents instead of adding a third, or why you chose a particular prompt structure]

---

### **Part 6: Brief Reflection (200-300 words)** 
*(Addresses Rubric Criterion 5: 20%)*

**Structure**:

**Paragraph 1: Agent-based vs. fixed workflow**
- What you learned: Agent-based design is valuable when the *path* through the task should vary based on input, not just the content at each step. A fixed workflow would analyze→feedback→practice every time; my agent system routes differently based on whether writing is complete, what issues exist, and whether boundaries are crossed.

**Paragraph 2: Why 2-agent is simplest adequate**
- The Assessment-Support split produces different prompting requirements (structured JSON output vs. warm student-facing prose) that are easier to optimise in separate agents. A single agent would need to switch modes, making prompt engineering harder and behaviour less consistent. Three or more agents would add coordination overhead without clear educational benefit. After testing, document whether the 2-agent design handled all three cases appropriately and whether a simpler design would have sufficed.

**Paragraph 3: Limitations and human oversight**
- Limitations: Cannot detect all concerning content; may miss cultural context; practice is limited to one coordinator-identified gap per support run; shared-demo session filtering is not authentication. Human review is needed for concerning content, revision frustration, unresolved clarification after two answers, and situations outside the system's educational role. Teachers should review feedback before real student use in any production setting.

---

## Implementation Timeline & Strategy

### **Phase 1: Build Version 1 (Foundation)**
- Set up LangGraph with 2 agents, all four routes, exact clarification resume, SQLite history, and the full dashboard
- Implement conditional routing with safety-first precedence and automated mocked tests after each stage
- Use the completed smoke comparison's official V1 choice: non-thinking mode at temperature 0; keep it fixed for V2 comparisons
- Test real frozen fixture flows; build a genuine best effort and observe actual problems

### **Phase 2: Test & Document Problems**
- Run all frozen test cases with the frozen official model configuration (temperature 0 only in non-thinking mode)
- Document actual routing decisions and coordination
- Identify 2-3 real problems from observed behaviour
- Preserve verified V1 with a Git tag before changing V2 behavior

### **Phase 3: Build Version 2 (Refinement)**
- Fix observed problems from V1 testing
- Submit V2 draft PDF to JeepyTA before finalizing
- Incorporate relevant JeepyTA feedback with judgment
- Retest using the identical frozen fixtures

### **Phase 4: Documentation**
- Write architecture justification
- Document development decisions (with real JeepyTA examples)
- Write reflection based on what you actually observed
- Assemble evidence (screenshots, logs, routing paths)
- Compile one PDF: `FirstName_LastName_Assignment_4.pdf`
- Submit to JeepyTA then link on Canvas

---

## Key Success Factors for Rubric

✅ **Architecture justification** (20%): 2-agent split has clear educational rationale; LangGraph enables conditional routing (not fixed workflow)

✅ **Functional with meaningful decisions** (20%): Conditional edges show agent-controlled routing; not every path runs every time

✅ **Appropriate behavior & coordination** (20%): 3 test cases show clarification, normal operation, and boundary handling; agent handoff is documented

✅ **Iterative improvement** (20%): V1→V2 shows specific, evidence-based fixes; same test cases demonstrate improvement

✅ **Development evidence & reflection** (20%): Architecture choices explained; AI suggestions filtered with judgment; limitations acknowledged

---

## Critical Design Decisions

### **Why Multi-Agent is Justified**

1. **Distinct educational roles**: Assessment vs. intervention mirrors authentic teaching practice
2. **Different prompting needs**: Assessment requires analytical/objective lens; support requires empathetic/developmental lens  
3. **Conditional coordination**: Not a fixed workflow - Support Agent only runs when needed
4. **State management**: LangGraph tracks conversation context across agents
5. **Future expansion**: Can add specialized agents in follow-up assignments

### **Avoiding the "Fixed Workflow" Trap**

- LangGraph conditional edges make routing decisions explicit
- Not every input follows the same path
- Assessment Coordinator makes meaningful decisions about what happens next
- State-driven routing (not sequential pipeline)

### **Simplest Adequate Architecture**

- Could be done with 1 agent + tools, but 2 agents provide:
  - Decision traceability (assessment vs. intervention failures are separately attributable)
  - Failure isolation (bad Support Agent response doesn't invalidate assessment)
  - Modular prompt optimisation (structured JSON output vs. warm student-facing prose)
  - Clear handoff point for Part 5 documentation
  - Foundation for future expansion
- More than 2 agents would add complexity without clear educational benefit at this scope
- The assignment permits a single agent — two agents is a deliberate design choice, not a requirement

---

## Key Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| **Fixed workflow criticism** | Conditional routing with LangGraph; document all four routing paths clearly |
| **Over-engineering criticism** | Keep to 2 agents; justify each agent role with observable benefits |
| **V1→V2 improvements unclear** | Build genuine V1; observe real problems; retest with identical frozen fixtures |
| **Coordination overhead** | Use LangGraph state management; keep handoffs simple |
| **Age-inappropriate feedback** | Explicit prompts for 5th-7th grade level; test with frozen examples |

---

## Success Criteria

This plan:
- ✅ Uses multi-agent LangGraph (learning goal + future expansion)
- ✅ Has observable justification for multi-agent (decision traceability, failure isolation, modular prompts)
- ✅ Demonstrates dynamic decision-making with safety-first routing precedence
- ✅ Is scoped to assignment requirements (not over-building)
- ✅ Has genuine V1→V2 improvement path (based on observed testing)
- ✅ Addresses all rubric criteria explicitly
- ✅ Covers all 8 submission items per syllabus
- ✅ Allows future expansion (can add agents in follow-up assignments)
