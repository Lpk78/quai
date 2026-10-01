# HY-14 — App screens: home and dictate

- **Author:** `MORHI11`
- **Date:** 2026-10-01
- **Branch:** `feature/app-home-dictate`
- **Issue:** none (follows `HY-01` / #18, which built the shell these screens fill)

## Prompt as typed

```
HY-14 App screens: home and dictate. Branch from main (the app does not depend on the landing sections in #42). First list what already exists under web/src (app routes, AppShell.jsx, API client) and reuse it; SamDana-maker is adding a VITE_API_URL client and /app/plan in SA-14a, so if it is not on main yet, write a minimal client in web/src/api.js that his can replace. /app = home: today's van, its boxes from the manifest, a big orange "Dictate rules" button. /app/dictate: tap to talk using the Web Speech API (fallback: a text field), show the transcript, send it to POST /constraints, then show each returned constraint as a readable card ("Keep upright: B3") plus the unresolved items, with "Confirm" leading to /app/plan and "Edit" returning to the transcript. Mobile-first (390px), light theme and tokens; the mockup is assets/mockups/app_mockups.png once SA-14a lands, otherwise ~/Downloads/QUAI_DA_FINAL/05_UI/QUAI_app_mockups.png. Mock the API in tests; cover the success, unresolved and error states. HY-13 (sticky nav, /pricing, phone-only login) stays promised and comes right after this.
```

## Decisions taken before writing any code

**SA-14a is not on `main` yet.** No `VITE_API_URL`, no `web/src/api.js`, no `/app/plan` route exist at
the time of writing (checked after pulling `main`). `web/src/api.js` is written as the minimal client the
task asks for, reading `VITE_API_URL` with a `http://127.0.0.1:8000` fallback — the same origin
`vite.config.js` and the README already assume for the FastAPI server. Sam's version replaces it; the
shape of `postConstraints(sentence, manifest)` is what `Dictate.jsx` calls, so his version only has to
keep that signature or the call site is updated alongside it.

**The mockup used is the fallback one.** `assets/mockups/app_mockups.png` does not exist, so
`~/Downloads/QUAI_DA_FINAL/05_UI/QUAI_app_mockups.png` was used for layout and mood only — its copy
("4h 20m Est. route time", a stop count, a navigation step) is not reproduced: `documentation/design.md`'s
copy rules forbid describing route, ETA or navigation as built, and the home screen in this task does not
touch the route at all.

**"Today's van" and "its boxes from the manifest" reuse the reference manifest** from
`documentation/prompt_evaluation.md` (`B1`–`B10`, stops `S1`–`S3`) rather than inventing new demo data,
since that manifest is already the project's one canonical fixture and is what `POST /constraints` will
be scored against.

**`AppShell.jsx` becomes a layout** (header, `<Outlet />`, footer) instead of the page itself, so `/app`
and `/app/dictate` are nested routes under it and both keep one header/footer. Its old placeholder content
(issues #7 and #8) is removed: it described `/app` as empty, which stops being true once this task fills it.

**`copy.test.jsx`'s `PAGES` list gains `/app/dictate`.** The copy rules in `design.md` apply to "the
landing page, the app... and anything published" — a new app route is exactly what that line already
covers, so the existing enforcement is extended rather than left to only check two of three routes.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/47
- **What the AI produced:** `web/src/data/manifest.js` (today's van, reusing the reference manifest),
  `web/src/api.js` (minimal `postConstraints` client), `AppShell.jsx` turned into a layout with nested
  routes, `Home.jsx`, `Dictate.jsx` (tap-to-talk with text-field fallback, the three result states),
  `app.css`, the updates to `pages.test.jsx`, `copy.test.jsx` and `styles.test.js`, the new
  `app.test.jsx` mocking the API client, and the README note.
- **How it was checked:** `npm test` (35 tests, all passing) and `npm run build` run locally.
- **What was changed by hand:** the decisions, not the output. Reusing the reference manifest from
  `documentation/prompt_evaluation.md` as "today's van" instead of inventing demo data. Leaving the
  route/ETA/stop-count content out of the home screen entirely, since it is both out of this task's
  scope and the kind of claim `design.md`'s copy rules single out. Extending `copy.test.jsx` to
  `/app/dictate` rather than leaving the new route unchecked.
