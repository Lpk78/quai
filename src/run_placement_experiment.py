"""Ask the model to place the demo load itself, twenty times, and score what comes back.

Run from the repository root:

    python3 src/run_placement_experiment.py              # 10 runs at temperature 0, 10 at 1
    python3 src/run_placement_experiment.py --runs 2     # a short rehearsal

This is `experiment/llm-only-placement` (SA-06). It is not on the product path: it exists so that
"the LLM never computes placement" is a measured conclusion rather than an assumption. Every reply
is written to `outputs/placement/` (Git-ignored) so the numbers in `documentation/failures.md` can
be re-derived without paying for the calls again.
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from demo import BOXES, VAN  # noqa: E402
from quai import llm, llm_placement, solver  # noqa: E402

OUTPUT = pathlib.Path(__file__).resolve().parents[1] / "outputs" / "placement"
TEMPERATURES = (0.0, 1.0)
RUNS = 10


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=RUNS,
                        help=f"runs per temperature (default {RUNS})")
    parser.add_argument("--model", default=None, help="override LLM_MODEL for this run")
    return parser.parse_args(argv)


def one_run(translator, temperature: float) -> llm_placement.Attempt:
    """One call, scored. A call that fails is an attempt that did not parse, not a crash."""
    import dataclasses
    asked = dataclasses.replace(translator, temperature=temperature)
    try:
        reply = asked.translate(llm_placement.SYSTEM_PROMPT,
                                llm_placement.load_description(BOXES, VAN), "")
    except llm.CallFailed as failure:
        return llm_placement.Attempt(raw="", placements=(), problems=(),
                                     parse_error=f"the call failed: {failure}")
    return llm_placement.score(reply, BOXES, VAN)


def summarise(attempts: list[llm_placement.Attempt]) -> dict:
    """The row for one temperature: how many answered, how many were valid, how much they vary."""
    parsed = [a for a in attempts if a.parsed]
    valid = [a for a in parsed if a.valid]
    signatures = {a.signature for a in parsed}
    kinds = {}
    for attempt in parsed:
        for problem in attempt.problems:
            kind = ("not placed" if "was not placed" in problem
                    else "overlap" if "overlaps" in problem
                    else "outside" if "outside" in problem
                    else "unsupported" if "supported" in problem
                    else "rotation" if "rotation" in problem
                    else "other")
            kinds[kind] = kinds.get(kind, 0) + 1
    return {"runs": len(attempts), "parsed": len(parsed), "valid": len(valid),
            "distinct_plans": len(signatures), "problems_by_kind": kinds,
            "problems_per_parsed_run": round(
                sum(len(a.problems) for a in parsed) / len(parsed), 2) if parsed else None}


def main(argv=None) -> int:
    args = parse_args(argv)
    try:
        translator = llm.from_env(args.model)
    except llm.NotConfigured as missing:
        print(f"Not run: {missing}", file=sys.stderr)
        return 1

    plan = solver.solve(BOXES, VAN)
    from quai.checks import find_problems
    print(f"Solver, for comparison: {len(plan.placements)}/{len(BOXES)} placed, "
          f"fill {plan.fill_rate:.0%}, problems {find_problems(plan.placements, VAN) or 'none'}")
    print(f"Model: {translator.model}\n")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    record, summaries = [], {}

    for temperature in TEMPERATURES:
        attempts = []
        print(f"temperature {temperature:g}:", end=" ", flush=True)
        for index in range(args.runs):
            attempt = one_run(translator, temperature)
            attempts.append(attempt)
            print("." if attempt.valid else ("x" if attempt.parsed else "?"), end="", flush=True)
            record.append({"temperature": temperature, "run": index + 1, "raw": attempt.raw,
                           "parse_error": attempt.parse_error,
                           "problems": list(attempt.problems),
                           "placed": len(attempt.placements)})
        summaries[temperature] = summarise(attempts)
        print(f"  {summaries[temperature]}")

    path = OUTPUT / f"llm_placement_{stamp}.json"
    path.write_text(json.dumps({"model": translator.model, "runs_per_temperature": args.runs,
                                "summaries": {str(k): v for k, v in summaries.items()},
                                "attempts": record}, indent=1), encoding="utf-8")
    print(f"\nReplies written to {path}")
    print("(. = a valid plan, x = parsed but broken, ? = did not parse)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
