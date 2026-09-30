"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quai import checks, solver as solver_module  # noqa: E402
from quai.checks import find_problems, overlaps, weight_above  # noqa: E402
from quai.models import Box, Container, Placement  # noqa: E402
from quai.solver import solve  # noqa: E402

CONTAINER = Container(100, 100, 100, max_weight=500)


def cubes(n: int, size: int = 50, weight: float = 10) -> list[Box]:
    return [Box(f"c{i}", size, size, size, weight) for i in range(n)]


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

    def test_random_loads_are_always_valid(self):
        import random
        rng = random.Random(42)
        for _ in range(50):
            boxes = [Box(f"b{i}", rng.randint(5, 60), rng.randint(5, 60), rng.randint(5, 60),
                         rng.randint(1, 30)) for i in range(25)]
            plan = solve(boxes, CONTAINER)
            self.assertEqual(find_problems(plan.placements, CONTAINER), [])


if __name__ == "__main__":
    unittest.main()
