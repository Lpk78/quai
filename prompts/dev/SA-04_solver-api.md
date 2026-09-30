# SA-04 — FastAPI server exposing the solver

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-09-30
- **Branch:** `feature/solver-api`
- **Issue:** #6 (plan endpoint only)

## Prompt as typed

```
SA-04 Build a FastAPI server in src/server.py exposing the solver: POST /plan takes boxes and a container and returns placements, fill rate and unplaced boxes; add tests and the run command to the README
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/16
- **What the AI produced:** `src/server.py` (`POST /plan` with input validation), `tests/test_server.py` (10 tests,
  mutation-checked), the dependencies, and the README run section with a real `curl` response.
- **What was changed by hand:** nothing yet. The scope was narrowed to the plan endpoint; the translation endpoint
  from #6 waits for #10 and #12.
