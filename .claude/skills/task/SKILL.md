---
description: Do one task end to end — branch, code, tests, small commits, push and a filled Pull Request.
disable-model-invocation: true
argument-hint: <what to build, or an issue number such as #4>
---

Task: $ARGUMENTS

Follow CONTRIBUTING.md and CLAUDE.md strictly. Work through these steps in order and do not skip any.

1. **Understand.** If the task is an issue number, read it with `gh issue view <n>`. Restate the task in two sentences. If it is ambiguous or too big for one PR (more than about a day of work), stop and propose how to split it before writing code.
2. **Start clean.** Run `git status`. Uncommitted files that belong to this task are kept and carried over; anything unrelated → stop and ask the user what to do with it. Then `git switch main` and `git pull`.
3. **Branch.** Create a branch with the right prefix (`feature/`, `experiment/`, `prompt/`, `fix/`, `docs/`) and a short name that says what it is for.
4. **Build in small steps.** After each coherent step: run the tests (`python3 -m unittest discover tests`, plus `npm test` if the change touches the web app), check `git diff`, then commit only the related files. Messages are in English and complete "This commit will…". Never `update`, `fix`, `changes`, `final`.
5. **Test what you added.** New behaviour gets a test. Never delete or weaken an existing test to make it pass.
6. **Document as you go.** Anything that failed along the way → an entry in `documentation/failures.md`. Notable AI help → a line in `documentation/ai_usage.md` (date, author, what for, what was kept). Changed setup or usage → README.
7. **Push.** `git push -u origin <branch>`.
8. **Open the PR.** Find the author with `gh api user -q .login` and pick the reviewer from the rotation in CLAUDE.md. Then `gh pr create --base main --reviewer <reviewer>` with a clear title and a body with three sections: `## Goal`, `## What changed` (bullet list), `## Please check` (what the reviewer must look at or run). Mention the issue with `Closes #<n>` when there is one.
9. **Report.** Give the user the PR link and a three-line summary they can explain to the professor. Never merge the PR: the reviewer merges it after reading it.
