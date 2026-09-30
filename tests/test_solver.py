"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quai import checks, solver as solver_module  # noqa: E402
from quai.checks import find_problems, overlaps  # noqa: E402
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
