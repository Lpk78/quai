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
## 2026-09-23 — Commit pushed to an already merged PR
- What happened: the commit adding @MORHI11 to the README was pushed to `docs/fill-repository-details` one minute after Sam merged PR #1, so it never reached `main`.
- Why: a PR merges the branch as it is at merge time; later commits on that branch are not included.
- What we tried: recovered the commit with `git cherry-pick` on a new branch and opened a new PR.
- What we learned: check the PR status (`gh pr view`) before pushing more work to its branch.

---

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

## 2026-09-30 — The branch followed a rule that `main` had already replaced

- What happened: `LP-05` added a row to `documentation/ai_usage.md`, as step 7 of `/task` asked when the
  branch was created. While the branch was open, #20 merged the opposite rule: AI help is recorded in the
  "Outcome" of `prompts/dev/<ID>_<slug>.md`, and a Pull Request never adds a row to that table. GitHub
  marked #21 as conflicting, and the conflict was on exactly the row the new rule forbids.
- Why: the branch was working from the rules as they stood when it started, and nothing tells a working
  copy that the rules moved. The conflict was the only signal — and it appeared at push time, not while
  the row was being written.
- What we tried: dropped our row and kept `main`'s, since the AI help for this task is already recorded in
  `prompts/dev/LP-05_constraint-schema.md`, then merged `main` into the branch and re-ran the tests.
- What we learned: this is the second conflict on this table (see the entry above), which is what #20 set
  out to end — so the rule works, it just arrived mid-branch. The habit to keep is merging `main` into a
  branch before writing documentation, not only before pushing: rules live in the repository, and a long
  branch reads an old copy of them.
- Related branch / PR: `feature/constraint-schema`, #21, rule from #20.

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

## 2026-09-30 — Two readings of the rubric document were wrong the first time

- What happened: `quai.rubric` reads the 25 test sentences and the route out of
  `documentation/prompt_evaluation.md`. Two of its parsers were wrong on the first run, and both
  failed quietly rather than raising. `cases()` returned **1 case instead of 25**: the regex reads
  the fenced JSON block with `re.DOTALL`, and the group for the sentence was `(.+)`, so the dot
  crossed newlines and the first match swallowed everything from T01 to the last quotation mark in
  the section. `stop_names()` returned `{('S1', 'Rouen'): None, ...}` instead of
  `{'S1': 'Rouen', ...}`, because `dict(dict.fromkeys(pairs))` builds keys out of the pairs
  themselves — `dict.fromkeys` was copied from the route parser, where the values being dropped is
  the point.
- Why: both are parsers whose wrong answer still has the right type. A list of one case is a list;
  a dict keyed by tuples is a dict. Nothing downstream would have raised: an evaluation run would
  simply have scored one sentence out of 25, and would have told the model the stops were named
  `None`.
- What we tried: matched the sentence with `[^\n]+` instead of `.+` so that DOTALL cannot reach past
  the line, and built the stop names with an explicit `setdefault` loop with a comment on why the
  first mention wins. Then wrote `tests/test_rubric.py` to pin what the readings must be, not only
  their shape: all 25 ids in order, no newline and no fence inside a sentence, one sentence compared
  word for word against the document, and every stop name checked against the route line.
- What we learned: a count is the cheapest assertion there is, and it catches the whole class. The
  LP-05 failure in this file was also a document parser returning something plausible (`S3` twice);
  the lesson repeated, so the rule now is that every reader of the document is pinned by a test that
  states the expected number of things and one exact value, never just the type.
- Related branch / PR: `feature/prompt-evaluation`, #11.

---
## 2026-09-30 — A harness written for a model the project does not use

- What happened: LP-06 was asked to send `temperature 0`, as the course material and the results
  table ask. It was written not to, on the grounds that "the current Claude models reject
  `temperature` with a 400" — true of Opus 5, Sonnet 5, Opus 4.7 and 4.8, and not true of
  `claude-haiku-4-5-20251001`, which is what `LLM_MODEL` names in `.env`. The temperature column was
  set to `n/a` and a failure entry was written here explaining a constraint that did not apply. The
  review of #22 reasoned from the same wrong model, so it did not catch it either. One real call to
  the model actually configured settled it in a second: `temperature 0`, HTTP 200.
- Why: `src/quai/llm.py` carried `DEFAULT_MODEL = "claude-opus-5"` and fell back to it whenever
  `.env` was silent, so the file read as though Opus 5 were the model in use. Nothing in the harness
  ever compared that name against `LLM_MODEL`, and every comment, docstring and doc paragraph was
  then written about Opus 5's behaviour — its thinking, its `max_tokens`, its sampling parameters —
  while every call would have gone to Haiku 4.5. A default that is almost never right is worse than
  no default: it is a claim about the run that nothing checks.
- What we tried: the default is gone. `LLM_MODEL` (or `--model`) names the model or the run stops
  with `MissingModel`, so a Results row cannot name a model that did not answer. `temperature 0` is
  sent, the column records `0`, and `temperature_cell` prints what was sent — `n/a` when a model
  that removed sampling parameters is run with none — rather than a constant.
- What we learned: check a model's behaviour against the model that is configured, with one call,
  before writing a paragraph about it. "The current models do X" is not a fact about a run; the name
  in `.env` is. Separately, the point the wrong entry made still stands on its own: `temperature 0`
  reduces variability and has never guaranteed identical outputs, so it never made a score
  repeatable. That is why every sentence is translated three times and a criterion counts as Yes
  only when all three runs say Yes — the three runs measure what the parameter merely made easy to
  forget, and they are the part that matters whether the column says `0` or `n/a`.
- Related branch / PR: `feature/prompt-evaluation`, #22.

---
## 2026-09-30 — A validated contract that refused a normal sentence

- What happened: the constraint schema refused `{"load_last": B9}` together with `{"load_last": B7}`
  as a contradiction — "B9 and B7 cannot both be loaded last at S3". "Load the toolbox and the paint
  cans last" is an ordinary thing for an operator to say, and because `parse()` refuses the whole
  output and never repairs it, the request was lost entirely, with no other way for the model to
  express it. The review of #21 caught it.
- Why: the check was written from the words of the constraint rather than from a sentence someone
  would say. "Loaded last" reads as a single position, one item per stop, and that reading was turned
  into a validation rule without asking what the operator would be refused by it. Every test written
  for the check confirmed the same wrong reading, so 90 green tests said nothing about it.
- What we tried: `load_last` now names a group. The items carrying it at a stop are the last group
  there and the solver orders them among themselves; the contract table, the *Route and unloading
  order* rules and T26 say so, and the test that used to demand a refusal now demands acceptance. The
  same review round found the opposite hole — `not_stackable` with `max_weight_on 20` on one item
  passed validation, which the solver would have had to settle silently — so that is refused now.
- What we learned: a rule that refuses is as much a design decision as a rule that accepts, and it
  costs an operator something. Before adding one, write the sentence it refuses and read it out loud.
  It was also cheap to fix only because no score had been recorded yet: the results table was empty,
  so changing the contract cost nothing. A week later it would have meant re-running every
  evaluation.
- Related branch / PR: `feature/constraint-schema`, #21.

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

---

## 2026-09-30 — A stack limit the solver only ever enforced upwards

- What happened: the solver checked `max_weight_on` by asking, of the box it was about to place, which
  boxes it would come to rest on and whether its weight still fitted under their limits. That is only
  right while boxes go in from the bottom up. A box placed later can slide into a gap *under* one already
  loaded — first fit tries the lowest corner first, so it does exactly that — and becomes a new support
  for it. The load already sitting above was never counted against it. 117 tests were green; a sweep over
  200 generated loads with routes and limits produced 2 plans that broke a limit.
- Why: the check was written as a delta — "what does this box add?" — because that is how the cap on the
  whole load works, and the same shape was reused without asking whether placing a box can change what
  rests on a box that is already placed. It can.
- What we tried: `checks.stack_problems()` is now the one definition of the rule. The independent checks
  ask it of the finished plan and the solver asks it of the plan a candidate placement would produce, so
  the solver cannot pack by a looser reading than the checks judge by. The smallest case is
  `test_a_box_cannot_slide_under_a_load_it_may_not_carry`, and the sweep that found it is now a test.
- What we learned: two things. A greedy packer does not fill bottom-up, so nothing about a plan may be
  treated as settled while boxes are still going in. And a hand-written suite only proves what its author
  already thought of — every one of the 117 tests was written by someone who believed the check was
  right, and the bug came out of loads nobody designed.
- Related branch / PR: `feature/solver-v2`, #17.
