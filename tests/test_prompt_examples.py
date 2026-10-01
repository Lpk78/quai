"""Check that no prompt version teaches itself the answers to the sentences it is scored on.

A few-shot version carries worked examples inside its prompt. If one of those were a test sentence,
or a close paraphrase of one, the version would be scored on inputs it had been shown — and its row
in the results table would not mean what every other row means.

The guard is mechanical rather than a promise, because the promise is the kind that holds until
someone adds a fifth example in a hurry.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import evaluate_prompt  # noqa: E402
from quai import rubric  # noqa: E402

FAMILIES = ROOT / "prompts"

# Each worked example states its sentence on a line of its own, so they can be found without parsing
# the prose around them.
OPERATOR_LINE = re.compile(r"^Operator:\s*(.+)$", re.M)

# Two sentences sharing more than this fraction of their words are close enough to be a paraphrase.
# The four examples in v4 peak at 0.29 against the 26, so this leaves real headroom; it is set to
# catch a future example written carelessly, not to police wording.
PARAPHRASE = 0.5


def words(sentence: str) -> set:
    return set(re.findall(r"[a-z]+", sentence.lower()))


def overlap(one: str, other: str) -> float:
    a, b = words(one), words(other)
    return len(a & b) / len(a | b) if a | b else 0.0


def version_files():
    for family in sorted(FAMILIES.iterdir()):
        if family.is_dir() and family.name != "dev":
            yield from sorted(family.glob("*.md"))


class TestExamplesAreNotTestSentences(unittest.TestCase):
    TEST_SENTENCES = [case.sentence for case in rubric.cases(rubric.read_doc())]

    def examples_in(self, path: Path):
        return OPERATOR_LINE.findall(evaluate_prompt.prompt_text(path))

    def test_some_version_really_does_carry_examples(self):
        """Otherwise the checks below would pass by finding nothing, which is the usual way.

        It asserts that examples exist somewhere, not how many a given version has: v4 carries four
        and v5 carries three, because v5 drops the two of v4's that measurably changed nothing. A
        count pinned to one file makes dropping an example that did not work into a test failure,
        which is the wrong incentive for a family whose whole point is that versions differ.
        """
        carriers = [p for p in version_files() if self.examples_in(p)]
        self.assertTrue(carriers, "no version file carries a worked example; the checks below "
                                  "would pass vacuously")
        for path in carriers:
            with self.subTest(path.name):
                self.assertGreaterEqual(len(self.examples_in(path)), 1)

    def test_no_example_is_a_test_sentence(self):
        def bare(sentence):
            return re.sub(r"[^a-z0-9 ]", "", sentence.lower()).strip()

        scored = {bare(s) for s in self.TEST_SENTENCES}
        for path in version_files():
            for example in self.examples_in(path):
                with self.subTest(f"{path.name}: {example[:40]}"):
                    self.assertNotIn(bare(example), scored)

    def test_no_example_is_a_close_paraphrase_of_one(self):
        for path in version_files():
            for example in self.examples_in(path):
                worst = max(self.TEST_SENTENCES, key=lambda s: overlap(example, s))
                with self.subTest(f"{path.name}: {example[:40]}"):
                    self.assertLess(
                        overlap(example, worst), PARAPHRASE,
                        f"too close to {worst!r} — a version must not be shown the sentences it is "
                        "scored on")

    def test_the_examples_use_items_that_are_not_in_the_manifest(self):
        """`A1`–`A6` exist only in the examples. A `B` id would bind a lesson to a real item."""
        real = set(rubric.manifest(rubric.read_doc()).items)
        for path in version_files():
            for example in self.examples_in(path):
                for item in re.findall(r"\bB\d+\b", example):
                    with self.subTest(f"{path.name}: {item}"):
                        self.assertNotIn(item, real)


class TestTheCheckWouldNotice(unittest.TestCase):
    """The guard above is only worth having if it fails on the thing it is meant to catch."""

    def test_a_test_sentence_used_as_an_example_is_caught(self):
        sentence = rubric.cases(rubric.read_doc())[0].sentence
        bare = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).strip()  # noqa: E731
        self.assertEqual(bare(sentence), bare(sentence))
        self.assertGreaterEqual(overlap(sentence, sentence), PARAPHRASE)

    def test_a_reworded_test_sentence_is_still_caught(self):
        # T01 with two words changed is exactly the case the exact-match check would miss.
        self.assertGreaterEqual(
            overlap("Don't put anything on top of the washing machine.",
                    "Do not put anything on top of the washing machine"),
            PARAPHRASE)


if __name__ == "__main__":
    unittest.main()
