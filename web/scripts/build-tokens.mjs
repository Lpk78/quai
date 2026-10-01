/**
 * Generate `src/tokens.css` from `assets/brand/tokens.json`.
 *
 * The design system says tokens.json is the machine-readable source for colours and fonts, and that
 * nothing should be eyedropped out of a mockup. Copying hex values into a stylesheet by hand is the
 * same mistake one step later, so the stylesheet is generated instead and `src/tokens.test.js`
 * regenerates it and fails if the committed file drifted.
 *
 * Regenerate after editing the tokens:  npm run build:tokens
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
export const TOKENS_PATH = resolve(here, "../../assets/brand/tokens.json");
export const CSS_PATH = resolve(here, "../src/tokens.css");

/**
 * `#FF8A00` is unreadable as small text on our background (2.19:1). design.md fixes orange text at
 * `#C2410C` (4.79:1). It is derived from the brand primary rather than supplied with it, so it is
 * named here as a derived token rather than invented at each call site.
 */
const ORANGE_TEXT = "#C2410C";

/**
 * Secondary text. The palette has one text colour, and an interface needs a quieter one for
 * supporting copy. Derived rather than invented at each call site, and kept well clear of AA:
 * 6.99:1 on the background, 7.56:1 on a card.
 */
const TEXT_MUTED = "#4B5563";

export function toCss(tokens) {
  const c = tokens.colors;
  const lines = [
    "/* Generated from assets/brand/tokens.json by scripts/build-tokens.mjs. Do not edit by hand. */",
    ":root {",
    `  --quai-background: ${c.background};`,
    `  --quai-surface: ${c.surface};`,
    `  --quai-text: ${c.text};`,
    "",
    "  /* Derived: secondary text, 6.99:1 on the background. See design.md, Accessibility. */",
    `  --quai-text-muted: ${TEXT_MUTED};`,
    "",
    `  --quai-navy: ${c.navy};`,
    `  --quai-orange: ${c.primary_safety_orange};`,
    "",
    "  /* Derived: the primary orange is a fill, never small text. See design.md, Accessibility. */",
    `  --quai-orange-text: ${ORANGE_TEXT};`,
    "",
    `  --quai-success: ${c.success};`,
    `  --quai-warning: ${c.warning};`,
    `  --quai-error: ${c.error};`,
    "",
    ...c.kraft.map((hex, i) => `  --quai-kraft-${i + 1}: ${hex};`),
    "",
    ...c.delivery_stops.map((hex, i) => `  --quai-stop-${i + 1}: ${hex};`),
    "",
    `  --quai-font-display: "${familyOf(tokens.typography.display)}", system-ui, sans-serif;`,
    `  --quai-font-text: "${familyOf(tokens.typography.text)}", system-ui, sans-serif;`,
    `  --quai-font-data: "${familyOf(tokens.typography.data)}", ui-monospace, monospace;`,
    "}",
    "",
  ];
  return lines.join("\n");
}

/** `"Plus Jakarta Sans 700"` -> `"Plus Jakarta Sans"`; the weights are applied where they are used. */
function familyOf(spec) {
  return spec.replace(/\s+[\d/]+$/, "").trim();
}

export function readTokens() {
  return JSON.parse(readFileSync(TOKENS_PATH, "utf8"));
}

if (import.meta.url === `file://${process.argv[1]}`) {
  writeFileSync(CSS_PATH, toCss(readTokens()));
  console.log(`wrote ${CSS_PATH}`);
}
