# HY-01 — React + Vite web app, installable on a phone

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/web-app`
- **Issue:** #18

## Prompt as typed

```
HY-01 #18 Create the React + Vite web app in a web/ folder: landing page at / and empty application page at /app, styled from documentation/design.md and following its copy rules (slogan "People talk. We load."), installable as a PWA on a phone, with a README section on how to run it; also add CORSMiddleware to src/server.py so the Vite dev server can call the API
```

## Branch base

This branch was cut from `docs/brand-kit` (#28) rather than `main`, because the task says to style the
app from `documentation/design.md` and the PWA needs the brand app icon — and neither was on `main` at
the time. Branching from `main` would have meant copying the palette by hand, the exact mistake
`design.md` warns about, or keeping a second copy that then drifts.

**#28 merged at 10:48 while this task was being built**, so the question resolved itself: `main` now
carries the brand kit, the branch was merged up, and the Pull Request targets `main` as normal.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/33
- **What the AI produced:** the whole `web/` project (React + Vite, plain JSX, `/` and `/app` routing,
  the landing copy, the empty shell), `scripts/build-tokens.mjs` generating `src/tokens.css` from
  `assets/brand/tokens.json`, the hand-written PWA manifest and service worker with icons rasterised
  from the brand SVG, 19 web tests, the `CORSMiddleware` in `src/server.py` with three tests, the `web`
  job in `tests.yml`, and the README section.
- **How it was checked:** the production build was served and opened in a real browser — both routes
  rendered, and the PWA criteria were verified rather than assumed (manifest served, all four icon
  entries resolving with the right content types, service worker registered and active, secure context,
  `display: standalone`). `npm ci` was run exactly as CI runs it. Each test was checked to fail when
  what it guards is removed: deleting the `CORSMiddleware` fails two of the server tests.
- **What it found on its own:** the "no literal colours in the stylesheet" test caught a grey written by
  hand (`#4b5563`). Rather than deleting the test, the colour was measured (6.99:1 on the background),
  promoted to a documented derived token `--quai-text-muted`, and the test kept.
- **What was changed by hand:** the decisions, not the output. Plain JSX over TypeScript, under "prefer
  the simplest code that works". A hand-written service worker over `vite-plugin-pwa`, so there is no
  generated precache list to keep in step. CORS origins listed rather than wildcarded, because this API
  is the only place the Claude key lives. And writing the landing copy at all: `design.md` records that
  no supplied mockup provides any that passes the copy rules.
