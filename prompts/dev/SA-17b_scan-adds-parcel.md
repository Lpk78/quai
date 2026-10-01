# SA-17b — The scan actually adds the parcel to the load

- **ID**: SA-17b
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-01
- **Branch**: `feature/scan-adds-parcel` (off `feature/app-scan-step`, `SA-17` / #54)
- **Issue**: none — demo preparation; the half `SA-17` deliberately left undone

## Prompt as typed

```
SA-17b, go. Reste sur SA-17 pour l'instant, ne commence pas tant qu'Hypolyte n'a pas poussé HY-15 —
tu rebases ta branche dessus à ce moment-là, pas sur main maintenant. Objectif du commit final :
sortir QUAI-BOX-0001 de BOXES dans manifest.js, le faire passer en state ajouté par /app/scan, et
/app/dictate doit alors lire 18 + 1.
```

A letter suffix rather than a free number, per `prompts/README.md`: this is the task `SA-17` split off
rather than a new one, and it belongs next to the ID it followed in time.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/57 (reviewer: `MORHI11`), based on
  `feature/app-scan-step` rather than `main` — `/app/scan` only exists on #54, so this is stacked and
  needs retargeting to `main` if #54 merges first.
- **What the AI produced:** the `SCANNED_PARCEL` / `loadWith()` split in `web/src/data/manifest.js`,
  `web/src/scan/scannedParcel.jsx`, the add-on-scan behaviour in `Scan.jsx`, the per-render load in
  `Dictate.jsx`, the count in `Home.jsx`, six tests, and the README update.
- **What was changed by hand:** nothing in the committed code.
- **The instruction that turned out to be already satisfied:** the task said not to start until MORHI11
  had pushed HY-15, then to rebase onto it. He had already pushed it as #56 by then, so the gate was
  open — but #56 touches only `PlanScreen.jsx` and `plan.css`, so there was no file overlap and nothing
  to rebase onto. The real dependency was `SA-17` itself, which is what this branched from. Checked
  rather than assumed, and said so on the PR.
- **The decision inside it that was not specified:** where the state lives. Router state only survives
  the hop it is attached to, and the parcel has to cross two (`/app/scan` → `/app/dictate` →
  `/app/plan`), so it is a context. A parcel lost on the second navigation would plan eighteen boxes
  with nothing on screen admitting it. Not persisted across a reload, deliberately: a reload is a fresh
  round, and deciding when a scan expires belongs with real operator sessions, which `LP-20` opened.
- **The bug this would have shipped with, caught by reading rather than testing:** `PLAN_BOXES` in
  `Dictate.jsx` was computed once at import from `BOXES`. Left alone it would always have been the
  eighteen, so the scan would have added a parcel the model heard about and the solver never received —
  the exact `unknown_item` failure mode, with no error anywhere to explain it. It is now derived per
  render, and both the `/constraints` manifest and the `/plan` load come from the same list.
- **One existing test changed:** `app.test.jsx` asserted `1 / 19`. It enters at `/app/dictate` without
  scanning, so `1 / 18` is the truthful number there now; the nineteen-box path is asserted in
  `scan.test.jsx` instead of assumed.
- **Also in this round:** `LP-20` landed as #55 while `SA-17` was in review, with `jsqr` installed and a
  camera loop inline in `Login.jsx`. `SA-17`'s own documentation had said LP-20 did not exist — true
  when written, stale within the hour — so it was corrected on that branch (`4f533c4`) to point at the
  loop a future task should lift out and share.
- **Verified:** 79 web tests pass (73 before), 347 Python tests pass, 1 skip, `npm run build` clean.

## Outcome of the review round (#57)

- **What the review asked for:** one change from `MORHI11`, which was this PR's own Please-check #1
  coming back — persist the scanned parcel so an accidental reload mid-demo cannot drop the load
  silently back to eighteen boxes. Confirmed by `Lpk78` before it was built, rather than taken from the
  reviewer's message alone.
- **What the AI produced:** `sessionStorage` behind the existing context in
  `web/src/scan/scannedParcel.jsx`, and five tests covering a reload.
- **The decision inside it:** only the **id** is stored, never the box. `data/manifest.js` stays the
  single source of what a parcel measures; a copy in storage would be a second one, free to go stale
  and impossible to notice. An id nothing recognises is dropped rather than restored, and reads and
  writes are both wrapped — Safari in private mode throws on write, and failing to remember a parcel is
  not a reason to fail to render the screen. `sessionStorage` rather than `localStorage` because a scan
  belongs to one sitting: closing the tab ends the round, which is the expiry rule we would otherwise
  have had to invent.
- **A test hazard the change introduced:** persistence survives between tests too, so a leaked parcel
  would have made "nothing was scanned" quietly assert the wrong thing. Cleared in `beforeEach` with
  the reason written next to it.
- **Also in this round:** `main` moved three times under this branch — #54, #56, then #55 and #58. The
  merge kept LP-20's `/login` route alongside the provider in `App.jsx`, and the scan-step README
  paragraph that supersedes SA-17's. GitHub had already retargeted this PR from
  `feature/app-scan-step` to `main` when #54 merged, so no manual retarget was needed.
- **Verified:** 97 web tests pass (79 before), 349 Python tests pass, 1 skip, `npm run build` clean.
