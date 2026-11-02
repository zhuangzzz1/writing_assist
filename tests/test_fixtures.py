from pathlib import Path

import pytest

from ui.components import FIXTURE_PATHS, load_fixture


@pytest.mark.parametrize(
    ("name", "grade", "assignment", "has_concern"),
    [
        ("Normal case", "6th Grade", "Persuasive Essay", False),
        ("Incomplete case", "7th Grade", "", False),
        ("Boundary A: concerning content", "6th Grade", "Personal Narrative", False),
        ("Boundary B: revision frustration", "7th Grade", "", True),
    ],
)
def test_frozen_fixtures_parse_without_changing_writing(name, grade, assignment, has_concern):
    fixture = load_fixture(name)
    source = (
        Path(__file__).resolve().parents[1] / "test_cases" / FIXTURE_PATHS[name]
    ).read_text(encoding="utf-8")

    assert fixture.writing == source.partition("Writing:\n")[2]
    assert fixture.grade_level == grade
    assert fixture.assignment_context == assignment
    assert bool(fixture.student_concerns) is has_concern


def test_unknown_fixture_name_is_rejected():
    with pytest.raises(KeyError):
        load_fixture("Unknown fixture")
