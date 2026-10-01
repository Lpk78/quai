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

`POST /route` takes the stops of a delivery list as addresses, **in the order they will be driven**, and
returns what a map needs: each stop geocoded, the road geometry, the driving time to each stop, and the
totals. `departure_time` is optional; give it and each stop also carries an absolute `eta`.

```bash
curl -X POST http://127.0.0.1:8000/route -H "Content-Type: application/json" -d '{
  "stops": [
    {"id": "S1", "address": "8 boulevard du Port, Amiens"},
    {"id": "S2", "address": "1 rue de la Paix, Paris"}
  ],
  "departure_time": "2026-10-02T08:00:00+02:00"
}'
```

```json
{"stops": [{"id": "S1", "address": "8 boulevard du Port, Amiens",
            "label": "8 Boulevard du Port 80000 Amiens", "lon": 2.290084, "lat": 49.897442,
            "eta_seconds": 0.0, "eta": "2026-10-02T08:00:00+02:00"},
           {"id": "S2", "address": "1 rue de la Paix, Paris", "label": "1 Rue de la Paix 75002 Paris",
            "lon": 2.33031, "lat": 48.868546,
            "eta_seconds": 6179.4, "eta": "2026-10-02T09:42:59.400000+02:00"}],
 "geometry": {"type": "LineString", "coordinates": [[2.290021, 49.897463], "… 3421 more …"]},
 "total_distance_m": 140494.9, "total_duration_s": 6179.4}
```

That response is a real one, run against both services on 2026-10-01. The figures will drift as the
road data behind OSRM changes, so treat them as the shape of the answer rather than as constants.

**QUAI never reorders the stops.** The order arrives with the delivery list and the solver loads the
vehicle against it, so a route drawn in any other order would describe a journey the van was not packed
for. The router is asked for `/route`, which drives the points as given — not `/trip`, which would return
a shorter journey in an order of its own choosing.

#### The two services this uses, and what they cost us

Neither is ours, both are free, and both are called at request time with no caching.

| Service | What it does | Limits that matter |
|---|---|---|
| [`api-adresse.data.gouv.fr`](https://adresse.data.gouv.fr/api-doc/adresse) (Base Adresse Nationale) | address → point | **France only.** An address anywhere else returns no match and the request is refused naming it. Rate-limited at 50 requests/second per IP. One call per stop. |
| [`router.project-osrm.org`](https://project-osrm.org/) (OSRM demo server) | points → road geometry, distance, duration | A **demo** server with no uptime promise and no support: fine for a student project, not for production. Driving profile only. One call per route. |

Consequences worth knowing before relying on it:

- **Estimated arrival times are driving time only.** Nothing in QUAI knows yet how long a stop takes to
  unload, so the ETA of the last stop of a long round will be optimistic.
- **Traffic is not modelled.** OSRM's durations come from road speeds, not from conditions on the day.
- **A stop that fails to geocode fails the whole request** (`422`, naming the address), because a route
  through an unknown point is not a route.
- **When a service is slow or down**, the request fails rather than hanging: `504` if it did not answer in
  time, `502` if it answered badly. Both carry a sentence saying which service and why.
- The tests mock both services, so the suite neither needs the network nor tests somebody else's uptime.

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
