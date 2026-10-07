"""Canonical rule checks used by the UI and automated tests."""

from __future__ import annotations

from datetime import date

from .calendar import is_leap_year, to_new_calendar


def expected_alignment(gregorian_date: date) -> tuple[int, int]:
    """Return the fixed ``(month, day)`` a canonical Gregorian date must map to.

    Month 0 denotes a festival day, matching :class:`NewCalendarDate`.
    """

    year = gregorian_date.year
    month_day = (gregorian_date.month, gregorian_date.day)
    if month_day == (3, 1):
        return (7, 12)
    if month_day == (8, 17):
        return (0, 1)
    if month_day == (8, 22):
        return (0, 6) if is_leap_year(year + 1) else (1, 1)
    if month_day == (8, 23):
        return (1, 1) if is_leap_year(year + 1) else (1, 2)
    if month_day == (2, 29):
        return (7, 11)
    if month_day == (2, 28):
        return (7, 10) if is_leap_year(year) else (7, 11)
    raise ValueError("no canonical rule for this date")


def _format_alignment(month: int, day: int) -> str:
    return f"祭典第 {day} 天" if month == 0 else f"新曆 {month}/{day}"


def expected_rule(gregorian_date: date) -> str:
    """Describe the expected alignment for a canonical Gregorian date."""

    return _format_alignment(*expected_alignment(gregorian_date))


def matches_rule(gregorian_date: date) -> bool:
    """Return whether a canonical Gregorian date satisfies its fixed alignment."""

    result = to_new_calendar(gregorian_date)
    return (result.month, result.day) == expected_alignment(gregorian_date)


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
            expected = expected_alignment(gregorian_date)
            rows.append(
                {
                    "公曆年份": year,
                    "公曆日期": gregorian_date.isoformat(),
                    "期望": _format_alignment(*expected),
                    "實際": _format_alignment(actual.month, actual.day),
                    "結果": "✅" if (actual.month, actual.day) == expected else "❌",
                    "新曆序日": actual.day_of_year,
                }
            )
    return rows
