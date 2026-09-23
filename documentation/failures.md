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
