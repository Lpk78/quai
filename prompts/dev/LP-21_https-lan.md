# LP-21 — HTTPS on the LAN, so the phone can use its camera

- **Author:** `Lpk78`
- **Date:** 2026-10-01
- **Branch:** `feature/https-lan`
- **Issue:** none (follows `LP-20` / #55, which found the problem this one fixes)

## Prompt as typed

```
Parfait, la fenêtre peut enchaîner. Donne-lui le feu vert — elle fait maintenant, dans l'ordre : modif vite.config.js (bloc https conditionnel déjà donné plus haut), relance des deux serveurs en HTTPS, mise à jour de VITE_API_URL et QUAI_LAN_ORIGIN en https://, ligne README, puis commit/push/PR sous l'ID LP-21, reviewer Sam.
```

Preceded by the mkcert setup, run in the same session:

```
brew install mkcert
mkcert -install
cd ~/Desktop/data-project
mkdir -p .certs
mkcert -key-file .certs/key.pem -cert-file .certs/cert.pem localhost 127.0.0.1 ::1 192.168.1.201
echo ".certs/" >> .gitignore
```

## Decisions taken before writing any code

**Branched from `feature/phone-demo-login`, not `main`.** This task changes two things that exist
only on `LP-20` / #55: the README's "Phone demo" section, and `QUAI_LAN_ORIGIN` in `src/server.py` —
the variable whose whole point was that the CORS origin would need its scheme changed one day, which
is today. Branching from `main` would mean writing both again and conflicting with #55 on merge. The
PR therefore targets `feature/phone-demo-login`, and lands on `main` behind it.

**The "https block already given above" was not in this window.** No such block was in the
conversation, so it is written here rather than guessed at from a description of it. It is
conditional on the certificate files being present, which matters: `.certs/` is gitignored, so on any
machine that has not run mkcert — CI, a teammate's checkout — `vite.config.js` must still load and
`npm run dev` must still serve plain HTTP. A config that assumed the files would break the build for
everyone but this Mac.

**The certificate is not committed and never will be.** `.certs/` is in `.gitignore`; `key.pem` is a
private key. The README says how to regenerate it instead, which is also the only thing that works
for a teammate whose LAN address is not `192.168.1.201`.

**The phone still has to be told to trust the CA.** `mkcert -install` installs the root into the
Mac's trust store and nothing else. Without the profile installed *and* enabled on the phone, Safari
refuses the certificate and there is still no camera. That is a step on the device, not in the
repository, so it is documented rather than automated.

## Outcome

- **PR:** https://github.com/Lpk78/quai/pull/58 (reviewer: `SamDana-maker`), based on
  `feature/phone-demo-login` / #55 rather than on `main`
- **What the AI produced:** `httpsIfAvailable()` and the `server.https` wiring in `vite.config.js`,
  the rewritten "Phone demo" section of the README, the `.gitignore` entry, the "Resolved the same
  evening" paragraph in `documentation/failures.md`, and the corrected header comment in
  `Login.jsx`. The mkcert commands themselves were the user's; `mkcert -install` was run by them,
  since it writes a root CA into the system trust store.
- **How it was checked:** `python3 -m unittest discover tests` (349, 1 skipped — no key), `npm test`
  (73) and `npm run build`, the last two run twice — once with `.certs/` present and once with it
  moved aside, which is the state of CI and of every other machine. Then the actual claim:
  `curl --cacert "$(mkcert -CAROOT)/rootCA.pem"` reached both servers over HTTPS with no `-k`, the
  CORS preflight from `https://…:5173` answered 200 while the old `http://` origin answered 400, and
  `isSecureContext` / `getUserMedia` / the scanner's state were read in a real browser at
  `https://192.168.1.201:5173/login`: `true`, present, `scanning`. The camera opens.
- **What was changed by hand:** the decisions, and two corrections to text this change falsified.
  `failures.md` still described the camera problem as unsolved and `Login.jsx`'s header still said
  the phone demo "cannot scan" — both were rewritten in the same commit as the change that made them
  wrong, rather than left for a reviewer to catch. `import.meta.dirname` was the first thing written
  for the certificate path and was replaced: it only exists from Node 20.11, and the README asks for
  Node 20 or later. No test was added, because what changed is dev-server configuration that the
  suites do not reach; that is stated in the PR rather than papered over.
