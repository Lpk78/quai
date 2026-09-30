"""Deterministic 3D placement heuristic (first fit on candidate points).

1. Sort boxes from largest to smallest volume.
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
from .checks import MIN_SUPPORT, is_inside, overlaps, stack_below, support_ratio, weight_above
from .constraints import ConstraintSet
from .models import Box, Container, Placement, Plan


def solve(boxes: list[Box], container: Container,
          constraints: ConstraintSet | None = None) -> Plan:
    placements: list[Placement] = []
    unplaced: list[Box] = []
    corners: set[tuple[int, int, int]] = {(0, 0, 0)}
    weight = 0.0
    cap = weight_cap(container, constraints)
    limits = stack_limits(constraints)

    for box in sorted(boxes, key=lambda b: (-b.volume, b.id)):
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
    """True if putting `candidate` here would push a box under it past its stack limit.

    The limit covers the whole stack above a box, so the candidate counts against every box it
    bears on, however many layers down.
    """
    if not limits:
        return False
    for under in stack_below(candidate, placements):
        limit = limits.get(under.box.id)
        if limit is not None and weight_above(under, placements) + candidate.box.weight > limit:
            return True
    return False
