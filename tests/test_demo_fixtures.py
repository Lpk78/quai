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
from quai import checks  # noqa: E402
from quai.checks import find_problems  # noqa: E402
from quai.constraints import parse  # noqa: E402
from quai import solver as solver_module  # noqa: E402
from quai.solver import solve  # noqa: E402


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
    # The two stop-1 cartons. The parcel is bound for stop 1, which is loaded last, so it goes in at
    # the end and only these two shift around it. `SA-24` briefly made it a stop-8 box, which moved
    # fifteen of the eighteen; stop 1 is what brought this back to two, and it is pinned exactly so
    # that a change moving a different set turns red instead of passing on a matching count.
    SHIFTED_BY_THE_SCAN = {"B15", "B18"}
    UNMOVED_BY_THE_SCAN = {"B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10",
                           "B11", "B12", "B13", "B14", "B16", "B17"}

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
        # Three of the eighteen are unaffected by the insertion. Asserted as the complement of the
        # moved set, so the two lists cannot drift apart without one of these two tests failing.
        before = self.coordinates(demo_fixtures.plan())
        after = self.coordinates(demo_fixtures.plan(include_scanned=True))
        self.assertEqual(set(before) - self.SHIFTED_BY_THE_SCAN, self.UNMOVED_BY_THE_SCAN)
        for box in sorted(self.UNMOVED_BY_THE_SCAN):
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


class TestTheDemonstration(unittest.TestCase):
    """The moment the whole demo is built around (`SA-24`).

    An operator says "this one is fragile, put it on top" and a box moves on screen. That only means
    anything if the box was *not* already on top — a constraint satisfied before it is given changes
    nothing, and the audience sees a sentence produce no effect. Both halves are asserted here, because
    a demonstration whose central moment cannot be shown in a test is one nobody should rely on.
    """

    PARCEL = demo_fixtures.SCANNED_ITEM["code"]

    def plan_with(self, *extra):
        """The scanned load, planned the way the app plans it.

        **No route.** `Dictate.jsx` sends `POST /plan` the boxes and whatever the model returned, and
        nothing else — `unload_at` is not among the types that endpoint passes to the solver, so it
        comes back in `not_applied`. Ordering is therefore by volume alone, and that is the ordering
        the audience sees. Asserting this against the route-ordered plan would be testing a path the
        demonstration never takes.
        """
        constraints = None
        if extra:
            constraints = parse({"constraints": list(extra), "unresolved": []},
                                demo_fixtures.manifest(include_scanned=True))
        return solve(demo_fixtures.boxes(include_scanned=True), demo_fixtures.VAN, constraints)

    def above(self, plan):
        placed = next(p for p in plan.placements if p.box.id == self.PARCEL)
        return sorted(box.box.id for box in checks.covering(placed, plan.placements))

    def test_the_parcel_starts_buried(self):
        # The half that is easy to lose: tune the fixture and the parcel quietly becomes clear again,
        # at which point the demo still "works" and demonstrates nothing.
        buried = self.above(self.plan_with())
        self.assertGreaterEqual(len(buried), 2,
                                "the parcel must start under at least two boxes or the sentence "
                                "below has nothing to change")

    def test_the_sentence_clears_it(self):
        clear = self.above(self.plan_with({"type": "on_top", "item": self.PARCEL}))
        self.assertEqual(clear, [], "on_top must leave nothing above the parcel")

    def test_the_box_visibly_moves(self):
        # Not just "the column is empty": the box is somewhere else, and far enough that it reads from
        # the back of a room.
        before = next(p for p in self.plan_with().placements if p.box.id == self.PARCEL)
        after = next(p for p in self.plan_with({"type": "on_top", "item": self.PARCEL}).placements
                     if p.box.id == self.PARCEL)
        self.assertNotEqual((before.x, before.y, before.z), (after.x, after.y, after.z))
        self.assertGreater(after.z, before.z, "it should end up higher than it started")

    def test_nothing_is_lost_either_way(self):
        # A demonstration that drops a box to make its point is not one to give in front of anyone.
        for label, plan in (("baseline", self.plan_with()),
                            ("with on_top", self.plan_with({"type": "on_top", "item": self.PARCEL}))):
            with self.subTest(label):
                self.assertEqual(plan.unplaced, [])
                self.assertEqual(len(plan.placements), 19)

    def test_both_plans_pass_the_independent_checks(self):
        clear = self.plan_with({"type": "on_top", "item": self.PARCEL})
        self.assertEqual(find_problems(clear.placements, demo_fixtures.VAN,
                                       must_be_clear={self.PARCEL}), [])
        # And the baseline is *invalid* under that same rule, which is what "buried" means here.
        self.assertTrue(find_problems(self.plan_with().placements, demo_fixtures.VAN,
                                      must_be_clear={self.PARCEL}))

    def test_the_fixture_makes_no_claim_about_fragility(self):
        # The operator's line is the only place fragility may come from (`SA-24`).
        parcel = demo_fixtures.SCANNED_ITEM
        self.assertNotIn("fragile", parcel)
        self.assertNotIn("fragile", parcel["label"].lower())

    def test_every_box_in_the_load_has_a_human_name(self):
        for item in demo_fixtures.items(include_scanned=True):
            with self.subTest(item["id"]):
                self.assertTrue(item["label"].strip(), "a box with no name shows as its id on screen")
                self.assertNotEqual(item["label"], item["id"])


class TestTheSpokenLine(unittest.TestCase):
    """The sentence the demo is given, pinned against the fixture it talks about.

    It is settled wording, written in the README, and it only works because it names the box: the
    model answers *"This one is fragile, put it on top"* with `ambiguous` and the question "Which item
    is fragile?", which is correct and useless on stage. What could quietly break it is renaming the
    box — the line would then name something no longer in the load, and the model would be right to
    refuse it. That is what this checks: not the model, which costs an API call, but that the words
    still match the manifest.
    """

    LINE = "The unmarked carton is fragile, put it on top."
    README = Path(__file__).resolve().parent.parent / "README.md"

    def test_the_readme_still_carries_the_agreed_line(self):
        self.assertIn(self.LINE, self.README.read_text(encoding="utf-8"),
                      "the demo line in the README has drifted from the one that was agreed")

    def test_the_line_names_the_box_that_is_actually_scanned(self):
        # "unmarked carton" against a label of "carton, unmarked": every word of the label appears in
        # the sentence, which is what lets the model match speech to an id.
        label = demo_fixtures.SCANNED_ITEM["label"]
        spoken = self.LINE.lower()
        for word in (w.strip(" ,") for w in label.lower().split()):
            with self.subTest(word):
                self.assertIn(word, spoken,
                              f"the scanned box is called {label!r}, which the agreed line no longer "
                              f"names — rename one or the other, not just the box")

    def test_the_line_asks_for_the_constraint_the_solver_honours(self):
        # "on top" is `on_top`, which the solver honours and `POST /plan` passes. Saying "nothing on
        # top of it" would translate to `not_stackable`, which the solver refuses (#29) — the same
        # sentence in spirit, and nothing would move.
        self.assertIn("on top", self.LINE.lower())
        self.assertIn("on_top", solver_module.HONOURED)
