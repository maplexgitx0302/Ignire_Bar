/*
 * Ignire calendar engine: twelve 30-day months plus five or six festival days.
 *
 * Rules
 * - Ignire year 1, month 1, day 1 is Gregorian 2023-08-23.
 * - The new year in Gregorian year Y is on 8/23 when Y+1 is a leap year, otherwise 8/22.
 * - Therefore Gregorian 3/1 is always 7/12 and 8/17 (聖日, the holy day) is always
 *   festival day 1. Festival days are not counted in the 360-day calendar.
 *
 * User-facing wording follows doctrine/火神信仰與祈禱手冊.md: 公元, 聖日, 祭典, 首日,
 * and days counted in 日.
 *
 * Dates are handled as integer day numbers (days since 1970-01-01), never as
 * JavaScript Date objects, so time zones and daylight saving cannot shift a day.
 * Gregorian dates are plain {year, month, day} objects (proleptic Gregorian).
 * Ignire dates use month 1-12 for regular days and month 0 for festival days.
 *
 * This file runs unchanged in browsers, in Node (tests), and inside the
 * Scriptable widget script, which embeds a copy of it (see scripts/build.mjs).
 */
const IgnireCalendar = (() => {
  "use strict";

  const MONTHS_PER_YEAR = 12;
  const DAYS_PER_MONTH = 30;
  const REGULAR_DAYS_PER_YEAR = MONTHS_PER_YEAR * DAYS_PER_MONTH;
  const EPOCH = Object.freeze({ year: 2023, month: 8, day: 23 });
  const EPOCH_YEAR = 1;
  // Only complete Ignire years whose first and last day fall in Gregorian years 1-9999.
  const MIN_YEAR = 1 - EPOCH.year + EPOCH_YEAR; // -2021
  const MAX_YEAR = 9998 - EPOCH.year + EPOCH_YEAR; // 7976
  const WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"];

  function isLeapYear(year) {
    return year % 400 === 0 || (year % 4 === 0 && year % 100 !== 0);
  }

  function daysInMonth(year, month) {
    if (month === 2) return isLeapYear(year) ? 29 : 28;
    return [4, 6, 9, 11].includes(month) ? 30 : 31;
  }

  function isValidGregorian(year, month, day) {
    return (
      Number.isInteger(year) && Number.isInteger(month) && Number.isInteger(day) &&
      year >= 1 && year <= 9999 && month >= 1 && month <= 12 &&
      day >= 1 && day <= daysInMonth(year, month)
    );
  }

  function requireGregorian(date) {
    if (!date || !isValidGregorian(date.year, date.month, date.day)) {
      throw new RangeError("無效的公元日期。");
    }
  }

  // Howard Hinnant's days_from_civil algorithm.
  function dayNumber(date) {
    requireGregorian(date);
    const year = date.month <= 2 ? date.year - 1 : date.year;
    const era = Math.floor(year / 400);
    const yearOfEra = year - era * 400;
    const dayOfYear = Math.floor((153 * ((date.month + 9) % 12) + 2) / 5) + date.day - 1;
    const dayOfEra =
      yearOfEra * 365 + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100) + dayOfYear;
    return era * 146097 + dayOfEra - 719468;
  }

  // Howard Hinnant's civil_from_days algorithm.
  function fromDayNumber(number) {
    if (!Number.isInteger(number)) throw new TypeError("day number must be an integer");
    const shifted = number + 719468;
    const era = Math.floor(shifted / 146097);
    const dayOfEra = shifted - era * 146097;
    const yearOfEra = Math.floor(
      (dayOfEra - Math.floor(dayOfEra / 1460) + Math.floor(dayOfEra / 36524) -
        Math.floor(dayOfEra / 146096)) / 365
    );
    const dayOfYear =
      dayOfEra - (365 * yearOfEra + Math.floor(yearOfEra / 4) - Math.floor(yearOfEra / 100));
    const shiftedMonth = Math.floor((5 * dayOfYear + 2) / 153);
    const day = dayOfYear - Math.floor((153 * shiftedMonth + 2) / 5) + 1;
    const month = shiftedMonth < 10 ? shiftedMonth + 3 : shiftedMonth - 9;
    const date = { year: yearOfEra + era * 400 + (month <= 2 ? 1 : 0), month, day };
    requireGregorian(date);
    return date;
  }

  function addDays(date, days) {
    return fromDayNumber(dayNumber(date) + days);
  }

  /** The Ignire new year that falls in a Gregorian year. */
  function newYearStart(gregorianYear) {
    if (!Number.isInteger(gregorianYear) || gregorianYear < 1 || gregorianYear > 9999) {
      throw new RangeError("公元年份超出支援範圍（1–9999）。");
    }
    return { year: gregorianYear, month: 8, day: isLeapYear(gregorianYear + 1) ? 23 : 22 };
  }

  const MIN_DATE = newYearStart(1);
  const MAX_DATE = addDays(newYearStart(9999), -1);
  const MIN_DAY_NUMBER = dayNumber(MIN_DATE);
  const MAX_DAY_NUMBER = dayNumber(MAX_DATE);

  /** Gregorian boundaries of one Ignire year. `end` is exclusive. */
  function yearInfo(year) {
    if (!Number.isInteger(year) || year < MIN_YEAR || year > MAX_YEAR) {
      throw new RangeError(`新曆年份必須介於 ${MIN_YEAR} 與 ${MAX_YEAR} 之間。`);
    }
    const gregorianYear = EPOCH.year + year - EPOCH_YEAR;
    const start = newYearStart(gregorianYear);
    const end = newYearStart(gregorianYear + 1);
    const length = dayNumber(end) - dayNumber(start);
    return { year, start, end, length, festivalDays: length - REGULAR_DAYS_PER_YEAR };
  }

  /** Convert a Gregorian {year, month, day} to an Ignire date. */
  function toIgnire(date) {
    const number = dayNumber(date);
    if (number < MIN_DAY_NUMBER || number > MAX_DAY_NUMBER) {
      throw new RangeError(
        `公元日期必須介於 ${formatISO(MIN_DATE)} 與 ${formatISO(MAX_DATE)} 之間。`
      );
    }
    let startYear = date.year;
    let start = dayNumber(newYearStart(startYear));
    if (number < start) {
      startYear -= 1;
      start = dayNumber(newYearStart(startYear));
    }
    const year = startYear - EPOCH.year + EPOCH_YEAR;
    const dayOfYear = number - start + 1;
    if (dayOfYear <= REGULAR_DAYS_PER_YEAR) {
      return {
        year,
        month: Math.floor((dayOfYear - 1) / DAYS_PER_MONTH) + 1,
        day: ((dayOfYear - 1) % DAYS_PER_MONTH) + 1,
        dayOfYear,
        isFestival: false,
      };
    }
    return { year, month: 0, day: dayOfYear - REGULAR_DAYS_PER_YEAR, dayOfYear, isFestival: true };
  }

  /** Convert an Ignire date to Gregorian. Use month 0 and day 1-5/6 for festival days. */
  function toGregorian(year, month, day) {
    const info = yearInfo(year);
    if (!Number.isInteger(month) || !Number.isInteger(day)) {
      throw new TypeError("月份與日期必須是整數。");
    }
    let offset;
    if (month === 0) {
      if (day < 1 || day > info.festivalDays) {
        throw new RangeError(`新曆 ${year} 年只有 ${info.festivalDays} 個祭典日。`);
      }
      offset = REGULAR_DAYS_PER_YEAR + day - 1;
    } else {
      if (month < 1 || month > MONTHS_PER_YEAR) {
        throw new RangeError("月份必須是 1–12，祭典請用 0。");
      }
      if (day < 1 || day > DAYS_PER_MONTH) throw new RangeError("每月只有 30 日。");
      offset = (month - 1) * DAYS_PER_MONTH + day - 1;
    }
    return addDays(info.start, offset);
  }

  /** Year label that never shows a year zero: 前一年, 前2年, ... */
  function yearLabel(year) {
    if (year >= 1) return `${year} 年`;
    const yearsBefore = 1 - year;
    return yearsBefore === 1 ? "前一年" : `前${yearsBefore}年`;
  }

  /** Festival day 1 is the holy day (聖日), Gregorian 8/17. */
  function isHolyDay(date) {
    return date.month === 0 && date.day === 1;
  }

  /** Full text, e.g. "新曆 4 年 2 月 17 日" or "新曆（4 年）祭典第 1 日". */
  function formatIgnire(date) {
    const label = yearLabel(date.year);
    if (date.month === 0) return `新曆（${label}）祭典第 ${date.day} 日`;
    return date.year >= 1
      ? `新曆 ${label} ${date.month} 月 ${date.day} 日`
      : `新曆（${label}）${date.month} 月 ${date.day} 日`;
  }

  /** Short text for widgets, e.g. "2/17" or "祭典第 1 日". */
  function compactText(date) {
    return date.month === 0 ? `祭典第 ${date.day} 日` : `${date.month}/${date.day}`;
  }

  function weekdayLabel(date) {
    // 1970-01-01 (day number 0) was a Thursday, index 3 when Monday is 0.
    return WEEKDAYS[(((dayNumber(date) + 3) % 7) + 7) % 7];
  }

  function formatISO(date) {
    return [
      String(date.year).padStart(4, "0"),
      String(date.month).padStart(2, "0"),
      String(date.day).padStart(2, "0"),
    ].join("-");
  }

  function parseISO(text) {
    const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(text).trim());
    if (!match) throw new RangeError("請輸入 YYYY-MM-DD 格式的日期。");
    const date = { year: Number(match[1]), month: Number(match[2]), day: Number(match[3]) };
    requireGregorian(date);
    return date;
  }

  /** The device's local calendar date for a JavaScript Date (default: now). */
  function today(now = new Date()) {
    return { year: now.getFullYear(), month: now.getMonth() + 1, day: now.getDate() };
  }

  return Object.freeze({
    MONTHS_PER_YEAR,
    DAYS_PER_MONTH,
    REGULAR_DAYS_PER_YEAR,
    EPOCH,
    MIN_YEAR,
    MAX_YEAR,
    MIN_DATE,
    MAX_DATE,
    isLeapYear,
    daysInMonth,
    isValidGregorian,
    dayNumber,
    fromDayNumber,
    addDays,
    newYearStart,
    yearInfo,
    toIgnire,
    toGregorian,
    yearLabel,
    isHolyDay,
    formatIgnire,
    compactText,
    weekdayLabel,
    formatISO,
    parseISO,
    today,
  });
})();

if (typeof module === "object" && module && module.exports) {
  module.exports = IgnireCalendar;
}
