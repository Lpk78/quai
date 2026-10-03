# HY-23 — Write documentation/llm_failure_modes.md

- **Author:** `MORHI11`
- **Date:** 2026-10-04
- **Branch:** `docs/llm-failure-modes`
- **Issue:** none (specification section 12: identify, reproduce or discuss at least one known LLM
  limitation)

## Prompt as typed

```
HY-23 Écrire documentation/llm_failure_modes.md

La section 12 du cahier des charges demande d'identifier, reproduire ou discuter au moins une limite connue des LLM. On en a observé plusieurs sur des cas réels, mais elles sont dispersées dans failures.md au milieu d'une vingtaine d'entrées. Ce document les rassemble et les rend visibles.

Relis documentation/failures.md et prompts/dev/ pour retrouver les cas réels. N'invente aucun exemple : si une catégorie n'a pas de cas reproduit dans ce dépôt, écris qu'elle n'a pas été observée plutôt que de la remplir.

HALLUCINATION — dans une review, l'assistant a affirmé qu'un appel précis existait dans le code. Il n'existait nulle part : le détail avait été inventé pour rendre un compliment concret. Retrouve le cas et cite-le.

PRUDENCE DE FAÇADE — la forme la plus coûteuse : annoncer sa prudence dans l'ouverture (« je n'ai pas lu la diff ligne à ligne ») puis asséner quand même le détail précis. Le marqueur signale le trou au lieu de le combler, et le lecteur retient la précision, pas la prudence. Observée plusieurs fois.

INJECTION DE PROMPT — déjà testée : les phrases de test de constraint-translation incluent des cas d'injection, et les critères C6 et C7 du barème ont été ajoutés pour les scorer. Retrouve ça dans documentation/prompt_evaluation.md.

FENÊTRE DE CONTEXTE — perte d'état en session, consignes tronquées à la transmission.

LE TEST QUI NE REGARDE PAS — c'est le motif le plus fréquent du projet et il mérite sa propre section. Cinq instances connues : #14, #35, #60, HY-20, et le garde de HY-25 qui tenait quatre phrases en dur pendant que la page d'accueil en promettait une cinquième. Vérifie chacune dans le dépôt avant de l'écrire.

Pour chacune : ce qui s'est passé, comment on l'a reproduite, la contre-mesure. Deux phrases méritent d'être écrites telles quelles : on lit la diff, jamais la description — et on change le code pour voir si le test s'en aperçoit.

LE CONTRE-EXEMPLE, instructif : face à « this one is fragile, put it on top », le modèle refuse de deviner et demande de quel colis il s'agit. Une limite bien cadrée produit un refus honnête plutôt qu'une invention.

ATTENTION, le périmètre a changé depuis que cette tâche a été écrite : SA-26 a fini la PR #38, et le résultat de l'expérience llm-only-placement est consigné dans la section « Planned experiment » de failures.md, pas dans un fichier qui l'attendrait. Ne crée pas de section vide pour lui — renvoie vers failures.md, et vérifie où la chose est réellement écrite avant de pointer dessus.

Propose aussi, en fin de document, d'ajouter à CONTRIBUTING.md et à la skill /review la question de relecture permanente : « ce test échoue-t-il si le code est faux ? ». Propose-la, ne la fais pas dans cette PR.

Lie le document depuis le README.

Reviewer : Lpk78. PR normale.
```

## Two premises in the task that the repository does not support

Both checked before writing, because the task's own instruction was to verify before pointing.

**1. `SA-26` has not finished #38, and the experiment's result is not in `failures.md`.** The task
says to point at the "Planned experiment" section as the place the result is recorded. It is not
recorded there:

```
## Planned experiment: LLM-only placement vs solver
- **Results:** _to run and record._
```

`gh api .../pulls/38` returns `open`, `merged=false`. `src/quai/llm_placement.py` does not exist on
`main`, and `notebooks/` is empty. The experiment *has* been run and its numbers are real — 1/10
physically valid plans at temperature 0, 0/10 at temperature 1 — but they live in **PR #38's
description and on its unmerged branch**, not in this repository's `main`. So the document points at
#38 and says plainly that the result is not yet on `main`, rather than pointing readers at a section
that still reads "to run and record".

**2. The hallucination case is not the one described, as far as the record shows.** The task
describes a review asserting that a precise call existed, invented to make a compliment concrete.
Searched systematically rather than from memory: every `name()` in backticks across all 54 review
bodies in the repository's PRs was extracted and checked against `git grep` — **15 names, all of
which exist.** The two most specific compliments were verified individually and both are true
(`from_env` really does raise `NotConfigured` directly for a missing `anthropic` package,
`llm.py:259`; the `refuse_impossible_start` claim on #36 was verified by running it, and the review
says so).

What the record *does* contain is the same failure with the opposite polarity, in the posted review
of #63: a **Concern** asserting that an unknown stop id would render an empty `<strong>`, when both
call sites already read `names[stop.id] ?? stop.id`. It was caught by reading the code before
posting, and the posted review says so in as many words. That is written up as the real case, and the
difference from the task's description is stated rather than smoothed over — if the compliment-shaped
instance exists in a chat transcript rather than in a PR, it is not reachable from this repository and
Lpk78 can point me at it.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/78 (reviewer: `Lpk78`)
- **What the AI produced:** `documentation/llm_failure_modes.md` and the README section that links it.
- **How it was checked:** every citation in the document was resolved against the file it names, in a
  script rather than by eye — `llm.py:259`, `TestTheSpokenLine`, C6/C7 and their wording, T25's
  injection text, the `operator_utterance` block, the four `failures.md` entries, the `13:36:57Z`
  timestamp, and both internal links. Both quotes are verbatim against the posted review bodies.
  409 Python and 195 web tests unchanged — this PR adds documentation only.
- **What was changed by hand:** the decision not to write the hallucination section the way it was
  briefed. The described case — a review inventing a *call* to make a *compliment* concrete — was
  searched for systematically (all 15 backticked `name()`s across 54 review bodies, checked with
  `git grep`; the two most specific compliments verified individually) and is not in the record. What
  is there is the same failure inverted: a fabricated *criticism* in the #63 draft, caught before
  posting. Writing the briefed version would have been an invented example inside a document about
  invention.
- **The second correction:** the brief said `SA-26` had finished #38 and the experiment's result was
  recorded in `failures.md`. #38 is `open`, `merged=false`; `llm_placement.py` is not on `main`; and
  that section still reads `_to run and record._`. The document points at #38 for the numbers and says
  explicitly that they are not established in this repository yet.
