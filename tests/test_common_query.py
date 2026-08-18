"""Tests for the Common Query safety net (handle_common_query,
_strip_question_prefix) - see DEVELOPMENT.md for why this exists."""


def test_strip_question_prefix_when_is(skill):
    from holidays_skill import _strip_question_prefix
    assert _strip_question_prefix("when is christmas", "en-us") == "christmas"
    assert _strip_question_prefix("When is Christmas?", "en-us") == "Christmas"


def test_strip_question_prefix_danish(skill):
    from holidays_skill import _strip_question_prefix
    assert _strip_question_prefix("hvornår er det jul", "da-dk") == "jul"


def test_strip_question_prefix_no_match_returns_none(skill):
    from holidays_skill import _strip_question_prefix
    assert _strip_question_prefix("play some music", "en-us") is None


def test_handle_common_query_resolves_known_holiday(skill):
    """Checks month-day only, not the year - this test should still
    pass correctly in any year without needing an update, since
    Christmas's calendar date never changes even though the specific
    upcoming year found by next_occurrence_of_holiday() will."""
    answer, confidence = skill.handle_common_query("when is christmas", "en-us")
    assert "-12-25" in answer
    assert confidence == 0.8


def test_handle_common_query_resolves_easter(skill):
    answer, confidence = skill.handle_common_query("when is easter", "en-us")
    assert answer is not None
    assert confidence == 0.8


def test_handle_common_query_unknown_holiday_returns_none(skill):
    result = skill.handle_common_query("when is spacemas", "en-us")
    assert result is None


def test_handle_common_query_non_matching_phrase_returns_none(skill):
    result = skill.handle_common_query("play some music", "en-us")
    assert result is None
