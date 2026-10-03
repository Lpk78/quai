# LP-23 — Bring the README to the project's real state

- **Author:** `Lpk78`
- **Date:** 2026-10-03
- **Branch:** `docs/readme-final-state`
- **Issue:** #49 (README has two web app sections since #45)

## Prompt as typed

```
/task LP-23 Remettre le README à l'état réel du projet

Le projet est terminé mais le README décrit la session 2. À corriger avant de donner l'accès à la
professeure.

1. Supprimer la ligne « Status: project scaffold (Session 2 checkpoint). Nothing below "Current
scope" works yet. » C'est faux et c'est la première chose qu'on lit.

2. La section « Current scope » décrit un prototype sans scan et sans LLM. Réécrire en ce qui existe
réellement, ou supprimer.

3. Remplir les quatre rubriques laissées en « To complete » — AI Usage, Main Challenges, Final
Result, Future Improvements. La section 7 du cahier des charges les exige. La matière est dans
documentation/failures.md et prompts/dev/ : ne rien inventer, remonter ce qui existe.

4. Corriger les affirmations périmées : le passage « One thing it does not do yet: the camera » sur
/app/scan est faux depuis la PR #66. Vérifier aussi, et corriger seulement si c'est faux : le
« eleven-box demo load » contre src/demo.py, la mention d'une base Supabase dans la table d'équipe,
et l'existence du script npm run dev:phone dans web/package.json.

5. Il y a deux sections « web app » qui se recouvrent. Les fusionner.

Ne rien affirmer sans l'avoir vérifié dans le code — c'est la règle du projet et c'est un README que
quelqu'un va noter.

Reviewer : SamDana-maker. PR normale.
```

Then, as a follow-up:

```
Complément LP-23 — la rubrique Tools est incomplète. Elle ne dit rien des outils d'IA générative qui
ont produit toute l'identité visuelle. La section 9 du cahier des charges demande de documenter les
outils principaux et de comprendre leur rôle. Ajoute-les, en distinguant bien les trois usages :
l'IA dans le produit, l'IA dans le développement, et l'IA dans le processus créatif.

Demande à Léo-Paul les noms exacts des outils. N'en invente aucun.
```

And the names, confirmed by the author after that question was asked: ChatGPT for the logo, brand
kit, characters, vehicles, environments, screen mockups, component boards and isolated renders;
Claude for the 32-second landing film; some assets retouched by hand after generation. A ten-shot
production method prepared for Higgsfield (`08_HIGGSFIELD/Higgsfield_website_workflow.txt`) was not
used — the film that shipped was made with Claude.

## Decisions taken before writing any code

- **Every sentence was checked, not reread.** Deleting the "nothing works yet" banner is what makes
  this necessary: with the banner there, the page read as a plan, and every present tense was
  understood as future. Without it, the same sentences become claims about today. So the four items
  the task named were checked, and so was everything else that asserted a capability.

- **The task asked to verify three things and correct only what was false.** Two were false
  (Supabase, the camera) and one was true (the eleven-box load, `len(demo.BOXES) == 11`), which was
  left exactly as it was. `npm run dev:phone` exists; what was wrong was its absence from the
  command table.

- **One claim the task did not list was false and is the largest.** The headline promised "live plan
  recomputation" and the Project paragraph said the plan is recomputed live. `src/server.py` exposes
  `/plan`, `/constraints` and `/route`, and nothing in `src/` or `web/src/` replans. Half of the
  product's stated idea is not built, and a README handed over for marking should say so in its
  first paragraph rather than in an issue.

- **No figure was estimated.** Every number in the new sections was measured at the time of writing:
  409 Python tests and 195 web tests, 50 merged Pull Requests, 49 task files, nine constraint types
  accepted against five honoured. Two counts that had been written from memory — "four times" for
  the tests that could not fail, and "twice" for the mockups overruled by the rules — were replaced
  by the real lists once checked, because an invented count is the failure this project has spent
  the week catching.

- **The creative tool names were asked for rather than guessed.** A search for every plausible
  generative tool across the repository returned nothing: no tool is named in `design.md`, the
  journal, or any of the 49 task files. Rather than infer from the output, the question went back to
  the author. The retouching is recorded at the precision given — "some assets" — and not resolved
  into a list, because that list was not supplied.

- **Higgsfield is recorded as prepared and not used.** The workflow document exists; the file that
  shipped was made with Claude. Writing that Higgsfield produced the film would have been false, and
  omitting it entirely would have hidden a real piece of the process.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/76 (reviewer: `SamDana-maker`), closes #49.
- **What the AI produced:** the rewritten sections and the verification commands behind them.
- **How it was checked:** every claim against the code — `src/server.py` for the routes,
  `len(demo.BOXES)` for the demo load, `grep -ri supabase` for the database, `Scan.jsx` and
  `scanCode.js` for the camera, `web/package.json` for the scripts, `CONSTRAINT_FIELDS` against
  `solver.HONOURED` for the nine-versus-five split, and the cited issue and PR numbers one by one.
  `python3 -m unittest discover tests` (409, 1 skipped) and `npm test` (195) after the change.
- **What was changed by hand:** the decisions above, and the two invented counts caught on reread.
- **Found on the way, not fixed here:** the landing page claims "Replans when a parcel is missing"
  and "Replan on incident", features that do not exist. `copy.test.jsx` enforces the rule against
  advertising unbuilt features, but its `CLAIMS` regex does not cover replanning — the same gap that
  test's own comment describes, one feature along. And issue #29 is titled "the five placement
  constraints it currently refuses" when there are four.
