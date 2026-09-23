# Prompts

One file per version, never overwritten: `v1_zero_shot.md`, `v2_few_shot.md`, `v3_structured.md`, …

Each file contains:

1. **Task** — what the model must do.
2. **Input** — what it receives.
3. **Expected output** — the exact shape.
4. **The prompt itself.**
5. **Change log** — what changed from the previous version, why, and which failure it targets.

Scores for every version are in `../documentation/prompt_evaluation.md`.
