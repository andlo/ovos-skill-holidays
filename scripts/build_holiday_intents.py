#!/usr/bin/env python3
"""Write when_is_holiday.intent and days_until_holiday.intent for every
language: the {holiday} templates, plus each template spelled out for every
name in holiday_aliases.json ("when is christmas", "hvornår er det jul").

Why spelled out (issue #2): ovos-skill-date-time, an installer default,
has "when is {date}" / "how many days until {date}". With only a free
{holiday} slot, padatious scored date-time's intent higher and "when is
christmas" never reached this skill; a holiday.entity file was not enough
(tested live). A sentence this skill was trained on word for word wins.
The templates stay for holidays not in the list (resolved against the
`holidays` library's own names).

Run after changing holiday_aliases.json."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "locale"

TEMPLATES = {
    "en-us": {"when_is_holiday": ["when is {holiday}", "when's {holiday}"],
              "days_until_holiday": ["how many days until {holiday}", "how many days left until {holiday}",
                                     "how long until {holiday}"]},
    "da-dk": {"when_is_holiday": ["hvornår er det {holiday}", "hvornår er {holiday}"],
              "days_until_holiday": ["hvor mange dage er der til {holiday}", "hvor lang tid er der til {holiday}"]},
    "de-de": {"when_is_holiday": ["wann ist {holiday}"],
              "days_until_holiday": ["wie viele tage sind es bis {holiday}", "wie lange dauert es bis {holiday}"]},
    "es-es": {"when_is_holiday": ["cuándo es {holiday}"],
              "days_until_holiday": ["cuántos días faltan para {holiday}", "cuánto falta para {holiday}"]},
    "fr-fr": {"when_is_holiday": ["quand est {holiday}", "c'est quand {holiday}"],
              "days_until_holiday": ["combien de jours avant {holiday}", "combien de temps avant {holiday}"]},
}

for lang, intents in TEMPLATES.items():
    d = ROOT / lang
    aliases = json.loads((d / "holiday_aliases.json").read_text(encoding="utf-8"))
    names = sorted({k.lower() for k in aliases if not k.startswith("_")})
    for intent, templates in intents.items():
        lines = list(templates)
        for t in templates:
            lines += [t.replace("{holiday}", n) for n in names]
        (d / f"{intent}.intent").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote holiday intents for", ", ".join(TEMPLATES))
