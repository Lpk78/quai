# SA-23 — Dressing the 3D plan screen to the mockup

- **ID**: SA-23
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/plan-screen-dressing`
- **Issue**: none — demo preparation
- **Reference**: `QUAI_DA_FINAL/08_SITE_IMAGES/phone_3d_plan.png`

## Prompt as typed

```
SA-23 Habiller l'écran du plan 3D d'après la maquette, sans toucher au rendu réel. Reviewer : Lpk78.

RÈGLE N°1 : la maquette montre une PHOTO d'intérieur de fourgon avec un contour orange. C'est un rendu
marketing. Tu ne remplaces pas le canvas 3D réel par une image. Le plan affiché doit rester celui que
le solveur a calculé. Tu reprends l'habillage autour, jamais le contenu.

GATE AVANT DE CODER : les contrôles de vue (3D / Top / Left / Right) supposent des presets de caméra.
Vérifie d'abord si le rendu 3D actuel peut les porter sans réécriture. Si oui, continue. Si ça implique
de refaire le composant 3D, arrête-toi : on livrera l'habillage sans les presets.

1. Segmented control « Load view » | « Delivery order », Load view actif en orange, Delivery order
   navigue vers /app/route. C'est un lien, pas un refactor.
2. Carte flottante « Next box » reliée par un trait au colis mis en évidence : l'arrêt, l'identifiant,
   la taille, le poids — tous lus dans le plan réel. « A-12 » : si on n'a pas ce type de référence, tu
   ne l'inventes pas, tu l'omets.
3. Contrôles de vue verticaux à droite, grandes cibles tactiles. Seulement si le gate est passé.
4. Panneau de statut « N / M loaded » + barre. La coche verte « All items placed » est CONDITIONNELLE :
   seulement si tout est réellement placé. Sinon le compte réel.
5. Bouton « Loaded, next → » câblé pour de vrai : avance un index dans l'ordre de chargement du
   solveur, met en évidence le colis suivant, met à jour la progression. Au bout, l'état final reste.

CHIFFRES : vrai compte du plan courant, colis scanné inclus. PALETTE : tokens.json, design.md:22 reste
la règle. NE TOUCHE PAS À Home.jsx. Tests et README. Dans le PR, le même tableau des écarts qu'en #63.
```

## Outcome

To be filled when the pull request is opened.
