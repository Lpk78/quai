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

Because they are references and not assets, the four largest are stored as JPEG rather than PNG — 7.6 MB
of PNG became 1.3 MB of JPEG at the same pixel sizes, and nothing is read off them that survives lossy
compression anyway. Anything that must stay exact is vector or text: the logo SVGs and `tokens.json`.

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
| `navy` | `#102238` | The logo's dock, dark surfaces, and **all text placed on orange** |

Navy arrived in the logo and the app icon but not in the supplied `tokens.json`. It is now a token:
it is the mandatory text colour on orange, so an interface built from the token file alone would
otherwise be missing the one colour the central accessibility rule requires. `tests/test_brand.py`
reads it from the tokens rather than hardcoding it, so the rule and the palette cannot drift apart.

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

The mark is a **Q read as a loading dock**: a navy arch, a white dock opening seen in slight
perspective, a safety-orange parcel door inside it, and a ramp running down and to the right that doubles
as the Q's tail. In the lockup the mark *is* the Q — the wordmark that follows it is `UAI`, set in a bold
rounded geometric sans drawn to match the display font.

All three files are **vectors traced from the sheet**: flat paths, no raster, no embedded fonts, no
live `<text>`. They are produced by `assets/brand/logo/build_logo.py`, which separates each lockup on
`quai-logo-v2-sheet.png` into its colour layers and traces them, so the proportions are the sheet's
rather than an estimate. An earlier version of that script drew the mark by hand from measurements and
got the Q and the wordmark wrong; the review of #33 caught it by putting the two side by side, which is
the check to repeat after any change here.

**Edit the script and re-run it; do not edit the SVGs by hand** — `tests/test_brand.py` regenerates
them into a temporary directory and fails if the committed files differ. That check needs `numpy`,
`pillow` and `potracer`, which are build-time tools rather than runtime dependencies of QUAI, so it
skips where they are absent and runs for whoever is editing the logo.

Rules:

- **Do not rebuild it.** Two earlier marks exist in older files — a geometric bracket logo, then a first
  dock Q. Both are retired. These three SVGs replace everything before them.
- **Do not recolour it.** Navy, white and orange, in those places. No gradients, no shadows, no outline.
- **Do not distort it.** Scale both axes together. Do not rotate it, do not condense the wordmark, do not
  re-space the letters.
- **Do not set the wordmark in a font.** `UAI` is outlines on purpose. Typing "QUAI" in Plus Jakarta Sans
  next to the mark gives a different logo.
- **Clear space:** keep a margin equal to the height of the dock opening on all four sides.
- **Minimum size:** 24 px tall for the mark alone, 96 px wide for the mark with the wordmark. Below that,
  use the app icon, which stays legible down to about 32 px.
- **On a photograph**, put the logo on a solid navy or off-white panel. Never straight onto a diorama.
- The app icon is a navy rounded square; export PNGs from the SVG at 1024, 256, 128, 64 and 32 px.

`assets/brand/logo/quai-logo-v2-sheet.png` is the supplied rendering of the approved mark. It is the
**reference** the vectors were drawn from, not an asset to use: it is a raster, it has no transparency,
and it is the thing the SVGs replace.

## Copy rules

What the product is allowed to say about itself. These apply to the landing page, the app, the README,
screenshots, the demo film and anything published.

**One slogan: "People talk. We load."** It is the only tagline. Do not write variations of it, do not
translate it in an English-language surface, and do not pair it with a second strapline.

**Never say the AI plans the load or orders the stops.** This is the architectural rule of the project,
and copy is where it is most easily broken. A deterministic solver computes placement; the route arrives
with the manifest as an input. The AI turns what the operator says into validated constraints and
explains the result.

| Do not write | Write instead |
|---|---|
| "The AI plans your load" | "QUAI plans your load" — or name the solver |
| "The AI decides what goes where" | "You talk, the solver places" |
| "Our AI optimises your route" | Nothing: QUAI does not compute routes |
| "AI-powered loading order" | "Loading order follows your delivery stops" |
| "Smart AI stacking" | "Stacking that respects the limits you stated" |

**Only describe features that are built or planned.** Changed on 2026-10-01: the route view, an
estimated time per stop, handing off to a navigation app and delivery progress are **planned** — the
server work is `SA-12` — issue #35, `POST /route` — and the app screen follows it. They may be described. What is still out of
scope, and still forbidden: pricing and billing, fleet management, a barcode catalogue, integrations.
The bonus list in `documentation/roadmap.md` is a list of things we have *not* built and is not
marketing copy.

**But QUAI never chooses the route or the stop order.** This is the same architectural rule as above,
and relaxing the first rule makes it easier to break, not harder. The delivery list arrives with the
manifest; QUAI shows it, loads to match it, and can hand the driver to a navigation app. It does not
compute it, reorder it or improve it.

| Do not write | Write instead |
|---|---|
| "Optimised route" / "we optimise your route" | "Your route" — it is the operator's |
| "QUAI plans the best order of stops" | "QUAI loads to match your stop order" |
| "AI-optimised delivery order" | Nothing: the order is an input |
| "Faster routes" | Nothing: that is a measured saving we have not measured |

**Say when something is not built yet.** A planned feature described as though it shipped is the same
dishonesty the old rule guarded against, one step along. Label it.

**These rules are executable.** `web/src/pages/copy.test.jsx` renders every page and fails on the
phrases above — the invented slogans, any claim that the AI or QUAI plans the load or chooses the
stops, a measured saving, pricing, and any mention of a school or a course. Read it before writing
copy: it is faster than reading this section, and it is the version that will actually stop you.

**No real brand marks in published images.** No real carrier, retailer, van, or software logo, no
recognisable real packaging, no real company name on a box, a truck, a building or a screen. Generated
illustrations are prone to producing them by accident — check every image before it is published, and
regenerate rather than retouch.

**Navy text on orange buttons**, every time. This is the accessibility rule above, repeated here because
button labels are copy as much as they are colour, and the supplied mockups get it wrong.

**Tone**, from the personality: human, calm, precise, optimistic. Say what happened and what the operator
can do about it. A box that could not be placed is a normal result stated plainly, never an apology and
never an error page.

### The supplied mockups break almost all of these

This is not hypothetical. The two newest reference sheets were checked against the rules above and they
fail them, which is exactly why the rules are written down. Treat both as mood images.

`reference/website-mockup.jpg`:

- Two invented slogans — "Smart loading. Delivery confidence." and "Smart logistics for a smoother day" —
  where there is one: *People talk. We load.*
- "Follow your **optimised route** and get **live updates**", a "4h 20m **Est. route time**" tile, and a
  map step. QUAI computes no routes, estimates no times and tracks nothing live. Three features we do
  not have, on one page.
- A **Pricing** item in the navigation, for a product with no pricing.
- "Get started" and "Start loading" drawn as **white text on orange**.

`reference/brand-applications.jpg`:

- Two more slogans: "Smarter Delivery Ahead." on the van and "People. Parcels. Forward." on the van and
  the business card.
- A **fabricated identity** — a named Operations Lead, an email address, a phone number and a domain.
  None of it is real and none of it may be published as though it were.
- A phone home screen carrying **real third-party app icons**. That is the real-brand-marks rule, broken
  by a generator that was only asked for "a phone". It is the easiest one to miss and the clearest
  reason to check every image before publishing it.

The useful parts of both sheets are the layout, the colour, the camera and the mood. The words are not
ours.

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

`reference/delivery-story.jpg` and `reference/brand-applications.jpg` extend the world to the delivery
itself and to vans, signage, packaging and stationery. Same material, same light, same cast.

The film storyboard runs: parcels arrive → the operator scans → the operator talks → the AI understands →
the 3D plan appears → the forklift loads → something unexpected happens → the plan recomputes on the spot
→ the load is finished → the deliveries come off in order. That last beat is the product's whole promise,
and it is the one a screenshot should show.

## Interface rules

The mockups in `reference/mobile-ui.png`, `reference/app-mockups.jpg` and `reference/website-mockup.jpg`
set the shape of the interface. Where they conflict with the accessibility rules or the copy rules above,
those rules win — and they do conflict, in the ways listed under *Copy rules*.

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

- No dark theme is defined. The dark logo exists, but the surface, text and status colours for a dark
  interface do not.
- No spacing scale, type scale or elevation scale. Whoever builds #18 should propose one and add it here
  rather than inventing it per screen.
- The landing page has no approved copy. The mockups supply none that passes the copy rules, so the words
  for `/` still have to be written.
