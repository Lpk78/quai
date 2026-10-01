"""Run from the repository root:  python3 -m unittest discover tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from quai import incident  # noqa: E402
from quai.models import Box, Placement  # noqa: E402


def box(box_id: str, weight: float = 10.0) -> Box:
    return Box(box_id, 50, 50, 50, weight)


def placed(box_id: str, z: int = 0) -> Placement:
    return Placement(box(box_id), 0, 0, z, 50, 50, 50)


class TestWhatAnIncidentIs(unittest.TestCase):
    def test_an_unknown_kind_is_refused(self):
        with self.assertRaises(incident.IncidentRefused):
            incident.Incident(kind="exploded", box_id="b1")

    def test_an_incident_has_to_name_a_box(self):
        with self.assertRaises(incident.IncidentRefused):
            incident.Incident(kind=incident.MISSING, box_id="")

    def test_adding_needs_the_box_not_just_its_id(self):
        """Dimensions and weight cannot be inferred from an id, and a plan needs them."""
        with self.assertRaises(incident.IncidentRefused) as refused:
            incident.Incident(kind=incident.ADDED, box_id="new")
        self.assertIn("dimensions", str(refused.exception))

    def test_the_added_box_has_to_be_the_box_named(self):
        with self.assertRaises(incident.IncidentRefused):
            incident.Incident(kind=incident.ADDED, box_id="new", box=box("other"))


class TestMissing(unittest.TestCase):
    def test_a_box_on_the_dock_leaves_the_plan(self):
        after_loaded, after_waiting = incident.apply(
            incident.Incident(incident.MISSING, "b2"), [placed("b1")], [box("b2"), box("b3")])
        self.assertEqual([p.box.id for p in after_loaded], ["b1"])
        self.assertEqual([b.id for b in after_waiting], ["b3"])

    def test_a_box_in_the_vehicle_is_refused(self):
        """It is either in the van or it is not, and the two readings give different plans."""
        with self.assertRaises(incident.IncidentRefused) as refused:
            incident.apply(incident.Incident(incident.MISSING, "b1"), [placed("b1")], [box("b2")])
        self.assertIn("already in the vehicle", str(refused.exception))

    def test_a_box_nobody_has_heard_of_is_refused(self):
        with self.assertRaises(incident.IncidentRefused) as refused:
            incident.apply(incident.Incident(incident.MISSING, "ghost"),
                           [placed("b1")], [box("b2")])
        self.assertIn("neither", str(refused.exception))


class TestDamaged(unittest.TestCase):
    def test_a_box_on_the_dock_leaves_the_plan(self):
        _, after_waiting = incident.apply(
            incident.Incident(incident.DAMAGED, "b2"), [placed("b1")], [box("b2"), box("b3")])
        self.assertEqual([b.id for b in after_waiting], ["b3"])

    def test_a_box_in_the_vehicle_comes_out(self):
        """This is the case that frees space, which is the reason to recompute at all."""
        after_loaded, after_waiting = incident.apply(
            incident.Incident(incident.DAMAGED, "b1"), [placed("b1"), placed("b2", z=50)],
            [box("b3")])
        self.assertEqual([p.box.id for p in after_loaded], ["b2"])
        self.assertEqual([b.id for b in after_waiting], ["b3"])

    def test_a_damaged_box_is_not_replanned(self):
        after_loaded, after_waiting = incident.apply(
            incident.Incident(incident.DAMAGED, "b1"), [placed("b1")], [])
        self.assertEqual(after_loaded, [])
        self.assertEqual(after_waiting, [])


class TestAdded(unittest.TestCase):
    def test_a_new_box_joins_the_dock(self):
        after_loaded, after_waiting = incident.apply(
            incident.Incident(incident.ADDED, "new", box=box("new")), [placed("b1")], [box("b2")])
        self.assertEqual([p.box.id for p in after_loaded], ["b1"])
        self.assertEqual([b.id for b in after_waiting], ["b2", "new"])

    def test_a_box_already_in_the_vehicle_cannot_be_added(self):
        with self.assertRaises(incident.IncidentRefused):
            incident.apply(incident.Incident(incident.ADDED, "b1", box=box("b1")),
                           [placed("b1")], [])

    def test_a_box_already_waiting_cannot_be_added(self):
        with self.assertRaises(incident.IncidentRefused):
            incident.apply(incident.Incident(incident.ADDED, "b2", box=box("b2")),
                           [], [box("b2")])


class TestTheListsAreNotDisturbed(unittest.TestCase):
    def test_the_waiting_order_is_kept(self):
        """The route decides the loading order later; an incident is not a reason to shuffle."""
        waiting = [box("b4"), box("b1"), box("b3")]
        _, after = incident.apply(incident.Incident(incident.ADDED, "b9", box=box("b9")),
                                  [], waiting)
        self.assertEqual([b.id for b in after], ["b4", "b1", "b3", "b9"])

    def test_the_inputs_are_not_mutated(self):
        loaded, waiting = [placed("b1")], [box("b2")]
        incident.apply(incident.Incident(incident.DAMAGED, "b1"), loaded, waiting)
        self.assertEqual([p.box.id for p in loaded], ["b1"])
        self.assertEqual([b.id for b in waiting], ["b2"])


if __name__ == "__main__":
    unittest.main()
