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

To be filled when the pull request is opened.
