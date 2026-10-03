# HY-25 — Take a feature the app does not have off the landing page

- **Author:** `MORHI11`
- **Date:** 2026-10-03
- **Branch:** `fix/landing-replan-claim`
- **Issue:** none (fixes copy added in `HY-12` / #42; touches the title of #29)
- **Reviewer:** `SamDana-maker` by one-off swap — the rotation in CLAUDE.md puts `MORHI11`'s work on
  `Lpk78`, but the claim being removed describes `SamDana-maker`'s open #36, and he is the one who
  can say whether the replacement wording under-sells what the solver really does. The rotation is
  unchanged; this is the exception, recorded so that the documented rotation and the practised one do
  not diverge without a trace.

## Prompt as typed

```
HY-25 Retirer de la page d'accueil une fonctionnalité qui n'existe pas

web/src/landing/sections.jsx:268 annonce « Replans when a parcel is missing » et :448 « Replan on incident — A missing parcel is not a stuck plan ». Rien dans l'app ne replanifie : l'API expose /plan, /constraints et /route, et la PR #36 qui l'ajouterait est encore ouverte.

documentation/design.md interdit d'annoncer ce que l'app n'a pas. C'est la première page que la professeure verra.

Réécris ces deux passages pour décrire ce que le produit fait réellement — il y a largement de quoi, entre la dictée, le plan calculé et la tournée. Ne pose pas de badge « planned » : décrire le vrai est plus simple et ne se discute pas.

ET DANS LE MÊME COMMIT, étends la regex de web/src/pages/copy.test.jsx. Elle couvre aujourd'hui estimated route time|navigation|hand-off|delivery progress, et c'est précisément pour ça qu'elle n'a pas vu passer la replanification. Sans ce correctif, la phrase peut revenir et le test continuera d'affirmer que tout va bien — le motif exact qu'on a attrapé trois fois sur ce projet.

Corrige aussi le titre de l'issue #29 : il dit « the five placement constraints it currently refuses », il y en a quatre (at_bottom, keep_upright, max_stack_height, not_stackable). Le README dit quatre, c'est le titre qui est faux.

Reviewer : SamDana-maker. PR normale.
```

## The claim, checked against the server rather than against memory

`main` exposes exactly three endpoints — `grep '@app\.\(get\|post\)' src/server.py` gives `/plan`,
`/constraints`, `/route`. There is no `src/quai/incident.py` and no `recompute` anywhere in
`server.py`. `SA-14` / #36, which adds `POST /plan/recompute`, is still open. So both passages
describe something no part of the shipped product can do.

## Why the test did not catch it

`copy.test.jsx` already walks every landing section looking for claims about unbuilt features. Its
pattern was:

```js
/estimated route time|navigation (app|and live)|hand-?off|delivery progress/i
```

Four specific phrases, each added the day someone noticed that phrase. Replanning was never one of
them, so the guard reported success on a page making a false claim — the same shape this project has
now caught four times (#14's parser regex, #35's stop order, #60's `on_top` pair, `HY-20`'s language
assertion): **a test that passes because it was not looking.**

## The count in #29 is stale rather than wrong

`#29 — Solver: honour the five placement constraints it currently refuses`. Read from the code rather
than counted by hand: `set(CONSTRAINT_FIELDS) - set(solver.HONOURED)` is
`['at_bottom', 'keep_upright', 'max_stack_height', 'not_stackable']` — four. It was five until
`SA-19` / #60 taught the solver `on_top` and moved it into `HONOURED`; the title was simply never
updated behind it. The README already says four.

## What replaced it had to be true as well

The obvious replacement for the strip item was something about plans being verified. It would have
been a second false claim: `POST /plan` returns `solve()`'s result and **does not** run
`checks.find_problems` over it — the independent checks run in the test suite and in
`demo_fixtures`, not in the request path. Checked before writing it rather than after.

So both replacements are things the endpoint demonstrably does:

| Was | Now | Why it is true |
|---|---|---|
| "Replans when a parcel is missing" | "Says what would not fit" | `POST /plan` returns `unplaced`, and `PlanScreen`'s `UnplacedList` prints it under "Not placed" rather than showing fewer boxes than were sent |
| "Replan on incident — A missing parcel is not a stuck plan" | "Rules you can check — Anything not applied is named" | `/plan` returns `not_applied` with a reason per rule (`SA-16` / #51), and `NotAppliedList` renders each one |

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/77 (reviewer: `SamDana-maker`)
- **What the AI produced:** the two replacement strings, the `UNBUILT` pattern and its comment in
  `copy.test.jsx`, and the corrected title on issue #29.
- **How it was checked:** `npm test` (195 web) and `python3 -m unittest discover tests` (409 on this
  branch; `HY-22`'s seven are on #75 and not merged yet). Then mutation-tested, which is the only
  evidence that matters here: reinstating `"Replans when a parcel is missing"` now **fails** the
  guard with *expected '3D loading planSee every parcel in pl…' to contain 'planned, not shipped'*.
  Before this change the same page passed.
- **What was changed by hand:** two decisions. Rejecting "every plan is verified" as the replacement
  once `server.py` showed the checks do not run in the request path — the task was to stop claiming
  an unbuilt feature, and swapping in a different unbuilt one would have been the same mistake with
  better intentions. And widening `UNBUILT` by *capability* rather than by phrase: the pattern now
  covers replanning, live tracking, WMS/ERP sync, fleet views and load history, none of which exist,
  with a note that the rule for adding is "the feature is unbuilt", not "someone spotted the words".
