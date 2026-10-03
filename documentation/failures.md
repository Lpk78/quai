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

---

## 2026-10-01 — A brand kit whose own mockups failed accessibility

- What happened: the approved design pack arrived with the primary action buttons drawn as white text
  on safety orange `#FF8A00` — the "Get started" and "Loaded, next" buttons visible in
  `assets/brand/reference/mobile-ui.png`. That combination measures 2.36:1, which fails WCAG AA at
  every size, including large display text. The same pack's palette invites `#FF8A00` to be used as a
  text colour on the `#F7F6F3` background, which is 2.19:1. Checking the rest of the palette the same
  way found four more: `success`, `warning`, `error` and the stop-2 green all fail AA as body text on
  our background, between 1.99:1 and 3.49:1.
- Why: the pack was designed as images. Orange on white looks confident in a rendering at full size on
  a laptop, and nothing in the process measured it. Nobody was careless — the failure mode is that a
  visual identity is approved by looking at it, and contrast is the one property that looking at it on
  a good screen cannot tell you.
- What we tried: text on orange is navy `#102238` (6.79:1), orange text is `#C2410C` (4.79:1), and the
  status and stop colours are documented as fills that carry an icon or a badge, never body text.
  `documentation/design.md` states each rule with its measured ratio and says explicitly that where the
  mockups disagree with it, the mockups lose. `tests/test_brand.py` computes the ratios from
  `assets/brand/tokens.json` and fails if any of them stops holding — including a test that white on
  orange still *fails*, so the rule cannot be quietly reverted by someone who reads the mockup instead
  of the document.
- We also found that the two supplied wordmark SVGs asked for Arial, which is neither the brand display
  font nor installed everywhere. They now name Plus Jakarta Sans with a fallback stack, but the
  wordmark is still live `<text>` and should be converted to outlines before the logo is used publicly.
  That needs a vector editor; it is written down in `design.md` rather than left to be rediscovered.
- What we learned: a design system is a set of claims, and claims can be tested. Colours are numbers,
  and contrast is arithmetic — so the accessibility section of a design document belongs in the test
  suite exactly like the constraint contract does. The reference renderings are now explicitly
  non-normative: sampling a pixel out of `colour-palette.png` gives `#FB830C` where the token says
  `#FF8A00`, so anyone eyedropping a mockup is already working from the wrong colour.
- Related branch / PR: `docs/brand-kit`, `HY-10`.

---
## 2026-10-01 — Mockups that advertised a product we are not building

- What happened: the second round of brand images arrived with a full website mockup and a brand
  applications board. Read as marketing copy rather than looked at as pictures, they describe a different
  product: "Follow your optimised route and get live updates", an "Est. route time 4h 20m" tile, a route
  map, and a Pricing item in the navigation. QUAI computes no routes, estimates no times, tracks nothing
  live and has no pricing. The same sheets carry three slogans that are not ours — "Smart loading.
  Delivery confidence.", "Smarter Delivery Ahead.", "People. Parcels. Forward." — alongside the real one,
  a business card with an invented employee, email, phone number and domain, and a phone home screen
  showing real third-party app icons.
- Why: an image generator asked for "a logistics SaaS landing page" produces the landing page of the
  average logistics SaaS, because that is what it has seen. Nothing in the brief said which features
  exist, so it supplied the usual ones. The route map is the sharpest case: route optimisation is in
  `documentation/roadmap.md` under *rejected scope*, and the mockup put it in the hero.
- What we tried: `documentation/design.md` gained a **Copy rules** section — one slogan, never saying the
  AI plans the load or orders the stops, no features the app does not have, no real brand marks in
  published images, navy text on orange buttons. It names each violation in each sheet, so the images
  stay useful for mood and layout without their words leaking into the product. Two of the rules are
  checked by `tests/test_brand.py`.
- What we learned: a mockup is an argument about what the product is, not only about how it looks, and it
  is persuasive precisely because nobody reads it as a claim. The dangerous ones were not the invented
  slogans, which are obviously wrong, but "optimised route" — plausible, adjacent, and a direct
  contradiction of the one architectural rule the project is built on. Reference images now get read for
  what they assert, not just looked at.
- Related branch / PR: `docs/brand-kit`, `HY-10`.

---

## 2026-10-01 — The first prompt version scored zero on a code fence

- What happened: `v1_zero_shot`, the first version of the constraint-translation family, scored **0 on
  all eight criteria and 0/26 Total**. Not one of the 78 replies failed on its content. All 78 came back
  wrapped in a ```json code fence, and `quai.evaluation` calls `json.loads` on the reply exactly as it
  arrives, so every one of them failed C1 before a single field was examined — and a sentence that fails
  C1 fails the other seven, because there is no object left to check. The prompt contains the sentence
  "No prose before or after it, no code fence, no explanation". The model fenced every time anyway.
- Why: a fence is what a chat model does with JSON, and one line of prose asking it not to does not
  outweigh that. The deeper point is about the rubric rather than the model: C1 is `parse()`, and
  `parse()` is a door, not a critic. It has no opinion about whether the content is good, so "right
  answer, wrong envelope" and "wrong answer" are the same event to it. That is the decision taken
  deliberately in #22, and this is the first run where it cost a version everything it knew.
- What we tried: recorded the zeros. The temptation was to add one line to the prompt and re-run before
  anyone saw the row, which would have taken about four minutes and produced a respectable first score.
  It was refused: v1 exists to be the number v2 is compared against, and a baseline quietly tuned until
  it looked acceptable measures nothing. Instead the stored transcript was re-scored with the fence
  stripped — **21/26** — and that figure is written into `documentation/prompt_evaluation.md` as an
  explicitly labelled diagnostic that no version is credited with and that never enters the table.
- What we learned: separate what a prompt *knows* from how it *delivers*, because one rubric column can
  hide the difference and a table of zeros looks like a prompt that understood nothing. The diagnostic
  is what makes the row readable, and it has to be derivable from a stored artefact rather than from
  memory — the transcript is why `outputs/evaluations/` exists, and this is the first time it earned its
  place. Second lesson, cheaper: the evaluation script was sending the *whole version file* as the system
  prompt, and `/prompt-version` requires that file to carry a change log. v1's names the sentences it
  expected to find hard, so the family's first recorded score would have been a prompt shown its own test
  set. Caught before the run; the script now sends only what sits between the prompt markers.
- Related branch / PR: `prompt/constraint-translation-v1-zero-shot`, #12.

---

## 2026-10-01 — Two prompt versions, 156 calls, and the fence did not move

- What happened: `v1_zero_shot` scored **0/26** because all 78 replies arrived inside a ```json fence
  and `parse()` reads the reply as it comes. `v2_output_format` changed the *Output* section and
  nothing else — the rest of the prompt was spliced from v1 byte for byte — removing the fenced
  example v1 had demonstrated while forbidding fences, stating the rule as a property the model can
  check while writing ("the first character you emit is `{`"), and giving the reason. It scored
  **0/26**: 78 of 78 replies fenced again, byte-identically, `Same answer on every run: 26/26` both
  times.
- Why: the hypothesis was that v1's instruction and its example disagreed and the example won. It was
  a good hypothesis — 78 out of 78 is far too consistent for reluctance — and it was wrong. Whatever
  produces the fence on `claude-haiku-4-5-20251001` is not reachable from the system prompt. Three
  separate instructions, a removed demonstration, and a stated reason changed the output by zero
  replies. The lesson is not about fences: it is that "say it more clearly" is a hypothesis like any
  other, and it can be tested cheaply and be false.
- What we tried: recorded both zeros, kept v2 rather than iterating the wording a third time, and
  wrote down what the remaining options actually cost — strip the fence before `parse()` (contradicts
  the contract, because the server hands the reply over unchanged), constrain the reply with
  `output_config.format` (rejected on purpose, it makes C1 true by construction), or score a different
  model (answers a different question). All three are decisions for the reviewer rather than a third
  rewording, so none is in the PR.
- What we learned: two things, and the second is the one worth keeping. First, a negative result for
  the cost of one evaluation is cheap, and the splice is what made it a result at all — because
  exactly one section differed, "wording cannot fix this" is a conclusion rather than a guess.
  Second, the run also re-tested the v1 diagnostic by deliberately *not* fixing the five non-fence
  failures: **T10, T16, T17 and T20 failed identically in both runs**, which is what makes the
  fence-stripped figure trustworthy enough to brief a later version on. T24 improved and T06 and T14
  regressed, so the diagnostic moved 21 → 20 while the recorded score stayed 0 → 0. A version that
  cannot be parsed is worth nothing whatever its content does.
- Related branch / PR: `prompt/constraint-translation-v2-output-format`, #12.

---

## 2026-10-01 — A worked example taught more than it was shown

- What happened: `v4_few_shot` added four worked examples to v3's prompt, one per `unresolved` failure.
  The Total moved 21/26 → 22/26. Underneath that: **T20 and T14 were fixed, T13 was broken, and T10,
  T16 and T17 did not move at all.** T13 had passed every criterion on v3.
- Why: Example 1 shows a compound sentence — one half names a real item, the other names something
  absent — and teaches "translate the real half, report the absent half, bind nothing to it". That is
  T20's exact shape and T20 was fixed. The model also drew the wider lesson "answer the resolvable
  part of any doubtful sentence", and applied it to T13, where there is no resolvable part: "the
  fragile stuff" is an ambiguous reference, so the contract wants an `unresolved` entry and an empty
  `constraints` list. v4 reports the ambiguity correctly and emits `on_top` for `B2` and `B5` anyway.
  An example teaches the decision it shows *and* whatever generalisation the reader draws from it, and
  the second is not the author's to choose.
- What we tried: kept the regression and recorded it per sentence rather than reporting +1 and moving
  on. The headline is the least informative number in the result: two fixed, one broken and three
  untouched is four different findings, and only the per-sentence table shows them. Also recorded that
  Examples 2 and 3 had **no measurable effect** — T10 still guesses kilograms and T16/T17 still answer
  `out_of_scope` where the contract wants `ambiguous` — so few-shot is not a general lever here. It
  moved what matched an example's shape and left the rest.
- What we learned: a prompt change is not one intervention with one number. v4 was four examples and
  produced at least four separate effects, two of them in opposite directions, and a Total that
  averages them hides all of it. The three-runs rule and the per-sentence table are what made this
  legible — without them this is "+1, few-shot helps a bit", which is the wrong conclusion in both
  directions. Next time, an experiment with four independent changes should expect to be read as four
  results.
- Related branch / PR: `prompt/constraint-translation-v4-few-shot`, #12.

---

## 2026-10-01 — Worked examples narrow what the model thinks an answer can look like

- What happened: v4 broke T13 by over-generalising one example. v5 fixed that precisely — a
  counter-example placed beside the rule, labelled as its limit — and **T13 passed again on all three
  runs**. In the same run, **T06 and T24 failed for the first time**, and both had passed in v3 (no
  examples) and in v4 (four examples). The Total went 22 back down to 21.
- Why: all three of v5's examples produce a non-empty `unresolved`, and two pair it with an empty
  `constraints`. T06 is a clear sentence with a reason attached — "Load the toolbox last, I need it
  first on site" — and v5 emits the right `load_last` and then reports the *reason* as
  `out_of_scope`, manufacturing doubt that is not there. T24 matches none of the three examples and
  comes back as two empty lists, the failure v1 had. The examples stopped being illustrations of
  decisions and became the space of permitted answers.
- What we tried: kept the result and reported it per sentence against both ancestors rather than as a
  Total, because the Total says "21, no better than v3" and the per-sentence table says three
  different things: the bound worked, two new sentences broke in the same direction, and three
  sentences have now resisted prose, four examples and three bounded examples alike.
- What we learned: an example is not an additive instruction. v4's lesson was that an example teaches
  the decision it shows *plus* whatever generalisation the reader draws; v5's is the other half —
  the set of examples also tells the model what an answer is allowed to look like, so a case covered
  by none of them gets answered in the nearest shape rather than from the contract. Adding an example
  changes the sentences it does not mention. Both regressions were invisible in the Total and obvious
  in the per-sentence diff, which is the second time that table has been the whole value of a run.
- Related branch / PR: `prompt/constraint-translation-v5-bounded-examples`, #12.

- **Decision, 2026-10-01 (`Lpk78`, AI-layer owner): example-based iteration stops here.** v5 is
  recorded as it stands — 21/26 is a result, and *each example fixes its target and breaks something
  else* is the finding. **v4 (22/26) remains the version `POST /constraints` (#19) uses in
  production.** The evidence is the per-sentence table across the three versions that could be
  scored, which no Total shows:

  | | v3 | v4 | v5 |
  |---|---|---|---|
  | T13 "Put the fragile stuff on top." | pass | **C2, C3** | pass |
  | T20 "…don't stack the microwave" | **C2, C3** | pass | pass |
  | T14 "the heavy things on the light ones" | **C5** | pass | pass |
  | T06 "Load the toolbox last, I need it first on site." | pass | pass | **C5** |
  | T24 "What's the weather in Rouen tomorrow?" | pass | pass | **C1, C5** |
  | T10, T16, T17 | fail | fail | fail |
  | **Total** | **21** | **22** | **21** |

  Read down the columns rather than along the bottom row: every example-based version fixed the
  sentences its examples depicted and broke sentences they did not. v4 bought T20 and T14 with T13;
  v5 bought T13 back with T06 and T24. Three sentences moved for nobody. A sixth version would be a
  fourth draw from the same distribution, and the next example's side effects are not predictable
  from the last one's.


---

## 2026-10-01 — The wiring we specified for `load_last` would have done nothing at all

- What happened: `SA-16` was specified as "reorder that item to the end of the boxes list passed to
  the solver (the solver places in list order, so this achieves loaded last)". The solver does not
  place in list order. `solve()` places `loading_order(boxes, constraints)`, and `loading_order`
  always sorts — by stop, then `load_last`, then descending volume, then id. Passing the list in a
  different order was checked against the real solver: reversing the input gave a **byte-identical
  plan**, and moving the box to the end of the list left its x unchanged at 0. The feature would have
  shipped, passed a careless test, and done nothing.
- Why: the premise was about a solver that does not exist. Worse, `load_last` is already in the
  solver's `HONOURED` set and already implemented in `loading_order` via `last_group` — the work was
  not to build the behaviour but to open a door to it. Three lines of wiring through
  `quai.constraints.parse()` move the box from x=0 (loaded first, back wall) to x=70 (loaded last,
  nearer the doors), which is the whole visible effect that was asked for.
- What we tried: the premise was tested before it was built, which is the only reason this entry is
  not a bug report. Two checks, both against `quai.solver` rather than against a reading of it:
  reorder the input list and compare the plan (identical), then pass a `load_last` constraint through
  `parse()` and compare (changed). The first attempt at the *test* was wrong in the same family — it
  used a box that the volume tie-break was already loading last, so it asserted nothing; and the
  first container was a 100 cm cube, where every box stacks at x=0 and "nearer the doors" cannot be
  observed even when the ordering is correct. Both are now chosen deliberately, with the reason in a
  comment.
- What we learned: a task that says "the solver does X, so do Y" is two claims, and the cheap one to
  check is the first. The reorder was plausible — plenty of packers do consume list order — and
  nothing about the specification looked wrong until `loading_order` was read. For a solver this
  layer does not own, read the function before wiring to its supposed behaviour.
- Related branch / PR: `feature/plan-constraints`, `SA-16`.

---

## 2026-10-01 — Scanning one small parcel ejected two cartons already loaded

- What happened: the demo fixture (`SA-15`) loads eighteen boxes at 77.8% fill, then adds the parcel
  scanned on stage. With that parcel assigned to stop 4 (Retiro), the plan came back **17 of 19
  placed**: the parcel went in and `B15` and `B18` — two cartons that fit before it existed — came
  out. The fill rate fell from 77.8% to 74.4%. Adding one 40 x 30 x 25 box made the load worse.
- Why: `quai.solver` is first fit over candidate corners, and `loading_order` sorts by stop before
  volume. A parcel for stop 4 is loaded in the middle of the round, so it takes a corner the boxes
  for stops 3, 2 and 1 were going to use, and the corners it creates in exchange are the wrong shape
  for them. Nothing is wrong with any single placement; the greedy choice is simply not reversible,
  and the heuristic never reconsiders a box it has already placed.
- What we tried: the parcel at every plausible stop. Stop 1 placed all nineteen (78.4%), stops 2 and
  8 lost one carton, stops 3 and 4 lost two. Shortening the lamp carton `B18` from 45 to 40 cm then
  let the parcel go to stop 2 — Chamberí, the first real delivery — with **19 of 19 placed** and the
  fill rate rising to 78.2%, which is the fixture as committed. So the fix was a centimetre of
  clearance, not a change of stop.
- What we learned: "the solver found a place for it" and "the load is still as good" are different
  questions, and only the second one matters to an operator watching a screen. A live-scan feature
  that re-plans has to compare the new plan against the old one and say what moved — which is the
  layer roadmap row 12 (`feature/constraint-solving`) will own, since that is where constraints
  accumulate across sentences and the plan is recomputed. Worth remembering before the demo: the
  cascade is real, it is reachable with one parcel, and it is invisible unless the unplaced list is
  on screen.
- Related branch / PR: `feature/demo-fixtures`, `SA-15`.

---

## 2026-10-01 — The phone demo and the camera cannot both work over `http://`

- What happened: `LP-20` asked for two things that turn out to contradict each other. Reaching the
  dev servers from a phone means serving them on the LAN over plain `http://`, at
  `http://192.168.1.201:5173`. Scanning an operator card means `getUserMedia`, which browsers only
  expose in a *secure context* — HTTPS, or `localhost`. A LAN IP over `http://` is neither, so on the
  phone `navigator.mediaDevices` is not merely blocked, it is `undefined`.
- Why: the two halves of the task were specified against different assumptions about where the app
  runs. Nothing in either half is wrong on its own; the conflict only exists once they are the same
  deployment. `localhost` is a special case in the spec precisely so that development works without
  certificates, and it does not extend to the machine's other addresses.
- What we tried: measured rather than assumed, with one vite server bound to both names on the same
  port so only the host differed. At `http://localhost:5174`, `isSecureContext` is `true` and
  `navigator.mediaDevices.getUserMedia` exists. At `http://192.168.1.201:5174`, `isSecureContext` is
  `false` and `navigator.mediaDevices` is absent. Same build, same port, same browser.
- What we learned: the screen was built so that the absent camera is a state and not a crash — the
  same shape the dictate screen already uses when speech recognition is missing. `/login` detects it
  and offers the code typed in instead, so the phone demo still signs in either way. That fallback is
  what made the finding survivable rather than fatal, and it is still the behaviour on any machine
  without a certificate.
- **Resolved the same evening (`LP-21`).** mkcert issues a certificate for the Mac's LAN address,
  `vite.config.js` picks it up when `.certs/` exists, and both servers run over HTTPS. Measured
  again at `https://192.168.1.201:5173`: `isSecureContext` is now `true`, `getUserMedia` exists, and
  the scanner reaches its `scanning` state — the camera opens. The remaining manual step is on the
  device and not in the repository: the phone trusts the Mac's CA only once its root is installed
  *and* enabled there, which the README now spells out.
- Related branch / PR: `feature/phone-demo-login`, `LP-20`; fixed by `feature/https-lan`, `LP-21`.

---

## 2026-10-02 — An unhandled exception told the operator the server was unreachable

- What happened: `POST /constraints` caught `llm.CallFailed` and nothing else. `_translate` calls
  `llm.from_env()`, which raises `MissingKey`, `MissingModel` or a bare `NotConfigured` when `.env`
  has no key, no model, or the `anthropic` package is absent — and `Translator.translate` raises
  `FatalCall` when the API rejects the request, which is what a key that is *present but wrong* does.
  **Four of the five ways that call can fail were unhandled**, and each answered a bare `500`.
- Why the `500` was the smaller half of the problem: FastAPI's default exception handler sits
  **outside** `CORSMiddleware`, so its response carries no `access-control-allow-origin`. The browser
  refuses to let the page read it, `fetch` throws, and `web/src/api.js` maps a thrown fetch to
  `kind: "unreachable"`. The screen then says *"Could not reach the solver at
  http://127.0.0.1:8000"* — about a server that is running, listening, and answering. Measured rather
  than reasoned: the same endpoint's handled `422` carries the header, and the same request shape
  tripping `MissingKey` came back `500` with no header at all. Same server, same origin, only the
  exception type differing.
- What we tried: catching `NotConfigured` by its **base class** rather than naming `MissingKey` and
  `MissingModel`. That covers the "anthropic is not installed" case, which is raised directly as
  `NotConfigured` and which neither of the two reports of this bug had noticed, and it covers whatever
  `from_env` learns to require next without anyone remembering to come back here. `FatalCall` is caught
  separately as a `502`: the model answered, just not usably, which is what the existing `502` for a
  reply that fails validation already means.
- What we learned: on an endpoint a browser calls, an unhandled exception is not "a 500 instead of a
  nice message" — it is a *different error class* by the time it reaches the user, because the handler
  that produces it is outside the middleware that makes it readable. The wrong diagnosis was the real
  cost: "could not reach the solver" sends an operator to restart a healthy process, which is the one
  action that cannot help. Worth asking of every `except` on this layer: what does the browser see for
  the exceptions this does *not* name?
- Found in end-to-end retesting the evening before the demo, independently by `MORHI11` and by
  `Lpk78`, which is the argument for retesting a path end to end after the screens around it change
  rather than trusting that each piece still works.
- Related branch / PR: `fix/constraints-config-errors`, `SA-18`.

---

## 2026-10-01 — The order test that could not fail

- What happened: `SA-12` adds `POST /route`, and the one rule it exists to protect is that QUAI never
  reorders stops — OSRM's `/trip` would happily return a shorter journey in a different order. Two tests
  asserted the order, and both passed. Then the guard was mutation-tested by replacing the stop list with
  `sorted(points, key=lambda q: q.lon)`: the whole suite still passed. The fixture drove Amiens → Paris →
  Lille, which is already in ascending longitude, so sorting it was a no-op and the assertion compared a
  list to itself.
- Why: the addresses were picked for being real and far apart, not for being in an awkward order. The
  test looked like it was about sequence while the data made sequence irrelevant — so it asserted a
  property the fixture guaranteed regardless of the code.
- What we tried: reordered the fixture to Lille → Amiens → Paris, which differs from sorting by longitude,
  by latitude *and* alphabetically, and re-ran the mutations. All four now fail the suite: sort by
  longitude, sort by latitude, reverse, and swapping `/route` for `/trip`. The reason the order was chosen
  is written into the fixture's docstring so the next person does not "tidy" it back.
- What we learned: this is the second time the same shape has caught us — #14 had a parser test that
  passed because the regex matched the wrong table, and both were found by changing the code to see
  whether the test noticed. A test that has never been seen to fail is a claim, not evidence. Where a test
  protects a rule, write the fixture so that breaking the rule changes the answer.
- Related branch / PR: `feature/route-display`, `SA-12`.

---

## 2026-10-01 — Valid Python locally, a syntax error in CI

- What happened: `SA-12` pushed with 290 tests passing locally and CI went red immediately. The whole
  `test_server` module failed to import on a `SyntaxError` in `src/server.py`:
  `f"duplicate stop ids: {", ".join(duplicates)}"`. Nesting the same quote character inside an f-string
  expression is legal from Python 3.12 (PEP 701) and a syntax error before it. The machine this was
  written on runs 3.14; `tests.yml` pins 3.11, which is also what the README promises.
- Why: the language version was the one part of the environment never checked. The rule we already wrote
  after the last one of these — "a green local run proves nothing if the working directory holds
  untracked leftovers" — was about *files*; this is the same lesson about the *interpreter*, and nothing
  in the local run could have surfaced it.
- What we tried: used `', '` inside the f-string, and then checked the whole repository rather than the
  one line, by parsing every file under `src/` and `tests/` with
  `ast.parse(source, feature_version=(3, 11))`. That compiles against the 3.11 grammar without needing
  3.11 installed, and it reported the rest of the tree clean. Worth running before a push whenever
  something new is written on a machine ahead of CI.
- What we learned: "it runs here" is a statement about this machine, and the gap that matters is usually
  the one nobody chose — here, a minor version that silently permits newer syntax. CI caught it in
  fifteen seconds, which is the system working; the cost is a red build on a reviewer's notification.
- Related branch / PR: `feature/route-display`, #35.

---

## 2026-10-02 — The constraint we wired for the demo changes nothing on the demo load

- What happened: `SA-20` added `on_top` to what `POST /plan` passes the solver, so that the dictated
  sentence *"this parcel is fragile, put it on top"* would move a box on screen. Driven end to end
  against a real server — a real Claude call to `/constraints`, its real reply fed to `/plan` — it
  works exactly as designed and **changes nothing at all**: the plan is byte-for-byte identical with
  and without the constraint. `not_applied` is empty, so the constraint did reach `solve()`; the parcel
  simply was already where it asked to be.
- Why: the scanned parcel is 40 x 30 x 25, the smallest box in the load, so `loading_order` already
  put it last by volume, and the greedy pass already left it clear at `z: 85`. Moving an item that is
  already last to the end of the order is a no-op. The constraint is satisfied before it is given.
- What we tried: asking the same question of every box the demo load actually buries — seven of them.
  Four give a clean visible change with all nineteen still placed and the fill rate unchanged at 78.2%
  (`B05` fridge, `B02` dishwasher, `B04` oven, `B10` tv). Three — the sofa, the washing machine and the
  wardrobe — come back **unplaced**, because a box that fills the floor has nowhere clear to go once it
  is loaded last, and the fill rate drops to 61–71%. So the sentence to dictate on stage is about one of
  the four, not about the parcel and not about the sofa.
- What we learned: wiring a constraint and demonstrating a constraint are different pieces of work, and
  only the second one needs a load that contradicts it. A unit test mocking the solver would have shown
  `on_top` arriving; the real run is what showed it arriving and mattering not at all. Before promising
  that a feature will be visible in a demo, run it against the demo's own data and look at the
  before-and-after, not at the status code.
- A second thing the real run found, unrelated and worth keeping: a `uvicorn` was already listening on
  port 8000 from another session, so the first `/constraints` call answered `503 ANTHROPIC_API_KEY is
  not set` from a server nobody intended to test. The message was right and the server was the wrong
  one. Bind to a port you started yourself before concluding anything about configuration.
- Related branch / PR: `feature/plan-passes-on-top`, `SA-20`.

---

## 2026-10-02 — A geocoder that answers 200 with the wrong continent

- What happened: `HY-17` added an "Est. route time" tile to `/app`, to be filled from `POST /route`
  rather than from the mockup's `4h 20m`. The round was still the Madrid fixture, and `POST /route`
  did not refuse it. Asked for `Depot-Centro`, `Chamberí` and `Salamanca`, the Base Adresse
  Nationale returned **200** with a depot in Sainte-Rose (Guadeloupe), Chambéry, and a street in
  Saint-Aubin-d'Écrosville, and OSRM dutifully drove between them: a 68 362-second leg, about
  nineteen hours, for a van crossing Madrid.
- Why: the geocoder's failure mode is a near match, not an error. `routing.py` raises
  `AddressNotFound` only on an empty feature list, and a fuzzy French match for a Spanish district
  name is not an empty list. Every layer behaved correctly and the number was still nonsense —
  there is no status code for "this answer is about somewhere else".
- What we tried: the tile shipped showing an em dash rather than a figure, on the rule that a number
  QUAI did not compute is never displayed. `SA-21` / #63 then moved the demo round to real Paris
  addresses for its own reasons, which made the lookup correct, and the tile now shows the measured
  **1h 40m** over 37.7 km. The dash remains the in-flight and request-failed state.
- What we learned: "the endpoint returned 200" is not "the endpoint answered the question". Where a
  service resolves free text against a dataset with a boundary — a country, a language, a catalogue
  — the boundary is a silent correctness condition, and the only way to see it is to run the real
  input through and read the answer rather than the status. The honest placeholder is also the cheap
  one: it cost one `—` and it was already right when the data moved underneath it.
- Related branch / PR: `feature/home-dictate-alignment`, `HY-17`; unblocked by `SA-21`, #63.

---

## 2026-10-02 — The merge gate read the review's state, not the review

- What happened: #62 was merged on an approval whose own first line said it was not the one to merge
  on. `SamDana-maker` had reviewed `MORHI11`'s PR as a second opinion and opened with: *"A second
  opinion, not the rotation's review — `Lpk78` is the requested reviewer and CLAUDE.md puts MORHI11's
  work with him. Flagged here so the approval below is not mistaken for the one that merges."* The
  rotation's review was written but not yet posted, and the merge did not wait for it.
- Why: the pre-merge check read `gh pr view --json reviewDecision,reviews`, which returned
  `APPROVED` and a list of approver logins. Both were true. The qualification that mattered existed
  only in the review's prose, and no field in the API carries it. `reviewDecision` answers "is there
  an approval", never "is it the approval this repository's rotation calls for".
- What we tried: the merge stands — the PR was green, approved by a team member, and the rotation's
  own assessment, written before the merge and posted after it, raised no objection. It went onto the
  PR as a comment rather than as an approval, saying plainly that it followed the merge instead of
  gating it: backdating the record would have been a second and worse version of the same mistake.
- What we learned: a status field is a summary, and a summary cannot carry a caveat its author wrote
  in prose beside it. Where a convention lives in a document rather than in branch protection — ours
  lives in the rotation table in `CLAUDE.md` — no API field will enforce it, so the check has to read
  what the reviewer wrote and compare the approver against the table. This is the same shape as the
  review posted on #64 eight minutes earlier, where a PR description claimed the diff did something the
  diff did not: in both cases a summary was trusted in place of the thing it summarises.
- Related branch / PR: #62, `feature/home-dictate-alignment`, `HY-17`; the review it should have
  waited for is now a comment on #62.

---

## 2026-10-02 — Six different speech failures all looked like a button that does nothing

- What happened: on an iPhone over HTTPS, the microphone on `/app/dictate` transcribed nothing and
  said nothing. `HY-14` had wired exactly two events on `SpeechRecognition` — `onresult` and
  `onend` — and `onend` only flips the button back to its resting state. So `not-allowed`,
  `service-not-allowed`, `no-speech`, `network`, `audio-capture`, `aborted`, a `nomatch`, and a
  `start()` that throws `InvalidStateError` synchronously all produced the identical screen: a mic
  button that lights up, goes out, and leaves an empty field.
- Why: the handler that would have reported any of it was never attached. Not a wrong message — no
  message. And `recognition.start()` was called unwrapped inside a click handler, so a synchronous
  throw died there too. The failure was therefore invisible to the only person who could see it,
  standing on a dock with the phone in their hand, and undiagnosable by anyone not holding it.
- What we tried: the diagnosis was made possible before it was attempted, which is the whole shape
  of this entry. `onerror`, `onnomatch` and `onend` now record the browser's own `event.error`
  verbatim, `start()` is wrapped and reports the thrown `name`, `navigator.permissions.query({name:
  "microphone"})` is read where it exists — and where it throws, *that* is recorded, since Safari
  refusing the query is itself a fact about the device. All of it is printed on the screen it
  happened on, in mono, never behind a console a phone does not have.
- The fix that is conditional on the answer: when the browser names a permission problem
  specifically — and only then — the screen offers to call `getUserMedia({audio: true})`, which on
  Safari raises the prompt `SpeechRecognition.start()` sometimes does not. It is not run on load and
  not offered for the other codes, because a prompt nobody asked for would hide which of the two
  APIs the device is unhappy with.
- What we learned: "it does nothing" is not a bug report, it is the absence of one, and the cost is
  paid by whoever is furthest from the keyboard. Every handler an API offers for reporting failure
  is worth wiring before the feature is called done — the asymmetry is stark, since wiring them is
  minutes and not wiring them turned a five-minute fix into a remote debugging session. What the
  code says about which cause it was: nothing yet. That answer arrives with one tap on the phone.
- Related branch / PR: `fix/dictate-speech-diagnostics`, `HY-19`.

---

## 2026-10-02 — A fallback that never fires, and the test that would have proved nothing

- What happened: `HY-19` made the microphone report its own failures, and the next phone test showed
  the transcription running but returning nonsense — a French speech model reading an English
  sentence. The cause was `Dictate.jsx`'s `recognition.lang = navigator.language || "en-US"`: on an
  iPhone set to French we were handing the engine `fr-FR` on purpose.
- Why it read as safe: the `|| "en-US"` looks like the English case is covered, and it is — but it
  fires only when `navigator.language` is empty, which on a real device never happens. **The branch
  that made the line look correct was the branch that never ran.** Deferring to the device locale is
  also the right default nearly everywhere; it is wrong here because what is recognised is not the
  operator's interface language but a fixed English vocabulary — box labels, stop names, and the
  sentences the constraint prompt was scored against.
- The near-miss worth recording: the obvious test is `expect(instance.lang).toBe("en-US")`, and it
  would have been **vacuous**. jsdom's own `navigator.language` is already `"en-US"`, so that
  assertion passes against the broken line exactly as happily as against the fix. It was checked
  rather than assumed — the probe printed `"en-US"` — and the tests now set the device to `fr-FR`
  and `es-ES`, which is what makes the two versions disagree. Mutation-tested both ways: restoring
  the old line fails all three with `'fr-FR'`, `'es-ES'` and `undefined`.
- What we learned, twice over. First: an absent value and a wrong value look identical from outside —
  both give behaviour nobody asked for — but they are found in opposite ways, so read the line before
  searching for it. Second, and the one this project keeps relearning: a test whose environment
  already satisfies the assertion is not a test. This is the fourth time (#14's parser regex, #35's
  stop order, #60's `on_top` pair, `HY-17`'s route-time tile), and every one was caught the same way,
  by changing the code to see whether the test noticed.
- Related branch / PR: `fix/speech-language`, `HY-20`; follows `HY-19`, #68.

---

## 2026-10-04 — A guard that could not fail, inside the pull request that added the guards

- What happened: `HY-22` rewrote `prompts/README.md`, which had described a *planned* prompt tree —
  "none of these version files exist yet" — while five tested versions sat beside it. Seven tests
  were added so the file could not drift again, and the PR reported them mutation-tested: restoring
  the old README produced **9 failures**. `Lpk78` read the sentence describing that result and found
  it wrong on three counts. Two were miscounts — four versions fail rather than five, because
  `v1_zero_shot` is named in *both* READMEs; three invented filenames fail rather than "both". The
  third was the real one: **no test covered the "planned" sentence at all**, because the one written
  for it could not fail.
- Why: the guard was `assertNotIn("none of these version files exist yet", TEXT)`, and in the file it
  was written to catch, that sentence wraps across a line — `"…so none\nof these version files exist
  yet"`. Markdown prose is wrapped at column 100, so the phrase a human reads as one sentence is not
  one string. The substring matched nothing in the old README, nothing in the new one, and the test
  passed in both directions while appearing to stand guard over the exact sentence that caused the
  task.
- What we tried: matched against a whitespace-flattened copy of the file instead of the raw text, and
  added the `**planned**` framing to the same assertion so the tripwire is about the claim rather
  than one phrasing of it. Re-ran the mutation: **10 failures** now, with the tripwire among them,
  and the description in the prompt file corrected to the verified breakdown.
- What we learned: this is the sixth instance of the same shape in this project, and the first one
  shipped *inside* a pull request whose entire subject was a document that described a plan instead
  of what was on disk. The mutation test was run and its total — nine — was reported accurately; what
  was never checked was *which* nine, so a missing guard hid inside a number that looked right.
  Counting failures is not reading them. Where a mutation is cited as evidence, name the assertions
  it trips, not how many.
  The ordinary cause is worth keeping too: a test that searches prose for a sentence has to flatten
  the whitespace first, or it is searching for something the file does not contain.
- Related branch / PR: `docs/prompts-readme-accuracy`, `HY-22`, #75; found in review by `Lpk78`.
