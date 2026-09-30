# HY-10 — Brand kit in the repository and the design documentation

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `docs/brand-kit`
- **Issue:** none (the design work has no issue of its own; it feeds #18, #7 and #8)

## Prompt as typed

```
HY-10 Add the brand kit to the repo from ~/Downloads/QUAI_DA_FINAL: copy the logo SVGs, app icon, tokens.json and the key reference images into assets/brand/, write documentation/design.md (colours, fonts, logo rules, illustration style, UI rules), and apply the tokens to the web app (background #F7F6F3, text #1F2937, navy #102238, primary #FF8A00, Plus Jakarta Sans / Inter / JetBrains Mono). Fix two accessibility issues on the way: text on orange is navy #102238, never white, and small orange text uses #C2410C. Do not add the 5 MB brand guide PDF.
```

## Scope decision taken before writing any code

The task asked for three things: the assets, `documentation/design.md`, and applying the tokens to the
web app. **The third was split off**, because `web/` does not exist yet — `HY-01` (#18) creates it and had
not been run. Building the app here would have put two issues in one Pull Request and left #18 without a
prompt file of its own.

So this task delivers the assets and the documentation, and **#18 applies the tokens as it builds the
app**, reading them from `documentation/design.md`. That is the better order anyway: the app is styled
correctly at birth instead of being retrofitted.

Also decided with the author: the 2.52 MB master brand board is kept at full size, since the kit's own
`CLAUDE_HANDOFF.txt` names it the source of truth. Only the 4.8 MB brand guide PDF is excluded, as asked.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/28
- **What the AI produced:** the `assets/brand/` layout and the copy set, `documentation/design.md`,
  `tests/test_brand.py` (23 tests computing every contrast ratio the document claims), the
  `failures.md` write-up and the README section. It measured the palette rather than trusting it:
  the two accessibility fixes in the task were confirmed numerically (white on orange 2.36:1, navy on
  orange 6.79:1, `#FF8A00` as text 2.19:1, `#C2410C` 4.79:1), and four further AA failures were found
  that the task had not asked about — `success`, `warning`, `error` and the stop-2 green as body text.
  It also found that both supplied wordmark SVGs asked for Arial rather than the brand display font.
- **What was changed by hand:** nothing in the output. Two decisions were taken by the author before
  any code was written: the web-app third of the task was split off to #18 because `web/` does not
  exist yet, and the 2.52 MB master brand board was kept at full size. Each test was checked to fail
  when the rule it guards is reversed.
