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

- **PR:** https://github.com/Lpk78/quai/pull/25 (reviewer: `SamDana-maker`)
- **What the AI produced:** the six backfilled records in `prompts/dev/` — `LP-01`, `LP-02`, `LP-03`,
  `LP-04b`, `LP-04c`, `LP-04d` — and the `failures.md` entry on the prompt that could not be recovered. It
  read every session file under
  `~/.claude/projects/-Users-leo-paulkerrinckx-Desktop-data-project/` and all 384 entries of
  `~/.claude/history.jsonl`, and cross-checked each prompt against the commits, PRs and issues it produced
  before writing an Outcome. The other three directories under `~/.claude/projects/` are ruled out by
  date rather than by reading — see the table in `LP-02`.
- **What was changed by hand:** nothing in the backfill itself — the review round below is where the
  by-hand changes are. Three points were decided rather than guessed and are flagged for the reviewer:
  - `LP-02` is deliberately incomplete. The prompt that wrote the solver is older than any session kept on
    this machine, so the file records that, with the evidence, instead of a reconstructed prompt.
  - `LP-04b` / `LP-04c` / `LP-04d` keep the letter suffix asked for in the prompt, even though the ID
    grammar documented in `CLAUDE.md` and in the task skill is `LP-nn` — the suffix is now explained in
    `prompts/README.md`, so the two agree. They are separate files because they are separate tasks on
    three different branches, not extra rounds of `LP-04` / PR #14.
  - Step 3 of the task skill wants the prompt file committed first and alone on the branch. That cannot
    hold for a backfill, so only `LP-16`'s own file follows it; the six others are the work itself.
- **Verified:** every prompt is quoted from the session history, not from memory. Every commit hash, PR
  number, issue number and timestamp in the six files was checked against `git log`, `gh pr view` and
  `gh issue view` — one claim was wrong on the first pass (that PR #3 closed #5; it never carried a
  `Closes`, and #5 was closed by hand at `2026-09-30T09:44:19Z`, after #3 merged at
  `2026-09-30T08:11:08Z`) and was corrected in `9cad3cd`.
  `python -m unittest discover tests` → 30 tests, OK when the backfill was written; the branch head runs
  **108** since `main` was merged in, all passing. No code changed on this branch at any point.

## Outcome of the review round (#25)

- **What the review asked for:** two blocking points and two optional ones. `documentation/failures.md`
  conflicted with `main`, because this branch and #21 both appended an entry to the same last line; the
  `#5` bullet said "33 minutes after the merge" where the real gap is `1:33:11`; the letter-suffix
  convention was undocumented; and `LP-02`'s claim about *this machine* rested on a search recorded as
  one directory.
- **What the AI produced:** the merge of `main` with both `failures.md` entries kept in date order
  (`c7360fa`), the `#5` bullet restated as the two timestamps with the arithmetic left to the reader
  (`ea9e60a`), the suffix paragraph in `prompts/README.md` (`43c0506`), this section, and the clause in
  `LP-02` naming the other project directories.
- **What was changed by hand:** which of the two offered wordings to take for `#5`. "1 h 33 min after the
  merge" was the simpler edit and was rejected: in the one PR whose value is that its records are
  re-derivable, a relative figure has to be taken on faith, and it is the shape that produced the error
  in the first place. The two timestamps say the same thing and can be checked against `gh`.
- **Verified:** 108 tests pass on the branch head. Both timestamps re-derived from `gh pr view 3` and
  `gh issue view 5`. The four directories under `~/.claude/projects/` were listed and their earliest
  session timestamps read, which is what the `LP-02` clause below now records.
- **Not changed, and why:** nothing was added to `documentation/ai_usage.md`. The review asks that the
  `LP-02` gap appear in that table; the table is filled once at the end of the project from the files in
  `prompts/dev/`, so a row written now would be the thing #20 removed. It belongs to whoever fills it.

