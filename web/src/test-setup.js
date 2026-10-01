import "@testing-library/jest-dom/vitest";

import { beforeEach, vi } from "vitest";

/* No test talks to the network.
 *
 * `/app/plan` asks the solver for a plan when it mounts, so any test that renders the router at that
 * address would otherwise call `http://127.0.0.1:8000/plan` for real — silently passing on a machine
 * with nothing listening, and hanging or flaking on one that has. A test that needs a plan passes a
 * `loadPlan` of its own; this makes the alternative loud rather than lucky.
 *
 * The rejection is what an unreachable server produces anyway, so a screen under test still shows
 * the failure it is designed to show instead of crashing.
 */
beforeEach(() => {
  vi.stubGlobal("fetch", (url) =>
    Promise.reject(
      new Error(
        `tests must not use the network (fetch ${url}) — pass a fixture or a stub instead`,
      ),
    ),
  );
});
