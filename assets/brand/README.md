# QUAI — art direction

Every image in this folder was produced with generative AI. The repository used to show the results —
a landing page, a styled app, a 32-second film — without saying where any of it came from, which left
a whole strand of our AI usage invisible. This is the index: what each piece is, what it was used
for, and which tool made it.

**Some assets were retouched by hand after generation.**

| Tool | What it produced |
|---|---|
| **ChatGPT** | The logo, the brand kit, the characters, the vehicles, the environments, the screen mockups, the component sheets and the isolated renders — everything in `art/` below, and `logo/`. |
| **Claude** | The 32-second explainer film on the landing page, `web/public/quai-video.mp4`. |

No other tool produced anything here. One was prepared and not used — see *A path prepared and
abandoned*, below.

---

## The four screen mockups

`art/mockup-01-home.webp` · `art/mockup-02-voice-rules.webp` · `art/mockup-03-load-plan-3d.webp` ·
`art/mockup-04-route-delivery-order.webp` — ChatGPT.

The reference for `/app`, `/app/dictate`, `/app/plan` and `/app/route`: layout, hierarchy and
structure.

**They are worth more for what we refused to take from them than for what we took**, and that is the
part a reader should not have to reconstruct. A mockup is a drawing, and a drawing can show a number
nobody measured or a feature nobody built. Three pull requests carry departure tables saying exactly
where the implementation parts company with the drawing, and why:

| What the mockup shows | What shipped | Where the reasoning is |
|---|---|---|
| **124 parcels, 28 stops, `4h 20m`** | The manifest's real counts, and a route time measured by `POST /route` — an em dash while it is unknown | [#63](https://github.com/Lpk78/quai/pull/63), [#72](https://github.com/Lpk78/quai/pull/72) |
| **"2 parcels · Rear doors"** per stop | The real parcel count only. Nothing in the manifest describes a door, so no door is named | [#63](https://github.com/Lpk78/quai/pull/63) |
| A **photograph of a van interior** with an orange outline | The actual 3D canvas the solver's plan renders into. The marketing render was never allowed to stand in for a computed plan | [#64](https://github.com/Lpk78/quai/pull/64), [#72](https://github.com/Lpk78/quai/pull/72) |
| **`A-12`**-style position labels | The real coordinates the solver returns | [#64](https://github.com/Lpk78/quai/pull/64) |
| `Edit`, `+ Add a rule`, a `?` help icon, an avatar | Omitted — none has behaviour behind it, and a control that does nothing is the interface version of a claim we cannot back | [#62](https://github.com/Lpk78/quai/pull/62) |

The mockups are therefore evidence twice over: of the art direction, and of the discipline applied to
it.

## Component sheets

`art/ui-kit-01-app-components.webp` · `art/ui-kit-02-voice-components.webp` ·
`art/ui-kit-03-plan-route-components.webp` — ChatGPT.

Buttons, cards, tabs, pills and states, drawn as sheets. They informed `web/src/app.css` and
`web/src/landing.css` — the pill buttons, the generous card radii, the segmented control on the plan
screen. Colour did **not** come from here: `assets/brand/tokens.json` is the source for that, and
`documentation/design.md` says why a sampled pixel is not a token.

## Isolated renders

All ChatGPT, all cut out on transparency:

| File | What it is | Where it was used |
|---|---|---|
| `art/render-van-open-loaded.webp` | The van, open and loaded, in profile | The same subject as the landing page's `van-side.png` card |
| `art/render-operator.webp` | The recurring operator character | Landing page figures |
| `art/render-forklift.webp` · `art/render-pallet-jack.webp` | Dock equipment | Landing page and film |
| `art/render-box-quai.webp` | A QUAI-marked parcel | Landing page |
| `art/render-pin-active.webp` · `art/render-pin-inactive.webp` | Map pins, two states | The round screen's visual language |
| `art/render-button-start-loading.webp` · `art/render-tabs-load-view.webp` · `art/render-mic-button.webp` | Single controls, rendered | Reference for the real CSS controls, which are built from tokens rather than from these images |
| `art/app-icon-dark.webp` | The app icon on a dark ground | Icon reference; the shipped icon is the vector in `logo/` |

The last row is the rule for all of them: these are **reference**, not assets the app loads. The
interface draws its own controls from `tokens.css`. The one generated image the product actually
ships is the van on the landing page.

## Boards, characters, world

| File | What it is | Tool |
|---|---|---|
| `art/master-brand-board.webp` | The master board — the visual source of truth the rest was generated against | ChatGPT |
| `art/characters-main-operator.webp` | The recurring operator, as a consistency reference | ChatGPT |
| `art/characters-secondary.webp` | Secondary characters | ChatGPT |
| `art/objects-and-vehicles.webp` | Forklift, truck, boxes | ChatGPT |
| `art/environments.webp` | Warehouse and delivery world | ChatGPT |

## Storyboards

`art/storyboard-film.webp` — the shot plan for the explainer film. `art/storyboard-delivery.webp` —
the delivery story. Both ChatGPT.

The film that shipped (`web/public/quai-video.mp4`) was generated by **Claude** from this direction.

## Tokens, as drawn

`art/tokens-colour-palette.webp` and `art/tokens-typography.webp` — ChatGPT.

Presentation sheets. **They are not the source.** `assets/brand/tokens.json` is, `web/src/tokens.css`
is generated from it, and `tests/test_brand.py` fails the build if the palette stops satisfying the
contrast rules in `documentation/design.md`. Reading a colour off these PNGs is the mistake that
document specifically warns against — a compressed swatch lands a few units from the real token.

## Brand guide — asked for, and deliberately not committed

`09_GUIDE/QUAI_FINAL_Brand_Guide.pdf` (4.8 MB, ChatGPT) was on the list for this folder and is **not
here**, because the repository already decided against it and enforces the decision.
`documentation/design.md` says:

> The 4.8 MB brand guide PDF from the original pack is deliberately not in this repository. It is a
> rendering of everything above and would be the largest file we own.

and `tests/test_brand.py::test_the_heavy_brand_guide_pdf_is_not_in_the_repository` asserts
`list(ROOT.rglob("*.pdf")) == []`, so committing it fails the build.

That reasoning is *stronger* now than when it was written, not weaker: the palette, the typography,
the characters, the environments and the master board were exactly what the guide rendered, and this
folder now carries each of them individually as WebP. The PDF would have added 4.8 MB — more than
everything else here combined — to duplicate content that is now present in a better form.

Reversing it is a decision for `Lpk78`, who owns `design.md`, not something to slip past a test.

---

## Demo QR codes — `demo-qr/`

**Without these, the demo cannot be replayed from a clone.** Both screens read a QR code, and neither
code was in the repository.

| File | Encodes | Screen | What it does |
|---|---|---|---|
| `demo-qr/demo-qr-operator-badge.png` | `QUAI:OPERATOR:QUAI-OP-7842` | **`/login`** | The operator's badge. Signs Léo-Paul in and opens the app |
| `demo-qr/demo-qr-parcel-label.png` | `QUAI:BOX:QUAI-BOX-0001` | **`/app/scan`** | The label on the parcel scanned on stage. Adds the carton to the load, so `/app/dictate` plans nineteen boxes rather than eighteen |

**Both kept as PNG, deliberately.** Everything else here is WebP for weight; a recompressed QR code
can stop scanning, and these two are the ones that have to work in front of an audience.

**Both strings were decoded from the images rather than transcribed**, and checked against what the
app actually accepts:

- `QUAI:OPERATOR:QUAI-OP-7842` satisfies `CODE_PATTERN` in `web/src/pages/Login.jsx:28` and matches
  `OPERATOR_CARD_ID` in `web/src/data/manifest.js:17`.
- `QUAI:BOX:QUAI-BOX-0001` satisfies `LABEL` in `web/src/scan/scanCode.js:15` and matches the
  `SCANNED_PARCEL` id in `web/src/data/manifest.js:94`.

To replay the demo: serve the app over HTTPS (README, *Phone demo* — the camera needs a secure
context), open `/login` and show the badge, then `/app/scan` and show the label. The typed field on
both screens is the fallback if the camera will not cooperate.

---

## A path prepared and abandoned

`higgsfield_workflow_not_used.txt` is a ten-shot method written for Higgsfield: clean reference
images from the master board, then shot-by-shot generation for the website film.

**It was not used.** The film that ships came from Claude. The file is kept because a route prepared
and then abandoned is part of how the work actually went, and deleting it would make the process look
tidier than it was. Nothing in QUAI was produced with Higgsfield.

---

## What is not here

`device-frame-blank.png` (an empty iPhone frame), `logo-glow-dark.png` (a blurred variant), the
`_doublons/` and `_to_delete/` folders, and the successive `landing_refs` variants were all left out
deliberately: they are working residue rather than art direction, and a folder that keeps everything
indexes nothing.

The logo itself lives in [`../logo/`](../logo/) as vector, and is traced from its sheet by
`logo/build_logo.py` with a fingerprint test so it cannot be hand-edited. The supplied renderings in
[`../reference/`](../reference/) are mood and UI references from the original pack, and
`documentation/design.md` explains why they are references rather than specifications.
