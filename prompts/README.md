# Prompts

Every prompt used in this project is versioned here. Two kinds, two places.

## Product prompts — `prompts/<family>/`

Prompts that QUAI itself sends to Claude at runtime. One folder per prompt family, one file per version,
never overwritten:

```
prompts/
└── constraint-translation/
    ├── v1_zero_shot.md
    ├── v2_structured_output.md
    ├── v3_few_shot.md
    └── v4_role_separation.md
```

Each file contains: Task, Input, Expected output, the prompt itself, and a change log (what changed from
the previous version, why, which failure it targets). Scores for every version are in
`../documentation/prompt_evaluation.md`. Each family has one owner, so version numbers never collide.
New versions are created with `/prompt-version`.

| Family | Owner | Purpose |
|---|---|---|
| `constraint-translation` | Lpk78 | Spoken loading constraint → validated JSON |
| `llm-only-placement` | SamDana-maker | Experiment: the LLM places boxes alone (to measure its failures) |

## Development prompts — `prompts/dev/`

Every task given to Claude Code during development, saved automatically by `/task` as
`prompts/dev/<ID>_<slug>.md`, with the author, the date, the branch, the exact prompt and the outcome
(what the AI produced, what was changed by hand, link to the PR).

IDs never collide because each member has a prefix and numbers follow the team task list:

| Prefix | Member |
|---|---|
| `LP-` | Léo-Paul (Lpk78) |
| `SA-` | Sam (SamDana-maker) |
| `HY-` | Hypolyte (MORHI11) |

Example: `/task SA-04 Build a FastAPI server…` creates `prompts/dev/SA-04_fastapi-server.md`.
