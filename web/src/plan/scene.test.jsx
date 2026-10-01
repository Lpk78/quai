import { describe, expect, it } from "vitest";

import { colourFor, sceneScale } from "./LoadScene.jsx";

/* What a canvas draws is not something jsdom can see, so these check the parts that are arithmetic:
   the colour a box gets and the scale the van is drawn at. The rest is checked by eye. */

describe("colour by index", () => {
  it("gives neighbouring boxes different colours", () => {
    expect(colourFor(0)).not.toBe(colourFor(1));
  });

  it("cycles rather than running out", () => {
    expect(colourFor(0)).toBe(colourFor(7));
    expect(colourFor(99)).toMatch(/^#[0-9A-F]{6}$/i);
  });

  it("is the same colour for the same box every render", () => {
    expect(colourFor(3)).toBe(colourFor(3));
  });
});

describe("fitting the van in the camera", () => {
  it("scales the longest side to two units whatever the vehicle", () => {
    expect(sceneScale({ length: 300, width: 170, height: 170 })).toBeCloseTo(2 / 300);
    expect(sceneScale({ length: 100, width: 400, height: 100 })).toBeCloseTo(2 / 400);
  });

  it("does not divide by zero on a degenerate container", () => {
    expect(Number.isFinite(sceneScale({ length: 0, width: 0, height: 0 }))).toBe(true);
  });
});
