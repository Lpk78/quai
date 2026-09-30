# SA-05 — Solver v2: stack weight limits and stop-ordered loading

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-09-30
- **Branch:** `feature/solver-v2`
- **Issue:** #17

## Prompt as typed

```
/task SA-05 #17 Extend the solver: respect a maximum weight on top of each box and load the last
delivery stop first, following the "Route and unloading order" section of
documentation/prompt_evaluation.md and reading constraints through src/quai/constraints.py; several
load_last items at one stop form the last group and the solver orders them, and a last group covering
the whole stop means no ordering constraint (see Sam's comment on #17); the weight limit is the smaller
of max_total_weight and Container.max_weight; with tests
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/27
- **What the AI produced:** the loading order driven by the route in `src/quai/solver.py`
  (`loading_order`, `weight_cap`, `stack_limits`, `overloads`), the stack vocabulary in
  `src/quai/checks.py` (`resting_on`, `stack_below`, `weight_above`, `stack_problems`) with
  `find_problems()` extended to judge a stated `max_weight_on`, `Plan.loading_order`, and 26 new tests
  in `tests/test_solver.py` — one per rule, including the three cases Sam's comment on #17 asked for.
  Also the roadmap and journal edits and the `documentation/failures.md` entry.
- **What was changed by hand:** the important one. The first version checked a stack limit against the
  box being placed — which boxes it would rest on, and whether its weight still fitted under their
  limits. That reading is only right if a load fills bottom-up, and first fit does not: it tries the
  lowest corner first, so a later box slides into a gap under one already loaded and becomes a support
  for it. The load above was never counted. All 117 tests were green, so the bug was found by generating
  200 random loads with routes and limits and running the independent check over the results: 2 were
  invalid. The rule now has a single definition, `checks.stack_problems()`, asked of the plan a
  placement would produce; the smallest case and the sweep are both tests now.
  Two smaller ones: the explicit special case for "the last group covers the whole stop" was written and
  then deleted — the sort key already gives that no-op, so the code would have been a guard no test
  could distinguish from its absence, and the guarantee is a test instead. And the branch was created as
  `feature/solver-weight-and-stop-order` before noticing the roadmap had already declared
  `feature/solver-v2`; it was renamed rather than letting the plan and the repository drift.
- **Verified:** 134 tests pass on the branch (117 before `main` was merged in, bringing the server
  and container-validation tests with it; 26 of the 117 are new here). Each rule was mutation-tested — loading the first stop first, loading the
  last group first, dropping the `min()` on the two weight caps, and reverting the stack check to the
  candidate-only version each make at least one test fail. 400 generated loads with routes, last groups
  and stack limits produce no plan the independent check rejects.
- **Known cost, recorded rather than hidden:** ordering by the route drops the demo load's fill rate from
  39 % to 21 % once its boxes are spread over three stops, because size no longer decides what goes in
  first. That is in `documentation/roadmap.md` under the greedy first-fit limitation.
