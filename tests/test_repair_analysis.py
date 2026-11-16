import json

from scripts.analyze_repairs import (
    analyze_artifacts,
    categorize_diagnostic,
    placeholder_category,
)


def support_response(stuck_step, revision_action="Revise the sentence in your own words."):
    return json.dumps(
        {
            "strengths": ["A clear focus."],
            "candidates": [
                {
                    "goal_id": "goal_1",
                    "title": "Explain the idea",
                    "why_it_matters": "Readers need the connection.",
                    "draft_reference": "A reason.",
                    "paragraph_number": 1,
                    "occurrence": 1,
                    "revision_action": revision_action,
                    "hint": {
                        "passage_reference": "A reason.",
                        "steps": ["A reason explains the claim.", "Find the reason."],
                        "self_check": "Does the connection make sense?",
                        "vocabulary_options": [],
                        "sentence_starter": "",
                    },
                    "stuck_step": stuck_step,
                }
            ],
            "goal_feedback": [],
            "source_limitations": [],
        }
    )


def repair_log(invalid, valid, error):
    return {
        "node": "support_agent",
        "display_name": "Instructional Support Agent",
        "timestamp": 123.0,
        "raw_responses": [invalid, valid],
        "model_calls": [{"token_usage": {}}, {"schema_repair": True, "token_usage": {}}],
        "prompt": [
            {"role": "system", "content": "Support"},
            {"role": "user", "content": f"Validation error: {error}"},
        ],
    }


def test_placeholder_analysis_distinguishes_target_frames_from_quoted_ellipsis():
    assert placeholder_category(
        "candidates[0].stuck_step", "Write one sentence that starts with 'My idea is...'"
    ) == "genuine_authorship_leak"
    assert placeholder_category(
        "candidates[0].hint.steps[1]", "Find the sentence in your draft that starts 'My idea...'"
    ) == "structural_validator_false_positive"
    assert placeholder_category(
        "candidates[0].stuck_step", "Add 'This shows that ____' to your sentence."
    ) == "genuine_authorship_leak"


def test_artifact_analysis_deduplicates_logs_and_counts_failed_and_api_attempts(tmp_path):
    invalid = support_response(
        "Finish this thought: 'My reason matters because ____.'",
        "Find the sentence in your draft that starts 'My reason...' and revise it.",
    )
    valid = support_response("Ask yourself what the reader needs to understand.")
    log = repair_log(invalid, valid, "Completion blanks or ellipses are not allowed.")
    logged_record = {
        "scenario_id": "logged",
        "initial_state": {
            "thread_id": "thread-1",
            "model_config": {},
            "execution_logs": [log],
        },
        "revision_states": [
            {"thread_id": "thread-1", "model_config": {}, "execution_logs": [log]}
        ],
        "model_attempts": [
            {"messages": [], "final_response": invalid},
            {"messages": [], "final_response": valid},
        ],
    }
    failed_invalid = support_response("Add 'This shows that ____' after your reason.")
    failed_record = {
        "scenario_id": "failed",
        "error": {
            "type": "ResponseValidationError",
            "message": "Support failed after one correction.",
        },
        "model_attempts": [
            {
                "messages": [{"role": "system", "content": "Instructional Support Agent"}],
                "final_response": failed_invalid,
            },
            {
                "messages": [{"role": "system", "content": "Instructional Support Agent"}],
                "final_response": failed_invalid,
            },
        ],
    }
    api_record = {
        "scenario_id": "empty",
        "error": {"type": "APIError", "message": "DeepSeek returned an empty response."},
        "model_attempts": [],
    }
    artifact = {
        "modes": {
            "nonthinking": {
                "records": [logged_record, failed_record, api_record],
                "summary": {"model_call_count": 2, "schema_repair_calls": 1},
            }
        }
    }
    path = tmp_path / "artifact.json"
    path.write_text(json.dumps(artifact))

    result = analyze_artifacts([path])

    mode = result["modes"][0]
    assert mode["validation_failure_event_count"] == 3
    assert mode["field_finding_count"] == 4
    assert mode["field_findings_by_category"]["genuine_authorship_leak"] == 3
    assert mode["field_findings_by_category"]["structural_validator_false_positive"] == 1
    assert mode["attempted_model_calls"] == 5
    assert mode["unrepresented_preserved_attempts"] == 2
    assert result["totals"]["api_empty_response_failure_count"] == 1
    assert result["support_schema_decision"] == (
        "defer_support_schema_refactor_no_echo_mismatch_burden"
    )


def test_echo_mismatch_requires_a_separate_schema_decision(tmp_path):
    invalid = support_response("Ask a question about your own idea.")
    valid = support_response("Ask another question about your own idea.")
    log = repair_log(
        invalid,
        valid,
        "Candidate and hint references must preserve the Coordinator reference.",
    )
    record = {
        "scenario_id": "echo",
        "initial_state": {
            "thread_id": "thread-echo",
            "model_config": {},
            "execution_logs": [log],
        },
    }
    artifact = {
        "modes": {
            "thinking": {
                "records": [record],
                "summary": {"model_call_count": 2, "schema_repair_calls": 1},
            }
        }
    }
    path = tmp_path / "echo.json"
    path.write_text(json.dumps(artifact))

    result = analyze_artifacts([path])

    assert result["modes"][0]["support_echo_mismatch_event_count"] == 1
    assert result["support_schema_decision"] == (
        "review_support_echo_burden_before_separately_versioned_refactor"
    )



def test_new_blank_and_ellipsis_validator_messages_are_categorized():
    blank = support_response("Add 'This shows that ____' after your reason.")
    blank_diagnostic = {
        "agent": "Instructional Support Agent",
        "validation_error": "Completion blanks are allowed only in approved abstract sentence starters.",
        "invalid_final_response": blank,
    }
    ellipsis = support_response("Say it aloud, then finish the thought: 'My reason matters because...'")
    ellipsis_diagnostic = {
        "agent": "Instructional Support Agent",
        "validation_error": (
            "Ellipses outside sentence starters must be exact quoted draft excerpts "
            "used for locating, not completion placeholders."
        ),
        "invalid_final_response": ellipsis,
    }

    assert categorize_diagnostic(blank_diagnostic)[0]["category"] == (
        "genuine_authorship_leak"
    )
    assert categorize_diagnostic(ellipsis_diagnostic)[0]["category"] == (
        "genuine_authorship_leak"
    )



def test_new_validator_analysis_skips_safe_fields_but_keeps_actual_target_frame():
    value = json.loads(support_response("Ask a question about your own idea."))
    first = value["candidates"][0]
    first["hint"]["steps"][1] = "Find the sentence in your draft that starts 'A reason...'"
    second = json.loads(json.dumps(first))
    second["goal_id"] = "goal_2"
    second["stuck_step"] = "Write one sentence before 'A reason...' that explains your idea."
    value["candidates"].append(second)
    diagnostic = {
        "agent": "Instructional Support Agent",
        "current_draft": "A reason.",
        "validation_error": (
            "Ellipses outside sentence starters must be exact quoted draft excerpts "
            "used for locating, not completion placeholders."
        ),
        "invalid_final_response": json.dumps(value),
    }

    findings = categorize_diagnostic(diagnostic)

    assert len(findings) == 1
    assert findings[0]["field"] == "candidates[1].stuck_step"
    assert findings[0]["category"] == "genuine_authorship_leak"
