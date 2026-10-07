import Foundation

/// A timezone-free proleptic Gregorian date used by the Ignire calendar engine.
///
/// Dates are stored as numeric components and compared through a serial day
/// number, so time zones, daylight-saving changes, and `Foundation.Calendar`
/// never take part in calendar arithmetic.
public struct GregorianDay: Comparable, Hashable, Sendable {
    public let year: Int
    public let month: Int
    public let day: Int

    public init(year: Int, month: Int, day: Int) throws {
        guard (1...9_999).contains(year) else {
            throw IgnireCalendarError.unsupportedGregorianDate
        }
        guard (1...12).contains(month),
              (1...Self.daysInMonth(year: year, month: month)).contains(day) else {
            throw IgnireCalendarError.invalidGregorianDate
        }
        self.year = year
        self.month = month
        self.day = day
    }

    /// Creates the date from a serial day number (days since 1970-01-01).
    public init(dayNumber: Int) throws {
        // Howard Hinnant's civil_from_days algorithm.
        let shifted = dayNumber + 719_468
        let era = (shifted >= 0 ? shifted : shifted - 146_096) / 146_097
        let dayOfEra = shifted - era * 146_097
        let yearOfEra = (dayOfEra - dayOfEra / 1_460 + dayOfEra / 36_524 - dayOfEra / 146_096) / 365
        let dayOfYear = dayOfEra - (365 * yearOfEra + yearOfEra / 4 - yearOfEra / 100)
        let shiftedMonth = (5 * dayOfYear + 2) / 153
        let day = dayOfYear - (153 * shiftedMonth + 2) / 5 + 1
        let month = shiftedMonth < 10 ? shiftedMonth + 3 : shiftedMonth - 9
        let year = yearOfEra + era * 400 + (month <= 2 ? 1 : 0)
        try self.init(year: year, month: month, day: day)
    }

    /// Creates the date that `date` falls on in `calendar`'s time zone.
    public init(_ date: Date, in calendar: Calendar = .autoupdatingCurrent) throws {
        var gregorian = Calendar(identifier: .gregorian)
        gregorian.timeZone = calendar.timeZone
        let components = gregorian.dateComponents([.era, .year, .month, .day], from: date)
        guard components.era == 1, let year = components.year,
              let month = components.month, let day = components.day else {
            throw IgnireCalendarError.unsupportedGregorianDate
        }
        try self.init(year: year, month: month, day: day)
    }

    /// Today's Gregorian date in the device's current time zone.
    public static var today: GregorianDay {
        // The device clock is always well inside years 1–9999.
        try! GregorianDay(Date())
    }

    public static func daysInMonth(year: Int, month: Int) -> Int {
        switch month {
        case 2: return IgnireCalendar.isLeapYear(year) ? 29 : 28
        case 4, 6, 9, 11: return 30
        default: return 31
        }
    }

    /// Days since 1970-01-01 (Howard Hinnant's days_from_civil algorithm).
    public var dayNumber: Int {
        let shiftedYear = month <= 2 ? year - 1 : year
        let era = (shiftedYear >= 0 ? shiftedYear : shiftedYear - 399) / 400
        let yearOfEra = shiftedYear - era * 400
        let dayOfYear = (153 * ((month + 9) % 12) + 2) / 5 + day - 1
        let dayOfEra = yearOfEra * 365 + yearOfEra / 4 - yearOfEra / 100 + dayOfYear
        return era * 146_097 + dayOfEra - 719_468
    }

    public func adding(days: Int) throws -> GregorianDay {
        try GregorianDay(dayNumber: dayNumber + days)
    }

    public func days(until end: GregorianDay) -> Int {
        end.dayNumber - dayNumber
    }

    /// Midnight at the start of this day in `calendar`'s time zone.
    public func startDate(in calendar: Calendar = .autoupdatingCurrent) -> Date? {
        var gregorian = Calendar(identifier: .gregorian)
        gregorian.timeZone = calendar.timeZone
        return gregorian.date(from: DateComponents(year: year, month: month, day: day))
    }

    public static func < (lhs: GregorianDay, rhs: GregorianDay) -> Bool {
        (lhs.year, lhs.month, lhs.day) < (rhs.year, rhs.month, rhs.day)
    }

    public var iso8601: String {
        String(format: "%04d-%02d-%02d", year, month, day)
    }
}

public enum IgnireCalendarError: Error, Equatable, LocalizedError {
    case invalidGregorianDate
    case unsupportedGregorianDate
    case unsupportedIgnireYear
    case invalidIgnireDate

    public var errorDescription: String? {
        switch self {
        case .invalidGregorianDate:
            return "無效的公曆日期。"
        case .unsupportedGregorianDate:
            return "公曆日期超出支援範圍。"
        case .unsupportedIgnireYear:
            return "新曆年份超出支援範圍。"
        case .invalidIgnireDate:
            return "無效的新曆日期。"
        }
    }
}

public struct IgnireYear: Equatable, Sendable {
    public let year: Int
    public let start: GregorianDay
    public let endExclusive: GregorianDay

    public var length: Int { start.days(until: endExclusive) }
    public var festivalDayCount: Int { length - IgnireCalendar.regularDaysPerYear }
    public var lastDay: GregorianDay { try! GregorianDay(dayNumber: endExclusive.dayNumber - 1) }
}

public struct IgnireDate: Equatable, Sendable {
    public let year: Int
    /// Months 1 through 12 are regular months; month 0 denotes a festival day.
    public let month: Int
    public let day: Int
    public let dayOfYear: Int

    public var isFestival: Bool { month == 0 }

    public var yearLabel: String {
        guard year < 1 else { return "\(year) 年" }
        let yearsBefore = 1 - year
        return yearsBefore == 1 ? "前一年" : "前\(yearsBefore)年"
    }

    public var displayText: String {
        if isFestival {
            return "新曆（\(yearLabel)）祭典第 \(day) 天"
        }
        return year >= 1
            ? "新曆 \(yearLabel) \(month)/\(day)"
            : "新曆（\(yearLabel)）\(month)/\(day)"
    }

    public var compactText: String {
        isFestival ? "祭典第 \(day) 天" : "\(month)/\(day)"
    }
}

/// Conversion engine shared by the app and its WidgetKit extension.
///
/// This mirrors `ignire_calendar/calendar.py`; `tests/test_swift_parity.py`
/// checks that both engines agree on every supported date.
public enum IgnireCalendar {
    public static let epochStart = try! GregorianDay(year: 2023, month: 8, day: 23)
    public static let epochYear = 1
    public static let monthsPerYear = 12
    public static let daysPerMonth = 30
    public static let regularDaysPerYear = monthsPerYear * daysPerMonth
    /// Only complete Ignire years whose first and last day lie in Gregorian 1–9999.
    public static let minimumIgnireYear = 1 - epochStart.year + epochYear  // -2021
    public static let maximumIgnireYear = 9_998 - epochStart.year + epochYear  // 7976
    public static let minimumGregorianDate = try! newYearStart(in: 1)
    public static let maximumGregorianDate = try! newYearStart(in: 9_999).adding(days: -1)

    public static func isLeapYear(_ year: Int) -> Bool {
        year.isMultiple(of: 400) || (year.isMultiple(of: 4) && !year.isMultiple(of: 100))
    }

    /// The New Year in Gregorian year Y is 8/23 when Y+1 is a leap year, or 8/22 otherwise.
    public static func newYearStart(in gregorianYear: Int) throws -> GregorianDay {
        guard (1...9_999).contains(gregorianYear) else {
            throw IgnireCalendarError.unsupportedGregorianDate
        }
        return try GregorianDay(
            year: gregorianYear,
            month: 8,
            day: isLeapYear(gregorianYear + 1) ? 23 : 22
        )
    }

    public static func year(_ ignireYear: Int) throws -> IgnireYear {
        guard (minimumIgnireYear...maximumIgnireYear).contains(ignireYear) else {
            throw IgnireCalendarError.unsupportedIgnireYear
        }
        let gregorianYear = epochStart.year + ignireYear - epochYear
        return IgnireYear(
            year: ignireYear,
            start: try newYearStart(in: gregorianYear),
            endExclusive: try newYearStart(in: gregorianYear + 1)
        )
    }

    public static func date(from gregorianDate: GregorianDay) throws -> IgnireDate {
        guard (minimumGregorianDate...maximumGregorianDate).contains(gregorianDate) else {
            throw IgnireCalendarError.unsupportedGregorianDate
        }

        var startYear = gregorianDate.year
        var start = try newYearStart(in: startYear)
        if gregorianDate < start {
            startYear -= 1
            start = try newYearStart(in: startYear)
        }

        let ignireYear = startYear - epochStart.year + epochYear
        let dayOfYear = start.days(until: gregorianDate) + 1
        if dayOfYear <= regularDaysPerYear {
            return IgnireDate(
                year: ignireYear,
                month: (dayOfYear - 1) / daysPerMonth + 1,
                day: (dayOfYear - 1) % daysPerMonth + 1,
                dayOfYear: dayOfYear
            )
        }
        return IgnireDate(
            year: ignireYear,
            month: 0,
            day: dayOfYear - regularDaysPerYear,
            dayOfYear: dayOfYear
        )
    }

    /// Converts an Ignire date to Gregorian. Use month 0 and day 1–5/6 for festival days.
    public static func gregorianDate(year: Int, month: Int, day: Int) throws -> GregorianDay {
        let ignireYear = try self.year(year)
        let offset: Int
        if month == 0 {
            guard (1...ignireYear.festivalDayCount).contains(day) else {
                throw IgnireCalendarError.invalidIgnireDate
            }
            offset = regularDaysPerYear + day - 1
        } else {
            guard (1...monthsPerYear).contains(month), (1...daysPerMonth).contains(day) else {
                throw IgnireCalendarError.invalidIgnireDate
            }
            offset = (month - 1) * daysPerMonth + day - 1
        }
        return try ignireYear.start.adding(days: offset)
    }
}
