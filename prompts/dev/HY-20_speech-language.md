# HY-20 — Fix the speech recognition language to English instead of the device's

- **Author:** `MORHI11`
- **Date:** 2026-10-02
- **Branch:** `fix/speech-language`
- **Issue:** none (follows `HY-19` / #68, whose diagnostics are what made this visible: once the
  microphone reported for itself, the next failure left was the transcript being wrong rather than
  absent)

## Prompt as typed

```
HY-20 Fixer la langue de la reconnaissance vocale à l'anglais au lieu de celle de l'appareil

Testé sur iPhone : la transcription fonctionne depuis #68, mais le moteur confond les langues — il essaie de lire une phrase anglaise avec un modèle français, et le résultat est inexploitable.

La cause n'est pas une affectation manquante. Dictate.jsx:149 sur main fait :

    recognition.lang = navigator.language || "en-US";

On transmet donc explicitement la langue de l'appareil. Sur un iPhone configuré en français, c'est fr-FR, pendant que la phrase de démo et les noms de colis sont en anglais. Le || "en-US" est un repli qui ne se déclenche presque jamais, ce qui fait paraître la ligne sûre alors qu'elle ne l'est pas.

Remplace-la par une valeur fixe, "en-US", dans une constante nommée au niveau du module, pour qu'on puisse en changer sans la chercher. Toute l'interface et les noms de colis sont en anglais : faire dépendre la reconnaissance du réglage du téléphone rend le comportement imprévisible d'un appareil à l'autre, et c'est exactement ce qui casse aujourd'hui.

Un test asserte que la valeur atteint bien l'instance de reconnaissance — le stub de dictateSpeech.test.jsx ajouté par #68 capture déjà l'instance, donc assertion sur made.instance.lang.

Dans le fichier de prompt, note que le défaut était une mauvaise valeur et non une valeur absente : chercher une affectation manquante qui existe déjà est une perte de temps qu'on peut éviter au suivant.

Reviewer : Lpk78. PR normale.
```

## The defect was a wrong value, not a missing one

Recorded because it is the part that would waste the next person's time. The first reading of this
bug was "`recognition.lang` is never set, so Safari falls back on the device locale" — and someone
acting on that would go looking for a missing assignment, not find one, and conclude the diagnosis
was wrong. The assignment is there:

```js
recognition.lang = navigator.language || "en-US";   // Dictate.jsx:149, before this change
```

We were *handing* the engine the device's language, deliberately, on purpose, in a line that looks
careful. Two things made it read as safe:

1. **The `|| "en-US"` fallback.** It looks like the English default is covered. It fires only when
   `navigator.language` is empty, which on a real phone is never — so the branch that makes the line
   look right is the branch that never runs.
2. **Deferring to the device is usually correct.** Reading the user's locale is good practice almost
   everywhere. It is wrong *here* specifically because what is being recognised is not the user's
   choice of interface language: it is a fixed English vocabulary — box labels, stop names and a
   demo sentence that exist in exactly one language.

The lesson worth carrying: "the value is absent" and "the value is wrong" present identically from
the outside — both give you a behaviour you did not ask for — but they are found in opposite ways.
Read the line before searching for it.

## The test nearly proved nothing

Worth recording beside the above, because it is the same shape of mistake one level up. The obvious
test is:

```js
expect(made.instance.lang).toBe("en-US");
```

and it is **vacuous**. jsdom's own `navigator.language` is `"en-US"` — checked, not assumed — so that
assertion passes against `navigator.language || "en-US"` exactly as happily as against the fixed
value. It would have been a test that could never fail, guarding the one line it was written for.

The three tests set the device language to `fr-FR` and `es-ES` first, which is what makes the broken
and fixed versions disagree. Mutation-tested in both directions: with the old line restored they fail
with `'fr-FR'`, `'es-ES'` and `undefined`; with the fix they pass. The third one removes
`navigator.language` entirely behind a throwing getter, so any future reintroduction of a
device-locale read fails loudly rather than silently.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/71 (reviewer: `Lpk78`)
- **What the AI produced:** the `SPEECH_LANGUAGE` constant and its use in `Dictate.jsx`, the three
  tests in `dictateSpeech.test.jsx`, and the `documentation/failures.md` entry.
- **How it was checked:** `npm test` and `python3 -m unittest discover tests` after each commit (178
  web, up from 174 before the rebase onto `SA-24`; 406 Python, untouched). Then mutation-tested: the
  old line restored makes all three new tests fail, which is the only evidence that they test
  anything.
- **What was changed by hand:** the decision to check jsdom's `navigator.language` before writing the
  assertion rather than after. The task asked for "a test that asserts the value reaches the
  instance", and the straightforward reading of that would have shipped a test that passes on broken
  code. The device-language override is the whole difference between the two.
