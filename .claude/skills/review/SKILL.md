---
description: Review a teammate's Pull Request and, once the reviewer agrees, post the review in their own voice, approve and merge.
disable-model-invocation: true
argument-hint: <PR number>
---

Pull Request to review: #$ARGUMENTS

The human running this session is the reviewer. You prepare the review; they decide.

1. `gh pr view $ARGUMENTS`, `gh pr diff $ARGUMENTS` and `gh pr checks $ARGUMENTS`. Check out the branch with `gh pr checkout $ARGUMENTS` and run the tests (`python -m unittest discover tests`, or `python3` if `python` is missing on your machine, plus `npm test` if the web app changed).
2. Check the PR against CONTRIBUTING.md: branch name, commit messages, PR template (Goal / What changed / Please check), tests, no secret or `.env`, no conflict marker, prompts added as new files with real scores, repository text in English, the LLM never computes placement.
3. Explain the PR to the reviewer, in the language they write in, in at most six lines: what it does, why, test results, anything that should block it.
4. Draft the review exactly as the reviewer would write it themselves: first person ("I ran the tests…", "I'd suggest…"), natural and concise, in English. It contains:
   - one or two sentences on what I checked and what I think of the change;
   - one to four comments, each on a file and line, in three parts: **Observation**, **Concern**, **Suggestion** (marked **Blocking** or **Optional**). At least one comment, even on a good PR.
5. Show the draft and ask: "Approve and merge, request changes, or edit the text?"
   - **Approve and merge** → `gh pr review $ARGUMENTS --approve --body "<review>"`, then `gh pr merge $ARGUMENTS --merge --delete-branch`.
   - **Request changes** → `gh pr review $ARGUMENTS --request-changes --body "<review>"`.
   - **Edit** → rewrite with their changes, then ask again.
6. Never post, approve or merge without the reviewer's explicit answer in this conversation. Never approve a PR whose tests fail.
7. `git switch main` and `git pull` at the end.
