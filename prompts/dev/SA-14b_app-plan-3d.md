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

