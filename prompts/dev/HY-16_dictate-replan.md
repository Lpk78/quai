# HY-16 — Wire Confirm to actually replan

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/dictate-replan`
- **Issue:** none (follows `HY-14` / #47, `SA-15` / #50, `SA-16` / #51)

## Prompt as typed

```
HY-16 Wire the dictate screen's "Confirm" button to actually replan. On confirm in /app/dictate, take the constraints array from the /constraints response and POST it to /plan alongside the current container and manifest (reuse whatever the plan screen already uses for its own POST /plan call, from #45 — don't duplicate the API client logic, extend api.js). Then navigate to /app/plan and show the result: the updated 3D view and list should reflect any load_last constraint that applied. If the response's not_applied field is non-empty, show those constraints clearly to the operator (type, item, reason) instead of silently dropping them — same honesty rule as everywhere else tonight. Use src/demo_fixtures.py's data (the Madrid round + 18 boxes + the scanned parcel) as the manifest/container source for this flow, so the demo is end-to-end real. Tests: confirm with an honoured constraint (load_last) shows a different plan than without it; confirm with an unhonoured type shows it under not_applied rather than hiding it; keep all existing tests green.
```

## Decisions taken before writing any code

**Branched from `feature/app-home-dictate`, not `main`.** `/app/dictate` — the screen this task wires up
— does not exist on `main` yet: `HY-14` / #47 is still open with `CHANGES_REQUESTED`, waiting on a
re-review that landed after the fix was pushed. Confirmed with the user rather than guessed, same as
`HY-15` hit minutes earlier. `main` is merged into this branch (not into #47's) so `SA-16` / #51's
`not_applied` field and `LP-11` / #46's real `/constraints` contract are both available without adding
more commits to a PR someone else is about to review.

**`src/demo_fixtures.py`'s data is ported to JS by hand, not generated.** There is no shared format
between the Python fixture and the web app, and a generator for one file read twice a project would
outlive is not worth building. `web/src/data/manifest.js` becomes the Madrid round — the 18 loaded
items plus the scanned parcel, nineteen boxes in total, the eight stops, the van — replacing the
`B1`–`B10` reference manifest from `documentation/prompt_evaluation.md` it held until now. That older
set was for scoring prompt versions against a fixed rubric, not for a live demo; reusing it here was a
placeholder from `HY-14`, and the task's own point is to stop placeholding.

**`PlanScreen.jsx` gains an optional seed from navigation state rather than a second code path for
"already have a plan."** `location.state.{plan, request}` short-circuits its existing `useEffect`
instead of a parallel fetch living in `Dictate.jsx` — the one `POST /plan` call this screen already
makes is reused exactly, not duplicated, which is what "extend `api.js`" turned out to mean once the
code was read: `postPlan(request)` already accepts whatever `request` shape the caller builds, so
nothing in `api.js` itself needed to change.

**`PlanScreen`'s caption stopped naming `DEMO_BOXES.length`.** It hard-coded "a demo load of 11 boxes"
regardless of what was actually being shown. True before this task, since the screen only ever showed
one fixture; false the moment a second source of plans exists. Fixed to read the actual request's box
count instead of being left to go stale quietly, which is the failure mode this whole project is built
against.

## Outcome

_Filled after the PR is opened._
