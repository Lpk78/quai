"""Score one prompt version on the fixed test inputs and print the result.

Run from the repository root:

    python3 src/evaluate_prompt.py prompts/constraint-translation/v1_zero_shot.md

The inputs, the reference manifest and the rubric all come from
`documentation/prompt_evaluation.md`, so every version is scored on the same 25 sentences with the
same seven criteria. The key comes from `.env`. With no key the script says so and prints no
scores: a row in the results table means a run that actually happened.

`--cases T01,T25` runs a subset while working on a prompt. Such a run is marked partial and gets no
results row, on purpose — a score over part of the inputs is not comparable with anything.
"""
import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from quai import evaluation, llm, rubric  # noqa: E402

TRANSCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "outputs" / "evaluations"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompt", type=pathlib.Path,
                        help="the prompt version to score, e.g. prompts/<family>/v1_zero_shot.md")
    parser.add_argument("--cases", default="",
                        help="comma-separated case ids to run instead of all 25 (partial run)")
    parser.add_argument("--model", default=None,
                        help="override the model from .env, recorded in the results row")
    parser.add_argument("--no-transcript", action="store_true",
                        help="do not write the replies to outputs/evaluations/")
    return parser.parse_args(argv)


def chosen_cases(all_cases, wanted: str):
    if not wanted:
        return all_cases, False
    ids = [name.strip() for name in wanted.split(",") if name.strip()]
    known = {case.id: case for case in all_cases}
    unknown = [name for name in ids if name not in known]
    if unknown:
        raise SystemExit(f"no such test sentence: {', '.join(unknown)}")
    return tuple(known[name] for name in ids), True


def write_transcript(run: evaluation.Run, folder: pathlib.Path) -> pathlib.Path:
    """Keep every reply, so a score can be re-read later without calling the model again."""
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = folder / f"{run.version}_{stamp}.json"
    path.write_text(json.dumps({
        "version": run.version,
        "model": run.model,
        "temperature": run.temperature,
        "date": datetime.date.today().isoformat(),
        "complete": run.complete,
        "cases": [{"id": s.case_id, "verdicts": s.verdicts, "match": s.match,
                   "notes": list(s.notes), "error": s.error, "output": s.output}
                  for s in run.scored],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def main(argv=None) -> int:
    args = parse_args(argv)
    if not args.prompt.is_file():
        print(f"no prompt file at {args.prompt}", file=sys.stderr)
        return 2
    text = rubric.read_doc()
    manifest = rubric.manifest(text)
    manifest_text = llm.manifest_block(rubric.items(text), rubric.stop_names(text))
    cases, partial = chosen_cases(rubric.cases(text), args.cases)

    try:
        translator = llm.from_env(args.model)
    except llm.MissingKey as missing:
        print(f"Not run: {missing}.", file=sys.stderr)
        print("The results table keeps its empty row until a run happens.", file=sys.stderr)
        return 1

    version = args.prompt.stem
    print(f"Scoring {version} on {len(cases)} of {len(rubric.cases(text))} sentences "
          f"with {translator.model}\n")

    def report(scored):
        state = "could not be run" if not scored.ran else ("all seven" if scored.passed
                                                          else "NO on " + ", ".join(
                                                              scored.failed_criteria()))
        print(f"  {scored.case_id}: {state}")

    scored = evaluation.run(translator.translate, args.prompt.read_text(encoding="utf-8"),
                            cases, manifest, manifest_text, on_case=report)
    run = evaluation.Run(version=version, model=translator.model, scored=scored,
                         expected_cases=len(rubric.cases(text)))

    print(f"\n{run.case_table()}\n")
    counts = run.per_criterion()
    print("  ".join(f"{name} {counts[name]}/{len(scored)}" for name in evaluation.CHECKS))
    print(f"Total (all seven yes): {run.total()}/{len(scored)}      "
          f"Matched the expected output: {run.matched()}/{len(scored)}")

    if not args.no_transcript:
        print(f"\nReplies written to {write_transcript(run, TRANSCRIPTS)}")

    if partial:
        print("\nPartial run: no results row. Run all 25 sentences to record a score.")
        return 0
    if not run.complete:
        print("\nNo results row: " + ", ".join(f"{s.case_id} ({s.error})"
                                               for s in run.could_not_run()))
        return 1
    print("\nRow for the Results table of documentation/prompt_evaluation.md:")
    print(run.results_row(datetime.date.today().isoformat()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
