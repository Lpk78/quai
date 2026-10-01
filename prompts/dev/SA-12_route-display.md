# SA-12 — Route display data: geocoding, road geometry and per-stop ETA

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `feature/route-display`
- **Issue:** none — this is new scope, not on the roadmap

## Prompt as typed

```
/task SA-12 Add route display data to the server: POST /route takes the ordered stops of a delivery
list (addresses) and returns, in that exact order, the geocoded points (api-adresse.data.gouv.fr), the
road route geometry and an estimated arrival time per stop (OSRM), plus total distance and duration.
QUAI never reorders stops: the order comes with the manifest. Timeouts and clear errors when a
geocoder or router is down; tests with mocked HTTP; document the two services and their limits in the
README.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/35 (reviewer: `MORHI11`)
- **What the AI produced:** `src/quai/routing.py` (the geocoder and router clients, their named failures
  and the arrival-offset arithmetic), `POST /route` in `src/server.py` with the error mapping,
  `tests/test_routing.py` and the `TestRouteEndpoint` class in `tests/test_server.py` — 29 tests, all HTTP
  mocked — the README section documenting both services and their limits, and the `failures.md` entry.
- **What was changed by hand:** two things, both about not trusting the work.
  The response shapes were taken from the live services before any client was written, not from memory:
  one call each to `api-adresse.data.gouv.fr` and `router.project-osrm.org`, which is how the leg/waypoint
  structure and the "empty `features` list rather than an error" behaviour were established.
  Then the order guard was mutation-tested, and the first version of the test fixture did not catch a
  sort. Fixed and written up (see below).
- **Verified:** 290 tests pass. The reordering guard was mutation-tested four ways — sort by longitude,
  sort by latitude, reverse the list, and swap `/route` for `/trip` — and each now fails the suite. The
  README's example response is a real one: the pipeline was run end to end against both live services on
  2026-10-01 and the numbers pasted from what came back, rather than an example written to look right.
- **What went wrong:** the two tests asserting stop order passed against `sorted(points, key=lon)`,
  because the fixture drove Amiens → Paris → Lille, which is already in ascending longitude. The test
  looked like it was about sequence while the data made sequence irrelevant. The fixture now drives
  Lille → Amiens → Paris, which differs from every plausible sort. `documentation/failures.md`,
  *The order test that could not fail*.
- **What went wrong, twice:** the push went out green locally and CI went red on a `SyntaxError`.
  `f"...{", ".join(x)}"` nests the same quote inside an f-string, which Python 3.12 allows and 3.11 —
  what `tests.yml` runs and what the README promises — does not. Fixed, and then the whole tree was
  parsed with `ast.parse(..., feature_version=(3, 11))` to check nothing else had crept in on a 3.14
  machine. `documentation/failures.md`, *Valid Python locally, a syntax error in CI*.
- **Scope note:** no issue and no roadmap row existed for this work. A `feature/route-display` row was
  added to the roadmap's *Later* table rather than leaving it untracked; the PR asks the reviewer whether
  it should have been an issue first.
