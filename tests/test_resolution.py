"""Tests for resolve_holiday() across all 5 locales - alias hits,
Easter sentinel, substring fallback, and unresolvable input."""
import importlib.util
import sys
from pathlib import Path

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("holidays_skill_mod", _INIT_PATH)
mod = importlib.util.module_from_spec(_spec)
sys.modules["holidays_skill_mod"] = mod
_spec.loader.exec_module(mod)


def test_alias_exact_match_en_us():
    assert mod.resolve_holiday("christmas", "en-us") == "Christmas Day"


def test_alias_exact_match_da_dk():
    assert mod.resolve_holiday("jul", "da-dk") == "Juledag"


def test_alias_case_insensitive():
    assert mod.resolve_holiday("CHRISTMAS", "en-us") == "Christmas Day"


def test_alias_strips_whitespace():
    assert mod.resolve_holiday("  christmas  ", "en-us") == "Christmas Day"


def test_easter_sentinel_en_us():
    assert mod.resolve_holiday("easter", "en-us") == mod.EASTER_SENTINEL


def test_easter_sentinel_da_dk():
    assert mod.resolve_holiday("påske", "da-dk") == mod.EASTER_SENTINEL


def test_easter_sentinel_fr_fr():
    assert mod.resolve_holiday("pâques", "fr-fr") == mod.EASTER_SENTINEL


def test_french_christmas_is_noel_not_fete_de_noel():
    """Regression test for a real curation error caught during
    development - see DEVELOPMENT.md."""
    assert mod.resolve_holiday("noël", "fr-fr") == "Noël"


def test_french_national_day_not_victory_day():
    """Regression test: 'fête nationale' must resolve to the actual
    14 July national day, not 8 May Victory Day - see
    DEVELOPMENT.md."""
    resolved = mod.resolve_holiday("fête nationale", "fr-fr")
    assert resolved == "Fête nationale"
    assert resolved != "Fête de la Victoire"


def test_substring_fallback_matches_unaliased_holiday():
    """'martin luther king' isn't in HOLIDAY_ALIASES but should still
    resolve via substring match against the library's real output."""
    resolved = mod.resolve_holiday("martin luther king", "en-us")
    assert resolved is not None
    assert "martin luther king" in resolved.lower()


def test_unresolvable_returns_none():
    assert mod.resolve_holiday("definitely not a real holiday", "en-us") is None


def test_empty_input_returns_none():
    assert mod.resolve_holiday("", "en-us") is None
    assert mod.resolve_holiday(None, "en-us") is None


def test_unknown_locale_falls_back_gracefully():
    """An unmapped locale has no country, so nothing should resolve -
    but it also shouldn't crash."""
    assert mod.resolve_holiday("christmas", "xx-xx") is None


def test_holiday_display_name_easter():
    assert mod.holiday_display_name(mod.EASTER_SENTINEL, "da-dk") == "påske"
    assert mod.holiday_display_name(mod.EASTER_SENTINEL, "en-us") == "Easter"


def test_country_for_locale_derives_from_region_subtag():
    """Regression test: the country code comes from the locale's
    region subtag directly, not a hardcoded per-locale table - see
    DEVELOPMENT.md 'Deriving the country from the locale, not a
    hardcoded table'."""
    assert mod._country_for_locale("en-us") == "US"
    assert mod._country_for_locale("da-dk") == "DK"
    assert mod._country_for_locale("fr-fr") == "FR"


def test_country_for_locale_no_region_returns_none():
    assert mod._country_for_locale("en") is None
    assert mod._country_for_locale("") is None
    assert mod._country_for_locale(None) is None


def test_holiday_display_name_passthrough():
    assert mod.holiday_display_name("Christmas Day", "en-us") == "Christmas Day"
