# Code Review — Writing Assistant (V2)

**Reviewed:** `main` branch (working tree, unstaged changes relative to `v1` tag)  
**Date:** 2026-11-02  
**Scope:** Full codebase — agents, graph, storage, UI, tests

---

## Summary

The codebase is well-structured for its purpose. The separation between the LangGraph
graph layer, agent logic, and Streamlit UI is clean. The V1→V2 migration is disciplined:
prompts and output schemas are versioned independently, the repair-call contract is
explicit, and tests use mocked model calls with byte-stable payloads. The findings below
are mostly medium-to-low severity; the one correctness bug (item 1) and the two
user-facing issues (items 3 and 8) are the highest priority.

---

## Findings

### 1. UX bug — "light-touch response" label shown on standard-support runs

**File:** `ui/components.py:111-113`  
**Severity:** Medium (wrong user-facing text)

When a V2 standard-support run has `needs_practice=False`, every priority's `practice`
field is `None`. After the user selects a focus, `_render_v2_support` falls through to:

```python
st.info(
    "You can revise on your own with this one suggestion. No practice exercise "
    "is needed for this light-touch response."
)
```

The string "light-touch response" is incorrect for a standard-support run where practice
was simply not requested. The test suite (`test_v2_light_touch_returns_one_optional_priority_without_practice`)
only exercises the light-touch path; a standard-support run with `needs_practice=False`
would trigger this same message under a different (wrong) label.

**Fix:** Guard on `revision_need` rather than the presence of `practice`:

```python
if practice is None:
    revision = state.get("revision_need", "standard")
    msg = (
        "You can revise on your own using this suggestion. "
        "No practice exercise is included for this focus."
        if revision == "standard"
        else "You can revise on your own with this one suggestion. "
             "No practice exercise is needed for this light-touch response."
    )
    st.info(msg)
    return
```

---

### 2. No maximum writing length validation

**File:** `agents/utils.py:146-149`  
**Severity:** Medium (silent failure path)

`validate_writing_input` only rejects blank submissions. A student could paste an
arbitrarily long text. The DeepSeek API will return an error (or silently truncate,
depending on the model) once the combined prompt exceeds the model's context limit.
That error surfaces as a generic `APIError` with no explanation.

**Fix:** Add a character ceiling with a clear user-facing message:

```python
MAX_WRITING_CHARS = 8_000  # ~2000 tokens; adjust to model context budget

def validate_writing_input(writing: str) -> str:
    if not writing.strip():
        raise InputValidationError("Enter some writing before starting an analysis.")
    if len(writing) > MAX_WRITING_CHARS:
        raise InputValidationError(
            f"The submission is too long ({len(writing):,} characters). "
            f"Please paste no more than {MAX_WRITING_CHARS:,} characters at a time."
        )
    return writing
```

---

### 3. `ResponseValidationError` detail leaked to students

**File:** `ui/layout.py:79`  
**Severity:** Medium (inappropriate audience)

```python
st.error(f"The AI returned an incomplete response: {error}")
```

`ResponseValidationError` messages contain internal schema language such as
`"Light-touch support must contain exactly one revision priority."` These details are
meaningless to a 5th-grader and undermine the demo's polish.

**Fix:** Show a fixed generic message to students; log the detail separately:

```python
elif isinstance(error, ResponseValidationError):
    st.error("The feedback could not be completed. Please try the analysis again.")
    if os.getenv("ENABLE_DEBUG_MODE", "false").lower() == "true":
        st.caption(f"Debug: {error}")
```

---

### 4. Session ID validation silently drops user history

**File:** `ui/layout.py:26-36`  
**Severity:** Medium (data loss without feedback)

`_session_id()` validates the `session_id` URL parameter with `uuid.UUID(value)`. If the
value is malformed (e.g. truncated URL, stale bookmark), `ValueError` is caught silently
and a brand-new session ID is generated. The user's prior run history becomes invisible
without any warning.

`uuid4().hex` generates a 32-char hex string without hyphens, which `uuid.UUID()` does
accept, so the round-trip is actually fine for machine-generated IDs. The risk is with
human-edited or copied URLs.

**Fix:** Show a one-time warning when falling back to a new session:

```python
value = st.query_params.get("session_id")
if isinstance(value, str):
    try:
        uuid.UUID(value)
        return value
    except ValueError:
        st.warning(
            "The session ID in the URL was not recognised. "
            "A new session has been started and prior history is not visible."
        )
value = uuid.uuid4().hex
st.query_params["session_id"] = value
return value
```

---

### 5. `parse_json_object` does not handle uppercase fence

**File:** `agents/utils.py:131-143`  
**Severity:** Low (edge case in fence stripping)

The function strips ` ```json ``` ` and ` ``` ``` ` fences but not ` ```JSON ``` ` or
` ```Json ``` `. Since `json_mode=True` is always used, the model rarely adds fences at
all, and the JSON mode makes this a belt-and-suspenders guard. Still, if it fires, the
fallback `json.loads` will likely succeed anyway (because the raw content would be pure
JSON), so the real risk is minimal.

**Fix (optional):**
```python
if stripped.lower().startswith("```json") and stripped.endswith("```"):
    stripped = stripped[stripped.index("\n") + 1:-3].strip()
elif stripped.startswith("```") and stripped.endswith("```"):
    stripped = stripped[3:-3].strip()
```

---

### 6. Inconsistent treatment of oversized model lists

**File:** `agents/assessment_coordinator.py:47-52`  
**Severity:** Low (silent truncation vs. hard error)

`AssessmentOutput` silently truncates `strengths` to three entries in the
`check_route_details` validator (`self.strengths = self.strengths[:3]`), but enforces
`Field(max_length=5)` on `issues` and `skill_gaps` — causing a hard `ValidationError`
(and triggering a repair call in V2) if the model returns six issues.

This asymmetry is intentional and tested, but it is undocumented. If a future author
adds a field and wonders why strengths behaves differently, the reason is not obvious.

**Fix:** Add a comment explaining the deliberate design:

```python
@model_validator(mode="after")
def check_route_details(self):
    # Silently cap strengths rather than failing: a valid assessment with four
    # strengths should not trigger a repair call. issues/skill_gaps use
    # Field(max_length=5) so the model sees a hard Pydantic error instead.
    self.strengths = self.strengths[:3]
    ...
```

---

### 7. `SQLiteStorage` opens a new connection per operation

**File:** `storage/sqlite_storage.py:41-46`  
**Severity:** Low (performance, not correctness)

`_connect()` opens a fresh `sqlite3.Connection` on every call. For a single-user demo
served by Streamlit this is imperceptible, but each call pays the overhead of
`PRAGMA journal_mode=WAL` and `PRAGMA busy_timeout=30000` on every read or write.

The separate persistent connection used by `SqliteSaver` (checkpointer) in
`langgraph_core/graph.py:153-156` already holds WAL mode open; the storage connections
don't need to reissue the pragma every time.

**Fix (optional):** Cache the pragma call or hold a module-level connection with
`check_same_thread=False` for the storage layer, matching the pattern already used for
the checkpointer.

---

### 8. Debug mode exposes raw prompts and model responses to any user

**File:** `ui/layout.py:261-271`  
**Severity:** Low-Medium (information disclosure in shared demo)

The "Capture prompts/responses on new runs" and "Show captured prompts/responses"
checkboxes are always visible in the sidebar. On Streamlit Cloud, the URL is shareable
and session isolation is explicitly noted as not being secure. Any visitor can enable
debug mode on an existing session and read the raw DeepSeek prompts (which embed the
student's submitted writing and coordinator evidence) from stored execution logs.

Since this is a demo with synthetic writing only and the privacy warning is displayed,
the risk is contained. But the checkboxes could reasonably be hidden behind
`ENABLE_DEBUG_MODE`:

```python
if os.getenv("ENABLE_DEBUG_MODE", "false").lower() == "true":
    st.sidebar.checkbox("Capture prompts/responses on new runs", ...)
    options["show_prompts"] = st.sidebar.checkbox(...)
else:
    options["show_prompts"] = False
```

---

### 9. `AssessmentOutputV2` validator runs after parent validator

**File:** `agents/assessment_coordinator.py:55-67`  
**Severity:** Low (ordering subtlety, no current bug)

`AssessmentOutputV2` inherits `AssessmentOutput` and adds its own `@model_validator`.
Pydantic v2 runs parent validators before child validators (`mode="after"` validators
run in MRO order). The parent's `check_route_details` truncates `self.strengths` and
checks for a clarification question. The child's `check_revision_need` checks
`len(self.issues)`. Because the parent already ran, `issues` has been validated (via
`Field(max_length=5)`) before the child's length check. This ordering is correct but
could silently break if the parent validator were to mutate `issues` in a future change.

**Note:** No fix required today; just be aware when modifying either validator.

---

### 10. Missing test cases

**Files:** `tests/`  
**Severity:** Low

The following paths are not covered by the current 61-check suite:

| Path | Location |
|---|---|
| `make_initial_state` rejects invalid grade level | `langgraph_core/state.py:80` |
| `make_initial_state` rejects invalid affect value | `langgraph_core/state.py:82` |
| `load_fixture` with an unknown fixture name | `ui/components.py:27` |
| `_safety_fallback` with missing/invalid `teacher_flag_reason` | `agents/assessment_coordinator.py:157-162` |
| `route_from_assessment` with `flag_teacher=True` AND a valid non-teacher route | `langgraph_core/routing.py:13` |
| V2 standard-support run where `needs_practice=False` (all practices None) | `agents/support_agent.py:169-174` |
| `delete_session` with zero threads | `storage/sqlite_storage.py:159` |
| Affect check-in `frustrated` reaching `teacher_review` via boundary-B fixture | end-to-end |

The routing-override test is especially worth adding since it guards the safety contract:

```python
def test_teacher_flag_overrides_valid_support_route():
    state = {
        "routing_decision": "support_agent",
        "flag_teacher": True,
    }
    assert route_from_assessment(state) == "teacher_review"
```

---

## What works well

- **Safety-first routing contract.** `flag_teacher` always wins in `route_from_assessment`
  and is re-checked in `_normalize`. The `_safety_fallback` preserves teacher-flag data
  even when other schema fields are malformed. This layered defence is robust.

- **Repair-call discipline.** Both agents implement exactly one bounded repair call with
  the validation error forwarded to the model. Debug logs record actual `api_calls` counts
  and retain both raw responses on success. The CLAUDE.md contract is faithfully implemented.

- **Clarification history management.** Replacing lists rather than appending avoids
  LangGraph checkpoint replay duplicating entries. The two-answer stopping limit is
  enforced in the graph node, not in the coordinator, keeping routing logic centralised.

- **Test structure.** Mocked model clients are deterministic and composable. The
  `coordinator_payload`/`support_payload` helpers keep test data consistent and readable.
  End-to-end graph tests use `tmp_path` SQLite databases and verify both the returned
  state and the stored `RunRecord`.

- **V1/V2 separation.** Prompts, output schemas (`AssessmentOutput` vs
  `AssessmentOutputV2`), and support payloads are cleanly versioned. V1 behaviour is
  preserved under the `v1` git tag.

- **Storage durability.** WAL mode, `busy_timeout=30000`, and the cumulative
  `duration_ms + ?` pattern handle multi-step resumed runs correctly.
