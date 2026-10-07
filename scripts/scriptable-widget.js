// 火與焰新曆 — Scriptable widget
//
// Shows today's date in the 火與焰 calendar on the Lock Screen (inline,
// circular, rectangular) or the Home Screen (small, medium). Paste this whole
// file into a new script in the Scriptable app, then add a Scriptable widget
// and choose this script.
//
// 火焰是淨化，火焰是祝福，火焰是重生。
//
// Generated from scripts/scriptable-widget.js by scripts/build.mjs.
// Edit those sources, not docs/scriptable/IgnireCalendar.js.

/*@@IGNIRE_CORE@@*/

const GOLD = new Color("#D9B15C");
const SOOT = new Color("#14100D");
const EMBER = new Color("#FFB27A");
const ASH = new Color("#BBA68C");
const WEB_URL = "@@WEB_URL@@";

function nextLocalMidnight(now) {
  const midnight = new Date(now);
  midnight.setHours(24, 0, 30, 0);
  return midnight;
}

function addText(container, text, font, { color, center = false, minimumScaleFactor } = {}) {
  const element = container.addText(text);
  element.font = font;
  if (color) element.textColor = color;
  if (center) element.centerAlignText();
  element.lineLimit = 1;
  if (minimumScaleFactor) element.minimumScaleFactor = minimumScaleFactor;
  return element;
}

// Wording follows 《火神信仰與祈禱手冊》: 聖日 is festival day 1, festival days are
// not counted in the calendar, and the fire pillar burns throughout the festival.
function describe(ignire) {
  const year = `新曆 ${IgnireCalendar.yearLabel(ignire.year)}`;
  const date = IgnireCalendar.compactText(ignire);
  if (IgnireCalendar.isHolyDay(ignire)) {
    return { inline: "🔥 聖日 · 祭典第 1 日", circularTop: "聖日", title: "聖日", date, detail: "點燃火柱", year };
  }
  if (ignire.isFestival) {
    return { inline: `🔥 ${date}`, circularTop: "祭典", title: "火柱長燃", date, detail: `${year}祭典`, year };
  }
  return {
    inline: `🔥 ${year} ${date}`,
    circularTop: `${ignire.month}月`,
    title: "今日新曆",
    date,
    detail: `${year} · 第 ${ignire.dayOfYear} 日`,
    year,
  };
}

function buildWidget(family, now) {
  const gregorian = IgnireCalendar.today(now);
  const ignire = IgnireCalendar.toIgnire(gregorian);
  const text = describe(ignire);
  const widget = new ListWidget();
  widget.refreshAfterDate = nextLocalMidnight(now);
  widget.url = WEB_URL;

  if (family === "accessoryInline") {
    addText(widget, text.inline, Font.systemFont(14));
  } else if (family === "accessoryCircular") {
    widget.addAccessoryWidgetBackground = true;
    widget.addSpacer();
    addText(widget, text.circularTop, Font.systemFont(11), { center: true });
    addText(widget, String(ignire.day), Font.boldRoundedSystemFont(24), { center: true });
    widget.addSpacer();
  } else if (family === "accessoryRectangular") {
    addText(widget, text.title, Font.systemFont(12));
    addText(widget, text.date, Font.boldRoundedSystemFont(22), { minimumScaleFactor: 0.6 });
    addText(widget, text.detail, Font.systemFont(12), { minimumScaleFactor: 0.7 });
  } else {
    // Home Screen widgets and the in-app preview: soot black and gold, like the emblem.
    widget.backgroundColor = SOOT;
    addText(widget, `🔥 ${text.title}`, Font.semiboldSystemFont(13), { color: GOLD });
    widget.addSpacer();
    addText(widget, text.date, Font.boldRoundedSystemFont(36), {
      color: ignire.isFestival ? EMBER : new Color("#F3E9D8"),
      minimumScaleFactor: 0.5,
    });
    addText(widget, ignire.isFestival ? text.detail : text.year, Font.semiboldSystemFont(15), {
      color: GOLD,
      minimumScaleFactor: 0.7,
    });
    widget.addSpacer(4);
    addText(
      widget,
      `公元 ${IgnireCalendar.formatISO(gregorian)} ${IgnireCalendar.weekdayLabel(gregorian)}`,
      Font.systemFont(11),
      { color: ASH, minimumScaleFactor: 0.6 }
    );
  }
  return widget;
}

const now = new Date();
const widget = buildWidget(config.widgetFamily, now);
if (config.runsInWidget) {
  Script.setWidget(widget);
} else {
  await widget.presentSmall();
}
Script.complete();
