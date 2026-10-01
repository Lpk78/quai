# SA-18 — `/constraints` answering clearly when the LLM is not configured

- **ID**: SA-18
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `fix/constraints-config-errors`
- **Issue**: none — found in end-to-end retesting the night before the demo

## Prompt as typed

```
src/server.py — /constraints : llm.from_env() peut lever MissingKey/MissingModel, pas seulement
CallFailed, et ces deux-là remontent comme une exception non gérée → 500 par défaut de FastAPI, sans
en-têtes CORS → le navigateur le rapporte comme "impossible de joindre le serveur" au lieu du vrai
problème. Attrape-les explicitement à côté de CallFailed, renvoie un 503 avec un message clair
(ex. "LLM not configured — check ANTHROPIC_API_KEY"), même format que le traitement existant de
CallFailed. Petit fix, mais blocking pour la démo : si la clé a le moindre souci demain, le message
actuel pointe droit vers un redémarrage d'uvicorn qui ne réglera rien.

Donne-lui un ID (LP-22 ou SA-18, à toi de choisir), review croisée comme d'habitude, et merge avant
de couper les serveurs ce soir.
```

`SA-18` rather than `LP-22`: `src/server.py` is the server, which is `SamDana-maker`'s area in
`CLAUDE.md`, so the ID takes that prefix and the review goes to `MORHI11`.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/59 (reviewer: `MORHI11`)
- **What the AI produced:** the two new `except` clauses in `src/server.py`, three tests, the
  `documentation/failures.md` entry and the README mapping.
- **What was changed by hand:** nothing in the committed code.
- **Verified before writing anything, rather than taken on trust:** each exception was driven through
  the real endpoint with the CORS origin header set. `MissingKey`, `MissingModel`, a bare
  `NotConfigured` and `FatalCall` all answered `500` with **no** `access-control-allow-origin`, while
  the already-handled `CallFailed` answered `503` with it. That is the whole bug: the status was the
  smaller half, and the missing header is what turned it into "could not reach the solver" on screen.
- **Two ways the task's framing understated it, both found by reading `llm.py` rather than the report:**
  `MissingKey` and `MissingModel` share a base class, `NotConfigured`, which is also raised directly
  for a missing `anthropic` package — so catching the base covers three cases and anything added later,
  where naming the two subclasses would have left the third. And `FatalCall` was uncaught too: a key
  that is *present but wrong* passes `from_env` and is refused by the API, which is the likelier
  failure on a machine that has an `.env` at all.
- **The decision nobody asked for:** `FatalCall` answers `502` rather than `503`, so that `503` means
  "this server cannot do the work" and `502` means "the upstream answered unusably" — the sense the
  endpoint's existing validation `502` already carried. Flagged on the PR as mine to defend.
- **Deliberately not done the night before a demo:** the shape of the problem is that *any* future
  unhandled exception here has the same consequence. An exception handler, or CORS placed so it wraps
  the error path, would fix the class rather than these five cases. Raised on the PR as an issue to
  open rather than a commit to make tonight.
- **Independently found by `MORHI11` and `Lpk78` in the same evening's retesting**, which is the
  argument for retesting a path end to end after the screens around it change.
- **Verified:** 352 tests pass (349 before), 1 skip.
