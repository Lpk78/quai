"""What a change on the loading dock does to a plan in progress.

An incident is one thing going wrong, or arriving, while a vehicle is being loaded. It never moves
a box that is already in the vehicle: the operator put it there, and the point of recomputing is to
work around it rather than to ask for the van to be emptied.

Three kinds, and what each one means for the two lists — what is already loaded, and what is still
waiting on the dock:

| kind | still on the dock | already in the vehicle |
|---|---|---|
| `missing` | cannot be found, so it leaves the plan | refused: one in the vehicle is not missing |
| `damaged` | unusable, so it leaves the plan | it comes out, and the space it frees is replanned |
| `added` | refused: it is already in the plan | refused: it is already in the vehicle |

`missing` on a box that is already loaded is the one case worth refusing rather than guessing. It
describes a vehicle that cannot exist — the box is either in the van or it is not — and the two
readings ("it fell out" and "the operator was wrong about loading it") lead to different plans. The
operator is standing next to the vehicle and can say which.
"""
from dataclasses import dataclass

from .models import Box, Placement

MISSING = "missing"
DAMAGED = "damaged"
ADDED = "added"

KINDS = frozenset([MISSING, DAMAGED, ADDED])


class IncidentRefused(ValueError):
    """The incident does not describe something that could have happened to this load."""


@dataclass(frozen=True)
class Incident:
    """One thing that happened. `box` is required for `added` and is otherwise just an id."""
    kind: str
    box_id: str
    box: Box | None = None

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise IncidentRefused(f"unknown incident {self.kind!r}; expected one of "
                                 f"{', '.join(sorted(KINDS))}")
        if not self.box_id:
            raise IncidentRefused("an incident has to name a box")
        if self.kind == ADDED and self.box is None:
            raise IncidentRefused(f"adding {self.box_id} needs the box itself: its dimensions "
                                  "and weight are not known from the id alone")
        if self.kind == ADDED and self.box.id != self.box_id:
            raise IncidentRefused(f"the added box is {self.box.id!r} but the incident names "
                                  f"{self.box_id!r}")


def apply(incident: Incident, loaded: list[Placement],
          waiting: list[Box]) -> tuple[list[Placement], list[Box]]:
    """The two lists as they are after the incident: what stays in the vehicle, what is replanned.

    Order is preserved in both. `waiting` keeps the order it arrived in: the route decides the
    loading order downstream, and an incident is not a reason to shuffle it.
    """
    in_vehicle = {placed.box.id for placed in loaded}
    on_dock = {box.id for box in waiting}

    if incident.kind == ADDED:
        if incident.box_id in in_vehicle:
            raise IncidentRefused(f"{incident.box_id} is already in the vehicle, so it cannot "
                                  "be added to the load")
        if incident.box_id in on_dock:
            raise IncidentRefused(f"{incident.box_id} is already waiting to be loaded, so it "
                                  "cannot be added again")
        return list(loaded), [*waiting, incident.box]

    if incident.box_id not in in_vehicle and incident.box_id not in on_dock:
        raise IncidentRefused(f"{incident.box_id} is neither in the vehicle nor waiting to be "
                              "loaded, so nothing can have happened to it here")

    if incident.kind == MISSING:
        if incident.box_id in in_vehicle:
            raise IncidentRefused(f"{incident.box_id} is already in the vehicle, so it cannot be "
                                  "missing. If it has been taken back out, report it as damaged or "
                                  "send the load as it now stands")
        return list(loaded), [box for box in waiting if box.id != incident.box_id]

    # DAMAGED: out of the plan either way, and out of the vehicle if that is where it is.
    return ([placed for placed in loaded if placed.box.id != incident.box_id],
            [box for box in waiting if box.id != incident.box_id])
