# LP-11 — POST /constraints endpoint

- **ID**: LP-11
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `feature/constraint-translation`
- **Issue**: #19 (roadmap row 11)

## Prompt as typed

```
LP-11 POST /constraints in src/server.py: takes {"text": "...", "manifest": [...]} and returns the
validated ConstraintSet JSON produced by the production prompt version (v4, prefill via
prefill_of()), using src/quai/llm.py. Model claude-haiku-4-5-20251001, temperature 0. Errors: invalid
JSON from the model → 502 with a clear message, CallFailed → 503, empty text → 422. Same CORS
allowlist as /plan. Tests mock the LLM call; no real API call in CI. Document the endpoint in the
README. MORHI11's dictate screen (HY-14) calls it, so keep the response shape documented with one
example.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/46 (reviewer: `SamDana-maker`)
- **What the AI produced:** `POST /constraints` in `src/server.py`, the `TestConstraintsEndpoint`
  tests in `tests/test_server.py`, and the README section documenting the endpoint.
- **What was changed by hand:** nothing yet — the first review round will tell.
- **Judgement calls made with the user, before writing code:** the manifest item shape (id, label,
  dimensions, weight, optional `stop`) and the route shape (`stops`, required, delivery order) were
  not specified by the task text and are a contract MORHI11's `HY-14` depends on, so they were
  confirmed rather than guessed. Also deliberately out of scope for this PR, per the task: the
  multi-sentence accumulation noted as a requirement on the #19 review thread, and authentication
  (CORS reuses the `/plan` allowlist) — both flagged for the reviewer on the PR.

