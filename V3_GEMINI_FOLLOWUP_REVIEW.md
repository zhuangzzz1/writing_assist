# Follow-up Context for Gemini Prompt Review

## Review request

You previously reviewed the prompts for a V3 iterative academic writing coach for multilingual learners in grades 5–7. Your main concern was that the prompts—especially the Support round prompt—might be so specific that they limit model performance.

This document summarizes subsequent logic and prompt changes, identifies which original concerns remain, and explains my concerns about your earlier critique. Please reassess which concerns are resolved, unchanged, or potentially worsened. In particular, consider whether the new language-feedback rules express generalizable principles or continue a patch-driven pattern.

The relevant code excerpts are included directly because you cannot access the local repository.

## 1. Version and scope

The packet you originally reviewed contained prompt/schema `v3.6.5`/`v3.6.3`. The current working tree uses **`v3.6.8`/`v3.6.3`**. The model-output schemas have not changed.

The latest changes do **not** implement a broad prompt simplification. They mainly add:

1. Narrow deterministic recovery for incorrect quotation locations.
2. More specific guidance for language-mechanics feedback.
3. Additional prompt rules responding to observed semantic errors.

The two-agent architecture remains unchanged: an Assessment Coordinator produces structured findings and routing, and an Instructional Support Agent converts those findings into student-facing feedback and scaffolds.

## 2. Latest logic changes

### Deterministic recovery for unique references

The Coordinator still generates `draft_reference`, `paragraph_number`, and `occurrence`. Before model-output validation, the app now checks issues whose supplied locations are invalid.

If the exact quotation occurs exactly once in the complete draft and lies within one blank-line-separated block, Python corrects its paragraph and occurrence metadata. The location helper is:

```python
def locate_unique_reference(text: str, reference: str) -> ReferenceLocation | None:
    if not reference:
        return None
    matches = list(re.finditer(re.escape(reference), text))
    if len(matches) != 1:
        return None
    match = matches[0]
    for paragraph_number, (start, end) in enumerate(_paragraph_spans(text), start=1):
        if match.start() >= start and match.end() <= end:
            return ReferenceLocation(
                start=match.start(),
                end=match.end(),
                paragraph_number=paragraph_number,
                occurrence=1,
            )
    return None
```

The Coordinator applies that recovery and records each correction:

```python
def normalize_unique_issue_locations(
    raw: dict[str, Any], writing: str
) -> list[dict[str, Any]]:
    normalizations = []
    issues = raw.get("issues", [])
    if not isinstance(issues, list):
        return normalizations
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        reference = issue.get("draft_reference")
        paragraph = issue.get("paragraph_number")
        occurrence = issue.get("occurrence")
        if not isinstance(reference, str) or not isinstance(paragraph, int) or not isinstance(occurrence, int):
            continue
        if reference_is_valid(writing, reference, paragraph, occurrence):
            continue
        location = locate_unique_reference(writing, reference)
        if location is None:
            continue
        normalizations.append(
            {
                "goal_id": issue.get("goal_id", ""),
                "previous_paragraph_number": paragraph,
                "previous_occurrence": occurrence,
                "paragraph_number": location.paragraph_number,
                "occurrence": location.occurrence,
            }
        )
        issue["paragraph_number"] = location.paragraph_number
        issue["occurrence"] = location.occurrence
    return normalizations
```

Each correction is recorded in `coordinator_reference_normalizations`, including the goal ID and old/new locations. Repeated, missing, ambiguous, or cross-paragraph references still trigger bounded model repair. Valid model-supplied locations remain unchanged.

This is a **narrow hybrid approach**, not full deterministic ownership of reference metadata. It currently applies to Coordinator issues, not every framework, Support, or final-comparison reference.

### Unchanged logic relevant to your critique

- Support still returns and exactly echoes Coordinator references, locations, goal statuses, carry-forward values, and source limitations. Python validates these but does not inject them automatically.
- Issue ranking still severity-sorts on every round.
- Clarification routing, final comparison, and the two-agent architecture are unchanged.
- The student runtime remains non-thinking at temperature 0.
- The sentence-starter allowlist and hint schema are unchanged.
- No Support output fields have been removed or replaced by deterministic post-processing.

## 3. Latest prompt changes

### Coordinator language assessment

The following Coordinator guidance was added or expanded:

```text
Recognize ideas separately from mechanics. Preserve voice, including appropriate informal narrative voice. Prioritize central meaning, evidence/details/elaboration, and organization before conventions unless errors seriously obscure meaning. For every language_conventions issue, supply obscures_meaning=true or false based on the actual reader effect; distraction or slower reading alone does not establish obscured meaning. When the teacher marks language corrections optional, a language_conventions goal requires obscures_meaning=true; otherwise use direct_response if no meaningful issue remains. Do not manufacture issues or catalog every error. Routine spelling belongs in the editor's spellcheck rather than a list of typo answers. A language candidate should teach one recognizable pattern, such as sentence boundaries or a non-count noun, rather than combine spelling, capitalization, and grammar in one goal. Its exact draft_reference must support the specific instruction; never claim a capitalization or other localized error that the reference does not show. A meaningful issue affects the task, central idea, genre/teacher requirement, reader understanding, a recognizable pattern, a critical localized claim/source interpretation, or a student-selected concern. Isolated conventions or synonyms are not meaningful merely because they can be changed.
```

The intended changes are:

- Distraction or slower reading alone does not establish obscured meaning.
- Routine spelling belongs in the editor’s spellcheck rather than a catalogue of typo answers.
- A language candidate should teach one recognizable pattern rather than combine spelling, capitalization, and grammar.
- The exact quoted reference must support the localized instruction.

### Support language instruction

The current Support language-pattern instruction is:

```text
LANGUAGE PATTERN INSTRUCTION: For a meaningful language_conventions issue, teach one recognizable pattern concisely rather than cataloguing isolated errors. Do not combine spelling, capitalization, and grammar in one candidate. A brief rule or meaning note is permitted when it helps the student understand the pattern. Direct the student to locate and edit the relevant wording in the draft. For routine spelling, direct the student to the editor's spellcheck and the intended meaning; do not ask the student to compare against a misspelled word as though it were the correction, and do not supply a list of spelling answers in vocabulary_options. Check the exact referenced words before giving a localized instruction: never ask the student to capitalize a word that is already capitalized or fix another error absent from the reference. The student must perform the revision; do not rewrite the complete sentence or paragraph. Reading aloud can support sentence-boundary revision when appropriate. Never move an on-topic opening frame into stuck_step with an instruction such as 'write a sentence that starts with' a supplied phrase; only the separately approved abstract sentence_starter may offer a structural frame.
```

These rules respond to observed errors, including a spelling-answer list and advice to capitalize an already-capitalized word. However, they also **increase rather than decrease prompt specificity**.

## 4. Other changes since the packet you reviewed

The intermediate `v3.6.6`–`v3.6.7` changes also added the following guidance and behavior:

- Strengths must identify observable writing choices or details and their reader effect rather than infer talent, research effort, or technical validity.
- An imaginative informational draft may propose an invented machine, system, or process without being reclassified as narrative or treated as fabricated evidence merely because it is invented.
- For speculative processes, assessment should consider sequence, inputs, outputs, and whether the reader can connect the process to the intended benefit.
- Feedback must not name possible destinations, mechanisms, or solutions that the student has not supplied.
- The model must not certify that an invented design works or that its science is accurate, and it must not impose source requirements on every imaginative task.
- Transition or conclusion goals must not be manufactured from length or missing guide words alone; an existing ending that serves a reasonable purpose should be recognized.
- Candidate rationales should name an actual reader effect or unanswered reader question rather than rely on generic statements such as “details make writing better.” Reader questions may use existing draft material but must not name the target answer.
- Coordinator paragraph guidance now explicitly counts a standalone title as a blank-line-separated block.
- The Choose interface initially presents one recommended goal, reveals alternatives on request, separates idea/reasoning/organization goals from optional sentence polishing, and makes no additional model calls for these presentation changes.

The final Coordinator and Support prompts are unchanged.

## 5. Original concerns that remain unresolved

### Hint-step contract

The prompt still contains these instructions:

```text
Each hint must include passage_reference exactly equal to the candidate's draft_reference, two to four linked thinking steps or guiding questions, and a useful self_check.
```

```text
Step 0 (concept restatement): Open with one sentence that re-grounds the underlying writing concept in plain terms before the procedural chain.
```

```text
Procedural steps (2-4 steps): After Step 0, provide the linked thinking steps.
```

The JSON example still describes “two to four linked passage-specific thinking steps,” and the PRD still specifies two to four steps. However, the actual model-output field permits **3–5 total steps**:

```python
steps: list[str] = Field(min_length=3, max_length=5)
```

Thus, the real issue is disagreement among the prompt, PRD, JSON description, and validator—not a validator that enforces two to four steps.

### Ranking precedence

The Coordinator still receives both instructions:

```text
Accuracy-tier findings should rank first in Round 1 regardless of which goal they map to.
```

```text
When student_concerns names a specific area and draft evidence supports a corresponding meaningful issue, place that issue first.
```

The code then severity-sorts issues on every round, not only Round 1:

```python
def _rank_by_severity(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rank issues by severity tier, then preserve within-tier order."""
    severity_order = {"accuracy": 0, "reasoning": 1, "development": 2}
    return sorted(issues, key=lambda issue: severity_order[issue["finding_severity"]])
```

The desired precedence between accuracy findings and supported student concerns remains a product decision.

### Claim anchoring across genres

The argument-oriented rule remains:

```text
CLAIM ANCHORING: Any phrase equivalent to "why this matters" or "why that helps" in why_it_matters or revision_action must be completed with a prepositional phrase anchoring to the specific claim from the student's draft. You receive the full draft via current_draft and should extract the student's claim text directly from it. Never output "why that matters," "why this helps," or "why this is important" without a completing clause that names the specific claim, such as "why that supports your argument that the school should start a garden" or "why that connects to your point about students needing more activities."
```

This remains awkward for narrative writing, informational writing organized around a central idea, and drafts whose main problem is the absence of a clear claim.

### Regression field naming

The revision prose still says:

```text
Identify meaningful new issues or regressions when present, marking regressions=true.
```

The actual output field remains singular:

```json
"regression": false
```

### Support field echoing

Support must still copy deterministic Coordinator data into its output. For example, the validator requires:

```python
if (
    candidate.draft_reference != issue["draft_reference"]
    or candidate.paragraph_number != issue["paragraph_number"]
    or candidate.occurrence != issue["occurrence"]
    or candidate.hint.passage_reference != candidate.draft_reference
):
    raise ValueError("Candidate and hint references must preserve the Coordinator reference.")
if output.source_limitations != state.get("source_limitations", []):
    raise ValueError("Support must preserve every Coordinator source limitation exactly.")
```

It also requires Support’s goal-feedback status and carry-forward value to match the Coordinator exactly:

```python
if (
    feedback.status != expected["status"]
    or feedback.carry_forward != expected["carry_forward"]
):
    raise ValueError("Support cannot change selected-goal status or carry-forward decisions.")
```

Therefore, your suggestion to inject these fields deterministically has not been implemented.

### Sentence starters

The sentence-starter table and allowlist remain unchanged. This includes:

- The literal option `This evidence/detail matters because ____.`
- Formal options such as `In conclusion, ____.` and `One concern is that ____; however, ____.`
- The requirement to use a nonempty starter for the first candidate whenever `reasoning_operation` is not `none`.

Any new starter wording would require both prompt and deterministic-allowlist changes.

### Boundary routes and final grounding

The prompt still does not comprehensively specify which ordinary assessment fields must be empty on clarification and teacher-review routes. Existing code already rejects framework coverage on boundary routes and rejects selected-goal observations outside normal revision routes.

The final Coordinator prompt still lacks the fuller source-grounding instructions used during round assessment. Existing deterministic checks block some unverified source wording, but they do not provide complete semantic source verification.

## 6. Current evidence and limitations

The project’s recorded verification reports:

- **260 mocked checks passed.**
- Earlier `v3.6.6` and `v3.6.7` attempts fell back after incorrect title-related paragraph locations. Explicit title-counting prompt guidance alone did not fix the failures.
- Replaying a failed response with deterministic unique-reference recovery corrected two locations without another model call.
- A final `v3.6.8` exact-text initial review completed in two non-thinking calls with no repairs or reference normalizations and produced four candidates with valid exact locations.
- A local Choose/Revise browser check preserved the expected goal and highlighting without additional model calls.

This was **one initial-review case**, not full acceptance. No revision or final reflection was exercised. Semantic concerns remained:

- One revision action requested two connections while its self-check referred to all four.
- Some requested station handoffs might already be inferable from later paragraphs.
- A potentially stronger process question was not selected as the recommended goal.

The result demonstrates successful technical delivery with mixed semantic quality. It does not establish clean pedagogical acceptance, educator approval, improved learning outcomes, or general superiority over the earlier prompt.

## 7. My concerns about your earlier critique

### Causal claims were stronger than the evidence

Non-thinking mode and temperature 0 do not themselves prove that prompt specificity causes stiff prose or validation failures. Temperature controls sampling randomness; it does not measure the model’s capacity to reconcile instructions.

The controlled three-handoff thinking comparison was promising for Support validation, but it was small. The full thinking run still had routing and semantic concerns and substantially higher latency. This does not establish that thinking generally solves the problem or that prompt length is the root cause.

### The hint-validator claim was incorrect

Your critique hypothesized a validator enforcing two to four steps. The actual field accepts three to five. The contract inconsistency is real, but the specific failure mechanism you described is not.

### Some proposed deterministic guards already existed

The application already has deterministic clarification-limit handling when the Coordinator requests another clarification after two answers. It also already rejects improvement or regression findings when the original and final drafts are unchanged.

There is still a separate routing loophole: a model once selected `teacher_review` with category `clarification_limit` directly after one unclear answer instead of asking another clarification question. That is a more specific issue than simply saying the application relies on the LLM to count clarification turns.

### Some criticisms were design preferences rather than demonstrated defects

- The severity taxonomy explicitly includes structure under `development`, so narrative pacing and organization are not necessarily unclassifiable.
- Offering `In conclusion` as an optional abstract starter is not directly equivalent to forcing a five-paragraph formula.
- Coordinator ownership of `reasoning_operation` is an intentional shared contract with Support, not automatically cross-agent leakage.
- Whether particular starters are too formal for grades 5–7 requires educator review rather than prompt inspection alone.

### Several recommendations require coordinated implementation changes

- New sentence starters require deterministic-allowlist updates.
- Changing hint counts requires alignment among the prompt, PRD, JSON description, validator, and tests.
- Removing Support fields requires prompt/schema changes, deterministic post-processing, state compatibility work, and regression tests.

These are not prompt-only edits.

### Reliability should not be optimized by weakening authorship boundaries

Earlier runs produced genuine target-answer frames and target-like vocabulary, not merely harmless JSON variants. Some repairs were false positives involving quoted ellipses, but others caught real authorship violations. Reducing repair counts is not sufficient evidence of a better prompt.

### The new recovery supports only part of your deterministic-code argument

The unique-reference recovery demonstrates that code can correct a narrow class of location failures. It does not establish that removing every echoed Support field would be the “single biggest reliability gain.” That claim requires analysis of actual failure categories and controlled comparisons.

## 8. Requested follow-up assessment

Please address these questions in your next review:

1. Which of your original concerns are resolved, unchanged, or potentially worsened by these changes?
2. Does the narrow deterministic recovery change your recommendation about who should own reference metadata?
3. Are the new language-feedback rules generalizable principles, or are they overly specific patches? What could be removed or generalized without losing the intended protection?
4. Should the next step be prompt compression, deterministic field injection, contract cleanup, or some combination? Please prioritize rather than assuming a fixed percentage of prompt text should be removed.
5. What controlled comparison would distinguish prompt-overload effects from model-mode effects? Hold the model, mode, Coordinator handoffs, schemas, and validators constant where possible, and assess semantic authorship, warmth, readability, grounding, and repair categories—not just repair counts.
6. Which judgments require educator review rather than another LLM’s recommendation?
