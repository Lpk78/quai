# Roadmap

Each step is a branch and a Pull Request. The AI layer comes second on purpose: it plugs into a system
that already works.

Owners follow the area split in `CLAUDE.md`, and each PR is reviewed by the other member named there.

## Phase 1 — The system works without AI

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 1 | #5 | `feature/solver-v1` | Boxes + container model, placement without overlap | `Lpk78` | `SamDana-maker` | Done (#3) |
| 2 | #6 | `feature/api-server` | FastAPI exposing the solver and the translation, key server-side | `SamDana-maker` | `MORHI11` | To do |
| 3 | #7 | `feature/3d-view` | 3D supervisor view of the plan | `MORHI11` | `Lpk78` | To do |
| 4 | #8 | `feature/box-form` | Box entry form: dimensions, weight, quantity, container | `MORHI11` | `Lpk78` | To do |

Row 1 is the one place where the owner column does not mean "wrote it": `Lpk78` wrote the v1 solver,
`SamDana-maker` reviewed it in #3, and owns the solver from there on — maintenance and extensions.

## Phase 2 — The AI layer

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 5 | #9 | `docs/constraint-test-sentences` | Fixed test sentences + expected JSON, including injection cases | `Lpk78` | `SamDana-maker` | In review (#14) |
| 6 | #10 | `feature/constraint-schema` | Strict JSON schema for constraints, validated before the solver | `Lpk78` | `SamDana-maker` | To do |
| 7 | #11 | `feature/prompt-evaluation` | Script scoring a prompt version on the fixed inputs | `Lpk78` | `SamDana-maker` | To do |
| 8 | #12 | `prompt/constraint-translation-v1-zero-shot` | First prompt of the family, `prompts/constraint-translation/v1_zero_shot.md`, + real scores | `Lpk78` | `SamDana-maker` | To do |
| 9 | — | `feature/constraint-translation` | Spoken sentence → validated JSON → solver | `Lpk78` | `SamDana-maker` | To do |

Row 9 is the feature the whole AI layer builds towards; rows 5 to 8 are what make it possible. It has
no issue yet — it is opened once v1 has been scored, so that what it wires together is known. #10
points at this row.

## Later — not yet opened as issues

| Branch | Deliverable | Status |
|---|---|---|
| `feature/operator-mode` | Step-by-step loading view + recomputation on incident | To do |
| `experiment/llm-only-placement` | LLM vs solver comparison, logged in `failures.md` | To do |
| `feature/dimension-scan` | Phone photo + scale marker → box dimensions | Bonus |
| `feature/barcode-catalogue` | Barcode scan fills a reusable catalogue | Bonus |
| `feature/delivery-order` | Ordered list of stops → loading sequence | Bonus |

## Known limitations of the v1 solver

Raised by `SamDana-maker` while reviewing PR #3. Neither is a bug: the plans the solver produces are
physically valid. Both are things it does not yet know about, recorded here so they are chosen rather
than forgotten.

| Limitation | What happens today | Why it matters |
|---|---|---|
| Stacking ignores weight and fragility | Boxes are ordered by volume only, so a heavy box may sit on a light or fragile one | A washing machine on cartons is a broken load even when the geometry checks out |
| First-fit is greedy, and never reconsiders | A box that fits nowhere is left out, even when reordering earlier boxes would have made room — the mattress in `src/demo.py` is the standing example | Fill rate stays lower than it needs to be (39 % on the demo load) |

Both are candidates for `feature/solver-v2`, after phase 1 works end to end.

## Course checkpoints

| Session | Expected state on GitHub |
|---|---|
| 1–2 | Repository, README, structure, first runnable commit pushed |
| 3 | Branches, first PR reviewed and merged |
| 4 | Development continues through PRs, documentation kept up to date |
| 5 | Several tested prompt versions, rubric, real scores |
| 6 | API integration, failure modes, final README, oral defence |
