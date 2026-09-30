# SA-10 — Validate Container dimensions

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-09-30
- **Branch:** `fix/container-validation`
- **Issue:** #15

## Prompt as typed

```
SA-10 #15 Validate Container dimensions: refuse zero or negative sizes and a negative max weight in __post_init__, like Box, and make Plan.fill_rate safe for a zero-volume container, with tests
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/23
- **What the AI produced:** `Container.__post_init__` (sides > 0, `max_weight` >= 0), the zero-volume guard in
  `Plan.fill_rate`, and 7 tests. The guard test was checked to fail without the guard.
- **What was changed by hand:** nothing so far.
