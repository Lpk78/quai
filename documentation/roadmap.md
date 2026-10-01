# Roadmap

Each step is a branch and a Pull Request. The AI layer comes second on purpose: it plugs into a system
that already works.

Owners follow the area split in `CLAUDE.md`, and each PR is reviewed by the other member named there.

## Phase 1 — The system works without AI

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 1 | #5 | `feature/solver-v1` | Boxes + container model, placement without overlap | `Lpk78` | `SamDana-maker` | Done (#3) |
| 2 | #17 | `feature/solver-v2` | Stack weight limit + stop-ordered loading (`SA-05`) | `SamDana-maker` | `MORHI11` | In review (#27) |
| 3 | #6 | `feature/solver-api` | FastAPI exposing the solver over `POST /plan` | `SamDana-maker` | `MORHI11` | In review (#16) |
| 4 | #18 | `feature/web-app` | React + Vite app installable on a phone: `/` landing, `/app` shell (`HY-01`) | `MORHI11` | `Lpk78` | In review (#33) |
| 5 | #7 | `feature/3d-view` | 3D supervisor view of the plan | `MORHI11` | `Lpk78` | To do |
| 6 | #8 | `feature/box-form` | Box entry form: dimensions, weight, quantity, container | `MORHI11` | `Lpk78` | To do |

Row 1 is the one place where the owner column does not mean "wrote it": `Lpk78` wrote the v1 solver,
`SamDana-maker` reviewed it in #3, and owns the solver from there on — maintenance and extensions,
starting with row 2.

## Phase 2 — The AI layer

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 7 | #9 | `docs/constraint-test-sentences` | Fixed test sentences + expected JSON, including injection cases | `Lpk78` | `SamDana-maker` | Done (#14) |
| 8 | #10 | `feature/constraint-schema` | Strict JSON schema for constraints, validated before the solver | `Lpk78` | `SamDana-maker` | In review (#21) |
| 9 | #11 | `feature/prompt-evaluation` | Script scoring a prompt version on the fixed inputs | `Lpk78` | `SamDana-maker` | In review (#22) |
| 10 | #12 | `prompt/constraint-translation-v5-bounded-examples` | The `constraint-translation` family, v1 to v5, each with real scores; v4 stays in production (`documentation/failures.md`) | `Lpk78` | `SamDana-maker` | In review (#43) |
| 11 | #19 | `feature/constraint-translation` | Spoken sentence → validated JSON → solver, over `POST /constraints` (`LP-11`) | `Lpk78` | `SamDana-maker` | To do |

Row 11 is the feature the whole AI layer builds towards; rows 7 to 10 are what make it possible. It is
where the prompt, the schema and the solver become one path, behind `POST /constraints` on the server
from row 3. #10 points at this row.

Row 9 is branched off row 8 rather than off `main`: C1 of the rubric is `quai.constraints.parse()`,
so #22 has to be merged after #21.

## Later — not yet opened as issues

| Branch | Deliverable | Owner | Status |
|---|---|---|---|
| `feature/operator-mode` | Step-by-step loading view + recomputation on incident | — | To do |
| `experiment/llm-only-placement` | LLM vs solver comparison, logged in `failures.md` | `SamDana-maker` | To do (`SA-06`) |
| `feature/dimension-scan` | Phone photo + scale marker → box dimensions | — | Bonus |
| `feature/barcode-catalogue` | Barcode scan fills a reusable catalogue | — | Bonus |
| `feature/delivery-order` | Ordered list of stops → loading sequence | `SamDana-maker` | Done in #17 |

A dash means nobody has claimed it yet, not that it has no natural owner.

## Known limitations of the v1 solver

Raised by `SamDana-maker` while reviewing PR #3. Neither is a bug: the plans the solver produces are
physically valid. Both are things it does not yet know about, recorded here so they are chosen rather
than forgotten.

| Limitation | What happens today | Why it matters |
|---|---|---|
| Stacking only knows the weight it was told about | The solver enforces a `max_weight_on` over the whole stack (#17), but a box nobody gave a limit for still carries anything that fits | A washing machine on cartons is a broken load even when the geometry checks out, and the operator has to say so for the solver to know |
| First-fit is greedy, and never reconsiders | A box that fits nowhere is left out, even when reordering earlier boxes would have made room — the mattress in `src/demo.py` is the standing example | Fill rate stays lower than it needs to be (39 % on the demo load) |

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
