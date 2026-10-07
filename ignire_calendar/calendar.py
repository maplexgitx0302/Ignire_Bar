"""Pure conversion logic for the Ignire calendar.

The calendar has twelve 30-day months followed by five or six festival days.
Its epoch is Gregorian 2023-08-23, which is Ignire year 1, month 1, day 1.

Keeping this module independent from Streamlit and pandas makes every rule usable
from scripts, tests, and future interfaces without importing UI dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterator

EPOCH_START = date(2023, 8, 23)
EPOCH_YEAR = 1
MONTHS_PER_YEAR = 12
DAYS_PER_MONTH = 30
REGULAR_DAYS_PER_YEAR = MONTHS_PER_YEAR * DAYS_PER_MONTH

# Python's date cannot represent Gregorian year 0 or 10000. We therefore expose
# only complete Ignire years whose start and exclusive end are representable.
MIN_NEW_YEAR = 1 - EPOCH_START.year + EPOCH_YEAR  # -2021, starts in Gregorian 1
MAX_NEW_YEAR = 9998 - EPOCH_START.year + EPOCH_YEAR  # 7976, ends in 9999


class CalendarRangeError(ValueError):
    """Raised when a conversion is outside Python's complete date range."""


def is_leap_year(year: int) -> bool:
    """Return whether *year* is a proleptic Gregorian leap year."""

    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("year must be an integer")
    if year < 1:
        raise ValueError("Gregorian year must be at least 1")
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def new_year_start_for_gregorian_year(gregorian_year: int) -> date:
    """Return the Ignire new-year date that occurs in a Gregorian year.

    It falls on August 23 when the following Gregorian year is a leap year,
    and August 22 otherwise.
    """

    if not isinstance(gregorian_year, int) or isinstance(gregorian_year, bool):
        raise TypeError("gregorian_year must be an integer")
    if not 1 <= gregorian_year <= date.max.year:
        raise CalendarRangeError("Gregorian year must be between 1 and 9999")
    day = 23 if is_leap_year(gregorian_year + 1) else 22
    return date(gregorian_year, 8, day)


MIN_GREGORIAN_DATE = new_year_start_for_gregorian_year(1)
MAX_GREGORIAN_DATE = new_year_start_for_gregorian_year(9999) - timedelta(days=1)


_WEEKDAY_LABELS = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")


def weekday_label(gregorian_date: date) -> str:
    """Return the Traditional Chinese weekday name of a Gregorian date."""

    return _WEEKDAY_LABELS[gregorian_date.weekday()]


def year_label(year: int) -> str:
    """Format an Ignire year without displaying a year zero."""

    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("year must be an integer")
    if year >= 1:
        return f"{year} 年"
    years_before = 1 - year
    return "前一年" if years_before == 1 else f"前{years_before}年"


@dataclass(frozen=True)
class CalendarYear:
    """Gregorian boundaries and derived metadata for one Ignire year."""

    year: int
    start: date
    end: date  # exclusive

    @property
    def length(self) -> int:
        return (self.end - self.start).days

    @property
    def festival_days(self) -> int:
        return self.length - REGULAR_DAYS_PER_YEAR

    @property
    def label(self) -> str:
        return year_label(self.year)


@dataclass(frozen=True)
class NewCalendarDate:
    """A date in the Ignire calendar.

    ``month`` is 1 through 12 for regular days and 0 for festival days.
    ``day`` is the day of that month, or the festival-day number when month is 0.
    """

    year: int
    month: int
    day: int
    day_of_year: int

    @property
    def is_festival(self) -> bool:
        return self.month == 0

    @property
    def display_year(self) -> str:
        return year_label(self.year)

    @property
    def display_date(self) -> str:
        if self.is_festival:
            return f"新曆（{self.display_year}）祭典第 {self.day} 天"
        if self.year >= 1:
            return f"新曆 {self.display_year} {self.month}/{self.day}"
        return f"新曆（{self.display_year}）{self.month}/{self.day}"


def _require_new_year(year: int) -> None:
    if not isinstance(year, int) or isinstance(year, bool):
        raise TypeError("Ignire year must be an integer")
    if not MIN_NEW_YEAR <= year <= MAX_NEW_YEAR:
        raise CalendarRangeError(
            f"Ignire year must be between {MIN_NEW_YEAR} and {MAX_NEW_YEAR} "
            "so that the complete year is representable"
        )


def start_of_year(year: int) -> date:
    """Return the Gregorian start date of a complete Ignire year in O(1)."""

    _require_new_year(year)
    gregorian_year = EPOCH_START.year + year - EPOCH_YEAR
    return new_year_start_for_gregorian_year(gregorian_year)


def get_calendar_year(year: int) -> CalendarYear:
    """Return boundaries and metadata for an Ignire year."""

    start = start_of_year(year)
    end = new_year_start_for_gregorian_year(start.year + 1)
    result = CalendarYear(year=year, start=start, end=end)
    if result.length not in (365, 366):  # Defensive assertion around the core rule.
        raise RuntimeError(f"unexpected Ignire year length: {result.length}")
    return result


def to_new_calendar(gregorian_date: date) -> NewCalendarDate:
    """Convert a Gregorian date to its Ignire calendar representation."""

    if type(gregorian_date) is not date:
        raise TypeError("gregorian_date must be a datetime.date")
    if not MIN_GREGORIAN_DATE <= gregorian_date <= MAX_GREGORIAN_DATE:
        raise CalendarRangeError(
            f"Gregorian date must be between {MIN_GREGORIAN_DATE.isoformat()} "
            f"and {MAX_GREGORIAN_DATE.isoformat()}"
        )

    start_year = gregorian_date.year
    candidate_start = new_year_start_for_gregorian_year(start_year)
    if gregorian_date < candidate_start:
        start_year -= 1
        candidate_start = new_year_start_for_gregorian_year(start_year)

    year = start_year - EPOCH_START.year + EPOCH_YEAR
    day_of_year = (gregorian_date - candidate_start).days + 1
    if day_of_year <= REGULAR_DAYS_PER_YEAR:
        month, zero_based_day = divmod(day_of_year - 1, DAYS_PER_MONTH)
        return NewCalendarDate(year, month + 1, zero_based_day + 1, day_of_year)
    return NewCalendarDate(year, 0, day_of_year - REGULAR_DAYS_PER_YEAR, day_of_year)


def to_gregorian(year: int, month: int, day: int) -> date:
    """Convert an Ignire date to Gregorian.

    Use month 1 through 12 for regular dates, or month 0 and day 1 through 5/6
    for festival dates.
    """

    calendar_year = get_calendar_year(year)
    if not isinstance(month, int) or isinstance(month, bool):
        raise TypeError("month must be an integer")
    if not isinstance(day, int) or isinstance(day, bool):
        raise TypeError("day must be an integer")

    if month == 0:
        if not 1 <= day <= calendar_year.festival_days:
            raise ValueError(
                f"Ignire year {year} has {calendar_year.festival_days} festival days"
            )
        offset = REGULAR_DAYS_PER_YEAR + day - 1
    else:
        if not 1 <= month <= MONTHS_PER_YEAR:
            raise ValueError("month must be 1 through 12, or 0 for a festival day")
        if not 1 <= day <= DAYS_PER_MONTH:
            raise ValueError("day must be 1 through 30")
        offset = (month - 1) * DAYS_PER_MONTH + day - 1
    return calendar_year.start + timedelta(days=offset)


def iter_calendar_year(year: int) -> Iterator[tuple[date, NewCalendarDate]]:
    """Yield every Gregorian/Ignire date pair in an Ignire year."""

    calendar_year = get_calendar_year(year)
    for offset in range(calendar_year.length):
        gregorian_date = calendar_year.start + timedelta(days=offset)
        yield gregorian_date, to_new_calendar(gregorian_date)


def build_year_rows(year: int) -> list[dict[str, object]]:
    """Build serialization-friendly rows for a yearly table or CSV export."""

    rows: list[dict[str, object]] = []
    for gregorian_date, ignire_date in iter_calendar_year(year):
        rows.append(
            {
                "新曆年": year,
                "新曆月": "祭典" if ignire_date.is_festival else ignire_date.month,
                "新曆日": ignire_date.day,
                "新曆序日": ignire_date.day_of_year,
                "是否祭典": "是" if ignire_date.is_festival else "否",
                "公曆日期": gregorian_date.isoformat(),
                "星期": weekday_label(gregorian_date),
            }
        )
    return rows
