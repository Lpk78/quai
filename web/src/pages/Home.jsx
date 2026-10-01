import { Link } from "react-router-dom";

import { OPERATOR_NAME, STOPS, loadWith } from "../data/manifest.js";
import { IconBox, IconPin } from "../landing/icons.jsx";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

export default function Home() {
  // Eighteen, or nineteen once a parcel has been scanned. Reading the same `loadWith` the dictate
  // screen plans with, so the count here cannot say eighteen while the plan holds nineteen.
  const { parcel } = useScannedParcel();
  const boxes = loadWith(parcel);

  // No "Estimated route time" tile next to these, unlike the landing page's own version of this
  // pattern (`LoadingPlanReady`): that one is marked "Example van — not a measured result", but this
  // screen is the operator's real load, with nothing invented to put a disclaimer on.
  const stats = [
    [<IconBox key="i" />, boxes.length, "Parcels"],
    [<IconPin key="i" />, STOPS.length, "Stops"],
  ];

  return (
    <>
      <h1>
        Good morning,
        <br />
        Let’s load.
      </h1>
      <p className="muted">
        {OPERATOR_NAME} · {STOPS.length} stops · {boxes.length} boxes
      </p>

      <ul className="stat-tiles">
        {stats.map(([icon, value, label]) => (
          <li className="stat-tile" key={label}>
            <span className="stat-tile__icon" aria-hidden="true">{icon}</span>
            <span>
              <strong className="data">{value}</strong>
              <span className="muted">{label}</span>
            </span>
          </li>
        ))}
      </ul>

      <section className="card van-card">
        <h2>Today’s load</h2>
        <ul className="box-list">
          {boxes.map((box) => (
            <li className="box-row" key={box.id}>
              <span className="badge">{box.id}</span>
              <span className="box-row__label">{box.label}</span>
              <span className="data muted">
                {box.length} × {box.width} × {box.height} cm · {box.weight} kg
              </span>
            </li>
          ))}
        </ul>
      </section>

      <Link className="button button--block" to="/app/scan">
        Scan a package <span aria-hidden="true">→</span>
      </Link>

      {/* The round is reference, not the next action: the operator loads first and drives after, so
          this sits under the main button rather than competing with it. */}
      <Link className="button button--block button--quiet" to="/app/route">
        See today’s round <span aria-hidden="true">→</span>
      </Link>
    </>
  );
}
