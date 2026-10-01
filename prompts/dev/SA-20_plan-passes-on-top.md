# SA-20 — `POST /plan` passing `on_top` to the solver

- **ID**: SA-20
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/plan-passes-on-top`
- **Issue**: none — the last link in the dictate-to-plan path, after `SA-19` / #60

## Prompt as typed

```
POST /plan filtre encore on_top avant d'atteindre solve() — seul load_last passe. Ajoute on_top à la
liste des types honorés côté endpoint (src/server.py, là où validate_constraints()/la liste HONOURED
décide quoi transmettre au solveur), pour qu'il arrive jusqu'à solve() au lieu de revenir en
not_applied. C'est le dernier maillon pour que "ce colis est fragile, mets-le en haut" bouge vraiment
une boîte à l'écran pendant la démo. Teste via /app/dictate → /plan en vrai, pas juste en test
unitaire — c'est le chemin que la démo emprunte.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/61 (reviewer: `MORHI11`)
- **What the AI produced:** `on_top` added to `WIRED` in `src/server.py` with the comment rewritten to
  state the test for membership, three tests replacing one stale one, the README update and the
  `documentation/failures.md` entry.
- **What was changed by hand:** nothing in the committed code.
- **The code change is one line.** Everything useful in this task came from the user's insistence on
  driving `/app/dictate` → `/plan` for real rather than unit-testing it.
- **What the real run found, and a unit test could not:** the constraint works and **changes nothing on
  the demo load.** A real Claude call turned "This parcel is fragile, put it on top." into
  `{"type": "on_top", "item": "QUAI-BOX-0001"}`, that reply went to `/plan`, `not_applied` came back
  empty — and the plan was identical with and without it. The parcel is the smallest box in the load, so
  it was already loaded last and already clear: the constraint was satisfied before it was given. On
  stage, nothing would have moved, and nobody would have known why.
- **What was done about it:** the same question asked of all seven boxes the load actually buries. Four
  give a clean visible change with 19/19 still placed and the fill rate unchanged (tv, fridge,
  dishwasher, oven); three come back unplaced because a box filling the floor has nowhere clear to go
  once it is loaded last (sofa, washing machine, wardrobe), costing 7–17 points of fill. The demo
  sentence should name one of the four — reported on the PR as the one decision left, and not a code one.
- **A second finding, unrelated:** a `uvicorn` from another session was already holding port 8000, so the
  first `/constraints` call answered `503 ANTHROPIC_API_KEY is not set` from a server nobody intended to
  test. The message was correct and the server was the wrong one. Also an unplanned field test of
  `SA-18`: a precise, CORS-carrying `503` where the night before there was a bare 500.
- **The test that had to be rewritten:** `test_on_top_is_now_a_type_the_solver_honours`, written in
  `SA-19`, asserted `on_top` came back under `#19`. That is precisely what this task changes, so it was
  replaced by three that assert what now happens — including one in a deliberately narrow container,
  with the baseline asserted to bury the box first so it cannot pass vacuously.
- **Verified:** 370 tests pass (368 before), 1 skip. Real end-to-end run against a server on a port of
  its own, both halves of the path.
