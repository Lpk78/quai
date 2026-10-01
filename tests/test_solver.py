"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quai import checks, solver as solver_module  # noqa: E402
from quai.checks import find_problems, overlaps, weight_above  # noqa: E402
from quai.constraints import Manifest, parse  # noqa: E402
from quai.models import Box, Container, Placement, Plan  # noqa: E402
from quai.solver import UnsupportedConstraint, solve, unhandled  # noqa: E402

CONTAINER = Container(100, 100, 100, max_weight=500)


def cubes(n: int, size: int = 50, weight: float = 10) -> list[Box]:
    return [Box(f"c{i}", size, size, size, weight) for i in range(n)]


def constraint_set(boxes: list[Box], stops, *constraints):
    """A validated set for these boxes, built the only way the solver ever gets one."""
    payload = {"constraints": list(constraints), "unresolved": []}
    return parse(payload, Manifest.from_boxes(boxes, stops))


def slabs(*weights: float) -> list[Box]:
    """Boxes that fill the floor of CONTAINER, so the only room left is on top of each other."""
    return [Box(chr(ord("a") + i), 100, 100, 20, w) for i, w in enumerate(weights)]


def half(box_id: str, height: int) -> Box:
    """Half the floor of CONTAINER, so two of them fit side by side and both can have a clear top."""
    return Box(box_id, 100, 50, height, 5)


def crate(box_id: str, height: int) -> Box:
    """A box filling the floor of CONTAINER; its height is its volume, so the largest-first
    tie-break is easy to tell apart from the order the route asks for."""
    return Box(box_id, 100, 100, height, 5)


class TestChecks(unittest.TestCase):
    def test_overlap_detected(self):
        box = Box("a", 10, 10, 10)
        self.assertTrue(overlaps(Placement(box, 0, 0, 0, 10, 10, 10),
                                 Placement(box, 5, 5, 5, 10, 10, 10)))

    def test_touching_faces_do_not_overlap(self):
        box = Box("a", 10, 10, 10)
        self.assertFalse(overlaps(Placement(box, 0, 0, 0, 10, 10, 10),
                                  Placement(box, 10, 0, 0, 10, 10, 10)))

    def test_floating_box_is_reported(self):
        box = Box("a", 10, 10, 10)
        problems = find_problems([Placement(box, 0, 0, 50, 10, 10, 10)], CONTAINER)
        self.assertIn("a is not supported enough", problems)

    def test_shrunk_box_is_reported(self):
        """A placement may not claim dimensions smaller than the box really is."""
        fridge = Box("fridge", 70, 70, 90)
        problems = find_problems([Placement(fridge, 0, 0, 0, 10, 10, 10)], CONTAINER)
        self.assertIn("fridge is not one of its upright rotations", problems)

    def test_box_lying_on_its_side_is_reported(self):
        """Boxes stay upright, so swapping a side with the height is not allowed."""
        fridge = Box("fridge", 70, 70, 90)
        problems = find_problems([Placement(fridge, 0, 0, 0, 90, 70, 70)], CONTAINER)
        self.assertIn("fridge is not one of its upright rotations", problems)

    def test_footprint_rotation_is_still_accepted(self):
        """The legitimate rotation must not be caught by the check above."""
        desk = Box("desk", 80, 40, 40)
        problems = find_problems([Placement(desk, 0, 0, 0, 40, 80, 40)], CONTAINER)
        self.assertEqual(problems, [])

    def test_minimum_support_is_defined_once(self):
        """The solver and the checks must agree on what counts as supported enough."""
        self.assertIs(solver_module.MIN_SUPPORT, checks.MIN_SUPPORT)

    def test_box_placed_twice_is_reported(self):
        fridge = Box("fridge", 30, 30, 30)
        twice = [Placement(fridge, 0, 0, 0, 30, 30, 30),
                 Placement(fridge, 30, 0, 0, 30, 30, 30)]
        self.assertIn("fridge is placed 2 times", find_problems(twice, CONTAINER))


def stack(*weights: float) -> list[Placement]:
    """One column of 50 x 50 x 20 boxes, `s0` on the floor and each next one on the previous."""
    return [Placement(Box(f"s{i}", 50, 50, 20, w), 0, 0, i * 20, 50, 50, 20)
            for i, w in enumerate(weights)]


class TestStackWeight(unittest.TestCase):
    """`max_weight_on` covers the whole stack above an item, not only what rests on it directly
    (contract, *Route and unloading order*)."""

    def test_weight_above_counts_the_whole_column(self):
        column = stack(5, 15, 10)
        self.assertEqual(weight_above(column[0], column), 25)

    def test_weight_above_stops_at_the_box_itself(self):
        column = stack(5, 15, 10)
        self.assertEqual(weight_above(column[2], column), 0)

    def test_a_neighbour_is_not_above(self):
        column = stack(5, 15)
        beside = Placement(Box("beside", 50, 50, 20, 40), 50, 0, 0, 50, 50, 20)
        self.assertEqual(weight_above(column[0], column + [beside]), 15)

    def test_stack_over_the_limit_is_reported(self):
        column = stack(5, 15, 10)
        problems = find_problems(column, CONTAINER, max_weight_on={"s0": 20})
        self.assertIn("s0 carries 25 kg, more than its 20 kg limit", problems)

    def test_direct_neighbour_alone_would_stay_under_the_limit(self):
        """The 15 kg resting directly on s0 is within 20 kg: only the whole stack breaks it."""
        column = stack(5, 15, 10)
        self.assertEqual(find_problems(column[:2], CONTAINER, max_weight_on={"s0": 20}), [])

    def test_a_stack_exactly_at_the_limit_is_accepted(self):
        column = stack(5, 15, 10)
        self.assertEqual(find_problems(column, CONTAINER, max_weight_on={"s0": 25}), [])

    def test_a_box_with_no_limit_is_not_checked(self):
        """s0 carries 25 kg, but the operator only gave a limit for s1, which carries 10 kg."""
        column = stack(5, 15, 10)
        self.assertEqual(find_problems(column, CONTAINER, max_weight_on={"s1": 20}), [])


class TestBox(unittest.TestCase):
    def test_zero_dimension_is_refused(self):
        """A zero side used to reach support_ratio and raise ZeroDivisionError."""
        with self.assertRaises(ValueError):
            Box("z", 0, 10, 10)

    def test_negative_dimension_is_refused(self):
        with self.assertRaises(ValueError):
            Box("n", -5, 10, 10)

    def test_negative_weight_is_refused(self):
        with self.assertRaises(ValueError):
            Box("w", 10, 10, 10, -1.0)

    def test_valid_box_is_still_accepted(self):
        self.assertEqual(Box("ok", 10, 20, 30, 1.5).volume, 6000)


class TestContainer(unittest.TestCase):
    def test_zero_dimension_is_refused(self):
        """A zero side used to be accepted and raise ZeroDivisionError later, in fill_rate."""
        for sides in ((0, 200, 200), (200, 0, 200), (200, 200, 0)):
            with self.subTest(sides), self.assertRaises(ValueError):
                Container(*sides)

    def test_negative_dimension_is_refused(self):
        with self.assertRaises(ValueError):
            Container(-400, 200, 200)

    def test_negative_max_weight_is_refused(self):
        with self.assertRaises(ValueError):
            Container(100, 100, 100, max_weight=-1)

    def test_error_names_the_field_and_the_value(self):
        with self.assertRaisesRegex(ValueError, "length must be greater than 0, got 0"):
            Container(0, 200, 200)

    def test_valid_container_is_still_accepted(self):
        self.assertEqual(Container(100, 40, 100).volume, 400_000)
        self.assertEqual(Container(100, 40, 100, max_weight=0).max_weight, 0)


class TestPlan(unittest.TestCase):
    def test_fill_rate_of_a_zero_volume_container_is_zero(self):
        # Container refuses this at construction; force it past validation to test the guard.
        container = Container(100, 100, 100)
        object.__setattr__(container, "length", 0)
        self.assertEqual(Plan(container, [], []).fill_rate, 0.0)

    def test_fill_rate_is_unchanged_for_a_normal_plan(self):
        box = Box("half", 50, 100, 100)
        plan = Plan(CONTAINER, [Placement(box, 0, 0, 0, 50, 100, 100)], [])
        self.assertEqual(plan.fill_rate, 0.5)


class TestSolver(unittest.TestCase):
    def test_exact_fit_uses_all_space(self):
        plan = solve(cubes(8), CONTAINER)
        self.assertEqual(len(plan.placements), 8)
        self.assertAlmostEqual(plan.fill_rate, 1.0)
        self.assertEqual(find_problems(plan.placements, CONTAINER), [])

    def test_ninth_cube_is_left_out(self):
        plan = solve(cubes(9), CONTAINER)
        self.assertEqual(len(plan.placements), 8)
        self.assertEqual(len(plan.unplaced), 1)

    def test_box_larger_than_container_is_not_forced_in(self):
        plan = solve([Box("huge", 150, 50, 50)], CONTAINER)
        self.assertEqual(plan.placements, [])
        self.assertEqual([b.id for b in plan.unplaced], ["huge"])

    def test_rotation_is_used_when_needed(self):
        plan = solve([Box("long", 40, 100, 20)], Container(100, 40, 100))
        self.assertEqual(len(plan.placements), 1)

    def test_weight_limit_is_respected(self):
        plan = solve(cubes(8, weight=100), CONTAINER)
        self.assertLessEqual(plan.total_weight, CONTAINER.max_weight)
        self.assertEqual(len(plan.placements), 5)

    def test_same_input_gives_same_plan(self):
        boxes = [Box(f"b{i}", 10 + i * 7 % 40, 20 + i * 3 % 30, 15 + i % 25) for i in range(30)]
        self.assertEqual(solve(boxes, CONTAINER).placements, solve(boxes, CONTAINER).placements)

    def test_stack_limit_keeps_a_box_off(self):
        """Nothing may be stacked on `a` beyond 10 kg, and there is nowhere else for b and c."""
        boxes = slabs(5, 20, 20)
        limited = constraint_set(boxes, ("S1",),
                                 {"type": "max_weight_on", "item": "a", "limit_kg": 10})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual([p.box.id for p in plan.placements], ["a"])
        self.assertEqual([b.id for b in plan.unplaced], ["b", "c"])

    def test_the_same_load_stacks_without_the_limit(self):
        """The three boxes do fit: it is the limit that keeps two of them out above."""
        plan = solve(slabs(5, 20, 20), CONTAINER)
        self.assertEqual([p.box.id for p in plan.placements], ["a", "b", "c"])

    def test_the_limit_counts_the_whole_stack_not_the_box_resting_on_it(self):
        """c rests on b, not on a, but its 10 kg still bear on a: 15 + 10 is over a's 20 kg."""
        boxes = slabs(5, 15, 10)
        limited = constraint_set(boxes, ("S1",),
                                 {"type": "max_weight_on", "item": "a", "limit_kg": 20})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual([p.box.id for p in plan.placements], ["a", "b"])
        self.assertEqual([b.id for b in plan.unplaced], ["c"])

    def test_a_stack_exactly_at_the_limit_is_still_loaded(self):
        boxes = slabs(5, 15, 10)
        limited = constraint_set(boxes, ("S1",),
                                 {"type": "max_weight_on", "item": "a", "limit_kg": 25})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual([p.box.id for p in plan.placements], ["a", "b", "c"])

    def test_the_plan_passes_the_independent_stack_check(self):
        boxes = slabs(5, 15, 10)
        limits = {"a": 20}
        limited = constraint_set(boxes, ("S1",),
                                 {"type": "max_weight_on", "item": "a", "limit_kg": 20})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual(find_problems(plan.placements, CONTAINER, max_weight_on=limits), [])

    def test_stated_total_weight_lowers_the_vehicle_limit(self):
        boxes = cubes(8, weight=100)
        limited = constraint_set(boxes, ("S1",), {"type": "max_total_weight", "limit_kg": 250})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual(plan.total_weight, 200)

    def test_stated_total_weight_cannot_raise_the_vehicle_limit(self):
        """900 kg is what the operator allows; the vehicle still carries 500."""
        boxes = cubes(8, weight=100)
        generous = constraint_set(boxes, ("S1",), {"type": "max_total_weight", "limit_kg": 900})
        plan = solve(boxes, CONTAINER, generous)
        self.assertEqual(plan.total_weight, 500)

    def test_a_box_cannot_slide_under_a_load_it_may_not_carry(self):
        """`top` overhangs `tall`, and `victim` is the only box that fits in the gap under it.

        Going there would make `victim` a support for `top` after `top` was already placed, so the
        30 kg land on a box that may take 10. The limit has to be read on the plan the placement
        would produce, not on what sits above the box at the moment it is placed.
        """
        boxes = [Box("tall", 80, 100, 50, 10), Box("top", 100, 100, 20, 30),
                 Box("victim", 20, 100, 50, 5)]
        limited = constraint_set(boxes, ("S1",),
                                 {"type": "max_weight_on", "item": "victim", "limit_kg": 10})
        plan = solve(boxes, CONTAINER, limited)
        self.assertEqual(plan.loading_order, ["tall", "top"])
        self.assertEqual([b.id for b in plan.unplaced], ["victim"])
        self.assertEqual(find_problems(plan.placements, CONTAINER,
                                       max_weight_on={"victim": 10}), [])

    def test_the_gap_is_filled_when_nothing_limits_the_box(self):
        """The same load without the limit: `victim` fits in the gap, and ends up under `top`."""
        boxes = [Box("tall", 80, 100, 50, 10), Box("top", 100, 100, 20, 30),
                 Box("victim", 20, 100, 50, 5)]
        plan = solve(boxes, CONTAINER)
        self.assertEqual(plan.loading_order, ["tall", "top", "victim"])

    def test_random_loads_are_always_valid(self):
        import random
        rng = random.Random(42)
        for _ in range(50):
            boxes = [Box(f"b{i}", rng.randint(5, 60), rng.randint(5, 60), rng.randint(5, 60),
                         rng.randint(1, 30)) for i in range(25)]
            plan = solve(boxes, CONTAINER)
            self.assertEqual(find_problems(plan.placements, CONTAINER), [])

    def test_random_constrained_loads_are_always_valid(self):
        """The same sweep with a route, last groups and stack limits: the plans still hold up
        under the independent check, which is how the slide-under case above was found."""
        import random
        rng = random.Random(7)
        stops = ("S1", "S2", "S3")
        for _ in range(50):
            boxes = [Box(f"b{i}", rng.randint(5, 60), rng.randint(5, 60), rng.randint(5, 60),
                         rng.randint(1, 30)) for i in range(25)]
            stated = [{"type": "unload_at", "item": b.id, "stop": rng.choice(stops)} for b in boxes]
            stated += [{"type": "load_last", "item": b.id} for b in boxes if rng.random() < 0.3]
            stated += [{"type": "max_weight_on", "item": b.id, "limit_kg": rng.randint(1, 60)}
                       for b in boxes if rng.random() < 0.3]
            route = constraint_set(boxes, stops, *stated)
            limits = {c["item"]: c["limit_kg"] for c in route.of_type("max_weight_on")}
            plan = solve(boxes, CONTAINER, route)
            self.assertEqual(find_problems(plan.placements, CONTAINER, max_weight_on=limits), [])


class TestLoadingOrder(unittest.TestCase):
    """The route drives the loading sequence: the last stop is loaded first, and `load_last` only
    orders items inside one stop (contract, *Route and unloading order*)."""

    def test_the_last_stop_is_loaded_first(self):
        boxes = [crate("a", 40), crate("b", 30), crate("c", 20)]
        route = constraint_set(boxes, ("S1", "S2", "S3"),
                               {"type": "unload_at", "item": "a", "stop": "S1"},
                               {"type": "unload_at", "item": "b", "stop": "S2"},
                               {"type": "unload_at", "item": "c", "stop": "S3"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["c", "b", "a"])

    def test_without_a_route_the_biggest_still_goes_in_first(self):
        """The same three boxes, so it is the route that reverses them, not their size."""
        boxes = [crate("a", 40), crate("b", 30), crate("c", 20)]
        self.assertEqual(solve(boxes, CONTAINER).loading_order, ["a", "b", "c"])

    def test_an_item_with_no_stop_travels_to_the_last_one(self):
        """`t` has no `unload_at`, so it comes off at `S3` and is loaded before anything for S1."""
        boxes = [crate("t", 30), crate("u", 40)]
        route = constraint_set(boxes, ("S1", "S2", "S3"),
                               {"type": "unload_at", "item": "u", "stop": "S1"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["t", "u"])

    def test_load_last_orders_items_inside_a_stop(self):
        boxes = [crate("p", 40), crate("q", 30)]
        route = constraint_set(boxes, ("S1",), {"type": "load_last", "item": "p"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["q", "p"])

    def test_the_stop_order_wins_when_the_two_disagree(self):
        """`m` is loaded last at `S3`, but everything for `S1` is loaded after the whole of `S3`."""
        boxes = [crate("m", 20), crate("n", 40)]
        route = constraint_set(boxes, ("S1", "S2"),
                               {"type": "load_last", "item": "m"},
                               {"type": "unload_at", "item": "n", "stop": "S1"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["m", "n"])

    def test_several_items_loaded_last_at_one_stop_form_the_last_group(self):
        """p and q are the last group at S1: r goes in before both, and the solver orders them."""
        boxes = [crate("p", 40), crate("q", 30), crate("r", 20)]
        route = constraint_set(boxes, ("S1",),
                               {"type": "load_last", "item": "p"},
                               {"type": "load_last", "item": "q"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["r", "p", "q"])

    def test_a_last_group_covering_the_whole_stop_orders_nothing(self):
        """Every item at S1 is loaded last, which says nothing: the order must not be inverted."""
        boxes = [crate("p", 40), crate("q", 30)]
        route = constraint_set(boxes, ("S1",),
                               {"type": "load_last", "item": "p"},
                               {"type": "load_last", "item": "q"})
        plan = solve(boxes, CONTAINER, route)
        self.assertEqual(plan.loading_order, solve(boxes, CONTAINER).loading_order)
        self.assertEqual(plan.loading_order, ["p", "q"])

    def test_a_whole_last_group_still_loses_to_the_stop_order(self):
        """The no-op is inside the stop only: S2 is still loaded before S1."""
        boxes = [crate("p", 40), crate("q", 30), crate("z", 20)]
        route = constraint_set(boxes, ("S1", "S2"),
                               {"type": "unload_at", "item": "p", "stop": "S1"},
                               {"type": "unload_at", "item": "q", "stop": "S1"},
                               {"type": "load_last", "item": "p"},
                               {"type": "load_last", "item": "q"})
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["z", "p", "q"])

    def test_a_constraint_the_solver_cannot_honour_is_refused(self):
        """Dropping it would hand back a plan the independent check calls valid (issue #29)."""
        boxes = [crate("a", 40), crate("b", 30)]
        # `on_top` left this list in `SA-19`, which is the whole point of that change. Four remain.
        for kind, extra in (("not_stackable", {}), ("at_bottom", {}),
                            ("keep_upright", {}), ("max_stack_height", {"limit_cm": 10})):
            with self.subTest(kind):
                route = constraint_set(boxes, ("S1",), {"type": kind, "item": "a", **extra})
                with self.assertRaises(UnsupportedConstraint) as refused:
                    solve(boxes, CONTAINER, route)
                self.assertIn(kind, str(refused.exception))

    def test_the_ones_it_does_honour_are_not_refused(self):
        boxes = [crate("a", 40), crate("b", 30)]
        route = constraint_set(boxes, ("S1", "S2"),
                               {"type": "unload_at", "item": "a", "stop": "S1"},
                               {"type": "load_last", "item": "b"},
                               {"type": "max_weight_on", "item": "a", "limit_kg": 50},
                               {"type": "max_total_weight", "limit_kg": 400})
        self.assertEqual(unhandled(route), [])
        self.assertEqual(solve(boxes, CONTAINER, route).loading_order, ["b", "a"])

    def test_every_contract_type_is_either_honoured_or_refused(self):
        """No type may fall between the two: that is how the five were being dropped."""
        from quai.constraints import CONSTRAINT_FIELDS
        from quai.solver import HONOURED

        self.assertTrue(HONOURED <= set(CONSTRAINT_FIELDS))
        for kind in CONSTRAINT_FIELDS:
            with self.subTest(kind):
                fields = CONSTRAINT_FIELDS[kind]
                constraint = {"type": kind}
                if "item" in fields:
                    constraint["item"] = "a"
                if "stop" in fields:
                    constraint["stop"] = "S1"
                if "limit_cm" in fields:
                    constraint["limit_cm"] = 10
                if "limit_kg" in fields:
                    constraint["limit_kg"] = 50
                boxes = [crate("a", 40)]
                route = constraint_set(boxes, ("S1",), constraint)
                if kind in HONOURED:
                    self.assertEqual(unhandled(route), [])
                else:
                    self.assertEqual(unhandled(route), [kind])

    def test_a_box_outside_the_manifest_is_refused(self):
        """The constraints were validated against a manifest; a box outside it has no stop."""
        boxes = [crate("a", 40)]
        route = constraint_set(boxes, ("S1",), {"type": "load_last", "item": "a"})
        with self.assertRaises(ValueError):
            solve(boxes + [crate("stowaway", 20)], CONTAINER, route)


class TestTheDemoLoad(unittest.TestCase):
    """What ordering by the route costs the greedy first fit, pinned so it is reproducible.

    `documentation/roadmap.md` records the drop under the first-fit limitation. MORHI11 pointed out
    on #27 that the number came from a split nothing in the repository wrote down — and that other
    splits of the same boxes go lower — so the split lives here, next to the figure it produces.
    """

    def route(self, boxes, stops=("S1", "S2", "S3")):
        """The demo boxes dealt round-robin across the stops, in manifest order."""
        stated = [{"type": "unload_at", "item": b.id, "stop": stops[i % len(stops)]}
                  for i, b in enumerate(boxes)]
        return constraint_set(boxes, stops, *stated)

    def test_the_demo_load_without_a_route(self):
        from demo import BOXES, VAN
        plan = solve(BOXES, VAN)
        self.assertEqual(len(plan.placements), 10)
        self.assertEqual(round(plan.fill_rate, 2), 0.39)

    def test_the_same_load_dealt_round_robin_over_three_stops(self):
        """21 %, against 39 % unrouted: size no longer decides what goes in first."""
        from demo import BOXES, VAN
        plan = solve(BOXES, VAN, self.route(BOXES))
        self.assertEqual(len(plan.placements), 9)
        self.assertEqual(round(plan.fill_rate, 2), 0.21)
        self.assertEqual(sorted(b.id for b in plan.unplaced), ["fridge", "sofa"])


if __name__ == "__main__":
    unittest.main()


class TestNothingAboveIsGeometric(unittest.TestCase):
    """`covering` reads the column, not the contact graph (`SA-19`).

    This is the one design decision inside `on_top`, so it is pinned rather than assumed: a box held
    up by a taller neighbour can hang over another box without resting on it, and an operator saying
    "nothing on top of this" means that box too.
    """

    def setUp(self):
        short = Placement(Box("short", 50, 100, 20), 0, 0, 0, 50, 100, 20)
        tall = Placement(Box("tall", 50, 100, 40), 50, 0, 0, 50, 100, 40)
        # Resting on `tall` (50 of its 60 cm of base, so 83% — supported), and overhanging `short`
        # by 10 cm without touching it: `short` ends at z=20, this starts at z=40.
        over = Placement(Box("over", 60, 100, 20), 40, 0, 40, 60, 100, 20)
        self.plan = [short, tall, over]
        self.short, self.over = short, over

    def test_an_overhang_counts_as_being_above(self):
        self.assertEqual([p.box.id for p in checks.covering(self.short, self.plan)], ["over"])

    def test_the_contact_graph_alone_would_have_missed_it(self):
        # Why `max_weight_on` and `on_top` cannot share one predicate: weight travels through contact,
        # and this box's weight does not reach `short`, but it is still over it.
        self.assertNotIn("short", [p.box.id for p in checks.stack_below(self.over, self.plan)])
        self.assertEqual(checks.weight_above(self.short, self.plan), 0)

    def test_the_checks_call_that_plan_invalid_when_short_must_stay_clear(self):
        problems = find_problems(self.plan, Container(100, 100, 100), must_be_clear={"short"})
        self.assertEqual(len(problems), 1)
        self.assertIn("short must stay clear", problems[0])
        self.assertIn("over", problems[0])

    def test_a_box_that_must_stay_clear_with_an_empty_column_is_valid(self):
        self.assertEqual(find_problems(self.plan, Container(100, 100, 100),
                                       must_be_clear={"over"}), [])


class TestOnTop(unittest.TestCase):
    """`on_top`, honoured by placing the box last so nothing can land on it (`SA-19`)."""

    def stack(self):
        # Each crate fills the floor, so the only place for the next one is on top of the last.
        return [crate("a", 40), crate("b", 30), crate("c", 20)]

    def test_without_the_constraint_the_biggest_box_is_buried(self):
        # The baseline the constraint has to change: largest-first puts `a` on the floor, and the
        # other two end up over it.
        plan = solve(self.stack(), CONTAINER)
        self.assertEqual(plan.loading_order, ["a", "b", "c"])
        placed = {p.box.id: p for p in plan.placements}
        self.assertEqual(sorted(o.box.id for o in checks.covering(placed["a"], plan.placements)),
                         ["b", "c"])

    def test_on_top_moves_it_to_the_end_of_the_load_and_clears_its_column(self):
        boxes = self.stack()
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "a"})
        plan = solve(boxes, CONTAINER, route)
        self.assertEqual(plan.loading_order[-1], "a", "it has to be loaded last")
        placed = {p.box.id: p for p in plan.placements}
        self.assertEqual(checks.covering(placed["a"], plan.placements), [])
        self.assertGreater(placed["a"].z, 0, "and it ends up on top of the others, not beside them")

    def test_nothing_is_attempted_after_it_which_is_why_the_property_holds(self):
        # The argument this change rests on, asserted directly on the order the solver walks: every
        # box that must stay clear is at the end of it, so no later placement exists that could land
        # on one. Asserted on the attempted order, not `plan.loading_order`, which lists only the
        # boxes that found room — a box left unplaced would otherwise hide the property.
        boxes = self.stack() + [crate("d", 10)]
        clear = {"a", "c"}
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "a"},
                               {"type": "on_top", "item": "c"})
        attempted = solver_module.last(solver_module.loading_order(boxes, route), clear)
        self.assertEqual([box.id for box in attempted][-2:], ["a", "c"])
        plan = solve(boxes, CONTAINER, route)
        for placed in plan.placements:
            if placed.box.id in clear:
                with self.subTest(placed.box.id):
                    self.assertEqual(checks.covering(placed, plan.placements), [])

    def test_two_boxes_that_must_stay_clear_do_not_bury_each_other(self):
        # The case ordering alone does not solve: the second one placed could land on the first. Half
        # the floor each, so there is genuinely room for both to be clear side by side — with
        # full-floor crates one of them would simply be unplaced and this would assert nothing.
        boxes = [half("big", 40), half("x", 30), half("a", 20), half("b", 20)]
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "a"},
                               {"type": "on_top", "item": "b"})
        plan = solve(boxes, CONTAINER, route)
        self.assertEqual(len(plan.placements), 4, "all four should fit; otherwise this proves little")
        self.assertEqual(find_problems(plan.placements, CONTAINER,
                                       must_be_clear={"a", "b"}), [])

    def test_the_independent_checks_agree_with_the_plan_the_solver_built(self):
        boxes = self.stack()
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "a"})
        plan = solve(boxes, CONTAINER, route)
        self.assertEqual(find_problems(plan.placements, CONTAINER, must_be_clear={"a"}), [])

    def test_a_box_with_nowhere_clear_to_go_is_unplaced_rather_than_forced(self):
        # Three crates exactly fill the height, so the last one can only go where it would be buried
        # or not at all. Reported, never forced in — the rule the whole solver follows.
        boxes = [crate("a", 40), crate("b", 40), crate("c", 40)]
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "c"})
        plan = solve(boxes, CONTAINER, route)
        self.assertIn("c", [box.id for box in plan.unplaced])
        self.assertEqual(find_problems(plan.placements, CONTAINER, must_be_clear={"c"}), [])

    def test_the_same_input_still_gives_the_same_plan(self):
        boxes = self.stack()
        route = constraint_set(boxes, ("S1",), {"type": "on_top", "item": "a"})
        first, second = solve(boxes, CONTAINER, route), solve(boxes, CONTAINER, route)
        self.assertEqual([(p.box.id, p.x, p.y, p.z) for p in first.placements],
                         [(p.box.id, p.x, p.y, p.z) for p in second.placements])

    def test_it_overrides_the_route_for_that_box_and_only_that_box(self):
        # Stated out loud because it is the cost of this design: `load_last` sits below the stop in
        # the order and can never cross it, but `on_top` has to, since being clear is a property of
        # the finished plan. The other boxes keep their route order.
        boxes = [crate("early", 40), crate("late", 30), crate("other", 20)]
        route = constraint_set(boxes, ("S1", "S2"),
                               {"type": "unload_at", "item": "early", "stop": "S1"},
                               {"type": "unload_at", "item": "late", "stop": "S2"},
                               {"type": "unload_at", "item": "other", "stop": "S2"},
                               {"type": "on_top", "item": "late"})
        plan = solve(boxes, CONTAINER, route)
        # `late` is for the last stop, so the route alone would load it first; `on_top` sends it last.
        self.assertEqual(plan.loading_order[-1], "late")
        self.assertLess(plan.loading_order.index("other"), plan.loading_order.index("early"),
                        "the boxes without on_top keep the order the route gave them")
