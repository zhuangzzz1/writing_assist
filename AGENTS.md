# AGENTS.md

Guidance for AI coding agents working in this repository. Keep documentation and user-facing text in English.

## Project Overview

This EDUC 6192 Applied Assignment 4 project is a writing assistant for students in grades 5-7 (ages 10-13). Two LangGraph agents analyze synthetic student writing, provide developmentally appropriate feedback and targeted practice, ask clarifying questions, and route boundary cases to simulated teacher review.

The assignment emphasizes meaningful agent-controlled decisions, appropriate clarification and stopping behavior, and evidence-based improvement from V1 to V2. It is an educational demo, not production software. The two-agent design is a project decision; the syllabus also permits a single agent.

## Current Repository Status

V2 is implemented as the active application, with V1 preserved at commit `4eaa0ad` under the annotated `v1` tag:

- `app.py`, `agents/`, `langgraph_core/`, `ui/`, and `storage/` implement the application.
- `requirements.txt`, `requirements-dev.txt`, `.env.example`, and `pytest.ini` configure it; `.env.example` and the application default select V2.
- The current suite has 83 passing checks using mocked model calls and temporary databases.
- Real V1 and V2 comparisons used the frozen configuration: `deepseek-flash`, non-thinking mode, temperature 0, and JSON mode.
- Actual V1 outcomes are in `PRD.md` Section 7.5, pre-review V2 outcomes in Section 7.6, and definitive post-JeepyTA outcomes in Section 7.7.
- Final V2 evidence is in git-ignored `data/v2_final_post_jeepyta_20261103.db` and `data/evidence/v2_final_post_jeepyta_20261103_summary.json`, with post-review browser captures in `data/evidence/`.
- The concise authoritative submission is `submission/Applied_Assignment_4_Revised.md`, with `submission/Patrick_Zhuang_Assignment_4.pdf` and ten embedded figures. JeepyTA review was completed on 2026-11-03; final Canvas submission and rubric completion remain open.
- The post-JeepyTA code is deployed from `origin/main` at commit `7d94b58`, and the annotated `v1` tag is public. After an authorized reboot, the public app and normal, incomplete/resume, and Boundary A scenarios passed on 2026-11-03. Evidence is in `data/evidence/deployed_v2_post_jeepyta_verification_20261103.json` and three captures.

Do not claim real model quality, learner-outcome improvements, performance targets, rubric completion, or deployment until corresponding artifacts exist. Design/output evidence is not evidence of improved learner motivation or engagement. Historical review documents are not evidence of current behavior.

## Repository Map

- `PRD.md`: Product and technical specification, including authoritative V1/V2 outcomes and evidence provenance.
- `project_plan.md`: Assignment strategy, rubric mapping, phases, and submission plan.
- `CLAUDE.md`: Detailed coding guidance, locked V1 decisions, and current V2 decisions.
- `EDUC_6192_Fall_2026_Syllabus.md`: Authoritative assignment requirements.
- `test_cases/`: Four committed, frozen, synthetic fixtures; do not edit them for official runs.
- `submission/`: Concise final submission, preserved full/sectional drafts, and cropped evidence figures. `Applied_Assignment_4_Revised.md` is the authoritative submission text and `Patrick_Zhuang_Assignment_4.pdf` is the submission PDF; `Applied_Assignment_4_Full_Draft.*` preserves the longer pre-review draft. `*_Review*.md` files are historical review records, not current behavior evidence.
- `CORRECTED_FIX_LIST.md`: Historical corrected design-review action list; current code and PRD supersede old state descriptions.
- `REVIEW_ANALYSIS.md`, `REVIEW_VALIDATION.md`, `FIX_APPLICATION_REVIEW.md`, `FIX_APPLICATION_REVIEW_VALIDATION.md`, `CODE_REVIEW.md`, `PROMPT_REVIEW.md`, `PROMPT_IMPROVEMENT_PLAN.md`: Historical development review records only; current code and PRD supersede old state descriptions.

When architecture or development rules change, keep `PRD.md`, `project_plan.md`, `CLAUDE.md`, and this file consistent with actual code.

## Technology and Commands

Python 3.11+ is required; the local virtual environment uses Python 3.12. LangGraph 1.2+, Streamlit, Pydantic, direct `requests` HTTP calls, and SQLite are used. LangChain Core is transitive, not a separate agent wrapper.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Add DEEPSEEK_API_KEY locally
pytest
streamlit run app.py
```

Run pytest after each implementation stage. No formatter, linter, or type-checker is configured. The API timeout is 30 seconds. Standard errors cover empty input, timeout/connection failures, HTTP errors, 429, 401, malformed model responses, and invalid support output.

## Agent and Graph Architecture

Preserve two distinct decision-making agents unless real testing supports an architecture change:

1. **Assessment Coordinator**
   - Analyzes completeness, quality, issues, skill gaps, affect self-reports, and boundaries.
   - Produces validated structured assessment, concise final-output rationale, and routing.
   - Owns initial boundary detection and sets `flag_teacher` and `routing_decision`.
   - In V2, also selects `light_touch` or `standard` revision need and permits one bounded schema repair.
2. **Instructional Support Agent**
   - Produces warm, grade-appropriate feedback grounded in coordinator findings and V2 clarification history.
   - V1 returns 2-3 priorities and one exercise when requested. V2 returns one light-touch priority or 2-3 standard choices, with one pregenerated optional exercise per standard choice when requested. Final V2 practice uses instructions, steps, and a self-check without complete worked examples.
   - Uses coordinator-identified gaps and does not own initial routing. V2 permits one bounded schema repair.

```text
Input -> Assessment Coordinator -> conditional route
    |- ask_clarification -> interrupt -> answer -> Assessment Coordinator
    |- support_agent -> feedback + pregenerated choices/practice -> END
    |- teacher_review -> separate student/teacher outputs -> END
    `- direct_response -> affirm without forced criticism -> END
```

Clarification uses exact LangGraph interrupt/resume, stable thread IDs, and SQLite checkpoints. After two unclear answers, the next clarification request becomes non-safety teacher review with category `clarification_limit`. Teacher review, clarification, and direct response are deterministic nodes, not additional agents. Teacher review uses coordinator evidence and category-specific templates and bypasses the Support Agent.

V2 learner focus and practice selection happen in Streamlit after graph completion. They change presentation only, do not add model calls or routes, and are not saved practice attempts. The optional affect check-in is self-reported, never inferred from prose.

Do not add audience-specific agents without new educational and architectural justification. Acknowledge the latency, state overhead, and failure points of two agents and bounded repairs.

### State and Routing Contract

The authoritative schema is `langgraph_core/state.py`.

- `routing_decision`: `ask_clarification`, `support_agent`, `teacher_review`, or `direct_response`.
- Router checks `flag_teacher` first, then the enum. Missing/malformed decisions fall back to `ask_clarification`, never `support_agent`.
- `needs_feedback` and `needs_practice` are Support Agent inputs only.
- V2 adds `affect_check_in`, `revision_need`, and `coordinator_repair_count`; `priority_index` links pregenerated exercises to learner choices.
- Inputs and metadata are initialized together. Each node returns only fields it owns; downstream nodes use `state.get()` for branch outputs.
- Optional UI text is `""`; branch outputs use `NotRequired`.
- Replacement lists, not additive reducers, prevent duplicate history/log entries when an interrupted node replays.
- `coordinator_reasoning` is concise final JSON rationale, never hidden chain-of-thought.
- Keep V1/V2 prompts separate in `agents/prompts.py`. Debug logs retain all responses for successful repairs, and `api_calls` counts actual model calls.

V2 progressive disclosure generates all choices, scaffolds, and requested exercises in one Support call and reveals only the selected content. Clarification resume is a separate intentional loop. Each V2 agent invocation permits one bounded repair; persistent Support failure produces no partial feedback.

## Storage, UI, and Versioning

- SQLite stores both graph checkpoints and persistent run history locally and on Streamlit Cloud.
- Random session IDs in URLs filter history and support pending-run recovery. This is not authentication or secure isolation; anyone with the URL can access the view.
- Data is retained until **Delete my data** or cloud filesystem replacement. No automatic retention period is applied.
- The dashboard includes controls, input/output, fixture loading, route/rationale, timeline, state changes, timing, debug panels, graph visualization, persistent history, and V2 learner-choice controls.
- Prompt/raw-response capture and display require server-side `ENABLE_DEBUG_MODE=true`; capture is separately opt-in for new runs. Raw prompt/response fields are omitted from state and log views unless prompt display is enabled. Student and teacher outputs remain separate.
- V1 is preserved at commit `4eaa0ad` under annotated tag `v1`. Deploy only the active V2 version; use saved runs and screenshots rather than a runtime version selector.

## Testing and Evidence Strategy

Use the frozen files unchanged:

| Fixture | Expected behavior |
| --- | --- |
| `normal_case.txt` | Support Agent; encouraging feedback, 2-3 priorities, and practice when a gap warrants it |
| `incomplete_case.txt` | Specific clarification, no premature feedback, exact checkpoint resume after an answer |
| `boundary_case_a.txt` | Direct teacher review, separate supportive student and evidence-based teacher messages, no critique |
| `boundary_case_b.txt` | Teacher review for revision frustration, effort acknowledgment, human follow-up, no harsh judgment |

Boundary A is the official third syllabus case; Boundary B is additional. Empty input is rejected locally. Every nonempty submission goes to the coordinator so safety precedes short/non-writing clarification rules. Near-perfect writing uses direct response only when no actionable issues exist; otherwise it receives affirming support without forced criticism.

For official comparisons:

- Use byte-identical extracted fixture writing and metadata in V1 and V2.
- Official V1 used non-thinking mode at temperature 0 after a real smoke comparison. Keep that configuration fixed for V2 and deployment. Thinking ignores temperature; temperature 0 never guarantees identical output.
- Record actual routing, concise rationale, outputs, timing, screenshots, and errors. Distinguish observations from expected behavior.
- Build V1 as a genuine best effort. Identify 2-3 real problems in V1 testing and base V2 on them. Never script failures, reactions, JeepyTA feedback, or before-and-after evidence.
- Automated tests use mocked model responses and temporary SQLite databases. Real fixture runs are separate evidence, not interchangeable with unit tests.

## Configuration and Deployment

`.env.example` defines `DEEPSEEK_API_KEY`, `DEEPSEEK_API_BASE` (`https://api.deepseek.com`), `DEEPSEEK_MODEL`, `DEEPSEEK_THINKING`, `APP_VERSION`, `LOG_LEVEL`, `ENABLE_DEBUG_MODE`, and `DATABASE_PATH`.

The active post-JeepyTA V2 app is deployed on Streamlit Cloud at `https://writingassist-zhuang.streamlit.app` from `main` commit `7d94b58`, using Python 3.12 and secrets configured in Streamlit Cloud. After an authorized reboot, the public app and required normal, incomplete/resume, and Boundary A scenarios were verified in Chrome on 2026-11-03. Normal and incomplete practice displayed no **Brief example** or complete worked answer. Evidence is in git-ignored `data/evidence/deployed_v2_post_jeepyta_verification_20261103.json` and three deployment captures. Cloud SQLite durability ends when the filesystem is replaced. Future revisions must be pushed and retested before presenting them as deployed behavior.

For submission, review JeepyTA feedback with judgment before finalizing V2, submit the JeepyTA assignment link on Canvas, and include all eight syllabus items in one document, including application access and an AI Use Acknowledgment.

## Privacy, Safety, and Security

- Use only synthetic writing. Never use real student essays.
- UI warning: "Do not submit writing containing real names, schools, or personal information. This is a demo system — your input is sent to an external AI service."
- DeepSeek prompts may contain writing, grade level, assignment context, concerns, optional affect self-reports, clarification history, and coordinator handoff fields. V2 Support also receives clarification history. SQLite stores inputs, outputs, routes, execution details, and checkpoints.
- Removing names does not necessarily de-identify prose. Redact submission artifacts.
- Never commit API keys, `.env`, Streamlit secrets, databases, confidential educational data, or personally identifying information.
- Teacher handoff is simulated; no teacher is notified. Recommend showing concerning writing to a teacher or trusted adult instead.
- Do not improvise keyword-only crisis detection, crisis language, or hotline numbers. Production protocols and resources must be institution-approved, current, and localized.
- COPPA/FERPA compliance, parental consent, production retention/de-identification, authentication, and a real review queue are outside this demo's scope.
