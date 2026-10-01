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

To be filled when the pull request is opened.
