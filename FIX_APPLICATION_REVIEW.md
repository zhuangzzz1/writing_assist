# Assessment of Applied Fixes

## Overall Assessment

The other LLM made **substantial improvements**, but its summary overstates the result. The claims that **“all fixes applied,” “internally consistent,” and “free of integrity and design problems” are not supported by the actual files**.

Several changes are genuinely complete: the date and model identifier were corrected, Python was bumped to 3.11+, the eight submission items were added, V1 is generally framed as a genuine effort, progressive disclosure replaced most multi-turn language, and privacy guidance was added.

However, important issues remain.

## Remaining Issues

### 1. The Router and State Schema Still Directly Contradict Each Other

`PRD.md:227-254` says `routing_decision` is the authoritative routing signal and that `needs_feedback`/`needs_practice` are never used by the router. But the actual router:

- Never reads `routing_decision`.
- Routes using `needs_feedback` and `needs_practice` (`PRD.md:182-202`).
- Continues to rely on several potentially conflicting booleans.

`CLAUDE.md:41-43` repeats the claim that routing uses only the enum, so it now describes behavior that the PRD code does not implement.

The “malformed state” fallback is also incomplete: direct lookups such as `state["flag_teacher"]` can raise `KeyError` before reaching the fallback.

**Required fix:** Choose one routing contract and use it consistently in the schema, router, and all three documents. Validate malformed output before accessing fields.

### 2. The Referenced Frozen Fixture Files Do Not Exist

There is currently no `test_cases/` directory. Nevertheless:

- `project_plan.md:131-145` references four fixture files.
- `PRD.md:628` and `PRD.md:676` label inputs as frozen files.
- `PRD.md:394-396` states that fixtures “are frozen” and “committed to git.”

The boundary-case prose does exist inline, which is useful, but the external files do not. The normal case also remains an LLM-generated placeholder (`PRD.md:543-551`), so not all test inputs are fixed.

There is also a naming mismatch: the project structure lists `boundary_case.txt`, while the scenarios reference `boundary_case_a.txt` and `boundary_case_b.txt` (`PRD.md:842-847`).

**Required fix:** Either create and reference the actual fixtures or describe fixture creation as a pending task. Select one boundary scenario as the official third assignment case; the other can be an additional test.

### 3. The Simulated Teacher Handoff Still Makes a False Promise

The student-facing message says:

> “A teacher will look at this before we continue” (`PRD.md:652-661`).

But the system only simulates teacher review; no teacher is notified. A success criterion requiring a “simulated” label does not make that statement truthful.

**Required fix:** Use language such as “I recommend showing this to a teacher or trusted adult,” while separately explaining that the demonstrated handoff is simulated.

### 4. An Untested Performance Claim Was Reintroduced

`PRD.md:275-276` says separate agents “produced more consistent and debuggable behaviour in practice.” No implementation or comparative testing exists. This recreates the same evidence problem the edits were supposed to remove.

**Required fix:** Phrase this as an expected benefit or hypothesis, then replace it with observed evidence after testing.

### 5. Old Staged-Response Language Remains in `project_plan.md`

`project_plan.md:197-200` still lists:

- “Split Support Agent into staged responses”
- “Made clarification behavior specific rather than generic”

These are presented as the two revisions for Part 5. That conflicts with both progressive disclosure and the requirement to base revisions on observed V1 problems.

**Required fix:** Replace these with placeholders for two actual revisions selected after V1 testing.

### 6. The Scope-Reduction Fix Was Largely Not Applied

Despite `CORRECTED_FIX_LIST.md:190-203`:

- Storage remains “Must Have” (`PRD.md:350-362`).
- SQLite is still scheduled for Day 1–2 (`PRD.md:1002-1007`).
- Advanced observability and visualization remain V1 must-haves (`PRD.md:327-348`).
- The three-column dashboard and highlighted graph remain mandatory in `CLAUDE.md:92-105`.

Storage is simultaneously mandatory and called a “Nice-to-have feature” at `PRD.md:1163-1169`.

**Required fix:** Actually apply the proposed must/should/nice-to-have tiers, especially given the November 3 deadline.

### 7. Document-Control Cleanup Is Incomplete

- Success metrics still have achievement checkmarks instead of being labeled targets (`PRD.md:23-28`).
- Rubric criteria are similarly pre-checked as though already satisfied (`PRD.md:1067-1098`).
- There are two contradictory `Approval` sections. One leaves timeline validation unchecked; the other checks it (`PRD.md:1284-1294`).

These directly contradict the corrected fix list’s instructions.

### 8. A Smaller Typing Error Remains

`PRD.md:214-215` declares `NotRequired[str]` while commenting “may be None.” Those are different concepts: `NotRequired` permits an omitted key, while `str | None` permits a present key with a `None` value. If the UI supplies `None`, the annotation should reflect that.

## Verdict on the Supplied Summary

- **Textual replacements and several structural improvements:** Mostly accurate.
- **“All fixes applied”:** False.
- **“Internally consistent”:** False, principally because of the router, fixtures, scope, and leftover Part 5 text.
- **“Free of integrity and design problems”:** False because of the untested performance claim and simulated teacher-review promise.
- **“Ready to start Day 1”:** Premature. The foundational routing contract and document inconsistencies should be corrected first.

The corrected fix list itself is generally sound; the main problem is that it was **incompletely and sometimes inconsistently applied**.
