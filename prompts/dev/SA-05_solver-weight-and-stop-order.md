# SA-05 — Solver v2: stack weight limits and stop-ordered loading

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-09-30
- **Branch:** `feature/solver-weight-and-stop-order`
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

