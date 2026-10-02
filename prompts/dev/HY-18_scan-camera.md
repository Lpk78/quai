# HY-18 — Put the camera on the package scan, reusing /login's loop

- **Author:** `MORHI11`
- **Date:** 2026-10-02
- **Branch:** `feature/scan-camera`
- **Issue:** none (follows `LP-20` / #55, which built the camera on `/login`, and `SA-17` / #54, whose
  `Scan.jsx` was written against this extraction happening later)

## Prompt as typed

```
HY-18 Câbler la caméra sur le scan de colis, en réutilisant ce qui marche déjà sur /login

Léo-Paul veut scanner le QR d'un colis à la caméra sur /app/scan, comme on le fait déjà pour le badge sur /login. Aujourd'hui /app/scan est en saisie manuelle uniquement.

GATE AVANT DE CODER : /login fait déjà caméra + décodage QR et ça fonctionne sur iPhone. Regarde si cette logique est extractible en un composant réutilisable sans réécrire Login.jsx. Si oui, continue sans me redemander. Si c'est enchevêtré au point qu'il faut refaire Login.jsx, arrête-toi et dis-le-moi : on ne touche pas à un écran de login qui marche quelques heures avant la démo.

N'INSTALLE AUCUNE NOUVELLE LIBRAIRIE. Le décodeur est déjà dans le projet puisque /login s'en sert. Si tu te retrouves à vouloir ajouter un paquet, c'est que tu as pris le mauvais chemin — reviens vers moi.

CONTRAINTE ABSOLUE : la saisie manuelle reste, visible ou à un geste. C'est le filet de la démo, et c'est ce qui rend cette tâche sans risque. Tu ne la remplaces pas par la caméra, tu ajoutes la caméra à côté. Le viseur se place au-dessus du champ existant, qui reste exactement ce pour quoi il a été construit : le recours quand l'étiquette est abîmée ou mouillée.

LES 4 TESTS CAMÉRA DE login.test.jsx SONT LE FILET DE SÉCURITÉ DE CE REFACTOR. Ils doivent continuer à passer sans la moindre modification contre le Login refactoré — caméra arrière demandée, décodage puis arrêt, permission refusée, décodeur qui jette. Si le refactor t'oblige à les toucher, c'est le refactor qui est faux, pas les tests. Tu t'arrêtes et tu me le dis.

PAUSE ET REPRISE — c'est toi qui as raison, c'est le seul comportement réellement nouveau : Login verrouille doneRef définitivement après le premier code, Scan doit pouvoir lire un colis, l'afficher, puis en lire un autre. Construis cette notion dans le composant partagé, avec une reprise explicite côté Scan. Login garde son comportement actuel de verrouillage, inchangé.

APRÈS LE DÉCODAGE : le colis décodé doit emprunter exactement le même chemin que la saisie manuelle — même fonction, même état, même ajout à la liste. Une seule source de vérité, la caméra ne fait que remplir le champ que le doigt remplissait. Si ce chemin comporte déjà une étape de confirmation, tu la gardes : une seule source de vérité vaut mieux qu'un geste économisé.

ÉCHECS, HONNÊTEMENT : permission refusée, pas de caméra, contexte non sécurisé — chacun dit ce qui se passe et renvoie vers la saisie manuelle. Le texte de repli reste propre à chaque écran, comme tu l'as relevé : celui de Login parle de la carte opérateur, celui de Scan parlera de l'étiquette. Jamais un bouton caméra qui ne fait rien, jamais un échec silencieux.

TESTS : les tests existants de scan doivent continuer à passer sans être desserrés. Ajoute la couverture du chemin de décodage avec la caméra simulée, sur le modèle de ce qui existe pour /login.

NE TOUCHE PAS À PlanScreen.jsx NI À app.test.jsx — SamDana-maker y travaille en ce moment sur #64.

Le conflit attendu sur app.css avec #62 : tu es l'auteur des deux, tu le résous toi-même, comme d'habitude.

Branche depuis main après le merge de #62. Reviewer : Lpk78. PR avec le tableau des écarts comme d'habitude.
```

## The gate, answered before any code was written

**Extractable without rewriting `Login.jsx`.** Its camera `useEffect` is 64 lines that know nothing
about what a QR code *means*: they open a camera, draw frames to an off-screen canvas, hand each one
to `jsQR`, and pass whatever string comes back to a callback. Deciding what the string *is* already
lives outside it on both screens — `readOperatorCode()` in `Login.jsx`, `identify()` in
`scan/scanCode.js`. The seam was already there; this moves the generic half behind it.

Two comments in the repository had already planned exactly this and named the file it would come
out of: `Scan.jsx` ("decoded frames once #55's `jsqr` loop is shared out of `Login.jsx`") and
`scanCode.js`. So this executes a documented intention rather than inventing a refactor.

**No new library.** `jsqr` is already a dependency; the shared component is the only thing that
imports it after this change.

## Outcome

(filled at the end)
