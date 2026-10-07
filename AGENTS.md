# Repository guide for coding agents

## Purpose

Ignire Calendar converts between the proleptic Gregorian calendar and a custom
calendar of twelve 30-day months plus five or six year-end festival days. The
Streamlit UI is in Traditional Chinese.

## Non-negotiable calendar invariants

- Ignire year 1, month 1, day 1 is Gregorian `2023-08-23`.
- A new year occurring in Gregorian year `Y` starts on August 23 when `Y + 1`
  is a leap year, and August 22 otherwise.
- Gregorian March 1 is always Ignire month 7, day 12.
- Gregorian August 17 is always festival day 1.
- Regular months are numbered 1–12 and contain exactly 30 days.
- Festival dates use month `0` in the Python API and day 1–5 or 1–6.
- User-facing labels never call the year before year 1 “year 0”; they use
  `前一年`, `前2年`, and so on.

If a requested change appears to contradict an invariant, confirm the calendar
rule with the user before changing the engine.

## Project map

- `ignire_calendar/calendar.py`: pure, dependency-free domain logic.
- `ignire_calendar/verification.py`: canonical alignment checks.
- `ignire_calendar/app.py`: Streamlit presentation only.
- `calendar_app.py`: stable Streamlit entry point.
- `tests/`: unit, boundary, invariant, and round-trip tests.
- `ios/`: standalone SwiftUI iPhone app and its WidgetKit extension.
- `ios/ParityTool/`: macOS CLI that dumps every Swift conversion for parity tests.

Do not put conversion logic in Streamlit callbacks. Add it to the domain module,
export public APIs from `ignire_calendar/__init__.py`, and test it directly.

The iOS target deliberately has a matching pure Swift conversion engine in
`ios/IgnireCalendar/IgnireCalendarCore.swift`; it is compiled into both the app
and widget extension. Any calendar-rule change must be mirrored in both engines
and tested on both sides; `IGNIRE_SWIFT_PARITY=1 pytest tests/test_swift_parity.py`
proves the two engines agree on every supported date. The Swift engine uses
integer day numbers, not `Foundation.Calendar`, for all calendar arithmetic.

## Development commands

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
./run.sh
```

Swift engine parity and iOS tests (full Xcode required):

```bash
IGNIRE_SWIFT_PARITY=1 pytest tests/test_swift_parity.py
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcodebuild \
  -project ios/IgnireCalendar.xcodeproj -scheme IgnireCalendar \
  -destination 'platform=iOS Simulator,name=iPhone 16' test
```

The standard-library-only fallback test command is:

```bash
python -m unittest discover -v
```

## Completion checklist

- Preserve all calendar invariants and cover new behavior with tests.
- Test both conversion directions and boundary/error behavior.
- Run Ruff and the complete test suite when the development dependencies exist.
- Keep local paths, secrets, generated CSV files, and caches out of version control.
- Update `README.md` and this file when commands or architecture change.
