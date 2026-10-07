// Builds docs/scriptable/IgnireCalendar.js: the Scriptable widget with the
// calendar engine embedded, so users can paste a single self-contained file.
//
//   node scripts/build-scriptable.mjs           write the file
//   node scripts/build-scriptable.mjs --check   fail if the file is out of date

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

export const WEB_URL = "https://maplexgitx0302.github.io/Ignire_Bar/";

const root = new URL("../", import.meta.url);
const read = (path) => readFileSync(new URL(path, root), "utf8");
export const outputPath = fileURLToPath(new URL("docs/scriptable/IgnireCalendar.js", root));

export function buildScriptable() {
  return read("scripts/scriptable-widget.js")
    .replace("/*@@IGNIRE_CORE@@*/", () => read("docs/ignire-calendar.js").trimEnd())
    .replace("@@WEB_URL@@", WEB_URL);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const built = buildScriptable();
  if (process.argv.includes("--check")) {
    if (readFileSync(outputPath, "utf8") !== built) {
      console.error("docs/scriptable/IgnireCalendar.js is out of date; run npm run build");
      process.exit(1);
    }
  } else {
    writeFileSync(outputPath, built);
  }
}
