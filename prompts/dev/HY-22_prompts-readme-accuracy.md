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

## The branches

`feature/app-visual-polish` — 0 commits ahead of `main`, no open PR using it as head or base. Both
checked before deleting rather than taken from the task. Deleted, local and remote.

The other two were investigated and **not** deleted. Both carry one commit `main` does not have by
SHA, and in both cases the *content* of that commit is already on `main` by another route — so
neither holds unmerged work, but that is a thing to be told rather than assumed on someone's behalf:

| Branch | Its one commit | Already on `main`? |
|---|---|---|
| `feature/demo-scenario` | `523bfd9` "Fix the agreed demo line in the README, and tie it to the box it names" | **Yes** — this is the change that merged as #70 from `fix/demo-line-in-readme`. `main` has both the line (`README.md:369`) and the guard (`TestTheSpokenLine`). The branch is also 34 commits behind, so its README still shows `_to fill_` placeholders. |
| `docs/fill-repository-details` | `2fbd084` "Add third team member to README" | **Yes** — it fills one placeholder row with `@MORHI11`. `main`'s team table has had all three real names and areas for a long time. 492 commits behind. |

Neither needs a PR: opening one would propose reverting `main` to an older README. Both are safe to
delete, and that is a recommendation, not an action taken.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/75 (reviewer: `Lpk78`)
- **What the AI produced:** the rewritten product-prompts section of `prompts/README.md` and the
  seven guards in `tests/test_prompts_readme.py`.
- **How it was checked:** `python3 -m unittest discover tests` — 416, up from 409. Then
  mutation-tested by restoring the previous `prompts/README.md` from `main`: **9 failures**, naming
  each of the five real versions as undocumented, both invented filenames as absent from disk, the
  "planned" sentence, and the unmarked experiment. Guards that pass against the state they were
  written to catch would have been decoration.
- **What was changed by hand:** two things. Keeping the `llm-only-placement` row rather than
  deleting it, once checking the branch showed the experiment has no folder *by design* — the row is
  now about where the prompt really lives, which is more useful than its absence. And writing the
  scores into the tree rather than only linking the evaluation: the summary a grader reads first
  should carry the result, including that the best score is `v4`'s 22/26 and that `v5` deliberately
  restarts from `v3`.
