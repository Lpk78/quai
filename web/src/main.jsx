import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App.jsx";

/* The brand faces, self-hosted rather than fetched from Google's CDN. `tokens.css` has named these
   families since the brand kit landed, but nothing ever loaded them, so every screen has been
   rendering in `system-ui` — the fallback — without saying so. Bundled here because the demo runs on
   a WiFi nobody controls: a font that has to be fetched from a third party is a font that may not
   arrive. Only the weights design.md specifies: Plus Jakarta Sans 700 for display, Inter 400/600 for
   text. `--quai-font-data` (JetBrains Mono) is deliberately left on its `ui-monospace` fallback —
   that one degrades to a real monospace face, so it is a far smaller miss than a display font
   silently becoming the system sans. */
import "@fontsource/plus-jakarta-sans/700.css";
import "@fontsource/inter/400.css";
import "@fontsource/inter/600.css";

import "./tokens.css";
import "./index.css";
import "./plan.css";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);

// Registered after load so a failing service worker can never stop the app from rendering.
if ("serviceWorker" in navigator && import.meta.env.PROD) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch((error) => {
      console.warn("[QUAI] service worker registration failed:", error);
    });
  });
}
