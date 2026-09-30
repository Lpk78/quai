"""Check the readings the evaluation script takes from the rubric document.

`tests/test_evaluation_inputs.py` checks that the document agrees with itself. This file checks
the other half: that what `quai.rubric` reads out of it is what the document says — the sentence
the operator speaks, the route in order, and the criteria a version is scored on.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quai import rubric  # noqa: E402


class TestCases(unittest.TestCase):
    def setUp(self):
        self.text = rubric.read_doc()
        self.cases = rubric.cases(self.text)

    def test_every_sentence_is_read_with_its_expected_output(self):
        self.assertEqual(len(self.cases), rubric.EXPECTED_SENTENCES)
        self.assertEqual([case.id for case in self.cases],
                         [f"T{n:02d}" for n in range(1, rubric.EXPECTED_SENTENCES + 1)])

    def test_the_sentence_is_one_line_of_speech(self):
        """The regex reads the JSON block with DOTALL; the sentence must not swallow the rest."""
        for case in self.cases:
            with self.subTest(case.id):
                self.assertNotIn("\n", case.sentence)
                self.assertTrue(case.sentence.strip())
                self.assertNotIn("```", case.sentence)

    def test_a_known_sentence_is_read_exactly(self):
        first = self.cases[0]
        self.assertEqual(first.sentence, "Don't put anything on top of the washing machine.")
        self.assertEqual(first.expected,
                         {"constraints": [{"type": "not_stackable", "item": "B1"}],
                          "unresolved": []})

    def test_cases_and_sentences_agree(self):
        self.assertEqual(rubric.sentences(self.text),
                         [(case.id, case.expected) for case in self.cases])


class TestManifestAndRoute(unittest.TestCase):
    def setUp(self):
        self.text = rubric.read_doc()

    def test_the_route_is_read_in_order(self):
        route = rubric.route(self.text)
        self.assertEqual(route, ("S1", "S2", "S3"))
        self.assertEqual(set(route), rubric.stop_ids(self.text))

    def test_the_last_stop_of_the_route_is_the_documented_one(self):
        self.assertEqual(rubric.manifest(self.text).last_stop, "S3")

    def test_every_stop_is_named_for_the_operator(self):
        """The operator says "Le Havre", not "S2" — the names have to reach the model."""
        names = rubric.stop_names(self.text)
        self.assertEqual(set(names), rubric.stop_ids(self.text))
        self.assertEqual(names["S2"], "Le Havre")

    def test_the_manifest_holds_every_item_of_the_document(self):
        manifest = rubric.manifest(self.text)
        self.assertEqual(set(manifest.items), rubric.manifest_ids(self.text))
        self.assertEqual(len(manifest.items), 10)

    def test_items_are_read_with_their_label_and_figures(self):
        items = {item.id: item for item in rubric.items(self.text)}
        self.assertEqual(items["B1"].label, "washing machine")
        self.assertEqual(items["B1"].weight, "70")
        self.assertEqual(items["B3"].label, "pallet of tiles")
        for item in items.values():
            with self.subTest(item.id):
                self.assertTrue(item.dimensions.strip())


class TestCriteria(unittest.TestCase):
    def test_the_criteria_are_the_eight_of_the_rubric(self):
        self.assertEqual(rubric.criteria(rubric.read_doc()),
                         ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"))


if __name__ == "__main__":
    unittest.main()
