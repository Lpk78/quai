# LP-10 — Fourth constraint-translation prompt (v4 few-shot)

- **ID**: LP-10
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `prompt/constraint-translation-v4-few-shot`
- **Issue**: #12 (roadmap row 10)

## Prompt as typed

```
/prompt-version constraint translation, v4 few-shot: add 3 to 4 worked examples covering the
unresolved cases v3 failed (an unknown item, a weight without a unit, an ambiguous reference like
"the heavy one", a sentence with no loading constraint at all). The examples must be new sentences
with different items and wording — never one of the 26 test sentences or a close paraphrase; add a
test that checks no example matches a test sentence. Change nothing else from v3.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/40 (reviewer: `SamDana-maker`)
- **What the AI produced:** `prompts/constraint-translation/v4_few_shot.md`,
  `tests/test_prompt_examples.py`, the results row and the per-sentence analysis in
  `documentation/prompt_evaluation.md`, and the `documentation/failures.md` entry.
- **What was changed by hand:** the shape of Example 1. The obvious way to teach T20's lesson is to
  write T20 with the nouns swapped — `keep_upright` plus an unknown item asked not to be stacked.
  That is the thing the task forbids, and it would have made the row meaningless. Example 1 is
  `at_bottom` plus an unknown item asked to be kept upright: the same decision, a different sentence.
  It is also the example that caused the regression, which is worth noting next to the care taken
  over it.
- **The guard is mechanical, not a promise.** `tests/test_prompt_examples.py` checks every version
  file in every family: no example is a test sentence once punctuation is stripped, none shares more
  than half its words with one, and none binds a lesson to a real `B` item. The four examples peak at
  **0.29** word overlap against the 26. Two further tests check the guard itself fails on a planted
  sentence and on a reworded one, since exact matching alone would miss the second. Mutation-tested:
  planting T14 as an example fails two tests.
- **Verified:** 310 tests pass. The run is real — 78 calls at temperature 0 on the same model and the
  same delivery as v3, so the rows compare. **22/26**, up from 21.
- **The result is not the number.** Two sentences fixed (T20, T14), one broken (T13, which passed on
  v3), three unmoved (T10, T16, T17). Example 1 fixed its target and over-generalised; Examples 2 and
  3 had no measurable effect at all. Written up per sentence in the document and in `failures.md`,
  because "+1, few-shot helps a bit" is the wrong conclusion in both directions.
- **Judgement call for the reviewer:** whether T16 and T17 are still prompt failures. Four versions
  have not moved them, and v4's answers are defensible readings rather than mistakes — T16 calls "load
  the appliances together" `out_of_scope`, which is arguable. Before a v5, the rubric's expectations
  for those two are worth re-reading against what an operator would accept. Raised in the PR.
