# LP-03 — An owner and a tracking issue for every phase 1 and 2 task

- **Author:** `Lpk78` (Léo-Paul)
- **Date:** 2026-09-28
- **Branch:** `docs/roadmap-issues`
- **Recorded afterwards:** yes — written on 2026-09-30 by `LP-16`. The `/task` skill was still unmerged on
  `docs/team-automation` when this ran, so no prompt file was written at the time. Text recovered from
  session `d41c63d9-…jsonl`, 2026-09-28T13:50:02Z, and quoted as typed. Note that it was typed as a plain
  message, not as `/task`, which is why it names `CONTRIBUTING.md` and the steps explicitly.

## Prompt as typed

```
Following CONTRIBUTING.md: from an up-to-date main, create a branch docs/roadmap-issues, create one
GitHub issue per task of phases 1 and 2 (the roadmap is in the QUAI plan: solver, API server, 3D view,
box form, test sentences, constraint schema, evaluation script, prompt v1), each assigned to its owner
(Lpk78, SamDana-maker, MORHI11), update documentation/roadmap.md with owners and issue numbers, commit,
push and open a PR with SamDana-maker as reviewer.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/13 (reviewer: `SamDana-maker`, merged 2026-09-30)
- **What the AI produced:** the eight tracking issues, created 2026-09-28 between 13:51:16Z and 13:51:33Z,
  each assigned to the owner given by the rotation, plus the owner and issue columns in
  `documentation/roadmap.md` in commit `aa826a3`:

  | Issue | Task | Assignee |
  |---|---|---|
  | #5 | Phase 1 — Deterministic placement solver | `SamDana-maker` |
  | #6 | Phase 1 — FastAPI server exposing the solver | `SamDana-maker` |
  | #7 | Phase 1 — 3D supervisor view of the plan | `MORHI11` |
  | #8 | Phase 1 — Box entry form | `MORHI11` |
  | #9 | Phase 2 — Test sentences for constraint translation | `Lpk78` |
  | #10 | Phase 2 — JSON schema for translated constraints | `Lpk78` |
  | #11 | Phase 2 — Prompt evaluation script | `Lpk78` |
  | #12 | Phase 2 — First constraint-translation prompt (v1 zero-shot) | `Lpk78` |

- **What was changed by hand:** nothing on 2026-09-28. The whole 2026-09-28 round is the single commit
  `aa826a3`.
- **Verified:** issues #5 to #12 exist with those assignees, and rows 1 to 11 of `roadmap.md` carry an
  issue number.
- **Not covered by this record:** the 2026-09-30 review round on PR #13 — the restored
  constraint-translation row, the prompt family layout, the `SA-05` and `HY-01` issues and the `ai_usage.md`
  merge conflict — was a separate round, logged in `ai_usage.md` for 2026-09-30, and was not given one of
  the six IDs in this backfill.
