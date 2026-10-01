# LP-08 — Second constraint-translation prompt (v2 output-format specification)

- **ID**: LP-08
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `prompt/constraint-translation-v2-output-format`
- **Issue**: #12 (roadmap row 10)

## Prompt as typed

```
/prompt-version constraint translation, v2 output-format specification: reply with the raw JSON
object only, no code fence and no prose, exactly matching the schema in src/quai/constraints.py;
change nothing else from v1. Require the PROMPT START / END markers for every file under
prompts/<family>/, as Sam suggested on #30.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/37 (reviewer: `SamDana-maker`)
- **What the AI produced:** `prompts/constraint-translation/v2_output_format.md`, the marker
  requirement in `src/evaluate_prompt.py` with four tests, the results row and comparison, and the
  `documentation/failures.md` entry.
- **What was changed by hand:** two things, both about keeping the experiment honest.

  **The file was spliced, not rewritten.** v2's prompt is v1's text with one section replaced — the
  head and tail were extracted, the new *Output* section inserted between them, and both halves
  checked byte for byte against v1 before the file was written. Retyping the prompt would have left
  dozens of incidental wording differences, and the score would then have been attributable to
  nothing in particular. The whole value of v2 is that exactly one thing changed.

  **The literal fence token came out of my own first draft.** The new section originally read "no
  code fence, no ```json" — which put the exact string we do not want emitted inside the prompt that
  forbids it. That is v1's mistake one step along: v1 forbade a fence and then demonstrated one. The
  wording is now "no code fence, no language label", and v2's prompt contains no triple backtick
  anywhere, which is checked.

- **The hypothesis, written before the run:** v1's prompt said "no code fence" and then showed the
  output shape inside a triple-backtick block. 78 fenced replies out of 78 is too consistent for
  reluctance; it looks like an instruction and an example disagreeing, with the example winning.
- **What is deliberately not fixed:** the five non-fence failures in the v1 diagnostic — T10, T16,
  T17, T20, T24, all in `unresolved`. Leaving them lets this run test the diagnostic itself: if they
  persist at about the same rate, the fence-stripped 21/26 was measuring something real, and v3 has
  an evidenced brief. If they move, the diagnostic was not sound and nothing should be built on it.
- **Verified:** the run is real — 26 sentences, 3 calls each, 78 calls to
  `claude-haiku-4-5-20251001` at temperature 0, same model and temperature as v1, so the two rows
  are comparable. The transcript is in `outputs/evaluations/` (Git-ignored).
- **Also in this task:** the marker rule Sam raised on #30. A version file with no markers at all was
  sent whole, silently, which is the failure the markers exist to prevent — unlike a half-open marker,
  which already failed loudly. Files under `prompts/<family>/` must now mark their prompt;
  `prompts/dev/` is excluded and a bare file elsewhere is unaffected.
