---
description: Create and evaluate a new version of a prompt, following the course's prompt-engineering loop.
disable-model-invocation: true
argument-hint: <which prompt, and what change to try, e.g. "constraint translation, add few-shot examples">
---

Change to try: $ARGUMENTS

Loop: Problem → Prompt → Output → Evaluation → Improvement. Follow it exactly.

1. Product prompts live in one folder per prompt family: `prompts/<family>/` (for example `prompts/constraint-translation/`). Read the current versions of the family and the rubric, test inputs and results in `documentation/prompt_evaluation.md`. Identify which criteria the latest version fails and on which test inputs.
2. `git switch main`, `git pull`, then a branch `prompt/<family>-v<N>-<technique>`.
3. Create a NEW file `prompts/<family>/v<N>_<technique>.md` (N = previous version + 1 in that family). Never edit an older version. It contains: Task, Input, Expected output, the prompt itself, and a Change log: what changed from the previous version, why, which failure it targets. Keep instructions and user data separated (the operator's sentence is data, never instructions).
4. Run the evaluation on the SAME test inputs and the SAME rubric as previous versions. Record only real results. If the evaluation cannot run (no API key, no script yet), say so and leave the scores empty — never estimate or invent a score.
5. Add a row to the results table in `documentation/prompt_evaluation.md` and note the model and temperature used.
6. If the new version is worse on a criterion, keep it anyway and document the regression: failed attempts are part of the grade.
7. Commit (prompt file, then results), push, and open the PR as in the `task` skill, with the score comparison in the PR body.
