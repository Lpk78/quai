# SA-16 — One dictated constraint reaching the plan

- **ID**: SA-16
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-01
- **Branch**: `feature/plan-constraints`
- **Issue**: none — demo preparation, ahead of roadmap row 12 (#19)

## Prompt as typed

```
SA-16 Minimal wiring to make one dictated constraint visibly affect the demo plan tonight — not the
full accumulate-and-solve design (row 12/#19), just enough for one constraint per recompute call.
Extend POST /plan/recompute's request model with an optional "constraints" field: a list of
constraint objects in the same shape parse() produces. Server-side, before calling solve(): for a
load_last constraint naming an item id, reorder that item to the end of the boxes list passed to the
solver (the solver places in list order, so this achieves "loaded last" / positioned near the door).
Ignore constraint types other than load_last for now (log a warning, don't crash) — document that
the other three honoured types aren't wired yet. Add tests: a recompute with a load_last constraint
places that item measurably differently (closer to the door / last in placement order) than the same
call without it. Keep max_total_weight and max_weight_on and unload_at untouched. 320+ tests must
stay green.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/51 (reviewer: `MORHI11`)
- **What the AI produced:** the `constraints` field and `not_applied` response field on
  `POST /plan`, the `split_constraints` / `why_not_applied` helpers in `src/server.py`, the
  `TestPlanConstraints` tests, the `documentation/failures.md` entry, and the README section.
- **What was changed by hand:** nothing in the committed code.
- **Two premises in the task that were wrong, found before writing anything:** the task named
  `POST /plan/recompute`, which does not exist — there is one planning endpoint — and it said the
  solver "places in list order", which it does not: `solve()` places `loading_order(...)`, which
  always sorts. Reversing the input list was checked against the real solver and gave a byte-identical
  plan, so the specified reorder would have shipped a no-op. `load_last` was meanwhile already in the
  solver's `HONOURED` set and already implemented, so the work was wiring a door rather than building
  behaviour. Written up in `documentation/failures.md`.
- **Judgement calls made with the user, before writing code:** two, both because they change the API
  surface MORHI11 builds against. The field went on `POST /plan` rather than a new endpoint — optional
  and backwards compatible. And unwired constraint types come back in a `not_applied` field rather
  than being logged and dropped: the task asked for a log only, but `quai.solver.refuse_unhandled`
  exists precisely so a dropped constraint cannot return as a plan the checks call valid, and a log
  line is invisible to the operator. Confirmed rather than decided alone.
- **Judgement calls made without asking:** a type outside the contract is a `422` rather than a
  `not_applied` entry, because that is malformed input and not a feature awaiting wiring;
  `constraints` is typed `list[dict]` so the shape stays `parse()`'s single responsibility, at the
  cost of no schema in `/docs`; and a single placeholder stop is synthesised because `Manifest`
  requires one — flagged on the PR, since it is a fake route entry even though nothing reads it.
- **What went wrong in my own first attempt:** the test asserted nothing twice over. It used a box the
  volume tie-break was already loading last, so `load_last` changed no order; and it used the 100 cm
  cube the other tests use, where every box stacks at `x: 0` and "nearer the doors" cannot be observed
  even when the ordering is right. Both are now deliberate, with the reason in a comment.
- **One existing test changed:** `test_empty_box_list_gives_an_empty_plan` pinned the exact response
  body, which now carries `not_applied: []`. The key was added to the expectation rather than the
  assertion loosened.
- **Verified:** 322 tests pass (311 before), 1 skip. `load_last` on the largest box moves it from
  `x: 0` and first in the load to `x: 70` and last.
