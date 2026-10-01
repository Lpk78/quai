# SA-15 — Demo fixture data

- **ID**: SA-15 (typed as `DEMO-01`; renumbered to the `SA-` prefix the team scheme reserves for
  `SamDana-maker`, see `prompts/README.md`)
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-01
- **Branch**: `feature/demo-fixtures`
- **Issue**: none — demo preparation

## Prompt as typed

```
DEMO-01 Create demo fixture data in src/demo_fixtures.py (or similar): an operator record
{"card_id": "QUAI-OP-7842", "name": "Léo-Paul", "stops": [8 Madrid stops in order: Depot-Centro,
Chamberí, Salamanca, Retiro, Arganzuela, Carabanchel, Latina, Moncloa-Aravaca]}, a manifest of ~18
already-loaded boxes with varied realistic dimensions/weights distributed across those 8 stops (aim
for ~75-80% fill when run through the solver), and one extra box {"code": "QUAI-BOX-0001", "label":
"fragile parcel", "dimensions": [40,30,25], "weight": 8, "fragile": true} that starts unplaced,
representing the box scanned live during the demo. Run it through the real solver (src/demo.py
pattern) to confirm it places realistically and the fill rate is in that range; adjust box sizes if
not. Write it as an importable fixture plus a short script to print the computed fill rate so it's
easy to verify. No API calls needed, no tests required beyond confirming the solver run succeeds.
```

## Outcome

To be filled when the pull request is opened.
