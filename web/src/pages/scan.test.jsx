import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App.jsx";
import { postConstraints, postPlan } from "../api.js";
import { BOXES } from "../data/manifest.js";

vi.mock("../api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  postConstraints: vi.fn(),
  postPlan: vi.fn(),
}));

beforeEach(() => {
  // The scan survives a reload now, which means it also survives between tests unless cleared —
  // a leaked parcel would make "nothing was scanned" quietly assert the wrong thing.
  window.sessionStorage.clear();
});

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

describe("the scan putting the parcel into the load", () => {
  beforeEach(() => {
    postConstraints.mockReset();
    postPlan.mockReset();
    postConstraints.mockResolvedValue({ constraints: [], unresolved: [] });
    postPlan.mockResolvedValue({
      placements: [], unplaced: [], fill_rate: 0, total_weight: 0, not_applied: [],
    });
  });

  it("keeps the parcel out of the eighteen boxes already in the van", () => {
    // The point of the split: BOXES means "already loaded", so the parcel is not one of them.
    expect(BOXES).toHaveLength(18);
    expect(BOXES.map((box) => box.id)).not.toContain("QUAI-BOX-0001");
  });

  it("dictates against eighteen boxes when nothing was scanned", async () => {
    at("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "Load the toolbox last." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(postConstraints).toHaveBeenCalled());
    expect(postConstraints.mock.calls[0][1]).toHaveLength(18);
  });

  it("dictates against nineteen once the parcel's label has been read", async () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));

    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "The fragile parcel goes on top." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(postConstraints).toHaveBeenCalled());

    // The manifest the model is asked about has to contain the parcel, or the sentence above comes
    // back as an unknown_item through no fault of the operator.
    const manifest = postConstraints.mock.calls[0][1];
    expect(manifest).toHaveLength(19);
    expect(manifest.map((box) => box.id)).toContain("QUAI-BOX-0001");
  });

  it("plans the nineteen boxes it dictated about", async () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "The fragile parcel goes on top." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    fireEvent.click(await screen.findByRole("button", { name: /confirm/i }));

    await waitFor(() => expect(postPlan).toHaveBeenCalled());
    // The solver must be given the same load the model was told about, parcel included.
    expect(postPlan.mock.calls[0][0].boxes).toHaveLength(19);
  });

  it("says the parcel is not loaded yet, and then that it is", () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    expect(screen.getByText(/not loaded yet/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));

    // Back for a second look at the same label: it is aboard now, and must not be added twice.
    fireEvent.click(screen.getByRole("link", { name: "← Home" }));
    fireEvent.click(screen.getByRole("link", { name: /scan a package/i }));
    readCode("QUAI:BOX:QUAI-BOX-0001");
    expect(screen.getByText(/already added to this load/i)).toBeInTheDocument();
  });

  it("recognises a box that was already in the van rather than offering to add it", () => {
    at("/app/scan");
    readCode("QUAI:BOX:B01");
    expect(screen.getByText("washing machine")).toBeInTheDocument();
    expect(screen.getByText(/already in the van/i)).toBeInTheDocument();
  });
});

describe("the scan surviving a reload", () => {
  beforeEach(() => {
    window.sessionStorage.clear();
    postConstraints.mockReset();
    postConstraints.mockResolvedValue({ constraints: [], unresolved: [] });
  });

  // Unmounting and rendering again from scratch is what a reload does to this app: React state is
  // gone and the provider is built fresh. Asked for in review of #57 — a reload mid-demo dropping
  // silently back to eighteen boxes is the failure being prevented.
  function reload(path) {
    cleanup();
    return at(path);
  }

  it("still plans nineteen boxes after a reload", async () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));

    reload("/app/dictate");
    fireEvent.change(screen.getByLabelText(/transcript/i), {
      target: { value: "The fragile parcel goes on top." },
    });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(postConstraints).toHaveBeenCalled());
    expect(postConstraints.mock.calls[0][1]).toHaveLength(19);
  });

  it("still counts nineteen on the home screen after a reload", () => {
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));

    reload("/app");
    expect(screen.getByText(/19 boxes/)).toBeInTheDocument();
  });

  it("stores the id, not a copy of the box", () => {
    // `manifest.js` stays the single source of what a parcel measures. A stored copy could go stale
    // against it and nothing would notice.
    at("/app/scan");
    readCode("QUAI:BOX:QUAI-BOX-0001");
    fireEvent.click(screen.getByRole("button", { name: /say what to do with it/i }));
    expect(window.sessionStorage.getItem("quai.scannedParcel")).toBe("QUAI-BOX-0001");
  });

  it("ignores a stored id it does not recognise instead of restoring rubbish", () => {
    window.sessionStorage.setItem("quai.scannedParcel", "QUAI-BOX-9999");
    at("/app");
    expect(screen.getByText(/18 boxes/)).toBeInTheDocument();
  });

  it("starts a fresh round at eighteen when nothing was stored", () => {
    at("/app");
    expect(screen.getByText(/18 boxes/)).toBeInTheDocument();
  });
});
