import itertools
import json
import re
from typing import Any


WORD = re.compile(r"[A-Za-z0-9]+(?:[’'-][A-Za-z0-9]+)*")
SENTENCE = re.compile(r"[^.!?]+[.!?]+(?:[\"'”’)]*)?|[^.!?]+$")
NUMBER_ANCHOR = re.compile(r"\b\d+(?:\.\d+)?%?\b")
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "because", "but", "by",
    "can", "could", "did", "do", "does", "for", "from", "had", "has", "have",
    "he", "her", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "me", "my", "not", "of", "on", "one", "or", "our", "she", "so", "that",
    "the", "their", "them", "they", "this", "to", "was", "we", "were", "what",
    "when", "which", "who", "why", "will", "with", "would", "you", "your",
}
READABILITY_METRIC_NOTES = [
    "Sentence splitting and word counts are simple descriptive heuristics for JSON text fragments.",
    "The long-action count uses the documented 38-word review heuristic, not a quality threshold.",
    "Repetition and action/self-check scope flags require human review and are not automatic failures.",
    "No Flesch–Kincaid grade-level score, pedagogical-quality score, educator approval, or learning outcome is inferred.",
]


def words(text: str) -> list[str]:
    return WORD.findall(text)


def content_words(text: str) -> set[str]:
    return {word.lower() for word in words(text) if word.lower() not in STOP_WORDS}


def sentence_word_counts(text: str) -> list[int]:
    return [len(words(sentence)) for sentence in SENTENCE.findall(text.strip()) if words(sentence)]


def field_stats(texts: list[str]) -> dict[str, Any]:
    counts = [count for text in texts for count in sentence_word_counts(text)]
    return {
        "sentence_count": len(counts),
        "word_count": sum(counts),
        "mean_words_per_sentence": round(sum(counts) / len(counts), 2) if counts else 0,
        "max_words_per_sentence": max(counts, default=0),
    }


def normalized(text: str) -> str:
    return " ".join(word.lower() for word in words(text))


def overlap(left: str, right: str) -> float:
    left_words = content_words(left)
    right_words = content_words(right)
    union = left_words | right_words
    return len(left_words & right_words) / len(union) if union else 1.0


def candidate_fields(candidate: dict[str, Any]) -> dict[str, str]:
    hint = candidate.get("hint", {})
    fields = {
        "revision_action": candidate.get("revision_action", ""),
        "self_check": hint.get("self_check", ""),
        "stuck_step": candidate.get("stuck_step", ""),
    }
    for index, step in enumerate(hint.get("steps", []), start=1):
        fields[f"hint_step_{index}"] = step
    return fields


def repetition_flags(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    fields = candidate_fields(candidate)
    flags = []
    for left, right in itertools.combinations(fields, 2):
        left_text = fields[left]
        right_text = fields[right]
        left_normalized = normalized(left_text)
        right_normalized = normalized(right_text)
        exact = bool(left_normalized) and left_normalized == right_normalized
        similarity = overlap(left_text, right_text)
        if exact or (
            similarity >= 0.65
            and min(len(content_words(left_text)), len(content_words(right_text))) >= 3
        ):
            flags.append(
                {
                    "fields": [left, right],
                    "exact_duplicate": exact,
                    "content_word_jaccard": round(similarity, 3),
                }
            )
    return flags


def scope_flags(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    action = candidate.get("revision_action", "")
    check = candidate.get("hint", {}).get("self_check", "")
    flags = []
    action_numbers = set(NUMBER_ANCHOR.findall(action))
    check_numbers = set(NUMBER_ANCHOR.findall(check))
    if action_numbers != check_numbers:
        flags.append(
            {
                "reason": "different_numeric_anchors",
                "action": sorted(action_numbers),
                "self_check": sorted(check_numbers),
            }
        )
    similarity = overlap(action, check)
    if (
        min(len(content_words(action)), len(content_words(check))) >= 3
        and similarity < 0.15
    ):
        flags.append(
            {
                "reason": "low_shared_content_word_overlap",
                "content_word_jaccard": round(similarity, 3),
            }
        )
    return flags


def readability_metrics(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    texts = {
        "why_it_matters": [candidate.get("why_it_matters", "") for candidate in candidates],
        "revision_action": [candidate.get("revision_action", "") for candidate in candidates],
        "hint_steps": [
            step
            for candidate in candidates
            for step in candidate.get("hint", {}).get("steps", [])
        ],
        "stuck_step": [candidate.get("stuck_step", "") for candidate in candidates],
    }
    per_candidate = []
    for candidate in candidates:
        per_candidate.append(
            {
                "scenario_id": candidate.get("scenario_id", ""),
                "goal_id": candidate.get("goal_id", ""),
                "field_sentence_words": {
                    "why_it_matters": field_stats([candidate.get("why_it_matters", "")]),
                    "revision_action": field_stats([candidate.get("revision_action", "")]),
                    "hint_steps": field_stats(candidate.get("hint", {}).get("steps", [])),
                    "stuck_step": field_stats([candidate.get("stuck_step", "")]),
                },
                "action_word_count": len(words(candidate.get("revision_action", ""))),
                "repetition_review_flags": repetition_flags(candidate),
                "action_self_check_scope_review_flags": scope_flags(candidate),
            }
        )
    return {
        "candidate_count": len(candidates),
        "field_sentence_words": {name: field_stats(values) for name, values in texts.items()},
        "long_actions": {
            "threshold_words": 38,
            "count": sum(item["action_word_count"] > 38 for item in per_candidate),
            "goal_ids": [
                item["goal_id"] for item in per_candidate if item["action_word_count"] > 38
            ],
        },
        "repetition": {
            "high_overlap_content_word_jaccard_threshold": 0.65,
            "review_count": sum(len(item["repetition_review_flags"]) for item in per_candidate),
            "exact_duplicate_count": sum(
                flag["exact_duplicate"]
                for item in per_candidate
                for flag in item["repetition_review_flags"]
            ),
        },
        "action_self_check_scope": {
            "review_count": sum(
                len(item["action_self_check_scope_review_flags"]) for item in per_candidate
            )
        },
        "candidates": per_candidate,
    }


def record_candidates(record: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    seen = set()
    states = []
    for key in ("initial_state", "genre_correction_state", "final_state"):
        if record.get(key):
            states.append(record[key])
    for key in ("clarification_states", "revision_states"):
        states.extend(record.get(key, []))
    for state in states:
        for candidate in state.get("revision_candidates", []):
            identity = (
                state.get("thread_id", ""),
                candidate.get("goal_id", ""),
                json.dumps(candidate, sort_keys=True, ensure_ascii=False),
            )
            if identity in seen:
                continue
            seen.add(identity)
            candidates.append({**candidate, "scenario_id": record.get("scenario_id", "")})
    return candidates


def record_readability(record: dict[str, Any]) -> dict[str, Any]:
    return readability_metrics(record_candidates(record))


def arm_readability(records: list[dict[str, Any]]) -> dict[str, Any]:
    return readability_metrics(
        [candidate for record in records for candidate in record_candidates(record)]
    )
