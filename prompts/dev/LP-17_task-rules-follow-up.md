# LP-17 — Follow-up to PR #4: prompt path, comment permissions, per-task AI usage

- **ID**: LP-17
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-09-30
- **Branch**: `docs/per-task-ai-usage-rule`

## Prompt as typed

```
/task LP-17 Small follow-up to PR #4: update the PR template to say prompts/<family>/, move the gh api
comments and replies permissions to ask, and change the rule so PRs no longer add a row to
documentation/ai_usage.md — AI help is recorded per task in prompts/dev/ and ai_usage.md is filled once at
the end from those files (LP-15). Update CLAUDE.md, CONTRIBUTING.md and the task skill accordingly.
```

## Outcome

- **PR**: https://github.com/Lpk78/quai/pull/20 (reviewer: `SamDana-maker`)
- Claude Code made the five edits and wrote the `CONTRIBUTING.md` §6 paragraph, the `journal.md` entry and
  the PR body, in five commits: the prompt file, the template path, the permission move, the AI-usage rule
  across `CLAUDE.md` / `CONTRIBUTING.md` / the `task` skill / `ai_usage.md`, and the journal.
- Changed by hand: nothing so far. Two points were raised for the reviewer rather than decided alone —
  that moving the `gh api` comment permissions to `ask` undoes `4a1c077` from #4 and brings back a prompt
  per reply in `/fix-review`, and that the existing `ai_usage.md` rows were kept rather than regenerated.
- Tests: `python3 -m unittest discover tests` → 19 tests, OK, after each commit. No code changed.
