# SA-07 — Replan around what is already in the van after an incident

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `feature/plan-recompute` (branched from `feature/solver-v2`, #27)
- **Issue:** none — the roadmap's *Later* row `feature/operator-mode` is the nearest thing

## Prompt as typed

```
/task SA-07 Add POST /plan/recompute: keep the boxes already loaded fixed, apply an incident (box
missing, damaged or added) and replan the rest with the same constraints and stop order, with tests
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/36 (reviewer: `MORHI11`) — **depends on #27**, which is
  where `solve()` learns about constraints and stop order; this branch is cut from `feature/solver-v2`
  and must merge after it, the same way #22 depended on #21.
- **What the AI produced:** the `fixed=` parameter and `refuse_impossible_start()` in
  `src/quai/solver.py`, `src/quai/incident.py` (the three incident kinds and what each does to the two
  lists), `POST /plan/recompute` in `src/server.py` with its error mapping, 39 new tests across
  `tests/test_incident.py`, `tests/test_solver.py` and `tests/test_server.py`, and the README section.
- **What was changed by hand:** the three decisions the task left open, which are written into the PR
  body rather than buried in code. `missing` on a box the operator says is already loaded is **refused**
  instead of applied, because it describes a vehicle that cannot exist and the two readings give
  different plans; `damaged` on a loaded box *is* applied, because freeing that space is the main reason
  to recompute at all. `added` carries the box rather than an id, since dimensions cannot be inferred
  from a name. Constraints are re-parsed against the load as it now stands rather than trusted, because
  the manifest changed when a box arrived or left.
- **Verified:** 323 tests pass, and every file parses under the 3.11 grammar
  (`ast.parse(..., feature_version=(3, 11))`) — the check added after SA-12 pushed syntax that only
  Python 3.12 accepts. The fixed-placement guarantee was mutation-tested three ways: not seeding the
  placements, ignoring the fixed weight, and dropping the start validation each fail the suite. The
  README's example response is a real one from the endpoint, not an invented example.
- **Scope note:** no issue existed. The roadmap's *Later* row `feature/operator-mode` is the nearest
  thing and now records that its server half is done; the PR asks the reviewer whether that should have
  been an issue instead.
