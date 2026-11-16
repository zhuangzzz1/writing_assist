import difflib
import hashlib
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ReferenceLocation:
    start: int
    end: int
    paragraph_number: int
    occurrence: int

    def as_dict(self) -> dict[str, int]:
        return {
            "start": self.start,
            "end": self.end,
            "paragraph_number": self.paragraph_number,
            "occurrence": self.occurrence,
        }


def _paragraph_spans(text: str) -> list[tuple[int, int]]:
    separator = re.compile(r"(?:\r?\n[ \t]*){2,}")
    spans = []
    start = 0
    for match in separator.finditer(text):
        spans.append((start, match.start()))
        start = match.end()
    spans.append((start, len(text)))
    return spans


def locate_reference(
    text: str,
    reference: str,
    paragraph_number: int,
    occurrence: int = 1,
) -> ReferenceLocation | None:
    if not reference or paragraph_number < 1 or occurrence < 1:
        return None
    spans = _paragraph_spans(text)
    if paragraph_number > len(spans):
        return None
    paragraph_start, paragraph_end = spans[paragraph_number - 1]
    paragraph = text[paragraph_start:paragraph_end]
    matches = list(re.finditer(re.escape(reference), paragraph))
    if occurrence > len(matches):
        return None
    match = matches[occurrence - 1]
    return ReferenceLocation(
        start=paragraph_start + match.start(),
        end=paragraph_start + match.end(),
        paragraph_number=paragraph_number,
        occurrence=occurrence,
    )


def reference_is_valid(
    text: str,
    reference: str,
    paragraph_number: int,
    occurrence: int = 1,
) -> bool:
    return locate_reference(text, reference, paragraph_number, occurrence) is not None


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


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"\S+|\s+", text)


def reference_overlaps_change(
    before: str,
    after: str,
    reference: str,
    side: str,
) -> bool:
    if not reference or side not in ("before", "after"):
        return False
    before_tokens = list(re.finditer(r"\S+|\s+", before))
    after_tokens = list(re.finditer(r"\S+|\s+", after))
    matcher = difflib.SequenceMatcher(
        a=[match.group() for match in before_tokens],
        b=[match.group() for match in after_tokens],
        autojunk=False,
    )
    text = before if side == "before" else after
    tokens = before_tokens if side == "before" else after_tokens
    changed_spans = []
    for operation, i1, i2, j1, j2 in matcher.get_opcodes():
        if operation == "equal":
            continue
        start_index, end_index = (i1, i2) if side == "before" else (j1, j2)
        if start_index < end_index:
            changed_spans.append(
                (tokens[start_index].start(), tokens[end_index - 1].end())
            )
    reference_start = text.find(reference)
    while reference_start >= 0:
        reference_end = reference_start + len(reference)
        if any(
            reference_start < changed_end and reference_end > changed_start
            for changed_start, changed_end in changed_spans
        ):
            return True
        reference_start = text.find(reference, reference_start + 1)
    return False


def build_text_diff(before: str, after: str) -> dict[str, Any]:
    before_tokens = _word_tokens(before)
    after_tokens = _word_tokens(after)
    matcher = difflib.SequenceMatcher(a=before_tokens, b=after_tokens, autojunk=False)
    operations = []
    added_words = 0
    removed_words = 0
    for operation, i1, i2, j1, j2 in matcher.get_opcodes():
        if operation == "equal":
            continue
        old_text = "".join(before_tokens[i1:i2])
        new_text = "".join(after_tokens[j1:j2])
        removed_words += len(old_text.split())
        added_words += len(new_text.split())
        operations.append(
            {
                "type": operation,
                "before": old_text,
                "after": new_text,
            }
        )
    unified = "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile="previous",
            tofile="current",
            lineterm="",
            n=1,
        )
    )
    return {
        "changed": before != after,
        "added_words": added_words,
        "removed_words": removed_words,
        "changed_words": added_words + removed_words,
        "operations": operations,
        "unified_diff": unified,
    }


def change_notification(
    previous: str,
    current: str,
    small_change_threshold: int = 8,
) -> dict[str, Any]:
    diff = build_text_diff(previous, current)
    return {
        **diff,
        "unchanged": previous == current,
        "needs_confirmation": previous == current
        or diff["changed_words"] <= small_change_threshold,
    }


def group_overlapping_goals(
    selected_goals: list[dict[str, Any]], text: str
) -> list[list[dict[str, Any]]]:
    located = []
    for input_index, goal in enumerate(selected_goals):
        location = locate_reference(
            text,
            goal["draft_reference"],
            goal["paragraph_number"],
            goal["occurrence"],
        )
        if location is not None:
            located.append(
                {"goal": goal, "location": location, "input_index": input_index}
            )
    located.sort(key=lambda item: (item["location"].start, item["location"].end))
    groups: list[list[dict[str, Any]]] = []
    group_ends: list[int] = []
    for item in located:
        location = item["location"]
        if groups and location.start < group_ends[-1]:
            groups[-1].append(item)
            group_ends[-1] = max(group_ends[-1], location.end)
        else:
            groups.append([item])
            group_ends.append(location.end)
    return [
        [item["goal"] for item in sorted(group, key=lambda item: item["input_index"])]
        for group in groups
    ]


def draft_sha256(writing: str) -> str:
    return hashlib.sha256(writing.encode("utf-8")).hexdigest()


def build_revision_history(
    snapshots: list[Any], rounds: list[Any]
) -> list[dict[str, Any]]:
    history = []
    for snapshot in snapshots[1:]:
        reviewed = None
        for round_record in rounds:
            round_state = round_record.state
            if (
                round_record.revision_number == snapshot.revision_number
                and round_record.status in ("active", "completed")
                and round_state.get("writing") == snapshot.writing
                and round_state.get("routing_decision")
                in ("support_agent", "direct_response")
            ):
                reviewed = round_record
        observations = {
            item.get("goal_id"): item
            for item in (
                reviewed.state.get("selected_goal_observations", []) if reviewed else []
            )
            if isinstance(item, dict)
        }
        selected_goals = []
        for goal in snapshot.selected_goals:
            goal_id = str(goal.get("goal_id", ""))
            observation = observations.get(goal_id, {})
            status = observation.get("status", "")
            if status not in (
                "specific_improvement",
                "improvement_not_yet_evident",
                "uncertain",
            ):
                status = ""
            carry_forward = observation.get("carry_forward")
            if not isinstance(carry_forward, bool):
                carry_forward = None
            selected_goals.append(
                {
                    "goal_id": goal_id,
                    "draft_reference": str(goal.get("draft_reference", "")),
                    "paragraph_number": goal.get("paragraph_number", 1),
                    "occurrence": goal.get("occurrence", 1),
                    "status": status,
                    "observation": str(observation.get("observation", "")),
                    "evidence_reference": str(
                        observation.get("evidence_reference", "")
                    ),
                    "carry_forward": carry_forward,
                }
            )
        history.append(
            {
                "revision_number": snapshot.revision_number,
                "snapshot_id": snapshot.snapshot_id,
                "reviewed_round_id": reviewed.round_id if reviewed else "",
                "reviewed_draft_sha256": draft_sha256(snapshot.writing),
                "selected_goals": selected_goals,
            }
        )
    return history


def selected_goal_ids(selected_goals: list[dict[str, Any]]) -> list[str]:
    return [str(goal.get("goal_id", "")) for goal in selected_goals]
