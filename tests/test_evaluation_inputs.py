"""Check that the constraint-translation test inputs stay consistent with their own contract.

The expected JSON in `documentation/prompt_evaluation.md` is what every prompt version is scored
against, so a typo there silently corrupts every score. These tests read the document and check it
against the manifest and output contract declared in the same file.

The readers themselves live in `src/quai/rubric.py`, because the evaluation script (LP-06) scores
prompt versions from the same document: one reading of the document, used by the tests that guard
it and by the script that runs on it. They are re-exported here so that a test module importing
them from this file keeps working.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from quai.rubric import (  # noqa: E402
    DOC, EXPECTED_SENTENCES, constraint_fields, manifest_ids, read_doc, reasons, sentences,
    stop_ids, table_rows)

__all__ = ["DOC", "EXPECTED_SENTENCES", "constraint_fields", "manifest_ids", "read_doc", "reasons",
           "sentences", "stop_ids", "table_rows"]


class TestEvaluationInputs(unittest.TestCase):
    def setUp(self):
        self.text = read_doc()
        self.items = manifest_ids(self.text)
        self.stops = stop_ids(self.text)
        self.constraints = constraint_fields(self.text)
        self.reasons = reasons(self.text)

    def test_every_expected_output_is_valid_json(self):
        # json.loads in sentences() raises if not; this pins the count too.
        self.assertEqual(len(sentences(self.text)), EXPECTED_SENTENCES)

    def test_sentences_are_numbered_without_gaps(self):
        ids = [tid for tid, _ in sentences(self.text)]
        self.assertEqual(ids, [f"T{n:02d}" for n in range(1, EXPECTED_SENTENCES + 1)])

    def test_every_output_has_both_keys_and_nothing_else(self):
        for tid, out in sentences(self.text):
            with self.subTest(tid):
                self.assertEqual(set(out), {"constraints", "unresolved"})

    def test_constraints_use_declared_types_and_fields(self):
        for tid, out in sentences(self.text):
            for c in out["constraints"]:
                with self.subTest(tid, type=c.get("type")):
                    self.assertIn(c["type"], self.constraints)
                    self.assertEqual(set(c) - {"type"}, self.constraints[c["type"]])

    def test_contract_table_is_not_polluted_by_other_tables(self):
        """Manifest rows have the same shape as contract rows and must not be read as types."""
        self.assertFalse(self.items & set(self.constraints))
        self.assertFalse(self.stops & set(self.constraints))
        for name, fields in self.constraints.items():
            with self.subTest(name):
                self.assertTrue(fields, f"{name} was parsed with no fields")

    def test_constraints_only_reference_manifest_items_and_stops(self):
        for tid, out in sentences(self.text):
            for c in out["constraints"]:
                with self.subTest(tid):
                    if "item" in c:
                        self.assertIn(c["item"], self.items)
                    if "stop" in c:
                        self.assertIn(c["stop"], self.stops)

    def test_unresolved_entries_are_well_formed(self):
        for tid, out in sentences(self.text):
            for u in out["unresolved"]:
                with self.subTest(tid):
                    self.assertEqual(set(u), {"text", "reason", "question"})
                    self.assertIn(u["reason"], self.reasons)
                    self.assertTrue(u["text"].strip())

    def test_every_sentence_produces_something(self):
        """An empty constraints list must be explained by an unresolved entry."""
        for tid, out in sentences(self.text):
            with self.subTest(tid):
                self.assertTrue(out["constraints"] or out["unresolved"])

    def test_required_categories_are_covered(self):
        used = {u["reason"] for _, out in sentences(self.text) for u in out["unresolved"]}
        for required in ("ambiguous", "unknown_item", "injection_attempt"):
            with self.subTest(required):
                self.assertIn(required, used)

    def test_exactly_one_injection_attempt(self):
        count = sum(1 for _, out in sentences(self.text)
                    for u in out["unresolved"] if u["reason"] == "injection_attempt")
        self.assertEqual(count, 1)

    def test_injection_case_still_keeps_the_real_constraint(self):
        """The attack must be refused without losing what the operator actually asked for."""
        for tid, out in sentences(self.text):
            if any(u["reason"] == "injection_attempt" for u in out["unresolved"]):
                with self.subTest(tid):
                    self.assertTrue(out["constraints"],
                                    "the injection sentence must keep its legitimate constraint")


if __name__ == "__main__":
    unittest.main()
