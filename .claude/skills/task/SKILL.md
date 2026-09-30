---
description: Do one task end to end — branch, code, tests, small commits, push and a filled Pull Request.
disable-model-invocation: true
argument-hint: <task ID such as SA-04> <what to build, or an issue number>
---

Task: $ARGUMENTS

Follow CONTRIBUTING.md and CLAUDE.md strictly. Work through these steps in order and do not skip any.

1. **Understand.** If the task is an issue number, read it with `gh issue view <n>`. Restate the task in two sentences. If it is ambiguous or too big for one PR (more than about a day of work), stop and propose how to split it before writing code.
2. **Start clean.** Run `git status`. Uncommitted files that belong to this task are kept and carried over; anything unrelated → stop and ask the user what to do with it. Then `git switch main` and `git pull`.
3. **Save the prompt.** The first word of the task is its ID (`LP-nn` for Lpk78, `SA-nn` for SamDana-maker, `HY-nn` for MORHI11). If it is missing, ask for it before doing anything. After creating the branch (step 4), write `prompts/dev/<ID>_<short-slug>.md` containing: the ID, the author's GitHub login, the date, the branch name, the exact task text as typed (in a fenced block), and an empty "Outcome" section. Commit it first, alone, with the message `Record the <ID> development prompt`. At the end, fill "Outcome" with the PR link and one line on what the AI produced and what was changed by hand, in its own commit.
4. **Branch.** Create a branch with the right prefix (`feature/`, `experiment/`, `prompt/`, `fix/`, `docs/`) and a short name that says what it is for.
5. **Build in small steps.** After each coherent step: run the tests (`python -m unittest discover tests`, or `python3` if `python` is missing on your machine, plus `npm test` if the change touches the web app), check `git diff`, then commit only the related files. Messages are in English and complete "This commit will…". Never `update`, `fix`, `changes`, `final`.
6. **Test what you added.** New behaviour gets a test. Never delete or weaken an existing test to make it pass.
7. **Document as you go.** Anything that failed along the way → an entry in `documentation/failures.md`. Notable AI help → a line in `documentation/ai_usage.md` (date, author, what for, what was kept). Changed setup or usage → README.
8. **Push.** `git push -u origin <branch>`.
9. **Open the PR.** Find the author with `gh api user -q .login` and pick the reviewer from the rotation in CLAUDE.md. Then `gh pr create --base main --reviewer <reviewer>` with a clear title and a body with three sections: `## Goal`, `## What changed` (bullet list), `## Please check` (what the reviewer must look at or run). Mention the issue with `Closes #<n>` when there is one.
10. **Report.** Give the user the PR link and a three-line summary they can explain to the professor. Never merge the PR: the reviewer merges it after reading it.
