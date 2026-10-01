"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
import math
from collections import Counter

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from quai.models import Box, Container
from quai.solver import solve

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


def _json_safe(value):
    """The same structure with `nan` and `inf` turned into their names.

    Only used on the text of a validation error, never on a plan.
    """
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


@app.exception_handler(RequestValidationError)
async def refused_input(request: Request, error: RequestValidationError) -> JSONResponse:
    """Answer a rejected request with the reason, even when the reason cannot be serialised.

    FastAPI's own handler echoes the offending value back inside the 422, and `JSONResponse` then
    refuses to serialise it if that value is `NaN` or an infinity — so a request carrying a bare
    `NaN` literal came back as an unhandled error, which is a `500`, instead of the `422` #16 set as
    the standard for bad input. A Python client reaches this by accident: `json.dumps` emits `NaN`
    unless told not to. Pydantic was already rejecting the value correctly; only the answer was
    broken. Found while checking the claim in #26 that this endpoint was safe from `NaN`.
    """
    return JSONResponse(status_code=422,
                        content={"detail": _json_safe(jsonable_encoder(error.errors()))})


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
    # `ge=0`, not `gt=0`: the model allows a limit of 0 and `models.py` pins that, so refusing it
    # here would make this second layer stricter than the first. "Nothing may be loaded" is a real
    # state for an empty or out-of-service vehicle. Pydantic rejects NaN for a bounded float either
    # way, which is the other half of #26.
    max_weight: float | None = Field(default=None, ge=0, description="kg; omitted means no limit")


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
