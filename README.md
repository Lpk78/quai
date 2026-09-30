# QUAI

**Constraint-driven 3D bin packing with natural-language input and live plan recomputation.**

> Status: project scaffold (Session 2 checkpoint). Nothing below "Current scope" works yet.

## Project

QUAI is a load-planning tool for logistics operators (trucks, containers, pallets).
An operator describes loading constraints in plain language ("the fridges go in last, nothing on top of the glass"),
a deterministic 3D solver computes the placement, and a step-by-step view tells the forklift operator
which item to load next and where. When reality changes on the dock (a missing parcel, a damaged box),
the plan is recomputed live.

## Objective

3D bin-packing software already exists, yet it is rarely used on loading docks: entering constraints
takes too long, and the plan breaks as soon as reality differs from it. QUAI targets those two blockers:

1. **Constraint entry** — natural language translated by an LLM into strict, validated JSON.
2. **Plan fragility** — fast recomputation when an incident happens during loading.

Core design rule: **the LLM never computes placement.** It translates constraints in and explains the
solver's output back in plain language. Placement comes from a deterministic solver, because an LLM
produces plausible but geometrically invalid, non-reproducible layouts (see `documentation/`).

## Team

| Name | GitHub | Main area |
|---|---|---|
| Léo-Paul Kerrinckx | @Lpk78 | _to fill_ |
| _to fill_ | @SamDana-maker | _to fill_ |
| _to fill_ | _@handle_ | _to fill_ |

## Tools

- Python 3.11+ (solver, LLM translation layer, evaluation scripts)
- Git, GitHub, GitHub CLI (`gh`)
- VS Code
- LLM in the product: Claude, through the Anthropic API (constraint translation and plan explanation only)
- AI assistant used during development: Claude Code in the terminal (see `documentation/ai_usage.md`)

## Installation / Access

Prerequisites: Python 3.11 or newer, Git.

```bash
git clone https://github.com/Lpk78/quai.git
cd quai
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then fill in your own API key; never commit .env
```

## Run

```bash
python3 src/main.py
```

Expected output:

```
QUAI starts successfully.
```

Score a prompt version on the fixed test inputs (needs `ANTHROPIC_API_KEY` in `.env`):

```bash
python3 src/evaluate_prompt.py prompts/constraint-translation/v1_zero_shot.md
```

Each sentence is translated three times, so that a prompt which only usually works is not scored as
one that works. It prints one line per sentence, the seven rubric criteria, how many of the three
runs passed, and the row to paste into the results table of `documentation/prompt_evaluation.md`.
With no key it says so and prints no scores. The method is described in that document, under
*Running an evaluation*.

## Current scope

The smallest useful version: a hand-typed list of boxes and one container, a solver that places them
without overlap, and a 3D view of the result. No scanning, no LLM yet.

## Project Structure

```
.
├── README.md              ← you are here
├── CONTRIBUTING.md        ← team rules: branches, commits, Pull Requests, reviews
├── src/                   ← project code
├── prompts/               ← every prompt version, never overwritten
├── outputs/               ← generated results (ignored by Git, folder kept)
├── notebooks/             ← exploration only
├── assets/                ← images, 3D models, demo material
└── documentation/         ← journal, prompt evaluation, failures, AI usage, roadmap
```

## AI Usage

_To complete as the project evolves._ Summary so far: AI was used to explore and challenge project ideas
(see `documentation/journal.md`). In the product, AI is limited to constraint translation and plan
explanation.

## Main Challenges

_To complete._ See `documentation/failures.md`.

## Final Result

_To complete at the end of the course._

## Future Improvements

_To complete at the end of the course._
