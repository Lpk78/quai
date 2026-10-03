# SA-06 — Measuring what happens when the LLM places the boxes itself

- **Author:** `SamDana-maker` (Sam)
- **Date:** 2026-10-01
- **Branch:** `experiment/llm-only-placement`
- **Issue:** none — roadmap *Later* row `experiment/llm-only-placement`

## Prompt as typed

```
/task SA-06 Run experiment/llm-only-placement: ask Claude (LLM_MODEL from .env) to place the demo
boxes directly as coordinates, 10 runs at temperature 0 and 10 at temperature 1, score each with
src/quai/checks.py (overlaps, out of bounds, unsupported boxes, differences between runs), compare
with the solver in notebooks/llm_vs_solver.ipynb (exploration only) and document the results in
documentation/failures.md
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/38 (reviewer: `MORHI11`)
- **What the AI produced:** `src/quai/llm_placement.py` (the prompt, the parsing, the scoring through
  `quai.checks.find_problems()`), `src/run_placement_experiment.py`, 19 tests in
  `tests/test_llm_placement.py`, `notebooks/llm_vs_solver.ipynb`, and the `failures.md` write-up.
- **What was changed by hand:** two decisions, both argued in the code rather than left implicit.
  A code fence is stripped before parsing — the opposite of what the rubric does for C1 — because here
  the envelope is not what is being measured and failing all twenty runs on a Markdown habit would
  answer a different question. And the model is given the same facts `solve()` works from and no worked
  example, so the experiment measures placing rather than copying.
  The conclusion was also rewritten after reading the data: the first draft said the model simply cannot
  place boxes, which the numbers do not support. It places all eleven in 17 runs of 20 and its one valid
  plan beat the solver. The honest finding is narrower — fluent about structure, unreliable about
  constraint arithmetic — and that is what the entry now says.
- **Verified:** 311 tests pass. Every figure in `failures.md` was re-derived from the stored transcript
  and compared against what was written: the per-kind counts (41 unsupported, 41 rotation, 20 overlap,
  5 outside, 3 not placed), the 17 runs placing all eleven, and the single valid plan. That plan was
  re-scored independently — 11/11 placed, all upright, minimum support 0.81, no problems, 46.9 % fill
  against the solver's 39.3 %. The notebook executes end to end and is committed with no stored outputs.
- **What the experiment cost:** 20 billed calls to `claude-haiku-4-5-20251001`, plus 2 in a rehearsal.
