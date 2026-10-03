# SA-26 — Finishing and merging the LLM-only placement experiment

- **ID**: SA-26
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-03
- **Branch**: `experiment/llm-only-placement` (resumed, `SA-06`'s branch, PR #38)
- **Issue**: none — finishes the experiment the README's founding claim rests on
- **Reviewer**: `MORHI11`

## Prompt as typed

```
SA-26 Finir et merger l'expérience llm-only-placement (PR #38)

Le README affirme que l'architecture repose sur le fait qu'un LLM produit des agencements plausibles
mais géométriquement invalides et non reproductibles, et renvoie vers documentation/. Cette preuve est
sur ta branche experiment/llm-only-placement, PR #38, jamais mergée. Le postulat fondateur du projet
n'est donc pas démontré dans le dépôt.

Reprends #38, rebase sur main — elle a 273 commits de retard, attends-toi à du travail — et termine-la.

Ce que l'expérience doit produire, et uniquement ce qu'elle mesure vraiment :
- le même chargement soumis au modèle seul et au solveur
- plusieurs passages du modèle sur la même entrée, pour montrer la reproductibilité ou son absence
- une vérification géométrique des agencements produits par le modèle, avec le même code de validation
  que le solveur — chevauchements, dépassements du conteneur, boîtes flottantes
- les chiffres réels obtenus, pas une conclusion écrite d'avance

Si le modèle s'en sort mieux que prévu, écris-le. Un résultat qui contredit notre postulat serait un
meilleur document qu'un résultat qui le confirme, et ce serait malhonnête de le cacher.

Le résultat va dans documentation/, et HY-23 a laissé une section vide pour lui dans
llm_failure_modes.md.

Si le rebase s'avère trop lourd ou si l'expérience ne tient pas debout, reviens me voir avant de
t'enferrer — on la documentera comme abandonnée avec sa raison, ce qui reste valorisé par la section 11.

Reviewer : MORHI11. PR normale.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/38 (reviewer: `MORHI11`) — `SA-06`'s branch, resumed
- **What the AI produced:** the rebase and its three conflict resolutions, the `.gitignore` exception
  and the committed run, `TestTheRecordedRun` in `tests/test_llm_placement.py`, the reproduction
  sections of `README.md` and `documentation/failures.md`, and the 2026-10-04 `failures.md` entry.
- **What was changed by hand:** nothing in the committed text. Three judgements shaped it.
- **The experiment was already sound; what was missing was that anyone could check it.** `SA-06` had
  really run twenty calls and really scored them with `quai.checks.find_problems()`, and the write-up
  already carried the contrary result rather than hiding it. But the twenty replies lived in
  `outputs/placement/`, which `.gitignore` excludes, so the table was unfalsifiable by anybody else:
  re-running costs twenty billed calls and returns *different* replies, since temperature 0 is not
  deterministic — which is one of the experiment's own findings. Committing the run (38 KB) and adding
  a test that re-derives every figure from it is the whole of this task's substance.
- **Nothing was re-measured, and that is the honest answer rather than a gap.** `.env` is unreadable
  from this session, so no new model calls were possible. Re-running would not have strengthened the
  result anyway — a second run cannot confirm a non-reproducible one, only sit beside it. What *was*
  verified is that the recorded numbers still hold under today's code: after 273 commits, including
  stop-ordered loading and `on_top`, every published figure re-derives identically, and the 39.3 %
  solver baseline the comparison leans on still holds exactly (10 of 11 placed, mattress left). That
  baseline is stored nowhere, so it was the figure most able to go stale in silence.
- **The task's premise about where the result goes was wrong, and nothing was deleted over it.**
  It said `HY-23` had left an empty section in `documentation/llm_failure_modes.md`. That file exists
  in no branch and in no commit in the history, and there is no `HY-23` task. The section actually
  waiting for this result is `## Planned experiment: LLM-only placement vs solver` in `failures.md`,
  whose `**Results:** _to run and record._` line is exactly the placeholder described — so that is
  where the write-up sits. Checked before writing rather than after, because the alternative was
  creating a file to match a filename nobody had written.
- **One test in here was vacuous first, caught by mutating it rather than by reading it.** The
  fault-total test asserted `str(total) in failures_text`; changing the prose from "41 boxes floating"
  to "40" left it green, because "41" occurs later in the same sentence. It now reads each total out
  of the sentence and compares it to the recount. All of them were then mutated both ways — editing
  the document, and lifting one box 1 cm off the floor in the one valid reply, which turns six red.
  Fifth time this project has shipped an assertion its own environment already satisfied, and the
  fifth time mutation is what found it.
- **Verified:** 436 Python tests, 1 skip. `git diff main HEAD` shows two deleted lines, both rows this
  branch rewrites on purpose, so the three append-only Markdown conflicts cost nothing from `main`.
