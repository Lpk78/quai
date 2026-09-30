"""Run from the repository root:  python3 -m unittest discover tests

Two things are checked here: that `src/quai/constraints.py` says the same thing as the contract in
`documentation/prompt_evaluation.md`, and that its validation accepts what the contract calls valid
and rejects everything else.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))  # so the document parsers can be reused, whichever way tests are run

from quai.constraints import (  # noqa: E402
    CONSTRAINT_FIELDS, LIMIT_FIELDS, REASONS, ConstraintSet, Manifest)
from test_evaluation_inputs import constraint_fields, read_doc, reasons  # noqa: E402

# A small manifest for the unit tests. The document's own manifest is used where the point is to
# check the module against the contract.
MANIFEST = Manifest(items=("B1", "B2", "B3"), stops=("S1", "S2", "S3"))


class TestContractIsInStep(unittest.TestCase):
    """The prose contract and this module are two copies of one agreement; they must not drift."""

    def setUp(self):
        self.text = read_doc()

    def test_the_nine_types_and_their_fields_match_the_document(self):
        self.assertEqual(CONSTRAINT_FIELDS,
                         {name: frozenset(fields)
                          for name, fields in constraint_fields(self.text).items()})

    def test_the_six_reasons_match_the_document(self):
        self.assertEqual(REASONS, frozenset(reasons(self.text)))

    def test_every_declared_limit_field_is_used_by_some_type(self):
        used = frozenset().union(*CONSTRAINT_FIELDS.values())
        self.assertEqual(LIMIT_FIELDS, LIMIT_FIELDS & used)


class TestManifest(unittest.TestCase):
    def test_last_stop_is_the_end_of_the_route(self):
        self.assertEqual(MANIFEST.last_stop, "S3")

    def test_a_manifest_needs_a_route(self):
        with self.assertRaises(ValueError):
            Manifest(items=("B1",), stops=())

    def test_repeated_ids_are_rejected(self):
        for field in ("items", "stops"):
            with self.subTest(field):
                with self.assertRaises(ValueError):
                    Manifest(**{"items": ("B1", "B2"), "stops": ("S1", "S2"), field: ("X", "X")})

    def test_a_manifest_can_be_built_from_the_boxes_of_a_load(self):
        from quai.models import Box
        boxes = [Box("B1", 60, 60, 85, 70), Box("B2", 120, 15, 70, 18)]
        self.assertEqual(Manifest.from_boxes(boxes, ["S1", "S2"]).items, ("B1", "B2"))


class TestReadingAConstraintSet(unittest.TestCase):
    def setUp(self):
        self.set = ConstraintSet(MANIFEST, constraints=(
            {"type": "at_bottom", "item": "B3"},
            {"type": "not_stackable", "item": "B3"},
            {"type": "unload_at", "item": "B1", "stop": "S1"},
            {"type": "max_weight_on", "item": "B2", "limit_kg": 20},
            {"type": "max_total_weight", "limit_kg": 1500},
        ))

    def test_items_are_listed_by_constraint_type(self):
        self.assertEqual(self.set.items_with("at_bottom"), ("B3",))
        self.assertEqual(self.set.items_with("on_top"), ())

    def test_limits_are_read_per_item(self):
        self.assertEqual(self.set.limit("max_weight_on", "B2"), 20)
        self.assertIsNone(self.set.limit("max_weight_on", "B1"))

    def test_the_total_weight_limit_is_read_without_an_item(self):
        self.assertEqual(self.set.limit("max_total_weight"), 1500)

    def test_a_stated_unload_stop_is_used(self):
        self.assertEqual(self.set.unload_stop("B1"), "S1")

    def test_an_item_with_no_unload_at_comes_off_at_the_last_stop(self):
        """A missing `unload_at` means the item travels the whole route, not that data is missing."""
        self.assertEqual(self.set.unload_stop("B2"), "S3")

    def test_the_unloading_plan_covers_the_whole_manifest(self):
        self.assertEqual(self.set.unloading_plan(), {"B1": "S1", "B2": "S3", "B3": "S3"})

    def test_asking_about_an_item_outside_the_manifest_is_an_error(self):
        """Silently answering "the last stop" for an unknown item would hide a bug."""
        with self.assertRaises(KeyError):
            self.set.unload_stop("B9")


if __name__ == "__main__":
    unittest.main()
