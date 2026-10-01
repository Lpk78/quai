"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
import dataclasses
import pathlib
from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from evaluate_prompt import prefill_of, prompt_text
from quai import llm
from quai.constraints import ConstraintError, Manifest, parse
from quai.models import Box, Container
from quai.solver import solve

app = FastAPI(title="QUAI")

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

    try:
        raw = _translate(request.text, manifest_text)
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
