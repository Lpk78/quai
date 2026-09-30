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

### Second prompt, same task, after the PR was opened

```
LP-06 #12 Add src/evaluate_prompt.py: it runs one prompt file from prompts/constraint-translation/
on every test sentence of documentation/prompt_evaluation.md through the Claude API, reading the key
from the ANTHROPIC_API_KEY variable and the model from LLM_MODEL in .env (update .env.example with
both names, without any value), temperature 0; it retries with exponential backoff on 429 and 5xx
and fails fast on 400 and 401; it runs each sentence 3 times to measure how much the output varies,
validates each output with src/quai/constraints.py, scores it against the rubric C1-C7
automatically, prints a results table and saves the raw outputs in outputs/. Use a mocked API in the
tests so they run without a key.
```

Then, mid-task:

```
Also add an entry to documentation/failures.md: the course material uses temperature 0 for
repeatable outputs, but current Claude models reject the temperature parameter with a 400; we
measure output variability with 3 runs per sentence instead, and record temperature as n/a.

For the results table, a sentence counts as passed only if all 3 runs pass all seven criteria; also
show, per sentence, how many of the 3 runs passed, so the variability is visible.
```

That second prompt described `src/evaluate_prompt.py` as a new file and named issue #12, but the
script already existed in this PR and #12 is the first prompt version (roadmap row 10, created by
`/prompt-version`). Rather than start a second LP-06 on a second branch from `main` — which would
have duplicated a file under review and guaranteed a conflict — the work was checked with the author
first and added here. Three things in it were genuinely new: the retry policy, the three runs, and
the key rename.

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

## Outcome of the second round

- **What the AI produced:** the retry policy in `src/quai/llm.py` (exponential backoff over four
  attempts on 408/409/429 and 5xx, honouring `retry-after`; `FatalCall` on 400/401/403/404, which the
  runner does not catch), `CaseRuns` and the three-runs-per-sentence logic in `src/quai/evaluation.py`
  with the `Runs` and `Same` columns, the `--runs` option and the fuller transcript in
  `src/evaluate_prompt.py`, the `ANTHROPIC_API_KEY` rename across the package, `.env.example`, the
  README and the tests, 25 more tests, and the two documentation entries.
- **What was changed by hand:** four things were decided rather than typed. `temperature 0` was
  dropped instead of sent, because the current models reject it with a 400 and the script is also
  meant to fail fast on a 400 — sent as asked it would have failed on its first call, 75 times over;
  this was checked with the author before writing anything. The task named issue #12 and a new file,
  both wrong — #12 is the prompt version and the file already existed in this PR — so the work landed
  on this branch instead of duplicating a file under review. `FatalCall` was deliberately made *not*
  a subclass of `CallFailed`, so the runner cannot record a bad key against one sentence and carry on
  through the other 24. And the SDK client is built with `max_retries=0`, so the backoff written here
  is the only one and can actually be observed in a test.
- **Judgement call for the reviewer:** a criterion is Yes for a sentence only when all three runs say
  Yes. The alternatives were best-of-three (flattering) and majority (hides a third of the failures).
  It changes what a rubric column means, so it has to be settled before v1 is measured; raised in the
  PR.
- **Not run:** still no scores. There is no prompt version to run yet (#12), and none was invented.
- **Verified:** 188 tests pass. `anthropic` was installed in a local `.venv` so that the 14 tests
  needing it — the retry, backoff and fail-fast tests — actually ran here rather than being left to
  the CI. No test makes a network call: the API is a stand-in replaying scripted 429s, 503s, 400s and
  dropped connections, and the backoff is checked by recording the waits instead of sleeping.

## Outcome of the third round: C8

- **Why:** the review of #21 is where this came from. C3 ("nothing invented") subtracts the expected
  constraints from the given ones, so it only ever catches an invention. Nothing in the rubric looked
  the other way, and the LP-06 notes above had already recorded the consequence as a known gap covered
  by `match` alone: a version that answers T20 with the `unknown_item` and drops "keep the washing
  machine upright" scored Yes on all seven criteria. C8 closes it.
- **What the AI produced:** the C8 row and its paragraph in `documentation/prompt_evaluation.md`,
  `_c8_nothing_missing` in `src/quai/evaluation.py`, the results-row and per-sentence-table column, the
  counts moved to eight criteria and 26 sentences across the module, `src/evaluate_prompt.py`, the
  README and the tests, and `tests/test_evaluation.TestC8NothingMissing`.
- **What was changed by hand:** what `match` is now for. It was justified in the code and in the
  document as covering the gap C8 now covers, so the docstring and the document had to say what it
  still adds instead — the count of `unresolved` entries, which no criterion compares — and a test was
  written for that (T17 has two faults; answering with one is Yes everywhere and matches nothing).
  `rubric.criteria()` needed no change: it reads the rubric table, so it picked C8 up on its own, which
  is the point of reading the document instead of copying it.
- **Verified:** 195 tests pass. Neutralising `_c8_nothing_missing` fails four of them. The rubric's own
  26 expected outputs still score all eight Yes and match, which is the property every score depends
  on.
