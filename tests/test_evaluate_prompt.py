"""Check the command line: what it runs, and what it refuses to print.

The rule under test is the one from `documentation/prompt_evaluation.md` and `CLAUDE.md`: a score
is only ever printed for a run that happened over all 26 sentences.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

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
    def a_run(self, runs=2):
        answer = '{"constraints": [], "unresolved": []}'
        attempt = evaluation.Scored("T01", {name: True for name in evaluation.CHECKS},
                                    (), True, answer)
        case = evaluation.CaseRuns("T01", (attempt,) * runs)
        return evaluation.Run("v0_test", "test-model", (case,), expected_cases=1, runs=runs), answer

    def test_every_reply_is_kept_with_the_verdicts(self):
        """A score must be re-readable later without calling the model again."""
        run, answer = self.a_run()
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = evaluate_prompt.write_transcript(run, Path(folder.name))
        kept = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(kept["version"], "v0_test")
        self.assertEqual(kept["model"], "test-model")
        self.assertEqual(kept["temperature"], "0")
        self.assertTrue(kept["complete"])
        self.assertEqual(kept["cases"][0]["id"], "T01")
        self.assertEqual(kept["cases"][0]["attempts"][0]["output"], answer)

    def test_every_run_of_every_sentence_is_kept(self):
        """Three runs mean three replies to keep, not one: the variability is the point."""
        run, answer = self.a_run(runs=3)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        kept = json.loads(evaluate_prompt.write_transcript(run, Path(folder.name))
                          .read_text(encoding="utf-8"))
        self.assertEqual(kept["runs_per_sentence"], 3)
        self.assertEqual(len(kept["cases"][0]["attempts"]), 3)
        self.assertEqual(kept["cases"][0]["passes"], 3)
        self.assertTrue(kept["cases"][0]["identical"])
        self.assertEqual([a["output"] for a in kept["cases"][0]["attempts"]], [answer] * 3)


if __name__ == "__main__":
    unittest.main()


class TestWhatIsSentAsThePrompt(unittest.TestCase):
    """A version file is a document around a prompt; only the prompt may reach the model."""

    def a_file(self, contents: str) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "v1_zero_shot.md"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_only_the_marked_section_is_sent(self):
        path = self.a_file("# Title\n\nTask prose.\n\n"
                           f"{evaluate_prompt.PROMPT_START}\nYou convert speech.\n"
                           f"{evaluate_prompt.PROMPT_END}\n\n## Change log\nT13 is the hard one.\n")
        self.assertEqual(evaluate_prompt.prompt_text(path), "You convert speech.")

    def test_the_change_log_never_reaches_the_model(self):
        """It names the sentences a version was written against — sending it would score a cheat."""
        path = self.a_file(f"{evaluate_prompt.PROMPT_START}\nPrompt.\n{evaluate_prompt.PROMPT_END}\n"
                           "## Known risks\nT15 and T17 carry two faults each.\n")
        sent = evaluate_prompt.prompt_text(path)
        for leak in ("Known risks", "T15", "T17"):
            with self.subTest(leak):
                self.assertNotIn(leak, sent)

    def test_a_file_without_markers_is_sent_whole(self):
        path = self.a_file("You convert speech.\n")
        self.assertEqual(evaluate_prompt.prompt_text(path), "You convert speech.\n")

    def test_an_unclosed_marker_stops_the_run(self):
        """Falling back to the whole file here would be exactly the leak the markers prevent."""
        path = self.a_file(f"{evaluate_prompt.PROMPT_START}\nPrompt.\n\n## Change log\nT13.\n")
        with self.assertRaises(SystemExit):
            evaluate_prompt.prompt_text(path)

    def test_the_real_v1_file_sends_its_prompt_and_not_its_change_log(self):
        path = ROOT / "prompts" / "constraint-translation" / "v1_zero_shot.md"
        if not path.is_file():                      # the family may not exist on every branch
            self.skipTest("v1_zero_shot.md is not on this branch")
        sent = evaluate_prompt.prompt_text(path)
        self.assertIn("You convert what a loading operator says", sent)
        self.assertNotIn("Change log", sent)
        self.assertNotIn("Known risks", sent)


class TestAVersionFileMustMarkItsPrompt(unittest.TestCase):
    """Sam's point on #30: a half-open marker fails loudly, no markers at all fails silently."""

    FAMILY = ROOT / "prompts" / "constraint-translation"

    def test_a_version_file_without_markers_stops_the_run(self):
        path = self.FAMILY / "v99_unmarked.md"
        path.write_text("# v99\n\nPrompt.\n\n## Change log\nT13 is the hard one.\n", encoding="utf-8")
        self.addCleanup(path.unlink)
        with self.assertRaises(SystemExit) as stopped:
            evaluate_prompt.prompt_text(path)
        self.assertIn("change log", str(stopped.exception))

    def test_a_bare_prompt_file_elsewhere_is_still_sent_whole(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "scratch.md"
        path.write_text("You convert speech.\n", encoding="utf-8")
        self.assertEqual(evaluate_prompt.prompt_text(path), "You convert speech.\n")

    def test_what_counts_as_a_version_file(self):
        cases = {
            self.FAMILY / "v1_zero_shot.md": True,
            ROOT / "prompts" / "dev" / "LP-07_constraint-translation-v1.md": False,
            ROOT / "prompts" / "README.md": False,
            ROOT / "documentation" / "design.md": False,
        }
        for path, expected in cases.items():
            with self.subTest(path.name):
                self.assertEqual(evaluate_prompt.is_version_file(path), expected)

    def test_every_committed_version_file_carries_its_markers(self):
        """The rule is only worth having if the files on this branch actually satisfy it."""
        for family in (ROOT / "prompts").iterdir():
            if not family.is_dir() or family.name == "dev":
                continue
            for path in sorted(family.glob("*.md")):
                with self.subTest(f"{family.name}/{path.name}"):
                    sent = evaluate_prompt.prompt_text(path)          # raises if unmarked
                    self.assertNotIn("Change log", sent)
                    self.assertLess(len(sent), len(path.read_text(encoding="utf-8")))


class TestThePrefillAVersionDeclares(unittest.TestCase):
    """How a version is delivered belongs to the version, so two rows stay comparable."""

    FAMILY = ROOT / "prompts" / "constraint-translation"

    def a_file(self, contents: str) -> Path:
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "v9_test.md"
        path.write_text(contents, encoding="utf-8")
        return path

    def test_a_version_that_does_not_prefill_says_so_by_silence(self):
        self.assertIsNone(evaluate_prompt.prefill_of(self.FAMILY / "v1_zero_shot.md"))
        self.assertIsNone(evaluate_prompt.prefill_of(self.FAMILY / "v2_output_format.md"))

    def test_the_declared_prefill_is_read(self):
        self.assertEqual(evaluate_prompt.prefill_of(self.FAMILY / "v3_response_prefill.md"), "{")

    def test_the_comment_space_is_not_sent(self):
        """`<!-- PREFILL: { -->` reads literally as '{ ', and the API refuses a trailing space."""
        path = self.a_file("<!-- PREFILL: { -->\ntext\n")
        self.assertEqual(evaluate_prompt.prefill_of(path), "{")

    def test_an_empty_prefill_stops_the_run(self):
        with self.assertRaises(SystemExit):
            evaluate_prompt.prefill_of(self.a_file("<!-- PREFILL:  -->\n"))

    def test_an_unclosed_prefill_stops_the_run(self):
        with self.assertRaises(SystemExit):
            evaluate_prompt.prefill_of(self.a_file("<!-- PREFILL: {\n"))


class TestTheRequestAPrefillBuilds(unittest.TestCase):
    @unittest.skipUnless(
        __import__("importlib.util", fromlist=["util"]).find_spec("anthropic") is not None,
        "the anthropic package is not installed on this machine")
    def test_the_assistant_turn_is_appended_and_rejoined(self):
        import anthropic  # noqa: F401

        sent = {}

        class Messages:
            def create(self, **kwargs):
                sent.update(kwargs)
                return type("R", (), {"stop_reason": "end_turn", "content": [
                    type("B", (), {"type": "text", "text": '"constraints": [], "unresolved": []}'})()]})()

        client = type("Client", (), {"messages": Messages()})()
        translator = llm.Translator(model="m", prefill="{", _client=client)
        out = translator.translate("p", "s", "m")
        self.assertEqual(sent["messages"][-1], {"role": "assistant", "content": "{"})
        self.assertTrue(out.startswith("{"))
        self.assertEqual(json.loads(out), {"constraints": [], "unresolved": []})

    def test_without_a_prefill_no_assistant_turn_is_sent(self):
        sent = {}

        class Messages:
            def create(self, **kwargs):
                sent.update(kwargs)
                return type("R", (), {"stop_reason": "end_turn", "content": [
                    type("B", (), {"type": "text", "text": "{}"})()]})()

        client = type("Client", (), {"messages": Messages()})()
        out = llm.Translator(model="m", _client=client).translate("p", "s", "m")
        self.assertEqual([m["role"] for m in sent["messages"]], ["user"])
        self.assertEqual(out, "{}")
