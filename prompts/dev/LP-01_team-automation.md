# LP-01 — Team automation setup: skills, permissions and tests workflow

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-28
- **Branch:** `docs/team-automation`
- **Recorded afterwards:** yes — written on 2026-09-30 by `LP-16`. This task is the one that created the
  `/task` skill, so the rule that a prompt is saved in `prompts/dev/` did not exist yet while it ran. The
  prompt text below was recovered from this machine's Claude Code session history
  (`~/.claude/projects/-Users-leo-paulkerrinckx-Desktop-data-project/d41c63d9-…jsonl`, 2026-09-28T13:36:57Z)
  and is quoted as typed, not reconstructed from memory.

## Prompt as typed

```
/task Commit the team automation setup: .claude/settings.json, .claude/skills,
.github/workflows/tests.yml and CLAUDE.md, on branch docs/team-automation
```

### Follow-up prompts, same task, same session

```
Answer to your two questions: 1) There is no automatic review bot: we dropped it. The correct files are
in fix-setup/. Switch to docs/team-automation, replace CLAUDE.md with fix-setup/CLAUDE.md and
.claude/skills/review/SKILL.md with fix-setup/review-SKILL.md, delete the fix-setup folder, commit with
the message "Replace the automatic bot review with a reviewer-drafted review", and push to update PR #4.
Mention this change of direction in documentation/journal.md in a second commit. 2) Yes, assign
SamDana-maker as reviewer on PR #3.
```

```
continue
```

```
Agreed. On docs/team-automation, remove the sentence "Do not mention that the text was drafted by an
assistant." from .claude/skills/review/SKILL.md and keep everything else as it is (first-person voice,
reviewer validates before posting). Then add one line to documentation/ai_usage.md saying that reviews
are drafted with the /review skill of Claude Code and read, edited and validated by the human reviewer
before posting. Two commits, push to update PR #4, and resolve item 2 in the PR body.
```

```
On docs/team-automation: replace CLAUDE.md with fix-setup/CLAUDE.md, .claude/skills/task/SKILL.md with
fix-setup/task-SKILL.md, .claude/skills/prompt-version/SKILL.md with fix-setup/prompt-version-SKILL.md,
and prompts/README.md with fix-setup/prompts-README.md; create prompts/dev/.gitkeep; delete fix-setup.
Commit in two steps ("Number and record every development prompt" for the task skill, prompts README and
prompts/dev; "Group product prompts by family" for the prompt-version skill and CLAUDE.md), push to
update PR #4 and add these changes to the PR body.
```

```
1) Keep the example tree in prompts/README.md but mark it clearly as the planned layout ("planned — files
are added as each version is tested"), commit, push to PR #4. 2) Leave the CLAUDE.md split as it is:
rewriting pushed history would need a force push, which our rules forbid.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/4 (reviewer: `SamDana-maker`, merged 2026-09-30)
- **What the AI produced:** the four team skills (`task`, `review`, `fix-review`, `prompt-version`),
  `.claude/settings.json`, `.github/workflows/tests.yml`, the review rotation and target architecture in
  `CLAUDE.md`, and the twelve commits of 2026-09-28 from `67249e6` to `7d8e29a`.
- **What was changed by hand:** the direction on reviews was reversed mid-task — the automatic review bot
  was dropped and replaced by a reviewer-drafted review, and the sentence hiding that the draft comes from
  an assistant was removed on the author's instruction. The corrected files came from a `fix-setup/` folder
  written outside Claude Code. The `CLAUDE.md` split across two commits was left as it was rather than
  rewritten, because fixing it would have needed a force push.
- **Verified:** `ai_usage.md` row of 2026-09-28 records that Claude Code found the tests workflow goes red
  on `main` until the solver branch is merged, and that this was documented in `failures.md` instead of
  being hidden.
- **Not covered by this record:** the 2026-09-30 review round on PR #4 is a separate task, `LP-04d`.
