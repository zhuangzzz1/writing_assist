# Corrected Fix List

**Purpose**: Consolidates the original external review (`REVIEW_ANALYSIS.md`) and its validation (`REVIEW_VALIDATION.md`) into a single, corrected action list. The validation caught real errors in the original recommended fixes; this document supersedes both.

**Document date**: 2026-11-01

---

## How to Read This

Each issue shows:
- **Finding**: What's wrong (from the review, validated)
- **Original fix**: What `REVIEW_ANALYSIS.md` proposed
- **Validation correction**: What `REVIEW_VALIDATION.md` corrected
- **Corrected fix**: The action to actually apply

---

## Issue 1: Intentional V1 Limitations

**Finding**: V1 is designed to deliberately fail its own must-haves. The syllabus expects problems to be *observed* through review (learning outcome at syllabus line 26), not predetermined.

**Original fix**: Remove intentional-limitations language; build genuine V1.

**Validation correction**: The "observed problems" phrase comes from the learning outcomes, not the cited Part 3 lines. Don't frame the original approach as "gaming the assignment" — that assumes intent.

**Corrected fix**: Remove all intentional-limitations design language from PRD, project_plan, and CLAUDE.md. Build V1 as a genuine best effort with reasonable design choices. Document the real problems you observe during testing. Do not characterize the earlier approach as an attempt to game anything.

---

## Issue 2: Scripted Evidence

**Finding**: PRD and project_plan contain prewritten student reactions, hypothetical JeepyTA suggestions presented as accepted/rejected, and "testing showed" claims with no test artifacts.

**Original fix**: Replace fabricated quotes with placeholders; label hypotheticals.

**Validation correction**: Don't call it academic misconduct — these appear in planning docs and could be intended as examples. The risk is that they *become* fabricated evidence if presented as real results.

**Corrected fix**: Relabel all hypothetical scenarios explicitly ("Example scenario, not yet tested"). Replace fabricated student quotes with placeholders ("[Student reaction to be recorded during testing]"). Remove "testing showed" claims. After real testing, replace placeholders with actual observations. Do not attribute misconduct.

---

## Issue 3: Submission Checklist

**Finding**: CLAUDE.md lists 6 parts; syllabus requires 8 items including Application Access and AI Use Acknowledgment. Workflow mismatch (PDF to JeepyTA first, then Canvas link).

**Original fix**: Create authoritative 8-item checklist.

**Validation correction**: Syllabus requires PDF for *drafts* to JeepyTA; the final "one document" format is sensible as PDF but not strictly mandated.

**Corrected fix**: Create one authoritative submission checklist matching the syllabus exactly:

```
Document: One PDF containing all sections
Filename: FirstName_LastName_Assignment_4
Workflow:
  1. Submit PDF draft to JeepyTA (required before finalizing V2 per Part 4)
  2. Submit the JeepyTA assignment link on Canvas
  3. Include application access (deployed URL or files/notebook)

Required sections (8 items from syllabus lines 137-150):
  1. Educational Need and Agent Architecture
  2. Agent-Based Application Version 1 and Evidence
  3. Review of Agent-Based Application Version 1
  4. Agent-Based Application Version 2, Before-and-After Evidence, and Verification
  5. Agent Architecture and Development Process
  6. Brief Reflection
  7. Agent-Based Application Access (link/files/notebook)
  8. AI Use Acknowledgment (tool, purpose, contribution)
```

---

## Issue 4: Safety Routing Precedence

**Finding**: Router checks `missing_context` before `flag_teacher`. A submission with both ambiguous context and self-harm content would get clarification instead of human review.

**Original fix**: Move `flag_teacher` first; default to `support_agent`.

**Validation correction**: Defaulting unknown/malformed states to `support_agent` is not safe enough.

**Corrected fix**: Use a single `routing_decision` enum (see Issue 8). Precedence order:

1. `teacher_review` — safety/human-review conditions first, unconditionally
2. `ask_clarification` — missing critical context
3. `support_agent` — needs feedback or practice
4. `direct_response` — no actionable issues

For malformed or contradictory assessment output, route to `ask_clarification` (not `support_agent`). Document this fallback explicitly.

---

## Issue 5: Teacher Flagging Is Only Simulated

**Finding**: System displays a teacher-review recommendation but no real handoff, recipient, or persistence. For concerning content, withholding feedback may be insufficient.

**Original fix**: Label as simulated; add crisis keywords and hotline numbers.

**Validation correction**: Keyword-only detection is unreliable. Crisis language and hotline information must be institution-approved, current, and localized — not improvised by the system.

**Corrected fix**: Label the handoff honestly as simulated in the UI and docs. Do NOT improvise crisis keywords or hotline numbers. Document that a production system would need institution-approved crisis protocols, localized resources, and a real review queue. Separate student-facing supportive language from teacher-facing evidence in the teacher_review node output.

---

## Issue 6: Privacy Protections for Minors' Writing

**Finding**: Writing and concerns sent to external API, stored, exported. Syllabus prohibits PII in submissions.

**Original fix**: State "only writing content and grade level sent to DeepSeek."

**Validation correction**: The state schema also includes `assignment_type` and `student_concerns`, so that statement is false to the design — it requires an implementation change, not just documentation. Also, removing identifiers does not de-identify the writing content itself.

**Corrected fix**: Accurately document what is sent to the API: `writing`, `grade_level`, `assignment_type`, and `student_concerns` (all fields the user submits). Use only synthetic/LLM-generated writing for all testing — never real student essays. Add a UI warning: "Do not submit writing containing real names, schools, or personal information." Note that de-identification of content itself (not just identifiers) is a production concern beyond this demo. State in the AI Use Acknowledgment that all test data is synthetic. If you want to send only writing + grade level, that is an implementation decision to make in code, not a documentation claim.

---

## Issue 7: V2 Staged Feedback Incompatible with One-Shot Flow

**Finding**: V2 asks "want more suggestions?" but state has no `feedback_stage`, graph ends, no continuation path.

**Original fix**: Option A (collapsible expander) or Option B (multi-turn with loop-back).

**Validation correction**: Option A is "progressive disclosure" since all content generates in one response. Option B does not necessarily need a loop-back edge — a new graph invocation with saved state could also work.

**Corrected fix**: Use **progressive disclosure** for V2 (Option A). Rename the feature from "staged feedback" to "progressive disclosure" throughout the docs. All feedback generates in one response; the UI shows priority items prominently and additional detail in a collapsible expander. No multi-turn, no `feedback_stage` field, no loop-back. This achieves the V2 goal (less overwhelming) within the one-shot graph.

---

## Issue 8: State Schema and Routing Inconsistency

**Finding**: `no_issues_found` used in router but missing from schema. V2 examples reference undeclared fields. Conflicting booleans allow contradictory states.

**Original fix**: Add `no_issues_found`, use `typing.NotRequired`, use single routing enum, remove `needs_feedback`/`needs_practice`.

**Validation correction**: `typing.NotRequired` is Python 3.11+, not 3.10 (PRD targets 3.10+). Removing `needs_feedback`/`needs_practice` breaks the router that still reads them. TypedDict doesn't enforce at runtime, but accessing a missing key raises KeyError. Schema and router must be redesigned together, not patched independently.

**Corrected fix**: Redesign schema and router together.

- Use `typing_extensions.NotRequired` (compatible with Python 3.10), OR bump the Python target to 3.11+, OR use a dataclass with defaults. Pick one and be consistent. Recommend: bump to Python 3.11+ and use `typing.NotRequired`, since this is a new project.
- Add `no_issues_found: bool` to the schema.
- Replace the conflicting booleans with a single `routing_decision: Literal["ask_clarification", "support_agent", "teacher_review", "direct_response"]` as the authoritative routing signal. Keep `flag_teacher` and `teacher_flag_reason` as inputs the coordinator sets, but route on `routing_decision`.
- Keep `needs_feedback` and `needs_practice` if the Support Agent uses them to choose feedback vs. practice — but document that they drive Support Agent behavior, not routing.
- Initialize every field with a default in the node that first produces it; never read an uninitialized key.

---

## Issue 9: Test Cases Not Reproducible

**Finding**: Normal/boundary inputs are placeholders. LLM generation with temperature 0.7 varies between runs. Can't attribute V1→V2 differences to revisions. Contradiction: practice described as optional but success criteria requires it if thesis issue found.

**Original fix**: Freeze test cases as files; use temperature 0; clarify practice is optional.

**Validation correction**: Temperature 0 reduces variability but does not guarantee identical outputs. The proposed practice logic says the Support Agent identifies skill gaps, but the architecture assigns that to the Assessment Coordinator.

**Corrected fix**: Pre-generate the three test cases once, save as literal text files in `test_cases/`, commit to git, and use the identical fixtures for V1 and V2. Use temperature 0 for official test runs and note that some variability remains. Clarify responsibility: the **Assessment Coordinator** identifies skill gaps; the **Support Agent** generates practice based on those gaps. Resolve the practice-optionality contradiction: practice is *offered* when a skill gap is identified; whether the student uses it is outside the one-shot scope, so success criteria should be "practice is offered when a skill gap is identified," not "practice is required."

---

## Issue 10: Two-Agent Justification Not Convincing

**Finding**: "Different mindsets" is weak; one agent with separate instructions could do it. Syllabus permits single agent and emphasizes simplest architecture.

**Original fix**: Add observable benefits; test single-agent comparison.

**Validation correction**: The assignment does not *require* coordination demonstration — syllabus line 123 says "if multiple agents are used." Multi-agent is not inherently required. Testing a single-agent comparison is optional and adds scope.

**Corrected fix**: Strengthen the justification with observable benefits without claiming the assignment requires multi-agent:
- Decision traceability: assessment decisions isolated from intervention execution.
- Failure isolation: a bad Support Agent response doesn't invalidate the assessment.
- Modular prompt engineering: structured JSON output vs. natural student-facing text.
- Future extensibility: add specialized agents without rewriting core logic.
- Clear handoff points to document for Part 5.

Acknowledge trade-offs honestly: extra latency, coordination overhead, more failure points. Do not claim the assignment requires coordination. Do not mandate a single-agent comparison test — it is optional scope. Note that a single agent with conditional actions could also be defensible, and explain why you chose two agents anyway.

---

## Issue 11: DeepSeek Model Identifier

**Finding**: PRD names "DeepSeek V4.1 Flash" but code sends `"model": "deepseek-chat"`. Official docs specify `deepseek-flash` for DeepSeek-V4.1-Flash-1017.

**Original fix**: Test `deepseek-chat` first.

**Validation correction**: Should test the documented `deepseek-flash` identifier first. An old alias may redirect or retire rather than erroring, so rely on official docs as the source of truth.

**Corrected fix**: Test the documented `deepseek-flash` identifier first. Use `requests` directly (not an ambiguous `deepseek-api-client` that may not exist). Verify with a real API call on Day 1 of implementation. Update all PRD references to use `deepseek-flash`. Keep `requests>=2.31.0` as an explicit dependency.

---

## Issue 12: Plan Over-Scoped

**Finding**: SQLite, hybrid storage, run history, live side-by-side, elaborate visualizations all treated as must-haves. Storage simultaneously "must have" and "nice to have." Delivery risk.

**Original fix**: Prioritize features; "all 6 parts + evidence" as must-have.

**Validation correction**: Must-haves should include all 8 submission items, not 6. "JeepyTA feedback incorporation" means reviewing with judgment, not necessarily accepting.

**Corrected fix**: Tier the features:

- **Must have (core assignment)**: two-agent LangGraph with conditional routing; three test cases working; V1; V2 with improvements; basic Streamlit UI; JeepyTA feedback reviewed with judgment; documentation covering all 8 submission items; evidence captured.
- **Should have (user learning goals)**: observability timeline; routing decision display; state change visibility; LangGraph static visualization; test case loader.
- **Nice to have**: SQLite persistence; live V1/V2 side-by-side; advanced charts; export.
- **Cut if behind**: SQLite (use session_state only); live comparison (use screenshots); fancy visualizations (text logs suffice); run history beyond current session.

---

## Issue 13: Smaller Inconsistencies

**Finding**: Wrong dates; missing routes in some docs; pre-checked approval boxes; inconsistent boundary assignments.

**Original fix**: Date to October 2024; uncheck boxes; route teacher-flag message to Support Agent.

**Validation correction**: October 2024 still conflicts with Fall 2026 assignment — use a 2026 date. The uncheck snippet left boxes checked. Routing the teacher-flag message to the Support Agent conflicts with the graph, which routes teacher review *around* the Support Agent — the message belongs in the teacher_review node.

**Corrected fix**:
- Set all document dates to 2026-11-01.
- Include all four routes (clarification, support, teacher_review, direct_response) consistently across PRD, project_plan, and CLAUDE.md.
- Uncheck approval boxes properly (leave only "Technical feasibility reviewed" and "Rubric alignment verified" checked; uncheck "Timeline validated" pending implementation, and keep "Development started" unchecked).
- Put the teacher-flag display in the `teacher_review` node, not the Support Agent. The Support Agent never runs when teacher review is triggered.
- Label success metrics as "Target Metrics (to be validated after implementation)" rather than pre-asserted facts.
- Fix the REVIEW_ANALYSIS.md internal summary error separately (4 critical, 6 important, 2 partial, 0 invalid — not 6/4/2/1).

---

## Application Order

Apply in this order to minimize rework:

1. **Issue 13** (dates, routes, boxes) — quick mechanical fixes.
2. **Issue 8** (state schema + router redesigned together) — foundational; affects Issues 4, 7.
3. **Issue 4** (routing precedence with safe fallback) — depends on Issue 8.
4. **Issue 7** (progressive disclosure rename) — depends on Issue 8.
5. **Issue 1** (remove intentional limitations) — affects PRD Section 8, CLAUDE.md, project_plan.
6. **Issue 2** (relabel scripted evidence) — affects PRD Section 8, project_plan.
7. **Issue 6** (privacy, accurate data-sent statement) — new PRD section.
8. **Issue 5** (simulated teacher review labeling) — affects PRD, CLAUDE.md.
9. **Issue 9** (freeze test cases, fix practice optionality, fix skill-gap owner) — affects PRD Section 7.
10. **Issue 10** (strengthen multi-agent justification) — affects PRD Section 4.4, project_plan.
11. **Issue 11** (DeepSeek model id) — affects PRD Section 9.3, requirements.
12. **Issue 12** (scope tiers) — affects PRD feature list, CLAUDE.md.
13. **Issue 3** (submission checklist) — affects PRD, CLAUDE.md.

---

*End of corrected fix list.*
