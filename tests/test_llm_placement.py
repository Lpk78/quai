"""Run from the repository root:  python3 -m unittest discover tests

No network here. The scoring has to be trustworthy before it is pointed at twenty real replies, so
it is tested against replies written by hand — including the shapes a model actually produces.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quai import llm_placement  # noqa: E402
from quai.models import Box, Container  # noqa: E402

VAN = Container(100, 100, 100, max_weight=500)
BOXES = [Box("a", 50, 50, 50, 10), Box("b", 50, 50, 50, 10)]


def reply(*placements: dict) -> str:
    import json
    return json.dumps({"placements": list(placements)})


def at(box_id: str, x: int, y: int, z: int, d: int = 50) -> dict:
    return {"id": box_id, "x": x, "y": y, "z": z, "dx": d, "dy": d, "dz": d}


class TestReadingAReply(unittest.TestCase):
    def test_a_plain_object_is_read(self):
        placements, error = llm_placement.read_placements(reply(at("a", 0, 0, 0)), BOXES)
        self.assertIsNone(error)
        self.assertEqual([(p.box.id, p.x) for p in placements], [("a", 0)])

    def test_a_fenced_object_is_read(self):
        """The model fences almost everything; here that is not what is being measured."""
        fenced = f"```json\n{reply(at('a', 0, 0, 0))}\n```"
        placements, error = llm_placement.read_placements(fenced, BOXES)
        self.assertIsNone(error)
        self.assertEqual(len(placements), 1)

    def test_prose_around_a_fence_is_ignored(self):
        body = reply(at("a", 0, 0, 0))
        wrapped = f"Here is the plan:\n\n```json\n{body}\n```\n\nHope that helps."
        _, error = llm_placement.read_placements(wrapped, BOXES)
        self.assertIsNone(error)

    def test_text_that_is_not_json_is_reported(self):
        _, error = llm_placement.read_placements("I cannot do that.", BOXES)
        self.assertIn("not JSON", error)

    def test_a_missing_placements_list_is_reported(self):
        _, error = llm_placement.read_placements('{"boxes": []}', BOXES)
        self.assertIn("no 'placements' list", error)

    def test_a_missing_field_is_reported(self):
        _, error = llm_placement.read_placements('{"placements": [{"id": "a", "x": 0}]}', BOXES)
        self.assertIn("missing", error)

    def test_an_invented_box_is_reported_not_dropped(self):
        """A model inventing a box is a result, not noise to tidy away."""
        _, error = llm_placement.read_placements(reply(at("ghost", 0, 0, 0)), BOXES)
        self.assertIn("ghost", error)

    def test_a_fractional_coordinate_is_reported(self):
        _, error = llm_placement.read_placements(
            '{"placements": [{"id": "a", "x": "left", "y": 0, "z": 0,'
            ' "dx": 50, "dy": 50, "dz": 50}]}', BOXES)
        self.assertIn("whole number", error)


class TestScoring(unittest.TestCase):
    def test_a_correct_plan_has_no_problems(self):
        attempt = llm_placement.score(reply(at("a", 0, 0, 0), at("b", 50, 0, 0)), BOXES, VAN)
        self.assertTrue(attempt.valid)
        self.assertEqual(attempt.problems, ())

    def test_overlapping_boxes_are_caught(self):
        attempt = llm_placement.score(reply(at("a", 0, 0, 0), at("b", 10, 0, 0)), BOXES, VAN)
        self.assertFalse(attempt.valid)
        self.assertTrue(any("overlaps" in p for p in attempt.problems))

    def test_a_box_outside_the_container_is_caught(self):
        attempt = llm_placement.score(reply(at("a", 80, 0, 0), at("b", 0, 0, 0)), BOXES, VAN)
        self.assertTrue(any("outside" in p for p in attempt.problems))

    def test_a_floating_box_is_caught(self):
        attempt = llm_placement.score(reply(at("a", 0, 0, 0), at("b", 0, 0, 90)), BOXES, VAN)
        self.assertTrue(any("supported" in p for p in attempt.problems))

    def test_a_box_left_out_is_caught(self):
        attempt = llm_placement.score(reply(at("a", 0, 0, 0)), BOXES, VAN)
        self.assertIn("b was not placed", attempt.problems)

    def test_a_reply_that_does_not_parse_is_not_valid(self):
        attempt = llm_placement.score("sorry", BOXES, VAN)
        self.assertFalse(attempt.parsed)
        self.assertFalse(attempt.valid)
        self.assertEqual(attempt.placements, ())


class TestComparingRuns(unittest.TestCase):
    def test_the_same_plan_has_the_same_signature(self):
        one = llm_placement.score(reply(at("a", 0, 0, 0), at("b", 50, 0, 0)), BOXES, VAN)
        two = llm_placement.score(reply(at("b", 50, 0, 0), at("a", 0, 0, 0)), BOXES, VAN)
        self.assertEqual(one.signature, two.signature, "order of the list is not a difference")

    def test_a_different_position_is_a_different_signature(self):
        one = llm_placement.score(reply(at("a", 0, 0, 0)), BOXES, VAN)
        two = llm_placement.score(reply(at("a", 0, 0, 50)), BOXES, VAN)
        self.assertNotEqual(one.signature, two.signature)


class TestWhatTheModelIsTold(unittest.TestCase):
    def test_every_box_is_described(self):
        text = llm_placement.load_description(BOXES, VAN)
        for box in BOXES:
            self.assertIn(box.id, text)

    def test_the_container_is_described(self):
        text = llm_placement.load_description(BOXES, VAN)
        self.assertIn("100", text)
        self.assertIn("500 kg", text)

    def test_no_worked_example_is_given(self):
        """Showing a plan would measure copying rather than placing."""
        self.assertNotIn('"x":', llm_placement.SYSTEM_PROMPT.split("Axes")[1])


if __name__ == "__main__":
    unittest.main()
