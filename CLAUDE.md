# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a multi-agent writing assistant for 5th-7th grade students, built as an academic project for EDUC 6192 (LLM and Education) at UPenn GSE. The system uses LangGraph to coordinate two agents that analyze student writing and provide developmentally-appropriate feedback and practice exercises.

**Key Context**: This is an academic assignment focused on demonstrating agent coordination and decision-making, NOT building production software. The rubric prioritizes clear agent behavior, meaningful routing decisions, and observable improvements from V1 to V2.

## Critical Design Decisions

### Multi-Agent Architecture (Must Preserve)

**Two agents with distinct roles**:
1. **Assessment Coordinator**: Analytical decision-maker that routes based on writing analysis
2. **Instructional Support Agent**: Empathetic feedback provider and practice generator

**Why multi-agent is justified**: Assessment and intervention require different "mindsets" (analytical vs. supportive). This mirrors authentic teaching practice and demonstrates conditional coordination (not a fixed workflow).

**Routing must be conditional**: Not every input follows the same path. The system must demonstrate "meaningful agent-controlled decisions" to meet rubric requirements. Avoid sequential pipelines where agents always run in the same order.

### V1 vs V2 Strategy

**V1 is a genuine best effort** — not deliberately deficient. Build V1 with reasonable design choices, test it against the frozen test cases, observe what actually goes wrong, and document those real problems for V2. Do not predetermine V1 failures or script evidence before testing.

**V2 fixes problems actually observed in V1 testing.** Target improvement areas (apply only if the problem was observed): feedback volume via progressive disclosure, clarification specificity, teacher-flagging transparency. The assignment grades on observed iteration, not predetermined failure.

## Architecture

### LangGraph State Flow

```
Input → Assessment Coordinator → (conditional routing) →
    ├─→ Ask Clarification (missing/ambiguous input)
    ├─→ Support Agent → Feedback or Practice
    ├─→ Flag Teacher (boundary conditions)
    └─→ Direct Response (minimal issues)
```

**State schema** (`langgraph_core/state.py`): Contains writing input, assessment results, a single `routing_decision` enum, agent outputs, and execution metadata. Requires Python 3.11+ (uses `typing.NotRequired`). Every field has exactly one node that first produces it; never read an uninitialized key. `needs_feedback` and `needs_practice` drive Support Agent behavior only — routing is driven solely by `routing_decision`.

**Routing logic** (`langgraph_core/routing.py`): Reads `state.get("flag_teacher")` first (safety override), then routes on the `routing_decision` enum. Uses `state.get()` for all field access to avoid `KeyError`. Malformed or missing `routing_decision` falls back to `ask_clarification`. `needs_feedback` and `needs_practice` are never read by the router — only by the Support Agent node.

### Agent Prompts

Located in `agents/prompts.py`. Keep V1 and V2 prompts separate.

**Assessment Coordinator**: Analytical tone, structured decision output (JSON or dict), includes routing reasoning.

**Support Agent**: Encouraging tone, grade-appropriate language (5th-7th grade), starts with strengths before improvements.

### Storage Abstraction

**Hybrid approach** (`storage/`):
- **Local development**: SQLite (`sqlite_storage.py`) persists run history across sessions — Nice to Have, build only if on track after Week 1
- **Streamlit Cloud**: Session state (`session_storage.py`) ephemeral but sufficient for demos and submission
- Auto-detection: Check for `/.streamlit` or use `FORCE_SQLITE` env var
- Both implement same interface (`storage/interface.py`)
- **Default**: Start with session_state only; add SQLite if time permits

## Development Commands

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env  # Add DEEPSEEK_API_KEY
```

### Run Application
```bash
streamlit run app.py
```

### Generate Test Cases
```bash
python test_cases/generator.py  # Uses LLM to create realistic student writing
```

### Deploy to Streamlit Cloud
Push to GitHub, connect repo at share.streamlit.io, set DEEPSEEK_API_KEY in secrets.

## Test Cases (Critical for Assignment)

Three required scenarios are represented by four frozen fixture files in `test_cases/`:

1. **Normal Case** (`normal_case.txt`): Complete 6th-grade persuasive essay
2. **Incomplete Case** (`incomplete_case.txt`): Outline only
3. **Boundary Case A** (`boundary_case_a.txt`): Concerning content — official third case
4. **Boundary Case B** (`boundary_case_b.txt`): Student frustration — additional test

Use the identical fixture text for V1 and V2, and use temperature 0 for all official test runs. Do not regenerate fixtures between versions.

## UI Requirements

**Priority**: Observability and agent behavior quality over UI polish.

**Must have**:
- 3-column layout: Controls (sidebar) | Input/Output (main) | Observability (right panel)
- Agent execution timeline showing step-by-step flow
- Routing path visualization (which agents ran, which path taken)
- State changes visible (what changed at each step)
- LangGraph structure visualization (graph with highlighted execution path)
- V1/V2 version toggle
- Test case loader (one-click to load normal/incomplete/boundary)

**Debug panels** (expandable): Full prompts, LLM responses, execution logs, timing info.

## API Integration

**DeepSeek V4.1 Flash 1017** via direct API (model identifier: `deepseek-flash` per official docs — verify on Day 1):
- Client in `agents/utils.py` using `requests>=2.31.0`
- Standard error handling: timeout, rate limit (429), auth (401)
- Set reasonable timeouts (30s default)
- Expected latency: 3-7 seconds end-to-end

**Cost**: DeepSeek is very cost-effective; daily testing negligible.

## Error Handling

**V1**: Standard error handling with specific error types and user-friendly messages.

**V2**: Can add retry logic, fallbacks, structured logging (optional improvement).

Catch: `APIError`, `RateLimitError`, `AuthError`, `InputValidationError`. Display helpful messages in Streamlit (`st.error`, `st.warning`).

## Assignment Submission Requirements

Must produce evidence for all 8 submission items (see syllabus lines 137-150):

1. Educational Need and Agent Architecture
2. Agent-Based Application Version 1 and Evidence
3. Review of Agent-Based Application Version 1
4. Agent-Based Application Version 2, Before-and-After Evidence, and Verification
5. Agent Architecture and Development Process
6. Brief Reflection (200-300 words)
7. Agent-Based Application Access (Streamlit Cloud URL / files / notebook)
8. AI Use Acknowledgment (tool, purpose, contribution)

**Submission workflow** (from syllabus lines 165-170):
1. Compile all sections into one PDF: `FirstName_LastName_Assignment_4.pdf`
2. Submit PDF to JeepyTA (required before finalizing V2 — Part 4)
3. Submit the JeepyTA assignment link on Canvas
4. Include Streamlit Cloud URL for live app access

Capture screenshots, routing decision logs, and timing info during testing. Redact any identifying info before including in the PDF.

## Key Constraints

**Rubric Focus**: 
- 20% Architecture justification (why multi-agent is simplest adequate)
- 20% Functional with meaningful decisions (avoid fixed workflow trap)
- 20% Appropriate behavior and coordination (3 test cases)
- 20% Iterative improvement (V1→V2 with evidence)
- 20% Development evidence and reflection

**Timeline**: 2 weeks balanced schedule (see PRD Section 10).

**Age appropriateness**: All feedback must be suitable for 10-13 year olds (encouraging, not harsh).

**Practice generation**: Broad coverage of writing skills (thesis, organization, transitions, evidence, grammar) based on identified gaps.

## What NOT to Do

- Don't make this a fixed workflow (same path every time)
- Don't add agents without clear justification (rubric penalizes over-engineering)
- Don't predetermine V1 failures or present scripted evidence as real test results
- Don't add production features (auth, multi-user, complex state persistence) unless required
- Don't spend excessive time on UI polish at expense of agent behavior quality
- Don't route to `support_agent` as a safety fallback — unclear/malformed state routes to `ask_clarification`
- Don't improvise crisis hotline numbers or keyword-based crisis detection — flag for teacher only and label the handoff as simulated

## Reference Documents

- **PRD.md**: Complete product requirements (read first)
- **project_plan.md**: Assignment strategy and rubric mapping
- **EDUC_6192_Fall_2026_Syllabus.md**: Assignment requirements and grading criteria

When in doubt about design decisions, consult PRD Section 4 (Architecture) and Section 8 (V1 vs V2 Strategy).
