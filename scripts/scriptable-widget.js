// Ignire 新曆 — Scriptable widget
//
// Shows today's Ignire date on the Lock Screen (inline, circular, rectangular)
// or the Home Screen (small, medium). Paste this whole file into a new script in
// the Scriptable app, then add a Scriptable widget and choose this script.
//
// Generated from scripts/scriptable-widget.js by scripts/build-scriptable.mjs.
// Edit those sources, not docs/scriptable/IgnireCalendar.js.

/*@@IGNIRE_CORE@@*/

const ACCENT = new Color("#D96C3B");
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

function buildWidget(family, now) {
  const gregorian = IgnireCalendar.today(now);
  const ignire = IgnireCalendar.toIgnire(gregorian);
  const yearText = `新曆 ${IgnireCalendar.yearLabel(ignire.year)}`;
  const widget = new ListWidget();
  widget.refreshAfterDate = nextLocalMidnight(now);
  widget.url = WEB_URL;

  if (family === "accessoryInline") {
    addText(widget, `🔥 ${yearText} ${IgnireCalendar.compactText(ignire)}`, Font.systemFont(14));
  } else if (family === "accessoryCircular") {
    widget.addAccessoryWidgetBackground = true;
    widget.addSpacer();
    addText(widget, ignire.isFestival ? "祭典" : `${ignire.month}月`, Font.systemFont(11), {
      center: true,
    });
    addText(widget, String(ignire.day), Font.boldRoundedSystemFont(24), { center: true });
    widget.addSpacer();
  } else if (family === "accessoryRectangular") {
    addText(widget, "今日新曆", Font.systemFont(12));
    addText(widget, IgnireCalendar.compactText(ignire), Font.boldRoundedSystemFont(22), {
      minimumScaleFactor: 0.6,
    });
    addText(widget, `${yearText} · 序日 ${ignire.dayOfYear}`, Font.systemFont(12), {
      minimumScaleFactor: 0.7,
    });
  } else {
    // Home Screen widgets and the in-app preview.
    widget.backgroundColor = Color.dynamic(new Color("#FFF8EF"), new Color("#241A14"));
    const text = Color.dynamic(new Color("#2B2118"), new Color("#F6EBDD"));
    const muted = Color.dynamic(new Color("#7A6555"), new Color("#BCA894"));
    addText(widget, "🔥 今日新曆", Font.semiboldSystemFont(13), { color: ACCENT });
    widget.addSpacer();
    addText(widget, IgnireCalendar.compactText(ignire), Font.boldRoundedSystemFont(36), {
      color: text,
      minimumScaleFactor: 0.5,
    });
    addText(widget, yearText, Font.semiboldSystemFont(15), { color: text });
    widget.addSpacer(4);
    addText(
      widget,
      `${IgnireCalendar.formatISO(gregorian)} ${IgnireCalendar.weekdayLabel(gregorian)}`,
      Font.systemFont(12),
      { color: muted, minimumScaleFactor: 0.7 }
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
