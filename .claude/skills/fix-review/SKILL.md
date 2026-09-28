---
description: Address the review comments on the current branch's Pull Request.
disable-model-invocation: true
argument-hint: <PR number, optional>
---

PR: $ARGUMENTS (if empty, use the PR of the current branch: `gh pr view`)

1. Read every review comment with `gh pr view --comments` and `gh api repos/{owner}/{repo}/pulls/<n>/comments`.
2. List them for the user: Blocking first, then Optional, with what you plan to do for each. Wait for the user's go-ahead if you disagree with a comment.
3. Stay on the same branch. Fix each point in its own small commit with a clear English message.
4. Run the tests, then `git push`. The PR updates by itself; never open a new PR for review fixes.
5. Reply to each comment with `gh pr comment` saying what changed, or why it was not changed.
