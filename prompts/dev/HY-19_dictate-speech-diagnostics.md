# HY-19 — Make the iPhone transcription failure say what it is, then fix it

- **Author:** `MORHI11`
- **Date:** 2026-10-02
- **Branch:** `fix/dictate-speech-diagnostics`
- **Issue:** none (follows `HY-14` / #47, which built the mic, and `LP-21` / #58, which put the phone
  demo on HTTPS and so made the microphone reachable at all)

## Prompt as typed

```
HY-19 Rendre visible pourquoi la transcription échoue sur iPhone, puis la réparer

Testé sur iPhone en HTTPS : le bouton micro ne transcrit rien, sans dire pourquoi. Dictate.jsx utilise window.SpeechRecognition || window.webkitSpeechRecognition, que Safari iOS expose mais gère mal.

PREMIÈRE ÉTAPE, avant toute tentative de correction : rends l'échec visible. Branche onerror, onnomatch, onend et l'état de la permission micro, et affiche à l'écran ce que le navigateur répond réellement — le code d'erreur tel quel, pas un message maison. Aujourd'hui l'échec est silencieux, donc indiagnosticable à distance, et c'est exactement ce qu'on s'interdit partout ailleurs dans ce projet.

ENSUITE seulement, corrige selon ce que l'erreur révèle. Les causes connues sur Safari iOS : start() hors d'un geste utilisateur, permission micro jamais demandée, continuous ou interimResults mal supportés, arrêt automatique après un silence court.

Garde un repli explicite : si la reconnaissance n'est pas disponible, l'écran doit le dire et renvoyer vers le champ texte, où le micro du clavier iOS fonctionne.

Reviewer : Lpk78. PR normale.
```

## What the code said before anything was changed

The symptom is explained by the handlers that are missing rather than by anything exotic. `HY-14`
wired exactly two events:

- **No `onerror` at all.** Every failure the API reports — `not-allowed`, `service-not-allowed`,
  `no-speech`, `network`, `aborted`, `audio-capture` — was dropped on the floor.
- **No `onnomatch`.**
- **`onend` only flips the button back.** It sets `listening` false and clears the ref, so after any
  failure the screen returns to its resting state with no transcript and no message. That *is* the
  reported symptom, and it is produced identically by six different causes.
- **`recognition.start()` is not wrapped.** Safari throws `InvalidStateError` synchronously if
  `start()` is called on a recogniser that is already running; an exception there dies in the click
  handler and never reaches the screen either.

So the first commit is not a guess at the cause: it is removing the reason the cause cannot be seen.

## The honesty limit on this task

There is no iPhone in the session this was written in. The diagnostics are built and tested; **which
error code they will show is not something that could be observed here**, so the second half of the
task — "fix according to what the error reveals" — is done as far as it honestly can be: the changes
applied are the ones that are correct regardless of which of the known causes it turns out to be, and
the panel is what will name the actual one on the dock.

## What the log will say, and what each answer means

The panel prints `mic: <permission> · <events>`. The signatures to expect, and the fix each one
points at — written down now so that reading the phone takes seconds rather than another session:

| What the panel shows | What it means | The fix it points to |
|---|---|---|
| `error: not-allowed` | The microphone was refused, possibly without a prompt ever appearing | Tap **Ask for the microphone** — already built, raises the prompt via `getUserMedia` |
| `error: service-not-allowed` | Safari refused its own speech service, not the mic | Same button; if it persists, the API is unusable on that device and the field is the answer |
| `start requested → end`, no error, no transcript | The session opened and closed without hearing anything — the classic `continuous` behaviour on Safari iOS | Set `continuous = false` for that engine, or restart on `end` while the operator is still holding the session |
| `error: no-speech` | The API ran correctly and heard nothing | Not a code bug; the mic is too far or the room too loud |
| `error: network` | The speech service was unreachable | Nothing in this app fixes it; the field is the answer |
| `start threw: InvalidStateError` | `start()` was called on a running recogniser | Guard the second tap — the throw is now caught, so this is already survivable |
| `mic: query-failed: …` or `permissions-api-absent` | The Permissions API does not answer for `microphone` here | Nothing to fix; it just means the permission line is uninformative on that device |

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/68 (reviewer: `Lpk78`)
- **What the AI produced:** the `onerror`/`onnomatch`/`onend` wiring and the `start()` guard in
  `Dictate.jsx`, the `SpeechReport` panel and its styles, the conditional `getUserMedia` request,
  and the 23 tests in `web/src/pages/dictateSpeech.test.jsx`.
- **How it was checked:** `npm test` and `python3 -m unittest discover tests` after every commit
  (171 web, up from 148; 399 Python, untouched). The panel was then exercised in a real browser:
  tapping the mic produced `mic: prompt · start requested` from the live Permissions API, stayed in
  its neutral style because nothing had failed, and offered no "Ask for the microphone" button —
  which is the behaviour that matters most, since a fix offered for a problem that does not exist is
  the same dishonesty as a failure hidden.
- **What was changed by hand:** the decision not to guess. The task sequenced diagnosis before
  repair, and with no iPhone in the session the repair half cannot honestly be finished — so what
  shipped is every fix that is correct whatever the cause (the `start()` guard, the button no longer
  sticking, the explicit fallback) plus one that is *driven by the error at runtime* rather than by
  a developer's hunch about which browser this is. The table above is the rest of the fix, waiting
  on one tap.
