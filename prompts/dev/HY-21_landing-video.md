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

## The button already existed, and was promising something it did not have

The hero already had a secondary CTA beside *Get started*: **Watch the film**, with a play icon,
linking to `#how-it-works` — a section of prose and a phone screenshot. It promised a film and
delivered a scroll.

So no third button was added. The one that was there now does what it said, which is a smaller change
and a more honest page than adding *See how it works* next to *Watch the film*. The task's wording —
"du type" — reads as illustrative rather than literal, and "Watch the film" is the clearer label for
a film.

## Not autoplaying is only half of not imposing 3.2 MB

The instruction was about weight, not just about motion, and the two are separate attributes.
`autoplay` being absent stops it *playing*; it does not stop it *downloading*. A `<video>` left at a
browser's default `preload` fetches metadata, and `preload="auto"` fetches the whole file — either
would put the 3.2 MB on every phone that opens the landing page without anyone asking to watch
anything.

`preload="none"` is the attribute that actually honours the instruction, and it is the one the test
asserts and the one that was mutation-tested. Measured in the browser rather than argued: on a fresh
load the Resource Timing API reports **0 requests and 0 bytes** for `quai-video.mp4`, `networkState`
is idle and `readyState` is `HAVE_NOTHING`. After the button is pressed, `networkState` becomes
`NETWORK_LOADING`. What the visitor pays for until then is the 44 KB poster.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/73 (reviewer: `SamDana-maker`)
- **What the AI produced:** the poster extraction and conversion, the `<figure class="film">` block
  and `playTheFilm` in `sections.jsx`, the `.film` styles, and the ten tests in
  `web/src/pages/landingVideo.test.jsx`.
- **How it was checked:** `npm test` and `python3 -m unittest discover tests` after the change (188
  web, up from 178; 409 Python, untouched). Then in a real browser at 390 px: the poster renders
  instead of a black rectangle, the 16:9 box is reserved before any bytes arrive, native controls are
  present, and the zero-bytes-until-asked measurement above. The `preload="none"` assertion was
  mutation-tested — set to `auto`, it fails with `expected 'auto' to be 'none'`.
- **What was changed by hand:** three decisions. Reusing the existing button instead of adding a
  second one. Choosing `preload="none"` as the thing to assert, because "no autoplay" alone would
  have satisfied a careless reading of the task while still shipping the megabytes. And using
  `qlmanage` rather than installing a video toolchain for one frame.

### What could not be verified here, and must be

**No frame of this video was decoded in a browser during this task.** The automated Chrome available
in this session fetched all 3 271 684 bytes in 99 ms with the correct `video/mp4` type and then
produced no metadata — not from the URL and not from an in-memory blob — with `v.error` null
throughout. That is the signature of a Chromium build without H.264, which is proprietary and
routinely omitted; `canPlayType` answering "probably" is advisory and is known to overstate it.

The file itself is sound: macOS decoded it to produce the poster, and `mdls` read its duration and
dimensions. The dev server delivers it correctly, including `206` on range requests, which is how a
player actually fetches. Every link in the chain is verified except the last one, and the last one
needs a human pressing play in Safari or a normal Chrome.
