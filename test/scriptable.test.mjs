// Runs the generated Scriptable widget against a minimal mock of Scriptable's API.
import assert from "node:assert/strict";
import { test } from "node:test";
import vm from "node:vm";

import { buildScriptable, WEB_URL } from "../scripts/build-scriptable.mjs";

class MockElement {
  constructor(kind, text) {
    Object.assign(this, { kind, text, centered: false });
  }
  centerAlignText() {
    this.centered = true;
  }
}

class MockListWidget {
  constructor() {
    this.items = [];
  }
  addText(text) {
    const element = new MockElement("text", text);
    this.items.push(element);
    return element;
  }
  addSpacer(length) {
    this.items.push(new MockElement("spacer", length));
  }
  async presentSmall() {
    this.presented = "small";
  }
  get texts() {
    return this.items.filter((item) => item.kind === "text").map((item) => item.text);
  }
}

class MockColor {
  constructor(hex) {
    this.hex = hex;
  }
  static dynamic(light, dark) {
    return { light, dark };
  }
}

async function runWidget(family, now) {
  const result = {};
  const RealDate = Date;
  class FixedDate extends RealDate {
    constructor(...args) {
      super(...(args.length ? args : [now.getTime()]));
    }
  }
  const font = (name) => (size) => ({ name, size });
  const context = vm.createContext({
    module: { exports: {} },
    Date: FixedDate,
    String,
    Number,
    Object,
    Math,
    RangeError,
    TypeError,
    ListWidget: class extends MockListWidget {
      constructor() {
        super();
        result.widget = this;
      }
    },
    Color: MockColor,
    Font: {
      systemFont: font("system"),
      semiboldSystemFont: font("semibold"),
      boldRoundedSystemFont: font("boldRounded"),
    },
    config: { runsInWidget: family !== null, widgetFamily: family },
    Script: {
      setWidget: (widget) => (result.setWidget = widget),
      complete: () => (result.completed = true),
    },
  });
  await vm.runInContext(`(async () => {\n${buildScriptable()}\n})()`, context);
  return result;
}

const OCT_7_2026 = new Date(2026, 9, 7, 9, 30);

test("lock-screen inline widget", async () => {
  const { widget, setWidget, completed } = await runWidget("accessoryInline", OCT_7_2026);
  assert.equal(setWidget, widget);
  assert.ok(completed);
  assert.deepEqual(widget.texts, ["🔥 新曆 4 年 2/17"]);
  assert.equal(widget.url, WEB_URL);
});

test("lock-screen circular widget", async () => {
  const { widget } = await runWidget("accessoryCircular", OCT_7_2026);
  assert.deepEqual(widget.texts, ["2月", "17"]);
  assert.equal(widget.addAccessoryWidgetBackground, true);
  assert.ok(widget.items.filter((item) => item.kind === "text").every((item) => item.centered));
});

test("lock-screen rectangular widget", async () => {
  const { widget } = await runWidget("accessoryRectangular", OCT_7_2026);
  assert.deepEqual(widget.texts, ["今日新曆", "2/17", "新曆 4 年 · 序日 47"]);
});

test("festival day and pre-epoch year", async () => {
  const festival = await runWidget("accessoryCircular", new Date(2024, 7, 21, 12));
  assert.deepEqual(festival.widget.texts, ["祭典", "5"]);
  const before = await runWidget("accessoryRectangular", new Date(2023, 7, 22, 12));
  assert.deepEqual(before.widget.texts, ["今日新曆", "祭典第 6 天", "新曆 前一年 · 序日 366"]);
});

test("home-screen widget and in-app preview", async () => {
  const home = await runWidget("small", OCT_7_2026);
  assert.deepEqual(home.widget.texts, ["🔥 今日新曆", "2/17", "新曆 4 年", "2026-10-07 星期三"]);
  const preview = await runWidget(null, OCT_7_2026);
  assert.equal(preview.widget.presented, "small");
  assert.equal(preview.setWidget, undefined);
});

test("refreshes just after the next local midnight", async () => {
  const { widget } = await runWidget("accessoryInline", new Date(2026, 9, 7, 23, 59));
  const refresh = widget.refreshAfterDate;
  assert.deepEqual(
    [refresh.getFullYear(), refresh.getMonth(), refresh.getDate(), refresh.getHours()],
    [2026, 9, 8, 0]
  );
});
