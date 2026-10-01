# SA-19 — Teaching the solver `on_top`

- **ID**: SA-19
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/solver-on-top`
- **Issue**: #29 (the constraint types the solver refuses rather than honours)

## Prompt as typed

```
Vas-y pour on_top, selon ta proposition en deux passes : le groupe non-on_top placé par la boucle
actuelle inchangée, puis les colis on_top placés en dernier, restreints aux positions dont le dessus
est libre (rien dans le plan ne chevauche leur empreinte à une hauteur supérieure). Le footprint
(colonne), pas le graphe de contact, pour "rien au-dessus" — même choix que pour not_stackable,
Léo-Paul confirme.

Inclus dans la même PR, comme tu l'as dit toi-même : la règle de conflit on_top + unload_at précoce
dans constraints.py (_conflict_problems), les tests qui le couvrent, et les tests qui prouvent la
propriété par construction (aucun autre colis n'est placé après, donc rien ne peut finir au-dessus).
Pas de not_stackable séparé pour l'instant — on se concentre sur on_top vu le temps qu'il reste.

Avant de merger, je veux voir ta proposition de code (pas juste les tests qui passent) — c'est le
cœur du solveur, hors de question de merger à l'aveugle cette nuit.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/60 (reviewer: `MORHI11`)
- **What the AI produced:** `covering` / `covered_problems` / `footprints_overlap` and the
  `must_be_clear` parameter in `src/quai/checks.py`; `must_stay_clear`, `last` and `buries` plus the
  two-pass order in `src/quai/solver.py`; the `on_top` conflict rule in `src/quai/constraints.py`;
  fifteen tests.
- **What was changed by hand:** nothing in the committed code.
- **Agreed with the user before any code was written**, at their request, since this is the core of the
  solver: the two-pass design, and "above" meaning the footprint column rather than the
  resting-contact graph. The diff was then read before the PR was opened, also at their request.
- **Where the instruction was not followed, and why:** the task asked for `on_top` + an early
  `unload_at` to be refused in `_conflict_problems`. It is not a contradiction — a box can ride on top
  and be reached at a later stop — and this contract refuses rather than repairs, so a false conflict
  costs the operator a whole sentence. `_conflict_problems` has no warning channel. What was added
  instead is the conflict that *is* logically identical to an existing one and was genuinely missing:
  `on_top` together with `max_weight_on` or `max_stack_height`, exactly as `not_stackable` already was.
  Raised before writing the code and flagged again on the PR.
- **The design decision inside it:** `buries()` asks its question of the whole prospective plan rather
  than of the candidate alone, copying `overloads()`. That is what catches both directions — a box
  landing *on* one that must stay clear, and a box that must stay clear landing *under* something
  already placed. Ordering alone cannot fix the second case when two boxes carry `on_top`.
- **The cost, stated rather than hidden:** `last()` is the one place `on_top` crosses the route. An
  `on_top` item for a late stop ends up near the doors instead of deep in the load. The alternative —
  leaving it where its stop puts it and blocking the column above it — holds the property too but
  wastes the space above a floor-level box. Documented in `last()` and flagged as Please-check #2.
- **A mistake worth recording:** two of the new tests were vacuous on the first attempt. With
  full-floor crates, "two `on_top` boxes do not bury each other" passed because one of them was left
  *unplaced*, so there was no violation to find. Rewritten with half-floor boxes so both genuinely fit,
  and the unplaceable case now asserts the box is in `unplaced` rather than only that no problem is
  reported. The same shape of error as the SA-16 test that used a box already loaded last.
- **Verified:** 368 tests pass (353 before), 1 skip. Through the demo fixture, "the fragile parcel goes
  on top" places it at `z=90`, loaded 19/19, nothing above, fill 78.2% — unchanged, so the constraint
  costs nothing on this load.
