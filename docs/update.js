/*
 * GitHub Pages lets browsers cache every file for 10 minutes, so right after a
 * deploy a visitor may still see the previous version. This checks version.json
 * (never cached) and, if the site has changed, loads the new version once.
 * Asset URLs carry content hashes (scripts/build.mjs), so a fresh page always
 * gets matching CSS, scripts, and images.
 */
(() => {
  "use strict";

  const meta = document.querySelector('meta[name="site-version"]');
  const current = meta && meta.content;
  if (!current || location.protocol === "file:") return;

  const url = new URL(location.href);
  if (url.searchParams.get("v") === current) {
    // We arrived here through an update: tidy the address bar.
    url.searchParams.delete("v");
    history.replaceState(history.state, "", url);
  }

  function alreadyTried(version) {
    try {
      const key = `site-update-${version}`;
      if (sessionStorage.getItem(key)) return true;
      sessionStorage.setItem(key, "1");
    } catch {
      // Storage unavailable: still update, the ?v= URL is unique per version.
    }
    return false;
  }

  async function check() {
    try {
      const response = await fetch(`version.json?t=${Date.now()}`, { cache: "no-store" });
      if (!response.ok) return;
      const { version } = await response.json();
      if (!version || version === current || alreadyTried(version)) return;
      const next = new URL(location.href);
      next.searchParams.set("v", version);
      location.replace(next);
    } catch {
      // Offline or blocked: keep showing the cached page.
    }
  }

  check();
  document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") check();
  });
})();
