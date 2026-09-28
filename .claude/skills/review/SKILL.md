---
description: Review a teammate's Pull Request with the help of the automatic Claude review, then approve and merge in one confirmation.
disable-model-invocation: true
argument-hint: <PR number>
---

Pull Request to review: #$ARGUMENTS

The human running this session is the reviewer. Make the review fast, but keep it real: they must understand what they approve, because the professor asks each student about the PRs they reviewed.

1. `gh pr view $ARGUMENTS --comments` and `gh pr diff $ARGUMENTS`. Read the automatic "Claude review" comment if there is one, and `gh pr checks $ARGUMENTS` for the test results.
2. Explain the PR to the reviewer, in the language they write in, in at most six lines: what it does, why, what the automatic review found, whether the tests pass. Then list any Blocking comment.
3. Ask the reviewer one question: "Approve and merge, request changes, or look closer?"
   - **Approve and merge** → write a short English review note in the reviewer's own words (ask them for one sentence on what they checked if they have not said it), then `gh pr review $ARGUMENTS --approve --body "<note>"` and `gh pr merge $ARGUMENTS --merge --delete-branch`.
   - **Request changes** → post the Blocking points with `gh pr review $ARGUMENTS --request-changes --body "<points>"`, each as Observation / Concern / Suggestion.
   - **Look closer** → walk them through the diff file by file.
4. Never approve or merge without the reviewer's explicit answer in this conversation. Never approve a PR whose tests fail.
5. `git switch main` and `git pull` at the end.
