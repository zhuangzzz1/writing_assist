from langgraph_core.revision import (
    build_text_diff,
    change_notification,
    locate_reference,
    reference_is_valid,
    reference_overlaps_change,
)


def test_exact_reference_returns_offsets_and_paragraph_metadata():
    text = "First paragraph.\n\nA repeated line. A repeated line.\n\nThird paragraph."

    location = locate_reference(text, "A repeated line.", 2, 2)

    assert location is not None
    assert text[location.start:location.end] == "A repeated line."
    assert location.paragraph_number == 2
    assert location.occurrence == 2


def test_repeated_references_require_the_correct_paragraph_and_occurrence():
    text = "Same idea.\n\nSame idea. Same idea."

    assert reference_is_valid(text, "Same idea.", 1, 1)
    assert reference_is_valid(text, "Same idea.", 2, 2)
    assert not reference_is_valid(text, "Same idea.", 2, 3)
    assert not reference_is_valid(text, "Same idea.", 3, 1)
    assert not reference_is_valid(text, "Invented idea.", 1, 1)


def test_stale_reference_is_not_relocated_to_unrelated_text():
    text = "The original sentence is here."
    edited = "The original sentence was changed."

    assert locate_reference(edited, "The original sentence is here.", 1) is None
    assert reference_is_valid(text, "original sentence", 1)


def test_one_word_critical_edit_is_reported_without_a_quality_judgment():
    diff = build_text_diff("Schools must allow gardens.", "Schools should allow gardens.")

    assert diff["changed"] is True
    assert diff["changed_words"] == 2
    assert "quality" not in diff
    assert "meaningful" not in diff
    assert diff["operations"] == [
        {"type": "replace", "before": "must", "after": "should"}
    ]


def test_large_unrelated_addition_is_only_a_factual_diff():
    diff = build_text_diff("A clear claim.", "A clear claim. " + "New detail. " * 30)

    assert diff["added_words"] == 60
    assert "improvement" not in diff
    assert "selected_goal" not in diff


def test_unchanged_and_punctuation_only_changes_need_neutral_confirmation():
    unchanged = change_notification("Same draft.", "Same draft.")
    punctuation = change_notification("Same draft", "Same draft.", small_change_threshold=8)

    assert unchanged["unchanged"] is True
    assert unchanged["needs_confirmation"] is True
    assert punctuation["unchanged"] is False
    assert punctuation["needs_confirmation"] is True
    assert "trivial" not in str(punctuation).lower()


def test_small_change_threshold_does_not_block_submission():
    notice = change_notification("One claim.", "One clearer claim.", small_change_threshold=0)

    assert notice["needs_confirmation"] is False
    assert notice["changed"] is True


def test_diff_supplies_actual_before_and_after_text():
    diff = build_text_diff("First paragraph.\n\nOld detail.", "First paragraph.\n\nNew detail.")

    assert "Old detail" in diff["unified_diff"]
    assert "New detail" in diff["unified_diff"]
    assert diff["operations"][0]["before"].strip() == "Old"
    assert diff["operations"][0]["after"].strip() == "New"


def test_reference_grounding_requires_overlap_on_the_correct_side_of_the_diff():
    before = "An unchanged claim.\n\nAn old explanation."
    after = "An unchanged claim.\n\nA clearer explanation."

    assert reference_overlaps_change(before, after, "A clearer explanation.", "after")
    assert reference_overlaps_change(before, after, "An old explanation.", "before")
    assert not reference_overlaps_change(before, after, "An unchanged claim.", "after")
    assert not reference_overlaps_change(before, after, "A clearer explanation.", "before")
