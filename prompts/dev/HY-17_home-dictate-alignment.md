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

- **PR:** https://github.com/Lpk78/quai/pull/62 (reviewer: `Lpk78`)
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

## Complement, 2026-10-02 — the real visual references

The approved screen mockups (`08_SITE_IMAGES/phone_home.png`, `phone_voice_rules.png`) arrived after
the six commits above, with an instruction to recreate both screens faithfully from them and to use
the supplied transparent van PNG rather than invent an illustration.

**The palette instruction was given, then withdrawn, and the work was reverted.** The complement
first specified colours eyedropped from the mockups — navy `#000B2B`, orange `#FD5101`, background
`#FDFDF9` — as taking precedence over `tokens.json`. That contradicts `design.md:22`, *"Never eyedrop
a mockup — read `tokens.json`"*, which the brand tests enforce. The change was applied across
`tokens.json`, the generated `tokens.css`, `design.md`'s palette and contrast tables, the logo
constants and the four regenerated logo SVGs — then withdrawn by Léo-Paul before any of it was
committed, on the grounds that repainting every screen hours before the demo is not a change to make
at night. All ten files were restored and the suite re-run green. Nothing from it survives.

Two measurements are worth keeping even though the change was reverted, because they are the reason
the decision is not free: against the deeper `#FD5101`, navy scores 5.87:1 and white 3.31:1 — so
white on orange, which fails at every size against today's `#FF8A00` (2.36:1), would pass AA for
*large* text under the sampled palette. `tests/test_brand.py::test_white_on_orange_fails_even_at_
large_sizes` asserts `< 3.0` and would have had to be restated. Whoever picks the palette up after
the demo should start there.

**What the mockups did decide:** layout, hierarchy and structure, which is all they are now taken
for. Home gained the header badge, the van card, three KPI tiles and the "Today's route" step list;
Dictate gained the mic panel with its rings and the "Your loading rules" card list.

### One thing worth the reviewer's attention

Point 6 removes real information from the screen, not just styling: the eighteen rows of box id,
label, dimensions and weight are gone, and nothing else in the app shows that list. The task asked for
exactly this and the mockup supports it, but it is the one change here a user could notice as a loss
rather than a tidy-up. `test_shows_the_operator_s_name_and_the_load_s_real_counts` now asserts `B01`
and *washing machine* are **absent**, so the removal is pinned deliberately rather than left to drift.

### The figures, and a vacuous test caught on the way

The mockups' numbers — `Van 12`, 28 stops, 124 parcels, `4h 20m` — are never copied. Stops and
parcels are counted from the manifest. `Van 12` has no source at all (the fixture has no van id; it
was invented in `HY-14` and removed again in `HY-16`), so the operator's name holds that slot.

`Est. route time` was nearly the exception. It has to come from `POST /route`, and while the round
was still the Madrid fixture that endpoint could not answer honestly: the Base Adresse Nationale
covers France, and asked for `Depot-Centro` it returned **200** with a depot in Guadeloupe and a
nineteen-hour leg — a confidently wrong number rather than an error, which is worse. The tile was
built to show an em dash for that reason. `SA-21` / #63 then moved the round to real Paris addresses,
so the figure became genuinely available and the tile now shows it: **1h 40m**, measured, with the
dash kept for in-flight and failed requests.

The first version of that tile's test was **vacuous**: it searched for `estimated route time` while
the tile is labelled `Est. route time`, so it matched nothing and passed both before and after the
tile existed. It now reads the tile's own value. Same shape as the order test in #35 and the two
`on_top` tests in #60 — a test that has never been seen to fail is a claim, not evidence.
