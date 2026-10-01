# LP-04b — Answering Sam's review on PR #3

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-30
- **Branch:** `feature/solver-v1`
- **Recorded afterwards:** yes — written on 2026-09-30 by `LP-16`. The `/task` skill writes a prompt file
  for a new task; this was a review round driven by direct prompts, so nothing was saved at the time. Text
  recovered from session `d41c63d9-…jsonl` and quoted as typed.
- **Note on the ID:** `LP-04b` / `LP-04c` / `LP-04d` were asked for by name in the `LP-16` prompt. The ID
  grammar documented in `CLAUDE.md`, `CONTRIBUTING.md` and the task skill is `LP-nn` with no letter suffix,
  and the existing habit for a later round of the same task (`LP-05`, `LP-06`) is an extra
  `## Outcome of the … round` section inside the one file. These three are kept as separate files because
  they are separate tasks on three different branches, not rounds of `LP-04` / PR #14.

## Prompt as typed

```
Address Sam's review on PR #3, on this branch feature/solver-v1. Read all review comments with gh pr view
3 --comments and gh api repos/Lpk78/quai/pulls/3/comments. List them for me, Blocking first, with what you
plan to do for each, and wait for my go. Then fix each point in its own small commit with a clear English
message: the blocking point is that checks.py must reject a placement whose dimensions are not an upright
rotation of the box's real dimensions, and a box placed twice; add tests for each case. Add a line to
documentation/ai_usage.md declaring that these commits were made with Claude Code. Run the tests, push,
and reply to each of Sam's comments on GitHub saying what changed or why not.
```

Session `d41c63d9-…jsonl`, 2026-09-30T07:57:54Z.

### Follow-up prompt, same task, after the plan was reviewed

```
Go. Do point 1 (fix + tests) and point 5 as planned. Include points 2 and 3 too, each in its own commit
with tests. For point 4, don't touch roadmap.md here: add the note on docs/roadmap-issues (PR #13) in a
separate commit, and tell Sam in your reply why it went there. Then run the tests, push both branches, and
reply to each of Sam's comments.
```

Session `d41c63d9-…jsonl`, 2026-09-30T07:59:43Z.

### Two `/fix-review 3` attempts came first

`~/.claude/history.jsonl` shows `/fix-review 3` typed twice, at 2026-09-30T07:57:07Z and 07:57:18Z, about
40 seconds before the prompt above. They left only an empty session stub
(`a2069ba2-…jsonl`, five lines, no assistant turn), which is why the task was then given as a direct
prompt that spells out the same steps by hand.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/3 (reviewer: `SamDana-maker`, approved 08:11:04Z and merged
  08:11:08Z on 2026-09-30, after having requested changes on 2026-09-29)
- **What the AI produced:** the review comments listed Blocking first with a plan per point, then five
  commits, one per point:
  - `9c0e252` reject placements that do not match the box they claim to be
  - `b492cf5` tests for shrunk, tipped and duplicated placements
  - `e0eed4c` refuse boxes with impossible dimensions or a negative weight
  - `f4b9566` define the minimum support ratio in one place
  - `8a421c0` declare the Claude Code help used on this branch
- **What was changed by hand:** the scope was cut back by the author twice. Point 4 was refused on this
  branch and moved to `docs/roadmap-issues` (PR #13) so PR #3 stayed about the checks it had been reviewed
  for — it became commit `18d02f5`, "Record the stacking and greedy limitations of the v1 solver". The
  container-validation point was also refused here and turned into issue #15 instead; that decision is
  `LP-04c`.
- **Verified:** the `ai_usage.md` row for 2026-09-30 records that each reported defect was reproduced
  before being fixed and each new test was checked to fail without its fix.
