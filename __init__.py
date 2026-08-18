"""
skill OVOS Holidays
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

Public holidays, Easter, and calendar-date math for OVOS - "is today
a holiday", "when is christmas", "how many days until easter", "what
day of the week is march 3rd". Fully offline: holiday dates are
COMPUTED live per query via the `holidays` Python library (which
implements Computus and other calendar rules directly, no network
lookups) rather than bundled as static pre-fetched dates the way
ovos-skill-wiki-offline bundles article text - there is no
data/build_*.py fetch step here, the "data" this skill ships is only
a small, hand-curated per-locale ALIAS list (see HOLIDAY_ALIASES
below), not the dates themselves.

A UTILITY skill (fixed intents), NOT a FallbackSkill - see
DEVELOPMENT.md "Why fixed intents, not FallbackSkill" for why this
follows ovos-skill-geometry/-geography's architecture rather than
ovos-skill-wiki-offline's open-ended lookup pattern. Uses the same
narrow @common_query safety net as its utility-skill siblings, for
the same reason (see ovos-skill-geometry's DEVELOPMENT.md and
OpenVoiceOS/ovos-m2v-pipeline#68).

Deliberately kept separate from ovos-skill-nameday despite both being
"calendar knowledge" - see this skill's own README "Relationship to
ovos-skill-nameday" and "Collision risk with ovos-skill-nameday" for
the reasoning and a verified (not assumed) collision example.
"""

import calendar
from datetime import date, timedelta
from pathlib import Path

import holidays
from dateutil.easter import easter as _easter
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler, common_query

SKILL_ROOT = Path(__file__).resolve().parent
LOCALE_DIR = SKILL_ROOT / "locale"

# lang -> ISO country code the `holidays` library understands. Not a
# 1:1 language-to-country mapping in general (es-es doesn't uniquely
# determine a Spanish-speaking country any more than en-us uniquely
# determines an English-speaking one) - but for THIS project family's
# existing 5 locales, each already maps to one specific country by
# convention (en-us -> US, not UK/AU/CA; es-es -> Spain, not Latin
# America), so a plain per-locale dict is honest and sufficient here.
# A generic language->country solution is a bigger problem this skill
# doesn't need to solve for its own fixed locale set.
LOCALE_TO_COUNTRY = {
    "en-us": "US",
    "da-dk": "DK",
    "de-de": "DE",
    "fr-fr": "FR",
    "es-es": "ES",
}

# Categories are NOT standardized across countries in this library -
# verified the hard way: Denmark's non-statutory observances
# (Grundlovsdag, Juleaftensdag) are under 'optional', while the US's
# equivalent (Halloween, Valentine's Day, Easter Sunday itself,
# Mother's/Father's Day) are under a DIFFERENTLY-NAMED 'unofficial'
# category - 'optional' isn't even in US's supported_categories at
# all. Guessing a fixed category-name tuple per HOLIDAY_CATEGORIES
# and filtering against what each country supports would have
# silently dropped Halloween-type entries for the US. Simpler and
# more robust: just request ALL of a country's supported categories -
# a superset can only resolve MORE of what people plausibly ask
# about, not introduce ambiguity (each entry still has its own
# distinct name).
def _country_holidays(lang, years):
    """Returns a holidays.HolidayBase-like dict {date: name} for the
    given lang's mapped country across the given years, across every
    category that country's library entry supports. Computed live,
    not cached across calls - the `holidays` library itself is fast
    enough (pure calendar arithmetic, no I/O) that per-query
    computation is fine, see DEVELOPMENT.md "Performance: why no
    caching layer"."""
    country = LOCALE_TO_COUNTRY.get(lang.lower())
    if country is None:
        return {}
    cls = getattr(holidays, country, None)
    if cls is None:
        return {}
    categories = getattr(cls, "supported_categories", ("public",))
    return cls(years=years, categories=categories)


# ---------------------------------------------------------------
# Alias resolution - the `holidays` library's own names are the
# FORMAL calendar names ("Juledag", "Christmas Day"), which don't
# always match how people naturally ask ("jul", not "juledag" - a
# real gap, verified by inspecting actual library output, not
# assumed). A small, hand-curated per-locale alias map covers the
# holidays people are actually likely to ask about by a shorter/
# different everyday name; anything not in this list still resolves
# via substring/prefix matching against the library's own official
# names as a fallback, see resolve_holiday().
# ---------------------------------------------------------------
HOLIDAY_ALIASES = {
    "en-us": {
        "christmas": "Christmas Day",
        "new year": "New Year's Day",
        "new years": "New Year's Day",
        "independence day": "Independence Day",
        "thanksgiving": "Thanksgiving Day",
        "labor day": "Labor Day",
        "halloween": "Halloween",
        "easter": "__EASTER__",
    },
    "da-dk": {
        "jul": "Juledag",
        "juledag": "Juledag",
        "juleaften": "Juleaftensdag",
        "nytår": "Nytårsdag",
        "nytårsaften": "Nytårsaften",
        "grundlovsdag": "Grundlovsdag",
        "pinse": "Pinsedag",
        "kristi himmelfart": "Kristi himmelfartsdag",
        "påske": "__EASTER__",
    },
    "de-de": {
        "weihnachten": "Erster Weihnachtstag",
        "neujahr": "Neujahr",
        "tag der deutschen einheit": "Tag der Deutschen Einheit",
        "christi himmelfahrt": "Christi Himmelfahrt",
        "pfingsten": "Pfingstmontag",
        "ostern": "__EASTER__",
    },
    "fr-fr": {
        "noël": "Noël",
        "jour de l'an": "Jour de l'an",
        "fête du travail": "Fête du Travail",
        "fête nationale": "Fête nationale",
        "toussaint": "Toussaint",
        "ascension": "Ascension",
        "pâques": "__EASTER__",
    },
    "es-es": {
        "navidad": "Natividad del Señor",
        "año nuevo": "Año Nuevo",
        "reyes": "Epifanía del Señor",
        "fiesta nacional": "Fiesta Nacional de España",
        "constitución": "Día de la Constitución Española",
        "asunción": "Asunción de la Virgen",
        "semana santa": "__EASTER__",
        "pascua": "__EASTER__",
    },
}

EASTER_SENTINEL = "__EASTER__"


def resolve_holiday(raw, lang):
    """Resolves spoken text to either EASTER_SENTINEL or one of the
    `holidays` library's own official names for this locale's
    country, or None if nothing matches. Exact-alias match first,
    then a substring match against the official names actually
    present in the library's data (not a fixed bundled list - this
    means a real but less-common holiday not in HOLIDAY_ALIASES can
    still resolve if the user happens to say something close to its
    official name)."""
    if not raw:
        return None
    lang = lang.lower()
    key = raw.strip().lower()
    aliases = HOLIDAY_ALIASES.get(lang, {})
    if key in aliases:
        return aliases[key]
    this_year = date.today().year
    official_names = set(_country_holidays(lang, [this_year, this_year + 1]).values())
    for name in official_names:
        if key in name.lower():
            return name
    return None


def holiday_display_name(resolved, lang):
    """Reverses resolve_holiday() for display: EASTER_SENTINEL ->
    a spoken-friendly word for this locale, official names -> as-is
    (they're already real words in the target language, unlike a
    machine key)."""
    if resolved == EASTER_SENTINEL:
        return {
            "en-us": "Easter", "da-dk": "påske", "de-de": "Ostern",
            "fr-fr": "Pâques", "es-es": "Pascua",
        }.get(lang.lower(), "Easter")
    return resolved


# ---------------------------------------------------------------
# Date math - language-agnostic.
# ---------------------------------------------------------------

def next_occurrence_of_holiday(resolved, lang, from_date=None):
    """Returns the next date (today or later) this holiday falls on,
    searching this year then next year - holidays are annual, so two
    years of lookahead is always enough regardless of what day
    'today' is."""
    from_date = from_date or date.today()
    if resolved == EASTER_SENTINEL:
        for year in (from_date.year, from_date.year + 1):
            d = _easter(year)
            if d >= from_date:
                return d
        return None
    country_holidays = _country_holidays(lang, [from_date.year, from_date.year + 1])
    matches = sorted(d for d, name in country_holidays.items()
                      if name == resolved and d >= from_date)
    return matches[0] if matches else None


def is_holiday_today(lang):
    """Returns the holiday name(s) for today in this locale's
    country, or None if today isn't one. A day can have more than one
    entry (e.g. a holiday coinciding with a flag day) - returns the
    first, joined-by-';' raw value from the library as-is rather than
    picking one arbitrarily, since the library itself already
    represents multiple same-day entries that way (see the Sweden
    'Påskdagen; Söndag' example found during research)."""
    today = date.today()
    country_holidays = _country_holidays(lang, [today.year])
    return country_holidays.get(today)


def weekday_name(target_date, lang):
    """Localized weekday name via the standard library's own locale
    data would require setting the process locale (not thread-safe,
    affects the whole process) - deliberately avoided. Uses a small
    hand-written table instead, same approach as
    ovos-skill-geometry's hand-authored glossary rather than pulling
    in a locale/i18n dependency for 5 weekday names."""
    weekday_names = {
        "en-us": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
        "da-dk": ["mandag", "tirsdag", "onsdag", "torsdag", "fredag", "lørdag", "søndag"],
        "de-de": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
        "fr-fr": ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"],
        "es-es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    }
    names = weekday_names.get(lang.lower(), weekday_names["en-us"])
    return names[target_date.weekday()]


def days_between(from_date, to_date):
    return (to_date - from_date).days


# ---------------------------------------------------------------
# Common Query safety net - narrow, same pattern as
# ovos-skill-geometry/-geography: only "what is X" style phrasings
# that risk being misrouted by a semantic classifier before our own
# Padatious intents get a chance (see OpenVoiceOS/ovos-m2v-pipeline
# #68), reusing the exact same resolve_holiday() intents already use
# rather than a second implementation.
# ---------------------------------------------------------------
QUESTION_PREFIXES = {
    "en-us": ["when is ", "when's "],
    "da-dk": ["hvornår er det ", "hvornår er "],
    "de-de": ["wann ist "],
    "fr-fr": ["quand est ", "c'est quand "],
    "es-es": ["cuándo es "],
}


def _strip_question_prefix(phrase, lang):
    lang = lang.lower()
    stripped = phrase.strip().rstrip("?").strip()
    lower = stripped.lower()
    for prefix in QUESTION_PREFIXES.get(lang, []):
        if lower.startswith(prefix):
            return stripped[len(prefix):].strip()
    return None


class Holidays(OVOSSkill):
    """Fixed intents only (not FallbackSkill) - see DEVELOPMENT.md
    "Why fixed intents, not FallbackSkill" for the reasoning."""

    @common_query()
    def handle_common_query(self, phrase, lang):
        subject = _strip_question_prefix(phrase, lang)
        if not subject:
            return None
        resolved = resolve_holiday(subject, lang)
        if resolved is None:
            return None
        next_date = next_occurrence_of_holiday(resolved, lang)
        if next_date is None:
            return None
        return self._speak_date_dialog(next_date, lang), 0.8

    def _speak_date_dialog(self, target_date, lang):
        """Formats a date as a spoken sentence fragment (weekday +
        ISO-ish date) for use both by Common Query (which needs a
        plain string, not a self.speak_dialog() call) and internally
        as the shared formatting logic for intent handlers."""
        weekday = weekday_name(target_date, lang)
        return f"{weekday}, {target_date.isoformat()}"

    @intent_handler("is_today_holiday.intent")
    def handle_is_today_holiday(self, message):
        holiday_name = is_holiday_today(self.lang)
        if holiday_name:
            self.speak_dialog("today_is_holiday", {"holiday": holiday_name})
        else:
            self.speak_dialog("today_is_not_holiday")

    @intent_handler("when_is_holiday.intent")
    def handle_when_is_holiday(self, message):
        raw = message.data.get("holiday")
        resolved = resolve_holiday(raw, self.lang)
        if resolved is None:
            self.speak_dialog("holiday_not_understood", {"holiday": raw or ""})
            return
        next_date = next_occurrence_of_holiday(resolved, self.lang)
        if next_date is None:
            self.speak_dialog("holiday_not_understood", {"holiday": raw or ""})
            return
        display_name = holiday_display_name(resolved, self.lang)
        self.speak_dialog("when_is_holiday", {
            "holiday": display_name,
            "weekday": weekday_name(next_date, self.lang),
            "date": next_date.isoformat(),
        })

    @intent_handler("days_until_holiday.intent")
    def handle_days_until_holiday(self, message):
        raw = message.data.get("holiday")
        resolved = resolve_holiday(raw, self.lang)
        if resolved is None:
            self.speak_dialog("holiday_not_understood", {"holiday": raw or ""})
            return
        next_date = next_occurrence_of_holiday(resolved, self.lang)
        if next_date is None:
            self.speak_dialog("holiday_not_understood", {"holiday": raw or ""})
            return
        days = days_between(date.today(), next_date)
        display_name = holiday_display_name(resolved, self.lang)
        if days == 0:
            self.speak_dialog("holiday_is_today", {"holiday": display_name})
        else:
            self.speak_dialog("days_until_holiday", {"holiday": display_name, "days": days})

    @intent_handler("weekday_for_date.intent")
    def handle_weekday_for_date(self, message):
        target_date = self._parse_date(message.data.get("date_utterance") or message.data.get("utterance"))
        if target_date is None:
            self.speak_dialog("date_not_understood")
            return
        self.speak_dialog("weekday_for_date", {
            "weekday": weekday_name(target_date, self.lang),
            "date": target_date.isoformat(),
        })

    def _parse_date(self, utterance):
        """Uses OVOSSkill's own get_response()-adjacent date-parsing
        helper (extract_datetime, already a transitive dependency via
        ovos-workshop/ovos-date-parser) rather than a second date-
        parsing implementation - see DEVELOPMENT.md "Date parsing:
        reusing the platform's own extractor"."""
        if not utterance:
            return None
        try:
            from ovos_date_parser import extract_datetime
            result = extract_datetime(utterance, lang=self.lang)
        except Exception:
            return None
        if result is None:
            return None
        dt, _ = result
        return dt.date()
