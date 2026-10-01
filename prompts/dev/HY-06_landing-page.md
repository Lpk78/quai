# HY-06 — The real landing page

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/landing-page`
- **Issue:** none (follows `HY-01` / #18, which built the shell this replaces)

## Prompt as typed

```
HY-06 Build the real landing page at / so it looks like ~/Downloads/QUAI_DA_FINAL/05_UI/QUAI_website_mockup_v2.png (main layout) and QUAI_website_mockup.jpg / QUAI_marketing_board.png (sections), as a real product site — no mention of a school or a course anywhere on the site. Copy the four images from ~/Downloads/QUAI_DA_FINAL/08_SITE_IMAGES into web/public/images as optimised WebP (responsive sizes). Use the logo SVGs from assets/brand exactly.

Sections, in order:
1. Nav: white rounded floating bar — logo; links How it works · Features · Why QUAI; outline "Log in" and orange "Get started" (navy text on orange).
2. Hero, like mockup v2: left = orange eyebrow "LOAD PLANNING FOR DELIVERY TEAMS", headline "People talk. We load.", subtitle "Say how the load has to go. QUAI turns your words into rules it can check, and a solver works out where every parcel goes: last stop at the back, first stop at the doors.", buttons "Get started" and "Watch the film" (play icon), then three small icon+label items: "Voice rules — Just say it", "3D load plan — Every parcel placed", "Stop order — Right parcels at the doors". Right = hero_dock_wide image, full-bleed, fading into the background on the left. On mobile, stack like the phone frame in mockup v2.
3. "How QUAI works" white card overlapping the hero bottom, like QUAI_website_mockup: four numbered orange steps joined by a dashed orange line — 1 Scan: "Scan each parcel. Size and weight come from your catalogue." 2 Say the rules: "\"Paint cans last, nothing on the glass.\" QUAI reads back what it understood and asks when it is not sure." 3 Get the 3D plan: "The solver places every parcel: no overlaps, every box supported, weight limits respected." 4 Load in stop order: "Follow the plan one parcel at a time. The first stop's parcels end up right behind the doors." — with an HTML/CSS phone in the middle showing the app home screen (demo data: "Good morning. Let's load." / "Van 12 · 3 stops · 24 parcels" / card "Loading plan ready — Built from your rules and your stop order." / button "Start loading" / tiles 24 Parcels · 3 Stops · 8 Rules).
4. Three feature panels side by side, like the lower row of mockup v2, each with an HTML/CSS phone: "VOICE TO PLAN — Just tell QUAI how to load" (voice rules screen: Paint cans — load last · Glass panels — nothing on top · Water packs — at the bottom · question card "\"The heavy one\" — which parcel?"); "3D LOADING PLAN — See every parcel in place" (3D plan screen: next-parcel callout "Next parcel · Stop 2 · B35 · 22 kg", progress 17/24, button "Loaded, next"; bullets: Respects your rules · Clear visual guidance · Replans when a parcel is missing); "STOP ORDER — The right parcels at the right doors" (stop list: Stop 1 · 8 parcels · at the doors / Stop 2 · 9 parcels · middle / Stop 3 · 7 parcels · at the back; note "Your delivery list sets the stop order. QUAI loads to match it." — no map, no ETA, no Navigate button). Use van_stops_colours as the visual for the stop panel.
5. A navy band like the bottom-left of QUAI_marketing_board: logo in white, "Smarter loading for a smoother day.", the operator image.
6. "The model never places a box." section: body "Language models write layouts that look right and are not: boxes overlap, float, change from one run to the next. In QUAI the AI only translates what you say; placement comes from a solver that is checked, repeatable and explainable." with three cards YOU SAY / VALIDATED JSON / 3D PLAN.
7. "A day on the dock" — image tiles: scan_parcel "Scan the parcels", van_stops_colours "Loaded in stop order", doorstep_handover "The right parcel, first time".
8. Final CTA "Next van, fewer surprises." with Get started / Log in, then footer "© 2026 QUAI · People talk. We load." with the nav links.

Rules: follow documentation/design.md (tokens only, navy text on orange, copy rules). Never claim measured savings (time, emissions, errors, fill rate), routes, ETA, live tracking, navigation or pricing. Responsive at 1440, 1024, 390 and 375 px. Open the page in a real browser at 1440 px and 390 px, compare each section with the mockups, iterate until it matches, and attach screenshots to the PR.
```

## Decisions taken before writing any code

**Section 5's strapline was changed, with the author's agreement.** The task asked for a navy band
carrying the logo and "Smarter loading for a smoother day.". `documentation/design.md` states that
"People talk. We load." is the only tagline and that it must not be paired with a second strapline — and
it names "Smarter Delivery Ahead." from the supplied mockups as exactly this mistake. That rule was
reviewed and approved in #28 and is covered by a test. The band keeps its layout, logo and operator
image; its line is "People talk. We load.".

**Branch base.** `web/` is not on `main` yet: it arrives with `HY-01` (#33), still in review. This branch
is cut from `feature/web-app` and its Pull Request targets that branch, to be retargeted to `main` when
#33 merges.

**The v2 mockup's copy is not used.** It advertises "Save time", "Fewer errors", "4h 20m Estimated route
time", "Higher vehicle utilisation", a route map and a Navigate button. The task forbids all of it and so
does `design.md`. The mockup is followed for layout, colour and composition only.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/PRNUM
- **What the AI produced:** the eight sections of the landing page, the four phone screens drawn in
  HTML and CSS, nine inline icons, the two stylesheets, the twelve responsive WebP images, and six
  further tests.
- **How it was checked:** the production build was opened in a real browser and compared section by
  section against `QUAI_website_mockup_v2.png` and `QUAI_marketing_board.png`, over three rounds of
  correction — the "Watch the film" button was rendering orange instead of white (a specificity clash
  with `.button`), the headline ran onto a bad line break, the feature panels left a gap because the
  phones were top-aligned, and the nav buttons wrapped their own labels at 390 px.
- **What it found on its own:** a two-layer CSS mask on the hero photo made it vanish in Chrome, because
  the prefixed and standard spellings of `mask-composite` disagree; it was reduced to one layer.
- **What was changed by hand:** the decisions. The strapline in section 5 was changed to the approved
  slogan (see above). The phones are drawn rather than screenshotted. The v2 mockup's copy was not used.
- **Note for whoever reviews the screenshots:** Chrome's screenshot pipeline does not always rasterise
  the masked hero photo, so some captures show that area blank while the page itself renders it. The
  committed screenshots are ones where it rendered.
