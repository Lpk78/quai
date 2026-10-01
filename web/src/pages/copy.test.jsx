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

const PAGES = ["/", "/app", "/app/dictate"];
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

describe("it reads as a product site", () => {
  it("never mentions a school, a course or an assignment", () => {
    // HY-06: the landing page is the product's own site. The project context belongs in the
    // repository, not on the page a delivery team would read.
    const banned = [
      /\bschool\b/i, /\bcourse\b/i, /\buniversity\b/i, /\bstudent\b/i,
      /\bassignment\b/i, /\bsemester\b/i, /\bprofessor\b/i, /\bALBERT\b/,
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });

});

describe("no measured saving is claimed", () => {
  it("promises no time, error, emission or utilisation figure", () => {
    // The supplied mockups carried "Save time", "Fewer errors", "Save hours every day" and
    // "Higher vehicle utilisation". We have measured none of them.
    const banned = [
      /save (time|hours)/i,
      /fewer (errors|delivery issues)/i,
      /\bemissions?\b/i,
      /higher .*utilisation/i,
      /\d+\s*%\s*(faster|fewer|more|less)/i,
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });
});

describe("no features the app does not have", () => {
  /* design.md changed on 2026-10-01: the route view, an estimated time per stop, navigation hand-off
     and delivery progress are planned (server SA-12), so those words are allowed. What stays out of
     scope is still out of scope. */
  it("promises no pricing, billing, fleet management or integrations", () => {
    const banned = [/\bpricing\b/i, /\bbilling\b/i, /fleet management/i, /barcode catalogue/i];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });
});

describe("an unbuilt feature carries its warning", () => {
  /* #34: the badge drifted from "Route view, estimated times and hand-off — planned, not shipped"
     to the single word "planned", which on a card headed "Route and stop order" reads most
     naturally as *planned route* — the one claim design.md forbids. design.md says a planned
     feature described as though it shipped is the same dishonesty one step along, and nothing
     pinned the label, so it drifted. This pins it. */
  it("says the route feature is not shipped, in words that cannot be read as the feature", () => {
    expect(textOf("/")).toContain("planned, not shipped");
  });

  it("puts that warning on every surface that mentions an unbuilt feature", () => {
    /* The first version of this test pinned the label to the route *panel*. The rule is about the
       page: the review of #42 found "Estimated route time" on a second surface with no warning,
       which is the same gap that let the badge drift in the first place. So the test now walks
       every section and asks the question of each one that raises the claim. */
    const { container } = render(
      <MemoryRouter initialEntries={["/"]}>
        <App />
      </MemoryRouter>,
    );
    const CLAIMS = /estimated route time|navigation (app|and live)|hand-?off|delivery progress/i;
    const surfaces = [...container.querySelectorAll("section, .panel")].filter(
      (node) =>
        CLAIMS.test(node.textContent) &&
        // only the innermost surface that raises it, so a parent is not blamed for its child
        ![...node.querySelectorAll("section, .panel")].some((child) =>
          CLAIMS.test(child.textContent),
        ),
    );
    expect(surfaces.length).toBeGreaterThan(0);
    for (const surface of surfaces) {
      expect(surface.textContent).toContain("planned, not shipped");
    }
  });

  it("never labels it with the bare word, which reads as a planned route", () => {
    const badges = [...document.querySelectorAll(".tag")].map((b) => b.textContent.trim());
    for (const badge of badges) expect(badge).not.toBe("planned");
  });
});

describe("QUAI never chooses the route or the stop order", () => {
  /* The architectural rule the relaxed feature rule makes easier to break: the delivery list is an
     input. QUAI shows it, loads to match it, and hands off to a navigation app — it does not compute
     it, reorder it or improve it. */
  it("never claims to optimise or choose a route", () => {
    const banned = [
      /optimis(ed|es|e|ing) (your |the )?(route|delivery order|stop order)/i,
      /best (route|order of stops)/i,
      /faster routes?/i,
      /we (plan|choose|decide) (your |the )?(route|stops?|stop order)/i,
      /AI[- ]optimised/i,
    ];
    for (const page of PAGES) {
      const text = textOf(page);
      for (const pattern of banned) expect(text).not.toMatch(pattern);
    }
  });

  it("says the sentence, not a paraphrase of it", () => {
    /* Asked for on #34: the previous assertion matched /your (delivery list|route|stop order)/i,
       which almost any sentence mentioning the route satisfies. This is the exact line. */
    const SENTENCE = "QUAI follows your delivery list: it never chooses or reorders your stops.";
    expect(textOf("/")).toContain(SENTENCE);
  });
});
