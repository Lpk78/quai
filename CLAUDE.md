# Instructions for AI coding assistants

Any AI assistant working in this repository (Claude, Copilot, ChatGPT, Cursor…) must follow
`CONTRIBUTING.md`. In short:

- Never commit to `main`. Work on a named branch (`feature/`, `experiment/`, `prompt/`, `fix/`, `docs/`).
- Small commits, one coherent change each, messages that complete "This commit will…".
- The LLM in QUAI never computes placement: it translates constraints into validated JSON and explains
  solver output. Do not propose designs that break this rule.
- A new prompt version is a new file in `prompts/`; never overwrite an old version.
- Never invent evaluation scores. Record only results that were actually run.
- Never write secrets in the repository; use `.env`.
- Log notable AI help in `documentation/ai_usage.md` and failures in `documentation/failures.md`.
- Prefer the simplest code and the simplest prompt that work.
