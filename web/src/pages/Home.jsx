import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { postRoute } from "../api.js";
import { OPERATOR_NAME, STOPS, loadWith } from "../data/manifest.js";
import { IconBox, IconClock, IconPin } from "../landing/icons.jsx";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

/** Seconds of driving as the tile shows them: "4h 20m", or "35m" under the hour. */
function asDuration(seconds) {
  const total = Math.round(seconds / 60);
  const hours = Math.floor(total / 60);
  return hours ? `${hours}h ${String(total % 60).padStart(2, "0")}m` : `${total}m`;
}

/* The three steps of the round, as the mockup's "TODAY'S ROUTE" list.
 *
 * `to` is the whole honesty rule of this list: a step that leads somewhere is a link and gets a
 * chevron, a step that does not is plain text and gets neither. Two of the three lead nowhere today,
 * and dressing them as controls would promise navigation and progress tracking that do not exist. */
const ROUTE_STEPS = [
  { title: "Load your van", detail: "Scan each parcel, then say your rules", to: "/app/scan" },
  // `SA-21` / #63 built `/app/route`, so this step became a real destination during the rebase.
  // It replaces the standalone "See today's round" button that PR added to this screen: same place
  // to go, reached from the step that describes it, rather than a second button beside the list.
  { title: "Deliver your stops", detail: "The round, in your delivery list's order", to: "/app/route" },
  { title: "Track progress", detail: "Not built yet", to: null },
];

export default function Home() {
  // Eighteen, or nineteen once a parcel has been scanned. Reading the same `loadWith` the dictate
  // screen plans with, so the count here cannot say eighteen while the plan holds nineteen.
  const { parcel } = useScannedParcel();
  const boxes = loadWith(parcel);

  /* The mockup's three figures are 124 parcels, 28 stops and 4h 20m. None of them is copied: the
     first two are counted from the manifest, and the third is driving time from `POST /route`.

     It is asked for here rather than passed down because Home is the first screen of the round, and
     an em dash is the honest answer while the request is in flight or if it fails. The one thing
     this tile must never do is show a number QUAI did not compute — which was a live risk until
     `SA-21` / #63: the stops were Madrid districts, and the France-only geocoder answered them with
     French and Guadeloupean addresses and a nineteen-hour leg, a wrong number rather than an error.
     Real Paris addresses arrived with that PR, so the figure is now real too. */
  const [routeSeconds, setRouteSeconds] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    let live = true;
    postRoute(STOPS, null, { signal: controller.signal })
      .then((data) => { if (live) setRouteSeconds(data.total_duration_s ?? null); })
      // A route that cannot be fetched leaves the dash. The round is still loadable without it, so
      // this is not worth an error state on the screen the operator starts their morning on.
      .catch(() => {});
    return () => { live = false; controller.abort(); };
  }, []);

  const stats = [
    [<IconBox key="i" />, String(boxes.length), "Parcels", null],
    [<IconPin key="i" />, String(STOPS.length), "Stops", null],
    [<IconClock key="i" />,
      routeSeconds === null ? "—" : asDuration(routeSeconds),
      "Est. route time",
      routeSeconds === null ? "Driving time not available yet" : null],
  ];

  return (
    <>
      <h1>
        Good morning,
        <br />
        Let’s load.
      </h1>
      {/* The mockup reads "Van 12 · 28 stops · 124 parcels". There is no van id in the fixture —
          "Van 12" was invented in `HY-14` and taken out again in `HY-16` — so the operator's name
          takes that slot, which is the one thing here that is actually known. */}
      <p className="muted home-sub">
        {OPERATOR_NAME} <span aria-hidden="true">•</span> {STOPS.length} stops{" "}
        <span aria-hidden="true">•</span> {boxes.length} parcels
      </p>

      <section className="card van-card">
        <img
          className="van-card__art"
          src="/assets/van-side.png"
          alt=""
          width="1448"
          height="1086"
          decoding="async"
        />
        <h2>Loading plan ready</h2>
        <p className="muted">
          Built from your rules and the stop order on your delivery list, so every parcel has a place
          before anyone picks one up.
        </p>
        <Link className="button button--block" to="/app/scan">
          Start loading <span aria-hidden="true">→</span>
        </Link>
      </section>

      <ul className="stat-tiles">
        {stats.map(([icon, value, label, unavailable]) => (
          <li className="stat-tile" key={label}>
            <span className="stat-tile__icon" aria-hidden="true">{icon}</span>
            <strong className="data">{value}</strong>
            <span className="muted">{label}</span>
            {unavailable && <span className="visually-hidden">{unavailable}</span>}
          </li>
        ))}
      </ul>

      <section className="route-steps" aria-labelledby="todays-route">
        <h2 className="route-steps__title" id="todays-route">Today’s route</h2>
        <ol className="route-steps__list">
          {ROUTE_STEPS.map(({ title, detail, to }, index) => {
            const body = (
              <>
                <span className={`route-step__pill${index === 0 ? " route-step__pill--now" : ""}`}>
                  {index + 1}
                </span>
                <span className="route-step__text">
                  <strong>{title}</strong>
                  <span className="muted">{detail}</span>
                </span>
                {to && <span className="route-step__chevron" aria-hidden="true">›</span>}
              </>
            );
            return (
              <li className="route-step" key={title}>
                {to ? <Link className="route-step__row" to={to}>{body}</Link>
                  : <div className="route-step__row route-step__row--inert">{body}</div>}
              </li>
            );
          })}
        </ol>
      </section>
    </>
  );
}
