"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from quai import routing  # noqa: E402
from quai.checks import find_problems  # noqa: E402
from quai.models import Box, Container, Placement  # noqa: E402
from server import app  # noqa: E402

client = TestClient(app)

CONTAINER = {"length": 100, "width": 100, "height": 100, "max_weight": 500}


def cubes(n: int, size: int = 50, weight: float = 10) -> list[dict]:
    return [{"id": f"c{i}", "length": size, "width": size, "height": size, "weight": weight}
            for i in range(n)]


class TestPlanEndpoint(unittest.TestCase):
    def post(self, boxes, container=CONTAINER):
        return client.post("/plan", json={"container": container, "boxes": boxes})

    def test_places_boxes_and_reports_fill_rate(self):
        response = self.post(cubes(8))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body["placements"]), 8)
        self.assertEqual(body["unplaced"], [])
        self.assertAlmostEqual(body["fill_rate"], 1.0)
        self.assertEqual(body["total_weight"], 80)

    def test_returned_plan_passes_the_independent_check(self):
        boxes = cubes(3, size=40) + [{"id": "flat", "length": 90, "width": 60, "height": 20}]
        body = self.post(boxes).json()
        by_id = {b["id"]: b for b in boxes}
        placements = [
            Placement(Box(p["id"], by_id[p["id"]]["length"], by_id[p["id"]]["width"],
                          by_id[p["id"]]["height"], by_id[p["id"]].get("weight", 0.0)),
                      p["x"], p["y"], p["z"], p["dx"], p["dy"], p["dz"])
            for p in body["placements"]]
        self.assertEqual(find_problems(placements, Container(100, 100, 100, 500)), [])

    def test_box_that_does_not_fit_is_unplaced_not_an_error(self):
        response = self.post([{"id": "long", "length": 150, "width": 10, "height": 10}])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["placements"], [])
        self.assertEqual(response.json()["unplaced"], ["long"])

    def test_weight_limit_is_applied(self):
        body = self.post(cubes(2, weight=300)).json()
        self.assertEqual(len(body["placements"]), 1)
        self.assertEqual(len(body["unplaced"]), 1)

    def test_max_weight_is_optional(self):
        container = {"length": 100, "width": 100, "height": 100}
        body = self.post(cubes(2, weight=1000), container).json()
        self.assertEqual(len(body["placements"]), 2)

    def test_empty_box_list_gives_an_empty_plan(self):
        body = self.post([]).json()
        self.assertEqual(body, {"placements": [], "unplaced": [], "fill_rate": 0.0,
                                "total_weight": 0.0})

    def test_zero_sized_container_is_rejected(self):
        # A zero volume would divide by zero in Plan.fill_rate (issue #15).
        response = self.post(cubes(1), {"length": 0, "width": 100, "height": 100})
        self.assertEqual(response.status_code, 422)

    def test_invalid_box_is_rejected(self):
        for field, value in (("length", 0), ("height", -5), ("weight", -1)):
            with self.subTest(field):
                box = cubes(1)[0] | {field: value}
                self.assertEqual(self.post([box]).status_code, 422)

    def test_duplicate_box_ids_are_rejected(self):
        response = self.post(cubes(1) + cubes(1))
        self.assertEqual(response.status_code, 422)
        self.assertIn("c0", response.json()["detail"])

    def test_missing_field_is_rejected(self):
        self.assertEqual(client.post("/plan", json={"boxes": []}).status_code, 422)


class TestCrossOrigin(unittest.TestCase):
    """The web app (#18) runs on its own origin, so the browser needs this to let it call the API."""

    def test_the_vite_dev_server_is_allowed(self):
        response = client.options(
            "/plan",
            headers={"Origin": "http://localhost:5173",
                     "Access-Control-Request-Method": "POST",
                     "Access-Control-Request-Headers": "content-type"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")

    def test_a_real_request_carries_the_header_back(self):
        response = client.post("/plan", json={"container": CONTAINER, "boxes": []},
                               headers={"Origin": "http://localhost:5173"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")

    def test_an_unknown_origin_is_not_allowed(self):
        # Not a wildcard: this API is the only place the Claude key lives, so any page in the
        # operator's browser must not be able to call it.
        response = client.post("/plan", json={"container": CONTAINER, "boxes": []},
                               headers={"Origin": "https://example.com"})
        self.assertNotIn("access-control-allow-origin", response.headers)


class TestRouteEndpoint(unittest.TestCase):
    """`POST /route` over mocked services. The order of the stops is the thing under test."""

    AMIENS = (2.290084, 49.897442)
    PARIS = (2.352200, 48.856600)
    LILLE = (3.057300, 50.629200)

    def stops(self):
        """Lille, then Amiens, then Paris — an order no sort would produce.

        Sorting these by longitude, by latitude or by name each gives a different sequence, so a
        reordering bug cannot hide behind the fixture.
        """
        return [{"id": "S1", "address": "Lille"},
                {"id": "S2", "address": "Amiens"},
                {"id": "S3", "address": "Paris"}]

    def services(self, points=None, legs_seconds=(600.0, 1200.0), code="Ok"):
        """A geocoder and a router that answer from a table, recording the URLs they were asked."""
        found = {"Amiens": self.AMIENS, "Paris": self.PARIS, "Lille": self.LILLE}
        if points is not None:
            found = points
        urls = []

        def transport(request: httpx.Request) -> httpx.Response:
            urls.append(str(request.url))
            if "api-adresse" in request.url.host:
                q = request.url.params.get("q", "")
                if q not in found:
                    return httpx.Response(200, json={"features": []})
                lon, lat = found[q]
                return httpx.Response(200, json={
                    "features": [{"geometry": {"type": "Point", "coordinates": [lon, lat]},
                                  "properties": {"label": f"{q}, France"}}]})
            legs = [{"distance": 1000.0, "duration": d} for d in legs_seconds]
            return httpx.Response(200, json={
                "code": code,
                "routes": [{"distance": 1000.0 * len(legs), "duration": sum(legs_seconds),
                            "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                            "legs": legs}]})

        def build():
            return httpx.Client(transport=httpx.MockTransport(transport))
        return build, urls

    def post(self, body, **kwargs):
        build, urls = self.services(**kwargs)
        with mock.patch.object(routing, "build_client", build):
            return client.post("/route", json=body), urls

    def test_the_stops_come_back_in_the_order_they_were_sent(self):
        response, _ = self.post({"stops": self.stops()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([s["id"] for s in response.json()["stops"]], ["S1", "S2", "S3"])

    def test_the_router_is_asked_for_that_same_order(self):
        """Not just the response: the order must reach OSRM, or the geometry is another trip."""
        _, urls = self.post({"stops": self.stops()})
        router = [u for u in urls if "osrm" in u][0]
        self.assertIn("3.0573,50.6292;2.290084,49.897442;2.3522,48.8566", router)
        self.assertNotIn("/trip/", router)

    def test_every_stop_carries_its_point_and_label(self):
        response, _ = self.post({"stops": self.stops()})
        first = response.json()["stops"][0]
        self.assertEqual((first["lon"], first["lat"]), self.LILLE)
        self.assertEqual(first["label"], "Lille, France")

    def test_arrival_times_accumulate_from_the_first_stop(self):
        response, _ = self.post({"stops": self.stops()})
        self.assertEqual([s["eta_seconds"] for s in response.json()["stops"]], [0.0, 600.0, 1800.0])

    def test_a_departure_time_turns_offsets_into_instants(self):
        response, _ = self.post({"stops": self.stops(),
                                 "departure_time": "2026-10-02T08:00:00+00:00"})
        etas = [s["eta"] for s in response.json()["stops"]]
        self.assertTrue(etas[0].startswith("2026-10-02T08:00:00"))
        self.assertTrue(etas[2].startswith("2026-10-02T08:30:00"))

    def test_without_a_departure_time_there_is_no_instant_to_give(self):
        response, _ = self.post({"stops": self.stops()})
        self.assertEqual([s["eta"] for s in response.json()["stops"]], [None, None, None])

    def test_totals_are_reported(self):
        body = self.post({"stops": self.stops()})[0].json()
        self.assertEqual(body["total_distance_m"], 2000.0)
        self.assertEqual(body["total_duration_s"], 1800.0)
        self.assertEqual(body["geometry"]["type"], "LineString")

    def test_one_stop_is_rejected_before_any_call(self):
        response, urls = self.post({"stops": [{"id": "S1", "address": "Lille"}]})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(urls, [])

    def test_duplicate_stop_ids_are_rejected(self):
        response, _ = self.post({"stops": [{"id": "S1", "address": "Lille"},
                                           {"id": "S1", "address": "Paris"}]})
        self.assertEqual(response.status_code, 422)
        self.assertIn("S1", response.json()["detail"])

    def test_an_address_that_matches_nothing_is_a_422_naming_it(self):
        response, _ = self.post({"stops": [{"id": "S1", "address": "Lille"},
                                           {"id": "S2", "address": "nowhere at all"}]})
        self.assertEqual(response.status_code, 422)
        self.assertIn("nowhere at all", response.json()["detail"])

    def test_a_router_refusal_is_a_502(self):
        response, _ = self.post({"stops": self.stops()}, code="NoRoute")
        self.assertEqual(response.status_code, 502)

    def test_a_service_that_times_out_is_a_504(self):
        def transport(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("too slow")

        def build():
            return httpx.Client(transport=httpx.MockTransport(transport))
        with mock.patch.object(routing, "build_client", build):
            response = client.post("/route", json={"stops": self.stops()})
        self.assertEqual(response.status_code, 504)
        self.assertIn("in time", response.json()["detail"])

    def test_a_service_that_is_down_is_a_502(self):
        def transport(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="maintenance")

        def build():
            return httpx.Client(transport=httpx.MockTransport(transport))
        with mock.patch.object(routing, "build_client", build):
            response = client.post("/route", json={"stops": self.stops()})
        self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
