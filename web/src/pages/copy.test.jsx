import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "../App.jsx";

/* The copy rules in documentation/design.md apply to "the landing page, the app, the README,
   screenshots, the demo film and anything published". They are prose, and prose drifts — so the
   ones that can be checked are checked, on the rendered text of every page. */

function textOf(path) {
  const { container } = render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
  return container.textContent;
}

const PAGES = ["/", "/app"];
const SLOGAN = "People talk. We load.";

describe("one slogan", () => {
  it("is the approved one, on the landing page", () => {
    expect(textOf("/")).toContain(SLOGAN);
  });

  it("is never joined by a second tagline", () => {
    // The supplied mockups carried "Smart loading. Delivery confidence.", "Smarter Delivery Ahead."
    // and "People. Parcels. Forward." alongside the real one.
    const banned = [
      "Smart loading",
      "Delivery confidence",
      "Smarter Delivery",
      "People. Parcels. Forward",
      "Smart logistics",
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const phrase of banned) expect(text).not.toContain(phrase);
    }
  });
});

describe("the AI never plans the load or orders the stops", () => {
  it("is never claimed in words", () => {
    const banned = [
      /AI[- ]powered/i,
      /the AI (plans|decides|optimis|comput)/i,
      /AI[- ]?(driven|optimised)/i,
      /smart AI/i,
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });
});

describe("no features the app does not have", () => {
  it("promises no route, ETA, tracking or pricing", () => {
    const banned = [
      /optimis(ed|e) route/i,
      /route map/i,
      /live (updates|tracking)/i,
      /\bETA\b/,
      /est\.? route time/i,
      /\bpricing\b/i,
      /\bbilling\b/i,
      /fleet management/i,
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });

  it("says plainly that QUAI does not plan routes", () => {
    expect(textOf("/")).toMatch(/does not plan your route/i);
  });
});
