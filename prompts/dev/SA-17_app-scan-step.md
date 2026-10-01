# SA-17 — A scan step before the dictate screen

- **ID**: SA-17
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-01
- **Branch**: `feature/app-scan-step`
- **Issue**: none — demo preparation

## Prompt as typed

```
SA-17 A "scan package" step before /app/dictate. New screen /app/scan: camera-based QR scan (reuse
whatever QR library LP-20 gets working, check with Lpk78's branch) reading a code shaped
"QUAI:BOX:<id>". On a valid scan of QUAI-BOX-0001, show its known dimensions/weight (from
src/demo_fixtures.py), add it to the current manifest as unplaced, then route to /app/dictate so the
operator can say what to do with it. Wire the home screen's main button to this new scan step instead
of going straight to /app/dictate. Mobile-first, reuse tokens.css.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/54 (reviewer: `MORHI11`)
- **What the AI produced:** `web/src/scan/scanCode.js` (the label seam), `web/src/pages/Scan.jsx`, the
  route in `App.jsx`, the repointed button in `Home.jsx`, `scan/scanCode.test.js` and
  `pages/scan.test.jsx`, and the README section.
- **What was changed by hand:** nothing in the committed code.
- **Two premises in the task that did not match the repository, both checked before writing code:**
  `LP-20` does not exist — no branch, PR, issue, prompt file or mention anywhere, and no QR library in
  `web/package.json` — so there was nothing of Léo-Paul's to reuse for the camera. And
  `QUAI-BOX-0001` is already inside `web/src/data/manifest.js`, so "add it to the current manifest as
  unplaced" had nothing to add it to; HY-16's own comment in that file says no before/after is
  modelled.
- **Judgement calls made with the user, before writing code:** both of the above were raised rather
  than guessed at. The camera was settled as a seam plus a working typed field — no dependency added,
  nothing to rip out when LP-20 chooses one. The manifest restructure the user sent to MORHI11 to
  arbitrate rather than deciding alone.
- **Coordination, because MORHI11 was in the same files:** he was doing HY-15 (visual polish) on these
  screens at the same time, so he was asked first. He confirmed he was not editing `App.jsx`, and in
  `Home.jsx` only classes and spacing rather than the `to=` attribute, which made the route and the
  one-line repoint safe. He also ruled the manifest restructure out of scope for both branches and
  asked that it get its own ID. On that basis this branch leaves `manifest.js`, `Dictate.jsx` and
  `app.css` untouched — and the screen adds no new class names, since `app.css` was being reworked
  underneath it.
- **One of his tests changed:** `pages/app.test.jsx` asserted the home button links to `/app/dictate`,
  which this task deliberately changes. The expectation was updated to `/app/scan` rather than the test
  removed; it still asserts the same thing about the same button.
- **Left undone, deliberately:** scanning a parcel *into* a load, so `/app/dictate` reads 18 + 1. Needs
  its own prompt file and ID; flagged on the PR for Léo-Paul to number.
- **Verified:** 73 web tests pass (60 before), 347 Python tests pass, 1 skip, `npm run build` clean.
