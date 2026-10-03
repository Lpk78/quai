# SA-28 — Documenting the pull requests left open

- **ID**: SA-28
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-04
- **Branch**: `docs/open-pull-requests`
- **Issue**: none — section 11 of the specification credits abandoned work that is documented
- **Reviewer**: `MORHI11`

## Prompt as typed

```
/task SA-28 Documenter les trois Pull Requests laissées ouvertes

#36, #38 et #41 sont ouvertes depuis avant la dernière ligne droite. Si #38 est mergée d'ici là, il
n'en restera que deux.

Laissées telles quelles, elles ressemblent à du travail abandonné. La section 11 du cahier des
charges valorise explicitement les idées abandonnées ET documentées : un abandon expliqué rapporte,
un abandon muet coûte.

Mets sur chacune un commentaire court disant ce qu'elle fait, où elle en est, et pourquoi elle n'a
pas été mergée. Pas d'excuse ni de promesse — l'état réel.

Pour #36 en particulier, dis que la page d'accueil annonçait la replanification qu'elle
implémenterait, que #77 a retiré cette annonce plutôt que de forcer la fonctionnalité, et que la PR
reste ouverte comme le travail qui la rendrait vraie. C'est une bonne illustration de l'ordre dans
lequel on a choisi de corriger les choses.

#36 n'a aucun relecteur assigné. Assignes-en un selon la rotation de CLAUDE.md, ou dis explicitement
qu'elle est en pause et pourquoi — mais ne la laisse pas dans un état qui ne veut rien dire.

Ne les merge pas et ne les ferme pas. Elles documentent l'état réel du projet, qui n'est pas « tout
fini ».

Reviewer : MORHI11. PR normale.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/80 (reviewer: `MORHI11`)
- **What the AI produced:** the two pull-request comments, the *Open pull requests* section of
  `documentation/roadmap.md`, and the resolved *Planned experiment* section of
  `documentation/failures.md`.
- **What was changed by hand:** nothing in the committed text. Three judgements decided its content.
- **The task said three pull requests and there were two.** #38 was merged by `MORHI11` at 22:55,
  while this was being prepared — checked before writing rather than after, so no comment was posted
  explaining why a merged pull request had not been merged.
- **Neither "why it was not merged" was taken from the pull request.** #36's reviews were read in
  full and its outstanding blocker reproduced on the branch — a 1000 kg container, a stated
  `max_total_weight` of 50 kg, 60 kg already loaded, and `refuse_impossible_start` accepts it, so
  every waiting box comes back unplaced with no cause named. For #41, the question was whether it was
  obsolete rather than merely unreviewed, so all three of its defects were run against today's
  `main`: `NaN` still accepted at construction, a bare `NaN` literal still answering 500, and
  `max_weight: 0` still refused by the API that the model allows. It is unreviewed, which is a
  different sentence from abandoned, and the comment says the one that is true.
- **#36 was marked paused rather than given a reviewer, which the task allowed either way.** The
  rotation puts `MORHI11` on `SamDana-maker`'s pull requests, and `MORHI11` had already reviewed it
  twice with `CHANGES_REQUESTED`. The outstanding item is the author's, so re-requesting review would
  have put a name in the field at the cost of the page reading "waiting on Hippolyte" when it is
  waiting on me — which is the meaningless state the task asked to avoid, differently dressed.
- **Added mid-task, under an ID that does not exist:** the request to resolve the *Planned
  experiment* section of `failures.md` arrived labelled `SA-27`, and there is no `SA-27` in
  `prompts/dev/`. It was folded in here rather than filed under an invented ID. The question and
  protocol were kept exactly as written instead of being replaced by the results, because having been
  written *before* the run is what stops the protocol looking chosen after the numbers were seen —
  so the stale section turned out to be worth keeping, with only its Results line resolved.
- **Verified:** 422 Python tests, 2 skipped. Neither pull request was merged or closed.
