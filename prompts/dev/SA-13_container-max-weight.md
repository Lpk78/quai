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

