# SA-13 — Refuse a NaN weight limit, and let the API allow the zero the model allows

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `fix/container-max-weight`
- **Issue:** #26 (raised by `MORHI11` reviewing #23)

## Prompt as typed

```
/task SA-13 #26 Container: refuse max_weight=NaN (use "not max_weight >= 0") and align the API with
max_weight=0 (ge=0 instead of gt=0), with tests for both
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/41 (reviewer: `MORHI11`) — closes #26
- **What the AI produced:** the `not max_weight >= 0` guard in `src/quai/models.py`, `ge=0` on
  `ContainerIn.max_weight` in `src/server.py`, the `RequestValidationError` handler that renders
  non-finite floats as their names, and 11 tests across `tests/test_solver.py` and
  `tests/test_server.py`.
- **What was changed by hand:** two things.
  Both defects were reproduced against `main` before any code changed — the issue's own script, run as
  written — rather than trusting the report. That is also how the third defect turned up: the issue
  says `POST /plan` is safe from NaN today because pydantic's `gt` rejects it. Pydantic does reject
  it, but FastAPI echoes the offending value into the 422 and `JSONResponse` cannot serialise a NaN,
  so the request ended as a 500. Confirmed pre-existing on `main` in a clean worktree, so neither
  caused nor hidden by the `ge=0` change. Fixed here because closing #26 otherwise means closing it on
  a sentence of the issue that is false; flagged in the PR as scope the reviewer may want split out.
  The commits were also re-split after the fact: the first attempt put all three changes in one
  commit, which `CONTRIBUTING.md` §2 asks against and which would have hidden the added scope inside
  a commit about something else. Each of the three now builds and passes on its own, checked in a
  detached worktree per commit.
- **Verified:** 314 tests pass. All three guards mutation-tested — reverting to `max_weight < 0` fails
  3 tests, `ge=0` back to `gt=0` fails 1, removing the validation handler fails 1. Every value checked
  end to end: NaN, `-inf`, `-1` refused; `0`, `inf` and omitted accepted, with `0` loading nothing.
  All files parse under the 3.11 grammar.
