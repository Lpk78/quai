# QUAI design system

The visual identity of QUAI: what the colours and fonts are, how the logo may be used, what the
illustrations look like, and the rules the interface follows. It is written for whoever builds the web
app (#18), the 3D view (#7) and the box form (#8), so that three people styling three screens end up
with one product.

**Principle:** *People talk. We load.*
**Personality:** human, calm, precise, optimistic.

## Where the truth lives

| File | What it is | Normative? |
|---|---|---|
| `assets/brand/tokens.json` | The colour, type and personality tokens, machine-readable | **Yes** |
| `documentation/design.md` | This document: the rules for using them | **Yes** |
| `assets/brand/logo/*.svg` | The logo and app icon, vector | **Yes** |
| `assets/brand/reference/*.png` | Mood, character, vehicle, environment and UI renderings | No — reference only |

The images in `reference/` are renderings, not specifications. Their swatches are anti-aliased and
compressed: sampling a pixel out of `colour-palette.png` gives values a few units away from the real
token (`#FB830C` where the token is `#FF8A00`). **Never eyedrop a mockup — read `tokens.json`.**

The 4.8 MB brand guide PDF from the original pack is deliberately not in this repository. It is a
rendering of everything above and would be the largest file we own.

## Colours

### Core

| Token | Hex | Use |
|---|---|---|
| `background` | `#F7F6F3` | Page background. Warm off-white, never pure white |
| `surface` | `#FFFFFF` | Cards, sheets and anything that sits on the background |
| `text` | `#1F2937` | All body text |
| `primary_safety_orange` | `#FF8A00` | The action colour: primary buttons, the microphone, the selected state |
| Navy | `#102238` | The logo's dock, dark surfaces, and **all text placed on orange** |

Navy `#102238` is in the logo and the app icon but not in `tokens.json`. It is a real part of the
identity and this document treats it as one; adding it to the token file is a job for whoever next
edits the kit.

### Status

| Token | Hex | Meaning |
|---|---|---|
| `success` | `#16A34A` | The plan is valid, the box is loaded |
| `warning` | `#F59E0B` | Something needs a decision — an unresolved constraint |
| `error` | `#EF4444` | Refused input, an impossible load |

### Kraft / box tones

`#D7B899`, `#B8936B`, `#8B6F47` — cardboard and pallets in the 3D view and the illustrations. They are
surface colours for objects, never interface colours.

### Delivery stops

`#2563EB` (stop 1), `#059669` (stop 2), `#7C3AED` (stop 3), `#DC2626` (stop 4) — one hue per stop on the
map, the 3D view and the loading list, in route order.

The kit labels this set colour-blind safe. Stops 2 and 4 are a green and a red, which is the one pair
that deuteranopia and protanopia collapse. **Colour never carries the stop on its own:** every stop is
also labelled with its number or its id. Colour is a second channel, never the only one.

## Accessibility

Contrast is a rule here, not a preference. The target is **WCAG 2.1 AA**: 4.5:1 for body text, 3:1 for
text at 24 px or 19 px bold and above. Measured against `background` `#F7F6F3` unless stated.

| Combination | Ratio | Verdict |
|---|---|---|
| `text` `#1F2937` on background | 13.58:1 | Passes AAA |
| Navy `#102238` on background | 14.86:1 | Passes AAA |
| `text` `#1F2937` on surface `#FFFFFF` | 14.68:1 | Passes AAA |
| **Navy `#102238` on orange `#FF8A00`** | **6.79:1** | **Passes AA at any size** |
| ~~White `#FFFFFF` on orange `#FF8A00`~~ | 2.36:1 | **Fails AA at every size** |
| ~~Orange `#FF8A00` as text on background~~ | 2.19:1 | **Fails AA at every size** |
| **Dark orange `#C2410C` as text on background** | **4.79:1** | **Passes AA** |

Two rules follow, and they override the mockups:

1. **Text on orange is navy `#102238`, never white.** The UI renderings in `reference/mobile-ui.png`
   show white text on the orange "Get started" and "Loaded, next" buttons. That combination is 2.36:1
   and fails at every size. The renderings are wrong; this rule wins.
2. **Orange is a fill, not a text colour.** For orange *text* — a link, a small label, a caption — use
   `#C2410C`. `#FF8A00` may be a background, a border, an icon or a large graphic element, never small
   type on a light background.

The same trap applies to the status and stop colours: none of them is a body-text colour on our
background.

| Colour | As text on `#F7F6F3` | Safe as text? |
|---|---|---|
| `success` `#16A34A` | 3.05:1 | No — fill and icons only |
| `warning` `#F59E0B` | 1.99:1 | No — fill and icons only |
| `error` `#EF4444` | 3.48:1 | No — fill and icons only |
| stop 1 `#2563EB` | 4.78:1 | Yes |
| stop 2 `#059669` | 3.49:1 | No — fill only |
| stop 3 `#7C3AED` | 5.27:1 | Yes |
| stop 4 `#DC2626` | 4.47:1 | Borderline — treat as fill only |

When one of these must label something in words, put the word in `text` `#1F2937` and let the colour be
the dot, the bar or the badge behind it. A red error message is written in `#1F2937` next to a `#EF4444`
icon, not in `#EF4444`.

`tests/test_brand.py` checks every ratio in this section against `tokens.json`, so a token that changes
without its contrast being rechecked fails the build.

## Typography

| Role | Font | Weights | Used for |
|---|---|---|---|
| Display | **Plus Jakarta Sans** | 700 | The wordmark, page titles, the landing hero |
| Text | **Inter** | 400 / 600 | Everything the operator reads: labels, body, buttons |
| Data | **JetBrains Mono** | 400 | Box ids, coordinates, dimensions, weights |

Mono is not decoration. Anything the solver produced or the operator must read back character by
character is mono: `Box #0423 › Stop 3 › Position B2`. It keeps digits aligned in a list and makes an
id impossible to misread on a phone in a warehouse.

All three are on Google Fonts. Self-host them with the app rather than hot-linking, so the interface
still renders on a loading dock with bad reception.

## Logo

Three files in `assets/brand/logo/`:

| File | Use |
|---|---|
| `quai-logo-light.svg` | On the `#F7F6F3` background and other light surfaces |
| `quai-logo-dark.svg` | On navy `#102238` and other dark surfaces |
| `quai-app-icon.svg` | The square icon: PWA manifest, favicon, home screen |

The mark is a rounded **Q read as a loading dock**: a navy outer Q, a white dock opening, a safety-orange
parcel door, and a small navy ramp at the base. The wordmark is bold and rounded, set in the display font.

Rules:

- **Do not rebuild it.** An earlier geometric bracket logo exists in older files; it is retired. These
  three SVGs replace everything before them.
- **Do not recolour it.** Navy, white and orange, in those places. No gradients, no shadows, no outline.
- **Do not distort it.** Scale both axes together. Do not rotate it, do not condense the wordmark.
- **Clear space:** keep a margin equal to the height of the Q's opening on all four sides.
- **Minimum size:** 24 px tall for the mark alone, 96 px wide for the mark with the wordmark. Below
  that, use the app icon.
- **On a photograph**, put the logo on a solid navy or off-white panel. Never straight onto a diorama.
- App icon sizes exported in the pack: 1024, 256, 128, 64 and 32 px. The 1024 px master is
  `quai-app-icon.png`; generate the rest from the SVG.

### Known defect in the supplied wordmark

`quai-logo-light.svg` and `quai-logo-dark.svg` render the word QUAI as live SVG `<text>`. This branch
sets that text to the display font the kit itself declares, with a fallback stack, because the files
arrived asking for Arial — which is neither the brand font nor present on every machine.

Live text still means the wordmark renders differently depending on what the viewer has installed.
**Before the logo is used anywhere public, the wordmark should be converted to outlines.** That needs a
vector editor and is not something this branch can do correctly. Until then, prefer the app icon, which
is pure geometry and has no text at all.

## Illustration style

> Bright premium miniature logistics diorama; painted-vinyl figures; tilt-shift; warm daylight.

Every image in the product comes from one world, the way a stop-motion film has one set:

- **Material:** painted vinyl and matte plastic. Soft edges, gentle specular highlights, no photoreal
  skin, no hard chrome.
- **Camera:** tilt-shift, shallow depth of field, slightly above eye level, so real warehouses read as
  models on a table.
- **Light:** warm daylight, soft shadows, never night, never harsh flash.
- **Characters** (`reference/operator.png`): one recurring operator — orange hi-vis vest, navy cap or
  curly brown hair, phone or tablet in hand. Calm and competent, never comic, never stressed. Other
  characters are the same build and vest so the cast reads as one team.
- **Objects and vehicles** (`reference/objects-vehicles.png`): yellow forklifts, kraft cartons, wooden
  pallets, white box trucks with the doors open. Boxes are kraft, not branded.
- **Environments** (`reference/environments.png`): warehouse interiors, loading docks, suburban delivery
  streets. Always mid-morning.

The film storyboard runs: parcels arrive → the operator scans → the operator talks → the AI understands →
the 3D plan appears → the forklift loads → something unexpected happens → the plan recomputes on the spot
→ the load is finished → the deliveries come off in order. That last beat is the product's whole promise,
and it is the one a screenshot should show.

## Interface rules

The mockups in `reference/mobile-ui.png` set the shape of the interface. Where they conflict with the
accessibility rules above, the accessibility rules win.

- **Phone first.** The operator is standing up holding a phone, sometimes in gloves. Design for one
  thumb, then let it grow to the supervisor's screen.
- **Corners are generous.** Cards and sheets ~20–24 px; buttons are full pills; the app icon is a
  rounded square. Nothing in this interface has a sharp corner.
- **One primary action per screen**, an orange pill with navy text and a `→`. Everything else is a text
  button or an outline.
- **The microphone is a circle**, orange, centred, the largest target on the screen. It is how the
  operator talks, and the product is named after talking.
- **Surfaces float:** white cards on the warm background, one soft shadow, no borders.
- **Touch targets are at least 44 px**, and further apart than looks necessary on a desktop screen.
- **Numbers are mono.** Dimensions, weights, box ids, coordinates.
- **State is shown, not described.** A green check for a placed box, a warning badge for an unresolved
  constraint, a stop colour plus its number for a destination.
- **Say what the solver did, and what it could not do.** An unplaced box is a normal result and gets a
  calm explanation, not an error screen. The tone is the personality: human, calm, precise, optimistic.

## What is not decided yet

- Navy `#102238` is used throughout but is not a token; it should be added to `tokens.json`.
- No dark theme is defined. The dark logo exists, but the surface, text and status colours for a dark
  interface do not.
- No spacing scale, type scale or elevation scale. Whoever builds #18 should propose one and add it here
  rather than inventing it per screen.
- The wordmark is still live text (see above).
