"""Check the command line: what it runs, and what it refuses to print.

The rule under test is the one from `documentation/prompt_evaluation.md` and `CLAUDE.md`: a score
is only ever printed for a run that happened over all 25 sentences.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import evaluate_prompt  # noqa: E402
from quai import evaluation, llm, rubric  # noqa: E402

TEXT = rubric.read_doc()
CASES = rubric.cases(TEXT)


class TestChoosingCases(unittest.TestCase):
    def test_no_selection_runs_every_sentence(self):
        cases, partial = evaluate_prompt.chosen_cases(CASES, "")
        self.assertEqual(len(cases), rubric.EXPECTED_SENTENCES)
        self.assertFalse(partial)

    def test_a_selection_is_marked_partial_and_keeps_the_given_order(self):
        cases, partial = evaluate_prompt.chosen_cases(CASES, "T25, T01")
        self.assertEqual([c.id for c in cases], ["T25", "T01"])
        self.assertTrue(partial)

    def test_an_unknown_case_id_stops_the_run(self):
        with self.assertRaises(SystemExit):
            evaluate_prompt.chosen_cases(CASES, "T99")


class TestRefusingToPrintAScore(unittest.TestCase):
    def a_prompt_file(self) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "v0_test.md"
        path.write_text("Translate the sentence.", encoding="utf-8")
        return path

    def test_a_missing_prompt_file_is_reported(self):
        self.assertEqual(evaluate_prompt.main([str(Path("no", "such", "prompt.md"))]), 2)

    def test_no_key_prints_no_scores(self):
        missing = llm.MissingKey("ANTHROPIC_API_KEY is not set in .env")
        with mock.patch.object(evaluate_prompt.llm, "from_env", side_effect=missing):
            with mock.patch("sys.stdout") as out:
                code = evaluate_prompt.main([str(self.a_prompt_file())])
        self.assertEqual(code, 1)
        printed = "".join(str(call) for call in out.write.call_args_list)
        self.assertNotIn("Row for the Results table", printed)


class TestTheTranscript(unittest.TestCase):
    def test_every_reply_is_kept_with_the_verdicts(self):
        """A score must be re-readable later without calling the model again."""
        scored = (evaluation.Scored("T01", {name: True for name in evaluation.CHECKS},
                                   (), True, '{"constraints": [], "unresolved": []}'),)
        run = evaluation.Run("v0_test", "test-model", scored, expected_cases=1)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = evaluate_prompt.write_transcript(run, Path(folder.name))
        kept = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(kept["version"], "v0_test")
        self.assertEqual(kept["model"], "test-model")
        self.assertEqual(kept["temperature"], "n/a")
        self.assertTrue(kept["complete"])
        self.assertEqual(kept["cases"][0]["id"], "T01")
        self.assertEqual(kept["cases"][0]["output"], '{"constraints": [], "unresolved": []}')


if __name__ == "__main__":
    unittest.main()
