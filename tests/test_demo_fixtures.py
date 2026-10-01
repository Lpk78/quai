"""The demo fixture has to survive a change to the solver, not just run once on the day.

These are the three claims the demo makes out loud: the van is about three quarters full, every box
in the manifest is actually in it, and scanning the parcel adds it without ejecting anything. Each is
cheap to assert and none of them calls an API.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import demo_fixtures  # noqa: E402
from quai.checks import find_problems  # noqa: E402


class TestLoadedVan(unittest.TestCase):
    def setUp(self):
        self.plan = demo_fixtures.plan()

    def test_every_box_in_the_manifest_is_placed(self):
        self.assertEqual(len(self.plan.placements), len(demo_fixtures.LOADED_ITEMS))
        self.assertEqual(self.plan.unplaced, [])

    def test_the_fill_rate_is_the_one_the_demo_quotes(self):
        # The range the fixture was tuned to. A solver change that moves the load outside it is not
        # necessarily wrong, but the slide saying "about 78%" would be.
        self.assertGreaterEqual(self.plan.fill_rate, 0.75)
        self.assertLessEqual(self.plan.fill_rate, 0.80)

    def test_the_plan_passes_the_independent_checks(self):
        self.assertEqual(find_problems(self.plan.placements, demo_fixtures.VAN), [])

    def test_the_load_is_inside_the_weight_limit(self):
        self.assertLessEqual(self.plan.total_weight, demo_fixtures.VAN.max_weight)


class TestScannedParcel(unittest.TestCase):
    # The two stop-1 cartons. Stop 1 comes off first, so it is loaded last — after the parcel, which
    # goes in 17th of 19 — and these two end up on different corners once it is in. They are pinned
    # rather than tolerated: until issue #36 lets the solver plan around what is already in the van,
    # two boxes moving is a fact of this fixture, and a solver change that moved a third should turn
    # this red rather than surprise anyone mid-demo.
    SHIFTED_BY_THE_SCAN = {"B15", "B18"}

    @staticmethod
    def coordinates(plan):
        return {p.box.id: (p.x, p.y, p.z, p.dx, p.dy, p.dz) for p in plan.placements}

    def test_scanning_places_it_without_ejecting_anything(self):
        before, after = demo_fixtures.plan(), demo_fixtures.plan(include_scanned=True)
        self.assertEqual(after.unplaced, [], "scanning the parcel ejected a box already loaded")
        self.assertEqual(len(after.placements), len(before.placements) + 1)
        self.assertIn(demo_fixtures.SCANNED_ITEM["code"],
                      [p.box.id for p in after.placements])

    def test_scanning_moves_exactly_the_two_stop_one_cartons(self):
        before = self.coordinates(demo_fixtures.plan())
        after = self.coordinates(demo_fixtures.plan(include_scanned=True))
        moved = {box for box, place in before.items() if after[box] != place}
        self.assertEqual(moved, self.SHIFTED_BY_THE_SCAN)

    def test_every_other_box_keeps_its_coordinates(self):
        # The half of the claim that does hold, and the one the demo depends on: sixteen of the
        # eighteen do not budge when the parcel goes in.
        before = self.coordinates(demo_fixtures.plan())
        after = self.coordinates(demo_fixtures.plan(include_scanned=True))
        for box in sorted(set(before) - self.SHIFTED_BY_THE_SCAN):
            with self.subTest(box):
                self.assertEqual(after[box], before[box])

    def test_it_starts_outside_the_load(self):
        self.assertNotIn(demo_fixtures.SCANNED_ITEM["code"],
                         [i["id"] for i in demo_fixtures.LOADED_ITEMS])

    def test_the_plan_with_it_still_passes_the_independent_checks(self):
        plan = demo_fixtures.plan(include_scanned=True)
        self.assertEqual(find_problems(plan.placements, demo_fixtures.VAN), [])


class TestRouteReachesTheSolverThroughTheContract(unittest.TestCase):
    def test_every_box_is_given_a_stop_on_the_route(self):
        stops = {stop["id"] for stop in demo_fixtures.STOPS}
        for item in demo_fixtures.items(include_scanned=True):
            with self.subTest(item["id"]):
                self.assertIn(item["stop"], stops)

    def test_the_constraint_set_is_built_by_parse(self):
        # Not a style check: `parse()` is the only door into the solver, so a fixture that built a
        # ConstraintSet by hand would be exercising a path production does not have.
        constraints = demo_fixtures.constraint_set(include_scanned=True)
        self.assertEqual(len(constraints.of_type("unload_at")),
                         len(demo_fixtures.items(include_scanned=True)))
        self.assertEqual(constraints.unresolved, ())


if __name__ == "__main__":
    unittest.main()
