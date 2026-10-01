"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
import dataclasses
import logging
import os
import pathlib
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from evaluate_prompt import prefill_of, prompt_text
from quai import llm
from quai.constraints import ConstraintError, Manifest, find_problems, parse
from quai.models import Box, Container
from quai.solver import HONOURED, solve

log = logging.getLogger(__name__)

app = FastAPI(title="QUAI")

# The constraint types `POST /plan` passes through to the solver. One, for now.
#
# This is deliberately narrower than the solver's own `HONOURED`. `load_last` needs nothing but the
# boxes, so it works with what this endpoint already receives. The other three the solver honours do
# not: `unload_at` needs the route in delivery order, and this request carries no route — the stop
# order would have to be invented, which is the one thing the route is not allowed to do. Wiring the
# rest, and accumulating constraints across sentences, is roadmap row 12 (#19).
WIRED: frozenset[str] = frozenset(["load_last"])

# `Manifest` requires at least one stop, because for the solver a route is an input rather than a
# default. With no `unload_at` applied here, every box travels the whole way and the stop never
# carries meaning: `unloading_plan()` maps them all to the last stop, so this single entry leaves
# `load_last` as the only thing ordering the load. It is a placeholder, not a route.
PLAN_ROUTE_STOP = "S1"

# The production prompt version: the one scored in documentation/prompt_evaluation.md, not whatever
# `.env`'s LLM_MODEL happens to name for an evaluation run. Read once at import time — the file is
# part of the repository, not a secret, so this needs no key and does not break collecting the tests.
CONSTRAINT_PROMPT_PATH = (pathlib.Path(__file__).resolve().parents[1] / "prompts"
                          / "constraint-translation" / "v4_few_shot.md")
CONSTRAINT_MODEL = "claude-haiku-4-5-20251001"
CONSTRAINT_PROMPT_TEXT = prompt_text(CONSTRAINT_PROMPT_PATH)
CONSTRAINT_PREFILL = prefill_of(CONSTRAINT_PROMPT_PATH)

# The web app runs on its own origin in development (Vite serves it on :5173), so the browser refuses
# to hand it the response unless this header says otherwise. The origins are listed rather than
# opened with "*" so that the dev app works without every page the operator happens to have open
# being able to read this API's answers.
#
# What this is not: access control. CORS is a rule browsers follow, not one the server enforces —
# a request from any origin still runs, and curl ignores the whole mechanism. `POST /plan` is pure
# computation, so that costs nothing. `POST /constraints` spends Claude API credits on every call and
# still has no authentication of its own — it reuses this same allowlist for now, which is a known
# gap, not a decision that it is enough. Flagged by SamDana-maker and MORHI11 on #19 and #33.
#
# The phone is not on localhost: it reaches the dev app at this Mac's address on the WiFi, so that
# origin has to be allowed as well. The address is handed out by DHCP and this file is tracked, so
# `QUAI_LAN_ORIGIN` overrides the fallback rather than anyone editing the literal — see the README's
# "Phone demo" section for the two commands that produce it.
LAN_ORIGIN = os.environ.get("QUAI_LAN_ORIGIN", "http://192.168.1.201:5173").strip()

DEV_ORIGINS = [
    "http://localhost:5173",   # vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:4173",   # vite preview, the production build served locally
    "http://127.0.0.1:4173",
    LAN_ORIGIN,                # the phone on the same WiFi, against `vite --host`
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=DEV_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class BoxIn(BaseModel):
    id: str = Field(min_length=1)
    length: int = Field(gt=0, description="cm")
    width: int = Field(gt=0, description="cm")
    height: int = Field(gt=0, description="cm")
    weight: float = Field(default=0.0, ge=0, description="kg")


class ContainerIn(BaseModel):
    length: int = Field(gt=0, description="cm")
    width: int = Field(gt=0, description="cm")
    height: int = Field(gt=0, description="cm")
    max_weight: float | None = Field(default=None, gt=0, description="kg; omitted means no limit")


class PlanRequest(BaseModel):
    container: ContainerIn
    boxes: list[BoxIn]
    constraints: list[dict] = Field(default_factory=list,
                                    description="optional; constraint objects in the shape "
                                                "`quai.constraints.parse()` validates. Types this "
                                                "endpoint does not pass to the solver come back in "
                                                "`not_applied` rather than being dropped in silence")


class PlacementOut(BaseModel):
    id: str
    x: int
    y: int
    z: int
    dx: int
    dy: int
    dz: int


class NotAppliedOut(BaseModel):
    """A constraint the caller sent that did not reach the solver, and why."""
    type: str
    item: str | None = None
    reason: str


class PlanResponse(BaseModel):
    placements: list[PlacementOut]
    unplaced: list[str]
    fill_rate: float
    total_weight: float
    not_applied: list[NotAppliedOut] = Field(default_factory=list)


def why_not_applied(kind: str) -> str:
    """The reason a known constraint type did not reach the solver.

    Two different reasons, and the caller needs to tell them apart: a type the solver could honour
    but this endpoint does not hand it yet, and a type the solver itself has not learned.
    """
    if kind == "unload_at":
        return ("the solver honours unload_at, but POST /plan carries no route, so the stop order "
                "it needs would have to be invented; roadmap row 12 (#19)")
    if kind in HONOURED:
        return (f"the solver honours {kind}, but POST /plan does not pass it yet; "
                "roadmap row 12 (#19)")
    return (f"the solver cannot honour {kind} yet and refuses to plan with it rather than drop it; "
            "issue #29")


def validation_stops(constraints: list[dict]) -> tuple[str, ...]:
    """Stop ids for the manifest the contract is checked against — not a route.

    `find_problems` asks whether a constraint's `stop` is one the route knows, and this endpoint has
    no route, so every stop named by an `unload_at` is added here before the question is put. That
    makes the check structural rather than geographic: it catches a stop that is missing, empty or
    not a string, and cannot catch one that is simply not on the round, because nothing here knows
    what the round is. Nothing is ordered by this list — `unload_at` is reported rather than applied,
    so it never reaches `loading_order`.
    """
    stops = [PLAN_ROUTE_STOP]
    for constraint in constraints:
        stop = constraint.get("stop")
        if isinstance(stop, str) and stop and stop not in stops:
            stops.append(stop)
    return tuple(stops)


def validate_constraints(constraints: list[dict], box_ids: tuple[str, ...]) -> None:
    """Refuse the whole list unless every constraint in it matches the contract.

    Before anything is acted on *or reported*. A constraint this endpoint does not wire is still
    checked, because `not_applied` is an answer about the caller's input and an answer about
    malformed input has to be a refusal — reporting `max_weight_on` with no `limit_kg` back as
    "honoured but not passed yet" says something false about it.

    `quai.constraints.find_problems` is asked rather than re-implemented: missing fields, undeclared
    fields, unknown types, items outside the load, limits that are not finite numbers and
    contradictions are all already written down there, and a second copy here would be the drift the
    contract exists to prevent.
    """
    if not constraints:
        return
    problems = find_problems({"constraints": constraints, "unresolved": []},
                             Manifest(box_ids, validation_stops(constraints)))
    if problems:
        raise HTTPException(status_code=422,
                            detail=f"the constraints did not validate: {'; '.join(problems)}")


def split_constraints(constraints: list[dict]) -> tuple[list[dict], list[NotAppliedOut]]:
    """The constraints this endpoint passes to the solver, and the ones it reports back instead.

    Both halves are known to be well formed: `validate_constraints` has already refused the request
    otherwise, so the only question left here is which ones the solver gets.
    """
    wired = [c for c in constraints if c["type"] in WIRED]
    not_applied = [NotAppliedOut(type=c["type"], item=c.get("item"),
                                 reason=why_not_applied(c["type"]))
                   for c in constraints if c["type"] not in WIRED]
    for entry in not_applied:
        log.warning("POST /plan did not apply %s: %s", entry.type, entry.reason)
    return wired, not_applied


@app.post("/plan")
def plan(request: PlanRequest) -> PlanResponse:
    duplicates = sorted(i for i, n in Counter(b.id for b in request.boxes).items() if n > 1)
    if duplicates:
        raise HTTPException(status_code=422, detail=f"duplicate box ids: {', '.join(duplicates)}")

    c = request.container
    container = Container(c.length, c.width, c.height,
                          max_weight=float("inf") if c.max_weight is None else c.max_weight)
    boxes = [Box(b.id, b.length, b.width, b.height, b.weight) for b in request.boxes]

    box_ids = tuple(b.id for b in boxes)
    validate_constraints(request.constraints, box_ids)
    wired, not_applied = split_constraints(request.constraints)
    constraints = None
    if wired:
        # Through `parse()` like everything else that reaches the solver. Nothing here came from a
        # model, but the door is the same one, and the set handed to `solve` is built by it rather
        # than assembled here. The validation above has already refused anything malformed, so this
        # raising at all would mean the two disagree.
        try:
            constraints = parse({"constraints": wired, "unresolved": []},
                                Manifest(box_ids, (PLAN_ROUTE_STOP,)))
        except ConstraintError as error:
            raise HTTPException(status_code=422,
                                detail=f"the constraints did not validate: {error}") from error
    result = solve(boxes, container, constraints)

    return PlanResponse(
        not_applied=not_applied,
        placements=[PlacementOut(id=p.box.id, x=p.x, y=p.y, z=p.z, dx=p.dx, dy=p.dy, dz=p.dz)
                    for p in result.placements],
        unplaced=[b.id for b in result.unplaced],
        fill_rate=result.fill_rate,
        total_weight=result.total_weight,
    )


class ManifestItemIn(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1, description="what the operator would call it, e.g. \"washing "
                                                  "machine\" — lets the model match speech to an id")
    length: int = Field(gt=0, description="cm")
    width: int = Field(gt=0, description="cm")
    height: int = Field(gt=0, description="cm")
    weight: float = Field(default=0.0, ge=0, description="kg")


class StopIn(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1, description="what the operator would call it, e.g. \"Le Havre\"")


class ConstraintsRequest(BaseModel):
    text: str = Field(description="one sentence said by the operator")
    manifest: list[ManifestItemIn]
    stops: list[StopIn] = Field(min_length=1, description="the route, in delivery order — QUAI never "
                                                           "reorders or chooses stops")


class ConstraintsResponse(BaseModel):
    constraints: list[dict]
    unresolved: list[dict]


@dataclasses.dataclass(frozen=True)
class _ManifestEntry:
    """What `llm.manifest_block` needs to describe one item — formatted the same way the evaluation
    manifest is, so production input matches what the prompt version was scored on."""
    id: str
    label: str
    dimensions: str
    weight: str


def _translate(text: str, manifest_text: str) -> str:
    """Call the production model with the production prompt version. The only door the server has
    to `quai.llm`, so a test can mock this one function instead of the Anthropic client."""
    translator = dataclasses.replace(llm.from_env(CONSTRAINT_MODEL), prefill=CONSTRAINT_PREFILL)
    return translator.translate(CONSTRAINT_PROMPT_TEXT, text, manifest_text)


@app.post("/constraints")
def constraints(request: ConstraintsRequest) -> ConstraintsResponse:
    if not request.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")

    item_duplicates = sorted(i for i, n in Counter(m.id for m in request.manifest).items() if n > 1)
    if item_duplicates:
        raise HTTPException(status_code=422,
                            detail=f"duplicate manifest item ids: {', '.join(item_duplicates)}")

    stop_duplicates = sorted(i for i, n in Counter(s.id for s in request.stops).items() if n > 1)
    if stop_duplicates:
        raise HTTPException(status_code=422, detail=f"duplicate stop ids: {', '.join(stop_duplicates)}")

    manifest = Manifest(items=tuple(m.id for m in request.manifest),
                        stops=tuple(s.id for s in request.stops))
    manifest_text = llm.manifest_block(
        [_ManifestEntry(m.id, m.label, f"{m.length} × {m.width} × {m.height}", str(m.weight))
         for m in request.manifest],
        {s.id: s.name for s in request.stops},
    )

    # Every way `_translate` can fail is answered here, because the one that is not becomes a bare 500
    # from FastAPI's default handler — and that handler sits outside `CORSMiddleware`, so the response
    # carries no `access-control-allow-origin`. The browser then cannot read it, `fetch` throws, and
    # `web/src/api.js` reports `unreachable`: the operator is told "could not reach the solver" about a
    # server that is running and answering. That sends them to restart uvicorn, which fixes nothing.
    #
    # `NotConfigured` is caught by its base class on purpose: it covers `MissingKey`, `MissingModel`
    # and the "anthropic is not installed" case, and a new setting added to `from_env` is covered the
    # day it is added rather than the day someone remembers this list.
    try:
        raw = _translate(request.text, manifest_text)
    except llm.NotConfigured as missing:
        raise HTTPException(status_code=503,
                            detail=f"the constraint translation model is not configured on the "
                                   f"server — check {llm.KEY_VARIABLE} and {llm.MODEL_VARIABLE} in "
                                   f".env: {missing}") from missing
    except llm.FatalCall as rejected:
        # A key that is present but wrong reaches this, not `NotConfigured`: `from_env` is satisfied
        # and the API refuses the call. 502 rather than 503 — the model answered, just not usably,
        # which is the same thing a reply that fails validation means below.
        raise HTTPException(status_code=502,
                            detail=f"the constraint translation model refused the request, which "
                                   f"usually means the key or the model name is wrong: "
                                   f"{rejected}") from rejected
    except llm.CallFailed as failed:
        raise HTTPException(status_code=503,
                            detail=f"the constraint translation model could not be reached: "
                                   f"{failed}") from failed

    try:
        result = parse(raw, manifest)
    except ConstraintError as error:
        raise HTTPException(status_code=502,
                            detail=f"the model's reply did not validate: {error}") from error

    return ConstraintsResponse(constraints=list(result.constraints),
                               unresolved=list(result.unresolved))
