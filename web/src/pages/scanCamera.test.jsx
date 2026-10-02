import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App.jsx";
import { SCANNED_PARCEL } from "../data/manifest.js";

vi.mock("jsqr", () => ({ default: vi.fn(() => null) }));
// eslint-disable-next-line import/first
import jsQR from "jsqr";

/* The camera path on `/app/scan`, with the same simulated camera `login.test.jsx` uses — jsdom has
   no `getUserMedia`, no video frames and no 2D context, so all three are stood up here.
   `scan.test.jsx` is deliberately left alone: it covers the typed path, which this change does not
   touch, and it passes untouched because without `navigator.mediaDevices` the viewfinder reports no
   camera and the field it already tests is still there. */

const LABEL = `QUAI:BOX:${SCANNED_PARCEL.id}`;

function at(path) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);
}

describe("the scan screen with a camera", () => {
  let frames;

  beforeEach(() => {
    window.sessionStorage.clear();
    jsQR.mockReset();
    jsQR.mockReturnValue(null);
    frames = [];

    navigator.mediaDevices = { getUserMedia: vi.fn().mockResolvedValue({ getTracks: () => [] }) };
    Object.defineProperty(HTMLVideoElement.prototype, "videoWidth", { value: 640, configurable: true });
    Object.defineProperty(HTMLVideoElement.prototype, "videoHeight", { value: 480, configurable: true });
    HTMLCanvasElement.prototype.getContext = vi.fn(() => ({
      drawImage: vi.fn(),
      getImageData: () => ({ data: new Uint8ClampedArray(4), width: 640, height: 480 }),
    }));
    // Captured rather than run, so a test decides how many frames the loop gets.
    vi.stubGlobal("requestAnimationFrame", (callback) => {
      frames.push(callback);
      return frames.length;
    });
    vi.stubGlobal("cancelAnimationFrame", vi.fn());
  });

  afterEach(() => {
    delete navigator.mediaDevices;
    vi.unstubAllGlobals();
  });

  it("opens the rear camera, the same one /login asks for", async () => {
    at("/app/scan");
    expect(await screen.findByText(/hold the label inside the frame/i)).toBeInTheDocument();
    expect(navigator.mediaDevices.getUserMedia)
      .toHaveBeenCalledWith({ video: { facingMode: "environment" } });
  });

  it("keeps the typed field, which is the whole point of adding the camera beside it", async () => {
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);
    expect(screen.getByLabelText("Package code")).toBeInTheDocument();
  });

  it("sends a decoded label down the same path as a typed one", async () => {
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockReturnValue({ data: LABEL });
    frames.shift()();

    // The same result card the typed path produces, and the field showing what was read — the
    // camera fills it rather than bypassing it.
    expect(await screen.findByRole("region", { name: "Scanned package" })).toBeInTheDocument();
    expect(screen.getByText("fragile parcel")).toBeInTheDocument();
    expect(screen.getByLabelText("Package code")).toHaveValue(LABEL);
  });

  it("still asks for the confirmation the typed path asks for, rather than jumping ahead", async () => {
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockReturnValue({ data: LABEL });
    frames.shift()();

    // One source of truth beats one gesture saved: reading a label does not load the parcel on its
    // own, exactly as typing the code does not.
    expect(await screen.findByRole("button", { name: /say what to do with it/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /scan the package/i })).toBeInTheDocument();
  });

  it("stops decoding once a label is read, so the result holds still", async () => {
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockReturnValue({ data: LABEL });
    frames.shift()();
    await screen.findByRole("region", { name: "Scanned package" });

    const decodes = jsQR.mock.calls.length;
    frames.shift()?.();
    expect(jsQR.mock.calls.length).toBe(decodes);
  });

  it("reads the next label after an explicit resume, which /login never does", async () => {
    // The one behaviour the shared component gained: `/login` latches for good because a visit signs
    // in once, and a loading screen reads one parcel after another.
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockReturnValue({ data: LABEL });
    frames.shift()();
    await screen.findByRole("region", { name: "Scanned package" });

    fireEvent.click(screen.getByRole("button", { name: /read another label/i }));
    expect(screen.getByLabelText("Package code")).toHaveValue("");
    expect(screen.queryByRole("region", { name: "Scanned package" })).not.toBeInTheDocument();

    const decodes = jsQR.mock.calls.length;
    jsQR.mockReturnValue({ data: "QUAI:BOX:B01" });
    frames.shift()();
    expect(jsQR.mock.calls.length).toBeGreaterThan(decodes);
    expect(await screen.findByText("washing machine")).toBeInTheDocument();
  });

  it("stops on a code that is not a QUAI label too, and still offers the way out", async () => {
    /* The deliberate asymmetry with `/login`, pinned because it is a decision rather than an
       accident. There, a card for someone else does **not** stop the loop: there is no result to
       read, and the operator simply holds up the right card. Here every decoded code produces a
       result card the operator has to read — unreadable, unknown, or the box — so the picture has
       to hold still, whichever of the three it is. Uniform "stop, then resume on purpose" is easier
       to reason about than "stop on a good label, keep going on a bad one", and it is only safe
       because the resume is always on screen next to the refusal. */
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockReturnValue({ data: "https://example.com/not-a-label" });
    frames.shift()();

    expect(await screen.findByRole("alert")).toHaveTextContent(/not a QUAI package label/i);
    const decodes = jsQR.mock.calls.length;
    frames.shift()?.();
    expect(jsQR.mock.calls.length).toBe(decodes);
    // Never a dead end: the camera stopped, and the button that starts it again is right there.
    expect(screen.getByRole("button", { name: /read another label/i })).toBeInTheDocument();
  });

  it("offers no resume button before anything has been read", async () => {
    // It would do nothing: the loop is already running.
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);
    expect(screen.queryByRole("button", { name: /read another label/i })).not.toBeInTheDocument();
  });

  it("survives a frame the decoder throws on", async () => {
    at("/app/scan");
    await screen.findByText(/hold the label inside the frame/i);

    jsQR.mockImplementation(() => { throw new Error("corrupt frame"); });
    expect(() => frames.shift()()).not.toThrow();
    expect(screen.getByRole("heading", { name: /scan the package/i })).toBeInTheDocument();
  });

  it("says the camera was refused, in this screen's words, and keeps the field", async () => {
    navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error("NotAllowedError"));
    at("/app/scan");
    expect(await screen.findByText(/camera was not allowed/i)).toBeInTheDocument();
    // Never /login's copy: that one talks about an operator card.
    expect(screen.queryByText(/operator card/i)).not.toBeInTheDocument();
    expect(screen.getByLabelText("Package code")).toBeInTheDocument();
  });
});

describe("the scan screen with no camera at all", () => {
  it("says there is none and still takes a typed code", async () => {
    // jsdom has no `navigator.mediaDevices`, which is the same state as a device without a camera.
    window.sessionStorage.clear();
    at("/app/scan");
    expect(await screen.findByText(/no camera on this device/i)).toBeInTheDocument();
    expect(screen.getByLabelText("Package code")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /read another label/i })).not.toBeInTheDocument();
  });

  it("names the insecure address when that is why, rather than blaming the device", async () => {
    // The phone demo over plain http:// — `isSecureContext` false and `mediaDevices` absent. The
    // two are fixed differently, so they are not allowed to read the same.
    const secure = Object.getOwnPropertyDescriptor(window, "isSecureContext");
    Object.defineProperty(window, "isSecureContext", { value: false, configurable: true });
    try {
      window.sessionStorage.clear();
      at("/app/scan");
      expect(await screen.findByText(/not on a secure address/i)).toBeInTheDocument();
      expect(screen.getByLabelText("Package code")).toBeInTheDocument();
    } finally {
      if (secure) Object.defineProperty(window, "isSecureContext", secure);
      else delete window.isSecureContext;
    }
  });
});
