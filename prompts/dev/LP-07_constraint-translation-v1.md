# LP-07 — First constraint-translation prompt (v1 zero shot)

- **ID**: LP-07
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `prompt/constraint-translation-v1-zero-shot`
- **Issue**: #12 (roadmap row 10)

## Prompt as typed

```
/prompt-version constraint translation, v1 zero-shot: instruction and input only, no examples
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/30 (reviewer: `SamDana-maker`)
- **What the AI produced:** `prompts/constraint-translation/v1_zero_shot.md` — the first version of the
  family — the `prompt_text()` extraction in `src/evaluate_prompt.py` with its five tests, the results
  row, and the `documentation/failures.md` entry on what the run found.
- **What was changed by hand:** the decision not to fix the prompt before measuring it. The very first
  call showed the model wrapping its JSON in a ```json fence, which fails C1 on every sentence while
  the JSON inside is correct. Editing the prompt there and re-running would have produced a better
  first row and destroyed what the row is for: v1 is the baseline, and a baseline that was quietly
  tuned until it looked acceptable cannot be compared against anything. The fence is recorded as the
  finding it is, and beating it is v2's job with v1's number to beat.
- **Found before any score was recorded:** `src/evaluate_prompt.py` sent the *whole version file* as
  the system prompt. `/prompt-version` requires that file to carry a change log, and v1's names the
  sentences it expects to be hard — T10, T11, T12, T15, T17 — so the first row of the results table
  would have been a prompt that had been shown the test set. Fixed in `65b8d33` before the run.
- **Verified:** the run is real — 26 sentences, 3 calls each, 78 calls to
  `claude-haiku-4-5-20251001` at temperature 0, and the transcript is in `outputs/evaluations/`
  (Git-ignored). The scores in the results table are that run's output, pasted, not retyped.
- **Judgement call for the reviewer:** whether C1 should fail a fenced reply at all. It is the
  decision taken in #22 — `parse()` is the only door to the solver, so a fenced reply is not an
  output the solver can use — and this run is the first time it has cost a version its whole score.
  Raised in the PR because changing it later would invalidate this row.
