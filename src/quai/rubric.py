"""Read the rubric document: the reference manifest, the contract and the 25 test inputs.

`documentation/prompt_evaluation.md` is the single source of truth for what a prompt version is
scored on. Reading it, rather than copying the manifest and the 25 expected outputs into Python,
is what keeps scores comparable between versions: there is one place where a test input can be
corrected, and `tests/test_evaluation_inputs.py` fails if that place stops agreeing with itself.

The parsers here were written for `tests/test_evaluation_inputs.py` (LP-04) and moved into the
package when the evaluation script needed the same readings, so that the two cannot drift apart.
"""
import json
import pathlib
import re
from dataclasses import dataclass

from quai.constraints import Manifest

DOC = pathlib.Path(__file__).resolve().parents[2] / "documentation" / "prompt_evaluation.md"

EXPECTED_SENTENCES = 25


@dataclass(frozen=True)
class Item:
    """One row of the reference manifest, as the document writes it."""
    id: str
    label: str
    dimensions: str
    weight: str


@dataclass(frozen=True)
class Case:
    """One test input: what the operator says, and the JSON a version is scored against."""
    id: str
    sentence: str
    expected: dict


def read_doc(path: pathlib.Path = DOC) -> str:
    return path.read_text(encoding="utf-8")


def manifest_ids(text: str) -> set:
    return set(re.findall(r"^\| `(B\d+)` \|", text, re.MULTILINE))


def stop_ids(text: str) -> set:
    return set(re.findall(r"`(S\d+)`", _route_line(text)))


def route(text: str) -> tuple[str, ...]:
    """The stops in route order, which `stop_ids` cannot give: it returns a set.

    The line names the last stop twice — once in the list, once to insist it is last — so
    repeats are dropped with the first mention winning (see `documentation/failures.md`).
    """
    return tuple(dict.fromkeys(re.findall(r"`(S\d+)`", _route_line(text))))


def stop_names(text: str) -> dict[str, str]:
    """Stop id -> the place the operator would say, e.g. `S2` -> "Le Havre"."""
    pairs = re.findall(r"`(S\d+)`\s+([A-Z][A-Za-z' -]*?)(?=,|\s+—|\s+in that|$)",
                       _route_line(text))
    named: dict[str, str] = {}
    for stop, name in pairs:
        named.setdefault(stop, name)  # the line names the last stop twice; the first wins
    return named


def _route_line(text: str) -> str:
    return re.search(r"^Stops on the route: (.+)$", text, re.MULTILINE).group(1)


def items(text: str) -> tuple[Item, ...]:
    rows = re.findall(r"^\| `(B\d+)` \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \|\s*$",
                      text, re.MULTILINE)
    return tuple(Item(*(cell.strip() for cell in row)) for row in rows)


def manifest(text: str) -> Manifest:
    """The load a translation is validated against: the item ids, and the stops in route order."""
    return Manifest(items=tuple(item.id for item in items(text)), stops=route(text))


def table_rows(text: str, header: str) -> list[list[str]]:
    """Rows of the one Markdown table introduced by `header`, as lists of cell strings.

    Reading a named table instead of every `| ... |` line in the document is what keeps the
    manifest rows (`| `B1` | washing machine | ... |`) out of the constraint contract.
    """
    rows = []
    for line in text.split(header)[1].splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if rows:
                break  # the table has ended
            continue
        if set(line) <= set("|-: "):
            continue  # the |---|---| separator
        rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows


def constraint_fields(text: str) -> dict[str, set]:
    """Map constraint name -> required fields, from the contract table."""
    return {
        row[0].strip("`"): set(re.findall(r"`(\w+)`", row[1]))
        for row in table_rows(text, "| Constraint | Fields | Meaning |")
    }


def reasons(text: str) -> set:
    return {row[0].strip("`") for row in table_rows(text, "| `reason` | Used when |")}


def criteria(text: str) -> tuple[str, ...]:
    """The rubric's criteria in document order, e.g. `("C1", ..., "C7")`."""
    return tuple(row[0] for row in table_rows(text, "| # | Criterion | Yes when |"))


def sentences(text: str) -> list[tuple[str, dict]]:
    """Return [(id, parsed_json)] for every test sentence."""
    return [(case.id, case.expected) for case in cases(text)]


def cases(text: str) -> tuple[Case, ...]:
    """Every test input in document order: the sentence said, and the JSON expected of it."""
    body = text.split("## Test inputs")[1].split("## Results")[0]
    # The sentence is one line, so it is matched with [^\n]+ rather than .+ : DOTALL is on for
    # the JSON block, and a dot that crosses newlines would swallow the whole section.
    found = re.findall(r'^\*\*(T\d+)\*\* — "([^\n]+)"\s*\n```json\n(.*?)\n```',
                       body, re.MULTILINE | re.DOTALL)
    return tuple(Case(tid, sentence, json.loads(block)) for tid, sentence, block in found)
