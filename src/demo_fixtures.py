"""Fixture data for the live demo: one operator, one Paris round, a loaded van, one scanned parcel.

Run from the repository root:  python3 src/demo_fixtures.py

It prints the fill rate the real solver computes, before and after the parcel is scanned, so the
numbers quoted on stage can be checked rather than remembered.

Nothing here calls an API. The route reaches the solver the only way it is allowed to — as a
`ConstraintSet` built by `quai.constraints.parse()` from `unload_at` entries — so this fixture
exercises the same path `POST /constraints` feeds, not a private one.

Two things about the data are deliberate and worth knowing before changing a number:

**Weight follows the route.** The solver loads the last stop first, so a box for stop 8 goes to the
back and onto the floor, and a box for stop 1 rides on top near the doors and comes off first. The
heavy items are therefore given late stops: that is what puts the appliances on the floor and the
light cartons above them. Move a 70 kg appliance to an early stop and the plan will stack it on top
of the cartons — correct for the route, wrong for the van.

**The scanned parcel goes to the first delivery, and two cartons still move.** Stop 2 is late enough
in the loading order — the parcel goes in 17th of 19 — that nothing is ejected, which a later stop
does not manage: give it stop 3 or 4 and the first-fit heuristic re-uses corners the boxes after it
needed, leaving two cartons unplaced.

What stop 2 does not buy is a load that holds still. `B15` and `B18` are the two stop-1 cartons, and
stop 1 comes off first so they are loaded *after* the parcel: both land somewhere else once it is in,
`B15` at (225, 0, 85) → (240, 85, 85) and `B18` at (240, 85, 85) → (185, 0, 90). They stay placed and
the plan stays valid — but a 3D view driven by real coordinates will show those two jump when the
parcel is scanned. Planning around what is already in the van is issue #36; until that lands, this is
a fact of the fixture rather than a bug in it, and `tests/test_demo_fixtures.py` pins which two boxes
move so a third one cannot appear unnoticed. See the 2026-10-01 entry in
`documentation/failures.md`.
"""
import json

from quai.constraints import Manifest, parse
from quai.models import Box, Container
from quai.solver import solve

# The van the round is driven in. Same vehicle as `src/demo.py`, so the two demos are comparable.
VAN = Container(length=300, width=170, height=170, max_weight=1200)

# The route, in delivery order: stop 1 is left first, stop 8 last.
#
# Paris, not Madrid: `POST /route` geocodes through the Base Adresse Nationale, which covers
# France only, so a Spanish address can never resolve and the map screen could never draw this
# round. The addresses themselves live in `web/src/data/manifest.js`, next to the screen that
# needs them — the solver only ever sees these ids.
STOPS = [
    {"id": "S1", "name": "Hôtel de Ville"},
    {"id": "S2", "name": "Champs-Élysées"},
    {"id": "S3", "name": "Bastille"},
    {"id": "S4", "name": "Convention"},
    {"id": "S5", "name": "Voltaire"},
    {"id": "S6", "name": "Faubourg Saint-Antoine"},
    {"id": "S7", "name": "Saint-Germain"},
    {"id": "S8", "name": "Opéra"},
]

OPERATOR = {
    "card_id": "QUAI-OP-7842",
    "name": "Léo-Paul",
    "stops": [stop["name"] for stop in STOPS],
}

# The eighteen boxes already in the van when the demo starts. Dimensions in centimetres, weight in
# kilograms, `stop` an id from STOPS.
#
# The 85 cm width is not decoration: the van is 170 wide, so two of them sit side by side with
# nothing wasted between, and 85 cm high means two layers reach the roof exactly. The cartons are
# 45 cm high on purpose — the head-room they leave is what holds the load at about 78% rather than
# the 89% a fully modular set reaches, which no real round looks like.
LOADED_ITEMS = [
    {"id": "B01", "label": "washing machine",      "length":  85, "width":  85, "height": 85,
     "weight": 74, "stop": "S8"},
    {"id": "B02", "label": "dishwasher",           "length":  60, "width":  85, "height": 85,
     "weight": 48, "stop": "S7"},
    {"id": "B03", "label": "tumble dryer",         "length":  60, "width":  85, "height": 85,
     "weight": 38, "stop": "S6"},
    {"id": "B04", "label": "oven, crated",         "length":  55, "width":  85, "height": 85,
     "weight": 35, "stop": "S5"},
    {"id": "B05", "label": "fridge, crated",       "length":  70, "width":  85, "height": 85,
     "weight": 68, "stop": "S7"},
    {"id": "B06", "label": "crate, bath fittings", "length":  60, "width":  85, "height": 85,
     "weight": 42, "stop": "S6"},
    {"id": "B07", "label": "sofa, wrapped",        "length": 100, "width": 170, "height": 85,
     "weight": 52, "stop": "S8"},
    {"id": "B08", "label": "wardrobe flat-pack",   "length":  85, "width":  85, "height": 85,
     "weight": 40, "stop": "S6"},
    {"id": "B09", "label": "bookshelf flat-pack",  "length":  50, "width":  85, "height": 85,
     "weight": 26, "stop": "S5"},
    {"id": "B10", "label": "tv, boxed",            "length":  45, "width":  85, "height": 45,
     "weight": 15, "stop": "S3"},
    {"id": "B11", "label": "office chair",         "length":  55, "width":  85, "height": 45,
     "weight": 14, "stop": "S4"},
    {"id": "B12", "label": "carton, books",        "length":  40, "width":  85, "height": 45,
     "weight": 22, "stop": "S4"},
    {"id": "B13", "label": "carton, kitchen",      "length":  40, "width":  85, "height": 45,
     "weight": 18, "stop": "S3"},
    {"id": "B14", "label": "carton, linen",        "length":  50, "width":  85, "height": 45,
     "weight": 11, "stop": "S2"},
    {"id": "B15", "label": "carton, toys",         "length":  45, "width":  85, "height": 45,
     "weight":  9, "stop": "S1"},
    {"id": "B16", "label": "crate, tiles",         "length":  40, "width":  85, "height": 45,
     "weight": 62, "stop": "S7"},
    {"id": "B17", "label": "carton, glassware",    "length":  40, "width":  85, "height": 45,
     "weight": 13, "stop": "S2"},
    {"id": "B18", "label": "carton, lamps",        "length":  40, "width":  85, "height": 45,
     "weight":  8, "stop": "S1"},
]

# The parcel scanned on stage. It starts outside the load: the demo adds it, and the solver finds it a
# place without ejecting any of the eighteen already in — two of them do move, though; see *The
# scanned parcel* in the module docstring.
#
# `fragile` is recorded because the label on the box says so, but nothing downstream reads it. The
# contract's nearest constraint is `not_stackable`, which `quai.solver` lists outside `HONOURED` and
# refuses rather than silently ignores — so asking for it here would raise `UnsupportedConstraint`
# instead of planning. Keeping nothing on top of this parcel is issue #29, not this fixture.
SCANNED_ITEM = {
    "code": "QUAI-BOX-0001",
    "label": "fragile parcel",
    "dimensions": [40, 30, 25],
    "weight": 8,
    "fragile": True,
    "stop": "S2",
}


def items(include_scanned: bool = False) -> list[dict]:
    """The load as records, the scanned parcel last when it is part of it."""
    if not include_scanned:
        return list(LOADED_ITEMS)
    length, width, height = SCANNED_ITEM["dimensions"]
    return LOADED_ITEMS + [{"id": SCANNED_ITEM["code"], "label": SCANNED_ITEM["label"],
                            "length": length, "width": width, "height": height,
                            "weight": SCANNED_ITEM["weight"], "stop": SCANNED_ITEM["stop"]}]


def boxes(include_scanned: bool = False) -> list[Box]:
    return [Box(i["id"], i["length"], i["width"], i["height"], i["weight"])
            for i in items(include_scanned)]


def manifest(include_scanned: bool = False) -> Manifest:
    return Manifest(tuple(i["id"] for i in items(include_scanned)),
                    tuple(stop["id"] for stop in STOPS))


def constraint_set(include_scanned: bool = False):
    """The route as the solver reads it: one `unload_at` per box, through `parse()`.

    Built as JSON and validated rather than constructed directly, because `parse()` is the only door
    into the solver and a fixture that skipped it would be testing a path production does not have.
    """
    payload = {"constraints": [{"type": "unload_at", "item": i["id"], "stop": i["stop"]}
                               for i in items(include_scanned)],
               "unresolved": []}
    return parse(json.dumps(payload), manifest(include_scanned))


def plan(include_scanned: bool = False):
    return solve(boxes(include_scanned), VAN, constraint_set(include_scanned))


def main() -> None:
    labels = {i["id"]: i["label"] for i in items(include_scanned=True)}
    before, after = plan(), plan(include_scanned=True)

    print(f"Operator {OPERATOR['name']} ({OPERATOR['card_id']}) — {len(STOPS)} stops: "
          f"{', '.join(OPERATOR['stops'])}")
    print(f"Van {VAN.length} x {VAN.width} x {VAN.height} cm = {VAN.volume:,} cm3, "
          f"max {VAN.max_weight:g} kg\n")

    print(f"{'box':<14} {'label':<21} {'stop':<16} {'x':>4} {'y':>4} {'z':>4}   size (cm)")
    for p in after.placements:
        stop = next(s["name"] for s in STOPS
                    if s["id"] == next(i["stop"] for i in items(True) if i["id"] == p.box.id))
        print(f"{p.box.id:<14} {labels[p.box.id]:<21} {stop:<16} "
              f"{p.x:>4} {p.y:>4} {p.z:>4}   {p.dx} x {p.dy} x {p.dz}")

    print(f"\nLoaded                 {len(before.placements)}/{len(LOADED_ITEMS)} placed   "
          f"fill {before.fill_rate:.1%}   weight {before.total_weight:g} kg")
    print(f"After scanning {SCANNED_ITEM['code']}  {len(after.placements)}/"
          f"{len(items(True))} placed   fill {after.fill_rate:.1%}   "
          f"weight {after.total_weight:g} kg")
    for name, result in (("loaded", before), ("after the scan", after)):
        if result.unplaced:
            print(f"Not placed ({name}):", ", ".join(b.id for b in result.unplaced))


if __name__ == "__main__":
    main()
