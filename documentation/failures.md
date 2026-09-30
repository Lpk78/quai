# Failures, experiments and challenges

For every entry: **What happened? Why? What did we try? What did we learn?**

Categories to watch: prompts that did not work, unexpected outputs, hallucinations, sycophancy,
prompt injection, context-window limits, tool limits, failed integrations, inconsistent results,
Git problems, merge conflicts, changes of direction, abandoned ideas.

---

## Planned experiment: LLM-only placement vs solver

- **Question:** can an LLM place boxes in a container on its own?
- **Protocol:** same box lists given to the LLM and to the solver; count overlaps, out-of-bounds boxes,
  and differences between repeated runs.
- **Results:** _to run and record._

---

<!-- Template
## YYYY-MM-DD — short title
- What happened:
- Why:
- What we tried:
- What we learned:
- Related branch / PR:
-->
## 2026-09-28 — The tests workflow is red until the solver branch is merged

- What happened: `tests.yml` runs `python -m unittest discover tests`, but `tests/` does not exist on
  `main` yet — it is added by PR #3 (`feature/solver-v1`). On a fresh checkout of a branch cut from
  `main`, discovery raises `ImportError: Start directory is not importable: 'tests'` and exits 1, so the
  check goes red on a PR that contains no Python at all.
- Why: the workflow was written against the solver branch, where `tests/` exists. Locally it seemed to
  pass because switching branches left an empty `tests/__pycache__` directory behind, which makes
  discovery report "NO TESTS RAN" instead of failing. The local run and the CI run were not the same run.
- What we tried: reproduced CI's condition in an empty directory (`python3 -m unittest discover tests`)
  and confirmed the ImportError; checked `git ls-files tests` to confirm `tests/` is untracked on `main`.
- What we learned: a green local test run proves nothing if the working directory holds untracked
  leftovers. Check `git ls-files`, not `ls`, before trusting that CI sees what you see. Kept the workflow
  as written — it is correct for the merged repository — rather than weakening the command to hide the
  failure. The check turns green once PR #3 brings `tests/` into `main`.
- Related branch / PR: `docs/team-automation`, depends on #3.

---

## 2026-09-30 — Merge conflict on `documentation/ai_usage.md` between #3 and #4

- What happened: while #4 (`docs/team-automation`) was open, #3 (`feature/solver-v1`) was merged into
  `main` and added its own row at the end of the AI usage table. #4 had added two rows at that same end.
  `git merge origin/main` could not decide which rows come last, so it stopped on
  `CONFLIT (contenu) : Conflit de fusion dans documentation/ai_usage.md` with both blocks between
  `<<<<<<<`, `=======` and `>>>>>>>`. GitHub had already marked the PR as not mergeable.
- Why: an append-only Markdown table is the classic conflict shape. Both branches wrote different lines
  at the same place — the last line of the table — and neither is wrong, so Git refuses to guess. Nothing
  was broken; the two sides were simply unaware of each other.
- What we tried: took both sides rather than choosing one, since the two branches document real and
  different uses of AI. Ordered the rows by date (`2026-09-28`, then the ongoing `From 2026-09-28` line,
  then `2026-09-30`), removed the three markers, checked with
  `grep -rn "<<<<<<<\|>>>>>>>" .` (only the two mentions inside CONTRIBUTING.md §5 remain, which is
  expected), ran `python3 -m unittest discover tests` — 19 tests pass now that `tests/` arrived with #3 —
  and committed the merge.
- What we learned: a conflict in a log file is almost always "keep both", not "pick one"; the only real
  decision is the order. Resolving it inside the branch keeps the merge visible in our history instead of
  hiding it behind the GitHub button. And merging `main` into a long-lived branch early would have made
  this a one-line conflict instead of a three-line one — the longer a branch stays open, the more it has
  to catch up on. The push re-runs the CI on top of the new `main`, which is what clears the red check
  from the entry above.
- Related branch / PR: `docs/team-automation`, #4, conflict with #3.

---

## 2026-09-30 — The prompt that produced the solver is unrecoverable

- What happened: `LP-16` backfilled `prompts/dev/` with the six development prompts given before the
  `/task` skill existed, recovering each one from this machine's Claude Code session history. Five came
  back verbatim. The sixth, `LP-02` — the solver behind #3 — did not. The solver commits `134abd3` to
  `6a1e0be` are dated 2026-09-28T13:09:05Z and #3 was opened at 13:09:10Z, but the oldest prompt kept
  anywhere on this machine for this repository is 13:36:57Z, about 28 minutes later. The only recorded
  solver prompt, "Commit the solver already written…", ran at 13:40:44Z, found the five commits already
  pushed and produced nothing.
- Why: the rule that every development prompt is saved in `prompts/dev/` was written *by* #4, and the
  solver was written before it. Session history is not an archive: it only holds what was typed into
  Claude Code, on the machine where it was typed, and the solver was not written that way.
- What we tried: searched every session file under
  `~/.claude/projects/-Users-leo-paulkerrinckx-Desktop-data-project/`, the other project directory, and all
  384 entries of `~/.claude/history.jsonl`. Confirmed the gap from two directions — the earliest recorded
  prompt is 28 minutes after the PR was opened, and the recorded prompt's own wording, "already written",
  says the code came from elsewhere. Then recorded `prompts/dev/LP-02_solver.md` as incomplete, stating
  what is missing and how that was established, rather than inventing a prompt that would have looked
  right.
- What we learned: a prompt that is not saved when it is given is usually lost, so the `/task` rule earns
  its place — it is cheaper to write the file up front than to reconstruct it two days later. Where a
  record cannot be honest it should be visibly empty: the Git history is graded on authenticity, and one
  file saying "this was not recovered, here is the proof" is worth more than six that all look complete.
- Related branch / PR: `docs/backfill-dev-prompts`, `LP-16`; the unrecoverable prompt belongs to #3.
