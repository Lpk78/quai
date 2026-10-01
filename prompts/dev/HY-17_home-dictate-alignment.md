# HY-17 — Align Home and Dictate with the mockups

- **Author:** `MORHI11`
- **Date:** 2026-10-02
- **Branch:** `feature/home-dictate-alignment`
- **Issue:** none (follows the screen-by-screen discrepancy list drawn up against
  `assets/mockups/app_mockups.png` earlier tonight; `PlanScreen.jsx` was already aligned in `HY-15` / #56
  and is out of scope here)

## Prompt as typed

```
HY-17 — alignement visuel Home/Dictate sur les maquettes, un commit par point, dans cet ordre :

1. Home + Dictate : titre sur deux lignes, virgule au lieu du point ("Good morning," / "Let's load.").
2. Dictate : phrase d'exemple visible en permanence sous le micro (pas un placeholder qui disparaît quand on clique).
3. Dictate : libellé "Tap and speak" au lieu de "Tap to talk".
4. Home : tuiles de stats avec icônes pour Parcels et Stops seulement — pas de tuile "Est. route time", contraire aux règles de copy de design.md (aucune estimation de trajet annoncée).
5. Dictate : panneau/carte autour du micro avec les barres d'onde décoratives des deux côtés.
6. Home : restructurer la liste de 19 boîtes en carte-résumé compacte ("Loading plan ready" + description + un seul CTA "Start loading"), en dernier et dans un commit à part — c'est le plus gros chantier, pour que le reste soit déjà acquis si le temps manque.

À ne pas faire, et pourquoi :
- Icône avatar (Home) et icône "?" (Dictate) — aucune fonctionnalité derrière, ce seraient des éléments morts à l'écran.
- Modèle de règles ajoutées une par une avec suppression individuelle (Dictate) — c'est l'architecture réelle du produit (une phrase à la fois, accumulation de contraintes = roadmap future), pas un bug visuel à corriger ce soir.
- Image/illustration du van — pas d'images fabriquées dans l'app fonctionnelle, choix de projet déjà acté.

Lance les tests après chaque commit, pas un seul gros commit à la fin.
```

## Decisions taken before writing any code

**No new dependencies, per the existing HY-15 constraint.** The stat-tile and sound-wave icons are
inline SVG or plain CSS (gradient bars / borders), not an icon package — consistent with the rest of
`app.css`, which has used neither images nor an icon font so far.

**The box list restructuring (point 6) changes `Home.jsx`'s behaviour, not just its style.** The 19
rows currently shown are real data (`loadWith(parcel)`); collapsing them into a summary card means that
detail genuinely stops being visible on this screen, not just visually deprioritised. Flagged here
rather than decided silently: if the per-box list is still wanted somewhere, that is a new screen, not
part of this task.

**Commit 6 last and separate, as instructed**, specifically so commits 1–5 are already on `main`-bound
history if the night ends before it is reached.

## Outcome

- **PR:** (filled below once opened) — reviewer `Lpk78`
- **What the AI produced:** the six commits, one per numbered point — the two-line headings, the
  persistent `.mic-example` line, the `Tap and speak` relabel, the `.stat-tiles` markup and CSS, the
  `.mic-panel` / `SoundWave` decoration, and the Home summary card — plus five new web tests and the
  updates to the three existing assertions the changes invalidated.
- **How it was checked:** `npm test` and `python3 -m unittest discover tests` after every commit
  (101 web, 399 Python at the end, from 97 and 399). `/app` and `/app/dictate` were also rendered at a
  real 390 px viewport and read back, since none of the six points is something a jsdom assertion can
  actually see.
- **What was changed by hand:** three decisions. Writing the Dictate heading as *"Tell QUAI your /
  loading rules"* rather than inventing the mockup's own "Voice rules" title, which names a screen this
  app does not have. Leaving the `{OPERATOR_NAME} · 8 stops · 18 boxes` line in place above the new
  tiles instead of deleting it as redundant — it carries the operator's name, which the tiles do not.
  And reaching the speech-recognition branch in tests through `vi.resetModules()` plus a dynamic
  re-import, because `SpeechRecognitionImpl` is read once at module load, so a stub set afterwards
  would never be seen and the two new mic tests would have passed against the fallback path instead.

### One thing worth the reviewer's attention

Point 6 removes real information from the screen, not just styling: the eighteen rows of box id,
label, dimensions and weight are gone, and nothing else in the app shows that list. The task asked for
exactly this and the mockup supports it, but it is the one change here a user could notice as a loss
rather than a tidy-up. `test_shows_the_operator_s_name_and_the_load_s_real_counts` now asserts `B01`
and *washing machine* are **absent**, so the removal is pinned deliberately rather than left to drift.
