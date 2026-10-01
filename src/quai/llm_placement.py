"""The experiment behind the rule: what happens when the model places the boxes itself.

`CLAUDE.md` says the LLM never computes placement — it translates constraints and explains solver
output. That rule was written down before anything measured it. This module asks the model to do the
solver's job directly, on the same load, and scores what comes back with
`quai.checks.find_problems()`, which is the same independent check the solver is held to.

Nothing here is on the product path. It exists so the rule can be justified with numbers, and so the
numbers can be re-derived by whoever doubts them.

Two decisions that make the comparison fair rather than flattering:

- **A code fence is stripped before parsing.** `documentation/prompt_evaluation.md` deliberately
  refuses one, because `POST /constraints` hands the reply to `parse()` untouched — there, the
  envelope is part of what is being measured. Here it is not: the question is whether the model can
  place boxes, and failing all twenty runs on a Markdown habit would answer a different question.
- **The model is given the geometry it needs and nothing about the answer.** The container, the
  box list, the axes and the rules a plan must satisfy — the same facts `solve()` works from. It is
  not shown a worked example or the solver's output, which would measure copying, not placing.
"""
import json
import re
from dataclasses import dataclass

from .checks import find_problems
from .models import Box, Container, Placement

# What the model is asked to produce, in the project's own axes (`models.py`): x is length from the
# back wall, y is width, z is height from the floor, and a box keeps its height — only the footprint
# may turn.
SYSTEM_PROMPT = """You plan how boxes are stacked inside a delivery vehicle.

Answer with one JSON object and nothing else:

{"placements": [{"id": "<box id>", "x": <int>, "y": <int>, "z": <int>,
                 "dx": <int>, "dy": <int>, "dz": <int>}]}

Axes, all in centimetres and all integers:
- x runs along the length of the container; x = 0 is the back wall.
- y runs across its width; y = 0 is the left side.
- z is height; z = 0 is the floor.
- (x, y, z) is the corner of the box nearest the back-left floor corner.
- (dx, dy, dz) are the box's dimensions as placed.

The rules a plan has to satisfy:
- Every box is inside the container: 0 <= x and x + dx <= the container length, same for y and z.
- No two boxes share any space. Touching faces are fine; overlapping volumes are not.
- A box must be supported: it rests on the floor (z = 0), or at least 75% of its base area sits on
  the tops of other boxes.
- Boxes stay upright. dz is always the box's own height; dx and dy are its length and width, which
  may be swapped to turn the box on the floor, and nothing else.
- Place every box you can. If one genuinely does not fit, leave it out rather than overlapping it.
"""


@dataclass(frozen=True)
class Attempt:
    """One reply, and what the independent checks made of it."""
    raw: str
    placements: tuple[Placement, ...]
    problems: tuple[str, ...]
    parse_error: str | None = None

    @property
    def parsed(self) -> bool:
        return self.parse_error is None

    @property
    def valid(self) -> bool:
        """A plan with nothing wrong with it. Not the same as a good plan — just a possible one."""
        return self.parsed and not self.problems

    @property
    def signature(self) -> tuple:
        """What makes two answers the same answer, for comparing runs with each other."""
        return tuple(sorted((p.box.id, p.x, p.y, p.z, p.dx, p.dy, p.dz) for p in self.placements))


def load_description(boxes: list[Box], container: Container) -> str:
    """The container and the boxes, as the model is told about them."""
    lines = [f"Container: {container.length} long x {container.width} wide x {container.height} "
             f"high, in centimetres."]
    if container.max_weight != float("inf"):
        lines.append(f"It carries at most {container.max_weight:g} kg.")
    lines.append("")
    lines.append("Boxes to place:")
    lines += [f"- {b.id}: {b.length} x {b.width} x {b.height} cm, {b.weight:g} kg" for b in boxes]
    return "\n".join(lines)


def strip_fence(reply: str) -> str:
    """The JSON inside a Markdown code fence, or the reply unchanged if there is no fence."""
    fenced = re.search(r"```(?:json)?\s*(.*?)```", reply, re.DOTALL)
    return (fenced.group(1) if fenced else reply).strip()


def read_placements(reply: str, boxes: list[Box]) -> tuple[list[Placement], str | None]:
    """Turn a reply into placements, or say why it could not be read.

    A placement naming a box that was never in the load is refused rather than dropped: the model
    inventing a box is a result worth seeing, not noise to tidy away.
    """
    by_id = {box.id: box for box in boxes}
    try:
        payload = json.loads(strip_fence(reply))
    except (json.JSONDecodeError, ValueError) as error:
        return [], f"the reply is not JSON: {error}"
    if not isinstance(payload, dict) or not isinstance(payload.get("placements"), list):
        return [], "the reply has no 'placements' list"
    placements = []
    for index, entry in enumerate(payload["placements"]):
        if not isinstance(entry, dict):
            return [], f"placements[{index}] is not an object"
        missing = [f for f in ("id", "x", "y", "z", "dx", "dy", "dz") if f not in entry]
        if missing:
            return [], f"placements[{index}] is missing {', '.join(missing)}"
        box = by_id.get(entry["id"])
        if box is None:
            return [], f"placements[{index}] names {entry['id']!r}, which is not in the load"
        try:
            placements.append(Placement(box, int(entry["x"]), int(entry["y"]), int(entry["z"]),
                                        int(entry["dx"]), int(entry["dy"]), int(entry["dz"])))
        except (TypeError, ValueError) as error:
            return [], f"placements[{index}] has a coordinate that is not a whole number: {error}"
    return placements, None


def score(reply: str, boxes: list[Box], container: Container) -> Attempt:
    """One reply, read and judged by the same checks the solver answers to."""
    placements, error = read_placements(reply, boxes)
    if error is not None:
        return Attempt(raw=reply, placements=(), problems=(), parse_error=error)
    problems = list(find_problems(placements, container))
    placed = {p.box.id for p in placements}
    for box in boxes:
        if box.id not in placed:
            problems.append(f"{box.id} was not placed")
    return Attempt(raw=reply, placements=tuple(placements), problems=tuple(problems))
