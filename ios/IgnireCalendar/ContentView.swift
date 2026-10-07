import SwiftUI

struct ContentView: View {
    @Environment(\.scenePhase) private var scenePhase
    @State private var today = GregorianDay.today
    @State private var pickedDate = Date()
    @State private var ignireYear = 1
    @State private var ignireMonth = 1  // 0 = festival
    @State private var ignireDay = 1
    @State private var didSelectToday = false

    var body: some View {
        NavigationStack {
            Form {
                todaySection
                gregorianToIgnireSection
                ignireToGregorianSection
            }
            .navigationTitle("Ignire Calendar")
        }
        .onAppear {
            refreshToday()
            selectTodayInIgnirePickers()
        }
        .onChange(of: scenePhase) { phase in
            if phase == .active { refreshToday() }
        }
        .onReceive(NotificationCenter.default.publisher(for: .NSCalendarDayChanged)) { _ in
            refreshToday()
        }
    }

    // MARK: - Sections

    private var todaySection: some View {
        let ignireDate = try? IgnireCalendar.date(from: today)
        return Section {
            if let ignireDate {
                VStack(spacing: 8) {
                    Image(systemName: "flame.fill")
                        .font(.system(size: 40))
                        .foregroundStyle(.orange)
                    Text(ignireDate.isFestival ? "祭典第 \(ignireDate.day) 天" : ignireDate.compactText)
                        .font(.system(size: 44, weight: .bold, design: .rounded))
                    Text("新曆 \(ignireDate.yearLabel) · 序日 \(ignireDate.dayOfYear)")
                        .font(.title3)
                    Text("公曆 \(today.iso8601)")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 8)
            }
        } header: {
            Text("今日新曆")
        }
    }

    private var gregorianToIgnireSection: some View {
        Section("公曆 → 新曆") {
            DatePicker(
                "公曆日期",
                selection: $pickedDate,
                in: supportedDateRange,
                displayedComponents: .date
            )
            .environment(\.calendar, Calendar(identifier: .gregorian))
            resultRow(
                Result {
                    try IgnireCalendar.date(from: GregorianDay(pickedDate)).displayText
                }
            )
        }
    }

    private var ignireToGregorianSection: some View {
        let festivalDays = (try? IgnireCalendar.year(ignireYear).festivalDayCount) ?? 5
        let maxDay = ignireMonth == 0 ? festivalDays : IgnireCalendar.daysPerMonth
        return Section("新曆 → 公曆") {
            Stepper("新曆 \(ignireYear) 年", value: $ignireYear, in: 1...IgnireCalendar.maximumIgnireYear)
            Picker("月份", selection: $ignireMonth) {
                ForEach(1...IgnireCalendar.monthsPerYear, id: \.self) { Text("\($0) 月").tag($0) }
                Text("祭典").tag(0)
            }
            Picker(ignireMonth == 0 ? "祭典日" : "日", selection: $ignireDay) {
                ForEach(1...maxDay, id: \.self) { Text("\($0)").tag($0) }
            }
            resultRow(
                Result {
                    "公曆 " + (try IgnireCalendar.gregorianDate(
                        year: ignireYear, month: ignireMonth, day: ignireDay
                    ).iso8601)
                }
            )
        }
        .onChange(of: maxDay) { newMax in
            ignireDay = min(ignireDay, newMax)
        }
    }

    // MARK: - Helpers

    private var supportedDateRange: ClosedRange<Date> {
        let lower = IgnireCalendar.minimumGregorianDate.startDate() ?? .distantPast
        let upper = IgnireCalendar.maximumGregorianDate.startDate() ?? .distantFuture
        return lower...upper
    }

    private func resultRow(_ result: Result<String, Error>) -> Text {
        switch result {
        case .success(let text):
            return Text(text).font(.headline)
        case .failure(let error):
            return Text(error.localizedDescription).font(.headline).foregroundColor(.red)
        }
    }

    private func refreshToday() {
        today = GregorianDay.today
    }

    private func selectTodayInIgnirePickers() {
        guard !didSelectToday, let current = try? IgnireCalendar.date(from: today) else { return }
        didSelectToday = true
        ignireYear = max(current.year, 1)
        ignireMonth = current.month
        ignireDay = current.day
    }
}
