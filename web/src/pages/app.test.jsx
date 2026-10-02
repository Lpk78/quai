import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Confirm navigates into /app/plan, which renders the 3D scene. WebGL does not exist in jsdom, so
// it renders as plain elements here — same stub plan/plan.test.jsx uses for the same reason.
vi.mock("@react-three/fiber", () => ({
  Canvas: ({ children, ...rest }) => <div data-testid="scene" {...rest}>{children}</div>,
  // `useThree` reaches the renderer's camera, which the camera presets move (`SA-23`). There is no
  // renderer here, so it hands back a camera-shaped object: the preset's effect runs without throwing
  // and the rest of the screen stays testable. What the camera *sees* is not something jsdom can tell
  // us either way — `plan/scene.test.jsx` asserts the view positions directly instead.
  useThree: (selector) => {
    const camera = { position: { set: () => {} }, lookAt: () => {} };
    return selector ? selector({ camera }) : { camera };
  },
}));
vi.mock("@react-three/drei", () => ({ OrbitControls: () => null }));

import App from "../App.jsx";
import { ApiError, postConstraints, postPlan, postRoute } from "../api.js";

vi.mock("../api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  postConstraints: vi.fn(),
  postPlan: vi.fn(),
  postRoute: vi.fn(),
}));

function at(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  postConstraints.mockReset();
  postPlan.mockReset();
  postRoute.mockReset();
  // Home asks for the round on mount; most tests here are not about that tile.
  postRoute.mockReturnValue(new Promise(() => {}));
});

describe("home", () => {
  it("shows the operator's name and the load's real counts, summarised rather than listed", () => {
    // HY-17: the per-box list (id, label, dimensions) moved out of this screen into a compact
    // summary card. Léo-Paul and the two counts are still here; an individual box's own detail,
    // such as B01's label, is not — that is what the stat tiles and the scan step are for now.
    const { container } = at("/app");
    // getAllBy, not getBy: the operator's name is now in two places, the subtitle and the header
    // badge's screen-reader label. A single-match query would fail on the badge rather than on
    // anything being wrong.
    expect(container.querySelector(".home-sub").textContent).toMatch(/Léo-Paul/);
    expect(screen.getAllByText(/Léo-Paul/).length).toBeGreaterThan(0);
    expect(screen.queryByText("B01")).not.toBeInTheDocument();
    expect(screen.queryByText(/washing machine/)).not.toBeInTheDocument();
  });

  it("has one big button, now to the scan step rather than straight to dictating", () => {
    // SA-17 put /app/scan in front of /app/dictate: the operator reads the package label first, so
    // the sentence they dictate next is about a box QUAI can name.
    at("/app");
    const link = screen.getByRole("link", { name: /start loading/i });
    expect(link).toHaveAttribute("href", "/app/scan");
  });

  it("shows a Parcels tile and a Stops tile, each matching the manifest", () => {
    at("/app");
    expect(screen.getByText("Parcels").previousElementSibling).toHaveTextContent("18");
    expect(screen.getByText("Stops").previousElementSibling).toHaveTextContent("8");
  });

  it("shows the route time the server returned, formatted but not rounded away", async () => {
    // The mockup's "4h 20m" is never copied: this is `total_duration_s` from `POST /route`.
    postRoute.mockResolvedValue({ stops: [], geometry: null, total_duration_s: 15600 });
    at("/app");
    expect(await screen.findByText("4h 20m")).toBeInTheDocument();
  });

  it("shows a dash rather than a number while the route is still being fetched", () => {
    /* An em dash is the honest answer before the server has answered, and the one thing this tile
       must never do is show a figure QUAI did not compute.

       The first version of this assertion was vacuous: it searched for "estimated route time" while
       the tile is labelled "Est. route time", so it matched nothing and passed both before and
       after the tile existed. It reads the tile's own value now. */
    postRoute.mockReturnValue(new Promise(() => {})); // never settles
    at("/app");
    const tile = screen.getByText("Est. route time").closest(".stat-tile");
    expect(tile.querySelector("strong").textContent).toBe("—");
  });

  it("leaves the dash in place when the route cannot be fetched at all", async () => {
    // A failing route must not take down the screen the operator starts their morning on.
    postRoute.mockRejectedValue(new ApiError("unreachable", "no"));
    at("/app");
    const tile = screen.getByText("Est. route time").closest(".stat-tile");
    await waitFor(() => expect(postRoute).toHaveBeenCalled());
    expect(tile.querySelector("strong").textContent).toBe("—");
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });
});

describe("dictate, with no speech recognition in this environment", () => {
  it("falls back to a text field and disables sending until it has text", () => {
    at("/app/dictate");
    expect(screen.getByLabelText(/transcript/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send/i })).toBeDisabled();
  });

  it("shows each returned constraint as a readable card, with a confirm button", async () => {
    postConstraints.mockResolvedValue({
      constraints: [{ type: "keep_upright", item: "B3" }],
      unresolved: [],
    });
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "Keep the pallet of tiles upright" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    // HY-17: a rule card is now a title and a line of explanation, as in the mockup, rather
    // than one "Keep upright: B3" string.
    expect(await screen.findByText("B3 — keep upright")).toBeInTheDocument();
    expect(screen.getByText("Never laid on its side or turned over.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /confirm/i })).toBeEnabled();
  });

  it("shows the unresolved items alongside what it understood", async () => {
    postConstraints.mockResolvedValue({
      constraints: [],
      unresolved: [
        { text: "the heavy one", reason: "ambiguous", question: "Which parcel do you mean?" },
      ],
    });
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "The heavy one goes last" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/the heavy one/i)).toBeInTheDocument();
    expect(screen.getByText(/which parcel do you mean/i)).toBeInTheDocument();
  });

  it("shows the server's own reason when the sentence is refused, and edit keeps the transcript",
    async () => {
      postConstraints.mockRejectedValue(
        new ApiError("refused", "text must not be empty", "text must not be empty"),
      );
      at("/app/dictate");
      fireEvent.change(screen.getByLabelText(/transcript/i), {
        target: { value: "Keep it upright" },
      });
      fireEvent.click(screen.getByRole("button", { name: /send/i }));

      expect(await screen.findByText("text must not be empty")).toBeInTheDocument();
      expect(screen.queryByText(/could not reach the solver/i)).not.toBeInTheDocument();

      fireEvent.click(screen.getByRole("button", { name: /edit/i }));
      expect(screen.getByLabelText(/transcript/i)).toHaveValue("Keep it upright");
    });

  it("names the solver when it cannot be reached at all", async () => {
    postConstraints.mockRejectedValue(
      new ApiError("unreachable", "Could not reach the solver at http://127.0.0.1:8000."),
    );
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "Keep it upright" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/could not reach the solver/i)).toBeInTheDocument();
    expect(screen.getByText(/uvicorn server:app/)).toBeInTheDocument();
  });
});

describe("dictate, with speech recognition available", () => {
  // `SpeechRecognitionImpl` is read once, at module load, which is exactly why the rest of this
  // file runs with no browser speech API: a stub set after `Dictate.jsx` is first imported would
  // never be seen. `vi.resetModules()` plus a dynamic import re-evaluates that module with the
  // stub already on `window`, which is the only way to reach this branch at all.
  it("shows a fixed example of what to say, which stays once typing starts", async () => {
    class MockSpeechRecognition {
      start() {}
      stop() {}
    }
    vi.stubGlobal("SpeechRecognition", MockSpeechRecognition);
    vi.resetModules();
    const { default: FreshApp } = await import("../App.jsx");

    render(
      <MemoryRouter initialEntries={["/app/dictate"]}>
        <FreshApp />
      </MemoryRouter>,
    );

    const example = /Keep the pallet of tiles upright and load the toolbox last\./;
    expect(screen.getByText(example)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/transcript/i), { target: { value: "some rule" } });
    expect(screen.getByText(example)).toBeInTheDocument();

    vi.unstubAllGlobals();
  });

  it("decorates the mic with sound-wave bars that stay out of the accessibility tree", async () => {
    class MockSpeechRecognition {
      start() {}
      stop() {}
    }
    vi.stubGlobal("SpeechRecognition", MockSpeechRecognition);
    vi.resetModules();
    const { default: FreshApp } = await import("../App.jsx");

    const { container } = render(
      <MemoryRouter initialEntries={["/app/dictate"]}>
        <FreshApp />
      </MemoryRouter>,
    );

    // HY-17: the bars are decoration either side of the mic, not information — a screen reader
    // user must still reach the same one control the sighted layout has.
    const waves = container.querySelectorAll(".sound-wave");
    expect(waves).toHaveLength(2);
    for (const wave of waves) expect(wave).toHaveAttribute("aria-hidden", "true");
    expect(screen.getByRole("button", { name: /tap and speak/i })).toBeInTheDocument();

    vi.unstubAllGlobals();
  });
});

describe("confirm sends the dictated constraints to /plan and shows what it returns", () => {
  async function confirmWith(constraints) {
    postConstraints.mockResolvedValue({ constraints, unresolved: [] });
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), { target: { value: "some rule" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await screen.findByRole("button", { name: /confirm/i });
    fireEvent.click(screen.getByRole("button", { name: /confirm/i }));
  }

  it("sends an honoured constraint, and the plan shown reflects it", async () => {
    postPlan.mockResolvedValue({
      placements: [{ id: "B18", x: 260, y: 0, z: 85, dx: 40, dy: 85, dz: 45 }],
      unplaced: [],
      fill_rate: 0.5,
      total_weight: 8,
      not_applied: [],
    });

    await confirmWith([{ type: "load_last", item: "B18" }]);

    expect(await screen.findByRole("heading", { name: "Load plan" })).toBeInTheDocument();
    expect(postPlan).toHaveBeenCalledWith(
      expect.objectContaining({ constraints: [{ type: "load_last", item: "B18" }] }),
    );
    // Not just any plan: the one /plan returned for this constraint, not the no-constraint default.
    // Scoped to the placed list rather than searched for anywhere, because B18 is also named in the
    // "Next box" card now (`SA-23`). The ids in the list are compared whole: a bare text query would
    // have found two, and `length > 0` would no longer pin which box or where.
    const listedIds = screen.getAllByTestId("placed-box")
      .map((row) => row.querySelector(".plan-id").textContent);
    expect(listedIds).toEqual(["B18"]);
    // Eighteen, not nineteen: this test enters at /app/dictate without passing through /app/scan, so
    // the fragile parcel is not aboard. SA-17b took it out of BOXES — scanning its label is what adds
    // it. The nineteen-box path is covered in scan.test.jsx.
    expect(screen.getByText("1 / 18")).toBeInTheDocument();
  });

  it("shows an unhonoured constraint under 'Not applied' rather than hiding it", async () => {
    postPlan.mockResolvedValue({
      placements: [],
      unplaced: [],
      fill_rate: 0,
      total_weight: 0,
      not_applied: [{
        type: "on_top",
        item: "B07",
        reason: "the solver cannot honour on_top yet and refuses to plan with it rather than "
          + "drop it; issue #29",
      }],
    });

    await confirmWith([{ type: "on_top", item: "B07" }]);

    expect(await screen.findByRole("heading", { name: "Not applied" })).toBeInTheDocument();
    const entry = screen.getByTestId("not-applied");
    expect(entry).toHaveTextContent("on_top: B07");
    expect(entry).toHaveTextContent(/issue #29/);
  });
});
