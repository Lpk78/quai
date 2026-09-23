# Roadmap

Each step is a branch and a Pull Request. The AI layer comes fifth on purpose: it plugs into a system
that already works.

| # | Branch | Deliverable | Owner | Reviewer | Status |
|---|---|---|---|---|---|
| 1 | `feature/solver-v1` | Boxes + container model, placement without overlap | | | To do |
| 2 | `feature/3d-view` | 3D supervisor view of the plan | | | To do |
| 3 | `feature/operator-mode` | Step-by-step loading view + recomputation on incident | | | To do |
| 4 | `prompt/v1-zero-shot` | First constraint-translation prompt + test inputs + scores | | | To do |
| 5 | `feature/constraint-translation` | Spoken sentence → validated JSON → solver | | | To do |
| 6 | `experiment/llm-only-placement` | LLM vs solver comparison, logged in `failures.md` | | | To do |
| 7 | `feature/dimension-scan` | Phone photo + scale marker → box dimensions | | | Bonus |
| 8 | `feature/barcode-catalogue` | Barcode scan fills a reusable catalogue | | | Bonus |
| 9 | `feature/delivery-order` | Ordered list of stops → loading sequence | | | Bonus |

## Course checkpoints

| Session | Expected state on GitHub |
|---|---|
| 1–2 | Repository, README, structure, first runnable commit pushed |
| 3 | Branches, first PR reviewed and merged |
| 4 | Development continues through PRs, documentation kept up to date |
| 5 | Several tested prompt versions, rubric, real scores |
| 6 | API integration, failure modes, final README, oral defence |
