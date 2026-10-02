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

## Outcome

(filled at the end)
