import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { MapContainer, Marker, Polyline, Popup, TileLayer } from "react-leaflet";
import L from "leaflet";

import { ApiError, postRoute } from "../api.js";
import { STOPS, loadWith } from "../data/manifest.js";
import { useScannedParcel } from "../scan/scannedParcel.jsx";
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

      <h1>Route &amp; delivery order</h1>
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

/* How many parcels come off at each stop, counted from the load actually in the van — the scanned
   parcel included once it is aboard. The mockup's second line reads "2 parcels · Rear doors"; we have
   no door data and will not invent any, so the count is the whole line. */
function parcelsByStop(parcel) {
  const counts = {};
  for (const box of loadWith(parcel)) {
    counts[box.stop] = (counts[box.stop] ?? 0) + 1;
  }
  return counts;
}

/* Where the van is in the round, from the arrival times the server gave and the clock — never a
   guess. The current stop is the last one whose time has arrived; before any of them have, the round
   has not started and the first stop is the one in hand. */
function currentIndex(stops, now = Date.now()) {
  let current = 0;
  stops.forEach((stop, index) => {
    if (stop.eta && Date.parse(stop.eta) <= now) current = index;
  });
  return current;
}

function Journey({ route }) {
  // GeoJSON is [lon, lat]; Leaflet wants [lat, lon]. Getting this backwards puts Paris in Somalia,
  // which is at least obvious on sight.
  const line = route.geometry.coordinates.map(([lon, lat]) => [lat, lon]);
  const names = Object.fromEntries(STOPS.map((stop) => [stop.id, stop.name]));
  const { parcel } = useScannedParcel();
  const parcels = parcelsByStop(parcel);
  const current = currentIndex(route.stops);

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

      <div className="route-summary">
        <h2>{route.stops.length} stops</h2>
        <span className="muted data">
          {(route.total_distance_m / 1000).toFixed(1)} km ·{" "}
          {Math.round(route.total_duration_s / 60)} min driving
        </span>
      </div>

      <ol className="route-list">
        {route.stops.map((stop, index) => {
          const here = index === current;
          const done = index < current;
          return (
            <li className={`card route-stop${here ? " route-stop--here" : ""}`} key={stop.id}>
              <span className={`route-pill${done || here ? "" : " route-pill--ahead"}`}>
                {index + 1}
              </span>
              <span className="route-stop__where">
                <strong>{names[stop.id] ?? stop.id}</strong>
                <span className="muted route-stop__detail">
                  {parcels[stop.id] ?? 0} {(parcels[stop.id] ?? 0) === 1 ? "parcel" : "parcels"}
                </span>
                {/* The address as the geocoder read it, not as we asked for it. Three of the eight
                    match at street level rather than house number, and an operator seeing the wrong
                    street is the reason this is shown rather than the input echoed back. */}
                <span className="muted data route-stop__label">{stop.label}</span>
              </span>
              <span className="data route-stop__eta">{clockOf(stop)}</span>
              <span className="route-stop__chevron" aria-hidden="true">›</span>
            </li>
          );
        })}
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
