# QUAI

**Constraint-driven 3D bin packing with natural-language input.**

## Project

QUAI is a load-planning tool for logistics operators (trucks, containers, pallets).
An operator describes loading constraints in plain language ("the fridges go in last, nothing on top of the glass"),
a deterministic 3D solver computes the placement, and a step-by-step view tells the forklift operator
which item to load next and where.

Recomputing the plan live when reality changes on the dock — a missing parcel, a damaged box — is the
second half of the idea and is **not built**: the API exposes `/plan`, `/constraints` and `/route`,
and nothing replans. See *Current scope* for the line between what runs and what does not.

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
| Sam Dana | @SamDana-maker | Server: solver, FastAPI, routing and the demo fixtures |
| Hippolyte Moraine | @MORHI11 | Interface: mobile app, 3D view, operator mode, landing page |

## Tools

Python 3.11+ for the solver, the translation layer and the evaluation scripts; Node 20+ for the web
app; Git, GitHub and the GitHub CLI (`gh`); VS Code. Everything below is declared in
`requirements.txt`, `requirements-dev.txt` or `web/package.json`, except where said otherwise.

**Server** — `requirements.txt`:

| | What it does here |
|---|---|
| FastAPI | the HTTP API over the solver: `POST /plan`, `/constraints`, `/route` (`src/server.py`) |
| Uvicorn | runs that API locally, and with the certificate for the phone demo |
| httpx | drives FastAPI's `TestClient` in `tests/test_server.py` |
| `anthropic` | the Claude client, used by `src/evaluate_prompt.py` to score a prompt version |
| `unittest` | the Python test runner — 409 tests, from the standard library, no third-party framework |

**Web app** — `web/package.json`:

| | What it does here |
|---|---|
| React, React DOM | the interface |
| Vite, `@vitejs/plugin-react` | dev server, production build, and the HTTPS switch the phone demo needs (`vite.config.js`) |
| React Router | the routes: `/`, `/login`, `/app`, `/app/scan`, `/app/dictate`, `/app/plan`, `/app/route` |
| three.js, `@react-three/fiber`, `@react-three/drei` | the 3D view of the load on `/app/plan` — the volume, the boxes, the camera presets |
| Leaflet, React Leaflet | the map and the round on `/app/route` |
| jsQR | decodes the QR codes the camera reads, shared by `/login` and `/app/scan` |
| Vitest, jsdom, Testing Library | the web test runner and the DOM it runs against — 195 tests |
| `@fontsource/inter`, `@fontsource/plus-jakarta-sans` | the two self-hosted typefaces, so no font is fetched from a third party |

**Build-time only** — `requirements-dev.txt`: NumPy, Pillow and potracer, used by
`assets/brand/logo/build_logo.py` to trace the logo SVGs from the brand sheet, and therefore by the
drift check in `tests/test_brand.py`. They are not runtime dependencies of the product.

**mkcert**, installed once per machine rather than declared in a manifest: it issues the local
certificate in `.certs/` that lets the phone demo run over HTTPS, which is what `/login` needs to
reach the camera at all. `vite.config.js` picks it up when it is there and stays on HTTP when it is
not, so a clone without one still runs. See *Phone demo*.

The two external services the product calls at runtime — the Base Adresse Nationale and OSRM — are
not libraries and are described under *The two services this uses, and what they cost us*.

AI was used in three distinct ways. They are listed apart because what each one is allowed to decide
is different, and only the first is part of the product.

**1 — In the product.** Claude through the Anthropic API, `claude-haiku-4-5-20251001` at temperature
0, for two jobs: turning a sentence into constraints, and explaining the solver's output back in
plain language. **Never for placement.** Positions are computed by the deterministic solver in
`src/quai/`, and the model's reply reaches it only through `quai.constraints.parse()`.

**2 — In development.** Claude Code in the terminal, in three separate sessions, one per team
member. What it produced on each task, how that was checked and what was changed by hand is recorded
per task in `prompts/dev/<ID>_<slug>.md`, and summarised in `documentation/ai_usage.md`.

**3 — In the creative process.** The visual identity is generated rather than drawn:

- **ChatGPT** — the logo, the brand kit, the characters, the vehicles, the environments, the screen
  mockups, the component boards and the isolated renders.
- **Claude** — the 32-second film on the landing page (`web/public/quai-video.mp4`).

Some assets were retouched by hand after generation.

A detailed ten-shot production method had also been written for **Higgsfield**
(`08_HIGGSFIELD/Higgsfield_website_workflow.txt`, in the brand hand-off rather than in this
repository) and was not used: the film that shipped was made with Claude. The document is kept
because the route it describes was real preparation, and dropping it was a decision rather than an
oversight.

What the generated material is allowed to settle is bounded by `documentation/design.md`: the
reference images are renderings for mood and layout, never specifications, and where a mockup
conflicts with the accessibility or copy rules, the rules win — and they did, which is written up
in `documentation/failures.md` under *A brand kit whose own mockups failed accessibility* and
*Mockups that advertised a product we are not building*.

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

`load_last` and `on_top` are the two types this endpoint passes to the solver. `load_last` moves the
toolbox from `x: 0`, loaded first against the back wall, to the far end of the load where the doors
are. `on_top` loads the named box last, into a column nothing stands over — so "this parcel is
fragile, put it on top" reaches the plan. Omit `constraints` and the endpoint behaves exactly as it
did before.

Both need nothing but the boxes, which is the test for belonging here. **`on_top` can leave a box
unplaced**, and that is the honest answer rather than a failure: a box loaded last has only what is
left to go into, so asking it of something that fills the floor — a wrapped sofa — means there is
nowhere clear for it, and it is reported in `unplaced` instead of being forced in.

Every other type comes back in `not_applied` with the reason, rather than being dropped in
silence — a plan that quietly ignored what the operator said is the one answer this layer must
not give:

```json
{"placements": [...], "fill_rate": 0.42, "not_applied": [
  {"type": "at_bottom", "item": "b1",
   "reason": "the solver cannot honour at_bottom yet and refuses to plan with it; issue #29"}]}
```

Two different reasons appear there. `at_bottom`, `keep_upright`, `max_stack_height` and
`not_stackable` are refused by the solver itself (issue #29). `max_weight_on` and
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

Two more, and they are the ones worth recognising on a dock. **`ANTHROPIC_API_KEY` or `LLM_MODEL`
missing** from `.env` — or the `anthropic` package not installed — is a `503` naming both variables:
the server is running, it simply has nothing to translate with. **A key that is present but wrong** is
a `502` saying the model refused the request, because the key passes the server's own check and only
the API can reject it. Neither is reported as an unreachable server: an unhandled exception would
answer `500` through a handler that sits outside the CORS middleware, and a response the browser
cannot read becomes "could not reach the solver" on screen — the one diagnosis that sends you to
restart a server that is working.


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


### The web app

The front end lives in `web/`. It needs Node 20 or later.

```bash
cd web
npm install
npm run dev                               # http://localhost:5173
```

| Command | What it does |
|---|---|
| `npm run dev` | dev server with hot reload |
| `npm run dev:phone` | the same, bound to the LAN so a phone can reach it — see *Phone demo* |
| `npm run build` | production bundle in `web/dist/` |
| `npm run preview` | serve that bundle, to check the PWA as it ships |
| `npm test` | the web unit tests: every screen, the scan and speech paths, the copy rules, the colour tokens |
| `npm run test:watch` | the same, re-run on change |
| `npm run build:tokens` | regenerate `src/tokens.css` from `assets/brand/tokens.json` |

The API server above must be running for the app to reach the solver — they are separate processes,
and the dev server's origin is allowed by the `CORSMiddleware` in `src/server.py`.

`/` is the landing page and `/login` the way into the app: it reads an operator card shaped
`QUAI:OPERATOR:<id>` off a QR code with the camera, and signs the operator in by name. Where there
is no camera the same code can be typed in, which is how the phone demo below signs in. `/app` is
the application shell, and `/app/plan` asks the solver for a plan and shows it: where each box goes,
and which ones did not fit. It needs the API running (`uvicorn server:app --app-dir src`), and reads
its address from `VITE_API_URL`, defaulting to `http://127.0.0.1:8000`. Screenshots at phone width
are in `documentation/screenshots/`.

**`/app/plan`** shows that plan in three dimensions, dressed to the approved mockup (which lives
outside the repository, in the brand hand-off): a switch across to the round, a **Next box** card
naming what to pick up and its real size and weight, camera presets (3D, Top, Left, Right) sized to be
pressed in handling gloves, and a progress panel. **Loaded, next** walks the solver's own loading order
one box at a time and stops at the end.

What it renders is the plan the solver computed — the mockup's photograph of a loaded van is a
marketing render and never replaces the canvas. The green **All items placed** appears only when
nothing was left unplaced *and* no constraint went unapplied; otherwise the real counts are shown,
because a tick over an incomplete plan is the one answer this project refuses.

Entering your own boxes is issue #8; until then the screen plans the same eleven-box demo load as
`src/demo.py`, and says so.

**`/app/dictate`** is where the sentence becomes constraints. The operator speaks or types it, the
screen sends it to `POST /constraints` (`web/src/api.js`, origin from `VITE_API_URL`), and the model's
reply reaches the solver only if `quai.constraints.parse()` validates it — output that fails is
refused, never repaired. The microphone reports what the speech API answered rather than failing in
silence (`HY-19`), and it listens in English whatever the phone is set to (`HY-20`), because the box
labels and stop names exist in one language.

The operator's path through the app is `/app` → `/app/scan` → `/app/dictate` → `/app/plan`: read the
label on the package in your hands, say what to do with it, see where the solver put it. `/app/route`
sits beside that path rather than in it — the round is reference, consulted before driving.

**`/app/route`** draws today's round: the road line, a numbered pin per stop in delivery order, and
the arrival time at each one. Every figure on it comes from `POST /route` — the coordinates, the line,
the distance, the driving time, the times themselves. Nothing is computed in the browser and nothing
is guessed: until the request answers there are no times on screen at all, because an invented arrival
time is the one number an operator would plan their morning around.

It shows the address **as the geocoder matched it**, not as the manifest asked. Three of the eight
round addresses resolve at street level rather than house number, and showing the server's own label is
how a wrong street becomes visible instead of silently trusted. The map tiles are OpenStreetMap's,
credited on the map as their licence asks, and need no key.

The round is in **Paris**, and that is a constraint rather than a preference: `POST /route` geocodes
through the Base Adresse Nationale, which covers France only. The round was Madrid until this screen
existed, and a Spanish address returns a `422` no amount of front-end work can fix.

**`/app/scan`** reads a label shaped `QUAI:BOX:<id>` and shows what the manifest knows about that
box — `QUAI:BOX:QUAI-BOX-0001` is the fragile parcel, 40 × 30 × 25 cm, 8 kg. A code that is not a
QUAI label and a QUAI label for a box that is not on this van are told apart, because they are
different mistakes on a loading dock.

Reading that label is what puts the parcel **in the van**. `BOXES` in `web/src/data/manifest.js` is
the eighteen boxes already loaded; the parcel is held apart from them as `SCANNED_PARCEL`, and a scan
moves it into app state. So `/app/dictate` then asks the model about nineteen boxes and the solver
plans nineteen — without the scan, both see eighteen. The count on `/app` follows the same list, so it
cannot say eighteen while the plan holds nineteen. Scan the same label twice and it is recognised, not
added again.

The scan survives a reload, through `sessionStorage` holding the box id — not a copy of the box, so
`manifest.js` stays the single source of what it measures. `sessionStorage` rather than
`localStorage` because a scan belongs to one sitting: closing the tab ends the round.

The **camera** reads that label since `HY-18`. `/app/scan` and `/login` drive one shared
`QrScanner` (`web/src/scan/QrScanner.jsx`), lifted out of `Login.jsx` rather than written a second
time, and `web/src/scan/scanCode.js` parses what it decodes. The typed field stays underneath it:
a camera that is refused, missing, or on an `http://` LAN address still leaves a way in, and the
screen names which of the three happened instead of showing an empty box.

**Installing it on a phone.** The app is a PWA: run `npm run build && npm run preview`, open it on
the phone over the same network, and use the browser's *Add to home screen*. It then opens at `/app`
in its own window. Installation needs HTTPS or `localhost`, so a plain LAN address will not offer it.

**Styling.** Every colour and font comes from `assets/brand/tokens.json` through the generated
`web/src/tokens.css` — never typed by hand. The rules for using them are in `documentation/design.md`,
including the two accessibility rules the interface must follow and the copy rules for anything the
product says about itself. `npm test` checks both.

### Phone demo

Both servers listen on localhost by default, which a phone cannot reach, and on a phone `127.0.0.1`
is the phone — so the app also has to be told where the API is. It is served over HTTPS, because
`/login` scans a QR code and `getUserMedia` exists only in a secure context: `http://` on a LAN
address is not one, and the camera is then not blocked but absent.

First, once per machine, a certificate for this Mac's own address — `.certs/` is gitignored, since a
private key is not committed and the address is this machine's:

```bash
brew install mkcert && mkcert -install        # a local CA, in this Mac's trust store
LAN=$(ipconfig getifaddr en0)                 # e.g. 192.168.1.201
mkdir -p .certs
mkcert -key-file .certs/key.pem -cert-file .certs/cert.pem localhost 127.0.0.1 ::1 "$LAN"
```

Then, to run:

```bash
QUAI_LAN_ORIGIN="https://$LAN:5173" \
  uvicorn server:app --app-dir src --host 0.0.0.0 \
  --ssl-keyfile .certs/key.pem --ssl-certfile .certs/cert.pem    # API: https://<LAN>:8000

cd web && VITE_API_URL="https://$LAN:8000" npm run dev:phone     # app: https://<LAN>:5173
```

Then open `https://<LAN>:5173` on the phone. `QUAI_LAN_ORIGIN` is what puts that origin on the API's
CORS allowlist (`DEV_ORIGINS` in `src/server.py`), which otherwise only knows localhost; it falls
back to the address this was written on, so the variable is what keeps it working after DHCP hands
out a different one — and what carries the `https://` scheme here. `vite.config.js` picks the
certificate up on its own when `.certs/` exists, and serves plain HTTP when it does not, so a clone
without one still runs.

**The phone has to be told to trust the CA as well.** `mkcert -install` installs the root into this
Mac's trust store and nowhere else. Send `"$(mkcert -CAROOT)/rootCA.pem"` to the phone, install it as
a profile, and on iOS enable it under *Settings → General → About → Certificate Trust Settings* —
installing the profile is not enough on its own. Without that, Safari refuses the certificate and
`/login` falls back to the typed code, which still signs the operator in.

### LLM-only placement experiment

Asks the model to place the demo boxes itself and scores every reply with the solver's own checks
(`SA-06`, needs `ANTHROPIC_API_KEY` and `LLM_MODEL`):

```bash
python3 src/run_placement_experiment.py            # 10 runs at temperature 0, 10 at temperature 1
python3 src/run_placement_experiment.py --runs 2   # a short rehearsal
```

It makes 20 billed calls, so **the run the published figures come from is in the repository**:
`outputs/placement/llm_placement_20261001-141020.json` holds all twenty replies. `TestTheRecordedRun`
in `tests/test_llm_placement.py` re-derives every number `documentation/failures.md` states from those
replies, with today's checks — so reading the result costs nothing, and the table cannot drift from the
evidence behind it. `notebooks/llm_vs_solver.ipynb` explores the same run.

Re-running answers a *different* twenty questions: the model is not reproducible at temperature 0
(that is one of the findings), so a fresh run can neither confirm nor refute the recorded one. Fresh
runs land beside it and stay Git-ignored. What this one found is in `documentation/failures.md` — one
physically valid plan in twenty.

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

### Demo fixture

**The line to say on stage, settled and not to be improvised:**

> **The unmarked carton is fragile, put it on top.**

In English, and naming the carton. Both of those are load-bearing.

The scanned box is `carton, unmarked` — a dull name and no fragility flag, because fragility is
something the operator knows and says, not something the fixture decides. In the plan as the app
builds it, that box sits on the floor with `B13` and `B17` stacked over it. The line above lifts it
85 cm to the top of the load with nothing above it, all nineteen boxes still placed.

**Say it any other way and nothing moves.** *"This one is fragile, put it on top"* comes back
`ambiguous`, with the question *"Which item is fragile?"* — the model is right, since nothing in the
sentence says which box is meant, and an honest `unresolved` is the correct answer to it. It is simply
not the answer anyone wants in front of an audience. `tests/test_demo_fixtures.py` asserts both halves
of the movement and that this line still names the box the fixture actually carries, because a
demonstration whose central moment cannot be asserted is one nobody should rely on.

The data the live demo runs on — one operator card, a Paris round of eight stops, eighteen boxes
already in the van, and the parcel scanned on stage. No key and no network:

```bash
python3 src/demo_fixtures.py
```

It prints the placement table and the fill rate the real solver computes, before and after the
parcel is scanned: **77.8% with the eighteen loaded boxes, 78.2% once the parcel is in**, all
nineteen placed. The route reaches the solver as a `ConstraintSet` built by
`quai.constraints.parse()`, the same path `POST /constraints` feeds, so the numbers come from the
production code and not from a second implementation. Import it as `demo_fixtures` to reuse the
same load elsewhere; `tests/test_demo_fixtures.py` holds the fill rate to the quoted range.

## Current scope

What runs end to end today: an operator signs in at `/login` by scanning an operator card, scans a
parcel label at `/app/scan`, says what to do with the load at `/app/dictate`, and reads the plan the
solver computed at `/app/plan`, one box at a time. `/app/route` shows the round beside that path.
The solver is deterministic; the model never places anything, and its output reaches the solver only
through `quai.constraints.parse()`, which refuses what does not validate rather than repairing it.

What is **not** built. Each of these is marked on the screen that would otherwise imply it, because a
plan that quietly omits something is the one answer this project refuses:

- **Replanning on incident.** The API is `/plan`, `/constraints` and `/route`; nothing recomputes a
  plan around what is already in the van (#36). This is half of the original idea and it is absent.
- **Entering your own boxes** (#8). Every screen plans the same eleven-box demo load from
  `src/demo.py`, and says so where it is shown.
- **Four of the nine constraint types.** The schema accepts nine; the solver honours five
  (`load_last`, `on_top`, `unload_at`, `max_weight_on`, `max_total_weight`) and refuses
  `at_bottom`, `keep_upright`, `max_stack_height` and `not_stackable` rather than dropping them
  silently — they come back in `not_applied` with the reason (#29).
- **Accounts and storage.** Nothing persists between sessions except one scanned parcel id in
  `sessionStorage`. There is no database.

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

**In the product.** Claude, through the Anthropic API, with exactly two jobs: turning a spoken or
typed sentence into constraints, and explaining the solver's output back in plain language. It never
computes placement. Its reply reaches the solver only through `quai.constraints.parse()` — output
that fails validation is refused, never repaired — and the key stays server-side, so the browser only
ever calls our own API.

Five prompt versions, none overwritten, each scored on the same 26 sentences against the same eight
criteria, `claude-haiku-4-5-20251001` at temperature 0, three runs per sentence:

| Version | Total /26 | What changed |
|---|---|---|
| `v1_zero_shot` | 0 | All 78 replies came back inside a ` ```json ` fence, so none parsed |
| `v2_output_format` | 0 | Output section rewritten, rest byte-identical — 78 of 78 fenced again |
| `v3_response_prefill` | 21 | Prompt identical to v2; the request ends on an assistant `{`. 78 of 78 parsed |
| **`v4_few_shot`** | **22** | v3 plus four worked examples. **In production** |
| `v5_bounded_examples` | 21 | Three examples from v3, one bounding another; fixed one sentence, broke two |

The method, the rubric and the full per-criterion table are in `documentation/prompt_evaluation.md`.
A score is recorded only if it was run; the one re-scored number in that document is labelled a
diagnostic and credited to no version.

**During development.** Claude Code in the terminal, recorded per task rather than per Pull Request.
`prompts/dev/` holds 49 task files — 20 `LP-`, 17 `SA-`, 12 `HY-` — each with the prompt as it was
typed, the decisions taken before any code was written, and an Outcome saying what the AI produced,
how it was checked, and what was changed by hand. `documentation/ai_usage.md` is filled from those
files. Reviews are drafted with AI, then read, edited and posted by the human reviewer from their own
account; the author never merges their own Pull Request.

## Main Challenges

Twenty-eight are written up in `documentation/failures.md`, each with what happened, why, what we
tried and what we learned. The ones that changed how we work:

- **Two prompt versions scored 0/26 on a code fence.** Every reply was wrapped in ` ```json `, so
  nothing parsed and no field was ever looked at. v2 rewrote the output instructions and moved the
  number not at all; what fixed it was ending the request on an assistant `{` so the model had
  already started the object. Rewording a prompt and changing how it is delivered are different
  tools, and we had been reaching for the wrong one.
- **Tests that could not fail.** The failure this project kept relearning: a parser regex (#14), a
  stop order (#35), an `on_top` pair (#60), a route-time tile (`HY-17`), and a speech-language
  assertion that jsdom's own `en-US` already satisfied (`HY-20`). Every one was found the same way,
  by changing the code to see whether the test noticed, and it is now the habit — a test is not
  evidence for a change until it has been made to fail against it.
- **The phone demo and the camera could not both work over `http://`.** `getUserMedia` needs a
  secure context and a LAN address is not one, so the camera was absent rather than refused. Solved
  with a local `mkcert` certificate and HTTPS on both servers, which then needed the phone to trust
  the CA as well — the fix was three steps longer than the diagnosis.
- **`Infinity` is valid JSON to Python and crashed the validator.** `json.loads` accepts it, the
  schema did not expect it, and the failure surfaced as a 500 rather than a refusal.
- **A geocoder that answered 200 about the wrong continent.** A Spanish district fuzzy-matched a
  French commune, and OSRM dutifully drove nineteen hours between them. "The endpoint returned 200"
  is not "the endpoint answered the question", and the honest placeholder — an em dash — was already
  right when the data moved underneath it.
- **Shared documents conflict because every branch appends to the end** (#32). `failures.md`,
  `ai_usage.md` and this README collide on almost every merge. The rule that came out of it: keep
  both sides, never pick one.

## Final Result

A working load-planning tool, demonstrated on a phone against a real Paris round.

- **Deterministic solver** in `src/quai/`: placement without overlap, stack weight limits, loading
  order by stop, `on_top` clearance.
- **FastAPI server** exposing `POST /plan`, `POST /constraints` and `POST /route`.
- **React + Vite app**, installable as a PWA: `/` landing page, `/login`, `/app`, `/app/scan`,
  `/app/dictate`, `/app/plan` with a 3D view, `/app/route` with the round on a map.
- **604 automated tests** — 409 Python (one skipped without an API key) and 195 web across 14 files
  — run on every Pull Request by `.github/workflows/tests.yml`.
- **50 Pull Requests merged**, one reviewer each from a fixed rotation, the author never merging
  their own.

What it does not do is listed under *Current scope*, and each limit is visible in the product rather
than only here: a green tick appears only when nothing was left unplaced **and** no rule went
unapplied, an unreachable service shows a dash instead of a number, and a constraint the solver
cannot honour comes back named in `not_applied`.

## Future Improvements

In the order they would be worth doing:

1. **Replanning on incident** (#36) — the second half of the original idea, and the one absence that
   changes what the product is.
2. **The four remaining constraint types** (#29): `at_bottom`, `keep_upright`, `max_stack_height`,
   `not_stackable`. The schema and the refusal path already exist, so the work is in the solver.
3. **Entering your own boxes** (#8), which is what lifts the app off the demo load.
4. **Passing constraints through `POST /plan`** (#19): the solver honours five types that the plan
   endpoint does not yet hand it, and `not_applied` says so on every plan today.
5. **Accounts and persistence**, so a round survives closing the tab.
6. **Lifting the round out of France.** `POST /route` geocodes through the Base Adresse Nationale,
   which covers France only — a Spanish address returns a 422 no front-end work can fix.
