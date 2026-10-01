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
