"""Check that the constraint-translation test inputs stay consistent with their own contract.

The expected JSON in `documentation/prompt_evaluation.md` is what every prompt version is scored
against, so a typo there silently corrupts every score. These tests read the document and check it
against the manifest and output contract declared in the same file.
"""

import json
import pathlib
import re
import unittest

DOC = pathlib.Path(__file__).resolve().parent.parent / "documentation" / "prompt_evaluation.md"

EXPECTED_SENTENCES = 25


def read_doc():
    return DOC.read_text(encoding="utf-8")


def manifest_ids(text):
    return set(re.findall(r"^\| `(B\d+)` \|", text, re.MULTILINE))


def stop_ids(text):
    line = re.search(r"^Stops on the route: (.+)$", text, re.MULTILINE).group(1)
    return set(re.findall(r"`(S\d+)`", line))


def constraint_fields(text):
    """Map constraint name -> required fields, from the contract table."""
    fields = {}
    for name, raw in re.findall(r"^\| `(\w+)` \| (.+?) \| .+? \|$", text, re.MULTILINE):
        if name in ("item", "text", "reason"):
            continue
        fields[name] = set(re.findall(r"`(\w+)`", raw))
    return fields


def reasons(text):
    block = text.split("| `reason` | Used when |")[1]
    return set(re.findall(r"^\| `(\w+)` \|", block, re.MULTILINE))


def sentences(text):
    """Return [(id, parsed_json)] for every test sentence."""
    body = text.split("## Test inputs")[1].split("## Results")[0]
    found = []
    for tid, block in re.findall(r"^\*\*(T\d+)\*\*.*?\n```json\n(.*?)\n```", body,
                                 re.MULTILINE | re.DOTALL):
        found.append((tid, json.loads(block)))
    return found


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
