# SA-06 — Measuring what happens when the LLM places the boxes itself

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `experiment/llm-only-placement`
- **Issue:** none — roadmap *Later* row `experiment/llm-only-placement`

## Prompt as typed

```
/task SA-06 Run experiment/llm-only-placement: ask Claude (LLM_MODEL from .env) to place the demo
boxes directly as coordinates, 10 runs at temperature 0 and 10 at temperature 1, score each with
src/quai/checks.py (overlaps, out of bounds, unsupported boxes, differences between runs), compare
with the solver in notebooks/llm_vs_solver.ipynb (exploration only) and document the results in
documentation/failures.md
```

## Outcome

