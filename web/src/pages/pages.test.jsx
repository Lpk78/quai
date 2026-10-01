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
    // The headline is broken over two lines, as the mockup sets it, so textContent has no space.
    const heading = screen.getByRole("heading", { level: 1 });
    expect(heading).toHaveTextContent(/People talk\./);
    expect(heading).toHaveTextContent(/We load\./);
  });

  it("shows the application home at /app", () => {
    at("/app");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Good morning. Let’s load.");
  });

  it("shows the dictate screen at /app/dictate, inside the same shell", () => {
    at("/app/dictate");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Tell QUAI your loading rules");
    expect(screen.getByAltText("QUAI")).toBeInTheDocument();
  });

  it("shows a plain page for an address that does not exist", () => {
    at("/nope");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Nothing at this address");
  });

  it("lets the landing page reach the application, through /login", () => {
    at("/");
    const toLogin = screen
      .getAllByRole("link")
      .filter((a) => a.getAttribute("href") === "/login");
    expect(toLogin.length).toBeGreaterThan(0);
    expect(toLogin.some((a) => /get started/i.test(a.textContent))).toBe(true);
    // /login is the way in, so no call to action skips it.
    expect(screen.queryAllByRole("link", { name: /open the app|log in|get started/i })
      .every((a) => a.getAttribute("href") === "/login")).toBe(true);
  });

  it("shows the login screen at /login", () => {
    at("/login");
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Scan your operator card");
  });
});
