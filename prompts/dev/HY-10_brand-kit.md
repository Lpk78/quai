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

- **PR:**
- **What the AI produced:**
- **What was changed by hand:**
