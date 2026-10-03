"""Run from the repository root:  python3 -m unittest discover tests

No network here. The scoring has to be trustworthy before it is pointed at twenty real replies, so
it is tested against replies written by hand — including the shapes a model actually produces.
"""
import collections
import json
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from demo import BOXES as DEMO_BOXES, VAN as DEMO_VAN  # noqa: E402
import run_placement_experiment  # noqa: E402
from quai import llm_placement, solver  # noqa: E402
from quai.checks import find_problems  # noqa: E402
from quai.models import Box, Container  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

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

class TestTheRecordedRun(unittest.TestCase):
    """The run the write-up in `documentation/failures.md` is built from (`SA-06`, finished in `SA-26`).

    The table there claims one physically valid plan in twenty. That claim was worth nothing to
    anybody but its author while the replies behind it sat in a Git-ignored directory: checking it
    meant twenty billed calls, which produce *different* replies and so can neither confirm nor
    refute the recorded ones. The run is tracked now, and this class is what makes it evidence —
    every figure the document states is re-derived from those replies using today's
    `find_problems()`, not the one that was current when the run happened. Edit a number in the
    table, or make the checks stricter, and this fails.
    """

    RUN = ROOT / "outputs" / "placement" / "llm_placement_20261001-141020.json"
    FAILURES = ROOT / "documentation" / "failures.md"

    @classmethod
    def setUpClass(cls):
        cls.recorded = json.loads(cls.RUN.read_text(encoding="utf-8"))
        cls.scored = {}
        for attempt in cls.recorded["attempts"]:
            cls.scored.setdefault(str(attempt["temperature"]), []).append(
                llm_placement.score(attempt["raw"], DEMO_BOXES, DEMO_VAN))
        # The experiment's own summariser, not a second copy of it: the classifier that produced
        # the published figures is the one that has to reproduce them.
        cls.summary = {temperature: run_placement_experiment.summarise(attempts)
                       for temperature, attempts in cls.scored.items()}
        cls.text = cls.FAILURES.read_text(encoding="utf-8")

    def documented_row(self, label):
        """One row of the results table, as the document actually holds it."""
        for line in self.text.split("\n"):
            stripped = line.strip()
            if stripped.startswith("|") and label in stripped:
                return [cell.strip().strip("*") for cell in stripped.strip("|").split("|")]
        self.fail(f"no row labelled {label!r} in failures.md — was the table reworded or removed?")

    def both_temperatures(self, label):
        row = self.documented_row(label)
        return (("0.0", row[1]), ("1.0", row[2]))

    def test_the_tracked_file_is_the_run_the_document_describes(self):
        self.assertEqual(self.recorded["model"], "claude-haiku-4-5-20251001")
        self.assertEqual(self.recorded["runs_per_temperature"], 10)
        self.assertEqual(len(self.recorded["attempts"]), 20)
        self.assertIn(self.recorded["model"], self.text)

    def test_the_valid_plan_count_in_the_table_re_derives_from_the_replies(self):
        # The headline the architecture rests on: 1/10 at temperature 0, 0/10 at temperature 1.
        for temperature, documented in self.both_temperatures("physically valid plans"):
            with self.subTest(temperature):
                self.assertEqual(f"{self.summary[temperature]['valid']}/10", documented)

    def test_the_parse_count_in_the_table_re_derives_from_the_replies(self):
        for temperature, documented in self.both_temperatures("replies that parsed"):
            with self.subTest(temperature):
                self.assertEqual(f"{self.summary[temperature]['parsed']}/10", documented)

    def test_the_problems_per_plan_in_the_table_re_derives_from_the_replies(self):
        for temperature, documented in self.both_temperatures("problems per plan"):
            with self.subTest(temperature):
                average = self.summary[temperature]["problems_per_parsed_run"]
                self.assertEqual(f"{average:.1f}", documented)

    def test_temperature_zero_was_not_deterministic(self):
        # Seven different plans from ten identical requests, which is the reproducibility half of
        # the question the experiment was asked.
        for temperature, documented in self.both_temperatures("distinct plans"):
            with self.subTest(temperature):
                distinct = self.summary[temperature]["distinct_plans"]
                self.assertEqual(f"{distinct} of 10", documented)

    def test_the_fault_totals_quoted_in_the_prose_re_derive_from_the_replies(self):
        # "41 boxes floating with nothing under them, 41 laid on their side …, 20 overlapping
        # another box, 5 outside the van, and 3 never placed at all."
        counted = collections.Counter()
        for summary in self.summary.values():
            counted.update(summary["problems_by_kind"])
        self.assertNotIn("other", counted, "a fault nobody classified is a fault nobody counted")
        # Each total is read out of the sentence itself. Asserting `str(total) in self.text` instead
        # was the first version of this test and it passed when the prose said forty: "41" still
        # appeared further along the same sentence. The document has to be the source, or the test
        # only checks the test.
        phrases = (("unsupported", r"(\d+) boxes floating"),
                   ("rotation", r"(\d+) laid on their side"),
                   ("overlap", r"(\d+) overlapping another box"),
                   ("outside", r"(\d+) outside the van"),
                   ("not placed", r"(\d+) never placed at all"))
        for kind, pattern in phrases:
            with self.subTest(kind):
                found = re.search(pattern, self.text)
                self.assertIsNotNone(found, f"failures.md no longer states a total for {kind}")
                self.assertEqual(counted[kind], int(found.group(1)))
        self.assertEqual(sum(counted.values()),
                         sum(int(re.search(p, self.text).group(1)) for _, p in phrases),
                         "the sentence lists faults the replies do not hold, or misses some")

    def test_the_solver_baseline_the_result_is_compared_against_still_holds(self):
        # The comparison is "46.9 % fill against the solver's 39.3 %". That second figure is stored
        # nowhere — it is whatever `solve()` does today, so the sentence can go stale in silence.
        # 273 commits of solver work have landed since the run, including stop-ordered loading.
        plan = solver.solve(DEMO_BOXES, DEMO_VAN)
        self.assertEqual([box.id for box in plan.unplaced], ["mattress"])
        self.assertEqual(f"{plan.fill_rate:.1%}", "39.3%")
        self.assertEqual(find_problems(plan.placements, DEMO_VAN), [])
        self.assertIn("39.3", self.text)

    def test_the_one_valid_plan_is_still_valid_and_still_beats_the_solver(self):
        # The result that complicates the story, and so the one most worth pinning: the model's
        # single valid plan fitted all eleven boxes, including the mattress the solver gives up on.
        valid = [a for a in self.scored["0.0"] if a.valid]
        self.assertEqual(len(valid), 1, "the run no longer holds exactly one valid plan")
        self.assertEqual(len(valid[0].placements), len(DEMO_BOXES))
        fill = sum(p.dx * p.dy * p.dz for p in valid[0].placements) / DEMO_VAN.volume
        self.assertEqual(f"{fill:.1%}", "46.9%")
        self.assertGreater(fill, solver.solve(DEMO_BOXES, DEMO_VAN).fill_rate)
        self.assertIn("46.9", self.text)
