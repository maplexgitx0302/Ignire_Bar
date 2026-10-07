// Checks the cache-busting stamps that scripts/build.mjs writes into the pages.
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";

import { PAGES } from "../scripts/build.mjs";

const docs = (path) => new URL(`../docs/${path}`, import.meta.url);
const hash = (path) => createHash("sha256").update(readFileSync(docs(path))).digest("hex").slice(0, 10);

test("every local asset exists and carries its content hash", () => {
  for (const page of PAGES) {
    const html = readFileSync(docs(page), "utf8");
    const refs = [...html.matchAll(/(?:src|href)="(?!https?:|\/\/|#|mailto:|\.\/)([^"]+\.(?:css|js|png|jpe?g|svg))(\?v=[0-9a-f]+)?"/g)];
    assert.ok(refs.length > 0, page);
    for (const [, path, stamp] of refs) {
      assert.ok(existsSync(docs(path)), `${page}: ${path} is missing`);
      assert.equal(stamp, `?v=${hash(path)}`, `${page}: ${path}`);
    }
  }
});

test("pages and version.json agree on the site version", () => {
  const { version } = JSON.parse(readFileSync(docs("version.json"), "utf8"));
  assert.match(version, /^[0-9a-f]{10}$/);
  for (const page of PAGES) {
    assert.ok(readFileSync(docs(page), "utf8").includes(`<meta name="site-version" content="${version}">`), page);
    assert.ok(readFileSync(docs(page), "utf8").includes('src="update.js?v='), `${page} loads update.js`);
  }
});
