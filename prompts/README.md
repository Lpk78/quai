# Prompts

Every prompt used in this project is versioned here. Two kinds, two places.

## Product prompts — `prompts/<family>/`

Prompts that QUAI itself sends to Claude at runtime. One folder per prompt family, one file per version,
never overwritten.

One family exists, with five versions. Every one of them was run against the same 26 test sentences
and scored; the scores below are the real ones, from
[`../documentation/prompt_evaluation.md`](../documentation/prompt_evaluation.md):

```
prompts/
└── constraint-translation/           # owner: Lpk78
    ├── v1_zero_shot.md               #  0/26 — instruction and input only
    ├── v2_output_format.md           #  0/26 — v1 with the output envelope specified
    ├── v3_response_prefill.md        # 21/26 — v2's prompt, assistant turn begun with `{`
    ├── v4_few_shot.md                # 22/26 — v3 plus four worked examples
    └── v5_bounded_examples.md        # 21/26 — from v3, three examples, one bounding another
```

The two zeros are not a failed start to skip past: v1 and v2 both produced correct JSON and scored
nothing, because every reply arrived wrapped in a Markdown fence and so parsed as nothing at all. v3
changed no words of the prompt — it begins the assistant's turn with `{`, and 78 replies out of 78
parsed. That is the single largest result in this family, and it came from the delivery rather than
from the wording.

v4 is the best score and is **not** the latest: v5 starts again from v3 rather than from v4, because
v4's fourth example fixed one sentence and broke another. Both are kept, as every version is.

Each file contains: Task, Input, Expected output, the prompt itself, and a change log (what changed from
the previous version, why, which failure it targets). Each family has one owner, so version numbers
never collide. New versions are created with `/prompt-version`.

| Family | Owner | Purpose | Where it is |
|---|---|---|---|
| `constraint-translation` | Lpk78 | Spoken loading constraint → validated JSON | `prompts/constraint-translation/`, five versions |
| `llm-only-placement` | SamDana-maker | Experiment: the LLM places boxes alone, to measure its failures | **No folder here.** Open on [PR #38](https://github.com/Lpk78/quai/pull/38); its prompt is `SYSTEM_PROMPT` in `src/quai/llm_placement.py` |

The second row is deliberately not a folder. A family directory holds a *series* of versions scored
against one another; that experiment was run once, to measure how the model fails when it is asked to
place boxes itself, and the answer became the rule in `CLAUDE.md` that the LLM never computes
placement. One prompt, measured once, with its result written up — so it lives beside the code that
sends it rather than pretending to a version history it does not have.

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

A letter suffix — `LP-04b`, `LP-04c` — marks a task recovered after the fact and placed next to the ID
it followed in time, rather than given a free number that was never assigned to it. It is a separate
task, not another round of the ID it sits beside.
