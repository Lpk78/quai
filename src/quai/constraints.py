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
- The stop order always wins over `load_last`, which only orders items within one stop. Several
  items may be loaded last at the same stop: they form the last group there, and the solver orders
  them among themselves.
"""
import json
import math
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

TOP_LEVEL_KEYS: frozenset[str] = frozenset(["constraints", "unresolved"])

# One field name per unit, so a value in the wrong unit cannot hide behind the right field name:
# `limit_m` is an unknown field, and 1.2 under `limit_cm` is metres wearing a centimetre label.
LIMIT_FIELDS: frozenset[str] = frozenset(["limit_cm", "limit_kg"])


@dataclass(frozen=True)
class Manifest:
    """What the sentence may refer to: the ids of the items in the load, and the stops in
    route order."""
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


class ConstraintError(ValueError):
    """Raised by `parse` when the output does not match the contract. It carries every problem,
    not only the first, so the operator can be told everything that is wrong at once."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = list(problems)


def parse(output, manifest: Manifest) -> ConstraintSet:
    """Validate raw model output and return it as a `ConstraintSet`.

    `output` is the JSON text the model returned, or an already decoded object. This is the only
    door into the solver: there is no path that skips `find_problems`, so unvalidated output can
    never be planned with.
    """
    if isinstance(output, (str, bytes, bytearray)):
        try:
            payload = json.loads(output)
        except json.JSONDecodeError as error:
            raise ConstraintError([f"the output is not valid JSON: {error}"]) from error
    else:
        payload = output
    problems = find_problems(payload, manifest)
    if problems:
        raise ConstraintError(problems)
    # Copied, so that a later change to the caller's payload cannot alter a validated set.
    return ConstraintSet(manifest,
                         tuple(dict(c) for c in payload["constraints"]),
                         tuple(dict(u) for u in payload["unresolved"]))


def find_problems(payload, manifest: Manifest) -> list[str]:
    """Every reason this output must not reach the solver. An empty list means it is valid."""
    if not isinstance(payload, dict):
        return [f"the output must be a JSON object, got {type(payload).__name__}"]
    problems = []
    for key in sorted(TOP_LEVEL_KEYS - set(payload)):
        problems.append(f"missing key {key!r}")
    # Anything outside the two keys is refused rather than ignored: this is where a plan, a
    # position or a loading sequence the solver must decide would arrive.
    for key in sorted(set(payload) - TOP_LEVEL_KEYS):
        problems.append(f"unknown key {key!r}")
    lists = {}
    for key in sorted(TOP_LEVEL_KEYS & set(payload)):
        if isinstance(payload[key], list):
            lists[key] = payload[key]
        else:
            problems.append(f"{key!r} must be a list, got {type(payload[key]).__name__}")
    for index, constraint in enumerate(lists.get("constraints", [])):
        problems += _constraint_problems(constraint, manifest, f"constraints[{index}]")
    for index, entry in enumerate(lists.get("unresolved", [])):
        problems += _unresolved_problems(entry, f"unresolved[{index}]")
    if len(lists) == len(TOP_LEVEL_KEYS) and not lists["constraints"] and not lists["unresolved"]:
        problems.append("nothing was translated and nothing was reported as unresolved")
    if not problems:
        # Only worth asking once every constraint is known to be well formed.
        problems += _conflict_problems(lists["constraints"])
    return problems


def _constraint_problems(constraint, manifest: Manifest, where: str) -> list[str]:
    if not isinstance(constraint, dict):
        return [f"{where} must be an object, got {type(constraint).__name__}"]
    kind = constraint.get("type")
    # `isinstance` first: a type given as a list or a dict is unhashable and would not even be
    # comparable to the declared names.
    if not isinstance(kind, str) or kind not in CONSTRAINT_FIELDS:
        return [f"{where}: unknown constraint type {kind!r}"]
    expected, given = CONSTRAINT_FIELDS[kind], set(constraint) - {"type"}
    problems = [f"{where}: {kind} needs {field!r}" for field in sorted(expected - given)]
    problems += [f"{where}: {kind} does not take {field!r}" for field in sorted(given - expected)]
    if "item" in expected & given and constraint["item"] not in manifest.items:
        # An item nobody loaded is an `unknown_item` for the operator to confirm, never a
        # constraint bound to the nearest box.
        problems.append(f"{where}: {constraint['item']!r} is not in the manifest")
    if "stop" in expected & given and constraint["stop"] not in manifest.stops:
        problems.append(f"{where}: {constraint['stop']!r} is not a stop on the route")
    for field in sorted(LIMIT_FIELDS & expected & given):
        problems += _limit_problems(constraint[field], field, where)
    return problems


def _limit_problems(value, field: str, where: str) -> list[str]:
    """Centimetres are whole; kilograms may be fractional; neither may be zero or negative."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return [f"{where}: {field} must be a number, got {value!r}"]
    if not math.isfinite(value):
        # JSON decodes Infinity and NaN, and a limit that is neither cannot be compared to a load.
        return [f"{where}: {field} must be a finite number, got {value!r}"]
    if field == "limit_cm" and value != int(value):
        # 1.2 here is one metre twenty in the wrong unit, not a centimetre count.
        return [f"{where}: {field} must be a whole number of centimetres, got {value!r}"]
    if value <= 0:
        return [f"{where}: {field} must be greater than 0, got {value!r}"]
    return []


def _unresolved_problems(entry, where: str) -> list[str]:
    if not isinstance(entry, dict):
        return [f"{where} must be an object, got {type(entry).__name__}"]
    given = set(entry)
    problems = [f"{where}: needs {field!r}" for field in sorted(UNRESOLVED_FIELDS - given)]
    problems += [f"{where}: does not take {field!r}" for field in sorted(given - UNRESOLVED_FIELDS)]
    reason = entry.get("reason")
    if "reason" in given and (not isinstance(reason, str) or reason not in REASONS):
        problems.append(f"{where}: unknown reason {reason!r}")
    if "text" in given and not _is_quoted_text(entry["text"]):
        problems.append(f"{where}: text must quote the part of the sentence at fault")
    question = entry.get("question")
    if "question" in given and question is not None and not _is_quoted_text(question):
        problems.append(f"{where}: question must be a question to ask the operator, or null")
    return problems


def _is_quoted_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _conflict_problems(constraints) -> list[str]:
    """Contradictions the model should have reported as `contradiction` instead of emitting."""
    problems = []
    flags = {kind: set(c["item"] for c in constraints if c["type"] == kind)
             for kind in ("at_bottom", "on_top")}
    for item in sorted(flags["at_bottom"] & flags["on_top"]):
        problems.append(f"{item} cannot be both at_bottom and on_top")
    for kind, field in (("unload_at", "stop"), ("max_stack_height", "limit_cm"),
                        ("max_weight_on", "limit_kg"), ("max_total_weight", "limit_kg")):
        stated: dict[str | None, object] = {}
        for c in constraints:
            if c["type"] != kind:
                continue
            item = c.get("item")
            if item in stated and stated[item] != c[field]:
                problems.append(f"{kind} for {item or 'the whole load'} is given twice, "
                                f"as {stated[item]} and as {c[field]}")
            stated.setdefault(item, c[field])
    # Several `load_last` items at one stop are not a clash: "load the toolbox and the paint cans
    # last" is one request, and refusing it would lose the whole sentence. They form the last group
    # at that stop and the solver orders them among themselves.
    return problems
