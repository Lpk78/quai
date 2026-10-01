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
| Léo-Paul Kerrinckx | @Lpk78 | AI layer: prompts, evaluation, constraint translation |
| _to fill_ | @SamDana-maker | Server: solver, FastAPI, Supabase database, routes |
| _to fill_ | @MORHI11 | Interface: mobile app, 3D view, operator mode, landing page |

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

### API server

```bash
uvicorn server:app --app-dir src --reload
```

The server listens on `http://127.0.0.1:8000`, and the interactive docs are at `/docs`.

`POST /plan` takes a container and a list of boxes (lengths in cm, weights in kg) and returns the placements, the unplaced boxes and the fill rate.
`max_weight` is optional:

```bash
curl -X POST http://127.0.0.1:8000/plan -H "Content-Type: application/json" -d '{
  "container": {"length": 300, "width": 170, "height": 170, "max_weight": 1200},
  "boxes": [
    {"id": "washer", "length": 60, "width": 60, "height": 85, "weight": 70},
    {"id": "sofa", "length": 200, "width": 90, "height": 80, "weight": 45}
  ]
}'
```

```json
{"placements": [{"id": "sofa", "x": 0, "y": 0, "z": 0, "dx": 200, "dy": 90, "dz": 80},
                {"id": "washer", "x": 0, "y": 90, "z": 0, "dx": 60, "dy": 60, "dz": 85}],
 "unplaced": [], "fill_rate": 0.2013840830449827, "total_weight": 115.0}
```

A box that fits nowhere is listed in `unplaced`; it is not an error. Invalid input (a zero or negative
dimension, a negative weight, duplicate box ids, a missing field) returns `422` with the reason as JSON.

`POST /plan/recompute` replans a load that is already half in the van. It takes what is already loaded
(with the positions the operator put it in), what is still on the dock, and the one thing that just
changed — a box `missing`, `damaged` or `added`. The boxes already in the vehicle never move; only what
is left is planned, against the same constraints and the same stop order as the first plan.

```bash
curl -X POST http://127.0.0.1:8000/plan/recompute -H "Content-Type: application/json" -d '{
  "container": {"length": 300, "width": 170, "height": 170, "max_weight": 1200},
  "loaded": [{"box": {"id": "sofa", "length": 200, "width": 90, "height": 80, "weight": 45},
              "x": 0, "y": 0, "z": 0, "dx": 200, "dy": 90, "dz": 80}],
  "waiting": [{"id": "washer", "length": 60, "width": 60, "height": 85, "weight": 70},
              {"id": "tv", "length": 130, "width": 20, "height": 80, "weight": 15}],
  "incident": {"kind": "damaged", "box_id": "washer"}
}'
```

```json
{"placements": [{"id": "sofa", "x": 0, "y": 0, "z": 0, "dx": 200, "dy": 90, "dz": 80},
                {"id": "tv", "x": 0, "y": 90, "z": 0, "dx": 130, "dy": 20, "dz": 80}],
 "unplaced": [], "fill_rate": 0.190080738177624, "total_weight": 60.0}
```

That is a real response: the sofa keeps the place the operator put it in, the damaged washing machine is
out of the plan, and only the television is placed around what was already there.

| incident | still on the dock | already in the vehicle |
|---|---|---|
| `missing` | cannot be found, so it leaves the plan | refused: a box in the van is not missing |
| `damaged` | unusable, so it leaves the plan | it comes out, and the space it frees is replanned |
| `added` | refused: it is already in the plan | refused: it is already in the vehicle |

`added` carries the box itself rather than just an id, because dimensions and weight cannot be inferred
from a name. `missing` on a box the operator says is already loaded is refused rather than guessed: the
box is either in the van or it is not, and the two readings give different plans — the operator is
standing next to the vehicle and can say which. `constraints` are optional; when given, `stops` must come
with them, and the whole set is re-validated against the load as it now stands, because a box may have
left it.

### Prompt evaluation

Score a prompt version on the fixed test inputs (needs `ANTHROPIC_API_KEY` and `LLM_MODEL` in
`.env`; neither has a default):

```bash
python3 src/evaluate_prompt.py prompts/constraint-translation/v1_zero_shot.md
```

Each sentence is translated three times, so that a prompt which only usually works is not scored as
one that works. It prints one line per sentence, the eight rubric criteria, how many of the three
runs passed, and the row to paste into the results table of `documentation/prompt_evaluation.md`.
With no key it says so and prints no scores. The method is described in that document, under
*Running an evaluation*.

### Web app

The front end lives in `web/`. It needs Node 20 or later.

```bash
cd web
npm install
npm run dev
```

It serves on `http://localhost:5173`: `/` is the landing page and `/app` is the application. The API
server above must be running for the app to reach the solver — the two are separate processes, and the
dev server's origin is allowed by the `CORSMiddleware` in `src/server.py`.

| Command | What it does |
|---|---|
| `npm run dev` | dev server with hot reload |
| `npm run build` | production bundle in `web/dist/` |
| `npm run preview` | serve that bundle, to check the PWA as it ships |
| `npm test` | unit tests (routing, the copy rules and the colour tokens) |
| `npm run build:tokens` | regenerate `src/tokens.css` from `assets/brand/tokens.json` |

**Installing it on a phone.** The app is a PWA: run `npm run build && npm run preview`, open it on the
phone over the same network, and use the browser's *Add to home screen*. It then opens at `/app` in its
own window. Installation needs HTTPS or `localhost`, so a plain LAN address will not offer it.

**Styling.** Every colour and font comes from `assets/brand/tokens.json` through the generated
`web/src/tokens.css` — never typed by hand. The rules for using them are in `documentation/design.md`,
including the two accessibility rules the interface must follow and the copy rules for anything the
product says about itself. `npm test` checks both.

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
│   └── brand/             ← logo, app icon, design tokens, visual references
├── web/                   ← React + Vite web app (landing page, operator app, PWA)
└── documentation/         ← journal, design system, prompt evaluation, failures, AI usage, roadmap
```

## Design

The visual identity lives in `assets/brand/` and the rules for using it in
`documentation/design.md`: colours, typography, logo, illustration style and interface rules.

`assets/brand/tokens.json` is the machine-readable source for colours and fonts. The PNGs in
`assets/brand/reference/` are renderings for mood and layout, not specifications — never take a
colour out of them by eyedropper.

Two rules are worth knowing before writing any interface code, because the supplied mockups break
both: **text on orange is navy `#102238`, never white**, and **small orange text is `#C2410C`**,
not the primary `#FF8A00`. `tests/test_brand.py` enforces these and every other contrast ratio
the design document claims.

`design.md` also carries the **copy rules** — one slogan, never claiming the AI plans the load or orders
the stops, and no features the app does not have. Read them before writing any user-facing text.

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
