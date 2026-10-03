"""`prompts/README.md` against the prompts that are actually on disk.

That file is the entry point to the prompt work — it is what gets opened first to read what was
tried and what it scored. It had drifted badly enough to be describing a plan rather than the work:
it called the tree "planned", said "none of these version files exist yet" while five tested
versions sat beside it, and listed three filenames (`v2_structured_output`, `v3_few_shot`,
`v4_role_separation`) that have never existed. `HY-22` rewrote it; this is what stops it drifting
again, because prose has no other way of failing.

Run from the repository root:  python3 -m unittest discover tests
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
README = PROMPTS / "README.md"
FAMILY = PROMPTS / "constraint-translation"

TEXT = README.read_text(encoding="utf-8")

# iCloud leaves "v4_few_shot 2.md" beside the real file. Those copies are git-ignored (#69) but they
# are still on disk in a synced clone, so the comparison is against what git tracks in spirit: a
# version file is `vN_name.md` with no trailing " 2".
VERSION = re.compile(r"^v\d+_[a-z_]+\.md$")


def version_files() -> set[str]:
    return {p.name for p in FAMILY.iterdir() if VERSION.match(p.name)}


class TestEveryVersionOnDiskIsDocumented(unittest.TestCase):
    def test_the_readme_names_each_version_file_that_exists(self):
        for name in sorted(version_files()):
            with self.subTest(name):
                self.assertIn(name, TEXT,
                              f"{name} exists but prompts/README.md does not mention it")

    def test_the_readme_names_no_version_file_that_does_not_exist(self):
        """The failure that prompted `HY-22`: three invented filenames, none of them ever written."""
        on_disk = version_files()
        for named in sorted(set(re.findall(r"v\d+_[a-z_]+\.md", TEXT))):
            with self.subTest(named):
                self.assertIn(named, on_disk,
                              f"prompts/README.md names {named}, which is not in "
                              f"prompts/constraint-translation/ — rename one or the other")

    def test_there_are_five_of_them(self):
        # Pinned so that adding a sixth version forces this file to be looked at, rather than the
        # README quietly describing four-fifths of the work.
        self.assertEqual(len(version_files()), 5)


class TestItDoesNotPromiseWhatIsNotThere(unittest.TestCase):
    def test_no_family_folder_is_claimed_without_existing(self):
        """`llm-only-placement` was listed as a family beside `constraint-translation`.

        It has no folder — not on `main`, and not on `experiment/llm-only-placement` either, where
        the prompt is a constant in `src/quai/llm_placement.py`. Any `prompts/<name>/` path the
        README mentions has to be a directory that is really there.
        """
        for claimed in sorted(set(re.findall(r"`prompts/([a-z][a-z-]+)/`", TEXT))):
            with self.subTest(claimed):
                self.assertTrue((PROMPTS / claimed).is_dir(),
                                f"prompts/README.md points at prompts/{claimed}/, which does not exist")

    def test_it_no_longer_calls_the_tree_planned(self):
        # The specific sentence that was false, kept as a tripwire: if someone reintroduces the
        # "planned" framing while five tested versions sit on disk, that is the bug again.
        self.assertNotIn("none of these version files exist yet", TEXT)

    def test_the_unmerged_experiment_is_marked_as_unmerged(self):
        """Kept in the table, but it has to say where it actually is."""
        self.assertIn("llm-only-placement", TEXT)
        self.assertIn("pull/38", TEXT, "the experiment's row must link to the open PR it lives on")
        self.assertIn("src/quai/llm_placement.py", TEXT,
                      "the row must say where the prompt actually lives")


class TestTheScoresItQuotes(unittest.TestCase):
    """Every score in the README has to be the one `prompt_evaluation.md` recorded."""

    EVALUATION = (ROOT / "documentation" / "prompt_evaluation.md").read_text(encoding="utf-8")

    def test_each_quoted_score_appears_in_the_evaluation_table(self):
        # The README quotes `N/26` beside each version. The evaluation document is the source; a
        # figure here that is not there would be one invented for the summary.
        quoted = set(re.findall(r"(\d+)/26", TEXT))
        self.assertTrue(quoted, "the README should quote the scores it summarises")
        for score in sorted(quoted, key=int):
            with self.subTest(score=score):
                self.assertRegex(
                    self.EVALUATION, rf"\*?\*?{score}\*?\*?",
                    f"{score}/26 is quoted in prompts/README.md but not in prompt_evaluation.md")


if __name__ == "__main__":
    unittest.main()
