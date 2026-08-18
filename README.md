# Holidays — a design document, not a working skill yet

**Status: idea and library-investigation stage.**

## The idea

"Hvornår er det påske i år", "er i dag en helligdag", "hvor mange
dage er der mellem jul og nytår" - public-holiday lookups and simple
calendar math, fully offline.

## Sourcing: computed, not bundled

Unlike `ovos-skill-nameday` (which needs an actual bundled per-locale
dataset), holiday dates can be **computed algorithmically** via the
Python `holidays` library - it covers ~100 countries, computes
movable feasts like Easter via the Computus algorithm rather than a
static lookup table, and needs zero network access or bundled data
files at runtime. This is a meaningfully different (and simpler)
architecture than every other skill in this project family, since
there's no `build_data.py`/`titles_*.json`/`summaries_*.json` step at
all - just a dependency and a locale-to-country mapping.

## Scope: two related but distinct capabilities

1. **Holiday lookup** - "is today a holiday", "when is Easter this
   year", "what's the next public holiday" - powered by the
   `holidays` library.
2. **General date arithmetic** - "how many days between X and Y",
   "what day of the week is/was [date]", "how many weeks until
   Christmas" - pure calculation, no library needed beyond the
   standard library's own date handling.

Both were originally considered for a PR to the official
`OpenVoiceOS/ovos-skill-date-time` skill instead of a new skill here,
since date arithmetic in particular is a natural, small extension of
what that skill already does (see
[ovos-skill-date-time#274](https://github.com/OpenVoiceOS/ovos-skill-date-time/issues/274)
for that half). Holiday lookup was judged too large a scope addition
for someone else's skill (a new dependency, multi-country data,
meaningfully expanding what "date-time" means) to propose as a PR -
better as its own thing here. Worth revisiting whether date
arithmetic ends up here instead, depending on how the upstream issue
is received.

## Relationship to ovos-skill-nameday

Deliberately kept separate - see "Relationship to a possible
holidays/calendar skill" in `ovos-skill-nameday`'s README for the
reasoning (different sourcing architecture, different maintenance
burden).

## Open questions (resolve before implementing)

- Locale-to-country mapping: `holidays` is keyed by country code, not
  language code - `da-dk` maps cleanly to Denmark, but a locale like
  `es-es` doesn't uniquely determine which Spanish-speaking country's
  holiday calendar to use. Needs an explicit mapping or a
  configurable "which country's holidays" setting, not an assumption.
- Whether the upstream `ovos-skill-date-time` PR
  (issue #274) lands, and whether that changes this skill's scope
  down to just holiday lookup.
- Regional/subnational holidays (some countries have state or
  province-level holidays in addition to national ones) - `holidays`
  supports this via subdivision codes, but worth deciding if v1 needs
  it or national-only is enough to start.

## Category
**Daily**

## Tags
#holidays #calendar #date-math #idea #design-doc
