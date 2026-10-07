// Runs docs/update.js against a fake browser to check it updates exactly once.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import vm from "node:vm";

const source = readFileSync(new URL("../docs/update.js", import.meta.url), "utf8");

async function run({ current = "aaa", served = "bbb", href = "https://x.test/Ignire_Bar/", storage = new Map() } = {}) {
  const calls = { fetches: [], replaced: null, replaceState: null };
  const listeners = {};
  const context = vm.createContext({
    URL,
    Date,
    document: {
      visibilityState: "visible",
      querySelector: () => (current === null ? null : { content: current }),
      addEventListener: (type, listener) => (listeners[type] = listener),
    },
    location: {
      href,
      protocol: new URL(href).protocol,
      replace: (next) => (calls.replaced = String(next)),
    },
    history: { state: null, replaceState: (_, __, next) => (calls.replaceState = String(next)) },
    sessionStorage: {
      getItem: (key) => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, value),
    },
    fetch: async (url, options) => {
      calls.fetches.push({ url, options });
      return { ok: true, json: async () => ({ version: served }) };
    },
  });
  vm.runInContext(source, context);
  await new Promise((resolve) => setImmediate(resolve));
  return { calls, listeners, storage };
}

test("loads the new version when version.json differs", async () => {
  const { calls } = await run();
  assert.equal(calls.fetches.length, 1);
  assert.match(calls.fetches[0].url, /^version\.json\?t=\d+$/);
  assert.equal(calls.fetches[0].options.cache, "no-store");
  assert.equal(calls.replaced, "https://x.test/Ignire_Bar/?v=bbb");
});

test("does nothing when already up to date", async () => {
  const { calls } = await run({ served: "aaa" });
  assert.equal(calls.replaced, null);
});

test("never reloads twice for the same version (no loops if caches lag)", async () => {
  const storage = new Map();
  await run({ storage });
  const second = await run({ storage });
  assert.equal(second.calls.replaced, null);
});

test("tidies ?v= from the address bar after an update", async () => {
  const { calls } = await run({ href: "https://x.test/Ignire_Bar/?v=aaa", served: "aaa" });
  assert.equal(calls.replaceState, "https://x.test/Ignire_Bar/");
  assert.equal(calls.replaced, null);
});

test("is inert for local files and pages without a version", async () => {
  assert.equal((await run({ href: "file:///docs/index.html" })).calls.fetches.length, 0);
  assert.equal((await run({ current: null })).calls.fetches.length, 0);
});

test("checks again when the page becomes visible", async () => {
  const { calls, listeners } = await run({ served: "aaa" });
  listeners.visibilitychange();
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(calls.fetches.length, 2);
});
