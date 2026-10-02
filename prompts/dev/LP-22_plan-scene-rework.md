# LP-22 — Rework the load plan's 3D scene, and make it legible on a phone

- **Author:** `Lpk78`
- **Date:** 2026-10-02
- **Branch:** `feature/plan-scene-rework`
- **Issue:** none (follows `SA-14b`, which built the scene, and `SA-23` / #64, which added the camera
  presets and the progress bar this task must leave working)

## Prompt as typed

```
/task LP-22 Refondre la scène 3D du plan de chargement selon la maquette et la spec fournies

L'écran /app/plan fonctionne mais il est visuellement raté sur téléphone : le canvas n'a presque pas
de hauteur, la carte « Next box » mange le viewport, les onglets sont coupés, et les boîtes
s'affichent sans contexte visuel. Testé en vrai sur iPhone à 3h30.

LA SPEC COMPLÈTE EST DANS LA MAQUETTE ET LE TEXTE QUE LÉO-PAUL A FOURNIS. Les points qui comptent :

- Le volume de chargement devient une simple boîte 3D transparente — parois gris chaud très clair,
  arêtes fines navy, sol discret. Surtout pas de modèle de camion réaliste. Le langage visuel final,
  c'est le volume transparent plus des cuboïdes simples.
- Chaque colis est un BoxGeometry aux vraies dimensions, placé exactement aux coordonnées que le
  solveur renvoie. Le viewer ne calcule aucune position. Jamais.
- Zones de livraison colorées au sol, en transparence faible, une par arrêt. Utilise les couleurs
  delivery_stops déjà présentes dans tokens.json — elles correspondent exactement au bleu/vert/violet
  de la maquette.
- Le colis à charger ensuite porte un contour orange vif, et c'est l'objet le plus important de la
  scène.
- Aucun texte rendu dans Three.js. Tout le texte reste en HTML par-dessus, pour rester net et
  accessible.

PÉRIMÈTRE POUR CETTE NUIT — phases 1 et 2 de la spec uniquement :
Phase 1 : volume transparent + cuboïdes aux positions du solveur + caméra 3/4 fixe.
Phase 2 : highlight orange du prochain colis + tap sur une boîte + fiche de détail HTML.

Les presets de caméra (3D / Top / Left / Right) et la barre de progression existent déjà depuis
SA-23 : tu ne les refais pas, tu veilles seulement à ce qu'ils continuent de marcher.

La phase 4 de la spec — l'animation des boîtes entre deux plans — est explicitement REPORTÉE. Ne la
commence pas.

CONTRAINTE DURE : l'écran marche aujourd'hui, il affiche un vrai plan calculé. Si la refonte visuelle
ne peut pas être terminée proprement, elle doit pouvoir être abandonnée sans laisser l'écran cassé.
Un écran moche qui fonctionne vaut mieux qu'un bel écran à moitié fini — la démo est dans quelques
heures.

MISE EN PAGE MOBILE : c'est la moitié du problème. Le canvas doit occuper une vraie hauteur, la carte
« Next box » doit flotter sans écraser la scène, les onglets ne doivent pas être coupés. Vérifie à
390px de large, pas seulement sur grand écran.

PALETTE : tokens.json, comme toujours.

Reviewer : SamDana-maker, conforme à la rotation. PR avec le tableau des écarts.
```

## Decisions taken before writing any code

- **The mockup and the full spec text were not in this window.** The prompt says they were provided;
  what arrived here is the summary above. Everything below follows those enumerated points, which
  are specific enough for phases 1 and 2. What only an image can settle — exact proportions, the
  card's resting position, how much floor shows — was decided from the 390 px constraint instead, and
  every such choice is listed in the PR's table of deviations rather than presented as the mockup's.

- **The order of the commits is the hard constraint, made structural.** Each commit leaves
  `/app/plan` working on its own, and they are sequenced worst-bug-first: the mobile layout, then the
  volume, then the orange outline, then the detail card, then the delivery zones. Stopping after any
  of them leaves a screen that is better than the one before it and never a half-finished one. The
  zones are last because they are the one piece resting on derived data.

- **Delivery zones are drawn from where the boxes already are, not from an allocation.** `POST /plan`
  returns no stop per box — `PlacementOut` is `{id, x, y, z, dx, dy, dz}` — and the solver is never
  given one. `stopOf()` in `PlanScreen.jsx` already reads the stop from the manifest, so the data
  exists on the screen but not in the plan. A zone is therefore the floor footprint of the boxes that
  share a stop: a shadow of the solver's own output, not a region the plan reserved. The viewer still
  computes no position. On the eleven-box demo load, whose ids the manifest has never heard of, every
  lookup returns `null` and no zone is drawn at all, which is the right answer rather than a fallback.

- **Phase 4 is not started**, and nothing here is built to make it easier later. A seam added for an
  animation nobody has specified is a guess with a maintenance cost.

- **`SA-23`'s camera presets and progress bar are not rewritten.** `VIEWS`, `CameraPreset` and
  `LoadProgress` keep their current behaviour; the tests that hold them are expected to pass
  unmodified, and that is the check that the rework left them alone.

## Outcome

- _to fill with the pull request link._
