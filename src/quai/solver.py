"""Deterministic 3D placement heuristic (first fit on candidate points).

1. Put the boxes in loading order: the last stop of the route first, and inside a stop the items
   the operator asked to load last; largest to smallest volume breaks the ties. Items that must stay
   clear (`on_top`) are then moved to the end of that order — nothing may be placed after them.
2. Keep a list of candidate corners, starting with the back-left floor corner.
3. For each box, try every candidate corner and every allowed rotation, and keep the
   first position (lowest, then furthest back, then leftmost) that is inside the
   container, overlaps nothing, is supported enough and overloads nothing under it.
4. Placing a box creates three new candidate corners: in front of it, beside it, on top of it.

Step 1's two groups are what make `on_top` hold by construction rather than by luck: the boxes that
must stay clear are placed when every other box is already down, and nothing is placed after them.

Same input, same plan, every time. A box that fits nowhere is reported as unplaced,
never forced in.

What the operator asked for reaches the solver only as a `ConstraintSet` built by
`quai.constraints.parse`: the solver never reads raw model output, and it reads a validated set
through its accessors rather than by digging into the constraint dictionaries.
"""
from .checks import (MIN_SUPPORT, covered_problems, is_inside, overlaps, stack_problems,
                     support_ratio)
from .constraints import CONSTRAINT_FIELDS, ConstraintSet
from .models import Box, Container, Placement, Plan

# The constraint types this solver knows how to honour. Everything else in the contract is a
# placement rule it has not learned yet (issue #29), and a set carrying one is refused rather than
# planned without: a constraint that passed validation and is then dropped comes back as a plan the
# independent checks call valid, which is the one answer this layer must never give. Read against
# `CONSTRAINT_FIELDS` rather than a second hand-written list, so a type added to the contract
# refuses itself here until someone teaches the solver what it means.
HONOURED: frozenset[str] = frozenset(["unload_at", "load_last", "max_weight_on",
                                      "max_total_weight", "on_top"])


class UnsupportedConstraint(ValueError):
    """The set carries a constraint the solver cannot honour yet.

    Raised instead of returning a plan, because the caller cannot tell the difference between a
    plan that respected a constraint and one that never read it.
    """


def solve(boxes: list[Box], container: Container,
          constraints: ConstraintSet | None = None) -> Plan:
    """Place the boxes, honouring the constraints this solver knows how to honour.

    The set's `unresolved` entries are deliberately not read here. They are the things the operator
    said that the model could not translate, and nothing about them is a placement rule — whether an
    unresolved entry should stop a plan being made at all, or be shown beside it, belongs to the
    end-to-end path (#19), which is the layer that can ask the operator. This function refuses what
    it cannot honour and ignores what was never a constraint; surfacing that is the caller's.
    """
    refuse_unhandled(constraints)
    placements: list[Placement] = []
    unplaced: list[Box] = []
    corners: set[tuple[int, int, int]] = {(0, 0, 0)}
    weight = 0.0
    cap = weight_cap(container, constraints)
    limits = stack_limits(constraints)
    clear = must_stay_clear(constraints)

    for box in last(loading_order(boxes, constraints), clear):
        if weight + box.weight > cap:
            unplaced.append(box)
            continue
        chosen = None
        for x, y, z in sorted(corners, key=lambda c: (c[2], c[0], c[1])):
            for dx, dy, dz in box.orientations():
                candidate = Placement(box, x, y, z, dx, dy, dz)
                if not is_inside(candidate, container):
                    continue
                if any(overlaps(candidate, p) for p in placements):
                    continue
                if support_ratio(candidate, placements) < MIN_SUPPORT:
                    continue
                if overloads(candidate, placements, limits):
                    continue
                if buries(candidate, placements, clear):
                    continue
                chosen = candidate
                break
            if chosen:
                break
        if chosen is None:
            unplaced.append(box)
            continue
        placements.append(chosen)
        weight += box.weight
        corners.discard((chosen.x, chosen.y, chosen.z))
        corners.update({(chosen.x2, chosen.y, chosen.z),
                        (chosen.x, chosen.y2, chosen.z),
                        (chosen.x, chosen.y, chosen.z2)})

    return Plan(container, placements, unplaced)


def unhandled(constraints: ConstraintSet | None) -> list[str]:
    """The constraint types in this set the solver cannot honour, in the contract's own order."""
    if constraints is None:
        return []
    return [kind for kind in CONSTRAINT_FIELDS
            if kind not in HONOURED and constraints.of_type(kind)]


def refuse_unhandled(constraints: ConstraintSet | None) -> None:
    """Stop before planning if the operator asked for something this solver cannot do."""
    kinds = unhandled(constraints)
    if kinds:
        raise UnsupportedConstraint(
            "this solver cannot honour " + ", ".join(kinds) + " yet, so it will not plan with "
            "them: a dropped constraint would come back as a plan the checks call valid. "
            "See issue #29.")


def loading_order(boxes: list[Box], constraints: ConstraintSet | None) -> list[Box]:
    """The boxes in the order they are loaded.

    The route decides first. The earliest stop has to come out first, so it is loaded last and the
    last stop is loaded first; an item with no `unload_at` travels the whole route and so is loaded
    with the last stop. Inside one stop, the items the operator asked to load last come last.
    Whatever is still tied is loaded from largest to smallest volume, then by id, so the same input
    always gives the same plan.
    """
    if constraints is None:
        return sorted(boxes, key=lambda b: (-b.volume, b.id))
    unknown = sorted(b.id for b in boxes if b.id not in constraints.manifest.items)
    if unknown:
        # The constraints were validated against a manifest; a box outside it was never checked,
        # and guessing a stop for it would invent the one thing the route is not allowed to invent.
        raise ValueError("these boxes are not in the manifest the constraints were validated "
                         f"against: {', '.join(unknown)}")
    stops = constraints.manifest.stops
    unloading = constraints.unloading_plan()
    # `load_last` only orders items within their own stop, so it sits below the stop in the key and
    # can never move a box past one for another stop. A stop whose items all carry it is a stop
    # where they all share this rank: the tie-breaks decide, exactly as if none of them carried it.
    last_group = set(constraints.items_with("load_last"))
    return sorted(boxes, key=lambda b: (-stops.index(unloading[b.id]), b.id in last_group,
                                        -b.volume, b.id))


def must_stay_clear(constraints: ConstraintSet | None) -> set[str]:
    """The items the operator asked to keep nothing above: `on_top`.

    "In the top layer" is not something a plan records — the solver never knows the finished height
    while it is working. "Nothing above it" is the same request in terms the geometry can answer, and
    it is the reading `quai.checks.covered_problems` judges a finished plan by.
    """
    if constraints is None:
        return set()
    return set(constraints.items_with("on_top"))


def last(order: list[Box], clear: set[str]) -> list[Box]:
    """The loading order, with the items that must stay clear moved to the end of it.

    This is the one place `on_top` overrides the route, and it has to. Nothing may be placed after a
    box that must stay clear, or the box placed after it could land on top; so it goes last, keeping
    its rank relative to the other `on_top` items. The cost is real and worth stating: that box no
    longer takes the position its stop would have given it, so an `on_top` item for a late stop ends
    up near the doors rather than deep in the load. `load_last` deliberately sits *below* the stop in
    `loading_order` for exactly this reason; `on_top` cannot, because being clear is a property of
    the finished plan and ordering is the only lever a single greedy pass has over it.

    Keeping the two groups in their original relative order is what makes the result deterministic,
    like everything else here.
    """
    if not clear:
        return order
    return ([box for box in order if box.id not in clear]
            + [box for box in order if box.id in clear])


def buries(candidate: Placement, placements: list[Placement], clear: set[str]) -> bool:
    """True if the plan this candidate would make puts something above a box that must stay clear.

    Asked of the whole resulting plan rather than of the candidate alone, for the same reason
    `overloads` is: it has to catch both directions at once. The candidate may be landing on top of a
    box that must stay clear, and the candidate may itself be one that must stay clear and be landing
    under something already placed. One question covers both.

    In the first pass this is vacuous — no box that must stay clear has been placed yet — and the cost
    of asking anyway is one empty loop, which is cheaper than a reader wondering which passes it
    applies to.
    """
    return bool(clear) and bool(covered_problems(placements + [candidate], clear))


def weight_cap(container: Container, constraints: ConstraintSet | None) -> float:
    """What the load may weigh: the lower of what the vehicle carries and what the operator allowed.

    Only the smaller of the two is ever reachable, so a `max_total_weight` above the vehicle's own
    limit does not raise it.
    """
    stated = constraints.limit("max_total_weight") if constraints is not None else None
    return container.max_weight if stated is None else min(container.max_weight, stated)


def stack_limits(constraints: ConstraintSet | None) -> dict[str, float]:
    """Each box that was given a `max_weight_on`, mapped to the weight its stack may not exceed."""
    if constraints is None:
        return {}
    return {c["item"]: c["limit_kg"] for c in constraints.of_type("max_weight_on")}


def overloads(candidate: Placement, placements: list[Placement],
              limits: dict[str, float]) -> bool:
    """True if the plan this candidate would make puts a box over its stack limit.

    The question is asked of the whole resulting plan, not of the candidate alone: the limit covers
    everything above a box, and a box placed later can come to rest under one already loaded and
    take its weight. `stack_problems` is the same rule the independent checks judge the finished
    plan by, so the solver cannot pack by a looser one.
    """
    return bool(limits) and bool(stack_problems(placements + [candidate], limits))
