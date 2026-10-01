# LP-20 — Phone demo access and the /login QR screen

- **Author:** `Lpk78`
- **Date:** 2026-10-01
- **Branch:** `feature/phone-demo-login`
- **Issue:** none (follows `HY-14` / #47 and `HY-16` / #53, which built the screens this one is the
  entry point to)

## Prompt as typed

```
LP-20 Two things. (1) Make the dev servers reachable from a phone on the same WiFi: run vite with --host so it binds to the LAN, find the Mac's local IP (ipconfig getifaddr en0), add that origin (http://<LAN-IP>:5173) to the FastAPI CORS allowlist in src/server.py, and confirm with a curl from the shell that OPTIONS succeeds against the LAN IP. Document both URLs (http://<LAN-IP>:5173 and :8000) in a short README note under a "Phone demo" heading. (2) Build a /login screen: camera-based QR scan (use an existing, already-installable JS QR library if one resolves — try installing jsqr or html5-qrcode first and report back if blocked before building anything), reading a code shaped "QUAI:OPERATOR:<id>". On a valid scan, show the operator's name (hardcode QUAI-OP-7842 → "Léo-Paul" for now) and route to /app. On an invalid/unreadable code, show a clear retry state, never a crash. Make / redirect to /login instead of showing the marketing landing page when visited from a phone-sized viewport — actually, just add /login as the new entry point and link "Open the app" to it instead of straight to /app. Mobile-first, reuse tokens.css.
```

## Decisions taken before writing any code

**The library gate was checked first, as asked.** Both candidates resolve against the registry:
`jsqr@1.4.0` and `html5-qrcode@2.3.8`. Nothing was blocked, so no fallback was needed and no decoder
was hand-written. `jsqr` is the one installed: it is a pure decoder — `jsQR(imageData, width, height)`
returns the decoded string or `null` — so the camera element, the framing and the retry state are all
ours to style from `tokens.css`, and the decode step is a plain function a unit test can call without
a browser. `html5-qrcode` renders its own DOM and manages its own camera UI, which would have to be
fought rather than reused, and cannot be driven from jsdom.

**The viewport redirect was not built.** The prompt proposes it and then withdraws it in the same
sentence ("actually, just add /login as the new entry point"). The withdrawn version is the better
one anyway: a `/` that serves different content to a narrow window breaks the landing page's own copy
tests and makes a shared link mean two different things. `/` stays the landing page at every width,
and its "Open the app" call to action points at `/login`.

**`QUAI-OP-7842` is not hardcoded twice.** `web/src/data/manifest.js` already exports
`OPERATOR_NAME` ("Léo-Paul"), ported from `src/demo_fixtures.py` where the same operator carries
`card_id: "QUAI-OP-7842"`. The card id joins it in that file rather than being written fresh in the
login screen, so the demo keeps one source for who the operator is.

**The LAN origin is read from the environment, with this machine's address as the fallback.** A
DHCP-assigned address committed as a literal is wrong for every other machine and for this one after
the next lease. `QUAI_LAN_ORIGIN` overrides it without editing a tracked file; the fallback is
`http://192.168.1.201:5173`, this Mac's address today, so the demo works with nothing exported.

## Outcome
