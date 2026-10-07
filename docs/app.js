/* Page logic for the Ignire calendar. The calendar rules live in ignire-calendar.js. */
(() => {
  "use strict";

  const C = IgnireCalendar;
  const $ = (id) => document.getElementById(id);

  let today = C.today();

  function monthName(month) {
    return month === 0 ? "祭典" : `${month} 月`;
  }

  function headline(ignire) {
    return ignire.isFestival ? `祭典第 ${ignire.day} 天` : `${ignire.month} 月 ${ignire.day} 日`;
  }

  function gregorianText(date) {
    return `${C.formatISO(date)}（${C.weekdayLabel(date)}）`;
  }

  function clampYear(value, fallback) {
    const year = Number.parseInt(value, 10);
    if (!Number.isFinite(year)) return fallback;
    return Math.min(Math.max(year, 1), C.MAX_YEAR);
  }

  function fillSelect(select, values, label, selected) {
    select.replaceChildren(
      ...values.map((value) => new Option(label(value), String(value), false, value === selected))
    );
  }

  function showResult(element, main, detail, isError = false) {
    element.classList.toggle("error", isError);
    element.textContent = main;
    if (detail) {
      const small = document.createElement("small");
      small.textContent = detail;
      element.append(small);
    }
  }

  const MONTH_VALUES = [...Array(C.MONTHS_PER_YEAR).keys()].map((i) => i + 1).concat(0);

  // ---------- Today ----------
  function renderToday() {
    const ignire = C.toIgnire(today);
    const info = C.yearInfo(ignire.year);
    $("today-date").textContent = headline(ignire);
    $("today-year").textContent = `新曆 ${C.yearLabel(ignire.year)} · 序日 ${ignire.dayOfYear}`;
    $("today-gregorian").textContent = `公曆 ${gregorianText(today)}`;

    const percent = Math.round((ignire.dayOfYear / info.length) * 100);
    $("today-progress").setAttribute("aria-valuenow", String(percent));
    $("today-progress-bar").style.width = `${percent}%`;

    const daysToNewYear = C.dayNumber(info.end) - C.dayNumber(today);
    if (ignire.isFestival) {
      $("today-countdown").textContent =
        `祭典進行中（共 ${info.festivalDays} 天），${daysToNewYear} 天後迎來新曆 ${C.yearLabel(ignire.year + 1)}。`;
    } else {
      const festivalStart = C.toGregorian(ignire.year, 0, 1);
      const days = C.dayNumber(festivalStart) - C.dayNumber(today);
      $("today-countdown").textContent =
        `距離祭典還有 ${days} 天（${C.formatISO(festivalStart)} 起，共 ${info.festivalDays} 天）。`;
    }

    // Widget preview mirrors the Scriptable widget layouts.
    $("preview-inline").textContent = `🔥 新曆 ${C.yearLabel(ignire.year)} ${C.compactText(ignire)}`;
    $("preview-circular-top").textContent = ignire.isFestival ? "祭典" : `${ignire.month}月`;
    $("preview-circular-day").textContent = String(ignire.day);
    $("preview-rect-date").textContent = C.compactText(ignire);
    $("preview-rect-year").textContent = `新曆 ${C.yearLabel(ignire.year)} · 序日 ${ignire.dayOfYear}`;
  }

  // ---------- Gregorian → Ignire ----------
  const g2iDate = $("g2i-date");
  g2iDate.min = C.formatISO(C.MIN_DATE);
  g2iDate.max = C.formatISO(C.MAX_DATE);
  g2iDate.value = C.formatISO(today);

  function renderGregorianToIgnire() {
    const output = $("g2i-result");
    if (!g2iDate.value) {
      showResult(output, "請選擇日期。", null, true);
      return;
    }
    try {
      const date = C.parseISO(g2iDate.value);
      const ignire = C.toIgnire(date);
      const info = C.yearInfo(ignire.year);
      showResult(
        output,
        C.formatIgnire(ignire),
        `${C.weekdayLabel(date)} · 序日 ${ignire.dayOfYear} · 該年共 ${info.length} 天、${info.festivalDays} 個祭典日`
      );
    } catch (error) {
      showResult(output, error.message, null, true);
    }
  }

  // ---------- Ignire → Gregorian ----------
  const i2gYear = $("i2g-year");
  const i2gMonth = $("i2g-month");
  const i2gDay = $("i2g-day");
  i2gYear.max = String(C.MAX_YEAR);

  function fillDays(select, year, month, selected) {
    const count = month === 0 ? C.yearInfo(year).festivalDays : C.DAYS_PER_MONTH;
    const days = [...Array(count).keys()].map((i) => i + 1);
    fillSelect(select, days, String, Math.min(selected, count));
  }

  function renderIgnireToGregorian() {
    const year = clampYear(i2gYear.value, 1);
    const month = Number(i2gMonth.value);
    fillDays(i2gDay, year, month, Number(i2gDay.value) || 1);
    const day = Number(i2gDay.value);
    const output = $("i2g-result");
    try {
      const date = C.toGregorian(year, month, day);
      const source = month === 0 ? `祭典第 ${day} 天` : `${month}/${day}`;
      showResult(output, `公曆 ${gregorianText(date)}`, `新曆 ${year} 年 ${source}`);
    } catch (error) {
      showResult(output, error.message, null, true);
    }
  }

  // ---------- Month view ----------
  const monthYear = $("month-year");
  const monthMonth = $("month-month");
  monthYear.max = String(C.MAX_YEAR);
  fillSelect(monthMonth, MONTH_VALUES, monthName, 1);

  function setMonth(year, month) {
    monthYear.value = String(year);
    monthMonth.value = String(month);
    renderMonth();
  }

  function stepMonth(delta) {
    const year = clampYear(monthYear.value, 1);
    const position = MONTH_VALUES.indexOf(Number(monthMonth.value)) + delta;
    const nextYear = year + Math.floor(position / MONTH_VALUES.length);
    if (nextYear < 1 || nextYear > C.MAX_YEAR) return;
    setMonth(nextYear, MONTH_VALUES[(position + MONTH_VALUES.length) % MONTH_VALUES.length]);
  }

  function renderMonth() {
    const year = clampYear(monthYear.value, 1);
    const month = Number(monthMonth.value);
    const info = C.yearInfo(year);
    const length = month === 0 ? info.festivalDays : C.DAYS_PER_MONTH;
    const first = C.toGregorian(year, month, 1);
    const last = C.addDays(first, length - 1);
    const todayNumber = C.dayNumber(today);
    $("month-title").textContent = `新曆 ${year} 年 ${monthName(month)}`;
    $("month-caption").textContent = `公曆 ${C.formatISO(first)} 至 ${C.formatISO(last)}`;
    $("month-prev").disabled = year === 1 && month === 1;
    $("month-next").disabled = year === C.MAX_YEAR && month === 0;

    const cells = [];
    for (let index = 0; index < length; index++) {
      const date = C.addDays(first, index);
      const cell = document.createElement("li");
      if (month === 0) cell.classList.add("festival");
      if (C.dayNumber(date) === todayNumber) {
        cell.classList.add("is-today");
        cell.setAttribute("aria-current", "date");
      }
      const num = document.createElement("span");
      num.className = "num";
      num.textContent = String(index + 1);
      const greg = document.createElement("span");
      greg.className = "greg";
      greg.textContent = `${date.month}/${date.day} ${C.weekdayLabel(date).slice(-1)}`;
      cell.title = gregorianText(date);
      cell.append(num, greg);
      cells.push(cell);
    }
    $("month-grid").replaceChildren(...cells);
  }

  function showTodayMonth() {
    const ignire = C.toIgnire(today);
    if (ignire.year >= 1) setMonth(ignire.year, ignire.month);
    else setMonth(1, 1);
  }

  // ---------- Tools ----------
  const EXPECTED_ALIGNMENTS = (year, month, day) => {
    if (month === 3 && day === 1) return [7, 12];
    if (month === 8 && day === 17) return [0, 1];
    if (month === 8 && day === 22) return C.isLeapYear(year + 1) ? [0, 6] : [1, 1];
    if (month === 8 && day === 23) return C.isLeapYear(year + 1) ? [1, 1] : [1, 2];
    if (month === 2 && day === 29) return [7, 11];
    return C.isLeapYear(year) ? [7, 10] : [7, 11]; // 2/28
  };

  function runVerification() {
    const output = $("verify-result");
    const from = Number.parseInt($("verify-from").value, 10);
    const to = Number.parseInt($("verify-to").value, 10);
    if (!(from >= 2 && to <= 9998 && from <= to)) {
      showResult(output, "年份需介於 2–9998，且起始年不可晚於結束年。", null, true);
      return;
    }
    let checks = 0;
    const failures = [];
    for (let year = from; year <= to; year++) {
      const days = [[2, C.isLeapYear(year) ? 29 : 28], [3, 1], [8, 17], [8, 22], [8, 23]];
      for (const [month, day] of days) {
        const date = { year, month, day };
        const actual = C.toIgnire(date);
        const [expectedMonth, expectedDay] = EXPECTED_ALIGNMENTS(year, month, day);
        checks++;
        if (actual.month !== expectedMonth || actual.day !== expectedDay) {
          failures.push(`${C.formatISO(date)} → ${C.compactText(actual)}`);
        }
      }
    }
    output.classList.toggle("ok", failures.length === 0);
    if (failures.length === 0) {
      showResult(output, `✅ 全部 ${checks} 項規則驗證通過（公曆 ${from}–${to} 年）。`);
    } else {
      showResult(output, `❌ ${failures.length} 項不符`, failures.slice(0, 20).join("、"), true);
    }
  }

  function csvRows(year) {
    const info = C.yearInfo(year);
    const rows = [["新曆年", "新曆月", "新曆日", "新曆序日", "是否祭典", "公曆日期", "星期"]];
    for (let offset = 0; offset < info.length; offset++) {
      const date = C.addDays(info.start, offset);
      const ignire = C.toIgnire(date);
      rows.push([
        year,
        ignire.isFestival ? "祭典" : ignire.month,
        ignire.day,
        ignire.dayOfYear,
        ignire.isFestival ? "是" : "否",
        C.formatISO(date),
        C.weekdayLabel(date),
      ]);
    }
    return rows;
  }

  function renderExportCaption() {
    const year = clampYear($("export-year").value, 1);
    const info = C.yearInfo(year);
    $("export-caption").textContent =
      `新曆 ${year} 年：公曆 ${C.formatISO(info.start)} 起，共 ${info.length} 天，其中 ${info.festivalDays} 天為祭典。`;
  }

  function downloadYearCsv() {
    const year = clampYear($("export-year").value, 1);
    const csv = "﻿" + csvRows(year).map((row) => row.join(",")).join("\r\n") + "\r\n";
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8" }));
    const link = Object.assign(document.createElement("a"), {
      href: url,
      download: `ignire-calendar-year-${year}.csv`,
    });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  // ---------- Scriptable script copy ----------
  // scriptable/source.js defines the script text, so copying also works when the
  // page is opened from disk (file://), where fetch() is blocked.
  const scriptText = window.IgnireScriptableSource;
  if (scriptText) {
    $("copy-script").disabled = false;
  } else {
    $("copy-status").textContent = "無法載入腳本，請改用「下載腳本」。";
  }

  async function copyScript() {
    const status = $("copy-status");
    try {
      await navigator.clipboard.writeText(scriptText);
    } catch {
      // Older browsers: fall back to a temporary selection.
      const area = Object.assign(document.createElement("textarea"), { value: scriptText });
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.append(area);
      area.select();
      const copied = document.execCommand("copy");
      area.remove();
      if (!copied) {
        status.textContent = "複製失敗，請改用「下載腳本」。";
        return;
      }
    }
    status.textContent = "已複製！到 Scriptable 新增腳本並貼上。";
  }

  // ---------- Wiring ----------
  function init() {
    const ignire = C.toIgnire(today);
    i2gYear.value = String(Math.max(ignire.year, 1));
    fillSelect(i2gMonth, MONTH_VALUES, monthName, ignire.year >= 1 ? ignire.month : 1);
    fillDays(i2gDay, Math.max(ignire.year, 1), Number(i2gMonth.value), ignire.year >= 1 ? ignire.day : 1);
    $("export-year").value = String(Math.max(ignire.year, 1));
    $("export-year").max = String(C.MAX_YEAR);

    renderToday();
    renderGregorianToIgnire();
    renderIgnireToGregorian();
    showTodayMonth();
    renderExportCaption();
  }

  g2iDate.addEventListener("input", renderGregorianToIgnire);
  i2gYear.addEventListener("input", renderIgnireToGregorian);
  i2gMonth.addEventListener("change", renderIgnireToGregorian);
  i2gDay.addEventListener("change", renderIgnireToGregorian);
  monthYear.addEventListener("input", renderMonth);
  monthMonth.addEventListener("change", renderMonth);
  $("month-prev").addEventListener("click", () => stepMonth(-1));
  $("month-next").addEventListener("click", () => stepMonth(1));
  $("month-today").addEventListener("click", showTodayMonth);
  $("verify-run").addEventListener("click", runVerification);
  $("export-year").addEventListener("input", renderExportCaption);
  $("export-run").addEventListener("click", downloadYearCsv);
  $("copy-script").addEventListener("click", copyScript);

  // Roll over to the new day if the page stays open past midnight.
  function refreshIfDayChanged() {
    const now = C.today();
    if (C.dayNumber(now) !== C.dayNumber(today)) {
      today = now;
      renderToday();
      renderMonth();
    }
  }
  document.addEventListener("visibilitychange", refreshIfDayChanged);
  setInterval(refreshIfDayChanged, 60 * 1000);

  init();
})();
