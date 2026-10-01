import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

import { CSS_PATH, readTokens, toCss } from "../scripts/build-tokens.mjs";

/* design.md: tokens.json is the machine-readable source for colours, and nothing is eyedropped.
   A stylesheet with hand-typed hex values is the same mistake one step later, so it is generated —
   and this is what makes that claim true rather than a comment. */

describe("the generated stylesheet", () => {
  it("matches what the generator produces from tokens.json", () => {
    expect(readFileSync(CSS_PATH, "utf8")).toBe(toCss(readTokens()));
  });

  it("carries the colours the interface is built from", () => {
    const css = readFileSync(CSS_PATH, "utf8");
    const tokens = readTokens().colors;
    expect(css).toContain(`--quai-background: ${tokens.background}`);
    expect(css).toContain(`--quai-navy: ${tokens.navy}`);
    expect(css).toContain(`--quai-orange: ${tokens.primary_safety_orange}`);
  });

  it("carries a secondary text colour that is not the body one", () => {
    const css = readFileSync(CSS_PATH, "utf8");
    expect(css).toContain("--quai-text-muted: #4B5563");
    expect(css).not.toContain(`--quai-text-muted: ${readTokens().colors.text}`);
  });

  it("keeps the darkened orange for text separate from the fill orange", () => {
    const css = readFileSync(CSS_PATH, "utf8");
    expect(css).toContain("--quai-orange-text: #C2410C");
    expect(css).not.toContain("--quai-orange-text: #FF8A00");
  });
});
