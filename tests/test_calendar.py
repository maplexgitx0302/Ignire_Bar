import unittest
from datetime import date, datetime, timedelta

from ignire_calendar import (
    EPOCH_START,
    MAX_GREGORIAN_DATE,
    MAX_NEW_YEAR,
    MIN_GREGORIAN_DATE,
    MIN_NEW_YEAR,
    CalendarRangeError,
    build_verification_rows,
    build_year_rows,
    get_calendar_year,
    is_leap_year,
    new_year_start_for_gregorian_year,
    start_of_year,
    to_gregorian,
    to_new_calendar,
    year_label,
)


class LeapYearTests(unittest.TestCase):
    def test_gregorian_leap_year_rules(self) -> None:
        for year in (4, 1996, 2000, 2024, 10000):
            with self.subTest(year=year):
                self.assertTrue(is_leap_year(year))
        for year in (1, 100, 1900, 2023, 2100):
            with self.subTest(year=year):
                self.assertFalse(is_leap_year(year))

    def test_invalid_years_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            is_leap_year(0)
        with self.assertRaises(TypeError):
            is_leap_year(True)


class CalendarBoundaryTests(unittest.TestCase):
    def test_epoch(self) -> None:
        result = to_new_calendar(EPOCH_START)
        self.assertEqual((result.year, result.month, result.day), (1, 1, 1))
        self.assertEqual(to_gregorian(1, 1, 1), EPOCH_START)

    def test_new_year_rule(self) -> None:
        self.assertEqual(new_year_start_for_gregorian_year(2023), date(2023, 8, 23))
        self.assertEqual(new_year_start_for_gregorian_year(2024), date(2024, 8, 22))
        self.assertEqual(new_year_start_for_gregorian_year(2027), date(2027, 8, 23))

    def test_supported_limits_are_complete_years(self) -> None:
        first = get_calendar_year(MIN_NEW_YEAR)
        last = get_calendar_year(MAX_NEW_YEAR)
        self.assertEqual(first.start, MIN_GREGORIAN_DATE)
        self.assertEqual(last.end - timedelta(days=1), MAX_GREGORIAN_DATE)
        self.assertEqual(to_new_calendar(MIN_GREGORIAN_DATE).day_of_year, 1)
        self.assertEqual(to_new_calendar(MAX_GREGORIAN_DATE).day_of_year, last.length)

    def test_dates_outside_complete_year_range_are_rejected(self) -> None:
        with self.assertRaises(CalendarRangeError):
            to_new_calendar(MIN_GREGORIAN_DATE - timedelta(days=1))
        with self.assertRaises(CalendarRangeError):
            to_new_calendar(MAX_GREGORIAN_DATE + timedelta(days=1))
        with self.assertRaises(CalendarRangeError):
            start_of_year(MIN_NEW_YEAR - 1)
        with self.assertRaises(CalendarRangeError):
            start_of_year(MAX_NEW_YEAR + 1)

    def test_non_date_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            to_new_calendar("2023-08-23")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            to_new_calendar(datetime(2023, 8, 23, 12))


class ConversionTests(unittest.TestCase):
    def test_dates_before_epoch_have_unambiguous_labels(self) -> None:
        previous_year = to_new_calendar(date(2022, 8, 22))
        year_before_that = to_new_calendar(date(2021, 8, 22))
        self.assertEqual(previous_year.year, 0)
        self.assertEqual(previous_year.display_year, "前一年")
        self.assertEqual(year_before_that.year, -1)
        self.assertEqual(year_before_that.display_year, "前2年")
        self.assertEqual(year_label(1), "1 年")

    def test_invalid_ignire_dates_are_rejected(self) -> None:
        invalid_dates = ((1, -1, 1), (1, 13, 1), (1, 1, 0), (1, 1, 31))
        for value in invalid_dates:
            with self.subTest(value=value), self.assertRaises(ValueError):
                to_gregorian(*value)

        five_day_year = next(
            year
            for year in range(1, 20)
            if get_calendar_year(year).festival_days == 5
        )
        with self.assertRaises(ValueError):
            to_gregorian(five_day_year, 0, 6)

    def test_fixed_alignment_rules_across_supported_gregorian_years(self) -> None:
        for year in range(2, 9999):
            with self.subTest(year=year, rule="March 1"):
                march = to_new_calendar(date(year, 3, 1))
                self.assertEqual((march.month, march.day), (7, 12))
            with self.subTest(year=year, rule="August 17"):
                festival = to_new_calendar(date(year, 8, 17))
                self.assertEqual((festival.month, festival.day), (0, 1))

    def test_every_year_is_well_formed(self) -> None:
        for year in range(MIN_NEW_YEAR, MAX_NEW_YEAR + 1):
            calendar_year = get_calendar_year(year)
            with self.subTest(year=year):
                self.assertIn(calendar_year.length, (365, 366))
                self.assertIn(calendar_year.festival_days, (5, 6))
                self.assertEqual(
                    to_new_calendar(calendar_year.start).day_of_year,
                    1,
                )
                self.assertEqual(
                    to_new_calendar(calendar_year.end - timedelta(days=1)).day_of_year,
                    calendar_year.length,
                )

    def test_round_trip_for_a_full_gregorian_cycle(self) -> None:
        current = date(2000, 1, 1)
        end = date(2400, 1, 1)
        while current < end:
            converted = to_new_calendar(current)
            self.assertEqual(
                to_gregorian(converted.year, converted.month, converted.day),
                current,
            )
            current += timedelta(days=1)

    def test_year_rows_cover_the_year(self) -> None:
        rows = build_year_rows(1)
        calendar_year = get_calendar_year(1)
        self.assertEqual(len(rows), calendar_year.length)
        self.assertEqual(rows[0]["公曆日期"], EPOCH_START.isoformat())
        self.assertEqual(rows[-1]["新曆序日"], calendar_year.length)
        self.assertEqual(
            sum(row["是否祭典"] == "是" for row in rows),
            calendar_year.festival_days,
        )

    def test_canonical_verification_rows_pass(self) -> None:
        rows = build_verification_rows(2000, 2399)
        self.assertEqual(len(rows), 2000)
        self.assertTrue(all(row["結果"] == "✅" for row in rows))


if __name__ == "__main__":
    unittest.main()
