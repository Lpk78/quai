"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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
