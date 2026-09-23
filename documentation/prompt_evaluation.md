# Prompt evaluation

Method (Session 5): same test inputs + same rubric for every prompt version; record real scores only.

## Task

Translate a spoken loading constraint into strict JSON that the solver can use.

- **Input:** one sentence said by an operator + the list of items currently in the load.
- **Desired output:** JSON matching the constraint schema (to be defined in `src/`).
- **How we know it is good:** the rubric below.

## Rubric (draft — to refine once v1 has been run)

| # | Criterion | Check |
|---|---|---|
| C1 | Output is valid JSON matching the schema | Yes / No |
| C2 | Every item referenced exists in the item list | Yes / No |
| C3 | No constraint is added that the operator did not say | Yes / No |
| C4 | Units are correct (cm, kg) | Yes / No |
| C5 | When the sentence is ambiguous, the output says so instead of guessing | Yes / No |

## Test inputs

_To write before running v1. Aim for 20 to 30 sentences, including ambiguous ones, unit traps,
references to items that do not exist, and one prompt-injection attempt._

## Results

| Version | C1 | C2 | C3 | C4 | C5 | Total | Date | Notes |
|---|---|---|---|---|---|---|---|---|
| v1_zero_shot | | | | | | | | |
