# UI/UX Review: Writing Coach V3

Audience: grades 5–7 (ages 10–13). Based on a full read of `app.py`, `ui/layout.py`, `ui/editor.py`, `ui/components.py`, `ui/observability.py`, and `mockups/v3_iterative_revision.html`.

---

## What the mockup got right that the live app doesn't fully deliver

The HTML mockup is a noticeably stronger design than what the Streamlit app currently renders. Key gaps:

- The mockup puts the step nav **in the header**, right-aligned beside the brand. The Streamlit app renders steps as four equal full-width buttons across the content area, making them feel like primary actions competing with the actual work.
- The mockup uses two distinct panes — essay left, feedback right — that scroll independently. The live workspace does this via columns, but the CSS marker hacks (`workspace-marker`, `draft-layout-marker`) are fragile and don't faithfully reproduce the layout on all screen sizes.
- The mockup has a clear visual hierarchy for goal cards: bold title → example quote in italic serif → plain explanation → hint toggle. The live `_render_candidate` outputs a flat stack of `st.markdown` calls with no visual grouping.

---

## Audience-critical issues

### 1. Cognitive load on the Draft screen

The "Add assignment details" expander hides 7 optional fields — framework name, components, genre, source, teacher directions, etc. The labels are written for a teacher or developer, not a student:

- "Framework name (optional)" — a 6th-grader doesn't know what a framework is in this context
- "Required components (optional, comma-separated)" — confusing for most adults too
- "Student concern or goal (optional)" — fine, but buried

**Recommendation:** rename the expander to something like "My assignment has extra info" and rewrite each label plainly:

| Current label | Student-facing label |
|---|---|
| Framework name | My teacher asked me to use a structure (like CER or RACES) |
| Required components | The parts my structure requires |
| Student concern or goal | What I want help with |

Consider replacing the framework text input with a small radio group for the common structures (CER, RACES, MEAL) plus an "other" option.

### 2. Privacy warning uses the wrong visual weight

`st.warning(...)` renders a yellow banner immediately above the submit button. For a student this reads as an error or a scare — something is wrong before they even start. The content is correct and required, but the warning color is the wrong choice. It should be a small gray caption styled as a matter-of-fact notice.

**Recommendation:**

```python
# replace
st.warning("Do not submit writing containing real names…")

# with
st.markdown(
    '<p class="v3-privacy-note">'
    '🔒 Don\'t include real names, schools, or personal info. '
    'Your draft is sent to an AI service for feedback.'
    '</p>',
    unsafe_allow_html=True
)
```

Style `.v3-privacy-note` as `font-size: 12px; color: #64748b; margin: 12px 0;`.

### 3. Goal card density overwhelms the feedback panel

Each goal in `_render_candidate` renders:

1. Checkbox + bold title
2. `why_it_matters` paragraph
3. Caption: paragraph number, occurrence, reference quote
4. "Try this:" action paragraph
5. "Show a hint" expander
6. Divider

That's up to 18 stacked items for three goals before any scrolling. For a 5th-grader this is too much to process at once.

The mockup handles this better by wrapping each goal in a card container so all its content reads as one unit. The `example-quote` treatment (left-border, italic serif) makes the located passage visually distinct from the instruction.

**Recommendation:** wrap each goal in a styled card and treat the quote distinctly:

```css
.v3-goal-card {
  padding: 14px 16px;
  border: 1px solid #dbe3ec;
  border-radius: 11px;
  background: #fff;
  margin-bottom: 12px;
}
.v3-goal-card.selected {
  border-color: #9db2ee;
  background: #f8faff;
}
.v3-goal-quote {
  padding-left: 10px;
  border-left: 3px solid #d7def0;
  color: #596780;
  font-family: Georgia, serif;
  font-style: italic;
  font-size: 14px;
  margin: 8px 0;
}
```

Then in `_render_candidate`, wrap the content block:

```python
st.markdown('<div class="v3-goal-card">', unsafe_allow_html=True)
# ... existing content ...
st.markdown('</div>', unsafe_allow_html=True)
```

### 4. Step navigation has no completed state

The current step nav uses Streamlit's `type="primary"` for active and `type="secondary"` for everything else. There's no completed state — once you're on Revise, the Draft and Choose buttons look the same as they did before you used them. The mockup's `.step.complete` applies a green number circle. That matters for students: they need to feel progress, not just position.

**Recommendation:** inject a CSS class or inline style on completed steps. The simplest approach is a hidden `aria-current="step"` already in the code — extend it with a completed marker:

```css
/* target the step button for a completed step via data attribute */
[data-step-complete="true"] {
  color: #176b4d;
}
[data-step-complete="true"] .step-number-circle {
  color: #176b4d;
  background: #eaf7f1;
  border-color: #a8d9c5;
}
```

### 5. Self-report language is too formal for students

```python
["No answer", "I tried this goal", "I intentionally deferred this goal"]
```

"Intentionally deferred" is not how a 12-year-old thinks or talks about their own work.

**Recommendation:**

```python
["Skip (no answer)", "I tried this", "I decided to skip this for now"]
```

### 6. Developer controls are visible to students by default

The header at `layout.py:1316` renders five columns: title, New composition, History, **Show Developer Controls**, **Show Agent Observability**. Students see these as normal navigation. "Agent Observability" means nothing to a 10-year-old, and clicking it reveals timing data, token counts, and a LangGraph diagram.

**Recommendation:** gate these buttons on `ENABLE_DEBUG_MODE`:

```python
# layout.py — render_dashboard
title_column, new_column, history_column = st.columns([2.5, 0.9, 0.9])
# ... render title, new, history ...

if _debug_enabled():
    developer_column, observability_column = st.columns([1.4, 1.4])
    # ... render developer and observability toggles ...
```

This keeps the student-facing header clean without removing any functionality for developers.

### 7. Font mismatch between editor and feedback

The CCv2 editor uses `Georgia, 'Times New Roman', serif` at 17px/1.7 line height — a deliberate "essay paper" feel. All surrounding Streamlit UI uses the default system sans-serif at a smaller size. The goal card labels and the essay text sit in different typographic worlds.

The mismatch isn't a problem in the editor itself, but feedback copy (goal titles, `why_it_matters` text, hint content) should feel connected to the same reading experience rather than switching registers. Consider setting the feedback panel text to 14–15px with 1.6 line height, slightly larger than Streamlit's default 14px captions, to close the perceived gap.

---

## Structural recommendations

### Move step navigation into the header

Right now `_render_steps` outputs 4 buttons, then the main content flows below. The steps compete visually with page content and push everything down by roughly 60px on every screen.

The mockup puts steps in the header:

```
┌──────────────────────────────────────────────────────────────┐
│  [W] Writing Coach                 1 Draft  2 Choose  3 …   │
│      Your ideas. Your words.                                  │
└──────────────────────────────────────────────────────────────┘
```

In Streamlit this is achievable by rendering the step row inside the existing 5-column title row rather than as a separate row below it:

```python
title_col, steps_col, new_col, history_col = st.columns([1.5, 3, 0.9, 0.9])
title_col.title("Writing Coach")
with steps_col:
    _render_steps(service)
```

### Reflection screen: read-only snapshots should read as snapshots

The side-by-side `st.text_area(disabled=True)` layout works structurally, but students may try to edit them — a disabled textarea still looks editable. A simple visual treatment makes the intent clear:

```css
.v3-snapshot-pane {
  padding: 18px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  font-family: Georgia, serif;
  font-size: 15px;
  line-height: 1.72;
  color: #334155;
  white-space: pre-wrap;
  overflow-y: auto;
  height: 360px;
}
```

Then replace:

```python
st.text_area("Original submitted draft", original.writing, height=360, disabled=True, …)
```

With:

```python
st.markdown(
    f'<div class="v3-snapshot-pane">{original.writing}</div>',
    unsafe_allow_html=True
)
```

---

## Streamlit theme configuration

The highest-value single change is setting the theme in `.streamlit/config.toml`. This makes all native Streamlit components — buttons, inputs, selectboxes — use the brand blue from the mockup instead of Streamlit's default indigo, with no Python changes required:

```toml
[theme]
primaryColor = "#3157c8"
backgroundColor = "#f5f7fb"
secondaryBackgroundColor = "#ffffff"
textColor = "#1f2937"
font = "sans serif"
```

The existing palette in the mockup is well-suited for this audience — not childish, not corporate gray:

| Token | Value | Role |
|---|---|---|
| Brand blue | `#3157c8` | Primary actions, focus rings, selected state |
| Brand dark | `#2445a5` | Hover states |
| Brand soft | `#edf2ff` | Selected card backgrounds |
| Success green | `#176b4d` | Completed steps, confirmed feedback |
| Amber warning | `#805600` | Source limitations, genuine cautions |
| Background | `#f5f7fb` | Page surface |
| Ink | `#1f2937` | Body text |

---

## Priority order

| Priority | Change | Effort |
|---|---|---|
| 1 | Add `.streamlit/config.toml` with theme tokens | 5 min |
| 2 | Gate developer/observability controls behind `ENABLE_DEBUG_MODE` | 15 min |
| 3 | Rewrite student-facing labels in the assignment details expander | 20 min |
| 4 | Replace `st.warning` privacy banner with styled caption | 10 min |
| 5 | Add goal card CSS wrapper in `_render_candidate` | 30 min |
| 6 | Update self-report option labels | 5 min |
| 7 | Move step nav into header row | 45 min |
| 8 | Replace disabled `st.text_area` in reflection with styled div | 20 min |

Items 1–4 are low-risk, no-logic changes. Items 5–8 are purely visual and don't touch any state or agent logic.
