# <img src='icon.png' card_color='#1E8882' width='50' height='50' style='vertical-align:bottom'/> Holidays

Public holidays, Easter, and calendar-date questions for OVOS - "is
today a holiday", "when is Christmas", "how many days until Easter",
"what day of the week is March 3rd". Fully offline, available in
English, Danish, German, French, and Spanish.

[![Tests](https://github.com/andlo/ovos-skill-holidays/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-holidays/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-holidays.svg)](https://pypi.org/project/ovos-skill-holidays/)

- [What it answers](#what-it-answers)
- [Usage](#usage)
- [Sourcing: computed, not bundled](#sourcing-computed-not-bundled)
- [Relationship to ovos-skill-nameday](#relationship-to-ovos-skill-nameday)
- [Known limitations](#known-limitations)
- [Install](#install)
- [Development](#development)

## What it answers

- **Is today a holiday** - `"is today a holiday"`.
- **When a named holiday falls** - `"when is Christmas"`, including
  Easter (`"when is Easter"`) computed directly via Computus rather
  than depending on it appearing in every country's own holiday list
  (some countries only list Easter Monday, since Easter Sunday is
  implicit).
- **Days until a named holiday** - `"how many days until Easter"`.
- **What weekday a given date falls/fell on** - `"what day of the
  week is March 3rd"`, `"what day of the week was May 17th 1990"`.

**Not included**: general arbitrary date-to-date arithmetic ("how
many days between March 3rd and June 12th") - that's proposed as a
small upstream addition to the official `ovos-skill-date-time` skill
instead of a new skill here, since it's a natural extension of what
that skill already does, not something specific to holidays. See
[OpenVoiceOS/ovos-skill-date-time#274](https://github.com/OpenVoiceOS/ovos-skill-date-time/issues/274).

## Usage
```
"is today a holiday"
"when is christmas"
"how many days until easter"
"what day of the week is march 3rd"
"er i dag en helligdag"                   (Danish)
"hvornår er det jul"                      (Danish)
"hvor mange dage er der til påske"        (Danish)
"ist heute ein feiertag"                  (German)
"wann ist weihnachten"                    (German)
"est-ce que c'est férié aujourd'hui"      (French)
"quand est noël"                          (French)
"es hoy festivo"                          (Spanish)
"cuándo es navidad"                       (Spanish)
```

## Sourcing: computed, not bundled

Unlike `ovos-skill-nameday` (which needs an actual bundled per-locale
dataset), holiday dates are **computed live** via the Python
`holidays` library - it covers ~100 countries and implements Computus
and other calendar rules directly, no network access and no bundled
date data at runtime. There is no `build_data.py`/`titles_*.json`
step the way `ovos-skill-wiki-offline`/`ovos-skill-geography` have -
just a dependency, a locale-to-country mapping, and a small
hand-curated per-locale alias list (`locale/<lang>/holiday_aliases.json`)
for the handful of holidays people are likely to ask about by an
everyday name rather than the library's formal calendar name (e.g.
Danish "jul" vs. the library's own "Juledag").

## Relationship to ovos-skill-nameday

Deliberately kept as a separate skill from name-day (navnedag)
lookups, despite both answering "what's special about today" -
holidays are computed algorithmically here, while name days need an
actual bundled per-locale dataset (closer to `ovos-skill-wiki-offline`'s
architecture). See `ovos-skill-nameday`'s README for the fuller
reasoning.

**Collision risk, verified rather than assumed**: an early draft used
an invented Danish example ("Sankt Hans") that turned out not to
exist in the actual `holidays` library data at all. The real,
checked collision case is Finland's official "flag days"
(liputuspäivät), several of which are genuinely named after real
people - e.g. `Mikael Agricolan päivä` (Mikael Agricola Day), where
"Mikael" is also an ordinary Finnish given name with its own name
day. Resolved by how each skill's intent is scoped: this skill's
`{holiday}` slot captures free text and validates it in code against
that locale's own official holiday names (`resolve_holiday()`) - a
bare "Mikael" with no match in that list simply doesn't resolve here,
while `ovos-skill-nameday`'s intents require an explicit anchor word
("navnedag" or the local equivalent) and match an open name slot
instead, so the two skills' matching utterances don't overlap even
though the underlying words can.

## Known limitations

- **Locale-to-country is a fixed mapping, not a general solution.**
  `holidays` is keyed by ISO country code; a locale like `es-es`
  doesn't uniquely determine a Spanish-speaking country in general
  the way it's mapped here to Spain specifically (not, say, Mexico or
  Argentina) - honest for this project's 5 fixed locales, not a claim
  to solve language-to-country mapping generally.
- **Same-day multi-category name merging.** When a country's library
  entry has two categories both naming the same date, `holidays`
  joins the names with `"; "` (e.g. the US's Martin Luther King Jr.
  Day). Resolution stays consistent either way, but a merged name
  would sound awkward spoken verbatim if a user's phrasing happened
  to substring-match into one rather than a curated alias.
- **Regional/subnational holidays aren't included** - `holidays`
  supports state/province-level subdivisions via a subdivision code,
  but this skill only requests national-level categories for now.
- **The alias list is hand-curated and incomplete by design** - it
  covers the holidays people are actually likely to ask about by an
  everyday name per locale; anything not listed still resolves via a
  substring match against the library's own official names, just
  less reliably than a curated entry.

See [DEVELOPMENT.md](DEVELOPMENT.md) for the full reasoning behind
each of these, plus two real alias-curation errors and a category-
naming bug caught by verifying against the library's actual output
rather than assuming it during development.

## Install
```bash
pip install ovos-skill-holidays
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Daily**

## Tags
#holidays #calendar #date-math #easter
