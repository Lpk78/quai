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

## Outcome of the review round (#51)

- **What the review asked for:** one blocking point from `MORHI11`. `split_constraints` checked a
  constraint's `type` against the contract and nothing else, so a known-but-unwired type was sorted
  into `not_applied` without its shape ever being validated —
  `{"type": "max_weight_on", "item": "does-not-exist", "bogus_field": 123}` came back `200` with all
  three faults echoed into the response. Reported instead of refused, which is the one thing the
  stated contract says must not happen, on the only path that did not enforce it.
- **What the AI produced:** `2a467c5`. A `validate_constraints` step that runs before anything is
  applied *or reported*, asking `quai.constraints.find_problems` rather than re-implementing the
  rules — so missing fields, undeclared fields, unknown types, items outside the load, non-finite or
  non-positive limits and contradictions are all caught by the contract's own code. Plus
  `validation_stops`, four new tests, and the README paragraph that had understated the rule as
  applying only to unknown types.
- **The tension the reviewer named, and how it was resolved:** a full `parse()` over the whole list
  collides with `PLAN_ROUTE_STOP`, because any `unload_at` naming a real stop would fail validation
  against a manifest holding only the placeholder. Rather than the narrower item-existence check he
  offered, the validation manifest is given the placeholder *plus* every stop the request names. That
  makes the stop check structural — it still catches a stop that is missing, empty or not a string —
  and honest about what it cannot check, since no route exists here to check against. Nothing is
  ordered by that list: `unload_at` is reported, never passed to `loading_order`.
- **What was changed by hand:** nothing in the committed code.
- **Also in this round:** `#46` merged while the fix was being written, so `origin/main` was merged in
  and the three-way conflict I had predicted on the PR — `README.md`, `src/server.py` and
  `tests/test_server.py`, since both PRs add to the same regions — was resolved by keeping both sides
  (`3313e80`). Verified afterwards that all five test classes, both endpoints and #46's rewritten CORS
  comment survived.
- **Verified:** 336 tests pass (322 mine, plus the 10 that arrived with #46), 1 skip. `MORHI11`'s
  payload now returns `422` naming all three faults, and a well-formed `unload_at` still returns `200`
  with the constraint reported — the line that had to hold.
