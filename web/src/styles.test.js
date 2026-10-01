import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/* The two accessibility rules from design.md, checked where they are actually applied.
   tests/test_brand.py proves the palette supports them; this proves the stylesheet uses them. */

// vitest runs with the web/ project as its working directory. Both stylesheets are read: the base
// rules live in index.css and the landing page's in landing.css, and the two accessibility rules
// have to hold wherever they are applied.
const base = readFileSync("src/index.css", "utf8");
const landing = readFileSync("src/landing.css", "utf8");
const css = base + "\n" + landing;

function ruleFor(selector) {
  const match = base.match(new RegExp(`\\${selector}\\s*\\{([^}]*)\\}`));
  if (!match) throw new Error(`no rule for ${selector}`);
  return match[1];
}

describe("the button, where text meets orange", () => {
  it("puts navy on the orange fill", () => {
    const button = ruleFor(".button");
    expect(button).toContain("background: var(--quai-orange)");
    expect(button).toContain("color: var(--quai-navy)");
  });

  it("never puts white on orange", () => {
    // 2.36:1 — fails AA at every size. The supplied mockups do this; design.md forbids it.
    expect(ruleFor(".button")).not.toMatch(/color:\s*(#fff|#ffffff|white|var\(--quai-surface\))/i);
  });

  it("is at least a 44 px touch target", () => {
    expect(ruleFor(".button")).toContain("min-height: 2.75rem");
  });
});

describe("orange as text", () => {
  it("uses the darkened token where orange is text", () => {
    expect(css).toContain("color: var(--quai-orange-text)");
  });

  it("only uses the fill orange as a colour on icons, never on type", () => {
    /* An inline SVG takes its colour from `color`, through currentColor, so the fill orange is
       allowed there — it is a graphic, not type. Anywhere else, `color: var(--quai-orange)` is the
       2.19:1 combination design.md forbids. */
    const offenders = [];
    for (const [, selector] of css.matchAll(/([^{}]+)\{[^}]*color:\s*var\(--quai-orange\)\s*;/g)) {
      const s = selector.trim().split("\n").pop().trim();
      if (!/svg$|icon|__play|step__n|screen__cta/.test(s)) offenders.push(s);
    }
    expect(offenders).toEqual([]);
  });
});

describe("the stylesheet", () => {
  it("takes every colour from a token rather than a literal", () => {
    const literals = css.match(/(?:background|color):\s*#[0-9a-f]{3,8}/gi) ?? [];
    expect(literals).toEqual([]);
  });
});
