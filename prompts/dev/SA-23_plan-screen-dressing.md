# SA-23 — Dressing the 3D plan screen to the mockup

- **ID**: SA-23
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/plan-screen-dressing`
- **Issue**: none — demo preparation
- **Reviewer**: `Lpk78` by one-off swap — the rotation in CLAUDE.md puts `MORHI11` on
  `SamDana-maker`'s PRs, but `MORHI11` was mid-`HY-17` (#62, the Home and Dictate alignment) and a
  review here would have interrupted both visual screens. The rotation is unchanged; this is the
  exception, recorded so that the documented rotation and the practised one do not diverge without a
  trace.
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

- **PR:** https://github.com/Lpk78/quai/pull/64 (reviewer: `Lpk78`, since `MORHI11` is on `HY-17`)
- **What the AI produced:** `VIEWS` and `CameraPreset` in `web/src/plan/LoadScene.jsx`; the view
  switch, Next box card, view controls and progress panel in `web/src/pages/PlanScreen.jsx`; the
  stylesheet additions in `web/src/plan.css`; fifteen tests; the README section.
- **What was changed by hand:** nothing in the committed code.
- **The gate, answered before writing anything:** the task asked whether the existing 3D view could
  carry camera presets without a rewrite. It can — `@react-three/fiber` 9.8.1 exports `useThree` and
  drei 10.7.9's `OrbitControls` is `forwardRef`-able, so a preset is one component rendered inside the
  existing `<Canvas>` plus a `view` prop. The meshes, scaling, lighting and selection are untouched.
- **What the mockup asked for and did not get, and why:** the photograph of a loaded van (a marketing
  render — the canvas keeps drawing the solver's plan), `A-12` (a storage reference we hold nowhere),
  `Medium` (a size bucket we do not have, so the real centimetres are shown), the leader line from the
  card to the box (a line pointing at nothing is decoration pretending to be information), `124 / 124`
  (the real count of the plan in hand), white on orange (2.36:1, fails AA at every size) and the `?`
  button (no behaviour defined). Each is listed on the PR with its reason, as `#63` did.
- **The conditional that matters:** `All items placed` renders only when `unplaced` **and**
  `not_applied` are both empty; otherwise the real counts appear. Three tests hold it, including one
  that puts an unapplied rule on a perfectly placed load and asserts the tick stays away.
- **What `Loaded, next` actually does:** advances an index through `plan.placements`, which *is* the
  solver's loading order, so the button is reading the plan rather than inventing a sequence. It stops
  at the end instead of looping.
- **Three test files needed updating, all for the same honest reason:** the next box's id now appears
  in the card as well as the list, so `getByText(id)` found two. The `@react-three/fiber` mocks also
  gained a `useThree` stub, without which the preset's effect threw and the whole screen rendered
  empty.
- **One of those updates loosened an assertion rather than scoping it, and the PR description said
  otherwise.** `app.test.jsx` went from `getByText("B18")` — exactly one, anywhere — to
  `getAllByText("B18").length > 0`, which pins neither how many nor which nor where. `plan.test.jsx`
  was scoped, but by `text.includes(id)` over the whole row, a substring match that would pass for a
  partial id. Caught by `Lpk78` in review of #64, who checked the diff against the description rather
  than taking the description's word. Both now read the `.plan-id` cell and compare it whole, and
  both were mutation-tested: a wrong box and a truncated id each fail. The lesson is not about the
  assertions — it is that a description claiming a diff says something is worth exactly nothing
  unless someone opens the diff.
- **Verified:** 130 web tests (115 before), 399 Python tests, 1 skip, `npm run build` clean.
  `Home.jsx` untouched, as asked — `MORHI11` is rewriting it.
