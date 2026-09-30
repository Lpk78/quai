"""The contract between the LLM and the solver.

`documentation/prompt_evaluation.md` states this contract in prose and scores every prompt version
against it; this module is the executable copy. The two must be kept in step —
`tests/test_constraints.py` reads the document and fails if they drift apart.

The translated output is always `{"constraints": [...], "unresolved": [...]}`, both keys present
even when empty. Every length is in centimetres and every weight in kilograms, whatever unit the
operator used.

Four definitions come from the contract's *Route and unloading order* section, so that the schema
and the solver mean the same thing by them:

- `max_weight_on` covers the whole stack above the item, not only the boxes resting directly on it.
  Enforcing that is the solver's job; this module only carries the number.
- The route is an input, never an output. Stops arrive with the manifest in order, and a constraint
  may only name one of them.
- An item with no `unload_at` comes off at the last stop. That is not missing information: it means
  the item travels the whole route (`ConstraintSet.unload_stop`).
- The stop order always wins over `load_last`, which only orders items within one stop.
"""
from dataclasses import dataclass

# The nine constraint types, each with exactly the fields it carries. A type that is not here, a
# missing field or an extra field is rejected: these nine shapes are all the solver ever sees.
CONSTRAINT_FIELDS: dict[str, frozenset[str]] = {
    "not_stackable": frozenset(["item"]),
    "at_bottom": frozenset(["item"]),
    "on_top": frozenset(["item"]),
    "keep_upright": frozenset(["item"]),
    "unload_at": frozenset(["item", "stop"]),
    "load_last": frozenset(["item"]),
    "max_stack_height": frozenset(["item", "limit_cm"]),
    "max_weight_on": frozenset(["item", "limit_kg"]),
    "max_total_weight": frozenset(["limit_kg"]),
}

# Why a sentence, or part of one, produced no constraint.
REASONS: frozenset[str] = frozenset([
    "ambiguous",
    "unknown_item",
    "unit_missing",
    "contradiction",
    "out_of_scope",
    "injection_attempt",
])

UNRESOLVED_FIELDS: frozenset[str] = frozenset(["text", "reason", "question"])

# One field name per unit, so a value in the wrong unit cannot hide behind the right field name:
# `limit_m` is an unknown field, and 1.2 under `limit_cm` is metres wearing a centimetre label.
LIMIT_FIELDS: frozenset[str] = frozenset(["limit_cm", "limit_kg"])


@dataclass(frozen=True)
class Manifest:
    """What the sentence may refer to: the ids of the items in the load, and the stops in route order."""
    items: tuple[str, ...]
    stops: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("items", "stops"):
            values = getattr(self, name)
            if len(set(values)) != len(values):
                raise ValueError(f"manifest {name} contains the same id twice: {values}")
        if not self.stops:
            raise ValueError("a manifest needs at least one stop: the route is an input")

    @property
    def last_stop(self) -> str:
        return self.stops[-1]

    @classmethod
    def from_boxes(cls, boxes, stops) -> "Manifest":
        return cls(tuple(box.id for box in boxes), tuple(stops))


@dataclass(frozen=True)
class ConstraintSet:
    """A translation that passed validation. Built by `parse`; read by the solver through these
    accessors rather than by digging into the raw dictionaries."""
    manifest: Manifest
    constraints: tuple[dict, ...] = ()
    unresolved: tuple[dict, ...] = ()

    def of_type(self, kind: str) -> tuple[dict, ...]:
        return tuple(c for c in self.constraints if c["type"] == kind)

    def items_with(self, kind: str) -> tuple[str, ...]:
        """The items carrying a flag constraint, e.g. `items_with("at_bottom")`."""
        return tuple(c["item"] for c in self.of_type(kind))

    def limit(self, kind: str, item: str | None = None) -> float | None:
        """The limit given for `item` under `kind`, or None if the operator never gave one.

        `max_total_weight` is about the whole load, so it is read with no item.
        """
        for c in self.of_type(kind):
            if c.get("item") == item:
                return c["limit_cm"] if "limit_cm" in c else c["limit_kg"]
        return None

    def unload_stop(self, item: str) -> str:
        """The stop where an item comes off. Without an `unload_at` it travels the whole route."""
        if item not in self.manifest.items:
            raise KeyError(f"{item} is not in the manifest")
        for c in self.of_type("unload_at"):
            if c["item"] == item:
                return c["stop"]
        return self.manifest.last_stop

    def unloading_plan(self) -> dict[str, str]:
        """Every item of the manifest mapped to the stop where it comes off."""
        return {item: self.unload_stop(item) for item in self.manifest.items}
