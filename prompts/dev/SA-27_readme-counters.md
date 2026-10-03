# SA-27 — Re-measuring the README's counters after the merges

- **ID**: SA-27
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-04
- **Branch**: `docs/readme-counters`
- **Issue**: none — follows the second review comment on #76
- **Reviewer**: `MORHI11`

## Prompt as typed

```
/task SA-27 Re-mesurer les compteurs du README après tous les merges

Le README cite plusieurs nombres que la série de merges de cette nuit a rendus faux. Tu en avais déjà
repéré un en relisant #76 : il annonce 49 fichiers dans prompts/dev/ dont 20 en LP-, alors que le
commit 825e164 de cette même PR en faisait déjà 50 et 21.

Depuis, #74, #75, #38, #78 et #80 ont toutes atterri : le nombre de tests est passé à 456 côté
Python, et le nombre de PR mergées, d'entrées de failures.md et de fichiers de tâche a encore bougé.

Reprends chaque nombre chiffré du README et re-mesure-le sur main, par commande et jamais de mémoire.
Corrige ceux qui ont dérivé.

Et tranche une fois pour toutes : un compteur qui périme à chaque merge mérite-t-il d'être dans le
README ? Pour ceux qui ne servent pas directement à comprendre le projet, une formulation durable
vaut mieux qu'un chiffre exact aujourd'hui et faux demain. C'est ton arbitrage — dis ce que tu as
choisi et pourquoi.

Reviewer : MORHI11. PR normale.
```

## Outcome

To be filled when the pull request is opened.
