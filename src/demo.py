"""Plan a small sample load and print the result.

Run from the repository root:  python3 src/demo.py
"""
from quai.checks import find_problems
from quai.models import Box, Container
from quai.solver import solve

VAN = Container(length=300, width=170, height=170, max_weight=1200)

BOXES = [
    Box("fridge", 70, 70, 160, 60),
    Box("washer", 60, 60, 85, 70),
    Box("dryer", 60, 60, 85, 40),
    Box("sofa", 200, 90, 80, 45),
    Box("tv", 130, 20, 80, 15),
    Box("carton-1", 60, 40, 40, 12),
    Box("carton-2", 60, 40, 40, 12),
    Box("carton-3", 60, 40, 40, 10),
    Box("carton-4", 40, 30, 30, 6),
    Box("carton-5", 40, 30, 30, 6),
    Box("mattress", 190, 140, 25, 25),
]


def main() -> None:
    plan = solve(BOXES, VAN)
    print(f"Container {VAN.length} x {VAN.width} x {VAN.height} cm, max {VAN.max_weight:g} kg\n")
    print(f"{'box':<10} {'x':>4} {'y':>4} {'z':>4}   size (cm)")
    for p in plan.placements:
        print(f"{p.box.id:<10} {p.x:>4} {p.y:>4} {p.z:>4}   {p.dx} x {p.dy} x {p.dz}")
    print(f"\nPlaced: {len(plan.placements)}/{len(BOXES)}   "
          f"Fill rate: {plan.fill_rate:.0%}   Weight: {plan.total_weight:g} kg")
    if plan.unplaced:
        print("Not placed:", ", ".join(b.id for b in plan.unplaced))
    problems = find_problems(plan.placements, VAN)
    print("Independent check:", "valid plan" if not problems else problems)


if __name__ == "__main__":
    main()
