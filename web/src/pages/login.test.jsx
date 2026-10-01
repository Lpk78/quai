import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App.jsx";
import Login, { readOperatorCode } from "./Login.jsx";
import { OPERATOR_CARD_ID, OPERATOR_NAME } from "../data/manifest.js";

vi.mock("jsqr", () => ({ default: vi.fn(() => null) }));
// eslint-disable-next-line import/first
import jsQR from "jsqr";

function at(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("reading a card", () => {
  it("accepts the operator's own card", () => {
    expect(readOperatorCode(`QUAI:OPERATOR:${OPERATOR_CARD_ID}`))
      .toEqual({ ok: true, id: OPERATOR_CARD_ID, name: OPERATOR_NAME });
  });

  it("trims what the camera or a paste adds around it", () => {
    expect(readOperatorCode(`  QUAI:OPERATOR:${OPERATOR_CARD_ID}\n`).ok).toBe(true);
  });

  it("refuses a code that is not a QUAI card", () => {
    for (const text of ["", "   ", "https://example.com", "QUAI:VAN:12", "OPERATOR:QUAI-OP-7842",
                        "QUAI:OPERATOR:", null, undefined]) {
      expect(readOperatorCode(text)).toEqual({ ok: false, reason: "not-a-card" });
    }
  });

  it("tells a well-formed card for someone else apart from a code it cannot read", () => {
    // Two different problems for the operator: a card QUAI does not know, and not a card at all.
    expect(readOperatorCode("QUAI:OPERATOR:QUAI-OP-0001"))
      .toEqual({ ok: false, reason: "unknown-card", id: "QUAI-OP-0001" });
  });
});

describe("the login screen with no camera, as on the phone demo's http:// address", () => {
  it("says why there is no viewfinder and offers the code instead", () => {
    at("/login");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Scan your operator card");
    expect(screen.getByText(/no camera here/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/operator code/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeDisabled();
  });

  it("signs the operator in by name and opens the app", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    at("/login");
    fireEvent.change(screen.getByLabelText(/operator code/i),
      { target: { value: `QUAI:OPERATOR:${OPERATOR_CARD_ID}` } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(new RegExp(OPERATOR_NAME))).toBeInTheDocument();
    // The name is shown first, then the app opens on its own.
    expect(screen.getByRole("link", { name: /continue/i })).toHaveAttribute("href", "/app");

    await vi.advanceTimersByTimeAsync(1500);
    expect(await screen.findByRole("heading", { name: /let’s load/i })).toBeInTheDocument();
    vi.useRealTimers();
  });

  it("keeps the operator on the screen with a reason when the code is not a card", () => {
    at("/login");
    fireEvent.change(screen.getByLabelText(/operator code/i),
      { target: { value: "not a card at all" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(screen.getByRole("alert")).toHaveTextContent(/not a QUAI operator card/i);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Scan your operator card");
    expect(screen.getByLabelText(/operator code/i)).toBeInTheDocument();
  });

  it("names the unknown card rather than refusing in the abstract", () => {
    at("/login");
    fireEvent.change(screen.getByLabelText(/operator code/i),
      { target: { value: "QUAI:OPERATOR:QUAI-OP-0001" } });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent(/not on this van’s round/i);
    expect(alert).toHaveTextContent("QUAI-OP-0001");
  });
});

describe("the login screen with a camera", () => {
  let frames;

  beforeEach(() => {
    jsQR.mockReset();
    jsQR.mockReturnValue(null);
    frames = [];

    // A camera that opens, a video with a frame in it, and a 2D context — none of which jsdom has.
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

  it("opens the rear camera and looks for a card", async () => {
    render(<MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter>);
    expect(await screen.findByText(/looking for a card/i)).toBeInTheDocument();
    expect(navigator.mediaDevices.getUserMedia)
      .toHaveBeenCalledWith({ video: { facingMode: "environment" } });
    expect(screen.queryByText(/no camera here/i)).not.toBeInTheDocument();
  });

  it("signs in on the frame the card appears in, and stops decoding after it", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true, toFake: ["setTimeout", "clearTimeout"] });
    render(<MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter>);
    await screen.findByText(/looking for a card/i);

    frames.shift()();                       // a frame with nothing in it
    expect(screen.queryByText(new RegExp(OPERATOR_NAME))).not.toBeInTheDocument();

    jsQR.mockReturnValue({ data: `QUAI:OPERATOR:${OPERATOR_CARD_ID}` });
    frames.shift()();                       // the frame the card is in

    expect(await screen.findByText(new RegExp(OPERATOR_NAME))).toBeInTheDocument();

    const decodes = jsQR.mock.calls.length;
    frames.shift()?.();                     // the loop keeps being scheduled; it must not decode
    expect(jsQR.mock.calls.length).toBe(decodes);
    vi.useRealTimers();
  });

  it("falls back to the typed code when the camera is refused", async () => {
    navigator.mediaDevices.getUserMedia = vi.fn().mockRejectedValue(new Error("NotAllowedError"));
    render(<MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter>);
    expect(await screen.findByText(/no camera here/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/operator code/i)).toBeInTheDocument();
  });

  it("survives a frame the decoder throws on", async () => {
    render(<MemoryRouter initialEntries={["/login"]}><App /></MemoryRouter>);
    await screen.findByText(/looking for a card/i);

    jsQR.mockImplementation(() => { throw new Error("corrupt frame"); });
    expect(() => frames.shift()()).not.toThrow();
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Scan your operator card");
  });
});
