# LP-16 — Backfill the development prompts given before `/task` existed

- **ID**: LP-16
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-09-30
- **Branch**: `docs/backfill-dev-prompts`

## Prompt as typed

```
/task LP-16 Backfill prompts/dev/ with the development prompts given before the /task skill existed:
LP-01 team automation setup, LP-02 solver, LP-03 roadmap issues, LP-04b addressing Sam's review on
PR #3, LP-04c issue #15, LP-04d addressing Sam's review on PR #4. Recover each prompt text from this
machine's Claude Code session history, mark each file "recorded afterwards", and link the resulting
PR or issue.
```

## Outcome

- **PR:** PR_URL_PLACEHOLDER (reviewer: `SamDana-maker`)
- **What the AI produced:** the six backfilled records in `prompts/dev/` — `LP-01`, `LP-02`, `LP-03`,
  `LP-04b`, `LP-04c`, `LP-04d` — and the `failures.md` entry on the prompt that could not be recovered. It
  read every session file under
  `~/.claude/projects/-Users-leo-paulkerrinckx-Desktop-data-project/` and all 384 entries of
  `~/.claude/history.jsonl`, and cross-checked each prompt against the commits, PRs and issues it produced
  before writing an Outcome.
- **What was changed by hand:** nothing yet. Three points were decided rather than guessed and are flagged
  for the reviewer:
  - `LP-02` is deliberately incomplete. The prompt that wrote the solver is older than any session kept on
    this machine, so the file records that, with the evidence, instead of a reconstructed prompt.
  - `LP-04b` / `LP-04c` / `LP-04d` keep the letter suffix asked for in the prompt, even though the ID
    grammar documented in three places is `LP-nn`. They are separate files because they are separate tasks
    on three different branches, not extra rounds of `LP-04` / PR #14.
  - Step 3 of the task skill wants the prompt file committed first and alone on the branch. That cannot
    hold for a backfill, so only `LP-16`'s own file follows it; the six others are the work itself.
- **Verified:** every prompt is quoted from the session history, not from memory. Every commit hash, PR
  number, issue number and timestamp in the six files was checked against `git log`, `gh pr view` and
  `gh issue view` — one claim was wrong on the first pass (that PR #3 closed #5; it never carried a
  `Closes`, and #5 was closed by hand 33 minutes after the merge) and was corrected in `9cad3cd`.
  `python -m unittest discover tests` → 30 tests, OK. No code changed.

