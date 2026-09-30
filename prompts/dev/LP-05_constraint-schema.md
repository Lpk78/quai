# LP-05 — Validated JSON schema for translated constraints

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-30
- **Branch:** `feature/constraint-schema`
- **Issue:** #10

## Prompt as typed

```
LP-05 #10 Define the constraint JSON schema in src/quai/constraints.py following the contract in
documentation/prompt_evaluation.md (the nine constraint types, the six unresolved reasons, cm and kg,
the "Route and unloading order" rules), with validation that rejects unknown item ids and wrong units,
and tests
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/21
- **What the AI produced:** `src/quai/constraints.py` — the nine constraint types with their fields, the
  six `unresolved` reasons, `Manifest` and `ConstraintSet` with the route accessors, `find_problems()` and
  `parse()` as the only door to the solver — plus `tests/test_constraints.py` (60 tests, including the
  module checked against the Markdown tables of the contract and all 25 expected outputs validated), the
  contract paragraph in `documentation/prompt_evaluation.md` and the rule added to `CLAUDE.md`.
- **What was changed by hand:** the first version validated shapes only, so the contradiction checks were
  added (`at_bottom` + `on_top`, two stops for one item, two items loaded last at the same stop) on the
  grounds that the contract gives the model a `contradiction` reason and the solver should never receive
  one. Three crash paths in the validator were found by asking what JSON allows that we never write, and
  fixed: `Infinity`/`NaN` limits, and a `type` or a `reason` given as a list, which are unhashable and
  raised `TypeError` instead of being refused. The test fixture that reads the route out of the document
  was also wrong at first (see `documentation/failures.md`).
- **Verified:** 90 tests pass. Every guard was mutation-tested — removing the unknown-item check, the
  unknown-stop check, the whole-centimetre check, the extra-field check, the unknown-top-level-key check,
  the contradiction pass or the `isinstance` guard each makes at least one test fail.
