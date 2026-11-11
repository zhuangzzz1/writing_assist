import json

import pytest

from agents.assessment_coordinator import AssessmentCoordinator
from agents.prompts import COORDINATOR_ROUND_PROMPT, SUPPORT_ROUND_PROMPT
from agents.support_agent import InstructionalSupportAgent
from agents.utils import ResponseValidationError
from langgraph_core.revision import build_text_diff
from langgraph_core.state import make_review_state
from tests.helpers import (
    DEFAULT_REFERENCE,
    INITIAL_DRAFT,
    FakeClient,
    candidate_for,
    coordinator_payload,
    final_coordinator_payload,
    final_support_payload,
    issue_for,
    observation_for,
    support_payload,
)


def round_state(genre="argument", source=""):
    return make_review_state(
        INITIAL_DRAFT,
        "6th Grade",
        genre_selection=genre,
        source_material=source,
    )


def support_state(revision=False, source=""):
    writing = INITIAL_DRAFT + "\n\nStudents learn to notice what their community needs." if revision else INITIAL_DRAFT
    selected = [candidate_for(issue_for(INITIAL_DRAFT))] if revision else []
    state = make_review_state(
        writing,
        "6th Grade",
        original_writing=INITIAL_DRAFT,
        previous_writing=INITIAL_DRAFT if revision else "",
        source_material=source,
        revision_number=1 if revision else 0,
        selected_goals=selected,
        text_diff=build_text_diff(INITIAL_DRAFT, writing) if revision else {},
    )
    state.update(
        {
            "working_genre": "argument",
            "strengths": ["Clear position"],
            "issues": [issue_for(writing)],
            "source_limitations": [],
            "selected_goal_observations": [observation_for()] if revision else [],
        }
    )
    return state


def final_state(changed=True):
    final = INITIAL_DRAFT + "\n\nA new explanation." if changed else INITIAL_DRAFT
    return make_review_state(
        final,
        "6th Grade",
        review_mode="final",
        original_writing=INITIAL_DRAFT,
        revision_number=1 if changed else 0,
        text_diff=build_text_diff(INITIAL_DRAFT, final),
    )


@pytest.mark.parametrize("genre", ["argument", "informational", "narrative"])
def test_coordinator_supports_all_three_explicit_genres(genre):
    state = round_state(genre)
    client = FakeClient([coordinator_payload(state)])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["working_genre"] == genre
    assert result.values["routing_decision"] == "support_agent"
    assert "Narrative" in client.calls[0][0][0]["content"]
    assert "Argument" in client.calls[0][0][0]["content"]


def test_auto_genre_uses_dominant_purpose_not_first_person_shortcut():
    state = make_review_state(
        "I will explain how pollination works.\n\nBees move pollen between flowers.",
        "7th Grade",
        genre_selection="auto",
    )
    payload = coordinator_payload(
        state,
        working_genre="informational",
        issues=[issue_for(state["writing"], "Bees move pollen between flowers.")],
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["working_genre"] == "informational"
    assert result.values["genre_basis"]


def test_material_genre_ambiguity_has_one_question_and_nonforced_choices():
    state = make_review_state("I learned a lesson. Schools should teach gardens.", "6th Grade")
    payload = coordinator_payload(
        state,
        route="ask_clarification",
        clarification_question="Is your main purpose to tell the experience or argue for school gardens?",
        clarification_choices=["narrative", "argument", "Something else / not sure"],
        working_genre="",
        genre_confidence="",
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["clarification_choices"][-1] == "Something else / not sure"
    assert result.values["clarification_question"].count("?") == 1
    assert result.values["issues"] == []


def test_explicit_genre_correction_is_normalized_without_model_repair():
    state = round_state("narrative")
    conflicting = coordinator_payload(state, working_genre="argument")
    client = FakeClient([conflicting])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["working_genre"] == "narrative"
    assert result.values["coordinator_repair_count"] == 0
    assert client.responses == []


def test_source_present_mismatch_requires_a_specific_source_location():
    state = round_state(source="Paragraph 3: The survey included 50 students.")
    issue = issue_for(
        state["writing"],
        source_dependent=True,
        source_location="paragraph 3",
        category="source_use",
    )
    payload = coordinator_payload(state, issues=[issue])

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["issues"][0]["source_location"] == "paragraph 3"
    assert state["source_material_available"] is True


def test_source_missing_dependent_finding_is_repaired():
    state = round_state()
    invalid_issue = issue_for(
        state["writing"], source_dependent=True, source_location="paragraph 3"
    )
    invalid = coordinator_payload(state, issues=[invalid_issue])
    valid = coordinator_payload(
        state,
        source_limitations=["I cannot check the quotation without its source passage."],
    )
    client = FakeClient([invalid, valid])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["source_limitations"]
    assert result.values["issues"][0]["source_dependent"] is False


def test_source_location_is_rejected_for_non_source_finding():
    state = round_state(source="A source")
    issue = issue_for(state["writing"], source_location="paragraph 1")
    invalid = coordinator_payload(state, issues=[issue])
    valid = coordinator_payload(state)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1


def test_coordinator_preserves_safety_flag_without_spending_repair():
    raw = json.dumps(
        {
            "flag_teacher": True,
            "routing_decision": "invalid",
            "teacher_flag_category": "concerning_content",
            "teacher_flag_reason": "The writer describes bullying.",
        }
    )
    client = FakeClient([raw])

    result = AssessmentCoordinator(client).run(round_state())

    assert result.values["routing_decision"] == "teacher_review"
    assert result.values["flag_teacher"] is True
    assert result.values["coordinator_repair_count"] == 0
    assert client.responses == []


def test_persistent_coordinator_validation_failure_uses_safe_clarification():
    client = FakeClient(["{", "still not json"])

    result = AssessmentCoordinator(client).run(round_state())

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["coordinator_repair_count"] == 1
    assert len(client.calls) == 2


def test_round_support_builds_one_candidate_and_specific_hint_per_issue():
    state = support_state()
    client = FakeClient([support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    candidate = result.values["revision_candidates"][0]
    assert candidate["goal_id"] == "goal_1"
    assert 2 <= len(candidate["hint"]["steps"]) <= 4
    assert candidate["hint"]["passage_reference"] == DEFAULT_REFERENCE
    assert candidate["hint"]["self_check"]
    assert "practice" not in candidate


def test_support_rejects_assigned_topic_replacement_field_then_repairs():
    state = support_state()
    invalid_candidate = candidate_for(state["issues"][0])
    invalid_candidate["hint"]["replacement_text"] = "Gardening makes students responsible citizens."
    invalid = support_payload(state, candidates=[invalid_candidate])
    client = FakeClient([invalid, support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert len(result.raw_responses) == 2
    assert "replacement_text" not in result.values["revision_candidates"][0]["hint"]


def test_hint_requires_two_to_four_steps_and_a_self_check():
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["steps"] = ["Why does this matter?"]
    invalid = support_payload(state, candidates=[candidate])
    client = FakeClient([invalid, support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert len(result.raw_responses) == 2


def test_abstract_sentence_starter_is_allowed_but_filled_frame_is_rejected():
    state = support_state()
    valid_candidate = candidate_for(state["issues"][0])
    valid_candidate["hint"]["sentence_starter"] = "This detail matters because ____."
    invalid_candidate = candidate_for(state["issues"][0])
    invalid_candidate["hint"]["sentence_starter"] = "Gardening teaches responsibility."
    client = FakeClient(
        [
            support_payload(state, candidates=[invalid_candidate]),
            support_payload(state, candidates=[valid_candidate]),
        ]
    )

    result = InstructionalSupportAgent(client).run(state)

    assert "____" in result.values["revision_candidates"][0]["hint"]["sentence_starter"]


def test_assigned_topic_frame_is_rejected_even_when_it_contains_blanks():
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["sentence_starter"] = (
        "Learning to care for plants could ____ because ____."
    )
    invalid = support_payload(state, candidates=[candidate])

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


def test_vocabulary_options_cannot_supply_numeric_evidence_answers():
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["vocabulary_options"] = ["31 of 50", "supports"]
    invalid = support_payload(state, candidates=[candidate])

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


def test_support_preserves_source_limitations_exactly():
    state = support_state()
    state["source_limitations"] = ["Add the passage so I can check the quotation."]
    invalid = support_payload(state, source_limitations=[])
    valid = support_payload(state)

    result = InstructionalSupportAgent(FakeClient([invalid, valid])).run(state)

    assert result.values["source_limitations"] == state["source_limitations"]


def test_revision_support_covers_every_selected_goal_and_status():
    state = support_state(revision=True)

    result = InstructionalSupportAgent(FakeClient([support_payload(state)])).run(state)

    assert len(result.values["goal_feedback"]) == 1
    assert result.values["goal_feedback"][0]["status"] == "specific_improvement"


def test_missing_selected_goal_observation_is_repaired():
    state = support_state(revision=True)
    invalid = support_payload(state, goal_feedback=[])

    result = InstructionalSupportAgent(FakeClient([invalid, support_payload(state)])).run(state)

    assert len(result.raw_responses) == 2
    assert len(result.values["goal_feedback"]) == 1


def test_deferred_self_report_is_sent_without_attempt_inference():
    state = support_state(revision=True)
    state["goal_self_reports"] = {"goal_1": "deferred"}
    client = FakeClient([support_payload(state)])

    InstructionalSupportAgent(client).run(state)

    prompt = client.calls[0][0][1]["content"]
    assert '"goal_1": "deferred"' in prompt
    assert "not attempted" not in prompt


def test_persistent_support_failure_produces_no_partial_feedback():
    state = support_state()
    invalid = support_payload(state, candidates=[])

    with pytest.raises(ResponseValidationError, match="after one correction"):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


@pytest.mark.parametrize(
    "claim",
    ["Your essay is ready to submit.", "You have mastered this skill.", "Score: 3/4"],
)
def test_support_rejects_readiness_mastery_and_scores(claim):
    state = support_state()
    invalid = support_payload(state, strengths=[claim])

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


def test_support_rejects_unverifiable_source_accuracy_claim():
    state = support_state()
    invalid = support_payload(state, strengths=["Your quotation looks correct."])

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


@pytest.mark.parametrize("framework", ["CER", "RACES", "MEAL"])
def test_teacher_framework_terminology_reaches_both_agents(framework):
    coordinator_state = round_state()
    coordinator_state["teacher_directions"] = f"Use {framework} for this response."
    coordinator_client = FakeClient([coordinator_payload(coordinator_state)])
    coordinator = AssessmentCoordinator(coordinator_client)
    assessment = coordinator.run(coordinator_state)
    handoff = {**coordinator_state, **assessment.values}
    support_client = FakeClient([support_payload(handoff)])

    InstructionalSupportAgent(support_client).run(handoff)

    assert framework in coordinator_client.calls[0][0][1]["content"]
    assert framework in support_client.calls[0][0][1]["content"]


def test_v3_state_has_no_affect_field_or_check_in():
    state = round_state()

    assert "affect_check_in" not in state
    assert not any("affect" in key for key in state)


def test_repair_metadata_records_latency_and_no_hidden_reasoning():
    state = support_state()
    invalid = support_payload(state, candidates=[])
    client = FakeClient([invalid, support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert result.model_calls[1]["schema_repair"] is True
    assert "latency_ms" in result.model_calls[1]
    assert "reasoning_content" not in json.dumps(result.model_calls)


def test_final_coordinator_and_support_use_verified_changes():
    state = final_state()
    coordinator_client = FakeClient([final_coordinator_payload(state)])
    assessment = AssessmentCoordinator(coordinator_client).run(state)
    state.update(assessment.values)
    support_client = FakeClient([final_support_payload(state)])

    result = InstructionalSupportAgent(support_client).run(state)

    assert result.values["final_reflection"]["improvements"][0]["finding_id"] == "improvement_1"
    assert "text_diff" in coordinator_client.calls[0][0][1]["content"]


def test_unchanged_final_comparison_cannot_invent_improvement():
    state = final_state(changed=False)
    invalid = final_coordinator_payload(state, changed=True)
    valid = final_coordinator_payload(state, changed=False)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["comparison_improvements"] == []
    assert result.values["coordinator_repair_count"] == 1


def test_final_reference_must_exist_in_actual_final_draft():
    state = final_state()
    invalid = final_coordinator_payload(state)
    raw = json.loads(invalid)
    raw["improvements"][0]["final_reference"] = "An invented sentence that is absent."
    valid = final_coordinator_payload(state)

    result = AssessmentCoordinator(FakeClient([json.dumps(raw), valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1


def test_final_support_cannot_hide_a_coordinator_regression():
    final = "Our school should start a garden."
    state = make_review_state(
        final,
        "6th Grade",
        review_mode="final",
        original_writing=INITIAL_DRAFT,
        revision_number=1,
        text_diff=build_text_diff(INITIAL_DRAFT, final),
    )
    regression = {
        "finding_id": "regression_1",
        "summary": "The final removes an essential explanation.",
        "original_reference": DEFAULT_REFERENCE,
        "final_reference": "",
        "goal_id": "goal_1",
    }
    coordinator_raw = final_coordinator_payload(
        state, changed=False, regressions=[regression]
    )
    assessment = AssessmentCoordinator(FakeClient([coordinator_raw])).run(state)
    state.update(assessment.values)
    invalid = json.loads(final_support_payload(state))
    invalid["regressions"] = []

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(
            FakeClient([json.dumps(invalid), json.dumps(invalid)])
        ).run(state)


def test_framework_prompt_assigns_coverage_to_coordinator_not_support():
    assert "assess every listed component" in COORDINATOR_ROUND_PROMPT
    assert "framework_coverage" in SUPPORT_ROUND_PROMPT
    assert "one candidate may cover several components" in SUPPORT_ROUND_PROMPT
    assert "Do not add components or issues" in SUPPORT_ROUND_PROMPT
    assert "make the candidate set collectively name RACES" not in SUPPORT_ROUND_PROMPT


def test_coordinator_prompt_distinguishes_author_position_from_student_claim():
    assert "the author's or source's position" in COORDINATOR_ROUND_PROMPT
    assert "student's own claim" in COORDINATOR_ROUND_PROMPT
    assert "does not by itself state" in COORDINATOR_ROUND_PROMPT


def test_omitted_optional_clarification_fields_do_not_trigger_repair():
    state = round_state()
    raw = json.loads(coordinator_payload(state))
    del raw["clarification_question"]
    del raw["clarification_choices"]
    client = FakeClient([json.dumps(raw)])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["routing_decision"] == "support_agent"
    assert result.values["coordinator_repair_count"] == 0
    assert result.values["clarification_question"] == ""
    assert result.values["clarification_choices"] == []
    assert len(client.calls) == 1


def test_coordinator_prompt_covers_unique_goals_regressions_and_nonobscuring_mechanics():
    assert "Every issue needs a unique goal_id" in COORDINATOR_ROUND_PROMPT
    assert "distinct new issue or regression needs a new goal_id" in COORDINATOR_ROUND_PROMPT
    assert "Do not ask clarification merely because" in COORDINATOR_ROUND_PROMPT
    assert "For every language_conventions issue" in COORDINATOR_ROUND_PROMPT
    assert "use direct_response if no meaningful issue remains" in COORDINATOR_ROUND_PROMPT


def test_optional_language_direction_rejects_nonobscuring_mechanics_goal():
    state = round_state()
    state["teacher_directions"] = (
        "Prioritize ideas and evidence. Language corrections are optional unless they obscure meaning."
    )
    issue = issue_for(
        state["writing"],
        category="language_conventions",
        description="An isolated article error is visible but does not obscure meaning.",
    )
    invalid = coordinator_payload(state, issues=[issue])
    valid = coordinator_payload(state, route="direct_response", issues=[])
    client = FakeClient([invalid, valid])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["routing_decision"] == "direct_response"
    assert result.values["coordinator_repair_count"] == 1


def test_missing_regression_field_defaults_to_false_without_repair():
    state = round_state()
    raw = json.loads(coordinator_payload(state))
    del raw["issues"][0]["regression"]
    client = FakeClient([json.dumps(raw)])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["issues"][0]["regression"] is False
    assert result.values["coordinator_repair_count"] == 0


def test_valid_coordinator_output_cannot_clear_a_teacher_flag():
    state = round_state()
    payload = coordinator_payload(
        state,
        route="direct_response",
        flag_teacher=True,
        teacher_flag_reason="",
        teacher_flag_category="none",
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["routing_decision"] == "teacher_review"
    assert result.values["flag_teacher"] is True
    assert result.values["teacher_flag_reason"]
    assert result.values["coordinator_repair_count"] == 0


def test_direct_coordinator_response_rejects_unverifiable_source_claims():
    state = round_state()
    invalid = coordinator_payload(
        state,
        route="direct_response",
        strengths=["Your quotation looks correct."],
    )
    valid = coordinator_payload(state, route="direct_response")

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["strengths"] == ["The draft has a clear position."]


def test_final_improvement_reference_must_overlap_changed_text():
    state = final_state()
    invalid = json.loads(final_coordinator_payload(state))
    invalid["improvements"][0]["final_reference"] = "Our school should start a garden."
    valid = final_coordinator_payload(state)

    result = AssessmentCoordinator(
        FakeClient([json.dumps(invalid), valid])
    ).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["comparison_improvements"][0]["final_reference"] == (
        "A new explanation."
    )


def test_final_validation_uses_actual_drafts_not_a_spoofed_diff_flag():
    state = final_state(changed=False)
    state["text_diff"]["changed"] = True
    invalid = final_coordinator_payload(state, changed=True)
    valid = final_coordinator_payload(state, changed=False)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["comparison_improvements"] == []


def framework_state(framework="RACES"):
    return make_review_state(
        INITIAL_DRAFT,
        "6th Grade",
        genre_selection="argument",
        framework_name=framework,
        framework_components=[],
    )


def coverage_for(state, status="present", goal_id="goal_1"):
    entries = []
    for component in state["framework_components"]:
        present = status == "present"
        entries.append(
            {
                "framework": state["framework_name"],
                "component": component,
                "status": status,
                "reference": DEFAULT_REFERENCE if present else "",
                "paragraph_number": 2 if present else None,
                "occurrence": 1 if present else None,
                "goal_id": "" if present else goal_id,
            }
        )
    return entries


def test_all_present_framework_components_allow_direct_response():
    state = framework_state()
    payload = coordinator_payload(
        state,
        route="direct_response",
        issues=[],
        framework_coverage=coverage_for(state),
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["routing_decision"] == "direct_response"
    assert len(result.values["framework_coverage"]) == 5
    assert result.values["coordinator_repair_count"] == 0


def test_multiple_framework_components_can_map_to_one_coordinator_issue():
    state = framework_state()
    payload = coordinator_payload(
        state, framework_coverage=coverage_for(state, status="issue")
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert len(result.values["issues"]) == 1
    assert len(result.values["framework_coverage"]) == 5
    assert {item["goal_id"] for item in result.values["framework_coverage"]} == {
        "goal_1"
    }


def test_missing_framework_component_triggers_bounded_repair():
    state = framework_state()
    valid_coverage = coverage_for(state, status="issue")
    invalid = coordinator_payload(
        state, framework_coverage=valid_coverage[:-1]
    )
    valid = coordinator_payload(state, framework_coverage=valid_coverage)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert len(result.values["framework_coverage"]) == 5


def test_framework_issue_must_reference_an_existing_goal():
    state = framework_state()
    invalid = coordinator_payload(
        state,
        framework_coverage=coverage_for(state, status="issue", goal_id="missing"),
    )
    valid = coordinator_payload(
        state, framework_coverage=coverage_for(state, status="issue")
    )

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1


def test_boundary_route_cannot_include_premature_framework_coverage():
    state = framework_state()
    invalid = coordinator_payload(
        state,
        route="ask_clarification",
        issues=[],
        framework_coverage=coverage_for(state),
    )
    valid = coordinator_payload(
        state, route="ask_clarification", issues=[], framework_coverage=[]
    )

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["framework_coverage"] == []


def test_framework_coverage_schema_supports_cer_without_new_fields():
    state = framework_state("CER")
    payload = coordinator_payload(
        state,
        route="direct_response",
        issues=[],
        framework_coverage=coverage_for(state),
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert [item["component"] for item in result.values["framework_coverage"]] == [
        "Claim",
        "Evidence",
        "Reasoning",
    ]


def test_obscuring_language_judgment_does_not_depend_on_description_keywords():
    state = round_state()
    state["teacher_directions"] = "Grammar fixes are optional."
    issue = issue_for(
        state["writing"],
        category="language_conventions",
        description="The pronoun leaves the reader uncertain which action it describes.",
        obscures_meaning=True,
    )
    payload = coordinator_payload(state, issues=[issue])

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["coordinator_repair_count"] == 0
    assert result.values["issues"][0]["obscures_meaning"] is True


def test_support_receives_framework_handoff_without_owning_coverage():
    state = framework_state()
    assessment = AssessmentCoordinator(
        FakeClient(
            [
                coordinator_payload(
                    state,
                    framework_coverage=coverage_for(state, status="issue"),
                )
            ]
        )
    ).run(state)
    state.update(assessment.values)
    client = FakeClient([support_payload(state)])

    InstructionalSupportAgent(client).run(state)

    prompt = client.calls[0][0][1]["content"]
    assert '"framework_coverage"' in prompt
    assert '"component": "Restate"' in prompt


def test_support_candidates_follow_coordinator_issue_order_deterministically():
    state = support_state()
    second_issue = issue_for(
        state["writing"], "Our school should start a garden.", "goal_2"
    )
    state["issues"] = [second_issue, state["issues"][0]]
    candidates = [candidate_for(issue) for issue in reversed(state["issues"])]

    result = InstructionalSupportAgent(
        FakeClient([support_payload(state, candidates=candidates)])
    ).run(state)

    assert [item["goal_id"] for item in result.values["revision_candidates"]] == [
        "goal_2",
        "goal_1",
    ]


def support_request_payload(client):
    return json.loads(client.calls[0][0][1]["content"].split("\n", 1)[1])


def test_support_source_payload_is_conditional_on_source_findings():
    state = support_state(source="A supplied passage.")
    client = FakeClient([support_payload(state)])
    InstructionalSupportAgent(client).run(state)
    assert "source_material" not in support_request_payload(client)

    state["issues"][0]["source_dependent"] = True
    state["issues"][0]["source_location"] = "paragraph 1"
    client = FakeClient([support_payload(state)])
    InstructionalSupportAgent(client).run(state)
    assert support_request_payload(client)["source_material"] == "A supplied passage."


def test_support_omits_empty_clarification_history_only_on_revision():
    state = support_state(revision=True)
    client = FakeClient([support_payload(state)])
    InstructionalSupportAgent(client).run(state)
    assert "clarification_history" not in support_request_payload(client)

    state["clarification_history"] = [{"question": "Genre?", "answer": "Argument"}]
    client = FakeClient([support_payload(state)])
    InstructionalSupportAgent(client).run(state)
    assert support_request_payload(client)["clarification_history"] == [
        {"question": "Genre?", "answer": "Argument"}
    ]


def test_final_support_passes_through_verified_fields_without_regenerating_them():
    state = final_state()
    state["original_strengths"] = ["The original has a clear position."]
    state["future_areas"] = ["Consider the reader's next question."]
    client = FakeClient([final_support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert "original_strengths" not in json.loads(result.raw_response)
    assert "future_possibilities" not in json.loads(result.raw_response)
    assert result.values["final_reflection"]["original_strengths"] == [
        "The original has a clear position."
    ]
    assert result.values["final_reflection"]["future_possibilities"] == [
        "Consider the reader's next question."
    ]


def test_accuracy_tier_findings_rank_first_regardless_of_goal():
    state = round_state()
    accuracy_issue = issue_for(
        state["writing"],
        reference="Our school should start a garden.",
        goal_id="goal_accuracy",
        finding_severity="accuracy",
        category="source_use",
        description="This claim is not supported by the source.",
    )
    reasoning_issue = issue_for(
        state["writing"],
        goal_id="goal_reasoning",
        finding_severity="reasoning",
        description="The connection needs more explanation.",
    )
    development_issue = issue_for(
        state["writing"],
        reference="should start a garden.",
        goal_id="goal_development",
        finding_severity="development",
        category="evidence_elaboration",
        description="Add more specific details.",
    )
    # Submit in non-severity order: development, reasoning, accuracy
    payload = coordinator_payload(
        state, issues=[development_issue, reasoning_issue, accuracy_issue]
    )
    client = FakeClient([payload])

    result = AssessmentCoordinator(client).run(state)

    # Verify accuracy ranks first, then reasoning, then development
    assert len(result.values["issues"]) == 3
    assert result.values["issues"][0]["goal_id"] == "goal_accuracy"
    assert result.values["issues"][0]["finding_severity"] == "accuracy"
    assert result.values["issues"][1]["goal_id"] == "goal_reasoning"
    assert result.values["issues"][1]["finding_severity"] == "reasoning"
    assert result.values["issues"][2]["goal_id"] == "goal_development"
    assert result.values["issues"][2]["finding_severity"] == "development"


def test_reasoning_operation_classification_guides_starter_selection():
    state = support_state()
    causal_issue = issue_for(
        state["writing"],
        goal_id="goal_causal",
        finding_severity="reasoning",
        reasoning_operation="causal",
        description="Explain why this leads to responsibility.",
    )
    state["issues"] = [causal_issue]
    client = FakeClient([support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    candidate = result.values["revision_candidates"][0]
    starter = candidate["hint"]["sentence_starter"].lower()
    # Causal operations should use "because" or "matters because" starters
    assert "because" in starter or starter == ""


def test_finding_severity_is_required_and_validated():
    state = round_state()
    issue = issue_for(state["writing"])
    del issue["finding_severity"]
    invalid = coordinator_payload(state, issues=[issue])
    valid_issue = issue_for(state["writing"], finding_severity="reasoning")
    valid = coordinator_payload(state, issues=[valid_issue])
    client = FakeClient([invalid, valid])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["issues"][0]["finding_severity"] in [
        "accuracy",
        "reasoning",
        "development",
    ]


def test_reasoning_operation_defaults_to_none_when_not_specified():
    state = round_state()
    issue = issue_for(state["writing"], finding_severity="development")
    # reasoning_operation should default to "none" if not specified
    payload = coordinator_payload(state, issues=[issue])
    client = FakeClient([payload])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["issues"][0]["reasoning_operation"] == "none"


def test_multiple_accuracy_findings_preserve_pedagogical_order():
    state = round_state()
    fabricated = issue_for(
        state["writing"],
        reference="Our school should start a garden.",
        goal_id="goal_fabricated",
        finding_severity="accuracy",
        category="evidence_elaboration",
        description="This detail is invented and not in the source.",
    )
    mischaracterized = issue_for(
        state["writing"],
        reference="It would teach responsibility.",
        goal_id="goal_mischaracterized",
        finding_severity="accuracy",
        category="source_use",
        description="This misrepresents what the source says.",
    )
    # Both are accuracy-tier; order should be preserved within tier
    payload = coordinator_payload(state, issues=[fabricated, mischaracterized])
    client = FakeClient([payload])

    result = AssessmentCoordinator(client).run(state)

    assert len(result.values["issues"]) == 2
    assert all(issue["finding_severity"] == "accuracy" for issue in result.values["issues"])
    assert result.values["issues"][0]["goal_id"] == "goal_fabricated"
    assert result.values["issues"][1]["goal_id"] == "goal_mischaracterized"
