import { describe, expect, it } from "vitest";

import { VIEWS, colourFor, sceneScale } from "./LoadScene.jsx";

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


describe("the camera presets (SA-23)", () => {
  it("offers exactly the four views the mockup names", () => {
    expect(Object.keys(VIEWS)).toEqual(["3D", "Top", "Left", "Right"]);
  });

  it("puts every view outside the van, which is two units across", () => {
    // `sceneScale` normalises any vehicle to two units, so a camera inside that box would be inside
    // the load. Each preset has to stand clear of it.
    for (const [name, position] of Object.entries(VIEWS)) {
      const distance = Math.hypot(...position);
      expect(distance, name).toBeGreaterThan(1.5);
    }
  });

  it("keeps Top off the exact vertical", () => {
    // Straight down leaves the camera's up-vector undefined and the view flips unpredictably. The
    // millimetre of offset is deliberate, so it is pinned here rather than looking like a typo.
    const [x, , z] = VIEWS.Top;
    expect(Math.hypot(x, z)).toBeGreaterThan(0);
  });

  it("looks down the two side axes for Left and Right", () => {
    expect(VIEWS.Left[0]).toBe(0);
    expect(VIEWS.Right[2]).toBe(0);
  });

  it("keeps every preset within the orbit's own distance limits", () => {
    // OrbitControls clamps to 1.5–8; a preset outside that would be yanked back the moment the
    // operator touched the scene, which looks like a bug rather than a limit.
    for (const [name, position] of Object.entries(VIEWS)) {
      const distance = Math.hypot(...position);
      expect(distance, name).toBeGreaterThanOrEqual(1.5);
      expect(distance, name).toBeLessThanOrEqual(8);
    }
  });
});
