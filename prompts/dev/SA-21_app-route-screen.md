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

To be filled when the pull request is opened.
