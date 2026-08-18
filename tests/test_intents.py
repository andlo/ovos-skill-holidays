"""Tests for the 4 intent handlers, en-us locale."""
from datetime import date
from unittest.mock import MagicMock


def _msg(**data):
    m = MagicMock()
    m.data = data
    return m


def test_is_today_holiday_positive(skill, monkeypatch):
    skill.speak_dialog = MagicMock()
    monkeypatch.setattr(
        "holidays_skill.is_holiday_today", lambda lang: "Christmas Day")
    skill.handle_is_today_holiday(_msg())
    skill.speak_dialog.assert_called_once_with(
        "today_is_holiday", {"holiday": "Christmas Day"})


def test_is_today_holiday_negative(skill, monkeypatch):
    skill.speak_dialog = MagicMock()
    monkeypatch.setattr(
        "holidays_skill.is_holiday_today", lambda lang: None)
    skill.handle_is_today_holiday(_msg())
    skill.speak_dialog.assert_called_once_with("today_is_not_holiday")


def test_when_is_holiday_known(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_when_is_holiday(_msg(holiday="christmas"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "when_is_holiday"
    assert data["holiday"] == "Christmas Day"
    assert data["date"].endswith("12-25")


def test_when_is_holiday_unknown(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_when_is_holiday(_msg(holiday="definitely not a holiday"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "holiday_not_understood"
    assert data["holiday"] == "definitely not a holiday"


def test_when_is_holiday_easter(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_when_is_holiday(_msg(holiday="easter"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "when_is_holiday"
    assert data["holiday"] == "Easter"


def test_days_until_holiday(skill, monkeypatch):
    import holidays_skill
    skill.speak_dialog = MagicMock()

    class FixedDate(holidays_skill.date):
        @classmethod
        def today(cls):
            return holidays_skill.date(2026, 12, 20)
    monkeypatch.setattr(holidays_skill, "date", FixedDate)
    skill.handle_days_until_holiday(_msg(holiday="christmas"))
    skill.speak_dialog.assert_called_once_with(
        "days_until_holiday", {"holiday": "Christmas Day", "days": 5})


def test_days_until_holiday_is_today(skill, monkeypatch):
    import holidays_skill
    skill.speak_dialog = MagicMock()

    class FixedDate(holidays_skill.date):
        @classmethod
        def today(cls):
            return holidays_skill.date(2026, 12, 25)
    monkeypatch.setattr(holidays_skill, "date", FixedDate)
    skill.handle_days_until_holiday(_msg(holiday="christmas"))
    skill.speak_dialog.assert_called_once_with(
        "holiday_is_today", {"holiday": "Christmas Day"})


def test_days_until_holiday_unknown(skill):
    skill.speak_dialog = MagicMock()
    skill.handle_days_until_holiday(_msg(holiday="nonsense"))
    dialog_name, data = skill.speak_dialog.call_args[0]
    assert dialog_name == "holiday_not_understood"


def test_weekday_for_date_known(skill, monkeypatch):
    skill.speak_dialog = MagicMock()
    monkeypatch.setattr(skill, "_parse_date", lambda u: date(2026, 8, 18))
    skill.handle_weekday_for_date(_msg(date_utterance="august 18th"))
    skill.speak_dialog.assert_called_once_with(
        "weekday_for_date", {"weekday": "Tuesday", "date": "2026-08-18"})


def test_weekday_for_date_unparseable(skill, monkeypatch):
    skill.speak_dialog = MagicMock()
    monkeypatch.setattr(skill, "_parse_date", lambda u: None)
    skill.handle_weekday_for_date(_msg(date_utterance="gibberish"))
    skill.speak_dialog.assert_called_once_with("date_not_understood")
