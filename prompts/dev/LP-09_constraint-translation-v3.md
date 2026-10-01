# LP-09 — Third constraint-translation prompt (v3 response prefill)

- **ID**: LP-09
- **Author**: `Lpk78` (Léo-Paul)
- **Date**: 2026-10-01
- **Branch**: `prompt/constraint-translation-v3-response-prefill`
- **Issue**: #12 (roadmap row 10)

## Prompt as typed

```
/prompt-version constraint translation, v3 response prefill: end the request with an assistant turn
"{" and parse "{" + the reply; change nothing else from v2. First check with one real call that the
model accepts an assistant prefill; if it does not, stop and tell me.
```

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/39 (reviewer: `SamDana-maker`)
- **What the AI produced:** `prompts/constraint-translation/v3_response_prefill.md`, the prefill
  mechanism in `src/quai/llm.py` and `src/evaluate_prompt.py` with nine tests, and the results row
  and comparison in `documentation/prompt_evaluation.md`.
- **The gate was run first, as asked.** One real call to `claude-haiku-4-5-20251001` with an assistant
  turn containing `{`: HTTP 200, `stop_reason: end_turn`, continuation `\n  "ok": true\n}`, and
  `{` + continuation parses. Worth recording why it was in doubt: assistant prefill is removed on
  Opus 5, Sonnet 5 and the 4.6/4.7/4.8 family. Haiku 4.5 predates that, so this option exists only
  because of the model `.env` names — on a newer model the fallback to option 1 would have been
  needed.
- **What was changed by hand:** two decisions the task did not specify.

  **Prefill is declared by the version, not by the command line.** The obvious implementation is a
  `--prefill` flag. That would have let anyone re-run v1 with it and record a row that silently was
  not the v1 everyone else scored, and *How a version is run* exists precisely so that two rows are
  comparable. `<!-- PREFILL: { -->` in the version file means every run of a version is the same run.

  **The declared value is stripped.** Reading the marker literally gives `"{ "`, because the comment
  syntax puts a space before `-->`. The API refuses an assistant turn ending in whitespace, so that
  would have failed all 78 calls. The smoke run caught it; a test pins it and the docstring says why
  rather than calling it tidiness.

- **Verified:** 303 tests pass. The run is real — 26 sentences, 3 calls each, 78 calls at temperature
  0 on the same model as v1 and v2. **21/26**, and 78 of 78 replies parsed where the same prompt text
  produced 156 fenced replies out of 156 across the two previous versions.
- **The useful second result:** the v1 fence-stripped diagnostic predicted Total 21/26 and v3 measured
  21/26, with six of eight criteria identical. That figure was the one thing in the document a
  reviewer could not check, and three versions of deliberately not fixing the five failures it
  pointed at is what made it checkable in the end.
- **Judgement call for the reviewer:** whether `POST /constraints` (#19) is now obliged to build the
  request the same way. The decision on #37 says it is, and this row only means what it says if the
  server prefills too. Raised in the PR.
