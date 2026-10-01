"""Run from the repository root:  python3 -m unittest discover tests

Every test here mocks the HTTP. The geocoder and the router are public services we do not own: a
suite that called them would be slow, would fail when someone else's server is down, and would be
testing their uptime rather than our code.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import httpx  # noqa: E402

from quai import routing  # noqa: E402

# Three real French addresses, far enough apart that a route between them is unambiguous.
AMIENS = (2.290084, 49.897442)
PARIS = (2.352200, 48.856600)
LILLE = (3.057300, 50.629200)


def geocoded(lon: float, lat: float, label: str) -> dict:
    """What the Base Adresse Nationale answers: a GeoJSON FeatureCollection."""
    return {"type": "FeatureCollection",
            "features": [{"type": "Feature",
                          "geometry": {"type": "Point", "coordinates": [lon, lat]},
                          "properties": {"label": label}}]}


def routed(points: list[tuple], seconds_per_leg: float = 600.0) -> dict:
    """What OSRM answers: one leg per pair of consecutive points, and a line through them."""
    legs = [{"distance": 1000.0, "duration": seconds_per_leg} for _ in range(len(points) - 1)]
    return {"code": "Ok",
            "routes": [{"distance": 1000.0 * len(legs),
                        "duration": seconds_per_leg * len(legs),
                        "geometry": {"type": "LineString",
                                     "coordinates": [list(p) for p in points]},
                        "legs": legs}]}


class Recorder:
    """A stand-in for both services that records every URL it was asked for."""

    def __init__(self, handler):
        self.urls = []
        self._handler = handler

    def client(self) -> httpx.Client:
        def transport(request: httpx.Request) -> httpx.Response:
            self.urls.append(str(request.url))
            return self._handler(request)
        return httpx.Client(transport=httpx.MockTransport(transport), timeout=routing.TIMEOUT)


def service(by_address: dict, route_payload: dict | None = None, points=()) -> Recorder:
    """A geocoder that answers from `by_address`, and a router that answers one fixed route."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "api-adresse" in request.url.host:
            query = request.url.params.get("q", "")
            if query not in by_address:
                return httpx.Response(200, json={"type": "FeatureCollection", "features": []})
            lon, lat = by_address[query]
            return httpx.Response(200, json=geocoded(lon, lat, f"{query} (as read)"))
        return httpx.Response(200, json=route_payload or routed(list(points)))
    return Recorder(handler)


class TestGeocoding(unittest.TestCase):
    def test_an_address_becomes_a_point(self):
        rec = service({"8 boulevard du Port, Amiens": AMIENS})
        with rec.client() as client:
            point = routing.geocode("8 boulevard du Port, Amiens", client)
        self.assertEqual((point.lon, point.lat), AMIENS)
        self.assertIn("as read", point.label)

    def test_the_label_the_geocoder_read_is_kept(self):
        """A wrong-but-plausible match is only spotted if the operator sees what was matched."""
        rec = service({"rue de la Paix": PARIS})
        with rec.client() as client:
            self.assertEqual(routing.geocode("rue de la Paix", client).label,
                             "rue de la Paix (as read)")

    def test_an_address_that_matches_nothing_is_named(self):
        rec = service({})
        with rec.client() as client:
            with self.assertRaises(routing.AddressNotFound) as refused:
                routing.geocode("zzzz nowhere at all", client)
        self.assertIn("zzzz nowhere at all", str(refused.exception))
        self.assertIn("France", str(refused.exception))

    def test_an_empty_address_is_refused_without_a_call(self):
        rec = service({})
        with rec.client() as client:
            with self.assertRaises(routing.AddressNotFound):
                routing.geocode("   ", client)
        self.assertEqual(rec.urls, [])


class TestTheRoute(unittest.TestCase):
    def points(self):
        return [routing.Point(*AMIENS, "Amiens"),
                routing.Point(*PARIS, "Paris"),
                routing.Point(*LILLE, "Lille")]

    def test_the_stops_are_driven_in_the_order_given(self):
        """The rule this module exists for: coordinates enter the URL in the order supplied."""
        rec = service({}, route_payload=routed([AMIENS, PARIS, LILLE]))
        with rec.client() as client:
            routing.road_route(self.points(), client)
        path = rec.urls[0]
        self.assertIn("2.290084,49.897442;2.3522,48.8566;3.0573,50.6292", path)

    def test_the_trip_service_is_never_called(self):
        """OSRM's /trip reorders the stops to make the journey shorter. That is the one thing QUAI
        must not do: the order comes with the manifest and the vehicle was loaded against it."""
        rec = service({}, route_payload=routed([AMIENS, PARIS, LILLE]))
        with rec.client() as client:
            routing.road_route(self.points(), client)
        self.assertIn("/route/v1/", rec.urls[0])
        self.assertNotIn("/trip/", rec.urls[0])

    def test_distance_duration_and_geometry_come_back(self):
        rec = service({}, route_payload=routed([AMIENS, PARIS, LILLE]))
        with rec.client() as client:
            road = routing.road_route(self.points(), client)
        self.assertEqual(road.distance_m, 2000.0)
        self.assertEqual(road.duration_s, 1200.0)
        self.assertEqual(road.geometry["type"], "LineString")
        self.assertEqual(len(road.legs), 2)

    def test_one_stop_is_not_a_route(self):
        rec = service({})
        with rec.client() as client:
            with self.assertRaises(routing.RouteError):
                routing.road_route([routing.Point(*PARIS, "Paris")], client)

    def test_a_refusal_from_the_router_is_reported(self):
        rec = service({}, route_payload={"code": "NoRoute", "message": "no route found"})
        with rec.client() as client:
            with self.assertRaises(routing.ServiceUnavailable) as refused:
                routing.road_route(self.points(), client)
        self.assertIn("NoRoute", str(refused.exception))

    def test_a_leg_count_that_does_not_match_the_stops_is_refused(self):
        """One leg per pair is what makes the cumulative sum mean 'arrival at stop i'."""
        wrong = routed([AMIENS, PARIS, LILLE])
        wrong["routes"][0]["legs"] = wrong["routes"][0]["legs"][:1]
        rec = service({}, route_payload=wrong)
        with rec.client() as client:
            with self.assertRaises(routing.ServiceUnavailable) as refused:
                routing.road_route(self.points(), client)
        self.assertIn("legs", str(refused.exception))


class TestArrivalTimes(unittest.TestCase):
    def test_the_first_stop_is_zero_and_the_rest_accumulate(self):
        road = routing.RoadRoute(geometry={}, distance_m=3000.0, duration_s=1800.0,
                                 legs=(routing.Leg(1000.0, 600.0), routing.Leg(2000.0, 1200.0)))
        self.assertEqual(routing.arrival_offsets(road), (0.0, 600.0, 1800.0))

    def test_there_is_one_offset_per_stop(self):
        road = routing.RoadRoute(geometry={}, distance_m=0.0, duration_s=0.0,
                                 legs=(routing.Leg(1.0, 1.0),) * 4)
        self.assertEqual(len(routing.arrival_offsets(road)), 5)


class TestWhenAServiceIsDown(unittest.TestCase):
    def failing(self, error: Exception) -> httpx.Client:
        def transport(request: httpx.Request) -> httpx.Response:
            raise error
        return httpx.Client(transport=httpx.MockTransport(transport), timeout=routing.TIMEOUT)

    def test_a_timeout_says_so(self):
        with self.failing(httpx.ConnectTimeout("too slow")) as client:
            with self.assertRaises(routing.ServiceTimeout) as failed:
                routing.geocode("anywhere", client)
        self.assertIn("in time", str(failed.exception))

    def test_an_unreachable_service_says_which_one(self):
        with self.failing(httpx.ConnectError("refused")) as client:
            with self.assertRaises(routing.ServiceUnavailable) as failed:
                routing.geocode("anywhere", client)
        self.assertIn("address lookup", str(failed.exception))

    def test_a_server_error_is_not_read_as_an_answer(self):
        def transport(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="down for maintenance")
        with httpx.Client(transport=httpx.MockTransport(transport)) as client:
            with self.assertRaises(routing.ServiceUnavailable) as failed:
                routing.geocode("anywhere", client)
        self.assertIn("503", str(failed.exception))

    def test_a_reply_that_is_not_json_is_not_read_as_an_answer(self):
        def transport(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="<html>gateway</html>")
        with httpx.Client(transport=httpx.MockTransport(transport)) as client:
            with self.assertRaises(routing.ServiceUnavailable):
                routing.geocode("anywhere", client)


if __name__ == "__main__":
    unittest.main()
