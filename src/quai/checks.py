"""Independent checks of a plan's physical validity.

These checks do not trust the solver. They are also what we will use to score
plans proposed by an LLM alone (experiment/llm-only-placement).
"""
from collections import Counter
from itertools import combinations

from .models import Container, Placement

# The one definition of "supported enough". The solver imports it so that the solver and
# these checks can never disagree about what counts as a valid plan.
MIN_SUPPORT = 0.75


def overlaps(a: Placement, b: Placement) -> bool:
    """True if two boxes share some volume (touching faces is allowed)."""
    return (a.x < b.x2 and b.x < a.x2
            and a.y < b.y2 and b.y < a.y2
            and a.z < b.z2 and b.z < a.z2)


def is_inside(p: Placement, c: Container) -> bool:
    return (p.x >= 0 and p.y >= 0 and p.z >= 0
            and p.x2 <= c.length and p.y2 <= c.width and p.z2 <= c.height)


def support_ratio(p: Placement, others: list[Placement]) -> float:
    """Share of the box's base resting on the floor or on the top of other boxes."""
    if p.z == 0:
        return 1.0
    supported = 0
    for o in others:
        if o is p or o.z2 != p.z:
            continue
        w = min(p.x2, o.x2) - max(p.x, o.x)
        d = min(p.y2, o.y2) - max(p.y, o.y)
        if w > 0 and d > 0:
            supported += w * d
    return supported / (p.dx * p.dy)


def resting_on(p: Placement, placements: list[Placement]) -> list[Placement]:
    """The placements `p` sits on directly: their top face is its base, footprints overlapping."""
    return [o for o in placements
            if o is not p and o.z2 == p.z
            and min(p.x2, o.x2) > max(p.x, o.x)
            and min(p.y2, o.y2) > max(p.y, o.y)]


def stack_below(p: Placement, placements: list[Placement]) -> list[Placement]:
    """Everything `p` bears on, directly or through the boxes in between.

    The contract reads `max_weight_on` as the whole stack above an item, so a box counts against
    every box under it and not only against the one it rests on.
    """
    below: list[Placement] = []
    seen = {id(p)}
    queue = list(resting_on(p, placements))
    while queue:
        other = queue.pop()
        if id(other) in seen:
            continue
        seen.add(id(other))
        below.append(other)
        queue += resting_on(other, placements)
    return below


def weight_above(p: Placement, placements: list[Placement]) -> float:
    """Total weight of the whole stack resting on `p`, at any height above it."""
    return sum(o.box.weight for o in placements
               if any(under is p for under in stack_below(o, placements)))


def footprints_overlap(a: Placement, b: Placement) -> bool:
    """True if `a` and `b` share floor area, whatever height either of them is at."""
    return (min(a.x2, b.x2) > max(a.x, b.x)
            and min(a.y2, b.y2) > max(a.y, b.y))


def covering(p: Placement, placements: list[Placement]) -> list[Placement]:
    """Everything standing in the column above `p`, resting on it or not.

    Deliberately not `stack_below` reversed. That walks the resting-contact graph, which is right for
    `max_weight_on` because weight travels through contact — but a box supported three quarters by a
    taller neighbour can **overhang** `p` without resting on it, and it is still over `p`. An operator
    saying "nothing on top of this" means the column, not the contact graph.
    """
    return [o for o in placements
            if o is not p and o.z >= p.z2 and footprints_overlap(o, p)]


def covered_problems(placements: list[Placement], must_be_clear: set[str] | None) -> list[str]:
    """Every box that had to stay clear and has something above it anyway.

    `on_top` is read as "nothing is above it", which is what makes it checkable at all: "the top
    layer" is not a thing the plan records, whereas an empty column is. The solver asks this of the
    plan a candidate would produce, so the rule it packs by and the rule this module judges by are one
    definition — the same arrangement `stack_problems` has.
    """
    problems = []
    for p in placements:
        if p.box.id not in (must_be_clear or set()):
            continue
        above = sorted(o.box.id for o in covering(p, placements))
        if above:
            problems.append(f"{p.box.id} must stay clear but carries {', '.join(above)} above it")
    return problems


def stack_problems(placements: list[Placement],
                   max_weight_on: dict[str, float] | None) -> list[str]:
    """Every box carrying more than the limit the operator gave it.

    The solver calls this on the plan a candidate placement would produce, so the rule it packs by
    and the rule this module judges by are one definition. Asking it of the finished plan is what
    makes it right: a box placed later can slide under one already loaded and pick up its weight,
    which no check of the candidate alone would see.
    """
    problems = []
    for p in placements:
        limit = (max_weight_on or {}).get(p.box.id)
        if limit is None:
            continue
        carried = weight_above(p, placements)
        if carried > limit:
            problems.append(f"{p.box.id} carries {carried:g} kg, more than its {limit:g} kg limit")
    return problems


def find_problems(placements: list[Placement], container: Container,
                  min_support: float = MIN_SUPPORT,
                  max_weight_on: dict[str, float] | None = None,
                  must_be_clear: set[str] | None = None) -> list[str]:
    """List every physical problem in a plan. An empty list means the plan is valid.

    `max_weight_on` maps a box id to the weight its whole stack may not exceed, as the operator
    stated it; boxes with no limit are left out of it. `must_be_clear` is the ids the operator asked
    to keep nothing above — `on_top` — and a plan that puts something over one of them is invalid
    here, not merely unlucky.
    """
    problems = []
    for p in placements:
        if (p.dx, p.dy, p.dz) not in p.box.orientations():
            problems.append(f"{p.box.id} is not one of its upright rotations")
            # The remaining geometry says nothing once the dimensions are wrong, and a
            # zero-width placement would divide by zero in support_ratio.
            continue
        if not is_inside(p, container):
            problems.append(f"{p.box.id} is outside the container")
        if support_ratio(p, placements) < min_support:
            problems.append(f"{p.box.id} is not supported enough")
    for box_id, count in Counter(p.box.id for p in placements).items():
        if count > 1:
            problems.append(f"{box_id} is placed {count} times")
    for a, b in combinations(placements, 2):
        if overlaps(a, b):
            problems.append(f"{a.box.id} overlaps {b.box.id}")
    problems += stack_problems(placements, max_weight_on)
    problems += covered_problems(placements, must_be_clear)
    total = sum(p.box.weight for p in placements)
    if total > container.max_weight:
        problems.append(f"total weight {total} kg exceeds {container.max_weight} kg")
    return problems
