# Roadmap

Each step is a branch and a Pull Request. The AI layer comes second on purpose: it plugs into a system
that already works.

Owners follow the area split in `CLAUDE.md`, and each PR is reviewed by the other member named there.

## Phase 1 — The system works without AI

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 1 | #5 | `feature/solver-v1` | Boxes + container model, placement without overlap | `Lpk78` | `SamDana-maker` | Done (#3) |
| 2 | #17 | `feature/solver-v2` | Stack weight limit + stop-ordered loading (`SA-05`) | `SamDana-maker` | `MORHI11` | Done (#27) |
| 3 | #6 | `feature/solver-api` | FastAPI exposing the solver over `POST /plan` | `SamDana-maker` | `MORHI11` | Done (#16) |
| 4 | #18 | `feature/web-app` | React + Vite app installable on a phone: `/` landing, `/app` shell (`HY-01`) | `MORHI11` | `Lpk78` | Done (#33) |
| 5 | #7 | `feature/3d-view` | 3D supervisor view of the plan | `SamDana-maker` | `MORHI11` | Done (#45 the plan screen, #48 the 3D view, #72 the scene rework) |
| 6 | #8 | `feature/box-form` | Box entry form: dimensions, weight, quantity, container | `MORHI11` | `Lpk78` | To do |

Row 1 is the one place where the owner column does not mean "wrote it": `Lpk78` wrote the v1 solver,
`SamDana-maker` reviewed it in #3, and owns the solver from there on — maintenance and extensions,
starting with row 2.

## Phase 2 — The AI layer

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 7 | #9 | `docs/constraint-test-sentences` | Fixed test sentences + expected JSON, including injection cases | `Lpk78` | `SamDana-maker` | Done (#14) |
| 8 | #10 | `feature/constraint-schema` | Strict JSON schema for constraints, validated before the solver | `Lpk78` | `SamDana-maker` | Done (#21) |
| 9 | #11 | `feature/prompt-evaluation` | Script scoring a prompt version on the fixed inputs | `Lpk78` | `SamDana-maker` | Done (#22) |
| 10 | #12 | `prompt/constraint-translation-v5-bounded-examples` | The `constraint-translation` family, v1 to v5, each with real scores; v4 stays in production (`documentation/failures.md`) | `Lpk78` | `SamDana-maker` | Done (#43) |
| 11 | #19 | `feature/constraint-translation` | Spoken sentence → validated JSON, over `POST /constraints` (`LP-11`) | `Lpk78` | `SamDana-maker` | Done (#46) |
| 12 | #19 | `feature/constraint-solving` | Constraints accumulated across sentences and handed to the solver | `Lpk78` | `SamDana-maker` | Partly done (#51, #61): the hand-off exists, the accumulation does not |

Row 11 is the translation step: one operator sentence into validated constraint JSON, over
`POST /constraints` on the server from row 3; rows 7 to 10 are what make it possible, and #10 points
at this row. Row 12 is the feature the whole AI layer builds towards — it is where the prompt, the
schema and the solver become one path, consuming what row 11 produces.

Row 12 is half built, and the half matters. `POST /plan` takes a `constraints` field and hands the
solver the types it honours — `load_last` since #51, `on_top` since #61 — while every other type comes
back in `not_applied` with a reason rather than being dropped in silence. So a dictated sentence does
move a box, which is what the demo shows. What does not exist is the accumulation this row is named
for: `Dictate.jsx` sends the constraints of the *last* sentence it translated, so a second rule
replaces the first instead of joining it. The screen is honest about it — the mockup's "Edit" and
"+ Add a rule" controls are deliberately absent, because editing one rule in place or adding one by
hand means a list that accumulates, and that is this row.

Row 9 is branched off row 8 rather than off `main`: C1 of the rubric is `quai.constraints.parse()`,
so #22 was merged after #21.

## Later — not yet opened as issues

| Branch | Deliverable | Owner | Status |
|---|---|---|---|
| `feature/operator-mode` | Step-by-step loading view + recomputation on incident | `SamDana-maker` | Recomputation is written and open as #36, paused on one named defect (see *Open pull requests*); the step-by-step view is not started |
| `experiment/llm-only-placement` | LLM vs solver comparison, logged in `failures.md` | `SamDana-maker` | Done (#38, `SA-06` finished as `SA-26`): 1 valid plan in 20 |
| `feature/route-display` | Addresses → geocoded points, road geometry and per-stop ETA (`SA-12`) | `SamDana-maker` | Done (#35) |
| `feature/dimension-scan` | Phone photo + scale marker → box dimensions | — | Bonus |
| `feature/barcode-catalogue` | Barcode scan fills a reusable catalogue | — | Bonus |
| `feature/delivery-order` | Ordered list of stops → loading sequence | `SamDana-maker` | Done (#27, issue #17) |

A dash means nobody has claimed it yet, not that it has no natural owner.

## Open pull requests — work that exists and did not land

Two pull requests are open on purpose rather than forgotten. Both are `SamDana-maker`'s, both have
their full state written on the pull request itself (`SA-28`), and neither is close to `main` any
more — they predate the last stretch and conflict with it. They are listed here because a repository
that shows only what was merged describes a project that went smoothly, and this one did not.

| PR | What it is | Why it is still open |
|---|---|---|
| #36 — `feature/plan-recompute` | `POST /plan/recompute` and `src/quai/incident.py`: replanning a load in progress around the boxes already in the van, after a parcel is reported missing, damaged or added. 671 lines, with tests | Two `CHANGES_REQUESTED` rounds from `MORHI11`. The first was fixed; the second is not — `refuse_impossible_start` checks the stack limits but never `weight_cap()`, so a start already over a stated `max_total_weight` is accepted and every box comes back unplaced with no cause named. Paused on the author, not on a reviewer |
| #41 — `fix/container-max-weight` | Refuses a `NaN` weight limit, maps a bare `NaN` literal to `422` instead of `500`, and relaxes `max_weight` from `gt=0` to `ge=0` so the API accepts the zero the model allows. 167 lines, with tests | Never reviewed. Not on the demo's path — the app sends neither `NaN` nor a zero limit — so it queued behind the final push and did not come back out. All three defects are still present on `main` |

The order in which #36 was handled is the part worth keeping. The landing page advertised
"Replans when a parcel is missing" while nothing in the API could replan. #77 removed the claim
rather than merging this to justify it, and widened the guard in `copy.test.jsx` that had missed it
for two releases. Taking an untrue sentence off the product was the urgent half; the work that would
make it true is still here, unfinished and visible, which is the honest way round.

## Known limitations of the v1 solver

Raised by `SamDana-maker` while reviewing PR #3. Neither is a bug: the plans the solver produces are
physically valid. Both are things it does not yet know about, recorded here so they are chosen rather
than forgotten.

| Limitation | What happens today | Why it matters |
|---|---|---|
| Stacking only knows the weight it was told about | The solver enforces a `max_weight_on` over the whole stack (#17), but a box nobody gave a limit for still carries anything that fits | A washing machine on cartons is a broken load even when the geometry checks out, and the operator has to say so for the solver to know |
| First-fit is greedy, and never reconsiders | A box that fits nowhere is left out, even when reordering earlier boxes would have made room — the mattress in `src/demo.py` is the standing example | Fill rate stays lower than it needs to be (39 % on the demo load). `SA-06` found a model-written plan that fitted all eleven boxes at 46.9 %, so the headroom is real and measured |

Weight-aware stacking was issue #17 (`feature/solver-v2`, row 2): a stated limit is now enforced, and
what is left of that row is fragility the operator never states. The greedy first-fit stays open, for
after phase 1 works end to end — and #17 made it worse rather than better, since the route now decides
what goes in first and size only breaks the ties: the demo load drops from 39 % to 21 % once its boxes
are dealt round-robin over three stops. Both figures are pinned by `TestTheDemoLoad` in
`tests/test_solver.py`, because the drop belongs to the split that produced it and other splits of the
same boxes go lower still. That is the right trade (a load nobody can unload is not a good load), but
it is the strongest argument yet for revisiting first fit.

## Course checkpoints

| Session | Expected state on GitHub |
|---|---|
| 1–2 | Repository, README, structure, first runnable commit pushed |
| 3 | Branches, first PR reviewed and merged |
| 4 | Development continues through PRs, documentation kept up to date |
| 5 | Several tested prompt versions, rubric, real scores |
| 6 | API integration, failure modes, final README, oral defence |
