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

- **PR:** https://github.com/Lpk78/quai/pull/50 (reviewer: `MORHI11`)
- **What the AI produced:** `src/demo_fixtures.py` (the operator card, the eight-stop Madrid route,
  the eighteen loaded boxes, the scanned parcel, and the `boxes()`/`manifest()`/`constraint_set()`/
  `plan()` helpers plus the printing script), `tests/test_demo_fixtures.py`, the
  `documentation/failures.md` entry, and the README subsection.
- **What was changed by hand:** nothing in the committed code. The box dimensions were not written
  once and kept, though — they were tuned against the real solver over five rounds, which is the only
  part of this task that was not a straight write (below).
- **How the fill rate was reached, since the task set a range rather than numbers:** the first set
  came back at **88.8%** with the full-width mattress unplaced — too dense, because 85 cm wide and
  85 cm high tile the 170 cm van exactly in both directions. Dropping the cartons to 45 cm high
  introduced the head-room voids a real round has and brought it to **78.1%** with 18/18 placed.
- **Judgement calls made with the user, before writing code:** the task ID. `DEMO-01` does not fit
  the `LP-`/`SA-`/`HY-` scheme `prompts/README.md` says exists so IDs never collide, so it was
  confirmed as `SA-15` rather than committed as typed, with the original noted at the top of this
  file.
- **Judgement calls made without asking, and why:** the van is the one `src/demo.py` already uses, so
  the two demos are comparable; the stops are `S1`–`S8` with names, because `Manifest` takes ids; and
  the eight stops were kept exactly as the task listed them, depot included, rather than demoted to
  seven real drops — flagged on the PR as something the reviewer may want changed.
- **What went wrong, and what it taught:** assigning the scanned parcel to stop 4 made the load
  *worse* — 17 of 19 placed, two already-placed cartons ejected, fill down to 74.4%. First fit never
  revisits a box it has placed, and `loading_order` puts a stop-4 parcel in the middle of the round
  where it takes corners the later boxes needed. Five cm off the lamp carton fixed it: the parcel now
  goes to stop 2 with **19/19 at 78.2%**. Recorded in `documentation/failures.md`, because the
  live-scan screen and roadmap row 12 both have to answer "what moved", not just "did it fit".
- **Verified:** 320 tests pass, 1 skip. `python3 src/demo_fixtures.py` prints 77.8% loaded and 78.2%
  scanned; no API call anywhere in the fixture or its tests.
