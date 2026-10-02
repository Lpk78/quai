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

To be filled when the pull request is opened.
