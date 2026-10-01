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

