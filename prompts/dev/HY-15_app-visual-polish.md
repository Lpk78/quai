# HY-15 — Visual polish on /app, /app/dictate and /app/plan

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/app-visual-polish`
- **Issue:** none (follows `HY-14` / #47, `SA-14a` / #45, `SA-14b` / #48, all merged)

## Prompt as typed

```
HY-15 Visual polish on /app, /app/dictate and /app/plan to match assets/mockups/app_mockups.png. First list what already exists. Concrete bugs to fix on /app/plan: (1) each box's "at x, y, z" renders one number per line instead of one compact line; (2) in "Not placed", the item name and "did not fit" overlap illegibly. Beyond those two: consistent card padding/radius, button style matching the landing page (orange #FF8A00 primary), readable monospace only where dimensions/positions show, clear hierarchy. Mobile-first (390px), verify at that width. No new dependencies, keep existing tests green.
```

## What was actually wrong, found by reading the grid before touching it

**Bug 1 is not about `.plan-at` — it's `.plan-dims`, and the same bug flips to `.plan-at` at the
desktop breakpoint.** `.plan-item` is a 3-column grid (`1.75rem 1fr auto`) with five children
(swatch, order, id, dims, position). The first three fill row one; `.plan-dims` had no explicit
`grid-column`, so CSS Grid auto-placed it into the 1.75rem swatch-width column of an implicit second
row — "60 × 60 × 85" wrapped one token per line. Verified in a real browser at a true 390px viewport
(an iframe, since the window itself won't go narrower than 500px here) before writing any CSS: the
`.plan-dims` span measured 28px wide and ~104px tall. Fixed with one declaration,
`.plan-dims { grid-column: 2 / -1; }`, mirroring `.plan-at`'s existing rule.

The desktop media query (`min-width: 40rem`) adds a 4th column and resets `.plan-at` to
`grid-column: auto` — which is exactly the same mistake at the wider breakpoint: with four columns
now holding swatch/order/id/dims on row one, `.plan-at` (the 5th item) auto-places into the narrow
column instead. Confirmed the same way: height 76px instead of 19px at 700px wide. Fixed by letting
`.plan-dims` revert to `auto` at that breakpoint instead (so it rejoins order and id on row one, the
column now being free) and leaving `.plan-at` on its inherited `2 / -1` always.

**Bug 2 does not reproduce with today's demo data, at 390px or any width tried.** `mattress` and
"did not fit" never overlap — `grid-template-columns: 1fr auto` already keeps them apart with the
load currently in `demoLoad.js`. It does reproduce the moment an id is long enough that the `1fr`
track's content can't shrink below its own width (a bare `1fr` track's minimum is its content size,
not zero) — tried with `QUAI-BOX-0001-fragile-parcel`, the kind of id the Madrid-round data (`SA-15`,
merging the same data `SA-17`/#54 also reads from) actually uses. Fixed defensively:
`grid-template-columns: minmax(0, 1fr) auto` lets the id track shrink, plus `overflow: hidden;
text-overflow: ellipsis; white-space: nowrap` truncates it instead of wrapping or overflowing.
Recorded here rather than claimed as a direct repro, since it wasn't one against the committed data.

## Decisions taken before writing any code

**`.plan-summary` and `.plan-failure` now use the shared `.card` class** (background, radius,
padding, shadow) instead of duplicating those four properties with different numbers
(`0.875rem`/`1rem` vs `.card`'s `1.4rem`/`1.5rem`) — the same inconsistency the task's "consistent
card padding and radius" line was about. `.plan-item` and `.plan-inspector` keep their own smaller,
mutually-consistent radius (`0.625rem`): they are dense, repeated list rows, not cards, and
design.md's "~20–24px" corner guidance is written for cards and sheets. `.plan-scene`'s radius moved
to `1.4rem` to match the surfaces around it, without adopting `.card` itself — its padding has to stay
`0` so the canvas fills the surface edge to edge.

**Button style was already consistent** — `.button`/`.button--quiet`/`.button--block` (orange
`#FF8A00` fill, navy text, pill) are the only button classes used anywhere in `/app`, `/app/dictate`
and `/app/plan`; `Failure`'s "Try again" already used `.button`. Nothing to change here; noted so the
task's own checklist shows it was looked at, not skipped.

**Monospace usage was already correct** on `/app/plan` (ids, dimensions, positions, the fill-rate and
weight figures) and on `/app`'s box list. `Dictate.jsx`'s constraint cards interpolate raw numbers
(`limit_cm`, `limit_kg`) into plain template strings rather than JSX, so they are not mono — leaving
that as is: making it mono means turning `describeConstraint` from a string-returning function into
one returning elements, which is a structural change past what a visual-polish pass should carry.
Flagged for a follow-up rather than folded in here.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/56 (reviewer: `Lpk78`)
- **What the AI produced:** the two `.plan-dims`/`.plan-at` grid-placement fixes (both breakpoints),
  the `.plan-item--unplaced` truncation fix, and moving `.plan-summary`/`.plan-failure` onto `.card`.
- **How it was checked:** `npm test` (60 pass) and `python -m unittest discover tests` (347 pass, 1
  skip) locally — but the two named bugs are CSS-layout bugs jsdom's test environment cannot see
  either way, passing or failing, since it does not run a real layout engine. Verified instead in an
  actual Chromium tab: a true 390px viewport via an iframe (window resize has a 500px floor here), the
  exact DOM rects measured before the fix (`.plan-dims` at 28×104px, wrapped) and after (294×21px,
  one line), the same at a 700px desktop width, and the truncation fix tried against a long id that
  isn't in the committed demo data. No new jsdom test was added for either bug: there isn't one that
  would exercise the actual failure mode, and a test that can't fail is worse than none.
- **What was changed by hand:** nothing in the committed code — the decisions are the diagnosis
  itself. The task described bug 1 as being about `.plan-at`; reading the grid before writing CSS
  found it was `.plan-dims`, and that the same mistake recurs for `.plan-at` at the desktop
  breakpoint. The task described bug 2 as a current, observed overlap; it does not reproduce against
  `demoLoad.js`'s data at any width tried, so it's recorded as a defensive fix for long ids (the kind
  the Madrid-round data already in `/app` and `/app/dictate` uses) rather than claimed as a direct
  repro.
