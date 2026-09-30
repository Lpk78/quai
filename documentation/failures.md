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

## 2026-09-30 — The route parser read the same stop twice

- What happened: `tests/test_constraints.py` builds a `Manifest` from the document's own route so that
  the 25 expected outputs can be validated against it. Reading the stops in route order off the manifest line
  ("Stops on the route: `S1` Rouen, then `S2` Le Havre, then `S3` Caen — in that order, `S3` last.")
  returned `('S1', 'S2', 'S3', 'S3')`, and `Manifest.__post_init__` refused it with
  `manifest stops contains the same id twice`. Three tests errored out.
- Why: the sentence names the last stop twice on purpose — once in the list, once to insist it is last —
  and a regex over the line cannot tell a member of the route from a comment about it. The first version
  of the fixture used `stop_ids()` from the other test file, which returns a *set*, so the duplicate was
  invisible; the bug only appeared when we needed the stops in order, because the route order is part of
  the contract and sorting a set is not reading a route.
- What we tried: kept the order and dropped repeats with `dict.fromkeys`, first mention winning, and
  wrote down why in the helper's docstring. Added a test that the parsed route holds exactly the stops
  `stop_ids()` finds and that its last element is what `last_stop` returns, so the two readings of the
  same line cannot drift apart.
- What we learned: the duplicate check we had just written in the schema is what caught it — strict
  validation pays for itself the first time something feeds it real data, even our own test fixture.
  And a set hides exactly the mistakes an ordered list exposes: sorting `S1, S2, S3` looked correct and
  would have silently reordered any route whose ids are not alphabetical.
- Related branch / PR: `feature/constraint-schema`, #10.

---

## 2026-09-30 — `Infinity` is valid JSON to Python, and it crashed the validator

- What happened: `_limit_problems` rejected fractional centimetres with `value != int(value)`, which
  reads well until the value is `inf` or `nan`: `int(float("inf"))` raises `OverflowError` and
  `int(float("nan"))` raises `ValueError`. `find_problems` would have crashed with a traceback instead of
  returning a problem, on the one path whose whole job is to survive bad input.
- Why: `json.loads` accepts the non-standard literals `Infinity`, `-Infinity` and `NaN` by default, so a
  model can hand us a limit that is not a number in any useful sense. The check assumed a finite value
  because every example we had written by hand was finite.
- What we tried: reproduced it with `json.loads('{"limit_cm": Infinity}')`, added an `math.isfinite`
  guard before the whole-number test, and a test for both literals.
- What we learned: a validator has to be written against what the format actually allows, not against the
  examples in the contract. We found this one by asking "what does `json.loads` accept that we never
  write?" — the same question is worth asking of every field we add later.
- Related branch / PR: `feature/constraint-schema`, #10.

---
