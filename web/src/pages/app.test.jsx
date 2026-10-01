import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Confirm navigates into /app/plan, which renders the 3D scene. WebGL does not exist in jsdom, so
// it renders as plain elements here — same stub plan/plan.test.jsx uses for the same reason.
vi.mock("@react-three/fiber", () => ({
  Canvas: ({ children, ...rest }) => <div data-testid="scene" {...rest}>{children}</div>,
}));
vi.mock("@react-three/drei", () => ({ OrbitControls: () => null }));

import App from "../App.jsx";
import { ApiError, postConstraints, postPlan } from "../api.js";

vi.mock("../api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  postConstraints: vi.fn(),
  postPlan: vi.fn(),
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
});

describe("home", () => {
  it("shows today's van and its boxes from the manifest", () => {
    at("/app");
    expect(screen.getByText(/Léo-Paul/)).toBeInTheDocument();
    expect(screen.getByText("B01")).toBeInTheDocument();
    expect(screen.getByText(/washing machine/)).toBeInTheDocument();
  });

  it("has one big button to dictate rules", () => {
    at("/app");
    const link = screen.getByRole("link", { name: /dictate rules/i });
    expect(link).toHaveAttribute("href", "/app/dictate");
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

    expect(await screen.findByText("Keep upright: B3")).toBeInTheDocument();
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
    expect(screen.getByText("B18")).toBeInTheDocument();
    expect(screen.getByText("1 / 19")).toBeInTheDocument();
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
