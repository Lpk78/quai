import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App.jsx";
import { postConstraints } from "../api.js";

vi.mock("../api.js", () => ({ postConstraints: vi.fn() }));

function at(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  postConstraints.mockReset();
});

describe("home", () => {
  it("shows today's van and its boxes from the manifest", () => {
    at("/app");
    expect(screen.getByText(/Van 12/)).toBeInTheDocument();
    expect(screen.getByText("B1")).toBeInTheDocument();
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

  it("shows each returned constraint as a readable card, and confirm leads to /app/plan", async () => {
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
    expect(screen.getByRole("link", { name: /confirm/i })).toHaveAttribute("href", "/app/plan");
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

  it("shows a calm message on a failed request, and edit keeps the transcript", async () => {
    postConstraints.mockRejectedValue(new Error("the server answered 500"));
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "Keep it upright" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText(/could not reach the solver/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /edit/i }));
    expect(screen.getByLabelText(/transcript/i)).toHaveValue("Keep it upright");
  });
});
