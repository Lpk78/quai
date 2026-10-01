"""HTTP API exposing the solver. The web app calls this; it never runs Python itself.

Run from the repository root:  uvicorn server:app --app-dir src --reload
"""
from collections import Counter
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from quai import routing
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


class StopIn(BaseModel):
    id: str = Field(min_length=1, description="the stop id used everywhere else, e.g. S1")
    address: str = Field(min_length=1, description="a postal address in France")


class RouteRequest(BaseModel):
    """The stops of one delivery list, in the order they will be driven.

    That order is an input, not a question: QUAI never reorders stops. It comes with the manifest
    and the solver loads the vehicle against it, so a route drawn in any other order would describe
    a different journey from the one that was loaded.
    """
    stops: list[StopIn] = Field(min_length=routing.MIN_STOPS)
    departure_time: datetime | None = Field(
        default=None,
        description="when the vehicle leaves the first stop; absolute ETAs are returned when given")


class StopOut(BaseModel):
    id: str
    address: str
    label: str              # the address as the geocoder read it, for spotting a wrong match
    lon: float
    lat: float
    eta_seconds: float      # driving time from the first stop; 0 at the first stop
    eta: datetime | None    # the same instant, only when a departure_time was given


class RouteResponse(BaseModel):
    stops: list[StopOut]
    geometry: dict          # GeoJSON LineString for the map
    total_distance_m: float
    total_duration_s: float


@app.post("/route")
def route(request: RouteRequest) -> RouteResponse:
    """Geocode the stops, route through them in order, and time the arrivals.

    Driving time only: nothing in QUAI knows yet how long unloading a stop takes.
    """
    duplicates = sorted(i for i, n in Counter(s.id for s in request.stops).items() if n > 1)
    if duplicates:
        raise HTTPException(status_code=422, detail=f"duplicate stop ids: {", ".join(duplicates)}")

    with routing.build_client() as client:
        try:
            points = [routing.geocode(stop.address, client) for stop in request.stops]
            road = routing.road_route(points, client)
        except routing.AddressNotFound as error:
            # The input is at fault rather than the service, the same as a negative dimension is.
            raise HTTPException(status_code=422, detail=str(error)) from error
        except routing.ServiceTimeout as error:
            raise HTTPException(status_code=504, detail=str(error)) from error
        except routing.ServiceUnavailable as error:
            raise HTTPException(status_code=502, detail=str(error)) from error
        except routing.RouteError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    offsets = routing.arrival_offsets(road)
    return RouteResponse(
        stops=[StopOut(id=stop.id, address=stop.address, label=point.label,
                       lon=point.lon, lat=point.lat, eta_seconds=offset,
                       eta=None if request.departure_time is None
                       else request.departure_time + timedelta(seconds=offset))
               for stop, point, offset in zip(request.stops, points, offsets)],
        geometry=road.geometry,
        total_distance_m=road.distance_m,
        total_duration_s=road.duration_s,
    )
