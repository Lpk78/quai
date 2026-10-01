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


class TestRecomputeEndpoint(unittest.TestCase):
    """`POST /plan/recompute`: the vehicle keeps what is in it, the dock gets replanned."""

    VAN = {"length": 100, "width": 100, "height": 200, "max_weight": 1000}

    def slab(self, box_id: str, z: int, weight: float = 5.0) -> dict:
        return {"box": {"id": box_id, "length": 100, "width": 100, "height": 20, "weight": weight},
                "x": 0, "y": 0, "z": z, "dx": 100, "dy": 100, "dz": 20}

    def crate(self, box_id: str, weight: float = 5.0) -> dict:
        return {"id": box_id, "length": 100, "width": 100, "height": 20, "weight": weight}

    def post(self, **body):
        body.setdefault("container", self.VAN)
        return client.post("/plan/recompute", json=body)

    def test_a_missing_box_is_simply_not_loaded(self):
        response = self.post(loaded=[self.slab("a", 0)], waiting=[self.crate("b"), self.crate("c")],
                             incident={"kind": "missing", "box_id": "b"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(p["id"] for p in response.json()["placements"]), ["a", "c"])

    def test_the_box_already_loaded_keeps_its_place(self):
        response = self.post(loaded=[self.slab("a", 0)], waiting=[self.crate("b")],
                             incident={"kind": "missing", "box_id": "b"})
        a = [p for p in response.json()["placements"] if p["id"] == "a"][0]
        self.assertEqual((a["x"], a["y"], a["z"]), (0, 0, 0))

    def test_a_damaged_box_in_the_vehicle_comes_out_and_frees_its_space(self):
        """The bottom slab is damaged, so the box waiting on the dock can take the floor."""
        response = self.post(loaded=[self.slab("a", 0)], waiting=[self.crate("b")],
                             incident={"kind": "damaged", "box_id": "a"})
        placements = response.json()["placements"]
        self.assertEqual([p["id"] for p in placements], ["b"])
        self.assertEqual(placements[0]["z"], 0)

    def test_an_added_box_is_planned_with_the_rest(self):
        response = self.post(loaded=[self.slab("a", 0)], waiting=[self.crate("b")],
                             incident={"kind": "added", "box_id": "new", "box": self.crate("new")})
        self.assertEqual(sorted(p["id"] for p in response.json()["placements"]), ["a", "b", "new"])

    def test_a_box_in_the_vehicle_cannot_be_missing(self):
        response = self.post(loaded=[self.slab("a", 0)], waiting=[],
                             incident={"kind": "missing", "box_id": "a"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("already in the vehicle", response.json()["detail"])

    def test_an_unknown_incident_kind_is_refused(self):
        response = self.post(loaded=[], waiting=[self.crate("b")],
                             incident={"kind": "set on fire", "box_id": "b"})
        self.assertEqual(response.status_code, 422)

    def test_adding_a_box_without_the_box_is_refused(self):
        response = self.post(loaded=[], waiting=[self.crate("b")],
                             incident={"kind": "added", "box_id": "new"})
        self.assertEqual(response.status_code, 422)
        self.assertIn("dimensions", response.json()["detail"])

    def test_an_overlapping_starting_state_is_refused(self):
        response = self.post(loaded=[self.slab("a", 0), self.slab("b", 10)], waiting=[],
                             incident={"kind": "added", "box_id": "n", "box": self.crate("n")})
        self.assertEqual(response.status_code, 422)
        self.assertIn("valid load", response.json()["detail"])

    def test_the_same_box_loaded_and_waiting_is_refused(self):
        response = self.post(loaded=[self.slab("a", 0)], waiting=[self.crate("a")],
                             incident={"kind": "added", "box_id": "n", "box": self.crate("n")})
        self.assertEqual(response.status_code, 422)
        self.assertIn("duplicate", response.json()["detail"])

    def test_the_stop_order_still_decides_what_goes_in_first(self):
        """The same rule as the first plan: the last stop is loaded first."""
        response = self.post(
            loaded=[], waiting=[self.crate("x"), self.crate("y")],
            incident={"kind": "added", "box_id": "z", "box": self.crate("z")},
            stops=["S1", "S2"],
            constraints={"constraints": [{"type": "unload_at", "item": "x", "stop": "S1"},
                                         {"type": "unload_at", "item": "y", "stop": "S2"}],
                         "unresolved": []})
        self.assertEqual(response.status_code, 200)
        order = [p["id"] for p in response.json()["placements"]]
        self.assertLess(order.index("y"), order.index("x"))

    def test_constraints_are_revalidated_against_the_load_as_it_now_is(self):
        """The damaged box is gone, so a constraint still naming it cannot be honoured."""
        response = self.post(
            loaded=[], waiting=[self.crate("b"), self.crate("c")],
            incident={"kind": "damaged", "box_id": "b"},
            stops=["S1"],
            constraints={"constraints": [{"type": "unload_at", "item": "b", "stop": "S1"}],
                         "unresolved": []})
        self.assertEqual(response.status_code, 422)
        self.assertIn("manifest", response.json()["detail"])

    def test_constraints_without_the_route_are_refused(self):
        response = self.post(
            loaded=[], waiting=[self.crate("b")],
            incident={"kind": "added", "box_id": "n", "box": self.crate("n")},
            constraints={"constraints": [{"type": "load_last", "item": "b"}], "unresolved": []})
        self.assertEqual(response.status_code, 422)
        self.assertIn("route", response.json()["detail"])

    def test_a_constraint_the_solver_cannot_honour_is_refused(self):
        response = self.post(
            loaded=[], waiting=[self.crate("b")],
            incident={"kind": "added", "box_id": "n", "box": self.crate("n")},
            stops=["S1"],
            constraints={"constraints": [{"type": "at_bottom", "item": "b"}], "unresolved": []})
        self.assertEqual(response.status_code, 422)
        self.assertIn("at_bottom", response.json()["detail"])

    def test_the_returned_plan_is_physically_valid(self):
        response = self.post(loaded=[self.slab("a", 0)],
                             waiting=[self.crate("b"), self.crate("c")],
                             incident={"kind": "added", "box_id": "d", "box": self.crate("d")})
        placements = [Placement(Box(p["id"], p["dx"], p["dy"], p["dz"]),
                                p["x"], p["y"], p["z"], p["dx"], p["dy"], p["dz"])
                      for p in response.json()["placements"]]
        container = Container(self.VAN["length"], self.VAN["width"], self.VAN["height"],
                              max_weight=self.VAN["max_weight"])
        self.assertEqual(find_problems(placements, container), [])


if __name__ == "__main__":
    unittest.main()
