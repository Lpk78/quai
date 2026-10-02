# HY-21 — Put the explainer video on the landing page

- **Author:** `MORHI11`
- **Date:** 2026-10-02
- **Branch:** `feature/landing-video`
- **Issue:** none (adds to the landing page built in `HY-06` / #34 and `HY-12` / #42)

## Prompt as typed

```
HY-21 Câbler la vidéo d'explication sur la page d'accueil du site

Léo-Paul a fait produire une vidéo motion design de 32 secondes qui explique le fonctionnement de QUAI. Elle est sur son Mac sous le nom quai-video.mp4 — cherche-la, probablement dans ~/Downloads ou dans ~/Downloads/QUAI_DA_FINAL. H.264, 1920x1080, 30 fps, 3,3 Mo.

Copie-la dans web/public/ et câble-la sur la page d'accueil du site (Landing.jsx).

COMPORTEMENT : un bouton secondaire clairement libellé, en anglais, du type "See how it works", à côté du CTA principal sans le remplacer. Au clic, la vidéo se lance. Pas de lecture automatique : 3,3 Mo imposés à chaque visiteur mobile sans qu'il l'ait demandé, c'est le genre de décision qu'on ne prend pas à sa place.

Prévois une image d'affiche (poster) pour que le lecteur ne soit pas un rectangle noir avant lecture — une frame de la vidéo suffit, extraite avec ffmpeg.

Contrôles natifs visibles, et la vidéo doit rester lisible et jouable sur téléphone comme sur grand écran. Vérifie à 390px de large.

Si la vidéo ne se trouve pas sur le disque, dis-le-moi plutôt que d'en chercher une autre ou d'en fabriquer un substitut.

Reviewer : SamDana-maker. PR normale.
```

## The file was found, and checked before it was copied

`~/Downloads/quai-video.mp4`, and it is the one described rather than a near-match — four other
QUAI videos sit in the same tree (`QUAI_Brand_Film_FINAL_16x9.mp4`, `QUAI_Brand_Film_REWORK_16x9.mp4`,
`10_HERO_VIDEO/quai-hero.mp4`, `quai-hero-720.mp4`), so the name was matched exactly rather than
"close enough". Verified with `mdls` before copying: H.264, 1920 × 1080, 32 s, 3 271 684 bytes.

## No ffmpeg on this machine, and none installed for one frame

The task says to extract the poster with `ffmpeg`. It is not installed — not on `PATH`, not in
`/opt/homebrew/bin`, not in `/usr/local/bin` — and installing a video toolchain to pull a single
still is a large change to someone's machine for a small need.

macOS already ships the capability: `qlmanage -t -s 1920` renders a Quick Look thumbnail and returned
a full 1920 × 1080 frame. It also picks a *representative* frame rather than frame 0, which is better
than what was asked for: frame 0 of a motion-design piece is usually a blank or fading-in title, and
the frame it chose is the "Scan every parcel." panel — on-brand, legible, and recognisably this
product. The PNG it emits is 1.2 MB, so it is converted to WebP for the page.

## Outcome

(filled at the end)
