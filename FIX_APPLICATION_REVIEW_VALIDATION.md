# Fix Application Review — Validation

**Date**: 2026-11-01

## Verdict

All 8 remaining issues identified in `FIX_APPLICATION_REVIEW.md` are **valid**. The earlier "all fixes applied / internally consistent" claim was overstated. The corrected fix list was sound but incompletely and inconsistently applied.

## Issue Validation

### 1. Router and State Schema Contradict Each Other — VALID
The schema declares `routing_decision` authoritative and says `needs_feedback`/`needs_practice` are never read by the router, but the actual router reads `needs_feedback`/`needs_practice` and never reads `routing_decision`. Direct lookups can also raise `KeyError` before the fallback. Real contradiction.

### 2. Frozen Fixture Files Do Not Exist — VALID
Confirmed: no `test_cases/` directory exists. PRD references frozen, committed fixtures that don't exist. Normal case is still an LLM-generated placeholder. Naming mismatch: `boundary_case.txt` vs `boundary_case_a.txt`/`boundary_case_b.txt`.

### 3. Simulated Teacher Handoff Makes False Promise — VALID
"A teacher will look at this before we continue" promises a handoff that doesn't occur. A "simulated" label elsewhere doesn't make this student-facing statement truthful.

### 4. Untested Performance Claim Reintroduced — VALID
"Produced more consistent and debuggable behaviour in practice" with no implementation. Recreates the evidence problem the edits were meant to remove.

### 5. Old Staged-Response Language Remains in project_plan.md — VALID
Part 5 still lists predetermined revisions ("Split Support Agent into staged responses"), conflicting with progressive disclosure and observed-problem requirement.

### 6. Scope-Reduction Fix Largely Not Applied — VALID
Storage is "Must Have" (5.2) and simultaneously "Nice-to-have" (Risk 4). SQLite in Day 1-2. Advanced observability mandatory. Must/should/nice-to-have tiers never actually applied.

### 7. Document-Control Cleanup Incomplete — VALID
Success metrics and rubric criteria use ✅ as if satisfied. Two contradictory Approval sections exist.

### 8. Typing Error — VALID
`NotRequired[str]` with comment "may be None" conflates omitted keys with None values.

## Fixes Applied

See the edits following this report.
