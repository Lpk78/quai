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

To be filled when the pull request is opened.
