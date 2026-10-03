# SA-27 — Re-measuring the README's counters after the merges

- **ID**: SA-27
- **Author**: `SamDana-maker` (Sam)
- **Date**: 2026-10-04
- **Branch**: `docs/readme-counters`
- **Issue**: none — follows the second review comment on #76
- **Reviewer**: `MORHI11`

## Prompt as typed

```
/task SA-27 Re-mesurer les compteurs du README après tous les merges

Le README cite plusieurs nombres que la série de merges de cette nuit a rendus faux. Tu en avais déjà
repéré un en relisant #76 : il annonce 49 fichiers dans prompts/dev/ dont 20 en LP-, alors que le
commit 825e164 de cette même PR en faisait déjà 50 et 21.

Depuis, #74, #75, #38, #78 et #80 ont toutes atterri : le nombre de tests est passé à 456 côté
Python, et le nombre de PR mergées, d'entrées de failures.md et de fichiers de tâche a encore bougé.

Reprends chaque nombre chiffré du README et re-mesure-le sur main, par commande et jamais de mémoire.
Corrige ceux qui ont dérivé.

Et tranche une fois pour toutes : un compteur qui périme à chaque merge mérite-t-il d'être dans le
README ? Pour ceux qui ne servent pas directement à comprendre le projet, une formulation durable
vaut mieux qu'un chiffre exact aujourd'hui et faux demain. C'est ton arbitrage — dis ce que tu as
choisi et pourquoi.

Reviewer : MORHI11. PR normale.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/81 (reviewer: `MORHI11`)
- **What the AI produced:** the measurement table on the pull request, the six corrections in
  `README.md`, and `test_the_fill_rate_with_the_scanned_parcel_is_the_one_the_demo_quotes`.
- **What was changed by hand:** nothing in the committed text. The arbitration below is the content.
- **The arbitration, stated once:** a number stays in the README if it describes the product, and
  goes if it only describes how much work was done. The first kind changes when a capability changes,
  which is when a reader wants telling; the second kind is false by the next merge and says nothing
  about QUAI. Kept as digits: the nine/five/four constraint split, the eleven-box load, both fill
  rates, the evaluation table and its method, the 32-second film, the brand rules. Replaced with
  durable wording: the test counts, the merged-PR count, the task-file count, the failures-entry
  count. For the tests the number was not simply deleted — the README now names the two commands that
  print it, which is better evidence than a digit, since it cannot go stale and the reader can run it.
- **Two facts decided it rather than taste.** The counters were wrong within about four hours of
  being written in #76. And the Python count went 456 to 457 *inside this task*, because the task
  added a test: a number that cannot survive the pull request documenting it does not belong in a
  README.
- **The find the task did not ask for.** `78.2%` was not stale from the merges. `SA-24` grew the
  scanned parcel from 40x30x25 to 65x85x85, moving the real figure to `83.3%`, and the README kept
  the old one because the only fill-rate test pinned the *unscanned* plan. The sentence sat three
  lines above the command that prints the correct number. Fixed, and now guarded by a test that reads
  the figure out of `README.md` and compares it to what the solver computes — mutation-tested by
  putting `78.2` back.
- **Also wrong in a way no recount would have caught:** "409 Python (one skipped without an API key)".
  There is no API-key `skipTest` anywhere in the suite. The two real skips are the logo-trace drift
  check and the QR decoder. Checking what the skips *were* rather than only how many there were is
  what turned a stale number into a false sentence.
- **The premise listed five merged pull requests and two were open.** #78 and #80 had not landed —
  #80 is `SA-28`, awaiting review. Verified before measuring, since "measured on `main`" means
  nothing if `main` is assumed.
- **A mistake of my own, mid-task:** mutation-testing the new assertion with `git checkout --
  README.md` reverted five uncommitted counter edits along with the mutation. Noticed by re-grepping
  for the stale strings rather than by trusting the revert, and re-applied. Commit before mutating a
  file that holds uncommitted work.
- **Verified:** 457 Python tests, 2 skipped; 195 web across 14 files.
