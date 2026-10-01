import { describe, expect, it } from "vitest";

import { identify, readCode } from "./scanCode.js";

const BOXES = [
  { id: "B01", label: "washing machine", length: 85, width: 85, height: 85, weight: 74 },
  { id: "QUAI-BOX-0001", label: "fragile parcel", length: 40, width: 30, height: 25, weight: 8 },
];

describe("readCode", () => {
  it("reads the id out of a QUAI label", () => {
    expect(readCode("QUAI:BOX:QUAI-BOX-0001")).toBe("QUAI-BOX-0001");
    expect(readCode("QUAI:BOX:B01")).toBe("B01");
  });

  it("tolerates the whitespace a scan or a paste brings with it", () => {
    expect(readCode("  QUAI:BOX:B01\n")).toBe("B01");
  });

  it("refuses anything that is not exactly a QUAI label", () => {
    for (const raw of [
      "B01", // the id alone, with no prefix
      "QUAI:BOX:", // the prefix alone
      "quai:box:B01", // the prefix is printed uppercase
      "QUAI:PALLET:B01",
      "https://example.com/QUAI:BOX:B01", // a code that merely contains ours
      "QUAI:BOX:B01 and more",
      "QUAI:BOX:-B01", // an id has to start with a letter or a digit
      "",
    ]) {
      expect(readCode(raw), raw).toBeNull();
    }
  });

  it("does not throw on what a decoder might hand it instead of a string", () => {
    for (const raw of [null, undefined, 42, {}]) {
      expect(readCode(raw)).toBeNull();
    }
  });
});

describe("identify", () => {
  it("returns the box when the manifest knows the code", () => {
    const found = identify("QUAI:BOX:QUAI-BOX-0001", BOXES);
    expect(found.status).toBe("known");
    expect(found.box.label).toBe("fragile parcel");
  });

  it("separates a label we cannot read from one naming a box we do not carry", () => {
    // Two different mistakes, two different sentences on screen: the first is not our label, the
    // second is our label for something that is not on this van.
    expect(identify("not a label", BOXES).status).toBe("unreadable");
    const unknown = identify("QUAI:BOX:B99", BOXES);
    expect(unknown.status).toBe("unknown");
    expect(unknown.id).toBe("B99");
  });
});
