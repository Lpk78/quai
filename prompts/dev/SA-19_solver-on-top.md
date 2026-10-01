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

To be filled when the pull request is opened.
