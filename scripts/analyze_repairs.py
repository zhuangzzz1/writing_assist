import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.support_agent import exact_ellipsis_locating_quotation
from scripts.evaluate_v3 import collect_states, repair_diagnostics_for_record


CATEGORIES = (
    "json_schema_mismatch",
    "coordinator_reference_location",
    "support_echo_mismatch",
    "genuine_authorship_leak",
    "structural_validator_false_positive",
    "grounding_or_source_limit",
    "api_empty_response",
    "api_other_failure",
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def instructional_texts(value: Any) -> Iterator[tuple[str, str]]:
    if not isinstance(value, dict):
        return
    for candidate_index, candidate in enumerate(value.get("candidates", [])):
        if not isinstance(candidate, dict):
            continue
        prefix = f"candidates[{candidate_index}]"
        for field in ("why_it_matters", "revision_action", "stuck_step"):
            text = candidate.get(field)
            if isinstance(text, str):
                yield f"{prefix}.{field}", text
        hint = candidate.get("hint", {})
        if not isinstance(hint, dict):
            continue
        for index, text in enumerate(hint.get("steps", [])):
            if isinstance(text, str):
                yield f"{prefix}.hint.steps[{index}]", text
        for field in ("self_check",):
            text = hint.get(field)
            if isinstance(text, str):
                yield f"{prefix}.hint.{field}", text
        for index, text in enumerate(hint.get("vocabulary_options", [])):
            if isinstance(text, str):
                yield f"{prefix}.hint.vocabulary_options[{index}]", text


def placeholder_category(field: str, text: str) -> str:
    if "____" in text:
        return "genuine_authorship_leak"
    lowered = text.lower()
    if re.search(r"\b(?:finish|complete)\b", lowered):
        return "genuine_authorship_leak"
    locating_quoted_excerpt = (
        ("find" in lowered or "read" in lowered or "look" in lowered)
        and ("draft" in lowered or "sentence before" in lowered)
    )
    completion_instruction = any(
        phrase in lowered
        for phrase in (
            "finish this thought",
            "finish it",
            "starts with",
            "start with",
            "say your position",
            "write one sentence",
        )
    )
    if completion_instruction and not locating_quoted_excerpt:
        return "genuine_authorship_leak"
    return "structural_validator_false_positive"


def placeholder_findings(
    raw_response: str, current_draft: str = "", allow_safe_locating: bool = False
) -> list[dict[str, str]]:
    try:
        value = json.loads(raw_response)
    except (json.JSONDecodeError, TypeError):
        return []
    findings = []
    for field, text in instructional_texts(value):
        if not any(marker in text for marker in ("____", "...", "…")):
            continue
        if (
            allow_safe_locating
            and current_draft
            and exact_ellipsis_locating_quotation(text, current_draft)
        ):
            continue
        findings.append(
            {
                "field": field,
                "category": placeholder_category(field, text),
                "evidence_excerpt": text[:500],
            }
        )
    return findings


def field_from_error(error: str) -> str:
    for line in error.splitlines():
        stripped = line.strip()
        if stripped.startswith("candidates.") or stripped.startswith("goal_feedback."):
            return stripped.split()[0]
    if "Sentence starters" in error:
        return "candidates[].hint.sentence_starter"
    if "source_limitations" in error or "source limitation" in error:
        return "source_limitations"
    if "reference" in error.lower():
        return "reference_or_location"
    return "response"


def categorize_diagnostic(diagnostic: dict[str, Any]) -> list[dict[str, Any]]:
    error = diagnostic.get("validation_error", "")
    agent = diagnostic.get("agent", "")
    raw_response = diagnostic.get("invalid_final_response", "")
    if "Completion blanks" in error or "Ellipses outside sentence starters" in error:
        findings = placeholder_findings(
            raw_response,
            diagnostic.get("current_draft", ""),
            allow_safe_locating="Ellipses outside sentence starters" in error,
        )
        if findings:
            return findings
    if any(
        message in error
        for message in (
            "Candidate and hint references must preserve",
            "Support must preserve every Coordinator source limitation exactly",
            "Support cannot change selected-goal status or carry-forward decisions",
            "Final references must match the verified Coordinator references",
        )
    ):
        category = "support_echo_mismatch"
    elif "Source-dependent findings require" in error or "Source accuracy" in error:
        category = "grounding_or_source_limit"
    elif agent == "Assessment Coordinator" and "reference" in error.lower():
        category = "coordinator_reference_location"
    elif agent == "Instructional Support Agent" and any(
        phrase in error for phrase in ("source", "grounding")
    ):
        category = "grounding_or_source_limit"
    else:
        category = "json_schema_mismatch"
    return [
        {
            "field": field_from_error(error),
            "category": category,
            "evidence_excerpt": error[:500],
            "needs_manual_review": (
                "Completion blanks" in error or "Ellipses outside sentence starters" in error
            ),
        }
    ]


def diagnostic_event(
    diagnostic: dict[str, Any], *, source: str
) -> dict[str, Any]:
    findings = categorize_diagnostic(diagnostic)
    return {
        "scenario_id": diagnostic.get("scenario_id", ""),
        "thread_id": diagnostic.get("thread_id", ""),
        "agent": diagnostic.get("agent", ""),
        "node": diagnostic.get("node", ""),
        "occurred_at": diagnostic.get("occurred_at"),
        "source": source,
        "validation_error": diagnostic.get("validation_error", ""),
        "categories": sorted({finding["category"] for finding in findings}),
        "findings": findings,
    }


def error_attempt_events(record: dict[str, Any], known_raw: set[str]) -> list[dict[str, Any]]:
    error = record.get("error", {})
    if error.get("type") != "ResponseValidationError":
        return []
    events = []
    for index, attempt in enumerate(record.get("model_attempts", []), start=1):
        messages = attempt.get("messages", [])
        system = messages[0].get("content", "") if messages else ""
        if "Instructional Support Agent" not in system:
            continue
        raw_response = attempt.get("final_response", "")
        if raw_response in known_raw:
            continue
        diagnostic = {
            "scenario_id": record.get("scenario_id", ""),
            "thread_id": "",
            "agent": "Instructional Support Agent",
            "node": "support_agent",
            "occurred_at": None,
            "validation_error": error.get("message", ""),
            "invalid_final_response": raw_response,
        }
        findings = placeholder_findings(raw_response)
        if not findings:
            findings = [
                {
                    "field": "unavailable_validation_detail",
                    "category": "json_schema_mismatch",
                    "evidence_excerpt": error.get("message", ""),
                    "needs_manual_review": True,
                }
            ]
        event = diagnostic_event(diagnostic, source="preserved_error_attempt")
        event["findings"] = findings
        event["categories"] = sorted({finding["category"] for finding in findings})
        event["model_attempt_index"] = index
        events.append(event)
    return events


def api_error_event(record: dict[str, Any]) -> dict[str, Any] | None:
    error = record.get("error")
    if not error or error.get("type") not in ("APIError", "RateLimitError", "AuthError"):
        return None
    message = error.get("message", "")
    category = "api_empty_response" if "empty response" in message.lower() else "api_other_failure"
    return {
        "scenario_id": record.get("scenario_id", ""),
        "category": category,
        "error": error,
    }


def analyze_mode(path: Path, mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    events = []
    api_errors = []
    other_errors = []
    unrepresented_attempts = 0
    for record in payload.get("records", []):
        logged_responses = Counter(
            response
            for state in collect_states(record)
            for log in state.get("execution_logs", [])
            for response in log.get("raw_responses", [])
        )
        for attempt in record.get("model_attempts", []):
            response = attempt.get("final_response", "")
            if logged_responses.get(response, 0):
                logged_responses[response] -= 1
            else:
                unrepresented_attempts += 1
        diagnostics = repair_diagnostics_for_record(record)
        events.extend(diagnostic_event(item, source="deduplicated_execution_log") for item in diagnostics)
        known_raw = {item.get("invalid_final_response", "") for item in diagnostics}
        events.extend(error_attempt_events(record, known_raw))
        api_error = api_error_event(record)
        if api_error:
            api_errors.append(api_error)
        elif record.get("error") and not any(
            event["scenario_id"] == record.get("scenario_id") for event in events
        ):
            other_errors.append(
                {"scenario_id": record.get("scenario_id", ""), "error": record["error"]}
            )
    summary = payload.get("summary", {})
    successful_logs = summary.get("model_call_count", 0)
    attempted_calls = successful_logs + unrepresented_attempts + len(api_errors)
    findings = [finding for event in events for finding in event["findings"]]
    category_counts = Counter(finding["category"] for finding in findings)
    agent_event_counts = Counter(event["agent"] for event in events)
    return {
        "mode": mode,
        "scenario_count": len(payload.get("records", [])),
        "attempted_model_calls": attempted_calls,
        "successful_response_logs": successful_logs,
        "unrepresented_preserved_attempts": unrepresented_attempts,
        "logged_schema_repair_calls": summary.get("schema_repair_calls", 0),
        "validation_failure_event_count": len(events),
        "validation_failure_events_by_agent": dict(sorted(agent_event_counts.items())),
        "field_finding_count": len(findings),
        "field_findings_by_category": {
            category: category_counts.get(category, 0) for category in CATEGORIES[:6]
        },
        "support_echo_mismatch_event_count": sum(
            "support_echo_mismatch" in event["categories"] for event in events
        ),
        "validation_failure_events": events,
        "api_or_empty_response_failures": api_errors,
        "other_scenario_errors": other_errors,
    }


def analyze_artifacts(paths: list[Path]) -> dict[str, Any]:
    analyses = []
    sources = []
    for path in paths:
        artifact = load_json(path)
        sources.append(
            {
                "path": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
        modes = artifact.get("modes", {})
        if not modes and "records" in artifact:
            modes = {artifact.get("mode", "unknown"): artifact}
        for mode, payload in modes.items():
            analyses.append(analyze_mode(path, mode, payload))
    category_totals = Counter()
    event_count = 0
    finding_count = 0
    echo_count = 0
    for analysis in analyses:
        category_totals.update(analysis["field_findings_by_category"])
        event_count += analysis["validation_failure_event_count"]
        finding_count += analysis["field_finding_count"]
        echo_count += analysis["support_echo_mismatch_event_count"]
    decision = (
        "defer_support_schema_refactor_no_echo_mismatch_burden"
        if echo_count == 0
        else "review_support_echo_burden_before_separately_versioned_refactor"
    )
    return {
        "analysis_type": "deduplicated validation-failure and repair-cause analysis; not a quality score",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_artifacts": sources,
        "modes": analyses,
        "totals": {
            "attempted_model_calls": sum(item["attempted_model_calls"] for item in analyses),
            "successful_response_logs": sum(item["successful_response_logs"] for item in analyses),
            "validation_failure_event_count": event_count,
            "field_finding_count": finding_count,
            "field_findings_by_category": {
                category: category_totals.get(category, 0) for category in CATEGORIES[:6]
            },
            "api_empty_response_failure_count": sum(
                error["category"] == "api_empty_response"
                for item in analyses
                for error in item["api_or_empty_response_failures"]
            ),
            "api_other_failure_count": sum(
                error["category"] == "api_other_failure"
                for item in analyses
                for error in item["api_or_empty_response_failures"]
            ),
        },
        "support_schema_decision": decision,
        "decision_boundary": (
            "Echo mismatches would require a separately versioned injection prototype and "
            "compatibility tests. Semantic failures and false positives do not justify that refactor."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze_artifacts(args.artifacts)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
