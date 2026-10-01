# HY-12 — Landing page round 2, static sections

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/landing-sections`
- **Issue:** none (follows `HY-06` / #34, which built the page this reworks)

## Prompt as typed

```
HY-12 Landing page round 2, static sections. First commit, required by Lpk78 on #34: the route badge reads "planned, not shipped" with a test that the route panel renders it and readable contrast, and the logo fingerprint skip applies only when CI is unset. Then, matching the references in ~/Downloads/QUAI_DA_FINAL/05_UI/landing_refs/ and using the cut-out images in 08_SITE_IMAGES: compact navy banner like landing_ref_1 (logo, "People talk. We load.", operator_bust cut at the band's bottom on the right) between sections plus a simple light footer; "Route & delivery order" like landing_ref_2 with van_topdown and a three-colour legend (orange: at the doors, blue: middle, green: at the back); "Loading plan ready" like landing_ref_3 with three stat tiles labelled as an example van and the home phone render; stats strip like landing_ref_6 with boxes_quai and operator_thumbsup, no measured-savings claims; "A day on the dock" tiles using customer and scan_parcel. All images as optimised responsive WebP, copy rules from design.md, screenshots at 1440 and 390 px against each reference.
```

## Scope, decided before writing any code

The interactive hero — `dock_background` behind, `van_open_quai`, `forklift`, `pallet_jack_boxes` and
`operator_bust` in front, each layer moving with the pointer and on scroll — **was split out of this
task** and is not in this branch. It is the only part with behaviour rather than layout, and the only
part that can regress silently; it gets its own task so it can be reviewed as one.

`#34` merged before this started, so the branch is cut from `main` and the Pull Request targets `main`.

## Outcome

- **PR:**
- **What the AI produced:**
- **What was changed by hand:**
