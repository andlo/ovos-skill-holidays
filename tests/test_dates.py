"""Tests for date computation: Easter, next-occurrence search,
weekday names, and the category-name-mismatch fix (US 'unofficial'
vs Denmark 'optional' - see DEVELOPMENT.md)."""
import importlib.util
import sys
from datetime import date
from pathlib import Path

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("holidays_skill_mod2", _INIT_PATH)
mod = importlib.util.module_from_spec(_spec)
sys.modules["holidays_skill_mod2"] = mod
_spec.loader.exec_module(mod)


def test_easter_2026_matches_known_date():
    """2026 Easter Sunday is 5 April - a fixed, independently
    verifiable fact, not something this test should compute itself."""
    next_date = mod.next_occurrence_of_holiday(mod.EASTER_SENTINEL, "en-us",
                                                from_date=date(2026, 1, 1))
    assert next_date == date(2026, 4, 5)


def test_easter_rolls_to_next_year_if_already_past():
    next_date = mod.next_occurrence_of_holiday(mod.EASTER_SENTINEL, "en-us",
                                                from_date=date(2026, 12, 1))
    assert next_date == date(2027, 3, 28)


def test_next_occurrence_of_named_holiday():
    next_date = mod.next_occurrence_of_holiday("Christmas Day", "en-us",
                                                from_date=date(2026, 1, 1))
    assert next_date == date(2026, 12, 25)


def test_next_occurrence_today_counts_as_next():
    """If today IS the holiday, it should return today, not skip to
    next year - 'how many days until christmas' on Christmas Day
    itself should say 0, not 365."""
    next_date = mod.next_occurrence_of_holiday("Christmas Day", "en-us",
                                                from_date=date(2026, 12, 25))
    assert next_date == date(2026, 12, 25)


def test_us_halloween_resolves_via_unofficial_category():
    """Regression test: US's 'unofficial' category (not 'optional',
    which US doesn't even support) must be included, or Halloween-
    type entries silently disappear - see DEVELOPMENT.md."""
    resolved = mod.resolve_holiday("halloween", "en-us")
    assert resolved == "Halloween"
    next_date = mod.next_occurrence_of_holiday(resolved, "en-us",
                                                from_date=date(2026, 1, 1))
    assert next_date == date(2026, 10, 31)


def test_weekday_name_known_date():
    """2026-08-18 (today, at time of writing) is a Tuesday."""
    assert mod.weekday_name(date(2026, 8, 18), "en-us") == "Tuesday"
    assert mod.weekday_name(date(2026, 8, 18), "da-dk") == "tirsdag"


def test_days_between():
    assert mod.days_between(date(2026, 1, 1), date(2026, 1, 11)) == 10
    assert mod.days_between(date(2026, 1, 1), date(2026, 1, 1)) == 0


def test_is_holiday_today_positive(monkeypatch):
    import datetime as _datetime
    class FixedDate(_datetime.date):
        @classmethod
        def today(cls):
            return _datetime.date(2026, 12, 25)
    monkeypatch.setattr(mod, "date", FixedDate)
    assert mod.is_holiday_today("en-us") == "Christmas Day"


def test_is_holiday_today_negative(monkeypatch):
    import datetime as _datetime
    class FixedDate(_datetime.date):
        @classmethod
        def today(cls):
            return _datetime.date(2026, 7, 15)
    monkeypatch.setattr(mod, "date", FixedDate)
    assert mod.is_holiday_today("en-us") is None
