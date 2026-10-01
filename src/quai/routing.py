"""Road route data for a delivery list: addresses in, points and timings out.

Two public services do the work, and neither of them is ours:

- **`api-adresse.data.gouv.fr`** (the Base Adresse Nationale) turns an address into a point. It
  covers **France only**, so an address anywhere else returns no result and is refused by name
  rather than guessed at.
- **`router.project-osrm.org`** (the OSRM demo server) turns the points into a road route: the
  geometry to draw, the distance and the duration of each leg.

The one rule this module exists to protect: **the stops keep the order they arrived in.** OSRM has
a `/trip` service that solves the travelling-salesman problem and hands back a better order; this
module calls `/route`, which drives the points in the order given, and `ROUTE_SERVICE` is spelled
out as a constant so that the difference is visible rather than buried in a URL. The route is an
input to QUAI, not an output — the same rule the solver follows for `unload_at`
(`documentation/prompt_evaluation.md`, *Route and unloading order*).

Distances are metres and durations seconds, which is what both services return; the field names say
so rather than leaving a reader to assume, the way `limit_cm` and `limit_kg` do in `constraints.py`.
"""
from dataclasses import dataclass

import httpx

GEOCODER_URL = "https://api-adresse.data.gouv.fr/search/"
ROUTER_URL = "https://router.project-osrm.org"

# `/route` drives the points in the order given. `/trip` would reorder them, which is the one thing
# this module must never do, so the choice is a named constant and not a fragment of an f-string.
ROUTE_SERVICE = "route/v1/driving"

# Both services are public, free and occasionally slow. A request that hangs is worse than one that
# fails: the operator is waiting in front of a map that never arrives, with nothing to act on.
TIMEOUT = httpx.Timeout(10.0, connect=5.0)

# OSRM needs somewhere to go: one point is a position, not a route.
MIN_STOPS = 2


class RouteError(RuntimeError):
    """Route data could not be produced.

    Carries a message meant for the operator rather than a stack trace.
    """


class AddressNotFound(RouteError):
    """One of the addresses did not geocode, so no route can be drawn through it."""


class ServiceUnavailable(RouteError):
    """A service we do not own answered badly, or did not answer."""


class ServiceTimeout(ServiceUnavailable):
    """A service did not answer in time."""


@dataclass(frozen=True)
class Point:
    """One geocoded stop.

    `label` is the address as the geocoder understood it, which is worth showing back to the
    operator: it is how a wrong-but-plausible match gets spotted.
    """
    lon: float
    lat: float
    label: str


@dataclass(frozen=True)
class Leg:
    distance_m: float
    duration_s: float


@dataclass(frozen=True)
class RoadRoute:
    geometry: dict          # GeoJSON LineString, ready for a map
    distance_m: float
    duration_s: float
    legs: tuple[Leg, ...]   # one per pair of consecutive stops, so always len(stops) - 1


def build_client() -> httpx.Client:
    """The HTTP client used when a caller does not supply one. Tests replace this."""
    return httpx.Client(timeout=TIMEOUT)


def geocode(address: str, client: httpx.Client) -> Point:
    """Turn one address into a point, or say which address could not be turned into one."""
    if not address or not address.strip():
        raise AddressNotFound("an empty address cannot be geocoded")
    payload = _get(client, GEOCODER_URL, {"q": address, "limit": 1}, service="the address lookup")
    features = payload.get("features") or []
    if not features:
        # An empty list, not an error status: the geocoder answers 200 with nothing found.
        raise AddressNotFound(f"no address found for {address!r}. The address lookup covers France "
                              "only, so an address elsewhere will never match")
    feature = features[0]
    lon, lat = feature["geometry"]["coordinates"]
    return Point(lon=float(lon), lat=float(lat),
                 label=str(feature.get("properties", {}).get("label", address)))


def road_route(points: list[Point], client: httpx.Client) -> RoadRoute:
    """The road route through `points`, in exactly the order given."""
    if len(points) < MIN_STOPS:
        raise RouteError(f"a route needs at least {MIN_STOPS} stops, got {len(points)}")
    path = ";".join(f"{p.lon},{p.lat}" for p in points)
    payload = _get(client, f"{ROUTER_URL}/{ROUTE_SERVICE}/{path}",
                   {"overview": "full", "geometries": "geojson"}, service="the route service")
    if payload.get("code") != "Ok":
        raise ServiceUnavailable(f"the route service could not route these stops "
                                 f"({payload.get('code', 'no code')}): "
                                 f"{payload.get('message', 'no reason given')}")
    routes = payload.get("routes") or []
    if not routes:
        raise ServiceUnavailable("the route service returned no route for these stops")
    first = routes[0]
    legs = tuple(Leg(distance_m=float(leg["distance"]), duration_s=float(leg["duration"]))
                 for leg in first.get("legs", []))
    if len(legs) != len(points) - 1:
        # Guards the ETA arithmetic below: one leg per pair is what makes a cumulative sum mean
        # "arrival at stop i". A different count means the answer is about a different journey.
        raise ServiceUnavailable(f"the route service returned {len(legs)} legs for {len(points)} "
                                 "stops; expected one fewer leg than stops")
    return RoadRoute(geometry=first["geometry"], distance_m=float(first["distance"]),
                     duration_s=float(first["duration"]), legs=legs)


def arrival_offsets(route: RoadRoute) -> tuple[float, ...]:
    """Seconds from departure to each stop: 0 at the first, then the legs accumulated.

    Driving time only. Time spent unloading is not counted, because nothing in QUAI knows it yet.
    """
    offsets, running = [0.0], 0.0
    for leg in route.legs:
        running += leg.duration_s
        offsets.append(running)
    return tuple(offsets)


def _get(client: httpx.Client, url: str, params: dict, service: str) -> dict:
    """One GET, with every way it can go wrong turned into a sentence naming the service."""
    try:
        response = client.get(url, params=params)
    except httpx.TimeoutException as error:
        raise ServiceTimeout(f"{service} did not answer in time") from error
    except httpx.HTTPError as error:
        raise ServiceUnavailable(f"{service} could not be reached: {error}") from error
    if response.status_code >= 400:
        raise ServiceUnavailable(f"{service} answered {response.status_code}")
    try:
        return response.json()
    except ValueError as error:
        raise ServiceUnavailable(f"{service} answered something that is not JSON") from error
