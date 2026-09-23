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
