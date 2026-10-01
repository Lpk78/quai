"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
import logging
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from quai.constraints import CONSTRAINT_FIELDS, ConstraintError, Manifest, parse
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

# The web app runs on its own origin in development (Vite serves it on :5173), so the browser refuses
# to hand it the response unless this header says otherwise. The origins are listed rather than
# opened with "*" so that the dev app works without every page the operator happens to have open
# being able to read this API's answers.
#
# What this is not: access control. CORS is a rule browsers follow, not one the server enforces —
# a request from any origin still runs, and curl ignores the whole mechanism. `POST /plan` is pure
# computation, so that costs nothing. `POST /constraints` (#19) will spend Claude API credits, and
# it needs authentication rather than an origin list. Checked by SamDana-maker on #33.
DEV_ORIGINS = [
    "http://localhost:5173",   # vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:4173",   # vite preview, the production build served locally
    "http://127.0.0.1:4173",
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


def split_constraints(constraints: list[dict]) -> tuple[list[dict], list[NotAppliedOut]]:
    """The constraints this endpoint passes to the solver, and the ones it reports back instead.

    An unknown type is not reported, it is refused: a name outside the contract is malformed input,
    not a feature waiting to be wired, and repairing it is the one thing this layer must not do.
    """
    unknown = sorted({str(c.get("type")) for c in constraints
                      if c.get("type") not in CONSTRAINT_FIELDS})
    if unknown:
        raise HTTPException(status_code=422,
                            detail=f"not constraint types in the contract: {', '.join(unknown)}")

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

    wired, not_applied = split_constraints(request.constraints)
    constraints = None
    if wired:
        # Through `parse()` like everything else that reaches the solver. Nothing here came from a
        # model, but the door is the same one, so a constraint naming a box that is not in the load
        # is refused here rather than planned around.
        try:
            constraints = parse({"constraints": wired, "unresolved": []},
                                Manifest(tuple(b.id for b in boxes), (PLAN_ROUTE_STOP,)))
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
