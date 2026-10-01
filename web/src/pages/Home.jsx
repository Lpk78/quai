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
        <h2>Loading plan ready</h2>
        <p className="muted">
          Scan each parcel as you load it, and say any rules QUAI needs to know.
        </p>
        <Link className="button button--block" to="/app/scan">
          Start loading <span aria-hidden="true">→</span>
        </Link>
      </section>

      {/* `SA-21`'s link to the round, kept: "Start loading" above is the next action and now lives
          inside the summary card, so the separate "Scan a package" button it replaced is gone. The
          round is reference rather than the next step, so it stays the quiet one. */}
      <Link className="button button--block button--quiet" to="/app/route">
        See today’s round <span aria-hidden="true">→</span>
      </Link>
    </>
  );
}
