# SA-21 — The `/app/route` screen, and the round moving to Paris

- **ID**: SA-21
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-02
- **Branch**: `feature/app-route-screen`
- **Issue**: none — demo preparation, consuming `POST /route` from `SA-12` / #35

## Prompt as typed

```
Écran /app/route à construire de zéro — carte interactive + ordre de livraison, consommant POST /route
(déjà en prod via #35).

1. Vérifie d'abord si une lib de carte légère s'installe (leaflet + react-leaflet, gratuites, pas de
clé API) — même type de vérification que jsqr tout à l'heure, le sandbox a bloqué certains paquets
cette nuit. Si bloqué, dis-le avant d'aller plus loin.
2. web/src/pages/Route.jsx : appelle POST /route avec les 8 arrêts Madrid du manifest, dans l'ordre
donné (jamais réordonné, conforme à ce que #35 garantit déjà côté backend). Affiche la carte
(marqueurs numérotés + tracé), puis la liste des arrêts avec l'ETA réelle renvoyée par l'endpoint —
jamais une heure inventée.
3. Gère les échecs honnêtement, même pattern ApiError{kind} que Dictate.jsx/PlanScreen.jsx
(unreachable/refused/server) — pas un message générique.
4. Route ajoutée dans App.jsx (/app/route), accessible depuis Home.
5. Tests comme d'habitude, README mis à jour.
```

Followed, after the Madrid round turned out not to be geocodable:

```
On abandonne Madrid pour la démo. Décision de Léo-Paul : toute la tournée passe en France, pas de swap
de géocodeur, on reste sur Base Adresse Nationale tel quel (SA-22/Nominatim annulé).

Nouvelle tournée (8 arrêts, adresses réelles à Paris, à mettre dans web/src/data/manifest.js avec au
moins {id, name, address}) : Hôtel de Ville / Champs-Élysées / Bastille / Convention / Voltaire /
Faubourg Saint-Antoine / Saint-Germain / Opéra.

Vas-y pour le renommage complet : demo_fixtures.py, manifest.js, tout ce qui affiche les noms de
quartiers doit passer de Madrid à Paris (S1→S8), partout où ça apparaît dans l'app (home, dictée,
plan 3D, route). Pas de mélange Madrid/Paris. Pour les 3 adresses matchées au niveau rue : laisse
comme ça, montre le label BAN tel qu'il revient. Ordre des arrêts : garde S1→S8 tel quel.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/63 (reviewer: `MORHI11`)
- **What the AI produced:** the Paris round in `src/demo_fixtures.py` and `web/src/data/manifest.js`,
  `postRoute` in `web/src/api.js`, `web/src/pages/Route.jsx` and `web/src/route.css`, the route in
  `App.jsx`, the link from `Home.jsx`, fifteen tests and the README section.
- **What was changed by hand:** nothing in the committed code.
- **The blocker found before writing any screen code:** `POST /route` geocodes through the Base
  Adresse Nationale, which covers France only, so the eight Madrid stops returned a `422` that no
  front-end work could fix. Reported rather than worked around; `Lpk78` moved the whole round to Paris
  and cancelled the Nominatim swap that would otherwise have been needed.
- **The library gate, asked for first:** `leaflet@1.9.4` and `react-leaflet@5.0.0` both install, and
  the project's React 19.2 matches their peer range exactly. Nothing blocked.

### The palette measurement, kept for after the demo

The task supplied colours eyedropped from the mockups — navy `#000B2B`, orange `#FD5101`, background
`#FDFDF9` — said to take precedence over `tokens.json`. They were **not** adopted: `design.md:22` says
"Never eyedrop a mockup — read `tokens.json`", and `tests/test_brand.py` pins the documented hexes.
`Lpk78` agreed and withdrew the instruction. The measurements are kept here because the sampled
palette is genuinely better and the question will be reopened:

| Pair | tokens.json today | sampled | Verdict for the sampled set |
|---|---|---|---|
| navy on background | 14.86 | **19.02** | better |
| navy on orange (the button rule) | 6.79 | **5.87** | still passes AA at any size |
| dark orange `#C2410C` as text on background | 4.79 | **5.08** | better |
| body text on background | 13.58 | **14.40** | better |
| white on orange — what the mockups do | 2.36 | **3.31** | **still fails AA**; the rule stands either way |

Adopting it means `assets/brand/tokens.json`, a regenerated `tokens.css`, the pinned hexes in
`tests/test_brand.py` and both contrast tables in `documentation/design.md` — and it repaints every
screen. Deferred until after the demo, deliberately.

- **Verified:** 115 web tests (97 before), 399 Python tests, 1 skip, `npm run build` clean. The screen's
  exact request was run against a live server: 8 stops in order, `200`, 37.7 km, 100 min, 1753 road
  points, and absolute arrival times 08:00 → 09:40.
