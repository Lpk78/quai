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

To be filled when the pull request is opened.
