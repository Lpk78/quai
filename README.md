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

**Constraints (optional).** `POST /plan` also accepts a `constraints` list, in the shape
`quai.constraints.parse()` validates — so what the operator dictated can reach the plan:

```bash
curl -X POST http://127.0.0.1:8000/plan -H "Content-Type: application/json" -d '{
  "container": {"length": 300, "width": 170, "height": 170},
  "boxes": [{"id": "toolbox", "length": 100, "width": 85, "height": 85, "weight": 20},
            {"id": "b1", "length": 85, "width": 85, "height": 85, "weight": 30}],
  "constraints": [{"type": "load_last", "item": "toolbox"}]
}'
```

`load_last` is the one type this endpoint passes to the solver today: the toolbox moves from `x: 0`,
loaded first against the back wall, to the far end of the load where the doors are. Omit
`constraints` and the endpoint behaves exactly as it did before.

Every other type comes back in `not_applied` with the reason, rather than being dropped in
silence — a plan that quietly ignored what the operator said is the one answer this layer must
not give:

```json
{"placements": [...], "fill_rate": 0.42, "not_applied": [
  {"type": "on_top", "item": "b1",
   "reason": "the solver cannot honour on_top yet and refuses to plan with it rather than drop it; issue #29"}]}
```

Two different reasons appear there. `at_bottom`, `keep_upright`, `max_stack_height`,
`not_stackable` and `on_top` are refused by the solver itself (issue #29). `max_weight_on` and
`max_total_weight` the solver honours, but this endpoint does not hand them over yet; `unload_at`
it honours too, but this request carries no route, and the stop order it needs is an input rather
than something to invent.
All three are roadmap row 12 (#19).

Being reported is for constraints that are *valid but unwired*. A malformed one is a `422`, even
when it is a type the endpoint would not have passed on anyway: a missing or undeclared field, a
limit that is not a positive finite number, an `item` that is not in the load, an unknown type. The
whole list is checked before any of it is applied or reported, by
`quai.constraints.find_problems` rather than a second copy of the rules — so one bad constraint
refuses the request instead of yielding a plan built from the half that parsed. The one thing not
checked is whether an `unload_at` names a real stop, because this request carries no route to check
it against.

`POST /constraints` takes one operator sentence plus the manifest (the items currently in the load) and
the route (the stops, in delivery order), and returns the validated constraint JSON that
`quai.constraints.parse()` produced from it — the same shape documented as the *Output contract* in
`documentation/prompt_evaluation.md`. It calls the production constraint-translation prompt
(`prompts/constraint-translation/v4_few_shot.md`) with `claude-haiku-4-5-20251001` at temperature 0, the
key read from `.env`:

```bash
curl -X POST http://127.0.0.1:8000/constraints -H "Content-Type: application/json" -d '{
  "text": "The washing machine stays at the bottom and comes off at Le Havre.",
  "manifest": [
    {"id": "B1", "label": "washing machine", "length": 60, "width": 60, "height": 85, "weight": 70}
  ],
  "stops": [
    {"id": "S1", "name": "Rouen"},
    {"id": "S2", "name": "Le Havre"}
  ]
}'
```

```json
{"constraints": [{"type": "at_bottom", "item": "B1"},
                 {"type": "unload_at", "item": "B1", "stop": "S2"}],
 "unresolved": []}
```

`text` left empty or blank is a `422`. A reply from the model that is not valid JSON, or that does
not match the contract, never reaches the caller: it is a `502` with the validation problem. A lost
call (rate limit, refusal, network error, after retries) is a `503`. CORS uses the same allowlist as
`/plan` — not authentication; tracked as a gap on issue #19.


### The web app

```bash
cd web && npm install && npm run dev      # http://localhost:5173
```

`/` is the landing page and `/login` the way into the app: it reads an operator card shaped
`QUAI:OPERATOR:<id>` off a QR code with the camera, and signs the operator in by name. Where there
is no camera the same code can be typed in, which is how the phone demo below signs in. `/app` is
the application shell, and `/app/plan` asks the solver for a plan and shows it: where each box goes,
and which ones did not fit. It needs the API running (`uvicorn server:app --app-dir src`), and reads
its address from `VITE_API_URL`, defaulting to `http://127.0.0.1:8000`. Screenshots at phone width
are in `documentation/screenshots/`.

The 3D view of that plan is issue #7 and entering your own boxes is #8; until then the screen plans
the same eleven-box demo load as `src/demo.py`, and says so.

### Phone demo

Both servers listen on localhost by default, which a phone cannot reach, and on a phone `127.0.0.1`
is the phone — so the app also has to be told where the API is:

```bash
LAN=$(ipconfig getifaddr en0)                                 # e.g. 192.168.1.201

QUAI_LAN_ORIGIN="http://$LAN:5173" \
  uvicorn server:app --app-dir src --host 0.0.0.0             # API: http://<LAN>:8000

cd web && VITE_API_URL="http://$LAN:8000" npm run dev:phone   # app: http://<LAN>:5173
```

Then open `http://<LAN>:5173` on the phone. `QUAI_LAN_ORIGIN` is what puts that origin on the API's
CORS allowlist (`DEV_ORIGINS` in `src/server.py`), which otherwise only knows localhost; it falls
back to the address this was written on, so the variable is what keeps it working after DHCP hands
out a different one.

**The camera does not work over this URL.** `getUserMedia` is only available in a secure context,
and `http://` on a LAN address is not one — so `/login` cannot reach the camera from the phone and
offers manual code entry instead. Scanning works at `http://localhost:5173` on the Mac, where
localhost counts as secure. Serving the LAN over HTTPS is not built; see
`documentation/failures.md`.

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

It serves on `http://localhost:5173`: `/` is the landing page, `/app` shows today's van and its boxes,
and `/app/dictate` turns a spoken or typed sentence into constraints through `POST /constraints`
(`web/src/api.js`, origin from `VITE_API_URL`, `http://127.0.0.1:8000` by default). The API server above
must be running for the app to reach the solver — the two are separate processes, and the dev server's
origin is allowed by the `CORSMiddleware` in `src/server.py`.

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
