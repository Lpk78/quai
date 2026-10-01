"""Deterministic 3D placement heuristic (first fit on candidate points).

1. Put the boxes in loading order: the last stop of the route first, and inside a stop the items
   the operator asked to load last; largest to smallest volume breaks the ties.
2. Keep a list of candidate corners, starting with the back-left floor corner.
3. For each box, try every candidate corner and every allowed rotation, and keep the
   first position (lowest, then furthest back, then leftmost) that is inside the
   container, overlaps nothing, is supported enough and overloads nothing under it.
4. Placing a box creates three new candidate corners: in front of it, beside it, on top of it.

Same input, same plan, every time. A box that fits nowhere is reported as unplaced,
never forced in.

What the operator asked for reaches the solver only as a `ConstraintSet` built by
`quai.constraints.parse`: the solver never reads raw model output, and it reads a validated set
through its accessors rather than by digging into the constraint dictionaries.
"""
from .checks import MIN_SUPPORT, is_inside, overlaps, stack_problems, support_ratio
from .constraints import CONSTRAINT_FIELDS, ConstraintSet
from .models import Box, Container, Placement, Plan

# The constraint types this solver knows how to honour. Everything else in the contract is a
# placement rule it has not learned yet (issue #29), and a set carrying one is refused rather than
# planned without: a constraint that passed validation and is then dropped comes back as a plan the
# independent checks call valid, which is the one answer this layer must never give. Read against
# `CONSTRAINT_FIELDS` rather than a second hand-written list, so a type added to the contract
# refuses itself here until someone teaches the solver what it means.
HONOURED: frozenset[str] = frozenset(["unload_at", "load_last", "max_weight_on",
                                      "max_total_weight"])


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

    for box in loading_order(boxes, constraints):
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
