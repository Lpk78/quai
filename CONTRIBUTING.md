# Team rules

These rules come from the course guidelines (DAT32-91) and sessions 2 to 5. They apply to every member,
for the whole project. The Git history is graded (25 %), and so is its authenticity.

## 1. Never work directly on `main`

`main` must always run. Every change goes through a branch and a Pull Request.

```bash
git switch main
git pull
git switch -c feature/<short-name>
```

Branch names say what the branch is for:

| Prefix | Use |
|---|---|
| `feature/` | a new capability (`feature/solver-first-fit`) |
| `experiment/` | something we test and may drop (`experiment/llm-only-placement`) |
| `prompt/` | a new prompt version (`prompt/v2-few-shot`) |
| `fix/` | a bug fix |
| `docs/` | documentation only |

Never `test`, `new`, `branch2`, `stuff`.

## 2. Commits

- Small and frequent: one coherent change per commit.
- The message completes the sentence "This commit will…": `Add container model`, `Reject boxes larger than the container`.
- Never `update`, `fix`, `changes`, `final`.
- If the message needs several unrelated "and", split the commit.
- Always check before committing: `git status`, then `git diff`.

## 3. Pull Requests

Push the branch, then open the PR (`gh pr create` or on GitHub). The template asks for:

- **Goal** — why this change;
- **What changed** — the list of changes;
- **Please check** — what the reviewer must look at.

## 4. Reviews

- Every PR is reviewed by **another** member. Nobody merges their own PR without a review.
- Nobody approves a PR they have not read.
- A review comment has three parts, anchored to a line when possible:
  - **Observation** — what you see;
  - **Concern** — why it matters;
  - **Suggestion** — what to do, marked **Blocking** or **Optional**.
- Fixes requested in review go on **the same branch**; the PR updates by itself.

## 5. Conflicts

A conflict means Git refuses to guess. Read the markers, choose the final content, delete every
`<<<<<<<`, `=======`, `>>>>>>>`, then check before staging:

```bash
grep -rn "<<<<<<<\|>>>>>>>" .
```

`git merge --abort` returns to the state before the merge.

## 6. Prompts

- Every prompt lives in `prompts/`, as its own file: `v1_zero_shot.md`, `v2_few_shot.md`, …
- A new version is a new file. Old versions are never overwritten.
- Each version states: what changed, why, which failure it targets.
- Every version is tested on **the same test inputs** with **the same rubric**
  (`documentation/prompt_evaluation.md`). Only real scores are recorded.
- The best prompt is the simplest one that passes the rubric.
- External text (what the user says) is data, never instructions: keep instructions and data separated.

## 7. Failures are part of the work

Every failed prompt, hallucination, wrong output, Git problem or abandoned idea goes into
`documentation/failures.md`: what happened, why, what we tried, what we learned.

## 8. Secrets

API keys live in `.env`, which is ignored by Git. Never paste a key in code, a notebook, a prompt or the README.

## 9. Everyone contributes

Each member commits, opens PRs and reviews. Everyone must be able to explain the whole project,
not only their own part: the professor can ask anyone about any branch, PR or prompt.
