# SA-25 — Bringing `ai_usage.md` and `roadmap.md` up to date

- **ID**: SA-25
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-03
- **Branch**: `docs/final-records`
- **Issue**: none — end-of-project records
- **Reviewer**: `MORHI11`

## Prompt as typed

```
SA-25 Remettre à jour ai_usage.md et roadmap.md. Deux documents décrivent un projet en cours alors
qu'il est fini.

1. documentation/ai_usage.md s'arrête au 2026-09-30. Tout le travail des 1er et 2 octobre manque. Le
fichier dit lui-même qu'il se remplit depuis les sections Outcome de prompts/dev/ : lis-les et ajoute
les lignes manquantes. C'est le document central du critère « AI Usage », qui pèse 25 %.

2. documentation/roadmap.md affiche « In review (#NN) » sur huit lignes dont les PR sont mergées
depuis des jours — lignes 2, 3, 4, 8, 9, 10, 11, et feature/route-display. La ligne 5 dit « 3D view
next » alors qu'elle existe depuis #72, et la ligne 12 dit « To do » alors que load_last et on_top
sont câblés. Passe les statuts à Done avec le numéro de PR.

Vérifie chaque statut contre la PR réelle avant de l'écrire, ne te fie pas à ta mémoire du projet.

Reviewer : MORHI11. PR normale.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/74 (reviewer: `MORHI11`)
- **What the AI produced:** the 34 new rows in `documentation/ai_usage.md`, the eleven status changes
  and the row-12 paragraph in `documentation/roadmap.md`, and the PR's own table of what was checked.
- **What was changed by hand:** nothing in the committed text, but three judgements that changed what
  got written.
- **The instruction not to trust my memory earned its place three times.** The task said to verify
  each status against the real pull request, and `gh pr list --state all` contradicted what I would
  have written from recall in three spots: #48, the 3D view, merged *before* #45, the plan screen it
  was stacked on; `HY-16`'s file links to #52, which is **closed**, while the branch actually landed
  as #53; and `SA-19`'s two vacuous tests were vacuous because a box was left *unplaced*, not because
  of a tie-break. Each of those would have been a plausible, checkable, wrong sentence in the document
  that carries 25 % of the grade.
- **Row 12 was not marked Done, which the task's wording would have allowed.** "`load_last` and
  `on_top` are wired" is true, and `POST /plan` does hand them to the solver — but the row is named
  for constraints *accumulated across sentences*, and `Dictate.jsx` sends only the last sentence's
  result, so a second rule replaces the first. `Dictate.jsx:453` already said in a comment that the
  accumulating list "is roadmap row 12". Marking the row Done would have made the roadmap contradict
  the code. It reads `Partly done (#51, #61)` with a paragraph naming which half exists — the same
  call `Lpk78` made on row 11 in #46.
- **One row was written and then removed.** A row for `SA-05` (#27) was drafted from the roadmap's
  own prose, then deleted on noticing that its "Outcome" section had never been read — every other
  row comes from the file it describes, and one row sourced differently would have been invisible
  later. The same check caught `SA-12` missing entirely: the IDs in the table were diffed against the
  `prompts/dev/` files rather than counted, since 43 rows is the right total for both the right set
  and a wrong one.
- **Two gaps left for the reviewer rather than filled:** pre-October tasks with a task file but no row
  (the preamble dates the rule to `LP-15`, so they may be deliberate), and #65 and #70, which merged
  with no task file and so produce no row under the documented rule.
- **Verified:** 409 Python tests, 1 skip. Documentation only, so `npm test` was not run.
