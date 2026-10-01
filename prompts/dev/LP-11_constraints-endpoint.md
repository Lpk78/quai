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
- **What was changed by hand:** nothing — the PR went to review as drafted.
- **Judgement calls made with the user, before writing code:** the manifest item shape (id, label,
  dimensions, weight) and the route shape (`stops`, required, delivery order) were not specified by
  the task text and are a contract MORHI11's `HY-14` depends on, so they were confirmed rather than
  guessed. An optional `stop` was confirmed as part of that shape too, then dropped in the first
  review round (`00acea0`) once it turned out to never reach the model past validation — deferred to
  a v5 prompt version rather than wired in here. Also deliberately out of scope for this PR, per the
  task: the multi-sentence accumulation noted as a requirement on the #19 review thread, and
  authentication (CORS reuses the `/plan` allowlist) — both flagged for the reviewer on the PR.

## Outcome of the review round (#46)

- **What the review asked for:** one blocking point and two optional ones. `ManifestItemIn.stop` was
  validated but never reached the model — `_ManifestEntry` and `llm.manifest_block` carry no stop
  column, so a documented input had no effect; the prefill wiring at the `_translate` seam was the
  one thing untested; and two commits (`ecf0b8a`, `847b82f`) open with "This commit will…" instead of
  completing it, with `847b82f` also bundling two unrelated changes.
- **What the AI produced:** `00acea0` drops `stop` from `ManifestItemIn`, its now-dead "unknown stop"
  validation, the matching test, and the README paragraph documenting it. `63ab54b` adds
  `TestTranslateSeam`: `CONSTRAINT_PREFILL == "{"`, and a test patching `llm.from_env` that checks the
  `Translator` handed to `.translate()` carries that prefill.
- **What was changed by hand:** none — both commits matched the reviewer's own suggested fix.
- **Verified:** 320 tests pass (up from 319), 1 skip. The new prefill test was checked to fail
  against the pre-fix `_translate` (`AssertionError: None != '{'`), with the fix reverted and
  restored for the check.
- **Not changed, and why:** the commit-message reword (`ecf0b8a`, `847b82f`) was left alone — fixing
  it means rewriting already-pushed commits and a force-push, which the reviewer's own suggestion
  flagged as not worth doing for a cosmetic fix on its own.

