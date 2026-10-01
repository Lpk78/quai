import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";

import { ApiError, postRoute } from "../api.js";
import { STOPS } from "../data/manifest.js";
import "leaflet/dist/leaflet.css";
import "../route.css";

/* The round on a map, and the order it is driven in.
 *
 * Every number on this screen comes from `POST /route`: the coordinates, the road line, the distance,
 * the driving time and the arrival time at each stop. None of it is computed here and none of it is
 * guessed — an invented ETA is the one thing an operator must never be shown, because they would plan
 * their morning around it. Until the request answers there are no times on screen at all.
 *
 * The stops are sent in the order the manifest holds them. That is the whole point of the endpoint:
 * the delivery order arrives with the round and nothing reorders it, so the line drawn here is the
 * journey the van actually makes rather than a shorter one some router preferred.
 */

// Leaflet's default marker icon is a file path relative to its own CSS, which a bundler rewrites and
// then cannot find. Numbered circles are what this screen wants anyway: the number *is* the delivery
// order, which is the thing being communicated.
function stopIcon(position) {
  return L.divIcon({
    className: "route-pin",
    html: `<span>${position}</span>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}

// A departure time is needed for absolute arrival times rather than offsets, and it has to be a real
// instant, so it is read once when the screen opens rather than hard-coded into the repository.
function departureNow() {
  return new Date().toISOString();
}

function clockOf(stop) {
  // `eta` is absolute and comes from the server. `eta_seconds` is the offset from departure, which is
  // what there is when no departure time was sent — shown as a duration, never dressed up as a time.
  if (stop.eta) {
    return new Date(stop.eta).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  const minutes = Math.round((stop.eta_seconds ?? 0) / 60);
  return minutes === 0 ? "on departure" : `+${minutes} min`;
}

export default function Route() {
  const [step, setStep] = useState("loading"); // loading | ready | error
  const [route, setRoute] = useState(null);
  const [error, setError] = useState(null);
  const departure = useRef(departureNow());

  useEffect(() => {
    const controller = new AbortController();
    let live = true;
    postRoute(STOPS, departure.current, { signal: controller.signal })
      .then((data) => {
        if (!live) return;
        setRoute(data);
        setStep("ready");
      })
      .catch((cause) => {
        if (!live || cause?.name === "AbortError") return;
        setError(cause instanceof ApiError
          ? cause
          : new ApiError("server", "The route could not be built.", String(cause)));
        setStep("error");
      });
    return () => {
      live = false;
      controller.abort();
    };
  }, []);

  return (
    <>
      <Link className="muted back-link" to="/app">
        ← Home
      </Link>

      <h1>Today’s round</h1>
      <p className="muted">
        {STOPS.length} stops, in the order they are driven. QUAI never reorders them.
      </p>

      {step === "loading" && (
        <div className="card status-card" role="status">
          <p>Looking up the addresses and asking for the road…</p>
        </div>
      )}

      {step === "error" && <Failure error={error} />}

      {step === "ready" && route && <Journey route={route} />}
    </>
  );
}

function Journey({ route }) {
  // GeoJSON is [lon, lat]; Leaflet wants [lat, lon]. Getting this backwards puts Paris in Somalia,
  // which is at least obvious on sight.
  const line = route.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
  const names = Object.fromEntries(STOPS.map((stop) => [stop.id, stop.name]));

  return (
    <>
      <section className="card route-map" aria-label="Map of today’s round">
        <MapContainer bounds={line} scrollWheelZoom={false} className="route-map__canvas">
          <TileLayer
            // OpenStreetMap tiles: free, no key, and their licence asks for this credit.
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Polyline positions={line} />
          {route.stops.map((stop, index) => (
            <Marker key={stop.id} position={[stop.lat, stop.lon]} icon={stopIcon(index + 1)}>
              <Popup>
                <strong>{names[stop.id] ?? stop.id}</strong>
                <br />
                {stop.label}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </section>

      <p className="muted data">
        {(route.total_distance_m / 1000).toFixed(1)} km ·{" "}
        {Math.round(route.total_duration_s / 60)} min driving
      </p>

      <ol className="card route-list">
        {route.stops.map((stop, index) => (
          <li className="route-stop" key={stop.id}>
            <span className="badge">{index + 1}</span>
            <span className="route-stop__where">
              <strong>{names[stop.id] ?? stop.id}</strong>
              {/* The address as the geocoder read it, not as we asked for it. Three of these match at
                  street level rather than house number, and an operator seeing the wrong street is
                  the reason this is shown rather than the input echoed back. */}
              <span className="muted data">{stop.label}</span>
            </span>
            <span className="data route-stop__eta">{clockOf(stop)}</span>
          </li>
        ))}
      </ol>
    </>
  );
}

function Failure({ error }) {
  const unreachable = error.kind === "unreachable";
  const refused = error.kind === "refused";
  return (
    <div className="card status-card" role="alert">
      <p>{error.message}</p>
      {unreachable && (
        <p className="muted">
          The solver runs separately: <code className="data">uvicorn server:app --app-dir src</code>
        </p>
      )}
      {refused && (
        <p className="muted">
          The address lookup covers France only, and it answers with the address it could not find.
        </p>
      )}
      {error.detail && !unreachable && error.detail !== error.message && (
        <p className="muted data">{error.detail}</p>
      )}
    </div>
  );
}
