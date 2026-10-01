import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/* HTTPS for the phone demo, and only when it has been set up.
 *
 * A phone reaches this server at the Mac's LAN address, and `getUserMedia` — the camera /login
 * scans with — exists only in a secure context. `http://` on a LAN address is not one, so without
 * this the login screen falls back to a typed code (see documentation/failures.md, 2026-10-01).
 *
 * The certificate is made by mkcert and lives in `.certs/`, which is gitignored: a private key is
 * not committed, and the address it is valid for is this machine's. So this is conditional. With no
 * certificate — CI, a fresh clone, a teammate who has not run mkcert — the server stays on HTTP and
 * everything else still works. See the README, "Phone demo".
 */
const CERTS = fileURLToPath(new URL("../.certs", import.meta.url));

function httpsIfAvailable() {
  const key = path.join(CERTS, "key.pem");
  const cert = path.join(CERTS, "cert.pem");
  if (!fs.existsSync(key) || !fs.existsSync(cert)) return undefined;
  return { key: fs.readFileSync(key), cert: fs.readFileSync(cert) };
}

// The dev server talks to the FastAPI server from #6 on :8000. Nothing secret lives here:
// the Claude key stays server-side, which is why the browser only ever calls our own API.
export default defineConfig({
  plugins: [react()],
  // The brand assets live at the repository root, outside this project, on purpose: there is one
  // copy of the logo and the web app reads it rather than keeping a second.
  server: { port: 5173, https: httpsIfAvailable(), fs: { allow: [".."] } },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.js"],
  },
});
