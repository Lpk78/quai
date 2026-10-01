"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from quai import incident as incidents
from quai.constraints import ConstraintError, Manifest, parse
from quai.models import Box, Container, Placement
from quai.solver import ImpossibleStart, UnsupportedConstraint, solve

app = FastAPI(title="QUAI")

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


class PlacementOut(BaseModel):
    id: str
    x: int
    y: int
    z: int
    dx: int
    dy: int
    dz: int


class PlanResponse(BaseModel):
    placements: list[PlacementOut]
    unplaced: list[str]
    fill_rate: float
    total_weight: float


@app.post("/plan")
def plan(request: PlanRequest) -> PlanResponse:
    duplicates = sorted(i for i, n in Counter(b.id for b in request.boxes).items() if n > 1)
    if duplicates:
        raise HTTPException(status_code=422, detail=f"duplicate box ids: {', '.join(duplicates)}")

    c = request.container
    container = Container(c.length, c.width, c.height,
                          max_weight=float("inf") if c.max_weight is None else c.max_weight)
    boxes = [Box(b.id, b.length, b.width, b.height, b.weight) for b in request.boxes]
    result = solve(boxes, container)

    return PlanResponse(
        placements=[PlacementOut(id=p.box.id, x=p.x, y=p.y, z=p.z, dx=p.dx, dy=p.dy, dz=p.dz)
                    for p in result.placements],
        unplaced=[b.id for b in result.unplaced],
        fill_rate=result.fill_rate,
        total_weight=result.total_weight,
    )


class PlacementIn(BaseModel):
    """One box already in the vehicle, where the operator put it."""
    box: BoxIn
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    z: int = Field(ge=0)
    dx: int = Field(gt=0)
    dy: int = Field(gt=0)
    dz: int = Field(gt=0)


class IncidentIn(BaseModel):
    kind: str = Field(description="missing, damaged or added")
    box_id: str = Field(min_length=1)
    box: BoxIn | None = Field(default=None, description="required for added, ignored otherwise")


class RecomputeRequest(BaseModel):
    """A load in progress, plus the one thing that just changed about it."""
    container: ContainerIn
    loaded: list[PlacementIn] = Field(default_factory=list,
                                      description="already in the vehicle; never moved")
    waiting: list[BoxIn] = Field(default_factory=list, description="still on the dock")
    incident: IncidentIn
    constraints: dict | None = Field(
        default=None,
        description="the same validated translation the first plan used, {constraints, unresolved}")
    stops: list[str] = Field(default_factory=list,
                             description="the route in order; required when constraints are given")


@app.post("/plan/recompute")
def recompute(request: RecomputeRequest) -> PlanResponse:
    """Replan what is left after an incident, around what is already in the vehicle.

    The boxes in `loaded` do not move. They are returned in the plan with the newly placed ones,
    because the answer has to describe the whole vehicle and not only the half that changed.
    """
    container = _container(request.container)
    loaded = [Placement(_box(p.box), p.x, p.y, p.z, p.dx, p.dy, p.dz) for p in request.loaded]
    waiting = [_box(b) for b in request.waiting]

    _refuse_duplicate_ids([p.box.id for p in request.loaded] + [b.id for b in request.waiting])

    try:
        event = incidents.Incident(kind=request.incident.kind, box_id=request.incident.box_id,
                                   box=None if request.incident.box is None
                                   else _box(request.incident.box))
        loaded, waiting = incidents.apply(event, loaded, waiting)
    except incidents.IncidentRefused as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    constraints = _constraints(request, loaded, waiting)

    try:
        plan = solve(waiting, container, constraints, fixed=loaded)
    except (ImpossibleStart, UnsupportedConstraint) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return _plan_response(plan)


def _box(box: BoxIn) -> Box:
    return Box(box.id, box.length, box.width, box.height, box.weight)


def _container(container: ContainerIn) -> Container:
    return Container(container.length, container.width, container.height,
                     max_weight=float("inf") if container.max_weight is None
                     else container.max_weight)


def _refuse_duplicate_ids(ids: list[str]) -> None:
    duplicates = sorted(i for i, n in Counter(ids).items() if n > 1)
    if duplicates:
        raise HTTPException(status_code=422, detail=f"duplicate box ids: {', '.join(duplicates)}")


def _constraints(request: RecomputeRequest, loaded: list[Placement], waiting: list[Box]):
    """The first plan's translation, re-validated against the load as it now stands.

    Re-validated rather than trusted: the manifest has changed — a box was added or has left — and a
    constraint naming a box that is no longer in the load is not a constraint this plan can honour.
    """
    if request.constraints is None:
        return None
    if not request.stops:
        raise HTTPException(status_code=422,
                            detail="constraints were given without the route; a constraint may "
                                   "name a stop, so the stops are needed to validate it")
    ids = [placed.box.id for placed in loaded] + [box.id for box in waiting]
    try:
        return parse(request.constraints, Manifest(tuple(ids), tuple(request.stops)))
    except (ConstraintError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


def _plan_response(plan) -> PlanResponse:
    return PlanResponse(
        placements=[PlacementOut(id=p.box.id, x=p.x, y=p.y, z=p.z, dx=p.dx, dy=p.dy, dz=p.dz)
                    for p in plan.placements],
        unplaced=[b.id for b in plan.unplaced],
        fill_rate=plan.fill_rate,
        total_weight=plan.total_weight,
    )
