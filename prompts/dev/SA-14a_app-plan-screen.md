# SA-14a — The plan screen at `/app/plan`, without the 3D view

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `feature/app-plan-screen`
- **Issue:** #7 (reassigned from `MORHI11` by `Lpk78` as product owner; `MORHI11` stays reviewer)

## Prompt as typed

```
/task SA-14 App screen: 3D load plan at /app/plan. First list what already exists under web/src (app
routes, API client, any 3D code) and reuse it. Render the solver's POST /plan response with three.js
(@react-three/fiber + drei): the van as a translucent box, each placed box coloured by stop,
orbit/zoom by touch, tap a box to see its id, stop and the constraints applied to it. Unplaced boxes
and UnsupportedConstraint are listed under the view, never hidden. Mobile-first (390px), brand tokens
from tokens.css, light theme like 05_UI/QUAI_app_mockups.png. Use a fixture response for tests; no
API key needed. Tests for: every placed box rendered, unplaced list shown, empty plan state.
```

## How it was split, and why

The survey step found the screen as specified is not buildable against `main`: `POST /plan` takes
`{container, boxes}` and returns `{placements, unplaced, fill_rate, total_weight}`, with no stop per
box and no constraint provenance, and `Plan` records neither. Colouring by stop and showing "the
constraints applied to it" therefore need API and solver work, not UI work.

Agreed with the product owner as three pieces: **SA-14a** this screen without 3D (no new
dependencies, buildable today), **SA-14b** the 3D scene stacked on it with boxes coloured by index,
**SA-14c** colour by stop and constraints applied, which waits for #36. Recorded on #7.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/45 (reviewer: `MORHI11`) — first half of #7
- **What the AI produced:** `web/src/api.js` (the first API client in the app), `PlanScreen.jsx` with
  `plan.css` and the `/app/plan` route, the demo load and a solver-generated fixture, 13 tests, the
  network guard in `test-setup.js`, the README and roadmap entries, and two screenshots at 390px.
- **What was changed by hand:** three things.
  The split itself. The brief asked for a 3D view with boxes coloured by stop and a tap panel showing
  the constraints applied; the survey found `POST /plan` returns no stop and `Plan` records no
  constraint provenance, so those are API and solver work. Raised before writing code and agreed with
  the product owner; written up on #7 so the reason survives.
  The duplicated failure message: a test caught the screen printing the same sentence twice when a
  refused load has its detail equal to its message. Fixed in the component rather than in the test.
  The network guard: while checking that the copy rules covered the new page, a `fetch` spy showed
  that rendering `/app/plan` in a test called `http://127.0.0.1:8000/plan` for real. It passed only
  because nothing was listening. Unmocked `fetch` now fails loudly.
- **Verified:** 310 Python tests and 38 web tests pass, `npm run build` is clean, and the screen was
  run against the live solver at 390px — 10 of 11 placed, 39 % fill, 276 kg, mattress not placed,
  which is exactly what `src/demo.py` produces. The fixture is a real response, not an invented one.
- **Ownership:** #7 was `MORHI11`'s. `Lpk78` reassigned it; the comment on #7 says so, tags
  `MORHI11` so nobody builds it twice, and records that he remains the reviewer.
