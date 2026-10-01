"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
