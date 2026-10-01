# LP-02 — First 3D placement solver

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-28
- **Branch:** `feature/solver-v1`
- **Issue:** #5 — opened later, by `LP-03` on 2026-09-28T13:51:16Z, to track work this branch had
  already done. PR #3 never carried a `Closes #5`, and #5 was closed by hand on 2026-09-30T09:44:19Z.
- **Recorded afterwards:** yes — written on 2026-09-30 by `LP-16`, after the `/task` skill existed.

## The prompt that produced the solver was not recovered

This is the one file of the backfill that cannot be completed honestly, and it is recorded as incomplete
rather than filled with a plausible guess.

The solver commits `134abd3` → `6a1e0be` are dated 2026-09-28T13:09:05Z and PR #3 was opened at
13:09:10Z. The oldest Claude Code prompt kept anywhere on this machine for this repository is
2026-09-28T13:36:57Z — the `LP-01` prompt — about 28 minutes *after* the solver was already pushed. This
was checked in every session file under
`~/.claude/projects/-Users-leo-paulkerrinckx-Desktop-data-project/` and in all 384 entries of
`~/.claude/history.jsonl` at the time. Nothing earlier exists.

"Anywhere on this machine" is the stronger half of that claim, so here is what it rests on.
`~/.claude/projects/` holds four directories, and the earliest session timestamp in each is:

| Directory | Earliest session | Could hold the solver prompt? |
|---|---|---|
| `…-Desktop-data-project` | 2026-09-28T13:36:57Z | This repository — searched; nothing earlier |
| `…-Desktop-EJC-web-claude` | 2026-08-03T12:55:53Z | No — a different project, unrelated to QUAI |
| `…-Desktop-quai-sam` | 2026-09-30T20:54:03Z | No — created two days *after* the solver |
| `…-Desktop-quai-hypo` | 2026-09-30T20:54:23Z | No — created two days *after* the solver |

The two `quai-*` checkouts did not exist when the solver was written, so a renamed or parallel checkout
cannot be where the prompt went. That is the step this file was missing: not "I looked here", but why
nowhere else could hold it.

So the solver was written before any session that was recorded on this machine, and the prompt that
produced `src/quai/models.py`, `checks.py`, `solver.py`, the tests and `src/demo.py` is gone. See
`documentation/failures.md`, 2026-09-30.

## Prompt as typed

The only recorded prompt about the solver is the one below. It did not write the solver: by the time it
ran, the work was already committed and PR #3 was already open, so it produced no commit.

```
/task Commit the solver already written (src/quai, tests, src/demo.py) on feature/solver-v1,
one commit per module
```

Session `d41c63d9-…jsonl`, 2026-09-28T13:40:44Z. The wording "already written" is itself the evidence
that the code came from somewhere else.

A related instruction in the next message of the same session, 13:44:13Z:

```
2) Yes, assign SamDana-maker as reviewer on PR #3.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/3 (reviewer: `SamDana-maker`, merged 2026-09-30T08:11:08Z)
- **What the AI produced for this prompt:** nothing. Claude Code checked `git status` and
  `git log main..feature/solver-v1`, found the five commits already present one per module, ran the tests
  on the branch, reported that the task was already done, and committed nothing. The five solver commits
  are not attributable to it.
- **What was changed by hand:** not applicable — no change was made under this prompt.
- **Verified:** the five commits `134abd3` (models), `7c39666` (checks), `6617c10` (first-fit solver),
  `7b53d0c` (tests), `6a1e0be` (demo) all carry the 2026-09-28T13:09:05Z author date, before this
  prompt's 13:40:44Z timestamp.
- **Not covered by this record:** the 2026-09-30 review round on PR #3 is a separate task, `LP-04b`, and
  its prompts *were* recovered.
