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

- **PR:** https://github.com/Lpk78/quai/pull/42
- **What the AI produced:** the two corrections required on #34, then five sections built from the
  references — Loading plan ready, Route & delivery order, the compact navy banner, the flanked stats
  strip and a plain light footer — plus eleven responsive WebP images and four new tests.
- **How the required corrections were checked:** by measurement, not by eye. The badge's contrast was
  computed before deciding whether to change it (6.61:1, so the colour stayed and a test was added
  instead), and the trace timing was measured in both conditions to prove the hole was real — `CI=1`
  gives 8.8 s with the trace executing, local gives 0.06 s skipped. Each new test was checked to fail
  when what it guards is reversed.
- **What it found on its own:** the `customer` cut-out is a portrait, and the square photo tiles
  cropped her head off; it is shown whole instead. The references' own copy carries two forbidden
  taglines and four measured-saving claims, all of which are named in the PR body rather than quietly
  dropped.
- **What was changed by hand:** the decisions. The interactive hero was split out as its own task
  before any code was written. `landing_ref_6`'s benefit claims were replaced by the capability items
  already on the page rather than invented afresh, and the stat tiles carry an explicit
  "not a measured result" label.
