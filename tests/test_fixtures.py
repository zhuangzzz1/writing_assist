import json

import pytest

from ui.scenarios import (
    SCENARIO_PATH,
    get_acceptance_scenario,
    get_scenario,
    load_acceptance_scenarios,
    load_scenarios,
)


def test_v3_scenarios_are_versioned_and_complete():
    data = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
    scenarios = load_scenarios()

    assert data["fixture_version"] == "v3.1.0"
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


def test_acceptance_fixture_set_contains_30_complete_versioned_scenarios():
    scenarios = load_acceptance_scenarios()

    assert [scenario.number for scenario in scenarios] == list(range(1, 31))
    assert len({scenario.scenario_id for scenario in scenarios}) == 30
    for scenario in scenarios:
        assert scenario.fixture_version == "v3.2.1"
        assert scenario.draft.strip()
        assert scenario.acceptance_focus
        assert scenario.grade_level in ("5th Grade", "6th Grade", "7th Grade")
        for revision in scenario.revisions:
            assert revision.draft.strip()
            assert revision.goal_selection in ("first", "three")


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
