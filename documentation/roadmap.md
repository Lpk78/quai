# Roadmap

Each step is a branch and a Pull Request. The AI layer comes second on purpose: it plugs into a system
that already works.

Owners follow the area split in `CLAUDE.md`, and each PR is reviewed by the other member named there.

## Phase 1 — The system works without AI

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 1 | #5 | `feature/solver-v1` | Boxes + container model, placement without overlap | `SamDana-maker` | `MORHI11` | In review (#3) |
| 2 | #6 | `feature/api-server` | FastAPI exposing the solver and the translation, key server-side | `SamDana-maker` | `MORHI11` | To do |
| 3 | #7 | `feature/3d-view` | 3D supervisor view of the plan | `MORHI11` | `Lpk78` | To do |
| 4 | #8 | `feature/box-form` | Box entry form: dimensions, weight, quantity, container | `MORHI11` | `Lpk78` | To do |

## Phase 2 — The AI layer

| # | Issue | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|---|
| 5 | #9 | `docs/test-sentences` | Fixed test sentences + expected JSON, including injection cases | `Lpk78` | `SamDana-maker` | To do |
| 6 | #10 | `feature/constraint-schema` | Strict JSON schema for constraints, validated before the solver | `Lpk78` | `SamDana-maker` | To do |
| 7 | #11 | `feature/prompt-evaluation` | Script scoring a prompt version on the fixed inputs | `Lpk78` | `SamDana-maker` | To do |
| 8 | #12 | `prompt/v1-zero-shot` | First constraint-translation prompt + real scores | `Lpk78` | `SamDana-maker` | To do |

## Later — not yet opened as issues

| Branch | Deliverable | Status |
|---|---|---|
| `feature/operator-mode` | Step-by-step loading view + recomputation on incident | To do |
| `experiment/llm-only-placement` | LLM vs solver comparison, logged in `failures.md` | To do |
| `feature/dimension-scan` | Phone photo + scale marker → box dimensions | Bonus |
| `feature/barcode-catalogue` | Barcode scan fills a reusable catalogue | Bonus |
| `feature/delivery-order` | Ordered list of stops → loading sequence | Bonus |

## Course checkpoints

| Session | Expected state on GitHub |
|---|---|
| 1–2 | Repository, README, structure, first runnable commit pushed |
| 3 | Branches, first PR reviewed and merged |
| 4 | Development continues through PRs, documentation kept up to date |
| 5 | Several tested prompt versions, rubric, real scores |
| 6 | API integration, failure modes, final README, oral defence |
