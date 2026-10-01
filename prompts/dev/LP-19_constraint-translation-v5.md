# LP-19 — Fifth constraint-translation prompt (v5 bounded examples)

- **ID**: LP-19
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `prompt/constraint-translation-v5-bounded-examples`
- **Issue**: #12 (roadmap row 10)

## Prompt as typed

```
/prompt-version constraint translation, v5 bounded examples: start from v3 (not v4) and add only
v4's Example 3 (unclear subject → ambiguous, not out_of_scope), plus v4's Example 1 paired with a
bounding counter-example: a wholly ambiguous sentence with no resolvable part, answered with
unresolved and empty constraints. The counter-example must use A-items only and pass the
contamination guard (it cannot be T13 or a paraphrase of it). Replace the exact-count assertion in
tests/test_prompt_examples.py with "at least one example in any few-shot file". Run the full 78-call
evaluation and report per sentence against v3 and v4.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/43 (reviewer: `SamDana-maker`)
- **What the AI produced:** `prompts/constraint-translation/v5_bounded_examples.md`, the loosened
  assertion in `tests/test_prompt_examples.py`, the results row and per-sentence comparison in
  `documentation/prompt_evaluation.md`, and the `documentation/failures.md` entry.
- **What was chosen rather than typed:** the counter-example's shape. It had to teach T13's lesson —
  a clear constraint type with an ambiguous subject, so nothing may be bound — without being T13 or a
  paraphrase. Three candidates were scored against all 26 sentences before one was written into the
  prompt: "The delicate ones must not be laid flat." scores **0.13** against its nearest test sentence
  and **0.08** against T13, where "The awkward ones go in last." reached 0.18 and risked colliding
  with T06 and T26, which both say *load … last*. The guard was then mutation-tested by planting T13
  itself in that slot: two tests fail.
- **Why the test assertion was loosened, in the words that matter:** a count pinned to one file turns
  *dropping an example that measurably did nothing* into a test failure. v4 carried four and v5
  carries three on purpose. It now asserts that some version carries examples at all — so the
  contamination checks cannot pass vacuously — and that any file carrying them carries at least one.
- **Verified:** 310 tests pass. The run is real — 78 calls at temperature 0, same model and same
  delivery as v3 and v4, so all three rows compare.
- **The result, which is not the Total.** 21/26, the same number as v3 and one below v4, and the
  per-sentence diff says three separate things:
  - **T13 passes again.** The bound worked exactly as designed, which was this version's whole
    purpose.
  - **T06 and T24 fail for the first time**, having passed in v3 with no examples and in v4 with
    four. T06 manufactures doubt about the operator's own reason for a request; T24 returns two empty
    lists.
  - **T10, T16 and T17 are unmoved** by prose, by four examples and by three bounded ones.
- **What that cost and bought:** a controlled fix for one regression, and two new ones in the opposite
  direction. Written up in `failures.md` as the second half of v4's lesson — an example teaches the
  decision it shows *and* narrows what the model treats as a possible answer, so adding one changes
  the sentences it does not mention.
- **Judgement call for the reviewer:** whether this family should keep adding examples at all. Three
  example-based versions have each fixed their target and broken something else, and the Total has
  not moved past 22. Raised in the PR.
