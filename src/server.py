"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
from collections import Counter

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from quai.models import Box, Container
from quai.solver import solve

app = FastAPI(title="QUAI")


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
