"""Canonical rule checks used by the UI and automated tests."""

from __future__ import annotations

from datetime import date

from .calendar import is_leap_year, to_new_calendar


def expected_rule(gregorian_date: date) -> str:
    """Describe the expected alignment for a canonical Gregorian date."""

    year = gregorian_date.year
    month_day = (gregorian_date.month, gregorian_date.day)
    if month_day == (3, 1):
        return "新曆 7/12"
    if month_day == (8, 17):
        return "祭典第 1 天"
    if month_day == (8, 22):
        return "祭典第 6 天" if is_leap_year(year + 1) else "新曆 1/1"
    if month_day == (8, 23):
        return "新曆 1/1" if is_leap_year(year + 1) else "新曆 1/2"
    if month_day == (2, 29):
        return "新曆 7/11"
    if month_day == (2, 28):
        return "新曆 7/10" if is_leap_year(year) else "新曆 7/11"
    raise ValueError("no canonical expectation for this date")


def matches_rule(gregorian_date: date) -> bool:
    """Return whether a canonical Gregorian date satisfies its fixed alignment."""

    result = to_new_calendar(gregorian_date)
    year = gregorian_date.year
    month_day = (gregorian_date.month, gregorian_date.day)
    actual = (result.month, result.day)
    if month_day == (3, 1):
        return actual == (7, 12)
    if month_day == (8, 17):
        return actual == (0, 1)
    if month_day == (8, 22):
        return actual == ((0, 6) if is_leap_year(year + 1) else (1, 1))
    if month_day == (8, 23):
        return actual == ((1, 1) if is_leap_year(year + 1) else (1, 2))
    if month_day == (2, 29):
        return actual == (7, 11)
    if month_day == (2, 28):
        return actual == ((7, 10) if is_leap_year(year) else (7, 11))
    raise ValueError("no canonical rule for this date")


def build_verification_rows(first_year: int, last_year: int) -> list[dict[str, object]]:
    """Build canonical rule checks for an inclusive Gregorian year range."""

    if not isinstance(first_year, int) or isinstance(first_year, bool):
        raise TypeError("first_year must be an integer")
    if not isinstance(last_year, int) or isinstance(last_year, bool):
        raise TypeError("last_year must be an integer")
    if not 2 <= first_year <= 9998 or not 2 <= last_year <= 9998:
        raise ValueError("verification years must be between 2 and 9998")
    if first_year > last_year:
        raise ValueError("first_year must not exceed last_year")

    rows: list[dict[str, object]] = []
    for year in range(first_year, last_year + 1):
        dates = [
            date(year, 2, 29) if is_leap_year(year) else date(year, 2, 28),
            date(year, 3, 1),
            date(year, 8, 17),
            date(year, 8, 22),
            date(year, 8, 23),
        ]
        for gregorian_date in dates:
            actual = to_new_calendar(gregorian_date)
            actual_text = (
                f"祭典第 {actual.day} 天"
                if actual.is_festival
                else f"新曆 {actual.month}/{actual.day}"
            )
            rows.append(
                {
                    "公曆年份": year,
                    "公曆日期": gregorian_date.isoformat(),
                    "期望": expected_rule(gregorian_date),
                    "實際": actual_text,
                    "結果": "✅" if matches_rule(gregorian_date) else "❌",
                    "新曆序日": actual.day_of_year,
                }
            )
    return rows
