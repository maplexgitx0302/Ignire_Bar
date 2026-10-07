import SwiftUI
import WidgetKit

private struct IgnireCalendarEntry: TimelineEntry {
    let date: Date
    let gregorianDate: GregorianDay
    let ignireDate: IgnireDate
}

private struct IgnireCalendarTimelineProvider: TimelineProvider {
    /// Days of entries supplied per timeline, so the widget keeps advancing at
    /// midnight even when WidgetKit postpones the next reload.
    private static let daysPerTimeline = 7

    func placeholder(in context: Context) -> IgnireCalendarEntry {
        entry(for: IgnireCalendar.epochStart, at: .now)
    }

    func getSnapshot(in context: Context, completion: @escaping (IgnireCalendarEntry) -> Void) {
        completion(entry(for: .today, at: .now))
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<IgnireCalendarEntry>) -> Void) {
        let now = Date()
        let calendar = Calendar.autoupdatingCurrent
        let today = GregorianDay.today
        var entries = [entry(for: today, at: now)]
        for offset in 1..<Self.daysPerTimeline {
            guard let day = try? today.adding(days: offset),
                  let midnight = day.startDate(in: calendar),
                  (try? IgnireCalendar.date(from: day)) != nil else { break }
            entries.append(entry(for: day, at: midnight))
        }
        let reload = calendar.date(byAdding: .day, value: 1, to: entries.last!.date)
            ?? now.addingTimeInterval(24 * 60 * 60)
        completion(Timeline(entries: entries, policy: .after(reload)))
    }

    private func entry(for gregorianDate: GregorianDay, at date: Date) -> IgnireCalendarEntry {
        IgnireCalendarEntry(
            date: date,
            gregorianDate: gregorianDate,
            // The device clock is always inside the supported range (0001–9999).
            ignireDate: try! IgnireCalendar.date(from: gregorianDate)
        )
    }
}

private struct IgnireCalendarWidgetView: View {
    @Environment(\.widgetFamily) private var family
    let entry: IgnireCalendarEntry

    var body: some View {
        content.widgetBackground {
            if family == .accessoryCircular {
                AccessoryWidgetBackground()
            } else {
                Color.clear
            }
        }
    }

    @ViewBuilder
    private var content: some View {
        switch family {
        case .accessoryInline:
            Text("新曆 \(entry.ignireDate.yearLabel) \(entry.ignireDate.compactText)")
        case .accessoryCircular:
            VStack(spacing: 1) {
                Text(entry.ignireDate.isFestival ? "祭典" : "\(entry.ignireDate.month)月")
                    .font(.caption2)
                Text("\(entry.ignireDate.day)")
                    .font(.title2.bold())
            }
            .widgetAccentable()
        default:
            VStack(alignment: .leading, spacing: 3) {
                Text("今日新曆")
                    .font(.caption)
                Text(entry.ignireDate.isFestival ? "祭典第 \(entry.ignireDate.day) 天" : entry.ignireDate.compactText)
                    .font(.title2.bold())
                Text("新曆 \(entry.ignireDate.yearLabel) · 序日 \(entry.ignireDate.dayOfYear)")
                    .font(.caption2)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .widgetAccentable()
        }
    }
}

private extension View {
    /// iOS 17+ shows an error placeholder for widgets without a container background.
    @ViewBuilder
    func widgetBackground<Background: View>(@ViewBuilder _ background: () -> Background) -> some View {
        if #available(iOSApplicationExtension 17.0, *) {
            containerBackground(for: .widget, content: background)
        } else {
            self.background(background())
        }
    }
}

struct IgnireCalendarWidget: Widget {
    static let kind = "IgnireCalendarWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: Self.kind, provider: IgnireCalendarTimelineProvider()) { entry in
            IgnireCalendarWidgetView(entry: entry)
                .widgetURL(URL(string: "ignirecalendar://today"))
                .accessibilityLabel(entry.ignireDate.displayText)
        }
        .configurationDisplayName("今日新曆")
        .description("在鎖定畫面顯示今天的 Ignire 新曆日期。")
        .supportedFamilies([.accessoryInline, .accessoryCircular, .accessoryRectangular])
    }
}

@main
struct IgnireCalendarWidgetBundle: WidgetBundle {
    var body: some Widget {
        IgnireCalendarWidget()
    }
}
