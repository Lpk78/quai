import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server talks to the FastAPI server from #6 on :8000. Nothing secret lives here:
// the Claude key stays server-side, which is why the browser only ever calls our own API.
export default defineConfig({
  plugins: [react()],
  // The brand assets live at the repository root, outside this project, on purpose: there is one
  // copy of the logo and the web app reads it rather than keeping a second.
  server: { port: 5173, fs: { allow: [".."] } },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./src/test-setup.js"],
  },
});
