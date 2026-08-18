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

## Collision risk with ovos-skill-nameday

**Correction, checked against the actual `holidays` library data**:
an earlier version of this section used "Sankt Hans" (23 June, whose
name embeds the common given name "Hans") as the example collision
case. Verified against `holidays.Denmark(years=2026,
categories=('public','optional'))` and it's simply **not present** in
either category - it's a folk tradition, not tracked by this library
at all for Denmark. Don't assume a plausible-sounding example holds
without checking the actual data source, same lesson wiki-offline
learned the hard way with its title-sourcing.

The real, **verified** collision case is Finland's official "flag
days" (liputuspäivät), which the library does track as `optional`
category entries and which are genuinely named after real people -
e.g. `2026-04-09 Mikael Agricolan päivä, suomen kielen päivä`
(Mikael Agricola Day). "Mikael" is an ordinary Finnish given name
with its own name day, so "milloin on Mikael-päivä" risks the exact
same collision as the originally-imagined Danish case, just for a
different country and confirmed to actually exist in the data.

**Resolution** (unchanged in substance, now grounded in a real
example): this skill's "when is X" intent trains its `{holiday}` slot
on a closed, known list of actual holiday/flag-day names pulled
directly from the `holidays` library's own data per country - not
open vocabulary. "Mikael Agricolan päivä" only matches here because
it's a literal entry in that closed, per-country list; a bare
"Mikael" never matches this skill's intent at all, closed-list slots
don't partial-match. `ovos-skill-nameday`, by contrast, requires an
explicit anchor word in the utterance and matches an open name slot -
so a plain "when is Mikael's name day" only ever routes there.

A genuinely ambiguous utterance with no anchor word and no full
holiday-name match is left unhandled by both skills deliberately,
rather than guessing - same kind of accepted, documented linguistic
gray zone as geometry's perimeter/omkreds word-sharing, not a bug to
solve.

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
