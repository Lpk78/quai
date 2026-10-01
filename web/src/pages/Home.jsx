import { Link } from "react-router-dom";

import { OPERATOR_NAME, STOPS, loadWith } from "../data/manifest.js";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

export default function Home() {
  // Eighteen, or nineteen once a parcel has been scanned. Reading the same `loadWith` the dictate
  // screen plans with, so the count here cannot say eighteen while the plan holds nineteen.
  const { parcel } = useScannedParcel();
  const boxes = loadWith(parcel);

  return (
    <>
      <h1>Good morning. Let’s load.</h1>
      <p className="muted">
        {OPERATOR_NAME} · {STOPS.length} stops · {boxes.length} boxes
      </p>

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
    </>
  );
}
