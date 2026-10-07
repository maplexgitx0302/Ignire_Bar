// Prints every supported Gregorian date with its Ignire conversion so that
// tests/test_swift_parity.py can compare this engine with the Python one.
//
// Build: swiftc -O ios/IgnireCalendar/IgnireCalendarCore.swift ios/ParityTool/main.swift
// Output: one "YYYY-MM-DD year month day dayOfYear" line per day.

import Foundation

var output = ""
output.reserveCapacity(1 << 16)
var day = IgnireCalendar.minimumGregorianDate
while true {
    let converted = try IgnireCalendar.date(from: day)
    let roundTrip = try IgnireCalendar.gregorianDate(
        year: converted.year, month: converted.month, day: converted.day
    )
    guard roundTrip == day else {
        FileHandle.standardError.write("round trip failed for \(day.iso8601)\n".data(using: .utf8)!)
        exit(1)
    }
    output += "\(day.iso8601) \(converted.year) \(converted.month) \(converted.day) \(converted.dayOfYear)\n"
    if output.utf8.count >= 1 << 16 {
        FileHandle.standardOutput.write(output.data(using: .utf8)!)
        output.removeAll(keepingCapacity: true)
    }
    if day == IgnireCalendar.maximumGregorianDate { break }
    day = try day.adding(days: 1)
}
FileHandle.standardOutput.write(output.data(using: .utf8)!)
