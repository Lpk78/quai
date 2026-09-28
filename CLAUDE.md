# Instructions for AI coding assistants

Any AI assistant working in this repository (Claude, Copilot, ChatGPT, Cursor…) must follow
`CONTRIBUTING.md`. In short:

- Never commit to `main`. Work on a named branch (`feature/`, `experiment/`, `prompt/`, `fix/`, `docs/`).
- Small commits, one coherent change each, messages that complete "This commit will…".
- Everything written in the repository is in English: code, comments, docs, prompts, commit messages, PRs, reviews.
- The LLM in QUAI never computes placement: it translates constraints into validated JSON and explains
  solver output. Do not propose designs that break this rule.
- A new prompt version is a new file in `prompts/`; never overwrite an old version.
- Never invent evaluation scores. Record only results that were actually run.
- Never write secrets in the repository; use `.env`.
- Log notable AI help in `documentation/ai_usage.md` and failures in `documentation/failures.md`.
- Prefer the simplest code and the simplest prompt that work.

## Team and review rotation

Every PR gets one reviewer, chosen from the author's GitHub login (`gh api user -q .login`):

| Author | Area | Reviewer |
|---|---|---|
| `Lpk78` (Léo-Paul) | AI layer: prompts, evaluation, constraint translation | `SamDana-maker` |
| `SamDana-maker` (Sam) | Server: solver, FastAPI, Supabase database, routes | `MORHI11` |
| `MORHI11` | Interface: mobile app, 3D view, operator mode, landing page | `Lpk78` |

Every PR gets an automatic first-pass review from Claude (GitHub Action `claude-review.yml`) and runs the tests (`tests.yml`).
The author never merges their own PR. The human reviewer reads the automatic review, then approves and merges (`/review`).

## Team skills

- `/task <description or #issue>` — branch, code, tests, commits, push, filled PR, reviewer assigned.
- `/review <PR number>` — explain the PR and the automatic review, then approve and merge after the reviewer says yes.
- `/fix-review` — address review comments on the same branch.
- `/prompt-version <change>` — new prompt file, evaluation on the same inputs, real scores, PR.

## Architecture (target)

- `src/quai/` — Python core: models, validity checks, deterministic solver.
- Server: FastAPI exposing the solver and the constraint translation (Claude API, key server-side only).
- Web app: React + Vite, installable on a phone (PWA), 3D view with Three.js; `/` landing page, `/app` application.
- Data and accounts: Supabase (vehicles, items, routes, stops, plans).
