import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

/* Leaflet measures a real viewport and draws into a canvas, neither of which jsdom has — the same
   reason `app.test.jsx` stubs `@react-three/fiber`. The stubs keep the component's own decisions
   visible: what it sends, what it renders from the answer, and the order it puts the stops in. */
vi.mock("react-leaflet", () => ({
  MapContainer: ({ children, ...rest }) => <div data-testid="map" {...rest}>{children}</div>,
  TileLayer: ({ attribution }) => <div data-testid="tiles" data-attribution={attribution} />,
  Polyline: ({ positions }) => <div data-testid="line" data-points={positions.length} />,
  Marker: ({ position, children }) => (
    <div data-testid="pin" data-lat={position[0]} data-lon={position[1]}>{children}</div>
  ),
  Popup: ({ children }) => <div data-testid="popup">{children}</div>,
}));
vi.mock("leaflet", () => ({ default: { divIcon: (opts) => opts } }));
vi.mock("leaflet/dist/leaflet.css", () => ({}));

import App from "../App.jsx";
import { ApiError, postRoute } from "../api.js";
import { STOPS } from "../data/manifest.js";

vi.mock("../api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  postRoute: vi.fn(),
}));

// Shaped like a real answer from POST /route, trimmed to three stops.
const ANSWER = {
  stops: [
    { id: "S1", address: "4 Rue de Lobau, 75004 Paris", label: "4 Rue de Lobau 75004 Paris",
      lon: 2.353536, lat: 48.856514, eta_seconds: 0, eta: "2026-10-02T08:00:00+02:00" },
    { id: "S2", address: "25 Avenue des Champs-Élysées, 75008 Paris",
      label: "25 Rue des Champs Élysées 75008 Paris",
      lon: 2.306, lat: 48.871, eta_seconds: 606, eta: "2026-10-02T08:10:06+02:00" },
    { id: "S3", address: "5 Place de la Bastille, 75011 Paris",
      label: "Place de la Bastille 75011 Paris",
      lon: 2.369, lat: 48.853, eta_seconds: 1648, eta: "2026-10-02T08:27:28+02:00" },
  ],
  geometry: { type: "LineString", coordinates: [[2.3535, 48.8565], [2.306, 48.871], [2.369, 48.853]] },
  total_distance_m: 37700,
  total_duration_s: 6000,
};

function at(path) {
  return render(<MemoryRouter initialEntries={[path]}><App /></MemoryRouter>);
}

beforeEach(() => {
  postRoute.mockReset();
});

describe("the round screen", () => {
  it("is reachable from home", () => {
    at("/app");
    expect(screen.getByRole("link", { name: /see today’s round/i }))
      .toHaveAttribute("href", "/app/route");
  });

  it("asks for the stops in the order the manifest holds them, never sorted", async () => {
    // The guarantee the endpoint makes and this screen must not undermine: the delivery order
    // arrives with the round. Sorting here would quietly describe a journey the van does not make.
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    await waitFor(() => expect(postRoute).toHaveBeenCalled());
    const [sent] = postRoute.mock.calls[0];
    expect(sent.map((s) => s.id)).toEqual(STOPS.map((s) => s.id));
  });

  it("sends a departure time, so the arrival times come back absolute", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    await waitFor(() => expect(postRoute).toHaveBeenCalled());
    const [, departure] = postRoute.mock.calls[0];
    expect(Number.isNaN(Date.parse(departure))).toBe(false);
  });

  it("says it is working while the lookup is in flight", () => {
    postRoute.mockReturnValue(new Promise(() => {}));
    at("/app/route");
    expect(screen.getByRole("status")).toHaveTextContent(/looking up the addresses/i);
    // And no times at all yet: a number on screen before the answer would be one we made up.
    expect(screen.queryByText(/08:00/)).not.toBeInTheDocument();
  });

  it("draws the road line and one numbered pin per stop", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    expect(await screen.findByTestId("map")).toBeInTheDocument();
    expect(screen.getByTestId("line")).toHaveAttribute("data-points", "3");
    expect(screen.getAllByTestId("pin")).toHaveLength(3);
  });

  it("puts the coordinates the right way round", async () => {
    // GeoJSON is [lon, lat] and Leaflet wants [lat, lon]. Swapped, Paris lands off Somalia.
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    const first = (await screen.findAllByTestId("pin"))[0];
    expect(Number(first.getAttribute("data-lat"))).toBeCloseTo(48.856514, 4);
    expect(Number(first.getAttribute("data-lon"))).toBeCloseTo(2.353536, 4);
  });

  it("credits OpenStreetMap, as its tile licence asks", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    expect(await screen.findByTestId("tiles"))
      .toHaveAttribute("data-attribution", expect.stringContaining("OpenStreetMap"));
  });

  it("shows the arrival time the server returned, not one of its own", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    // 08:10:06+02:00 rendered in the test environment's locale and zone.
    const expected = new Date(ANSWER.stops[1].eta)
      .toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    expect(await screen.findByText(expected)).toBeInTheDocument();
  });

  it("shows the address the geocoder matched, not the one we asked for", async () => {
    // Three of the real eight match at street level rather than house number. Showing the server's
    // label is how an operator spots a wrong street instead of trusting a silent mismatch.
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    // Twice on purpose: in the list and in the pin's popup, so it is there whichever the operator
    // is looking at. What must never appear is the address we asked for, dressed up as a match.
    expect(await screen.findAllByText("Place de la Bastille 75011 Paris")).toHaveLength(2);
    expect(screen.queryAllByText("5 Place de la Bastille, 75011 Paris")).toHaveLength(0);
  });

  it("lists the stops in delivery order, numbered", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    await screen.findByTestId("map");
    const items = screen.getAllByRole("listitem").map((li) => li.textContent);
    expect(items).toHaveLength(3);
    expect(items[0]).toMatch(/^1/);
    expect(items[2]).toMatch(/^3/);
  });

  it("shows the real parcel count per stop, and invents no door", async () => {
    // The mockup's second line reads "2 parcels · Rear doors". We have no door data anywhere in the
    // manifest, so the count is the whole line — the mockup gives the layout, not the content.
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    await screen.findByTestId("map");
    expect(screen.getAllByText(/\d+ parcels?$/).length).toBe(3);
    for (const invented of [/rear doors/i, /front doors/i, /side entrance/i, /middle/i]) {
      expect(screen.queryByText(invented)).not.toBeInTheDocument();
    }
  });

  it("marks one stop as the one in hand, from the clock and the real times", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    await screen.findByTestId("map");
    const here = screen.getAllByRole("listitem").filter((li) =>
      li.className.includes("route-stop--here"));
    expect(here).toHaveLength(1);
  });

  it("names the stops from the manifest, not Stop 1 / Stop 2", async () => {
    // The mockup's labels are placeholders; the round has real names.
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    // In the list and in the pin's popup, like every stop name on this screen.
    expect(await screen.findAllByText("Hôtel de Ville")).toHaveLength(2);
    expect(screen.queryByText(/^Stop 1$/)).not.toBeInTheDocument();
  });

  it("shows the distance and driving time from the answer", async () => {
    postRoute.mockResolvedValue(ANSWER);
    at("/app/route");
    expect(await screen.findByText(/37\.7 km/)).toBeInTheDocument();
    expect(screen.getByText(/100 min driving/)).toBeInTheDocument();
  });
});

describe("the round screen when the request fails", () => {
  beforeEach(() => {
    postRoute.mockReset();
  });

  it("names the solver when it cannot be reached, and says how to start it", async () => {
    postRoute.mockRejectedValue(
      new ApiError("unreachable", "Could not reach the solver at http://127.0.0.1:8000."));
    at("/app/route");
    expect(await screen.findByRole("alert")).toHaveTextContent(/could not reach the solver/i);
    expect(screen.getByText(/uvicorn server:app/)).toBeInTheDocument();
  });

  it("passes on the server's own words when an address is refused", async () => {
    // The real 422: the endpoint names the address it could not find, which is the actionable part.
    const detail = "no address found for '5 Place de la Bastille, 75011 Paris'.";
    postRoute.mockRejectedValue(new ApiError("refused", detail, detail));
    at("/app/route");
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("5 Place de la Bastille");
    expect(alert).toHaveTextContent(/covers France only/i);
  });

  it("reports a server failure without dressing it up as unreachable", async () => {
    postRoute.mockRejectedValue(
      new ApiError("server", "The solver answered 503.", "the route service is unavailable"));
    at("/app/route");
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("The solver answered 503.");
    expect(alert).toHaveTextContent("the route service is unavailable");
    expect(screen.queryByText(/uvicorn server:app/)).not.toBeInTheDocument();
  });

  it("shows no stops and no times when the request failed", async () => {
    postRoute.mockRejectedValue(new ApiError("server", "The route could not be built."));
    at("/app/route");
    await screen.findByRole("alert");
    expect(screen.queryByTestId("map")).not.toBeInTheDocument();
    expect(screen.queryByRole("listitem")).not.toBeInTheDocument();
  });
});
