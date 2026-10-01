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

describe("the planned-not-shipped badge", () => {
  /* The one element on the page whose job is to stop a reader believing something untrue, in the
     combination most likely to fall under AA: small muted text on a faint tint. Checked here the
     way tests/test_brand.py checks every other pair. */
  function flatten(hex, alpha, over) {
    const parse = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
    const [f, b] = [parse(hex), parse(over)];
    return f.map((c, i) => Math.round(c * alpha + b[i] * (1 - alpha)));
  }

  function luminance([r, g, b]) {
    const lin = [r, g, b]
      .map((c) => c / 255)
      .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
  }

  function contrast(a, b) {
    const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
    return (hi + 0.05) / (lo + 0.05);
  }

  it("clears AA for small text on its own tint", () => {
    const rule = landing.match(/\.tag\s*\{([^}]*)\}/)[1];
    expect(rule).toContain("background: rgba(16, 34, 56, 0.07)");
    expect(rule).toContain("color: var(--quai-text-muted)");
    // the tint sits on a white card
    const pill = flatten("#102238", 0.07, "#FFFFFF");
    // Read from tokens.css, not written out: the same drift this project fixed for navy on #28 and
    // for the manifest colours on #33, and --quai-text-muted is derived in build-tokens.mjs rather
    // than in tokens.json, so it is the easier one to change without thinking (#42).
    const tokens = readFileSync("src/tokens.css", "utf8");
    const muted = tokens.match(/--quai-text-muted:\s*(#[0-9A-Fa-f]{6})/)[1];
    const text = [1, 3, 5].map((i) => parseInt(muted.slice(i, i + 2), 16));
    expect(contrast(text, pill)).toBeGreaterThanOrEqual(4.5);
  });
});

describe("the stylesheet", () => {
  it("takes every colour from a token rather than a literal", () => {
    const literals = css.match(/(?:background|color):\s*#[0-9a-f]{3,8}/gi) ?? [];
    expect(literals).toEqual([]);
  });
});
