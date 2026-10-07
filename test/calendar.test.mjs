import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { test } from "node:test";

const C = createRequire(import.meta.url)("../docs/ignire-calendar.js");
const g = (year, month, day) => ({ year, month, day });

// SHA-256 of "YYYY-MM-DD year month day dayOfYear\n" for every supported date,
// produced by the original Python engine before it was retired (v0.3.0, commit d56e689).
const PYTHON_ENGINE_SHA256 = "bc59ef37967a64d7189f6846ef59ffa63aff8aca880f26990f2d12c12c6e68fa";

test("matches the retired Python engine and round-trips on every supported date", () => {
  const hash = createHash("sha256");
  let lines = [];
  let count = 0;
  for (let n = C.dayNumber(C.MIN_DATE); n <= C.dayNumber(C.MAX_DATE); n++) {
    const date = C.fromDayNumber(n);
    const r = C.toIgnire(date);
    assert.equal(C.dayNumber(C.toGregorian(r.year, r.month, r.day)), n);
    lines.push(`${C.formatISO(date)} ${r.year} ${r.month} ${r.day} ${r.dayOfYear}\n`);
    if (lines.length === 10000) {
      hash.update(lines.join(""));
      lines = [];
    }
    count++;
  }
  hash.update(lines.join(""));
  assert.equal(count, 3651695);
  assert.equal(hash.digest("hex"), PYTHON_ENGINE_SHA256);
});

test("hand-computed reference dates", () => {
  const cases = [
    // [Gregorian, Ignire year, month, day, day of year]
    [g(2023, 8, 22), 0, 0, 6, 366], // 前一年 ends with six festival days
    [g(2023, 8, 23), 1, 1, 1, 1], // epoch
    [g(2023, 9, 21), 1, 1, 30, 30],
    [g(2023, 9, 22), 1, 2, 1, 31],
    [g(2024, 2, 29), 1, 7, 11, 191],
    [g(2024, 3, 1), 1, 7, 12, 192],
    [g(2024, 8, 16), 1, 12, 30, 360],
    [g(2024, 8, 17), 1, 0, 1, 361],
    [g(2024, 8, 21), 1, 0, 5, 365], // 2025 is not leap: five festival days
    [g(2024, 8, 22), 2, 1, 1, 1],
    [g(2026, 10, 7), 4, 2, 17, 47],
    [g(2027, 8, 22), 4, 0, 6, 366],
    [g(2027, 8, 23), 5, 1, 1, 1],
    [g(2099, 8, 22), 77, 1, 1, 1], // 2100 is not a leap year
    [g(2399, 8, 23), 377, 1, 1, 1], // 2400 is a leap year
  ];
  for (const [date, year, month, day, dayOfYear] of cases) {
    const r = C.toIgnire(date);
    assert.deepEqual([r.year, r.month, r.day, r.dayOfYear], [year, month, day, dayOfYear], C.formatISO(date));
    assert.deepEqual(C.toGregorian(year, month, day), date);
  }
});

test("year boundaries match a naive year-by-year walk", () => {
  const leap = (y) => (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0;
  let start = C.dayNumber(g(1, 8, 22)); // 0002 is not leap
  for (let year = C.MIN_YEAR; year <= C.MAX_YEAR; year++) {
    const gregorianYear = C.fromDayNumber(start).year + 1;
    const end = C.dayNumber(g(gregorianYear, 8, leap(gregorianYear + 1) ? 23 : 22));
    const info = C.yearInfo(year);
    assert.equal(C.dayNumber(info.start), start, `year ${year}`);
    assert.equal(info.length, end - start);
    assert.ok(info.festivalDays === 5 || info.festivalDays === 6);
    assert.equal(C.toIgnire(C.fromDayNumber(start)).dayOfYear, 1);
    assert.deepEqual(C.toIgnire(C.fromDayNumber(end - 1)), {
      year, month: 0, day: info.festivalDays, dayOfYear: info.length, isFestival: true,
    });
    start = end;
  }
  assert.equal(start - 1, C.dayNumber(C.MAX_DATE));
});

test("fixed alignments hold in every supported Gregorian year", () => {
  for (let year = 2; year <= 9998; year++) {
    const at = (month, day) => {
      const r = C.toIgnire(g(year, month, day));
      return [r.month, r.day];
    };
    const nextLeap = C.isLeapYear(year + 1);
    assert.deepEqual(at(3, 1), [7, 12], `${year}-03-01`);
    assert.deepEqual(at(8, 17), [0, 1], `${year}-08-17`);
    assert.deepEqual(at(8, 22), nextLeap ? [0, 6] : [1, 1], `${year}-08-22`);
    assert.deepEqual(at(8, 23), nextLeap ? [1, 1] : [1, 2], `${year}-08-23`);
    assert.deepEqual(at(2, 28), C.isLeapYear(year) ? [7, 10] : [7, 11], `${year}-02-28`);
    if (C.isLeapYear(year)) assert.deepEqual(at(2, 29), [7, 11], `${year}-02-29`);
  }
});

test("labels and formatting", () => {
  assert.equal(C.yearLabel(1), "1 年");
  assert.equal(C.yearLabel(0), "前一年");
  assert.equal(C.yearLabel(-1), "前2年");
  assert.equal(C.formatIgnire(C.toIgnire(g(2026, 10, 7))), "新曆 4 年 2/17");
  assert.equal(C.formatIgnire(C.toIgnire(g(2023, 8, 22))), "新曆（前一年）祭典第 6 天");
  assert.equal(C.formatIgnire(C.toIgnire(g(2021, 9, 1))), "新曆（前2年）1/11");
  assert.equal(C.formatIgnire(C.toIgnire(g(2024, 8, 17))), "新曆（1 年）祭典第 1 天");
  assert.equal(C.compactText(C.toIgnire(g(2024, 8, 17))), "祭典第 1 天");
  assert.equal(C.weekdayLabel(g(1970, 1, 1)), "星期四");
  assert.equal(C.weekdayLabel(g(2026, 10, 7)), "星期三");
  assert.equal(C.weekdayLabel(g(1, 1, 1)), "星期一");
  assert.equal(C.formatISO(g(1, 8, 22)), "0001-08-22");
  assert.deepEqual(C.parseISO(" 2024-02-29 "), g(2024, 2, 29));
});

test("today() uses the device's local calendar date", () => {
  assert.deepEqual(C.today(new Date(2026, 9, 7, 0, 0, 1)), g(2026, 10, 7));
  assert.deepEqual(C.today(new Date(2026, 9, 7, 23, 59, 59)), g(2026, 10, 7));
});

test("invalid input is rejected", () => {
  for (const [year, month, day] of [[1, -1, 1], [1, 13, 1], [1, 1, 0], [1, 1, 31], [1, 1.5, 1]]) {
    assert.throws(() => C.toGregorian(year, month, day), `${year}/${month}/${day}`);
  }
  const fiveDayYear = [1, 2, 3, 4, 5].find((y) => C.yearInfo(y).festivalDays === 5);
  assert.throws(() => C.toGregorian(fiveDayYear, 0, 6), RangeError);
  assert.throws(() => C.yearInfo(C.MIN_YEAR - 1), RangeError);
  assert.throws(() => C.yearInfo(C.MAX_YEAR + 1), RangeError);
  assert.throws(() => C.toIgnire(C.addDays(C.MIN_DATE, -1)), RangeError);
  assert.throws(() => C.toIgnire(C.addDays(C.MAX_DATE, 1)), RangeError);
  assert.throws(() => C.toIgnire(g(2023, 2, 29)), RangeError);
  assert.throws(() => C.parseISO("2023/08/23"), RangeError);
  assert.throws(() => C.parseISO("2023-02-30"), RangeError);
  assert.throws(() => C.fromDayNumber(C.dayNumber(g(9999, 12, 31)) + 1), RangeError);
});
