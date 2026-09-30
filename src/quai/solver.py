"""Deterministic 3D placement heuristic (first fit on candidate points).

1. Sort boxes from largest to smallest volume.
2. Keep a list of candidate corners, starting with the back-left floor corner.
3. For each box, try every candidate corner and every allowed rotation, and keep the
   first position (lowest, then furthest back, then leftmost) that is inside the
   container, overlaps nothing and is supported enough.
4. Placing a box creates three new candidate corners: in front of it, beside it, on top of it.

Same input, same plan, every time. A box that fits nowhere is reported as unplaced,
never forced in.
"""
from .checks import MIN_SUPPORT, is_inside, overlaps, support_ratio
from .models import Box, Container, Placement, Plan


def solve(boxes: list[Box], container: Container) -> Plan:
    placements: list[Placement] = []
    unplaced: list[Box] = []
    corners: set[tuple[int, int, int]] = {(0, 0, 0)}
    weight = 0.0

    for box in sorted(boxes, key=lambda b: (-b.volume, b.id)):
        if weight + box.weight > container.max_weight:
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
