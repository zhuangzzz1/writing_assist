import pytest

from agents.utils import InputValidationError
from langgraph_core.assignment import (
    FRAMEWORK_COMPONENTS,
    language_corrections_optional,
    resolve_framework,
)
from langgraph_core.state import make_review_state


@pytest.mark.parametrize("name", list(FRAMEWORK_COMPONENTS))
def test_known_frameworks_supply_bounded_component_presets(name):
    framework, components = resolve_framework(name.lower(), None, "")

    assert framework == name
    assert components == list(FRAMEWORK_COMPONENTS[name])


def test_custom_framework_requires_explicit_name_and_components():
    framework, components = resolve_framework(
        "SOAPSTone", ["Subject", "Occasion", "Audience", "Purpose"], ""
    )

    assert framework == "SOAPSTone"
    assert components == ["Subject", "Occasion", "Audience", "Purpose"]
    with pytest.raises(InputValidationError, match="custom framework"):
        resolve_framework("Custom", [], "")
    with pytest.raises(InputValidationError, match="Name the framework"):
        resolve_framework("", ["Opening"], "")


def test_framework_components_must_be_unique():
    with pytest.raises(InputValidationError, match="unique"):
        resolve_framework("Custom", ["Claim", " claim "], "")


@pytest.mark.parametrize(
    ("directions", "expected"),
    [
        ("Use RACES for this response.", "RACES"),
        ("Use RACES, not MEAL.", "RACES"),
        ("Do not use RACES; use MEAL.", "MEAL"),
    ],
)
def test_free_text_detection_handles_explicit_and_negated_directions(directions, expected):
    framework, components = resolve_framework("", None, directions)

    assert framework == expected
    assert components == list(FRAMEWORK_COMPONENTS[expected])


def test_free_text_detection_rejects_ambiguous_multiple_frameworks():
    with pytest.raises(InputValidationError, match="one required framework"):
        resolve_framework("", None, "Use CER and RACES.")


def test_optional_and_negated_framework_directions_do_not_commission_coverage():
    assert resolve_framework("", None, "Do not use RACES.") == ("", [])
    assert resolve_framework("", None, "RACES is optional.") == ("", [])


@pytest.mark.parametrize(
    "directions",
    [
        "Language corrections are optional unless they obscure meaning.",
        "Grammar fixes are optional.",
        "Mechanics are optional.",
        "Don't focus on mechanics.",
        "Mechanics are not graded.",
    ],
)
def test_language_policy_recognizes_explicit_optional_directions(directions):
    assert language_corrections_optional(directions) is True


@pytest.mark.parametrize(
    "directions",
    [
        "Language corrections are not optional.",
        "Mechanics are required.",
        "Focus on grammar and organization.",
    ],
)
def test_language_policy_rejects_required_or_unrelated_directions(directions):
    assert language_corrections_optional(directions) is False


def test_review_state_preserves_structured_framework_input():
    state = make_review_state(
        "A draft with a claim.",
        "6th Grade",
        framework_name="CER",
        framework_components=[],
    )

    assert state["framework_name"] == "CER"
    assert state["framework_components"] == ["Claim", "Evidence", "Reasoning"]
