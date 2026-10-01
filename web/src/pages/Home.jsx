import { Link } from "react-router-dom";

import { BOXES, OPERATOR_NAME, STOPS } from "../data/manifest.js";

export default function Home() {
  return (
    <>
      <h1>Good morning. Let’s load.</h1>
      <p className="muted">
        {OPERATOR_NAME} · {STOPS.length} stops · {BOXES.length} boxes
      </p>

      <section className="card van-card">
        <h2>Today’s load</h2>
        <ul className="box-list">
          {BOXES.map((box) => (
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

      <Link className="button button--block" to="/app/dictate">
        Dictate rules <span aria-hidden="true">→</span>
      </Link>
    </>
  );
}
