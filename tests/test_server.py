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
        # `not_applied` is always present, empty when every constraint reached the solver — so the
        # web app can read its length without first checking the key exists (SA-16).
        self.assertEqual(body, {"placements": [], "unplaced": [], "fill_rate": 0.0,
                                "total_weight": 0.0, "not_applied": []})

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


# A van rather than the 100 cm cube the tests above use, because the claim being tested is
# geometric: in a 100 cm container these boxes stack in y and z and every x stays 0, so "nearer the
# doors" could not be observed even when the ordering is right.
#
# The toolbox is the largest box on purpose. Without a constraint the solver loads largest first, so
# it goes in at x=0 — the back wall. `load_last` has to move it to the far end, and a test built on a
# box that was already going to be loaded last would pass while asserting nothing.
VAN = {"length": 300, "width": 170, "height": 170, "max_weight": 1200}
TOOLBOX = {"id": "toolbox", "length": 100, "width": 85, "height": 85, "weight": 20}
OTHERS = [{"id": "b1", "length": 85, "width": 85, "height": 85, "weight": 30},
          {"id": "b2", "length": 70, "width": 85, "height": 85, "weight": 25}]


class TestPlanConstraints(unittest.TestCase):
    """`POST /plan` taking constraints, the one wired type being `load_last` (SA-16)."""

    def post(self, constraints=None):
        body = {"container": VAN, "boxes": [TOOLBOX] + OTHERS}
        if constraints is not None:
            body["constraints"] = constraints
        return client.post("/plan", json=body)

    def order(self, response):
        return [p["id"] for p in response.json()["placements"]]

    def toolbox_x(self, response):
        return next(p["x"] for p in response.json()["placements"] if p["id"] == "toolbox")

    def test_a_request_without_constraints_plans_exactly_as_before(self):
        response = self.post()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order(response)[0], "toolbox")
        self.assertEqual(self.toolbox_x(response), 0)
        self.assertEqual(response.json()["not_applied"], [])

    def test_load_last_moves_the_item_to_the_end_of_the_load(self):
        before, after = self.post(), self.post([{"type": "load_last", "item": "toolbox"}])
        self.assertEqual(after.status_code, 200)
        self.assertEqual(self.order(before)[0], "toolbox", "the baseline loads it first")
        self.assertEqual(self.order(after)[-1], "toolbox", "load_last must load it last")
        self.assertEqual(after.json()["not_applied"], [])

    def test_load_last_moves_the_item_away_from_the_back_wall(self):
        # The visible effect, and the one the demo shows: x is the distance from the back wall, so a
        # box loaded last sits further forward — nearer the doors the operator opens.
        before, after = self.post(), self.post([{"type": "load_last", "item": "toolbox"}])
        self.assertGreater(self.toolbox_x(after), self.toolbox_x(before))

    def test_the_rest_of_the_plan_is_still_valid(self):
        response = self.post([{"type": "load_last", "item": "toolbox"}])
        body = response.json()
        self.assertEqual(body["unplaced"], [])
        boxes = {b["id"]: b for b in [TOOLBOX] + OTHERS}
        container = Container(VAN["length"], VAN["width"], VAN["height"], VAN["max_weight"])
        placements = [Placement(Box(p["id"], boxes[p["id"]]["length"], boxes[p["id"]]["width"],
                                    boxes[p["id"]]["height"], boxes[p["id"]]["weight"]),
                                p["x"], p["y"], p["z"], p["dx"], p["dy"], p["dz"])
                      for p in body["placements"]]
        self.assertEqual(find_problems(placements, container), [])

    def test_a_type_the_solver_cannot_honour_is_reported_not_dropped(self):
        response = self.post([{"type": "on_top", "item": "toolbox"}])
        self.assertEqual(response.status_code, 200)
        not_applied = response.json()["not_applied"]
        self.assertEqual([e["type"] for e in not_applied], ["on_top"])
        self.assertEqual(not_applied[0]["item"], "toolbox")
        self.assertIn("#29", not_applied[0]["reason"])

    def test_a_type_the_solver_honours_but_this_endpoint_does_not_pass_is_reported(self):
        # 50 kg against a 75 kg load: had the cap been applied, the solver would have left `b2` out.
        # Asserting nothing was unplaced is what proves the constraint was reported, not quietly used.
        response = self.post([{"type": "max_total_weight", "limit_kg": 50}])
        self.assertEqual(response.status_code, 200)
        not_applied = response.json()["not_applied"]
        self.assertEqual([e["type"] for e in not_applied], ["max_total_weight"])
        self.assertIn("#19", not_applied[0]["reason"])
        self.assertEqual(response.json()["unplaced"], [])
        self.assertEqual(response.json()["total_weight"], 75)

    def test_unload_at_says_why_a_route_is_missing(self):
        response = self.post([{"type": "unload_at", "item": "toolbox", "stop": "S2"}])
        self.assertEqual(response.status_code, 200)
        self.assertIn("no route", response.json()["not_applied"][0]["reason"])

    def test_a_wired_and_an_unwired_constraint_in_one_call(self):
        response = self.post([{"type": "load_last", "item": "toolbox"},
                              {"type": "at_bottom", "item": "b1"}])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order(response)[-1], "toolbox", "the wired one still applies")
        self.assertEqual([e["type"] for e in response.json()["not_applied"]], ["at_bottom"])

    def test_a_type_outside_the_contract_is_refused(self):
        response = self.post([{"type": "teleport", "item": "toolbox"}])
        self.assertEqual(response.status_code, 422)
        self.assertIn("teleport", response.json()["detail"])

    def test_a_malformed_constraint_is_refused_even_when_it_is_not_wired(self):
        """The whole list is validated before any of it is applied *or reported*.

        Reporting a `max_weight_on` that carries no `limit_kg` back as "honoured but not passed yet"
        would be saying something false about it: it is not a constraint at all. Found by MORHI11 in
        review of #51, where `not_applied` was the one path that reported instead of refusing.
        """
        for label, constraint in (
            ("missing field", {"type": "max_weight_on", "item": "toolbox"}),
            ("undeclared field", {"type": "on_top", "item": "toolbox", "bogus_field": 123}),
            ("item not in the load", {"type": "at_bottom", "item": "does-not-exist"}),
            ("limit not a number", {"type": "max_total_weight", "limit_kg": "heavy"}),
            ("limit not positive", {"type": "max_total_weight", "limit_kg": -5}),
            ("stop not a string", {"type": "unload_at", "item": "toolbox", "stop": 123}),
        ):
            with self.subTest(label):
                response = self.post([constraint])
                self.assertEqual(response.status_code, 422)
                self.assertIn("did not validate", response.json()["detail"])

    def test_the_three_faults_in_one_constraint_are_all_refused(self):
        # MORHI11's payload verbatim: no `limit_kg`, an item that is not in the load, and a field the
        # type does not declare. It used to come back 200 with the whole thing echoed into
        # `not_applied`.
        response = self.post([{"type": "max_weight_on", "item": "does-not-exist",
                               "bogus_field": 123}])
        self.assertEqual(response.status_code, 422)
        detail = response.json()["detail"]
        self.assertIn("limit_kg", detail)
        self.assertIn("does-not-exist", detail)
        self.assertIn("bogus_field", detail)

    def test_a_well_formed_unload_at_is_still_reported_rather_than_refused(self):
        # The line to hold: validation must not turn an unwired-but-valid constraint into an error.
        # This endpoint has no route, so the stop cannot be checked against one — only that it is a
        # stop id at all.
        response = self.post([{"type": "unload_at", "item": "toolbox", "stop": "S7"}])
        self.assertEqual(response.status_code, 200)
        self.assertEqual([e["type"] for e in response.json()["not_applied"]], ["unload_at"])

    def test_one_bad_constraint_refuses_the_whole_request(self):
        # Not "apply the good one and report the bad one": a caller who sent something malformed gets
        # told, rather than a plan built from the half that parsed.
        response = self.post([{"type": "load_last", "item": "toolbox"},
                              {"type": "max_weight_on", "item": "toolbox"}])
        self.assertEqual(response.status_code, 422)

    def test_load_last_naming_a_box_not_in_the_load_is_refused(self):
        response = self.post([{"type": "load_last", "item": "ghost"}])
        self.assertEqual(response.status_code, 422)
        self.assertIn("ghost", response.json()["detail"])

    def test_an_empty_constraint_list_is_not_sent_through_parse(self):
        # `parse()` refuses a payload with nothing in it, so an empty list has to mean "no
        # constraints" rather than becoming one.
        response = self.post([])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.order(response)[0], "toolbox")


if __name__ == "__main__":
    unittest.main()
