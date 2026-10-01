"""Score one prompt version on the fixed test inputs and print the result.

Run from the repository root:

    python3 src/evaluate_prompt.py prompts/constraint-translation/v1_zero_shot.md

The inputs, the reference manifest and the rubric all come from
`documentation/prompt_evaluation.md`, so every version is scored on the same 26 sentences with the
same eight criteria. The key and the model both come from `.env` (`ANTHROPIC_API_KEY`, `LLM_MODEL`);
neither is guessed. With either one missing the script says so and prints no scores: a row in the
results table means a run that actually happened, on the model the row names.

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

# A version file carries its task, its expected output and its change log around the prompt. None of
# that may reach the model: a change log says what a version was written against and often names the
# test sentences it found hard, so sending the whole file would score a prompt that had been shown
# the answers. These mark what is actually sent.
PROMPT_START = "<!-- PROMPT START -->"
PROMPT_END = "<!-- PROMPT END -->"

# Where a documented version file lives. Anything under here must carry the markers: these files are
# required to have a change log, and a change log names the sentences a version found hard.
VERSIONS = pathlib.Path(__file__).resolve().parents[1] / "prompts"


def is_version_file(path: pathlib.Path) -> bool:
    """Whether `path` is a product prompt version — `prompts/<family>/v2_output_format.md`.

    `prompts/dev/` is excluded: those are development task records, never sent to a model.
    """
    try:
        inside = path.resolve().relative_to(VERSIONS)
    except ValueError:
        return False
    return len(inside.parts) == 2 and inside.parts[0] != "dev"


def prompt_text(path: pathlib.Path) -> str:
    """The system prompt inside a version file: what lies between the markers.

    A file under `prompts/<family>/` must carry both markers. It is required to document its own task
    and change log, so sending it whole would score a prompt that had been shown the sentences it was
    written against — and unlike a half-open marker that fails loudly, a file with no markers at all
    would do it silently and produce a plausible score. Suggested by the review of #30.

    A file anywhere else with no markers is sent whole, which is what a bare prompt file is. An
    opening marker with no closing one is always refused rather than guessed at.
    """
    text = path.read_text(encoding="utf-8")
    if PROMPT_START not in text:
        if is_version_file(path):
            raise SystemExit(
                f"{path}: a version file must mark its prompt with {PROMPT_START} and {PROMPT_END}, "
                "so that its change log is not sent to the model")
        return text
    body = text.split(PROMPT_START, 1)[1]
    if PROMPT_END not in body:
        raise SystemExit(f"{path}: {PROMPT_START} is never closed by {PROMPT_END}")
    return body.split(PROMPT_END, 1)[0].strip()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompt", type=pathlib.Path,
                        help="the prompt version to score, e.g. prompts/<family>/v1_zero_shot.md")
    parser.add_argument("--cases", default="",
                        help="comma-separated case ids to run instead of all 26 (partial run)")
    parser.add_argument("--runs", type=int, default=evaluation.RUNS,
                        help=f"calls per sentence, to measure how much the output varies "
                             f"(default {evaluation.RUNS})")
    parser.add_argument("--model", default=None,
                        help="override LLM_MODEL from .env, recorded in the results row")
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
        "runs_per_sentence": run.runs,
        "complete": run.complete,
        "cases": [{"id": case.case_id,
                   "verdicts": case.verdicts,
                   "passes": case.passes,
                   "identical": case.identical,
                   "match": case.match,
                   "attempts": [{"verdicts": a.verdicts, "match": a.match, "notes": list(a.notes),
                                 "error": a.error, "output": a.output} for a in case.attempts]}
                  for case in run.cases],
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
    except llm.NotConfigured as missing:
        print(f"Not run: {missing}.", file=sys.stderr)
        print("The results table keeps its empty row until a run happens.", file=sys.stderr)
        return 1

    version = args.prompt.stem
    print(f"Scoring {version} on {len(cases)} of {len(rubric.cases(text))} sentences, "
          f"{args.runs} runs each, with {translator.model} at temperature "
          f"{evaluation.temperature_cell(translator.temperature)}\n")

    def report(case):
        if not case.ran:
            print(f"  {case.case_id}: could not be run ({case.error})")
            return
        answered = f"{case.passes}/{len(case.attempts)} runs"
        state = "all eight" if case.passed else "NO on " + ", ".join(case.failed_criteria())
        wandered = "" if case.identical else ", and the runs disagreed"
        print(f"  {case.case_id}: {state} ({answered}{wandered})")

    try:
        scored = evaluation.run(translator.translate, prompt_text(args.prompt),
                                cases, manifest, manifest_text, runs=args.runs, on_case=report)
    except llm.FatalCall as fatal:
        print(f"\nStopped: {fatal}", file=sys.stderr)
        print("Nothing is scored from a run that could not be made.", file=sys.stderr)
        return 1

    run = evaluation.Run(version=version, model=translator.model, cases=scored,
                         expected_cases=len(rubric.cases(text)), runs=args.runs,
                         temperature=evaluation.temperature_cell(translator.temperature))

    print(f"\n{run.case_table()}\n")
    counts = run.per_criterion()
    print("  ".join(f"{name} {counts[name]}/{len(scored)}" for name in evaluation.CHECKS))
    print(f"Total (all eight yes on every run): {run.total()}/{len(scored)}")
    print(f"Same answer on every run: {run.identical()}/{len(scored)}      "
          f"Matched the expected output: {run.matched()}/{len(scored)}")

    if not args.no_transcript:
        print(f"\nReplies written to {write_transcript(run, TRANSCRIPTS)}")

    if partial:
        print("\nPartial run: no results row. Run all 26 sentences to record a score.")
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
