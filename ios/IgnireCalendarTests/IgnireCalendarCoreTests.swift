import XCTest
@testable import IgnireCalendar

final class IgnireCalendarCoreTests: XCTestCase {
    func testEpochRoundTrip() throws {
        let epoch = try GregorianDay(year: 2023, month: 8, day: 23)
        let ignireDate = try IgnireCalendar.date(from: epoch)

        XCTAssertEqual(ignireDate, IgnireDate(year: 1, month: 1, day: 1, dayOfYear: 1))
        XCTAssertEqual(try IgnireCalendar.gregorianDate(year: 1, month: 1, day: 1), epoch)
    }

    func testFixedAlignmentRules() throws {
        for year in 2000...2399 {
            XCTAssertEqual(
                try IgnireCalendar.date(from: GregorianDay(year: year, month: 3, day: 1)).month,
                7
            )
            XCTAssertEqual(
                try IgnireCalendar.date(from: GregorianDay(year: year, month: 3, day: 1)).day,
                12
            )
            let festival = try IgnireCalendar.date(
                from: GregorianDay(year: year, month: 8, day: 17)
            )
            XCTAssertEqual(festival.month, 0)
            XCTAssertEqual(festival.day, 1)
        }
    }

    func testFestivalDayValidation() throws {
        let fiveDayYear = try (1...20).first { try IgnireCalendar.year($0).festivalDayCount == 5 }!
        XCTAssertThrowsError(try IgnireCalendar.gregorianDate(year: fiveDayYear, month: 0, day: 6))
    }

    func testEveryDayRoundTripsAcrossOneGregorianCycle() throws {
        var day = try GregorianDay(year: 2000, month: 1, day: 1)
        let end = try GregorianDay(year: 2400, month: 1, day: 1)
        while day < end {
            let ignire = try IgnireCalendar.date(from: day)
            XCTAssertEqual(
                try IgnireCalendar.gregorianDate(year: ignire.year, month: ignire.month, day: ignire.day),
                day
            )
            day = try day.adding(days: 1)
        }
    }

    func testSupportedDateBoundaries() throws {
        XCTAssertEqual(
            try IgnireCalendar.date(from: IgnireCalendar.minimumGregorianDate).dayOfYear,
            1
        )
        let finalYear = try IgnireCalendar.year(IgnireCalendar.maximumIgnireYear)
        XCTAssertEqual(
            try IgnireCalendar.date(from: IgnireCalendar.maximumGregorianDate).dayOfYear,
            finalYear.length
        )
    }

    func testReferenceDates() throws {
        let cases: [(GregorianDay, IgnireDate)] = [
            (try GregorianDay(year: 2023, month: 8, day: 22), IgnireDate(year: 0, month: 0, day: 6, dayOfYear: 366)),
            (try GregorianDay(year: 2024, month: 2, day: 29), IgnireDate(year: 1, month: 7, day: 11, dayOfYear: 191)),
            (try GregorianDay(year: 2024, month: 8, day: 21), IgnireDate(year: 1, month: 0, day: 5, dayOfYear: 365)),
            (try GregorianDay(year: 2026, month: 10, day: 7), IgnireDate(year: 4, month: 2, day: 17, dayOfYear: 47)),
            (try GregorianDay(year: 2099, month: 8, day: 22), IgnireDate(year: 77, month: 1, day: 1, dayOfYear: 1)),
        ]
        for (gregorian, ignire) in cases {
            XCTAssertEqual(try IgnireCalendar.date(from: gregorian), ignire, gregorian.iso8601)
        }
        XCTAssertEqual(cases[3].1.displayText, "新曆 4 年 2/17")
        XCTAssertEqual(cases[0].1.displayText, "新曆（前一年）祭典第 6 天")
    }

    func testDayNumberRoundTripsAcrossTheWholeRange() throws {
        let first = try GregorianDay(year: 1, month: 1, day: 1)
        let last = try GregorianDay(year: 9_999, month: 12, day: 31)
        XCTAssertEqual(try GregorianDay(year: 1970, month: 1, day: 1).dayNumber, 0)
        XCTAssertEqual(first.days(until: last), 3_652_058)
        var dayNumber = first.dayNumber
        while dayNumber <= last.dayNumber {
            let day = try GregorianDay(dayNumber: dayNumber)
            XCTAssertEqual(day.dayNumber, dayNumber)
            dayNumber += 97  // Sample every 97th day to keep the test fast.
        }
        XCTAssertThrowsError(try last.adding(days: 1))
        XCTAssertThrowsError(try GregorianDay(year: 2023, month: 2, day: 29))
        XCTAssertThrowsError(try GregorianDay(year: 2023, month: 13, day: 1))
    }

    func testDeviceDateConversionUsesTheGivenTimeZone() throws {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(identifier: "Asia/Taipei")!
        // 2026-10-06 16:30 UTC is already 2026-10-07 00:30 in Taipei.
        let instant = Date(timeIntervalSince1970: 1_791_304_200)
        XCTAssertEqual(try GregorianDay(instant, in: calendar), try GregorianDay(year: 2026, month: 10, day: 7))
        let start = try XCTUnwrap(GregorianDay(year: 2026, month: 10, day: 7).startDate(in: calendar))
        XCTAssertEqual(try GregorianDay(start, in: calendar), try GregorianDay(year: 2026, month: 10, day: 7))
    }
}
