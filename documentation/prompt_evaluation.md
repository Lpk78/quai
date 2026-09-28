# Prompt evaluation

Method (Session 5): same test inputs + same rubric for every prompt version; record real scores only.

## Task

Translate a spoken loading constraint into strict JSON that the solver can use.

- **Input:** one sentence said by an operator + the list of items currently in the load (the manifest below).
- **Desired output:** JSON matching the output contract below.
- **How we know it is good:** the rubric below.

The model never places a box. It turns speech into constraints; the solver decides positions.

## Reference manifest

Every test sentence is evaluated against this fixed load. It does not change between prompt versions —
if it changed, the scores would stop being comparable.

| id | label | dimensions (cm) | weight (kg) |
|---|---|---|---|
| `B1` | washing machine | 60 × 60 × 85 | 70 |
| `B2` | flat-screen TV | 120 × 15 × 70 | 18 |
| `B3` | pallet of tiles | 120 × 80 × 60 | 900 |
| `B4` | sofa | 220 × 90 × 80 | 55 |
| `B5` | box of glassware | 40 × 40 × 40 | 12 |
| `B6` | fridge | 60 × 65 × 180 | 85 |
| `B7` | paint cans (× 6) | 50 × 30 × 30 | 30 |
| `B8` | mattress | 200 × 140 × 25 | 25 |
| `B9` | toolbox | 60 × 30 × 30 | 22 |
| `B10` | garden table | 150 × 90 × 75 | 40 |

Stops on the route: `S1` Rouen, `S2` Le Havre, `S3` Caen.

## Output contract

This is the shape the expected JSON below targets. Issue #10 turns it into a validated schema in `src/`;
until then this table is the contract, and the two must be kept in step.

```json
{ "constraints": [], "unresolved": [] }
```

Both keys are always present, even when empty. A sentence that yields nothing usable gives an empty
`constraints` list and at least one `unresolved` entry — never an invented constraint.

| Constraint | Fields | Meaning |
|---|---|---|
| `not_stackable` | `item` | Nothing may be placed on top of this item |
| `at_bottom` | `item` | Must sit on the floor of the container |
| `on_top` | `item` | Must be in the top layer |
| `keep_upright` | `item` | May not be laid on its side |
| `unload_at` | `item`, `stop` | Comes off at this stop |
| `load_last` | `item` | Loaded last, so it comes out first |
| `max_stack_height` | `item`, `limit_cm` | Height of whatever is stacked on it, in cm |
| `max_weight_on` | `item`, `limit_kg` | Weight this item can carry, in kg |
| `max_total_weight` | `limit_kg` | Weight limit for the whole load, in kg |

Every length is in centimetres and every weight in kilograms, whatever unit the operator used.

An `unresolved` entry is `{ "text": <the part of the sentence at fault>, "reason": <below>, "question": <what to ask the operator, or null> }`.

| `reason` | Used when |
|---|---|
| `ambiguous` | The sentence has more than one reasonable reading |
| `unknown_item` | It names something that is not in the manifest |
| `unit_missing` | A number is given with no unit and the unit cannot be assumed |
| `contradiction` | The sentence asks for two things that cannot both hold |
| `out_of_scope` | It is not a loading constraint, or it asks for placement |
| `injection_attempt` | It tries to give the model new instructions |

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
