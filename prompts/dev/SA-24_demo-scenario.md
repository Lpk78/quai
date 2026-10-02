# SA-24 — A demo scenario that holds up on screen

- **ID**: SA-24
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/demo-scenario`
- **Issue**: none — demo preparation
- **Reviewer**: `MORHI11`

## Prompt as typed

```
SA-24 Rendre le scénario de démo réel : noms lisibles, colis neutre, et une contrainte qui déplace
vraiment quelque chose. Problème constaté en testant sur le téléphone. Trois défauts liés :

1. Les boîtes s'affichent avec des identifiants internes (B16, S7) incompréhensibles pour qui regarde
l'écran. Donne à chaque boîte du chargement de démo un nom humain et crédible — machine à laver,
cartons de peinture, téléviseur, etc. — en gardant l'identifiant comme donnée technique, pas comme
libellé principal.

2. QUAI-BOX-0001 arrive déjà marqué fragile. C'est faux dans le principe : la fragilité doit venir de
ce que l'opérateur dit, pas de la fixture. Donne-lui un nom neutre et banal, et retire toute marque de
fragilité de la donnée.

3. LE POINT CRITIQUE — aujourd'hui, dire « mets-la en haut » sur ce colis ne déplace rien, parce qu'il
est chargé en dernier et donc déjà dégagé. La contrainte est satisfaite d'avance. Il faut que dans le
plan de base, ce colis ait des boîtes au-dessus de lui, pour que la contrainte produise un mouvement
visible à l'écran. Ajuste la fixture (arrêt de livraison, dimensions, ordre) pour que ce soit le cas,
et prouve-le par un test : dans le plan de base, ce colis a au moins deux boîtes au-dessus ; avec la
contrainte on_top, il n'en a aucune. Si le test ne peut pas montrer les deux états, le scénario de
démo ne tient pas.

C'est le cœur de la démonstration : une phrase dite à voix haute qui déplace une boîte sous les yeux
du public. Tout le reste est secondaire. Reviewer : MORHI11. PR normale.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/69 (reviewer: `MORHI11`)
- **What the AI produced:** the parcel's new identity, size and stop in `src/demo_fixtures.py` and
  `web/src/data/manifest.js`; `labelOf` and the corrected `stopOf` in `PlanScreen.jsx` with the list and
  card rebuilt around them; nine new tests; the README section.
- **What was changed by hand:** nothing in the committed code.
- **The fixture values were searched for, not chosen.** Three sweeps over stop, dimensions and both
  loading orders. The first answer — stop 8, 55 × 85 × 40 — was wrong and a live run is what showed it:
  it buried the parcel in `demo_fixtures.plan()`, which applies the round, but **not** in what the app
  shows, because `Dictate.jsx` sends `POST /plan` only the dictated constraints and `unload_at` is not
  among the types that endpoint passes on. The plan on screen is ordered by volume. Only 65 × 85 × 85
  is large enough to be loaded early under that ordering *and* survive the constraint without being
  left unplaced; stop 1 is what keeps the route-ordered plan at 19 of 19, where stop 8 ejected two
  boxes. Both numbers are load-bearing and the fixture says so.
- **The sentence is part of the scenario.** "This one is fragile, put it on top" returns `ambiguous`
  with "Which item is fragile?" — correct, and useless on stage. "The unmarked carton is fragile, put
  it on top" returns the constraint and the box rises 85 cm. Found by running the real endpoint, not by
  reasoning about the prompt, and recorded in the README as the line to say.
- **What I broke and caught:** leading with the name made the `.plan-id` cell conditional, so it
  disappeared for unnamed boxes — the exact selector the assertions tightened on #64 read, which would
  have left them silently unable to fail. The element is always rendered now and a test covers it.
- **An assertion that had to move twice:** `SHIFTED_BY_THE_SCAN` went from two boxes to fifteen when the
  parcel was briefly a stop-8 box, then back to two at stop 1. Re-measured each time rather than
  loosened, which is how the fifteen-box version was noticed as a symptom rather than accepted.
- **Verified:** 406 Python tests (399 before), 152 web (148 before), build clean, and the full
  scenario run against a live server end to end.
