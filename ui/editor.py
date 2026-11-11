from typing import Any

import streamlit as st


_EDITOR = st.components.v2.component(
    "v3_goal_highlight_editor",
    html="""
<div class="editor-shell">
  <div class="editor-wrap">
    <div class="editor-highlights" aria-hidden="true"><pre id="highlight-content"></pre></div>
    <textarea id="essay-editor" aria-label="Editable essay draft" spellcheck="true"></textarea>
  </div>
  <div class="editor-status"><span id="draft-status">Unsubmitted edits stay in this workspace.</span><span id="word-count">0 words</span></div>
</div>
""",
    css="""
.editor-shell { width: 100%; }
.editor-wrap { position: relative; height: clamp(360px, calc(100vh - 460px), 740px); background: #ffffff; }
.editor-highlights { position: absolute; z-index: 1; inset: 0; overflow: hidden; pointer-events: none; border: 1px solid transparent; border-radius: 8px; background: #ffffff; }
.editor-highlights pre { margin: 0; color: #1a2638; font-family: 'Lora', Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.72; white-space: pre-wrap; overflow-wrap: break-word; tab-size: 4; }
#essay-editor { position: absolute; z-index: 2; inset: 0; width: 100%; height: 100%; box-sizing: border-box; padding: 16px 18px; resize: none; border: 1.5px solid #dde3f0; border-radius: 8px; background: transparent; color: transparent; -webkit-text-fill-color: transparent; caret-color: #1a2638; font-family: 'Lora', Georgia, 'Times New Roman', serif; font-size: 16px; line-height: 1.72; overflow: auto; scrollbar-width: none; }
#essay-editor::-webkit-scrollbar { display: none; }
#essay-editor::selection { background: rgba(47,84,192,.2); }
#essay-editor:focus-visible { border-color: #2f54c0; outline: 3px solid rgba(47,84,192,.22); outline-offset: 2px; }
.editor-highlights pre { padding: 16px 18px; }
.goal-highlight { padding: 1px 0; border-bottom: 2px solid #9a6200; border-radius: 2px; background: rgba(248,196,70,.5); box-decoration-break: clone; -webkit-box-decoration-break: clone; }
.editor-status { display: flex; justify-content: space-between; gap: 12px; margin-top: 8px; color: #8fa0b8; font-family: 'Nunito', ui-sans-serif, system-ui, sans-serif; font-size: 11.5px; font-weight: 600; }
""",
    js=r"""
export default function (component) {
  const { data, parentElement, setStateValue } = component
  const editor = parentElement.querySelector('#essay-editor')
  const highlightContent = parentElement.querySelector('#highlight-content')
  const wordCount = parentElement.querySelector('#word-count')
  if (!editor || !highlightContent || !wordCount) return

  const nextValue = data.value ?? ''
  if (editor.value !== nextValue) editor.value = nextValue
  const goals = Array.isArray(data.goals) ? data.goals : []
  const selectedKey = goals.map(goal => goal.goal_id).join('|')
  const previousKey = editor.dataset.selectedKey || ''
  const newlySelected = goals.filter(goal => !previousKey.split('|').includes(goal.goal_id))

  function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[character]))
  }
  function paragraphSpans(text) {
    const spans = []
    const separator = /(?:\r?\n[ \t]*){2,}/g
    let start = 0
    let match
    while ((match = separator.exec(text)) !== null) {
      spans.push([start, match.index])
      start = match.index + match[0].length
    }
    spans.push([start, text.length])
    return spans
  }
  function locate(text, goal) {
    const spans = paragraphSpans(text)
    const paragraphNumber = Number(goal.paragraph_number)
    const occurrence = Number(goal.occurrence)
    if (paragraphNumber < 1 || occurrence < 1 || paragraphNumber > spans.length) return null
    const [paragraphStart, paragraphEnd] = spans[paragraphNumber - 1]
    const paragraph = text.slice(paragraphStart, paragraphEnd)
    const reference = goal.draft_reference
    if (!reference) return null
    let index = -1
    for (let count = 0; count < occurrence; count += 1) {
      index = paragraph.indexOf(reference, index + 1)
      if (index < 0) return null
    }
    return { goal, start: paragraphStart + index, end: paragraphStart + index + reference.length }
  }
  function syncScroll() {
    highlightContent.style.transform = `translate(${-editor.scrollLeft}px, ${-editor.scrollTop}px)`
  }
  function renderHighlights() {
    const text = editor.value
    const ranges = goals.map(goal => locate(text, goal)).filter(Boolean).sort((a,b) => a.start - b.start || a.end - b.end)
    const groups = []
    ranges.forEach(range => {
      const group = groups[groups.length - 1]
      if (group && range.start < group.end) {
        group.end = Math.max(group.end, range.end)
        group.goals.push(range.goal)
      } else {
        groups.push({start: range.start, end: range.end, goals: [range.goal]})
      }
    })
    let cursor = 0
    let html = ''
    groups.forEach(group => {
      const goalIds = group.goals.map(goal => goal.goal_id).join('|')
      const label = group.goals.length > 1 ? `${group.goals.length} selected goals reference overlapping passages` : 'Selected goal reference'
      html += escapeHTML(text.slice(cursor, group.start))
      html += `<mark class="goal-highlight" data-goals="${escapeHTML(goalIds)}" aria-label="${escapeHTML(label)}">${escapeHTML(text.slice(group.start, group.end))}</mark>`
      cursor = group.end
    })
    highlightContent.innerHTML = html + escapeHTML(text.slice(cursor)) + '\n'
    syncScroll()
  }
  function updateCount() {
    const trimmed = editor.value.trim()
    wordCount.textContent = `${trimmed ? trimmed.split(/\s+/).length : 0} words`
  }
  function scrollGoalIntoView(goal) {
    const marker = Array.from(highlightContent.querySelectorAll('[data-goals]')).find(element => element.dataset.goals.split('|').includes(goal.goal_id))
    if (!marker) return
    editor.scrollTo({top: Math.max(0, marker.offsetTop - editor.clientHeight * .3), behavior: 'smooth'})
  }

  editor.oninput = () => {
    updateCount()
    renderHighlights()
    setStateValue('value', editor.value)
  }
  editor.onscroll = syncScroll
  editor.onblur = () => {
    if (editor.value !== data.value) setStateValue('value', editor.value)
  }
  updateCount()
  renderHighlights()
  if (selectedKey !== previousKey && newlySelected.length) scrollGoalIntoView(newlySelected[newlySelected.length - 1])
  editor.dataset.selectedKey = selectedKey
}
""",
)


def goal_highlight_editor(
    *,
    composition_id: str,
    initial_value: str,
    selected_goals: list[dict[str, Any]],
) -> str:
    key = f"essay_editor_{composition_id}"
    component_state = st.session_state.get(key, {})
    value = component_state.get("value", initial_value)

    def sync_value() -> None:
        value = st.session_state[key]["value"]
        st.session_state.editor_text = value
        st.session_state.writing_input = value

    result = _EDITOR(
        key=key,
        data={"value": value, "goals": selected_goals},
        default={"value": value},
        on_value_change=sync_value,
        height="content",
    )
    value = result.value if result and result.value is not None else value
    st.session_state.editor_text = value
    st.session_state.writing_input = value
    return value
