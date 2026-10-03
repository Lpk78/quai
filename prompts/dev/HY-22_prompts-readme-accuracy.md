# HY-22 — Make prompts/README.md describe the prompts that exist

- **Author:** `MORHI11`
- **Date:** 2026-10-03
- **Branch:** `docs/prompts-readme-accuracy`
- **Issue:** none (housekeeping before the hand-in; `prompts/README.md` is the entry point for the
  Prompt Engineering mark, which is 25 % of it)

## Prompt as typed

```
HY-22 Corriger prompts/README.md et nettoyer les branches

1. prompts/README.md affirme « none of these version files exist yet » alors que prompts/constraint-translation/ contient cinq versions réelles : v1_zero_shot, v2_output_format, v3_response_prefill, v4_few_shot, v5_bounded_examples. Les noms annoncés dans le fichier (v2_structured_output, v3_few_shot, v4_role_separation) n'existent pas. Réécris au présent avec les vrais noms. C'est le fichier qu'on ouvrira pour noter le Prompt Engineering, qui pèse 25 %.

2. Le tableau des familles annonce llm-only-placement comme existante, détenue par SamDana-maker. Elle n'est pas sur main — elle vit sur la PR #38, non mergée. Soit tu retires la ligne, soit tu la gardes en disant explicitement que l'expérience est restée à l'état de PR ouverte, avec le lien vers #38. Ne laisse pas le README promettre un dossier absent.

3. Branches : feature/app-visual-polish est à 0 commit d'avance, entièrement mergée — supprime-la. feature/demo-scenario et docs/fill-repository-details ont un commit d'avance et aucune PR : regarde ce qu'elles contiennent et dis-moi s'il faut ouvrir une PR ou supprimer. Ne supprime rien qui porte du travail non mergé sans me demander.

Reviewer : Lpk78. PR normale.
```

## What the file claimed, and what is on disk

The tree was labelled **planned**, with the sentence "none of these version files exist yet", and
listed `v2_structured_output.md`, `v3_few_shot.md`, `v4_role_separation.md`. None of those three file
names has ever existed. Five versions do, all tracked, all scored:

```
v1_zero_shot.md  v2_output_format.md  v3_response_prefill.md
v4_few_shot.md   v5_bounded_examples.md
```

So the document describing the prompt work was describing a plan that was abandoned in favour of
better work, and understating what was done. For the file a grader opens first, that is the wrong
direction to be wrong in.

## `llm-only-placement` is wrong more deeply than "not merged yet"

The task describes the row as promising a folder that is not on `main` because PR #38 is open. That is
true, and there is a second half: **merging #38 would still not create `prompts/llm-only-placement/`.**
Checked against the branch rather than assumed — `git ls-tree origin/experiment/llm-only-placement --
prompts/` lists only `README.md`, `constraint-translation/v1_zero_shot.md` and `dev/`. The
experiment's prompt is a `SYSTEM_PROMPT` constant in `src/quai/llm_placement.py`.

That is a defensible structure, not an oversight: the family folders exist to hold a *series* of
versions scored against each other, and this experiment was run once to measure a failure, not
iterated. So the row stays — the experiment is real and the roadmap depends on its result — and it
now says where the prompt actually lives, that the work sits on an open PR, and why it has no folder.

## Outcome

(filled at the end)
