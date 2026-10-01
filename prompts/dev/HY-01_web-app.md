# HY-01 — React + Vite web app, installable on a phone

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/web-app`
- **Issue:** #18

## Prompt as typed

```
HY-01 #18 Create the React + Vite web app in a web/ folder: landing page at / and empty application page at /app, styled from documentation/design.md and following its copy rules (slogan "People talk. We load."), installable as a PWA on a phone, with a README section on how to run it; also add CORSMiddleware to src/server.py so the Vite dev server can call the API
```

## Branch base, decided before writing any code

This branch is cut from `docs/brand-kit` (#28), **not** from `main`, and its Pull Request targets that
branch rather than `main`.

The task says to style the app from `documentation/design.md` and the app needs the brand app icon for
its PWA manifest. Neither is on `main`: both arrive with #28, which is `MERGEABLE` but still waiting on
its review. Branching from `main` would have meant either copying the token values by hand — the exact
"eyedrop the mockup instead of reading the source" mistake `design.md` warns about — or inventing a
second copy of the palette that would then drift.

**When #28 merges, this PR is retargeted to `main`** and its diff becomes only the web app.

## Outcome

- **PR:**
- **What the AI produced:**
- **What was changed by hand:**
