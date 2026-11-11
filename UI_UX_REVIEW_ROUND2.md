# UI/UX Review: Writing Coach V3 — Round 2

Based on uncommitted changes to `ui/layout.py` and `ui/editor.py`, compared against the Round 1 review recommendations.

---

## What was addressed

### ✓ Developer controls gated behind env var

The header now branches on `_evaluation_controls_enabled()` (the new `SHOW_EVALUATION_CONTROLS` env flag). When the flag is off, `developer_controls_visible` and `agent_observability_visible` are force-reset to `False` and the toggle buttons are not rendered at all. This was priority 2 in Round 1 and is now cleanly done.

One note: the guard uses `_evaluation_controls_enabled()` rather than `_debug_enabled()`. That means a developer who sets `ENABLE_DEBUG_MODE=true` but forgets `SHOW_EVALUATION_CONTROLS=true` won't see the debug toggles. The two flags are now coupled in a non-obvious way. Consider whether these should be the same flag, or at least document the dependency clearly in `.env.example`.

### ✓ Self-report labels rewritten

```python
GOAL_SELF_REPORT_VALUES = ("", "attempted", "deferred")
GOAL_SELF_REPORT_LABELS = {
    "": "No answer",
    "attempted": "I tried this",
    "deferred": "I decided to skip this for now",
}
```

"I intentionally deferred this goal" is gone. This is correct. The selectbox now uses `format_func=GOAL_SELF_REPORT_LABELS.get` so internal values remain stable storage keys. The history view also picks up the new labels via `GOAL_SELF_REPORT_LABELS.get(report, report)`. Good catch to update both display sites.

### ✓ Assignment details expander relabelled

All seven field labels are now student-facing:
- "Writing type (optional)" instead of "Genre"
- "Assignment question (optional)" instead of "Assignment prompt"
- "My teacher's directions or required structure" instead of "Teacher directions or required structure"
- "Writing structure my teacher asked for" instead of "Framework name"
- "Parts my structure must include" instead of "Required components"
- "Passage or source my assignment uses" instead of "Source material"
- "What I want help with" instead of "Student concern or goal"

The expander now also opens with a plain caption: "Add information from your teacher or tell me what you want help with." That sets context before the student sees the fields.

One gap remaining: the expander label itself is still "Add assignment details". From the outside this reads like a form for teachers. "My assignment has extra info" or "Add details from my teacher" would match the student-facing language inside.

### ✓ Privacy notice converted from warning banner

The `st.warning(...)` is replaced with a styled `<div class="v3-privacy-note">` with a left border, soft background, and muted text. It includes `role="note"` and `aria-label` — good accessibility call. The visual weight is now appropriate: informational, not alarming.

Minor: the text still reads "Do not submit writing containing real names, schools, or personal information." The imperative "Do not" is slightly stern. The mockup from Round 1 suggested the more direct: "Don't include real names, schools, or personal info." Either works, but consistency with the student-facing voice elsewhere would be cleaner.

### ✓ Goal cards wrapped in `st.container(border=True)`

`_render_candidate` now wraps each goal in `with st.container(border=True):`. The `.v3-goal-card-marker` and `.v3-goal-card-selected` CSS classes visually distinguish selected cards (blue-tinted border and background). The paragraph number caption is simplified to "Paragraph N, matching passage N" — cleaner than the previous "Paragraph N, occurrence N".

The draft reference quote is now a `<blockquote class="v3-goal-quote">` with `.v3-goal-quote` styling: left border, italic serif, appropriate contrast. This directly matches the mockup's `.example-quote` treatment. Well done.

The divider between goal cards is gone — the card container provides the separation now. That's the right call.

### ✓ Step nav shows completed state

Steps now show `✓` in place of the number when complete, using this logic:

```python
completed = {
    "Draft": bool(snapshots),
    "Choose": has_selection or any(snapshot.selected_goals for snapshot in snapshots),
    "Revise": len(snapshots) > 1,
    "Reflect": final_complete,
}
```

The CSS targets `[data-testid="stColumn"]:has(.v3-step-complete-marker)` to apply green styling to completed step buttons. The `aria-current` region now also announces completed steps: "Current step: Revise. Completed steps: Draft, Choose." That's a meaningful accessibility improvement.

### ✓ Reflection screen uses styled snapshot panes

`_render_snapshot` replaces `st.text_area(disabled=True)`. The `.v3-snapshot-pane` div uses a soft background, serif font at 1rem/1.72 line height, and `tabindex="0"` so keyboard users can scroll it. Text is HTML-escaped via `html.escape()` before injection. The read-only intent is now visually clear.

### ✓ Editor height is now responsive

The editor height changed from a fixed `480px` to `clamp(360px, calc(100vh - 420px), 740px)`. This means the editor breathes with the viewport rather than leaving unused whitespace on tall screens or clipping on shorter ones. The CCv2 component `height` parameter also changed from a numeric `530` to `"content"`, which lets the component size itself from CSS.

### ✓ Step nav moved into header row

The header now uses a `steps_column` between the title and the action buttons:

```python
title_column, steps_column, new_column, history_column = st.columns([1.6, 3.4, 0.9, 0.9])
with steps_column:
    _render_steps(service)
```

`_render_steps` is no longer called in the main content flow. This was priority 7 in Round 1 and is the structurally most significant change. The header CSS (`.v3-header-marker`) applies `align-items: center` to the header row so the title, steps, and buttons sit on the same visual baseline.

---

## Remaining issues and new observations

### 1. No `.streamlit/config.toml` yet

The theme tokens recommended in Round 1 (`primaryColor = "#3157c8"`, etc.) are still absent. Without them, Streamlit's native components — text inputs, selectboxes, the default button focus ring — still use Streamlit's built-in indigo. The gap is most visible on the Draft screen where the grade level selectbox, the main textarea, and the assignment details inputs all render in Streamlit's default style while the custom CCv2 editor and goal cards look more polished.

This is still the highest-impact, lowest-effort change available. Five lines in a new file:

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#3157c8"
backgroundColor = "#f5f7fb"
secondaryBackgroundColor = "#ffffff"
textColor = "#1f2937"
font = "sans serif"
```

### 2. Expander label still reads as teacher-facing

As noted above: the expander is now labelled "Add assignment details". The student-facing language inside starts with "Add information from your teacher or tell me what you want help with." The label and the interior caption are pulling in slightly different directions. Suggested fix:

```python
with st.expander("Add details from my teacher (optional)", expanded=False):
```

### 3. Goal card CSS selector specificity is fragile

The CSS for goal card selection state relies on a deep `:has()` chain:

```css
[data-testid="stLayoutWrapper"]:has(
  > [data-testid="stVerticalBlock"]
  > [data-testid="stElementContainer"]
  .v3-goal-card-selected
)
```

This is a four-level `:has()` with direct child combinators targeting internal Streamlit testids. Streamlit does not guarantee the stability of `stLayoutWrapper`, `stVerticalBlock`, or `stElementContainer` across patch versions — a Streamlit upgrade could silently break the selected-card visual without any Python error. The `.v3-goal-card-marker` approach works, but the selector depth is risky.

A more resilient pattern would be to render the entire card as a single HTML block via `st.markdown(unsafe_allow_html=True)` rather than relying on CSS to reach inside a Streamlit container. That trades Streamlit-managed layout for more control over the card DOM.

### 4. The feedback panel font size rule is scoped too broadly

```css
[data-testid="stColumn"]:has(.v3-feedback-marker) [data-testid="stMarkdownContainer"] p,
[data-testid="stColumn"]:has(.v3-feedback-marker) [data-testid="stMarkdownContainer"] li {
  font-size: 1rem; line-height: 1.6;
}
```

This applies `1rem` to every paragraph inside the entire feedback column. That includes the goal card `why_it_matters` text, the hint content, the `revision_action`, and the goal feedback observations — all good. But it also catches the `st.caption()` calls (paragraph number, overlap note, stale highlight notice, process milestones), which are intentionally smaller. Those captions currently display at `1rem` even though the design intent of `st.caption` is to be visually secondary.

Consider scoping this rule to named content zones rather than the whole column, or exclude captions explicitly.

### 5. `v3-editor-panel-marker` / `v3-feedback-panel-marker` height overrides

```css
[data-testid="stLayoutWrapper"]:has(... .v3-editor-panel-marker) {
  height: clamp(480px, calc(100vh - 320px), 860px) !important;
  flex: 0 0 auto !important;
}
```

Using `!important` on height and flex on a Streamlit layout wrapper is likely to cause layout instability on smaller viewports or when content inside the panel grows taller than expected (e.g., many goal candidates, long goal text). If the feedback panel content overflows its clamped height, it will either clip or scroll inside a fixed-height flex item, depending on what the inner container does.

The workspace already uses `st.container(border=True, height=640)` for the editor and `height=510` for the feedback panel. Those fixed heights, combined with the clamped wrapper height above, could double-constrain the panels on small screens. It's worth checking this at 1024px wide and at 768px tall to confirm the panels don't stack or clip unexpectedly.

### 6. Word count in the Draft screen textarea is missing

The CCv2 editor shows a live word count in the editor status bar. The Draft screen's `st.text_area("Student draft", ...)` does not. A student writing from scratch on the Draft screen has no feedback on length. Even a simple caption updated on submission would help, though a live count matching the editor would be better.

### 7. "Show less feedback" / "I'm stuck" buttons have no visual grouping

In the Revise panel, these two buttons sit between the goal card list and the self-report section with no visual separation. They're secondary controls that modify display state, not actions on the student's work. They read as more prominent than they should be.

Suggestion: group them together in a single row of smaller ghost-style buttons, visually subordinate to the goal cards above and the submit actions below. This can be done with a horizontal flex container:

```python
col1, col2, _ = st.columns([1, 1, 2])
# render show_less / show_all in col1
# render I'm stuck in col2
```

### 8. Self-report caption still uses slightly formal language

The self-report section caption was updated to: "Share what you tried or decided to skip. If you do not answer, I will not assume whether you tried."

The second sentence ("If you do not answer, I will not assume whether you tried") is accurate but reads like a legal disclosure. For a 6th-grader it could just say: "This is optional. Skip it if you like." The first-person "I" referring to the AI also slightly breaks register — elsewhere the app doesn't address students in first person from the system itself.

---

## Summary

Six of eight Round 1 priorities are addressed. The changes are substantive and correct — the goal cards, step completion state, snapshot panes, privacy notice, label rewrites, and developer-control gating are all clear improvements. The header step nav reorganization is structurally the right move.

The two items still open from Round 1:

| # | Item | Status |
|---|---|---|
| 1 | `.streamlit/config.toml` theme tokens | Not yet done |
| 2 | Expander label ("Add assignment details") | Partially done — interior relabelled, outer label not yet |

New items surfaced in Round 2:

| Priority | Item | Effort |
|---|---|---|
| High | Add `.streamlit/config.toml` | 5 min |
| Medium | Fix expander outer label | 2 min |
| Medium | Self-report caption tone | 2 min |
| Medium | "Show less" / "I'm stuck" button grouping | 15 min |
| Low | Goal card selector fragility (deep `:has()`) | 30 min if refactored |
| Low | Feedback column font rule scope | 10 min |
| Low | Workspace panel height double-constraint | Needs testing first |
| Low | Word count on Draft screen textarea | 20 min |
