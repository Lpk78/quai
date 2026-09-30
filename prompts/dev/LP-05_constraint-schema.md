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
- **Rule that moved under the task:** #20 merged while this branch was open and replaced step 7 of
  `/task`, so the row this task had added to `documentation/ai_usage.md` was dropped and this Outcome is
  the only record of the AI help (see `documentation/failures.md`).
- **Verified:** 90 tests pass. Every guard was mutation-tested — removing the unknown-item check, the
  unknown-stop check, the whole-centimetre check, the extra-field check, the unknown-top-level-key check,
  the contradiction pass or the `isinstance` guard each makes at least one test fail.

## Outcome of the review round (#21)

- **What the review asked for:** one blocking point and three optional ones. `load_last` refused twice
  at the same stop, which refuses "load the toolbox and the paint cans last"; `not_stackable` with
  `max_weight_on` passing validation; a reminder that #19 must re-check the accumulated set; and a
  confirmation that `unloading_plan()` is the accessor SA-05 wants.
- **What the AI produced:** the `load_last` group rule (check removed, contract table, *Route and
  unloading order*, T26 as the test sentence, the refusal test turned into an acceptance test), the
  `not_stackable` + limit contradiction with its two tests, the C8 rubric row, and the
  `documentation/failures.md` entry on refusing a normal sentence.
- **What was changed by hand:** where T26 goes. Inserting a two-items-last sentence among the clear
  sentences would have renumbered T07–T25, and a number is a test input's identity — earlier notes and
  failure entries refer to sentences by number. It was appended as T26 with that rule written into the
  document, and the 25 counts moved to 26 everywhere instead. The C8 row was also reworded after
  writing it: the first version promised that a dropped constraint was acceptable if something was put
  in `unresolved` instead, which is not what the check does and not what C5 allows.
- **Verified:** 91 tests pass. The two new contradiction tests fail if the check is removed, and T26
  fails validation if the `load_last` change is reverted.
- **Not changed, and why:** nothing was added for the accumulated-set point. `find_problems()` already
  works on any list of constraints, so #19 has only to call it again before the solver; that was
  written on the issue rather than guessed at in code here.
