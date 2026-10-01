# SA-14b — The 3D load plan on `/app/plan`

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `feature/app-plan-3d` (stacked on `feature/app-plan-screen`, #45)
- **Issue:** #7 (second half; the list screen is SA-14a)

## Prompt as typed

```
Start SA-14b now, stacked on feature/app-plan-screen; do not wait for the review.
```

Agreed scope from the SA-14 split recorded on #7: the 3D scene with `three` +
`@react-three/fiber` + `@react-three/drei`, the van as a translucent box, placed boxes, orbit and
zoom by touch, tap a box to see it. **Coloured by index, not by stop** — `POST /plan` returns no
stop per box, so colour by stop is SA-14c and waits for #36.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/48 (reviewer: `MORHI11`), stacked on #45
- **What the AI produced:** `web/src/plan/LoadScene.jsx`, the inspector and selection wiring in
  `PlanScreen.jsx`, the scene styles, the three dependencies, and 9 tests.
- **What was changed by hand:** colour by index rather than by stop, because the response carries no
  stop — the brief asked for stop colours and the data does not exist until #36. The inspector shows
  only what the response holds for the same reason. The 3D modules are mocked in the screen tests:
  jsdom has no WebGL, so what a canvas draws is not visible to the suite, and the tests check the
  arithmetic instead rather than pretending to check pixels.
- **Verified:** 47 web tests, 333 Python tests, `npm run build` clean.
