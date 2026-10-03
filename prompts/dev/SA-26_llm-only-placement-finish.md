# SA-26 — Finishing and merging the LLM-only placement experiment

- **ID**: SA-26
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-03
- **Branch**: `experiment/llm-only-placement` (resumed, `SA-06`'s branch, PR #38)
- **Issue**: none — finishes the experiment the README's founding claim rests on
- **Reviewer**: `MORHI11`

## Prompt as typed

```
SA-26 Finir et merger l'expérience llm-only-placement (PR #38)

Le README affirme que l'architecture repose sur le fait qu'un LLM produit des agencements plausibles
mais géométriquement invalides et non reproductibles, et renvoie vers documentation/. Cette preuve est
sur ta branche experiment/llm-only-placement, PR #38, jamais mergée. Le postulat fondateur du projet
n'est donc pas démontré dans le dépôt.

Reprends #38, rebase sur main — elle a 273 commits de retard, attends-toi à du travail — et termine-la.

Ce que l'expérience doit produire, et uniquement ce qu'elle mesure vraiment :
- le même chargement soumis au modèle seul et au solveur
- plusieurs passages du modèle sur la même entrée, pour montrer la reproductibilité ou son absence
- une vérification géométrique des agencements produits par le modèle, avec le même code de validation
  que le solveur — chevauchements, dépassements du conteneur, boîtes flottantes
- les chiffres réels obtenus, pas une conclusion écrite d'avance

Si le modèle s'en sort mieux que prévu, écris-le. Un résultat qui contredit notre postulat serait un
meilleur document qu'un résultat qui le confirme, et ce serait malhonnête de le cacher.

Le résultat va dans documentation/, et HY-23 a laissé une section vide pour lui dans
llm_failure_modes.md.

Si le rebase s'avère trop lourd ou si l'expérience ne tient pas debout, reviens me voir avant de
t'enferrer — on la documentera comme abandonnée avec sa raison, ce qui reste valorisé par la section 11.

Reviewer : MORHI11. PR normale.
```

## Outcome

To be filled when the pull request is updated.
