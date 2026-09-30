# LP-06 — Script scoring a prompt version on the fixed inputs

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-30
- **Branch:** `feature/prompt-evaluation`
- **Issue:** #11

## Prompt as typed

```
git switch feature/constraint-schema, then start LP-06 from there (it needs src/quai/constraints.py
from PR #21, not merged yet) and open its PR against main, noting in the PR body that it depends on
#21 and must be merged after it.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/22
- **Branched off #21, not `main`:** asked for explicitly, and necessary — C1 of the rubric is
  `quai.constraints.parse()`, which is #21. The PR body says it depends on #21 and must be merged
  after it, and `documentation/roadmap.md` records the same.
- **What the AI produced:** `src/quai/rubric.py` (the document reader), `src/quai/evaluation.py`
  (the seven criteria as checks, plus `Run` and the results row), `src/quai/llm.py` (one call per
  sentence, key from `.env`), `src/evaluate_prompt.py` (the command), 73 new tests across
  `tests/test_rubric.py`, `tests/test_evaluation.py`, `tests/test_llm.py` and
  `tests/test_evaluate_prompt.py`, the *Running an evaluation* section of
  `documentation/prompt_evaluation.md`, the README command, and the `anthropic` line in
  `requirements.txt`.
- **What was changed by hand:** the parsers were moved out of `tests/test_evaluation_inputs.py`
  into the package rather than copied, because two readings of the same document drift and a drifted
  reading silently corrupts every score; that test file now imports them and its assertions are
  untouched. Scoring was split from the API call so the whole harness could be exercised offline on
  outputs written by hand. Three judgement calls were changed after thinking about what a criterion
  is for: a sentence that could not be translated is scored on *no* criterion instead of seven No's,
  `results_row()` now raises rather than returning a row for an unfinished run, and the reply is
  asked for as plain text instead of being constrained to the schema server-side — which would have
  made C1 true by construction and measured nothing.
- **What the rubric cannot say, and what was not done about it:** a version that silently drops a
  constraint the operator did say answers Yes to all seven criteria. The script therefore records per
  sentence whether the output *matched* the expected one and prints that count, but no eighth column
  was added to the results table: changing the rubric is the reviewer's call and has to happen before
  any version is scored, not after. Raised in the PR.
- **Contract problem found:** the results table asks for the temperature used, and the current Claude
  models reject `temperature` outright. The script sends no sampling parameter and the column records
  `n/a` — what was actually used — rather than a number nobody sent. Raised in the PR.
- **Not run:** no scores. There is no prompt version yet (that is #12, row 10 of the roadmap) and
  `anthropic` is not installed on this machine, so no call was made and
  `documentation/prompt_evaluation.md` keeps its empty `v1_zero_shot` row. The no-key path was
  exercised: it says why and prints nothing.
- **Verified:** 163 tests pass (2 skip without `anthropic` installed; they run on the CI, which
  installs `requirements.txt`). Neutralising any one of the seven checks makes between 2 and 5 tests
  fail. The rubric's own 25 expected outputs score all seven Yes and match — a necessary property,
  since they are what every version is compared against.
