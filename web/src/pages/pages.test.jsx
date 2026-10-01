import { render, screen } from "@testing-library/react";
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

describe("routing", () => {
  it("shows the landing page at /", () => {
    at("/");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("People talk. We load.");
  });

  it("shows the application shell at /app", () => {
    at("/app");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Plan a load");
  });

  it("shows a plain page for an address that does not exist", () => {
    at("/nope");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Nothing at this address");
  });

  it("lets the landing page reach the application", () => {
    at("/");
    expect(screen.getAllByRole("link", { name: /open the app/i }).length).toBeGreaterThan(0);
  });
});

describe("the application shell is deliberately empty", () => {
  it("names what will fill it rather than pretending it is there", () => {
    at("/app");
    expect(screen.getByText("#7")).toBeInTheDocument();
    expect(screen.getByText("#8")).toBeInTheDocument();
    expect(screen.getByText(/nothing to show yet/i)).toBeInTheDocument();
  });
});
