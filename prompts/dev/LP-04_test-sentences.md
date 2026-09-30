# LP-04 — Test sentences for constraint translation

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-28
- **Branch:** `docs/constraint-test-sentences`
- **Issue:** #9

## Prompt as typed

```
LP-04 — follow the /task process from the docs/team-automation branch (it is not on main yet):
from an up-to-date main, create branch docs/constraint-test-sentences, save this prompt in
prompts/dev/LP-04_test-sentences.md, then write 25 test sentences for constraint translation in
documentation/prompt_evaluation.md: include ambiguous sentences, unit traps (cm vs m, kg vs t),
references to items that do not exist, and one prompt injection attempt; give the expected JSON for
each and finalise the Yes/No rubric. Small commits, push, open a PR with SamDana-maker as reviewer.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/14
- **What the AI produced:** the reference manifest, the output contract (nine constraint types, six
  `unresolved` reasons), the 25 sentences with their expected JSON, the seven-criterion rubric, and
  `tests/test_evaluation_inputs.py`.
- **What was changed by hand:** the draft rubric in the repository stopped at C5 and scored nothing for
  the injection case or for the rule that the model never places a box, so C6 (speech is data) and C7
  (no placement) were added and the results table widened. C5 was made two-directional so that a version
  answering "ambiguous" to everything cannot score well. The expected outputs for T10 and T11 were made
  stricter on purpose and are flagged in the PR for the reviewer to confirm.
- **Verified:** 10/10 tests pass, and the checks were mutation-tested — an out-of-manifest item id and a
  dropped constraint in T25 were both caught.
