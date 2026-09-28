"""Independent checks of a plan's physical validity.

These checks do not trust the solver. They are also what we will use to score
plans proposed by an LLM alone (experiment/llm-only-placement).
"""
from itertools import combinations

from .models import Container, Placement


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


def find_problems(placements: list[Placement], container: Container,
                  min_support: float = 0.75) -> list[str]:
    """List every physical problem in a plan. An empty list means the plan is valid."""
    problems = []
    for p in placements:
        if not is_inside(p, container):
            problems.append(f"{p.box.id} is outside the container")
        if support_ratio(p, placements) < min_support:
            problems.append(f"{p.box.id} is not supported enough")
    for a, b in combinations(placements, 2):
        if overlaps(a, b):
            problems.append(f"{a.box.id} overlaps {b.box.id}")
    total = sum(p.box.weight for p in placements)
    if total > container.max_weight:
        problems.append(f"total weight {total} kg exceeds {container.max_weight} kg")
    return problems
