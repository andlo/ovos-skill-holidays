# Development

## Language data belongs in locale/, not hardcoded in __init__.py

An earlier draft hardcoded `HOLIDAY_ALIASES`, weekday names, the
Easter display name, and the Common Query `QUESTION_PREFIXES`
directly as Python dicts inside `__init__.py`, instead of following
`ovos-skill-geometry`'s established convention of loading translatable
content from `locale/<lang>/*.json` via a `_load_locale_json()`
helper. Caught in review, not by a test - nothing broke, it was
simply the wrong place for the data to live: someone adding or fixing
a translation had to edit Python code instead of a locale file, and
it was inconsistent with every sibling skill in this project family.
Fixed by moving all four into `locale/<lang>/holiday_aliases.json`,
`weekday_names.json`, `easter_name.json`, and `question_prefixes.json`
respectively, loaded the same way geometry loads
`glossary_names.json`/`formula_words.json`. `LOCALE_TO_COUNTRY`
deliberately stayed a Python constant, not a locale file - it isn't
translatable content, it's a structural decision about which country
each of this project's 5 fixed locales maps to.

## Architecture: fixed intents, not FallbackSkill

Public holidays and calendar math are a bounded domain with
predictable question shapes ("is today a holiday", "when is X",
"how many days until X", "what day of the week is X") - the same
category as `ovos-skill-geometry`/`ovos-skill-geography`, not the
open-ended lookup `ovos-skill-wiki-offline` needs `FallbackSkill`
for. This skill uses plain Adapt/Padatious intents plus the same
narrow `@common_query` safety net its siblings use for the
documented `ovos-m2v-pipeline` misrouting bug
(OpenVoiceOS/ovos-m2v-pipeline#68) - not a `FallbackSkill` catch-all.

## Data: computed live, not bundled

Unlike `ovos-skill-wiki-offline`/`ovos-skill-geography`, there is no
`data/build_*.py` fetch step and no bundled `*.json` dataset of
dates. Holiday dates are computed on every query via the `holidays`
Python library (Computus and other calendar rules implemented
directly, no I/O). The only actual "data" shipped is the small,
hand-curated `HOLIDAY_ALIASES` table in `__init__.py` - see below.

## The alias gap: official names vs. how people actually talk

Verified by inspecting real library output, not assumed: the
`holidays` library's own names are the FORMAL calendar names people
don't necessarily use in speech. Denmark's Christmas Day is
"Juledag" in the library; a Dane would say "jul", not "juledag". Same
pattern in every locale checked. `HOLIDAY_ALIASES` hand-maps the
handful of holidays people are actually likely to ask about (by
locale) to the library's exact official name; anything not in that
list falls back to substring-matching the spoken text against
whatever official names the library actually returns for that
locale's country - so a real, less-common holiday not explicitly
aliased can still resolve, just less reliably than a curated one.

**Two real errors caught by verifying instead of guessing** while
building the alias table: French Christmas was initially guessed as
"Fête de Noël" (wrong - the library's actual name is just "Noël"),
and "fête nationale" was initially mapped to "Fête de la Victoire"
(wrong - that's 8 May Victory in Europe Day; the actual 14 July
national day is "Fête nationale"). Caught by running the library and
reading its real output before shipping the alias table, not by
inspection of the code alone.

## Categories aren't standardized across countries

Also verified, not assumed: Denmark's non-statutory
observances/half-days (Grundlovsdag, Juleaftensdag) live under a
category named `'optional'`. The equivalent concept for the US
(Halloween, Valentine's Day, Easter Sunday itself, Mother's/Father's
Day) lives under a DIFFERENTLY-NAMED category, `'unofficial'` -
`'optional'` isn't even in `US.supported_categories` at all. An
earlier draft hard-coded a fixed `('public', 'optional')` tuple and
filtered per-country against what each supports - this silently
dropped every Halloween-style entry for the US, since `'optional'`
never matched anything there. Fixed by just requesting **all**
categories a country's library entry supports, rather than guessing
category names that turn out not to be consistent across countries.

## Known limitation: same-day multi-category name merging

When two categories both name the same date, the `holidays` library
joins the names with `"; "` - e.g. the US's Martin Luther King Jr.
Day gets `"Birthday of Martin Luther King, Jr.; Martin Luther King
Jr. Day"` when both the `'government'` and `'public'` categories are
requested together (which this skill always does, see above). This
doesn't break resolution or the closed-list matching (both
`resolve_holiday()` and `next_occurrence_of_holiday()` call the same
`_country_holidays()` with the same category set, so the merged
string is used consistently on both sides) - but it would sound
awkward spoken aloud verbatim if a user's phrasing happened to
substring-match into one of these merged entries rather than a
curated alias. Not fixed for v1 - a real but narrow edge case,
documented rather than silently glossed over.

## Locale-to-country mapping is a simplification, not a general solution

`holidays` is keyed by ISO country code; a BCP-47 locale like
`es-es` or `en-us` doesn't uniquely determine a country in general
(Spanish is spoken natively in ~20 countries; English in many more).
`LOCALE_TO_COUNTRY` hard-codes one specific country per this
project's existing 5 locales (en-us -> US, es-es -> Spain, not "some
representative Spanish-speaking country") - honest for this fixed
locale set, not a claim to solve the general language-to-country
mapping problem.

## Date parsing: reusing the platform's own extractor

`weekday_for_date.intent`'s date argument is parsed via
`ovos_date_parser.extract_datetime()` - the same date-understanding
OVOS's own core uses - rather than writing a second date-parsing
implementation. Verified directly: handles both relative ("tomorrow")
and absolute ("march 3rd 2020", "3. marts") phrasings correctly, and
correctly keeps an explicit year in the past rather than rolling it
forward (only date-without-year phrasings roll forward to the next
future occurrence, which is the right default for "what day of the
week is march 3rd" without a stated year).

## Collision risk with ovos-skill-nameday

See README "Collision risk with ovos-skill-nameday" for the full
analysis and the verified (not invented) Finnish flag-day example.

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-holidays.git
cd ovos-skill-holidays
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`,
same convention as the rest of this project family.

## Style / conventions

- License: GPL-3.0-or-later
- `locale/<lang-code>/` layout, `skill.json` inside each locale folder
- 5 locales: en-us, da-dk, de-de, fr-fr, es-es (project baseline)
