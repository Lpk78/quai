import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

/* The speech path on `/app/dictate`, with a stand-in for `SpeechRecognition`.
 *
 * `HY-19`: the bug these cover is not a wrong message, it is *no* message. On an iPhone the mic
 * button did nothing and said nothing, and six different causes produced that same screen. So what
 * is asserted here is that each cause reaches the screen as the browser's own code — if these ever
 * pass while the screen stays silent, they are not doing their job.
 *
 * `Dictate.jsx` reads `window.SpeechRecognition` once at module load, so every test re-imports the
 * module with the stub already in place — the same reason `app.test.jsx` does it for the mic panel.
 */

const PANEL = /mic:/;

function recogniser() {
  // Captures the handlers the screen attaches, so a test can fire them as the browser would.
  const made = {
    started: 0,
    startThrows: null,
    start() {
      made.started += 1;
      if (made.startThrows) throw made.startThrows;
    },
    stop: vi.fn(),
  };
  class Stub {
    constructor() {
      made.instance = this;
    }
    start() { made.start(); }
    stop() { made.stop(); }
  }
  made.Stub = Stub;
  return made;
}

async function freshApp() {
  vi.resetModules();
  const { default: App } = await import("../App.jsx");
  return App;
}

async function atDictate(made) {
  vi.stubGlobal("SpeechRecognition", made.Stub);
  const App = await freshApp();
  render(<MemoryRouter initialEntries={["/app/dictate"]}><App /></MemoryRouter>);
  return made;
}

function tapMic() {
  fireEvent.click(screen.getByRole("button", { name: /tap and speak/i }));
}

/* `navigator.permissions` only, rather than replacing `navigator` wholesale: the component reads
   `navigator.language` too, and a stand-in navigator loses it. */
let hadPermissions;
function withPermissions(value) {
  hadPermissions = Object.getOwnPropertyDescriptor(navigator, "permissions");
  Object.defineProperty(navigator, "permissions", { value, configurable: true });
}

/* The device's own language, which `HY-20` stopped the recogniser from following. */
let hadLanguage;
function withDeviceLanguage(value) {
  hadLanguage = Object.getOwnPropertyDescriptor(navigator, "language");
  Object.defineProperty(navigator, "language", { value, configurable: true });
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  if (hadPermissions) Object.defineProperty(navigator, "permissions", hadPermissions);
  else delete navigator.permissions;
  hadPermissions = undefined;
  if (hadLanguage) Object.defineProperty(navigator, "language", hadLanguage);
  hadLanguage = undefined;
});

describe("the dictate screen reporting what the speech API said", () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it("says nothing until the mic has actually been tried", async () => {
    await atDictate(recogniser());
    expect(screen.queryByText(PANEL)).not.toBeInTheDocument();
  });

  it("reports an error with the browser's own code, not a message of ours", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    // What Safari reports when the microphone permission is refused.
    made.instance.onerror({ error: "not-allowed" });

    expect(await screen.findByText(/not-allowed/)).toBeInTheDocument();
  });

  it.each(["service-not-allowed", "no-speech", "network", "audio-capture", "aborted"])(
    "reports the %s code verbatim",
    async (code) => {
      const made = await atDictate(recogniser());
      tapMic();
      made.instance.onerror({ error: code });
      // `error: <code>` rather than the bare code: the advice line for `network` also contains the
      // word "network", and a looser match would pass on the sentence instead of the raw value —
      // which is the one thing this test exists to pin.
      expect(await screen.findByText(new RegExp(`error: ${code}`))).toBeInTheDocument();
    },
  );

  it("reports a code it has no advice for, rather than hiding it", async () => {
    // The reason the raw value is on screen at all: an unknown code is the one most worth seeing.
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onerror({ error: "some-future-webkit-code" });

    expect(await screen.findByText(/some-future-webkit-code/)).toBeInTheDocument();
  });

  it("reports a nomatch, which used to be indistinguishable from a silent failure", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onnomatch();
    made.instance.onend();

    expect(await screen.findByText(/nomatch/)).toBeInTheDocument();
  });

  it("reports a start() that throws synchronously, as Safari's does", async () => {
    const made = recogniser();
    made.startThrows = Object.assign(new Error("already started"), { name: "InvalidStateError" });
    await atDictate(made);
    tapMic();

    expect(await screen.findByText(/InvalidStateError/)).toBeInTheDocument();
    // And the button must come back, rather than being stuck mid-listen on a recogniser that died.
    expect(screen.getByRole("button", { name: /tap and speak/i })).toBeInTheDocument();
  });

  it("shows the ordinary run too, so a working device is distinguishable from a broken one", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onend();

    // "end" with no error is a real answer: the API ran and returned nothing.
    expect(await screen.findByText(/start requested → end/)).toBeInTheDocument();
  });

  it("names the microphone permission the browser reports", async () => {
    const query = vi.fn().mockResolvedValue({ state: "denied" });
    withPermissions({ query });
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onerror({ error: "not-allowed" });

    expect(await screen.findByText(/denied/)).toBeInTheDocument();
    expect(query).toHaveBeenCalledWith({ name: "microphone" });
  });

  it("records that the permissions query itself is unsupported, which Safari does", async () => {
    withPermissions({
      query: vi.fn().mockRejectedValue(Object.assign(new Error("nope"), { name: "TypeError" })),
    });
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onend();

    expect(await screen.findByText(/query-failed: TypeError/)).toBeInTheDocument();
  });
});

describe("the language the recogniser listens in", () => {
  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it("is English on a phone set to French, which is the bug HY-20 fixed", async () => {
    /* The assertion that can actually fail. jsdom's own `navigator.language` is already `en-US`, so
       asserting `en-US` on a default environment passes against the old
       `navigator.language || "en-US"` just as happily as against the fixed value — it would prove
       nothing. Setting the device to French is what makes the two versions disagree: before
       `HY-20` this read `fr-FR`, which is a French model transcribing an English sentence. */
    withDeviceLanguage("fr-FR");
    const made = await atDictate(recogniser());
    tapMic();

    expect(made.instance.lang).toBe("en-US");
  });

  it("is English on a phone set to Spanish too, so it is fixed rather than merely not French", async () => {
    withDeviceLanguage("es-ES");
    const made = await atDictate(recogniser());
    tapMic();

    expect(made.instance.lang).toBe("en-US");
  });

  it("does not read the device language at all", async () => {
    // The property is removed outright: anything still reaching for it would throw rather than
    // quietly fall back, so this fails loudly if the old line ever comes back in another form.
    hadLanguage = Object.getOwnPropertyDescriptor(navigator, "language");
    Object.defineProperty(navigator, "language", {
      get() { throw new Error("navigator.language must not decide what the recogniser listens to"); },
      configurable: true,
    });
    const made = await atDictate(recogniser());
    expect(() => tapMic()).not.toThrow();
    expect(made.instance.lang).toBe("en-US");
  });
});

describe("asking for the microphone, only when the browser blamed the permission", () => {
  const ASK = { name: /ask for the microphone/i };

  beforeEach(() => {
    window.sessionStorage.clear();
  });

  it("offers it on not-allowed", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onerror({ error: "not-allowed" });
    expect(await screen.findByRole("button", ASK)).toBeInTheDocument();
  });

  it("offers it on service-not-allowed", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onerror({ error: "service-not-allowed" });
    expect(await screen.findByRole("button", ASK)).toBeInTheDocument();
  });

  it.each(["no-speech", "network", "audio-capture", "aborted"])(
    "does not offer it on %s, which a permission prompt would not fix",
    async (code) => {
      const made = await atDictate(recogniser());
      tapMic();
      made.instance.onerror({ error: code });
      await screen.findByText(new RegExp(`error: ${code}`));
      expect(screen.queryByRole("button", ASK)).not.toBeInTheDocument();
    },
  );

  it("does not offer it when nothing has failed", async () => {
    const made = await atDictate(recogniser());
    tapMic();
    made.instance.onend();
    await screen.findByText(/start requested → end/);
    expect(screen.queryByRole("button", ASK)).not.toBeInTheDocument();
  });

  it("records what getUserMedia answered, granted or refused", async () => {
    const getUserMedia = vi.fn().mockResolvedValue({ getTracks: () => [] });
    navigator.mediaDevices = { getUserMedia };
    try {
      const made = await atDictate(recogniser());
      tapMic();
      made.instance.onerror({ error: "not-allowed" });
      fireEvent.click(await screen.findByRole("button", ASK));

      expect(await screen.findByText(/microphone granted/)).toBeInTheDocument();
      expect(getUserMedia).toHaveBeenCalledWith({ audio: true });
    } finally {
      delete navigator.mediaDevices;
    }
  });

  it("names the exception when the microphone is refused outright", async () => {
    navigator.mediaDevices = {
      getUserMedia: vi.fn().mockRejectedValue(
        Object.assign(new Error("denied"), { name: "NotAllowedError" }),
      ),
    };
    try {
      const made = await atDictate(recogniser());
      tapMic();
      made.instance.onerror({ error: "not-allowed" });
      fireEvent.click(await screen.findByRole("button", ASK));

      expect(await screen.findByText(/microphone refused: NotAllowedError/)).toBeInTheDocument();
    } finally {
      delete navigator.mediaDevices;
    }
  });
});

describe("the dictate screen with no speech recognition at all", () => {
  it("says so and sends the operator to the field, where the keyboard mic works", async () => {
    // jsdom defines neither constructor, which is the same state as a browser without the API.
    vi.resetModules();
    const { default: App } = await import("../App.jsx");
    render(<MemoryRouter initialEntries={["/app/dictate"]}><App /></MemoryRouter>);

    expect(screen.getByText(/no speech recognition/i)).toBeInTheDocument();
    expect(screen.getByText(/microphone key on your keyboard/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/transcript/i)).toBeInTheDocument();
  });
});
