# Project journal

How the idea evolved and why each decision was made. One entry per meaningful decision, newest last.

---

## Idea exploration (before Session 2)

We used an AI assistant (Claude) to generate and challenge project ideas against the course guidelines.
Ideas considered, in order:

| Idea | What it was | Why we dropped it |
|---|---|---|
| PromptCI | A secret-keeping "Guardian" prompt attacked by prompt injections, with a CI that scores each prompt version on every PR | Strong for grading, but not a real product that helps anyone |
| Panel Zéro | Market research answered by hundreds of synthetic personas, calibrated against a real survey | Interesting, but we wanted more concrete utility |
| Le Dossier | An agent that sorts a pile of administrative letters into cases, deadlines and draft replies | Real impact, but heavy OCR and legal-deadline risk |
| L'Organologie | Impossible musical instruments generated from poetic descriptions, where 3D geometry drives the sound | Very original, prototype built, but little practical use |
| Dream map | Recurring dream motifs turned into a navigable 3D map | Same: striking but not useful |
| **QUAI** | **Load planning for logistics with spoken constraints and live recomputation** | **Selected** |

## Decision: QUAI

**Why:** it solves a real, specific problem (planning tools abandoned on loading docks), needs no external
dataset (we measure real objects; container and Euro-pallet sizes are public standards), and gives AI a
precise, defensible role.

**Key architecture decision: the LLM never computes placement.**
An LLM asked to place boxes produces overlapping or out-of-bounds coordinates, gives a different plan on
each call, and cannot say when a load is impossible. A deterministic solver does all three correctly.
The LLM is used where it is strong: turning spoken constraints into strict JSON, and explaining the plan.
We plan to *measure* this with an experiment (LLM-only placement vs solver), which also covers the
"LLM failure modes" requirement.

**Scope decisions:**

- Core: solver + 3D supervisor view, step-by-step operator view, live recomputation, spoken constraints.
- Bonus, each on its own branch once the core works: dimension scanning with a printed scale marker,
  barcode catalogue, ordered delivery-stop import, QR position labels, cost avoided, centre of gravity.
- Rejected: maps and route computation, object recognition without barcodes, tracking chips,
  WMS integration.

## Session 2 — repository setup

- 2026-09-23 — Léo-Paul created the private repository `Lpk78/quai`, pushed the scaffold in three commits and invited Sam.
- From now on, every change goes through a branch and a reviewed Pull Request.

## Session 5 — change of direction: no automatic review bot

- 2026-09-28 — We dropped the idea of an automatic first-pass review from a GitHub Action
  (`claude-review.yml`). It was described in `CLAUDE.md` before it was ever built, and we chose not to
  build it.
- **Why:** a bot comment posted on every PR adds noise without adding judgement, and it invited the
  reviewer to skim the bot's summary instead of reading the diff. The course asks each of us to be able
  to explain any PR we approved, so the reading has to stay with the reviewer.
- **What replaces it:** `/review` now does the checking work locally — it checks out the branch, runs the
  tests and goes through `CONTRIBUTING.md` point by point — then drafts a review that the reviewer reads,
  edits and validates before it is posted from their account. Nothing is posted, approved or merged
  without their explicit answer.
- **Kept from the old design:** the rotation (one reviewer per PR), the Observation / Concern / Suggestion
  format, and the rule that the author never merges their own PR.
- Related branch / PR: `docs/team-automation`, PR #4.

## Session 5 — AI usage recorded per task

- 2026-09-30 — A Pull Request no longer adds a row to `documentation/ai_usage.md`. AI help is recorded in
  the "Outcome" section of the task's own file in `prompts/dev/<ID>_<slug>.md`, and `ai_usage.md` is filled
  once, at the end, from those files.
- **Why:** the same story was being written twice, once in the prompt file and once in the table, and the
  table is a single shared block of lines that every branch appends to — it caused the merge conflict
  between #3 and #4 written up in `documentation/failures.md`. Per-task files cannot conflict.
- **Also in this follow-up:** the PR template checklist now points at `prompts/<family>/`, and reading or
  replying to PR line comments with `gh api` moved from `allow` to `ask`, so a comment is never posted on
  GitHub without one of us saying yes.
- Related branch / PR: `docs/per-task-ai-usage-rule`, follow-up to PR #4.

## Session 5 — Day summary, 2026-09-30

The day phase 1 and phase 2 started for real: the solver landed on `main`, the team rules and the
evaluation material were merged, and the first server and schema work went into review.

**What we built**

- **Solver v1** (#3) is on `main`: boxes and container model, a deterministic first-fit placement and an
  independent validity check. #5 was closed as completed by it.
- **Team automation** (#4): the `/task`, `/review`, `/fix-review` and `/prompt-version` skills, the
  permission file and the `tests.yml` workflow, which now runs the tests on every PR.
- **Evaluation material** (#14): the reference manifest, the output contract, 25 test sentences with their
  expected JSON and the seven-criterion rubric, fixed before any prompt exists. During review, the contract
  also gained the route rules the solver needs (stack weight limit, route order, default stop, `load_last`
  within a stop).
- **Roadmap** (#13): every phase 1 and 2 task has an owner, a reviewer and an issue. New issues opened
  today: #15, #17 (`SA-05`), #18 (`HY-01`), #19 (`LP-11`).
- **Rule change** (#20): AI help is recorded per task in `prompts/dev/`, not as a row in `ai_usage.md`
  (see the entry above).

**Who did what**

- **Léo-Paul (`Lpk78`)** wrote #3, #4, #13, #14 and #20, answered the reviews on each, and opened #21
  (constraint schema) and #22 (prompt evaluation script), both in review.
- **Sam (`SamDana-maker`)** reviewed, approved and merged #3, #4, #13, #14 and #20; requested changes on
  #21 (allow several `load_last` items per stop before prompt v1 is scored) and on #2 (out of date with
  `main`). Opened #16 (`SA-04`, FastAPI `POST /plan`) and #23 (`SA-10`, container validation, closes #15).
- **`MORHI11`** is the reviewer of #16 and #23 and owns #18 (the web app); none of his work was merged
  today.

**What failed**

- **Merge conflicts on `ai_usage.md`, three times.** Between #3 and #4 (written up in `failures.md`),
  then #13 and #14, then #16 against the result. Every branch appended a row at the same last line of one
  shared table. The fix was a rule rather than more careful merging: #20 stopped PRs from adding rows.
- **A test that could not fail.** In #14, the parser for the contract table also read the manifest table,
  so `B1`–`B10` counted as constraint types and `{"type": "B1"}` would have passed. Found in review, fixed
  with a test that fails against the old regex.
- **A branch name that drifted from the roadmap.** `SA-04` was opened on `feature/solver-api` while the
  roadmap said `feature/api-server`; roadmap row 3 was corrected on the PR's branch.

**Pull Requests merged today:** #3, #4, #13, #14, #20. **Still open:** #2, #16, #21, #22, #23.
