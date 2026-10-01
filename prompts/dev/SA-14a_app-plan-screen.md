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

