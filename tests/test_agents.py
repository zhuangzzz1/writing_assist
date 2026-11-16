import json

import pytest

from agents.assessment_coordinator import (
    AssessmentCoordinator,
    IssueOutput,
    build_prior_findings,
)
from agents.prompts import (
    BASELINE_READABLE_COORDINATOR_ROUND_PROMPT,
    BASELINE_READABLE_SUPPORT_PROMPT,
    BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT,
    BASELINE_READABLE_V2_COORDINATOR_ROUND_PROMPT,
    BASELINE_READABLE_V2_SUPPORT_PROMPT,
    COORDINATOR_FINAL_PROMPT,
    COORDINATOR_ROUND_PROMPT,
    REGRESSION_READABLE_COORDINATOR_FINAL_PROMPT,
    REGRESSION_READABLE_COORDINATOR_ROUND_PROMPT,
    REGRESSION_READABLE_SUPPORT_PROMPT,
    STRUCTURAL_COORDINATOR_FINAL_PROMPT,
    STRUCTURAL_COORDINATOR_ROUND_PROMPT,
    STRUCTURAL_SUPPORT_ROUND_PROMPT,
    SUPPORT_ROUND_CONSOLIDATED_PROMPT,
    SUPPORT_ROUND_PROMPT,
    V3_7_1_COORDINATOR_FINAL_PROMPT,
    V3_7_1_COORDINATOR_ROUND_PROMPT,
    V3_7_1_SUPPORT_ROUND_PROMPT,
)
from agents.support_agent import InstructionalSupportAgent
from agents.utils import PROMPT_VERSION, ResponseValidationError
from langgraph_core.revision import build_text_diff, draft_sha256
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


def attach_final_history(state, status, reference="A new explanation."):
    state["revision_history"] = [
        {
            "revision_number": 1,
            "snapshot_id": "snapshot_1",
            "reviewed_round_id": "round_1",
            "reviewed_draft_sha256": draft_sha256(state["writing"]),
            "selected_goals": [
                {
                    "goal_id": "goal_1",
                    "draft_reference": reference,
                    "paragraph_number": 3,
                    "occurrence": 1,
                    "status": status,
                    "observation": "The latest Coordinator verdict for this goal.",
                    "evidence_reference": reference,
                    "carry_forward": status != "specific_improvement",
                }
            ],
        }
    ]
    return state


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
    assert 3 <= len(candidate["hint"]["steps"]) <= 5
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


@pytest.mark.parametrize("step_count", [2, 6])
def test_hint_rejects_counts_outside_three_to_five(step_count):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["steps"] = [
        f"Use your own words for thinking step {index}."
        for index in range(step_count)
    ]
    invalid = support_payload(state, candidates=[candidate])
    client = FakeClient([invalid, support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert len(result.raw_responses) == 2


@pytest.mark.parametrize("step_count", [3, 4, 5])
def test_hint_accepts_three_to_five_total_steps(step_count):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["steps"] = [
        f"Use your own words for thinking step {index}."
        for index in range(step_count)
    ]

    result = InstructionalSupportAgent(
        FakeClient([support_payload(state, candidates=[candidate])])
    ).run(state)

    assert len(result.values["revision_candidates"][0]["hint"]["steps"]) == step_count
    assert len(result.raw_responses) == 1


@pytest.mark.parametrize(
    "starter",
    [
        "This detail matters because ____.",
        "This evidence matters because ____.",
        "This matters because ____.",
        "____ because ____.",
        "According to the survey, ____.",
    ],
)
def test_legacy_abstract_starters_are_accepted_without_repair(starter):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["sentence_starter"] = starter
    client = FakeClient([support_payload(state, candidates=[candidate], legacy=True)])

    result = InstructionalSupportAgent(client, legacy_contract=True).run(state)

    assert result.values["revision_candidates"][0]["hint"]["sentence_starter"] == starter
    assert len(result.raw_responses) == 1


@pytest.mark.parametrize(
    "starter",
    [
        "Gardening teaches responsibility.",
        "Learning to care for plants could ____ because ____.",
        "This connects to becoming a better citizen because ____.",
        "This evidence/detail matters because ____.",
    ],
)
def test_legacy_on_topic_or_completed_starters_require_bounded_repair(starter):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["sentence_starter"] = starter
    invalid = support_payload(state, candidates=[candidate], legacy=True)
    client = FakeClient([invalid, support_payload(state, legacy=True)])

    result = InstructionalSupportAgent(client, legacy_contract=True).run(state)

    assert len(result.raw_responses) == 2
    assert result.values["revision_candidates"][0]["hint"]["sentence_starter"] == ""


@pytest.mark.parametrize("field", ["stuck_step", "hint_step"])
def test_completion_placeholders_in_instructional_fields_require_bounded_repair(field):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    if field == "stuck_step":
        candidate["stuck_step"] = "Sarah had so much homework that..."
    else:
        candidate["hint"]["steps"][1] = "Explain ____ in your own words."
    invalid = support_payload(state, candidates=[candidate])
    client = FakeClient([invalid, support_payload(state)])

    result = InstructionalSupportAgent(client).run(state)

    assert len(result.raw_responses) == 2
    assert result.values["revision_candidates"][0]["stuck_step"]


def test_scaffold_authorship_prompt_covers_every_scaffold_field():
    assert "every candidate action, hint step, self-check" in SUPPORT_ROUND_PROMPT
    assert "without listing likely target causes" in SUPPORT_ROUND_PROMPT
    assert "Question form does not make a supplied answer acceptable" in SUPPORT_ROUND_PROMPT
    assert "Keep concrete-first, linked process specificity" in SUPPORT_ROUND_PROMPT
    assert "do not offer 'focus less,' 'miss instructions,' 'make mistakes,'" in SUPPORT_ROUND_PROMPT
    assert "Never place completion blanks" in SUPPORT_ROUND_PROMPT
    assert "Was Sarah too tired or out of time?" in SUPPORT_ROUND_PROMPT


def test_legacy_vocabulary_options_cannot_supply_numeric_evidence_answers():
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["vocabulary_options"] = ["31 of 50", "supports"]
    invalid = support_payload(state, candidates=[candidate], legacy=True)

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(
            FakeClient([invalid, invalid]), legacy_contract=True
        ).run(state)


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


@pytest.mark.parametrize("status", ["improvement_not_yet_evident", "uncertain"])
def test_final_rejects_same_unchanged_goal_improvement_after_negative_verdict(status):
    state = attach_final_history(final_state(), status)
    invalid = final_coordinator_payload(state)
    valid = final_coordinator_payload(state, changed=False)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["comparison_improvements"] == []


def test_final_allows_same_unchanged_goal_after_prior_specific_improvement():
    state = attach_final_history(final_state(), "specific_improvement")

    result = AssessmentCoordinator(
        FakeClient([final_coordinator_payload(state)])
    ).run(state)

    assert result.values["coordinator_repair_count"] == 0
    assert len(result.values["comparison_improvements"]) == 1


def test_final_allows_unrelated_improvement_and_does_not_infer_empty_goal_id():
    state = attach_final_history(final_state(), "improvement_not_yet_evident")
    state["writing"] += "\n\nA separate new detail."
    state["text_diff"] = build_text_diff(INITIAL_DRAFT, state["writing"])
    unrelated = final_coordinator_payload(state)
    result = AssessmentCoordinator(FakeClient([unrelated])).run(state)
    assert result.values["coordinator_repair_count"] == 0

    same_text_without_goal = json.loads(final_coordinator_payload(state))
    same_text_without_goal["improvements"][0]["final_reference"] = "A new explanation."
    same_text_without_goal["improvements"][0]["goal_id"] = ""
    result = AssessmentCoordinator(
        FakeClient([json.dumps(same_text_without_goal)])
    ).run(state)
    assert result.values["coordinator_repair_count"] == 0


def test_final_prior_verdict_guard_requires_latest_review_of_same_draft():
    state = attach_final_history(final_state(), "improvement_not_yet_evident")
    state["revision_history"][0]["reviewed_draft_sha256"] = "different-draft"

    result = AssessmentCoordinator(
        FakeClient([final_coordinator_payload(state)])
    ).run(state)

    assert result.values["coordinator_repair_count"] == 0


def test_final_rejects_deletion_claim_when_exact_opening_remains():
    original = "Our school should start later.\n\nAn old explanation."
    final = "Our school should start later.\n\nA different explanation."
    state = make_review_state(
        final,
        "6th Grade",
        review_mode="final",
        original_writing=original,
        revision_number=1,
        text_diff=build_text_diff(original, final),
    )
    regression = {
        "finding_id": "regression_1",
        "summary": "The later-start proposal was deleted from the Final draft.",
        "original_reference": "Our school should start later.",
        "final_reference": "A different explanation.",
        "goal_id": "goal_1",
    }
    invalid = final_coordinator_payload(state, regressions=[regression])
    valid = final_coordinator_payload(state, regressions=[])

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["comparison_regressions"] == []


def test_final_exact_deletion_guard_does_not_reject_semantic_weakening():
    original = "Our school should start later.\n\nAn old explanation."
    final = "Our school should start later.\n\nA different explanation."
    state = make_review_state(
        final,
        "6th Grade",
        review_mode="final",
        original_writing=original,
        revision_number=1,
        text_diff=build_text_diff(original, final),
    )
    regression = {
        "finding_id": "regression_1",
        "summary": "The explanation of the later-start proposal is weaker.",
        "original_reference": "Our school should start later.",
        "final_reference": "A different explanation.",
        "goal_id": "goal_1",
    }

    result = AssessmentCoordinator(
        FakeClient([final_coordinator_payload(state, regressions=[regression])])
    ).run(state)

    assert result.values["coordinator_repair_count"] == 0


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


def test_accuracy_partition_preserves_all_nonaccuracy_coordinator_order():
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
    # The supported development concern remains ahead of unrelated reasoning.
    payload = coordinator_payload(
        state, issues=[development_issue, reasoning_issue, accuracy_issue]
    )
    client = FakeClient([payload])

    result = AssessmentCoordinator(client).run(state)

    assert [issue["goal_id"] for issue in result.values["issues"]] == [
        "goal_accuracy",
        "goal_development",
        "goal_reasoning",
    ]


def test_v3_8_support_contract_rejects_removed_scaffold_fields():
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["hint"]["vocabulary_options"] = []
    candidate["hint"]["sentence_starter"] = ""
    invalid = support_payload(state, candidates=[candidate])

    with pytest.raises(ResponseValidationError):
        InstructionalSupportAgent(FakeClient([invalid, invalid])).run(state)


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


def test_legacy_reasoning_operation_defaults_to_none_when_not_specified():
    state = round_state()
    issue = issue_for(state["writing"], finding_severity="development")
    payload = coordinator_payload(state, issues=[issue], legacy=True)

    result = AssessmentCoordinator(
        FakeClient([payload]), legacy_contract=True
    ).run(state)

    assert result.values["issues"][0]["reasoning_operation"] == "none"


def test_v3_8_coordinator_contract_rejects_reasoning_operation():
    state = round_state()
    issue = issue_for(state["writing"], reasoning_operation="causal")
    invalid = coordinator_payload(state, issues=[issue])
    valid = coordinator_payload(state)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert "reasoning_operation" not in result.values["issues"][0]


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


def test_prior_findings_serializer_is_bounded_and_preserves_selection_status():
    state = make_review_state(INITIAL_DRAFT, "6th Grade")
    first = issue_for(INITIAL_DRAFT, "Our school should start a garden.", "goal_1")
    second = issue_for(INITIAL_DRAFT, DEFAULT_REFERENCE, "goal_2")
    third = issue_for(INITIAL_DRAFT, DEFAULT_REFERENCE, "goal_3", occurrence=2)
    state["issues"] = [first, second, third]
    state["selected_goals"] = [candidate_for(first), candidate_for(second)]
    state["goal_self_reports"] = {"goal_2": "deferred"}

    findings = build_prior_findings(state)

    assert [item["selection_status"] for item in findings] == [
        "selected",
        "deferred",
        "unselected",
    ]
    assert set(findings[0]) == {
        "goal_id",
        "category",
        "severity",
        "description",
        "draft_reference",
        "paragraph_number",
        "occurrence",
        "selection_status",
    }
    assert findings[0]["severity"] == first["finding_severity"]
    assert json.dumps(findings, sort_keys=True) == json.dumps(
        build_prior_findings(state), sort_keys=True
    )
    assert "execution_logs" not in json.dumps(findings)
    assert "coordinator_reasoning" not in json.dumps(findings)


def test_prior_findings_are_excluded_by_default_and_exact_in_history_arm():
    selected = candidate_for(issue_for(INITIAL_DRAFT))
    state = make_review_state(
        INITIAL_DRAFT,
        "6th Grade",
        original_writing=INITIAL_DRAFT,
        previous_writing=INITIAL_DRAFT,
        revision_number=1,
        selected_goals=[selected],
        text_diff=build_text_diff(INITIAL_DRAFT, INITIAL_DRAFT),
    )
    prior = [
        {
            "goal_id": "goal_1",
            "category": "evidence_elaboration",
            "severity": "reasoning",
            "description": "The connection needs more explanation.",
            "draft_reference": DEFAULT_REFERENCE,
            "paragraph_number": 2,
            "occurrence": 1,
            "selection_status": "selected",
        }
    ]
    state["prior_findings"] = prior
    response = coordinator_payload(state, observations=[observation_for()])
    default_client = FakeClient([response])
    history_client = FakeClient([response])

    AssessmentCoordinator(default_client).run(state)
    AssessmentCoordinator(history_client, include_prior_findings=True).run(state)

    default_payload = json.loads(default_client.calls[0][0][1]["content"].split("\n", 1)[1])
    history_payload = json.loads(history_client.calls[0][0][1]["content"].split("\n", 1)[1])
    assert "prior_findings" not in default_payload
    assert history_payload["prior_findings"] == prior



def test_speculative_process_guidance_preserves_imagination_and_source_boundaries():
    assert "SPECULATIVE PROCESS AND SYSTEM EXPLANATIONS" in COORDINATOR_ROUND_PROMPT
    assert "not fabricated evidence merely because they are invented" in COORDINATOR_ROUND_PROMPT
    assert "trace a material or output already named in the draft" in COORDINATOR_ROUND_PROMPT
    assert "Do not name possible destinations, mechanisms, or solutions" in COORDINATOR_ROUND_PROMPT
    assert "Do not certify that a proposed design works" in COORDINATOR_ROUND_PROMPT
    assert "do not impose source requirements on every imaginative task" in COORDINATOR_ROUND_PROMPT
    assert "Do not manufacture transition or conclusion goals" in COORDINATOR_ROUND_PROMPT


def test_v3_8_runtime_prompts_remove_scaffolds_and_preserve_legacy_controls():
    assert "reasoning_operation" not in COORDINATOR_ROUND_PROMPT
    assert "vocabulary_options" not in SUPPORT_ROUND_PROMPT
    assert "sentence_starter" not in SUPPORT_ROUND_PROMPT
    assert "reasoning_operation" in V3_7_1_COORDINATOR_ROUND_PROMPT
    assert "vocabulary_options" in V3_7_1_SUPPORT_ROUND_PROMPT
    assert "sentence_starter" in V3_7_1_SUPPORT_ROUND_PROMPT
    assert "revision_history" in COORDINATOR_FINAL_PROMPT
    assert "revision_history" not in V3_7_1_COORDINATOR_FINAL_PROMPT


def test_readable_support_candidate_uses_budgets_and_distinct_field_jobs():
    prompt = BASELINE_READABLE_SUPPORT_PROMPT
    assert "PLAIN-LANGUAGE DELIVERY" in prompt
    assert "title: 3-6 plain words" in prompt
    assert "approximately 25 words total" in prompt
    assert "approximately 15 words per sentence" in prompt
    assert "approximately 18 words per step" in prompt
    assert "same writing move as revision_action" in prompt
    assert "one smaller immediate action" in prompt
    assert "PLAIN-ENGLISH GROUNDING" in prompt
    assert "CLAIM ANCHORING" not in prompt
    assert "First: explain what 62%" not in prompt
    assert "circle the first tap" in prompt
    assert "SOURCE-BOUND ELABORATION" in prompt
    assert "do not ask the student to supply a real-world function" in prompt
    assert "development-level relevance finding" in prompt
    assert "Use second-person 'you' and 'your'" in prompt
    assert "vocabulary_options" not in prompt
    assert "sentence_starter" not in prompt
    assert "PLAIN-LANGUAGE DELIVERY" not in STRUCTURAL_SUPPORT_ROUND_PROMPT


def test_readable_candidate_mocked_revision_handoff_preserves_contract():
    state = support_state(revision=True, source="The supplied survey included 50 students.")
    state["source_limitations"] = ["Check only the supplied survey text."]
    payload = support_payload(state)
    client = FakeClient([payload])

    result = InstructionalSupportAgent(
        client, round_prompt=BASELINE_READABLE_SUPPORT_PROMPT
    ).run(state)

    candidate = result.values["revision_candidates"][0]
    assert candidate["goal_id"] == state["issues"][0]["goal_id"]
    assert candidate["draft_reference"] == state["issues"][0]["draft_reference"]
    assert candidate["hint"]["passage_reference"] == candidate["draft_reference"]
    assert result.values["goal_feedback"][0]["status"] == "specific_improvement"
    assert result.values["source_limitations"] == state["source_limitations"]
    assert "vocabulary_options" not in candidate["hint"]
    assert "sentence_starter" not in candidate["hint"]
    assert client.calls[0][0][0]["content"] == BASELINE_READABLE_SUPPORT_PROMPT


def test_grounding_candidate_addresses_strong_drafts_and_synthetic_classroom_context():
    prompt = BASELINE_READABLE_COORDINATOR_ROUND_PROMPT
    assert "no meaningful actionable issue remains" in prompt
    assert "Do not create optional expansion" in prompt
    assert "classroom or shared task context" in prompt
    assert "identifies it as synthetic" in prompt
    assert "bounded development-level elaboration issue" in prompt
    assert "Genuine fabricated evidence" in prompt
    assert "EVALUATION CANDIDATE" not in COORDINATOR_ROUND_PROMPT


def test_grounding_candidate_does_not_force_strong_draft_route():
    writing = (
        "Our school should add a quiet reading period. During a recent synthetic "
        "class discussion, several students said interruptions made reading difficult. "
        "A scheduled period would protect time for sustained reading."
    )
    state = make_review_state(writing, "6th Grade", genre_selection="argument")
    direct = coordinator_payload(state, route="direct_response", issues=[])

    result = AssessmentCoordinator(
        FakeClient([direct]),
        round_prompt=BASELINE_READABLE_COORDINATOR_ROUND_PROMPT,
    ).run(state)

    assert result.values["routing_decision"] == "direct_response"
    assert result.values["issues"] == []


def test_grounding_candidate_allows_bounded_discussion_development_finding():
    writing = (
        "Our school should add a quiet reading period. A class discussion showed "
        "that interruptions are a problem. This proves the period will help everyone."
    )
    state = make_review_state(writing, "6th Grade", genre_selection="argument")
    issue = issue_for(
        writing,
        "A class discussion showed that interruptions are a problem.",
        finding_severity="development",
        description="The attribution needs enough context for the reader to understand the discussion.",
    )
    payload = coordinator_payload(state, issues=[issue])

    result = AssessmentCoordinator(
        FakeClient([payload]),
        round_prompt=BASELINE_READABLE_COORDINATOR_ROUND_PROMPT,
    ).run(state)

    assert result.values["issues"][0]["finding_severity"] == "development"
    assert result.values["issues"][0]["source_dependent"] is False


def test_support_guidance_combines_reader_questions_with_bounded_language_instruction():
    assert "actual reader effect or unanswered reader question" in SUPPORT_ROUND_PROMPT
    assert "must not name the student's target answer" in SUPPORT_ROUND_PROMPT
    assert "teach one recognizable pattern concisely" in SUPPORT_ROUND_PROMPT
    assert "The student must perform the revision" in SUPPORT_ROUND_PROMPT
    assert "do not rewrite the complete sentence or paragraph" in SUPPORT_ROUND_PROMPT
    assert "do not supply a list of spelling answers" in SUPPORT_ROUND_PROMPT
    assert "never ask the student to capitalize a word that is already capitalized" in SUPPORT_ROUND_PROMPT
    assert "Never instruct the student to begin with a supplied on-topic phrase" in SUPPORT_ROUND_PROMPT
    assert "Routine spelling belongs in the editor's spellcheck" in COORDINATOR_ROUND_PROMPT
    assert "distraction or slower reading alone does not establish obscured meaning" in COORDINATOR_ROUND_PROMPT



def test_reference_guidance_counts_standalone_title_blocks():
    assert "including a standalone title" in COORDINATOR_ROUND_PROMPT
    assert "the first prose paragraph is paragraph 2" in COORDINATOR_ROUND_PROMPT
    assert "Locate the exact quoted reference in the full draft" in COORDINATOR_ROUND_PROMPT



def test_unique_exact_issue_reference_is_normalized_without_model_repair():
    writing = "My System\n\nThe opening gives a purpose.\n\nA unique process step."
    state = make_review_state(writing, "5th Grade", genre_selection="informational")
    issue = issue_for(
        writing,
        "A unique process step.",
        paragraph_number=2,
    )
    client = FakeClient([coordinator_payload(state, issues=[issue])])

    result = AssessmentCoordinator(client).run(state)

    assert result.values["routing_decision"] == "support_agent"
    assert result.values["coordinator_repair_count"] == 0
    assert result.values["issues"][0]["paragraph_number"] == 3
    assert result.values["issues"][0]["occurrence"] == 1
    assert result.values["coordinator_reference_normalizations"] == [
        {
            "goal_id": "goal_1",
            "previous_paragraph_number": 2,
            "previous_occurrence": 1,
            "paragraph_number": 3,
            "occurrence": 1,
        }
    ]
    assert len(client.calls) == 1


def test_ambiguous_repeated_reference_still_requires_bounded_repair():
    writing = "My System\n\nSame idea.\n\nSame idea."
    state = make_review_state(writing, "5th Grade", genre_selection="informational")
    invalid_issue = issue_for(writing, "Same idea.", paragraph_number=1)
    valid_issue = issue_for(writing, "Same idea.", paragraph_number=2)
    client = FakeClient(
        [
            coordinator_payload(state, issues=[invalid_issue]),
            coordinator_payload(state, issues=[valid_issue]),
        ]
    )

    result = AssessmentCoordinator(client).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["issues"][0]["paragraph_number"] == 2
    assert result.values["coordinator_reference_normalizations"] == []
    assert len(client.calls) == 2



def test_phase_one_prompt_and_schema_contracts_are_aligned():
    assert "3-5 total steps: one concept restatement followed by 2-4 procedural steps" in SUPPORT_ROUND_PROMPT
    assert "3-5 total items" in SUPPORT_ROUND_PROMPT
    assert "regression=true" in COORDINATOR_ROUND_PROMPT
    assert "regressions=true" not in COORDINATOR_ROUND_PROMPT
    assert "clarification_limit yourself" in COORDINATOR_ROUND_PROMPT
    assert '"none | concerning_content | serious_discouragement | clarification_limit"' not in COORDINATOR_ROUND_PROMPT
    assert "addresses_student_concern" not in IssueOutput.model_fields


def test_revision_accuracy_partition_keeps_supported_development_concern_next():
    state = support_state(revision=True)
    state["student_concerns"] = "I want help making my garden reason more specific."
    accuracy = issue_for(
        state["writing"],
        "Our school should start a garden.",
        "goal_accuracy",
        finding_severity="accuracy",
        category="source_use",
    )
    concern = issue_for(
        state["writing"],
        DEFAULT_REFERENCE,
        "goal_concern",
        finding_severity="development",
    )
    reasoning = issue_for(
        state["writing"],
        "Students learn to notice what their community needs.",
        "goal_reasoning",
        finding_severity="reasoning",
    )
    state["selected_goals"] = [candidate_for(concern)]
    observations = [observation_for("goal_concern")]
    payload = coordinator_payload(
        state,
        issues=[concern, reasoning, accuracy],
        observations=observations,
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert [issue["goal_id"] for issue in result.values["issues"]] == [
        "goal_accuracy",
        "goal_concern",
        "goal_reasoning",
    ]
    assert result.values["coordinator_repair_count"] == 0


def test_unsupported_concern_does_not_change_nonaccuracy_order():
    state = round_state()
    state["student_concerns"] = "I want help with a conclusion, but my draft has no conclusion problem."
    reasoning = issue_for(state["writing"], goal_id="goal_reasoning")
    development = issue_for(
        state["writing"],
        "Our school should start a garden.",
        "goal_development",
        finding_severity="development",
    )
    payload = coordinator_payload(state, issues=[reasoning, development])

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert [issue["goal_id"] for issue in result.values["issues"]] == [
        "goal_reasoning",
        "goal_development",
    ]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("strengths", ["Premature strength"]),
        ("issues", [issue_for(INITIAL_DRAFT)]),
        (
            "framework_coverage",
            [
                {
                    "framework": "CER",
                    "component": "Claim",
                    "status": "present",
                    "reference": DEFAULT_REFERENCE,
                    "paragraph_number": 2,
                    "occurrence": 1,
                    "goal_id": "",
                }
            ],
        ),
        ("source_limitations", ["Premature source limitation"]),
        ("selected_goal_observations", [observation_for()]),
    ],
)
@pytest.mark.parametrize("route", ["ask_clarification", "teacher_review"])
def test_boundary_routes_reject_ordinary_assessment_collections(route, field, value):
    state = round_state()
    invalid_raw = json.loads(coordinator_payload(state, route=route))
    invalid_raw[field] = value
    invalid = json.dumps(invalid_raw)
    valid = coordinator_payload(state, route=route)

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["routing_decision"] == route
    expected_repairs = 0 if route == "teacher_review" else 1
    assert result.values["coordinator_repair_count"] == expected_repairs
    for collection in (
        "strengths",
        "issues",
        "framework_coverage",
        "source_limitations",
        "selected_goal_observations",
    ):
        assert result.values[collection] == []


def test_teacher_review_permits_empty_genre_without_repair():
    state = round_state()
    payload = coordinator_payload(state, route="teacher_review")

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["working_genre"] == ""
    assert result.values["genre_confidence"] == ""
    assert result.values["genre_basis"] == ""
    assert result.values["coordinator_repair_count"] == 0


def test_unrelated_clarification_retains_working_genre():
    state = round_state()
    payload = coordinator_payload(
        state,
        route="ask_clarification",
        clarification_question="Which part of the assignment should I use?",
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["working_genre"] == "argument"
    assert result.values["genre_confidence"] == "high"
    assert result.values["genre_basis"]


def test_revision_route_still_requires_each_selected_goal_observation():
    state = support_state(revision=True)
    invalid = coordinator_payload(state, observations=[])
    valid = coordinator_payload(state, observations=[observation_for()])

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert len(result.values["selected_goal_observations"]) == 1


def test_model_selected_clarification_limit_is_neutralized_before_teacher_review():
    state = round_state()
    payload = coordinator_payload(
        state,
        route="teacher_review",
        teacher_flag_category="clarification_limit",
        teacher_flag_reason="The model requested an early clarification limit.",
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["flag_teacher"] is False
    assert result.values["teacher_flag_category"] == "none"
    assert result.values["clarification_question"]
    assert result.values["coordinator_repair_count"] == 0


def test_malformed_clarification_limit_never_becomes_concerning_content():
    state = round_state()
    raw = json.dumps(
        {
            "flag_teacher": True,
            "routing_decision": "teacher_review",
            "teacher_flag_category": "clarification_limit",
        }
    )

    result = AssessmentCoordinator(FakeClient([raw, raw])).run(state)

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["teacher_flag_category"] == "none"
    assert result.values["flag_teacher"] is False


def test_final_prompt_grounds_source_and_framework_claims():
    assert "Use only supplied source material" in COORDINATOR_FINAL_PROMPT
    assert "Do not invent framework requirements" in COORDINATOR_FINAL_PROMPT
    assert "preserve" in COORDINATOR_FINAL_PROMPT.lower() or "uncertainty" in COORDINATOR_FINAL_PROMPT


def test_final_missing_source_rejects_accuracy_claim_but_supplied_source_is_bounded():
    state = final_state()
    invalid = final_coordinator_payload(
        state, future_areas=["The fact is accurate."]
    )
    with pytest.raises(ResponseValidationError):
        AssessmentCoordinator(FakeClient([invalid, invalid])).run(state)

    state["source_material_available"] = True
    state["source_material"] = "The supplied passage states the relevant fact."
    result = AssessmentCoordinator(FakeClient([invalid])).run(state)
    assert result.values["coordinator_repair_count"] == 0



def unique_framework_state(writing):
    return make_review_state(
        writing,
        "6th Grade",
        genre_selection="argument",
        framework_name="Custom",
        framework_components=["Claim"],
    )


def single_present_coverage(reference, paragraph_number, occurrence=1):
    return [
        {
            "framework": "Custom",
            "component": "Claim",
            "status": "present",
            "reference": reference,
            "paragraph_number": paragraph_number,
            "occurrence": occurrence,
            "goal_id": "",
        }
    ]


def test_unique_present_framework_title_location_is_normalized_without_repair():
    writing = "My Garden\n\nOur school should start a garden.\n\nIt would teach responsibility."
    state = unique_framework_state(writing)
    issue = issue_for(writing)
    coverage = single_present_coverage(DEFAULT_REFERENCE, 2)
    payload = coordinator_payload(state, issues=[issue], framework_coverage=coverage)

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["framework_coverage"][0]["paragraph_number"] == 3
    assert result.values["coordinator_repair_count"] == 0
    assert result.values["coordinator_reference_normalizations"] == []
    assert result.values["coordinator_framework_normalizations"] == [
        {
            "framework": "Custom",
            "component": "Claim",
            "previous_paragraph_number": 2,
            "previous_occurrence": 1,
            "paragraph_number": 3,
            "occurrence": 1,
        }
    ]


def test_valid_present_framework_location_is_unchanged():
    state = unique_framework_state(INITIAL_DRAFT)
    payload = coordinator_payload(
        state, framework_coverage=single_present_coverage(DEFAULT_REFERENCE, 2)
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["framework_coverage"][0]["paragraph_number"] == 2
    assert result.values["coordinator_framework_normalizations"] == []
    assert result.values["coordinator_repair_count"] == 0


@pytest.mark.parametrize(
    ("writing", "reference", "valid_paragraph"),
    [
        ("Same claim.\n\nSame claim.", "Same claim.", 2),
        (INITIAL_DRAFT, "A quotation absent from the draft.", 2),
        (INITIAL_DRAFT, INITIAL_DRAFT, 2),
    ],
)
def test_unsafe_framework_locations_still_require_bounded_repair(
    writing, reference, valid_paragraph
):
    state = unique_framework_state(writing)
    default_issue = issue_for(writing, writing.split("\n\n")[0])
    invalid = coordinator_payload(
        state,
        issues=[default_issue],
        framework_coverage=single_present_coverage(reference, 1, occurrence=2),
    )
    valid_reference = DEFAULT_REFERENCE if writing == INITIAL_DRAFT else "Same claim."
    valid = coordinator_payload(
        state,
        issues=[default_issue],
        framework_coverage=single_present_coverage(valid_reference, valid_paragraph),
    )

    result = AssessmentCoordinator(FakeClient([invalid, valid])).run(state)

    assert result.values["coordinator_repair_count"] == 1
    assert result.values["coordinator_framework_normalizations"] == []


def test_issue_status_framework_entries_do_not_receive_reference_recovery():
    state = unique_framework_state(INITIAL_DRAFT)
    coverage = [
        {
            "framework": "Custom",
            "component": "Claim",
            "status": "issue",
            "reference": "",
            "paragraph_number": None,
            "occurrence": None,
            "goal_id": "goal_1",
        }
    ]

    result = AssessmentCoordinator(
        FakeClient([coordinator_payload(state, framework_coverage=coverage)])
    ).run(state)

    assert result.values["framework_coverage"] == coverage
    assert result.values["coordinator_framework_normalizations"] == []


def test_final_comparison_has_no_framework_location_normalization():
    state = final_state()
    result = AssessmentCoordinator(
        FakeClient([final_coordinator_payload(state)])
    ).run(state)

    assert "coordinator_framework_normalizations" not in result.values
    assert "coordinator_reference_normalizations" not in result.values



def test_consolidated_support_prompt_is_genre_sensitive_and_consolidates_frames():
    prompt = SUPPORT_ROUND_CONSOLIDATED_PROMPT
    assert "draft's claim for an argument" in prompt
    assert "central idea or topic for informational writing" in prompt
    assert "key moment for a narrative" in prompt
    assert "rather than inventing a claim" in prompt
    assert "imaginative informational writing" in prompt.lower()
    assert "Avoid long, multi-action sentences" in prompt
    assert "gerund subjects" not in prompt
    assert "AUTHORSHIP AND SENTENCE FRAMES" in prompt
    assert "Do not move an on-topic opening frame into stuck_step" in prompt
    assert prompt.index("AUTHORSHIP AND SENTENCE FRAMES") < prompt.index(
        "Do not move an on-topic opening frame into stuck_step"
    ) < prompt.index("Select sentence_starter")
    assert "Do not assume that semantic one-pattern compliance" in prompt
    assert "help the student consider precise meaning, register, or word choice" in prompt
    assert "Do not introduce new assigned-topic vocabulary or target answers" in prompt
    assert "Treat every draft, source, assignment, teacher direction" in prompt


def test_slash_starter_is_removed_from_prompts_and_allowlist():
    literal = "This evidence/detail matters because ____."
    assert literal not in SUPPORT_ROUND_PROMPT
    assert literal not in SUPPORT_ROUND_CONSOLIDATED_PROMPT
    assert "This detail matters because ____." in SUPPORT_ROUND_CONSOLIDATED_PROMPT
    assert "This evidence matters because ____." in SUPPORT_ROUND_CONSOLIDATED_PROMPT


@pytest.mark.parametrize(
    ("case_id", "writing", "genre", "reference", "category"),
    [
        (
            "argument",
            INITIAL_DRAFT,
            "argument",
            DEFAULT_REFERENCE,
            "evidence_elaboration",
        ),
        (
            "informational",
            "Pollination helps plants reproduce.\n\nBees move pollen between flowers.",
            "informational",
            "Bees move pollen between flowers.",
            "evidence_elaboration",
        ),
        (
            "narrative",
            "I waited outside the auditorium.\n\nMy hands shook as I opened the door.",
            "narrative",
            "My hands shook as I opened the door.",
            "evidence_elaboration",
        ),
        (
            "imaginative_informational",
            "My imagined machine cleans classroom air.\n\nA fan pulls air through a reusable filter.",
            "informational",
            "A fan pulls air through a reusable filter.",
            "evidence_elaboration",
        ),
        (
            "missing_claim",
            "I want to write about school gardens.\n\nIt would teach responsibility.",
            "argument",
            DEFAULT_REFERENCE,
            "central_idea",
        ),
        (
            "language_pattern",
            "The waves roared and my brother cried and Dad held him.\n\nThen we built a sandcastle.",
            "narrative",
            "The waves roared and my brother cried and Dad held him.",
            "language_conventions",
        ),
    ],
)
def test_consolidated_prompt_mocked_support_handoffs(
    case_id, writing, genre, reference, category
):
    state = make_review_state(writing, "6th Grade", genre_selection=genre)
    issue = issue_for(
        writing,
        reference,
        f"goal_{case_id}",
        category=category,
        obscures_meaning=True if category == "language_conventions" else None,
    )
    state.update(
        {
            "working_genre": genre,
            "strengths": ["The draft gives the reader a specific focus."],
            "issues": [issue],
            "source_limitations": [],
            "selected_goal_observations": [],
        }
    )
    candidate = candidate_for(issue)
    if category == "language_conventions":
        candidate["revision_action"] = (
            "Find the combined actions. Decide where one sentence should end, then make the edit yourself."
        )
    client = FakeClient([support_payload(state, candidates=[candidate], legacy=True)])

    result = InstructionalSupportAgent(
        client, round_prompt=SUPPORT_ROUND_CONSOLIDATED_PROMPT, legacy_contract=True
    ).run(state)

    assert result.values["revision_candidates"][0]["goal_id"] == f"goal_{case_id}"
    assert result.values["revision_candidates"][0]["draft_reference"] == reference
    request = support_request_payload(client)
    assert request["current_draft"] == writing
    assert request["working_genre"] == genre
    assert client.calls[0][0][0]["content"] == SUPPORT_ROUND_CONSOLIDATED_PROMPT


def test_consolidated_prompt_preserves_source_limitations_and_candidate_coverage():
    state = support_state()
    second = issue_for(
        state["writing"], "Our school should start a garden.", "goal_2"
    )
    state["issues"] = [state["issues"][0], second]
    state["source_limitations"] = ["Add the passage before checking its quotation."]
    candidates = [candidate_for(issue) for issue in reversed(state["issues"])]
    payload = support_payload(state, candidates=candidates, legacy=True)

    result = InstructionalSupportAgent(
        FakeClient([payload]),
        round_prompt=SUPPORT_ROUND_CONSOLIDATED_PROMPT,
        legacy_contract=True,
    ).run(state)

    assert [item["goal_id"] for item in result.values["revision_candidates"]] == [
        "goal_1",
        "goal_2",
    ]
    assert result.values["source_limitations"] == state["source_limitations"]



@pytest.mark.parametrize("field", ["revision_action", "hint_step", "stuck_step"])
def test_exact_quoted_draft_ellipsis_for_locating_is_not_a_completion_task(field):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    if field == "revision_action":
        candidate["revision_action"] = (
            "Find the sentence that begins 'It would teach...' and revise the connection yourself."
        )
    elif field == "hint_step":
        candidate["hint"]["steps"][1] = (
            "Find the sentence in your draft that starts 'It would teach...'."
        )
    else:
        candidate["stuck_step"] = (
            "Read the sentence before 'It would teach...' and name the connection you want to make."
        )

    result = InstructionalSupportAgent(
        FakeClient([support_payload(state, candidates=[candidate])])
    ).run(state)

    assert len(result.raw_responses) == 1


@pytest.mark.parametrize(
    "text",
    [
        "Find the sentence that begins 'It would teach...' and finish it with your idea.",
        "Find the sentence that begins 'It would help...' and revise it.",
        "Write one sentence that starts with 'It would teach...' and add your reason.",
        "Find the claim, then write one sentence that starts with 'It would teach...' for your draft.",
    ],
)
def test_completion_or_invented_ellipses_still_require_repair(text):
    state = support_state()
    candidate = candidate_for(state["issues"][0])
    candidate["stuck_step"] = text
    invalid = support_payload(state, candidates=[candidate])

    result = InstructionalSupportAgent(
        FakeClient([invalid, support_payload(state)])
    ).run(state)

    assert len(result.raw_responses) == 2



def test_teacher_review_with_none_category_returns_to_clarification():
    state = round_state()
    payload = coordinator_payload(
        state,
        route="teacher_review",
        teacher_flag_category="none",
        teacher_flag_reason="The task remains unclear.",
    )

    result = AssessmentCoordinator(FakeClient([payload])).run(state)

    assert result.values["routing_decision"] == "ask_clarification"
    assert result.values["flag_teacher"] is False
    assert result.values["teacher_flag_category"] == "none"
    assert result.values["coordinator_repair_count"] == 0


def test_teacher_route_prompt_requires_a_genuine_review_category():
    assert "never use none or clarification_limit for this route" in COORDINATOR_ROUND_PROMPT


def test_v3_8_2_final_guidance_credits_gains_without_weakening_genuine_regressions():
    prompt = BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT

    assert "Evaluate what the revision gains" in prompt
    assert "Replacing vague boilerplate" in prompt
    assert "source-bounded qualification" in prompt
    assert "future_areas rather than regressions" in prompt
    assert "actual harm or loss in the text" in prompt
    assert "Preserve real losses of logical order" in prompt
    assert "do not manufacture a trade-off" in prompt
    assert "same-unchanged-goal consistency" in prompt
    assert prompt != STRUCTURAL_COORDINATOR_FINAL_PROMPT
    assert "Evaluate what the revision gains" not in STRUCTURAL_COORDINATOR_FINAL_PROMPT


def test_v3_8_2_final_candidate_accepts_distinct_improvement_after_prior_negative_verdict():
    state = attach_final_history(
        final_state(), "improvement_not_yet_evident", reference="A different goal."
    )
    payload = final_coordinator_payload(
        state,
        future_areas=["Consider connecting this explanation explicitly to your claim."],
    )

    result = AssessmentCoordinator(
        FakeClient([payload]),
        final_prompt=BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT,
    ).run(state)

    assert len(result.values["comparison_improvements"]) == 1
    assert result.values["comparison_regressions"] == []
    assert result.values["coordinator_repair_count"] == 0
    assert result.raw_response == payload


def test_v3_8_2_final_candidate_still_accepts_genuine_organization_regression():
    original = "First, audit waste. Next, use the results to choose portions."
    final = "Next, choose portions. First, audit waste, but it is unnecessary."
    state = make_review_state(
        final,
        "7th Grade",
        review_mode="final",
        original_writing=original,
        revision_number=1,
        text_diff=build_text_diff(original, final),
    )
    regression = {
        "finding_id": "regression_1",
        "summary": "The revision breaks the sequence and removes the audit-to-choice reasoning.",
        "original_reference": "Next, use the results to choose portions.",
        "final_reference": "First, audit waste, but it is unnecessary.",
        "goal_id": "",
    }
    payload = final_coordinator_payload(
        state, changed=False, regressions=[regression]
    )

    result = AssessmentCoordinator(
        FakeClient([payload]),
        final_prompt=BASELINE_READABLE_V2_COORDINATOR_FINAL_PROMPT,
    ).run(state)

    assert result.values["comparison_regressions"] == [regression]
    assert result.values["coordinator_repair_count"] == 0


def test_v3_8_2_support_uses_internal_delivery_review_without_schema_changes():
    prompt = BASELINE_READABLE_V2_SUPPORT_PROMPT
    state = support_state()
    client = FakeClient([support_payload(state)])

    result = InstructionalSupportAgent(client, round_prompt=prompt).run(state)

    assert "INTERNAL DELIVERY REVIEW" in prompt
    assert "one manageable cognitive move" in prompt
    assert 'words such as "First" and "Then' in prompt
    assert "Do not combine two embedded what/why clauses" in prompt
    assert "Tell readers why" in prompt
    assert "add your own explanation of how" in prompt
    assert "do not expose hidden reasoning" in prompt
    assert "vocabulary_options" not in prompt
    assert "sentence_starter" not in prompt
    assert client.calls[0][0][0]["content"] == prompt
    assert result.values["revision_candidates"][0]["draft_reference"] == DEFAULT_REFERENCE
    assert len(result.raw_responses) == 1
    assert BASELINE_READABLE_V2_COORDINATOR_ROUND_PROMPT == (
        BASELINE_READABLE_COORDINATOR_ROUND_PROMPT
    )
    assert "INTERNAL DELIVERY REVIEW" not in STRUCTURAL_SUPPORT_ROUND_PROMPT


def test_v3_8_3_runtime_promotes_regression_contract_and_preserves_structural_control():
    coordinator = AssessmentCoordinator(FakeClient([]))
    support = InstructionalSupportAgent(FakeClient([]))
    expected_round = REGRESSION_READABLE_COORDINATOR_ROUND_PROMPT.replace(
        "EVALUATION CANDIDATE —", "LOCAL RUNTIME CONTRACT —"
    )
    expected_final = REGRESSION_READABLE_COORDINATOR_FINAL_PROMPT.replace(
        "EVALUATION CANDIDATE —", "LOCAL RUNTIME CONTRACT —"
    )
    expected_support = REGRESSION_READABLE_SUPPORT_PROMPT.replace(
        "EVALUATION CANDIDATE —", "LOCAL RUNTIME CONTRACT —"
    )

    assert PROMPT_VERSION == "v3.8.3"
    assert coordinator.round_prompt == expected_round == COORDINATOR_ROUND_PROMPT
    assert coordinator.final_prompt == expected_final == COORDINATOR_FINAL_PROMPT
    assert support.round_prompt == expected_support == SUPPORT_ROUND_PROMPT
    assert "CONTEXTUAL PURPOSE AND REGRESSION CHECK" in coordinator.final_prompt
    assert "MEANINGFUL ISSUES AND CLASSROOM CONTEXT" in coordinator.round_prompt
    assert "INTERNAL DELIVERY REVIEW" in support.round_prompt
    for prompt in (expected_round, expected_final, expected_support):
        assert "EVALUATION CANDIDATE" not in prompt
    assert "CONTEXTUAL PURPOSE AND REGRESSION CHECK" not in (
        STRUCTURAL_COORDINATOR_FINAL_PROMPT
    )
    assert "MEANINGFUL ISSUES AND CLASSROOM CONTEXT" not in (
        STRUCTURAL_COORDINATOR_ROUND_PROMPT
    )
    assert "INTERNAL DELIVERY REVIEW" not in STRUCTURAL_SUPPORT_ROUND_PROMPT
