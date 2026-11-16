import json

import pytest

from ui.scenarios import (
    SCENARIO_PATH,
    get_acceptance_scenario,
    get_experiment_scenario,
    get_scenario,
    load_acceptance_scenarios,
    load_coordinator_targeted_scenarios,
    load_experiment_scenarios,
    load_final_history_scenarios,
    load_final_regression_scenarios,
    load_readability_coverage_scenarios,
    load_scenarios,
    load_support_comparison_scenarios,
)


def test_v3_scenarios_are_versioned_and_complete():
    data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    scenarios = load_scenarios()

    assert data["fixture_version"] == "v3.4.0"
    assert len(scenarios) >= 6
    for scenario in scenarios:
        assert scenario.scenario_id
        assert scenario.fixture_version == data["fixture_version"]
        assert scenario.draft.strip()
        assert scenario.grade_level in ("5th Grade", "6th Grade", "7th Grade")
        assert scenario.assignment_prompt.strip()
        assert scenario.teacher_directions.strip()


def test_scenarios_cover_genres_and_source_availability():
    scenarios = load_scenarios()

    assert {scenario.genre for scenario in scenarios} >= {
        "argument",
        "informational",
        "narrative",
    }
    assert any(scenario.source_material for scenario in scenarios)
    assert any(not scenario.source_material for scenario in scenarios)
    assert any(scenario.genre == "auto" for scenario in scenarios)


def test_races_and_informal_narrative_scenarios_are_present():
    races = get_scenario("races_informational_pollination")
    narrative = get_scenario("personal_narrative_voice")

    assert "RACES" in races.teacher_directions
    assert "kinda scary" in narrative.draft
    assert narrative.source_material == ""


def test_unknown_scenario_is_rejected():
    with pytest.raises(KeyError):
        get_scenario("unknown")


def test_historical_v2_fixtures_remain_separate_and_unmodified_in_location():
    historical = SCENARIO_PATH.parents[1]
    assert (historical / "normal_case.txt").exists()
    assert (historical / "incomplete_case.txt").exists()
    assert (historical / "boundary_case_a.txt").exists()
    assert (historical / "boundary_case_b.txt").exists()
    assert SCENARIO_PATH.parent.name == "v3"


def test_acceptance_fixture_set_contains_32_complete_versioned_scenarios():
    scenarios = load_acceptance_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 33))
    assert len({scenario.scenario_id for scenario in scenarios}) == 32
    for scenario in scenarios:
        assert scenario.fixture_version == "v3.4.0"
        assert scenario.draft.strip()
        assert scenario.acceptance_focus
        assert scenario.grade_level in ("5th Grade", "6th Grade", "7th Grade")
        for revision in scenario.revisions:
            assert revision.draft.strip()
            assert revision.goal_selection in ("first", "three", "explicit")
            if revision.goal_selection == "explicit":
                assert bool(revision.goal_indices) != bool(revision.goal_references)


def test_additional_final_reflection_scenarios_are_enabled():
    assert all(get_acceptance_scenario(number).finish for number in (7, 9, 15))


def test_density_pair_controls_context_and_does_not_prescribe_candidate_count():
    short = get_acceptance_scenario(31)
    long = get_acceptance_scenario(32)

    assert 50 <= len(short.draft.split()) <= 70
    assert 375 <= len(long.draft.split()) <= 450
    for field in (
        "grade_level",
        "genre",
        "assignment_prompt",
        "teacher_directions",
        "source_material",
        "student_concerns",
    ):
        assert getattr(short, field) == getattr(long, field)
    for scenario in (short, long):
        assert "no candidate count is prescribed" in scenario.acceptance_focus.lower()


def test_long_informational_fixture_exceeds_350_words_and_has_source():
    scenario = get_acceptance_scenario(23)

    assert len(scenario.draft.split()) >= 350
    assert scenario.source_material
    assert scenario.genre == "informational"
    assert scenario.grade_level == "7th Grade"


def test_weak_middle_fixture_has_exactly_four_paragraphs():
    scenario = get_acceptance_scenario(25)

    assert len(scenario.draft.split("\n\n")) == 4
    assert "middle" in scenario.teacher_directions.lower()


def test_short_grade5_fixture_has_four_sentences_and_no_five_paragraph_requirement():
    scenario = get_acceptance_scenario(22)

    assert scenario.draft.count(".") == 4
    assert "do not need five paragraphs" in scenario.teacher_directions


def test_argument_language_fixture_preserves_evidence_and_target_error_types():
    scenario = get_acceptance_scenario(24)

    assert scenario.genre == "argument"
    assert scenario.source_material
    assert "article, tense, and preposition" in scenario.acceptance_focus
    assert "a students" in scenario.draft
    assert "Students learns" in scenario.draft
    assert "in weekend" in scenario.draft


def test_multi_goal_multi_round_and_clarification_fixture_sequences_are_complete():
    three_goals = get_acceptance_scenario(7)
    deferred = get_acceptance_scenario(15)
    multiple_rounds = get_acceptance_scenario(8)
    clarification = get_acceptance_scenario(30)

    assert three_goals.revisions[0].goal_selection == "three"
    assert three_goals.revisions[0].self_reports == {"all": "attempted"}
    assert deferred.revisions[0].self_reports == {
        "first": "attempted",
        "others": "deferred",
    }
    assert len(multiple_rounds.revisions) == 2
    assert multiple_rounds.finish is True
    assert clarification.clarification_answers == ("Not sure", "Anything, I guess")


def test_live_el_contrasts_are_versioned_reviewed_and_explicitly_selected():
    scenarios = load_experiment_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 17))
    assert len({scenario.scenario_id for scenario in scenarios}) == 16
    for scenario in scenarios:
        assert scenario.fixture_version == "v3.6.6-live-el.1"
        assert scenario.expected_outcomes
        assert scenario.workstreams
        assert scenario.draft.strip()
        if scenario.support_only:
            assert scenario.controlled_round
            assert not scenario.revisions
            for issue in scenario.controlled_round["issues"]:
                assert issue["draft_reference"] in scenario.draft
                if issue["source_dependent"]:
                    assert scenario.source_material
                    assert issue["source_location"]
        for revision in scenario.revisions:
            assert revision.goal_selection == "explicit"
            assert 1 <= len(revision.goal_references) <= 3
            for reference in revision.goal_references:
                previous_draft = (
                    scenario.draft
                    if revision == scenario.revisions[0]
                    else scenario.revisions[scenario.revisions.index(revision) - 1].draft
                )
                assert reference in previous_draft

    assert scenarios[6].controlled_round == scenarios[0].controlled_round
    assert scenarios[0].controlled_round["revision_number"] == 1
    assert len(load_acceptance_scenarios()) == 32


def test_speculative_process_fixture_is_synthetic_bounded_and_source_free():
    scenario = get_experiment_scenario(16)

    assert scenario.grade_level == "5th Grade"
    assert scenario.genre == "auto"
    assert scenario.source_material == ""
    assert "imaginative" in scenario.assignment_prompt.lower()
    assert "no scientific source is required" in scenario.teacher_directions.lower()
    assert "The filter catches dirt and tiny pieces of plastic." in scenario.draft
    assert not scenario.revisions
    assert not scenario.controlled_round
    assert any("not fabricated evidence" in outcome for outcome in scenario.expected_outcomes)
    assert any("without suggesting disposal or treatment answers" in outcome for outcome in scenario.expected_outcomes)



def test_support_2x2_handoffs_are_frozen_complete_and_cover_required_strata():
    scenarios = load_support_comparison_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 15))
    assert len({scenario.scenario_id for scenario in scenarios}) == 14
    assert all(scenario.support_only for scenario in scenarios)
    assert {scenario.controlled_round["revision_number"] for scenario in scenarios} == {0, 1}
    assert {scenario.genre for scenario in scenarios} >= {
        "argument",
        "informational",
        "narrative",
    }
    assert any(scenario.source_material for scenario in scenarios)
    assert any(not scenario.source_material for scenario in scenarios)
    ids = {scenario.scenario_id for scenario in scenarios}
    assert "support_imaginative_filter_process" in ids
    assert "support_missing_claim_garden" in ids
    assert "support_first_person_friend_moment" in ids
    assert "support_language_sentence_boundary" in ids
    assert "support_multi_action_survey_explanation" in ids
    for scenario in scenarios:
        setup = scenario.controlled_round
        assert setup["issues"]
        for issue in setup["issues"]:
            assert issue["draft_reference"] in scenario.draft
            if issue["source_dependent"]:
                assert scenario.source_material
                assert issue["source_location"]
        if setup["revision_number"]:
            assert setup["selected_goals"]
            assert len(setup["selected_goal_observations"]) == len(
                setup["selected_goals"]
            )


def test_coordinator_targeted_set_covers_new_and_preserved_behaviors():
    scenarios = load_coordinator_targeted_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 13))
    assert len({scenario.scenario_id for scenario in scenarios}) == 12
    ids = {scenario.scenario_id for scenario in scenarios}
    assert "acceptance_10_strong_draft" in ids
    assert "live_el_16_speculative_process" in ids
    assert "coordinator_initial_accuracy_concern_priority" in ids
    assert "coordinator_revision_accuracy_concern_priority" in ids
    assert "coordinator_framework_title_unique_location" in ids
    assert "coordinator_repeated_reference_locations" in ids
    assert "coordinator_final_source_present" in ids
    assert "coordinator_final_source_missing" in ids
    assert "coordinator_final_unchanged" in ids
    assert scenarios[2].clarification_answers == ("Still not sure",)
    assert scenarios[3].clarification_answers == ("Not sure", "Anything, I guess")
    assert scenarios[5].framework_name == "CER"
    for scenario in scenarios:
        assert scenario.draft.strip()
        assert scenario.expected_outcomes
        assert scenario.workstreams


def test_final_history_contrasts_are_versioned_controlled_and_synthetic():
    scenarios = load_final_history_scenarios()

    assert [scenario.number for scenario in scenarios] == [1, 2]
    assert len({scenario.scenario_id for scenario in scenarios}) == 2
    for scenario in scenarios:
        setup = scenario.controlled_round
        assert scenario.fixture_version == "v3.8.0-final-history.1"
        assert scenario.finish is True
        assert not scenario.revisions
        assert setup["revision_number"] == 1
        assert setup["original_draft"] != scenario.draft
        assert len(setup["selected_goals"]) == 1
        assert len(setup["selected_goal_observations"]) == 1
        assert setup["selected_goal_observations"][0]["status"] == (
            "improvement_not_yet_evident"
        )
        assert setup["selected_goals"][0]["goal_id"] == setup[
            "selected_goal_observations"
        ][0]["goal_id"]
    first = scenarios[0]
    assert first.controlled_round["selected_goals"][0]["draft_reference"] in first.draft
    assert first.controlled_round["selected_goals"][0]["draft_reference"] not in (
        first.controlled_round["original_draft"]
    )
    assert "Our school should start later." in scenarios[1].draft
    assert "Our school should start later." in scenarios[1].controlled_round["original_draft"]


def test_v3_8_2_final_regression_fixtures_preserve_lineage_and_controlled_history():
    scenarios = load_final_regression_scenarios()

    assert [scenario.number for scenario in scenarios] == [1, 2, 3, 4]
    assert len({scenario.scenario_id for scenario in scenarios}) == 4
    assert [scenario.lineage["scenario_number"] for scenario in scenarios] == [8, 9, 1, 9]
    for scenario in scenarios:
        setup = scenario.controlled_round
        assert scenario.fixture_version == "v3.8.2-final-regression.1"
        assert scenario.finish is True
        assert not scenario.revisions
        assert setup["revision_number"] == 1
        assert setup["original_draft"] != scenario.draft
        assert len(setup["selected_goals"]) == 1
        assert len(setup["selected_goal_observations"]) == 1
        assert setup["selected_goals"][0]["goal_id"] == setup[
            "selected_goal_observations"
        ][0]["goal_id"]
        for issue in setup["issues"]:
            assert issue["draft_reference"] in scenario.draft
    assert "rather than proving health benefits" in scenarios[0].draft
    assert scenarios[0].source_material
    assert not scenarios[1].source_material
    assert "I think better concentration" in scenarios[1].draft
    assert scenarios[2].controlled_round["selected_goal_observations"][0]["status"] == (
        "improvement_not_yet_evident"
    )
    assert scenarios[3].controlled_round["issues"][0]["regression"] is True
    assert "Finally, students can choose smaller portions." in scenarios[3].draft


def test_v3_8_2_coverage_fixtures_separate_adaptive_and_controlled_paths():
    scenarios = load_readability_coverage_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 8))
    assert len({scenario.scenario_id for scenario in scenarios}) == 7
    assert all(
        scenario.fixture_version == "v3.8.2-readability-coverage.1"
        for scenario in scenarios
    )
    assert all(scenario.lineage for scenario in scenarios)
    adaptive = scenarios[0]
    assert adaptive.revisions[0].goal_selection == "all_available"
    assert adaptive.allow_direct_response_finish is True
    assert adaptive.lineage["scenario_number"] == 15
    assert any("Do not claim" in outcome for outcome in adaptive.expected_outcomes)

    controlled = scenarios[1]
    assert controlled.controlled_round["revision_number"] == 0
    assert len(controlled.controlled_round["revision_candidates"]) == 3
    assert controlled.revisions[0].goal_selection == "three"
    assert controlled.revisions[0].self_reports == {
        "first": "attempted",
        "others": "deferred",
    }

    finish = scenarios[2]
    assert finish.allow_direct_response_finish is True
    assert finish.finish is True
    assert finish.revisions[0].goal_selection == "first"
    reviewed = scenarios[3]
    assert reviewed.controlled_round["revision_number"] == 1
    assert reviewed.controlled_round["selected_goal_observations"]
    assert not reviewed.revisions

    assert "Language corrections are optional" in scenarios[4].teacher_directions
    assert scenarios[5].clarification_answers == ("Not sure", "Anything, I guess")
    assert scenarios[6].genre == "narrative"
    assert not scenarios[6].finish
    for scenario in (controlled, reviewed):
        for issue in scenario.controlled_round["issues"]:
            assert issue["draft_reference"] in scenario.draft
