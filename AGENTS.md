# Repository guide for coding agents

## Purpose

Ignire Calendar converts between the proleptic Gregorian calendar and a custom
calendar of twelve 30-day months plus five or six year-end festival days. It is
a static website (GitHub Pages, `docs/`) and a Scriptable iPhone widget. All
user-facing text is Traditional Chinese.

## Non-negotiable calendar invariants

- Ignire year 1, month 1, day 1 is Gregorian `2023-08-23`.
- A new year occurring in Gregorian year `Y` starts on August 23 when `Y + 1`
  is a leap year, and August 22 otherwise.
- Gregorian March 1 is always Ignire month 7, day 12.
- Gregorian August 17 is always festival day 1.
- Regular months are numbered 1–12 and contain exactly 30 days.
- Festival dates use month `0` in the API and day 1–5 or 1–6.
- User-facing labels never call the year before year 1 “year 0”; they use
  `前一年`, `前2年`, and so on.

If a requested change appears to contradict an invariant, confirm the calendar
rule with the user before changing the engine. `PYTHON_ENGINE_SHA256` in
`test/calendar.test.mjs` pins the output for every supported date; it must only
change together with a confirmed rule change.

## Doctrine and wording

`doctrine/火神信仰與祈禱手冊.md` is the leader's original text; never edit it.
`docs/handbook.html` reproduces it verbatim. All user-facing wording must follow it:

- 公元 (not 公曆); count days in 日 (not 天); 8/17 is 聖日 (festival day 1);
  the year's first day is 首日; the sect is 火與焰; members are 信徒 and 使者.
- Festival days are not counted in the calendar: never show a day-of-year for them.
- Visual language: soot black and gold; rainbow only at the tip of a line
  (`.tail-rule`), like the emblem's tail.

## Project map

- `docs/ignire-calendar.js`: the only calendar engine. Classic script with no
  dependencies; works in browsers, Node (`require`), and Scriptable. Uses integer
  day numbers, never `Date`, for calendar arithmetic.
- `docs/app.js`, `docs/index.html`, `docs/style.css`: website UI only.
- `docs/handbook.html`: the handbook page.
- `design/hinokarasu.JPEG`: the user's original logo (gold crow on navy).
  `docs/crow.png` and `docs/crow-128.png` are transparent cut-outs of it (alpha
  from the red channel above the navy background RGB 35,40,48, then cropped);
  `docs/favicon.png` and `docs/apple-touch-icon.png` put that cut-out on soot
  #14100D. The cut-out only works on dark surfaces; keep it off light ones.
  Do not replace the logo with a drawn one.
- The masthead is always a soot band (both themes) with icon tabs; the current
  page is marked with `aria-current="page"`, which draws the flame indicator.
- `scripts/scriptable-widget.js`: Scriptable widget source.
- `scripts/build-scriptable.mjs`: embeds the engine into the widget, producing
  `docs/scriptable/IgnireCalendar.js`. Never edit the generated file by hand.
- `test/`: Node built-in tests (`node --test`).

Do not put conversion logic in `app.js` or the widget; add it to the engine and
test it directly.

## Development commands

```bash
npm run build   # regenerate docs/scriptable/IgnireCalendar.js
npm test        # fails if the generated script is stale, then runs all tests
npm run serve   # preview at http://localhost:8000
```

## Completion checklist

- Preserve all calendar invariants and cover new behavior with tests.
- Run `npm run build` after changing the engine or widget, then `npm test`.
- Check the site at phone width (390px) and in light and dark mode.
- Update `README.md` and this file when commands or architecture change.
