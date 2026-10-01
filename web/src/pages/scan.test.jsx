import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "../App.jsx";

function at(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

function readCode(value) {
  fireEvent.change(screen.getByLabelText("Package code"), { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: /read code/i }));
}

describe("the scan step", () => {
  it("is where the home screen's main button now goes", () => {
    at("/app");
    const main = screen.getByRole("link", { name: /scan a package/i });
    expect(main).toHaveAttribute("href", "/app/scan");
    // The dictate screen is reached through the scan step now, not straight from home.
    expect(screen.queryByRole("link", { name: /dictate rules/i })).not.toBeInTheDocument();
  });

  it("renders at /app/scan", () => {
    at("/app/scan");
    expect(screen.getByRole("heading", { name: /scan the package/i })).toBeInTheDocument();
  });

  it("shows the parcel's dimensions and weight once its label is read", () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    expect(screen.getByRole("region", { name: "Scanned package" })).toBeInTheDocument();
    expect(screen.getByText("fragile parcel")).toBeInTheDocument();
    expect(screen.getByText("QUAI-BOX-0001")).toBeInTheDocument();
    expect(screen.getByText(/40 × 30 × 25 cm · 8 kg/)).toBeInTheDocument();
  });

  it("offers the dictate step only after something has been read", () => {
    at("/app/scan");
    const onward = /say what to do with it/i;
    expect(screen.queryByRole("button", { name: onward })).not.toBeInTheDocument();
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: onward }));
    expect(screen.getByRole("heading", { name: /loading rules/i })).toBeInTheDocument();
  });

  it("says a code is not a QUAI label rather than guessing at it", () => {
    at("/app/scan");
    readCode("1234");
    expect(screen.getByRole("alert")).toHaveTextContent(/not a QUAI package label/i);
    expect(screen.queryByRole("region", { name: "Scanned package" })).not.toBeInTheDocument();
  });

  it("distinguishes a QUAI label for a box that is not on this van", () => {
    at("/app/scan");
    readCode("QUAI:BOX:B99");
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("B99");
    expect(alert).toHaveTextContent(/not in today’s manifest/i);
  });

  it("cannot be submitted empty", () => {
    at("/app/scan");
    expect(screen.getByRole("button", { name: /read code/i })).toBeDisabled();
  });
});
