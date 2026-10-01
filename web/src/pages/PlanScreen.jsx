import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError, postPlan } from "../api.js";
import LoadScene, { colourFor } from "../plan/LoadScene.jsx";
import { DEMO_BOXES, DEMO_REQUEST } from "../plan/demoLoad.js";

/* The load plan at /app/plan.
 *
 * SA-14a was the list; SA-14b adds the 3D view. Colour by stop is SA-14c — see #7. What the
 * screen shows is bounded by what `POST /plan` returns: placements, unplaced, fill rate and
 * weight. There is no stop per box and no record of which constraint affected which, so it
 * shows neither rather than inventing them.
 *
 * Nothing that did not fit is ever hidden. A plan that quietly drops a box is worse than one that
 * says it could not place it, which is the whole reason `unplaced` exists in the response.
 */

function Summary({ plan, requested }) {
  const placed = plan.placements.length;
  return (
    <section className="plan-summary" aria-label="Plan summary">
      <p className="plan-count">
        <strong data-testid="placed-count">{placed} / {requested}</strong> placed
      </p>
      <dl className="plan-figures">
        <div>
          <dt>Fill rate</dt>
          <dd className="data">{Math.round(plan.fill_rate * 100)}%</dd>
        </div>
        <div>
          <dt>Total weight</dt>
          <dd className="data">{Math.round(plan.total_weight)} kg</dd>
        </div>
      </dl>
    </section>
  );
}

function Inspector({ placement, index }) {
  /* What the plan knows about one box. Not its stop and not the constraints applied to it: the
     response carries neither, and a panel with empty fields reads as missing data rather than
     absent data. SA-14c fills this in once #36 gives it something true to show. */
  if (!placement) {
    return <p className="muted plan-hint">Tap a box to see what it is.</p>;
  }
  return (
    <div className="plan-inspector" data-testid="inspector">
      <span className="plan-swatch" style={{ background: colourFor(index) }} aria-hidden="true" />
      <strong>{placement.id}</strong>
      <span className="data">{placement.dx} × {placement.dy} × {placement.dz} cm</span>
      <span className="data muted">at {placement.x}, {placement.y}, {placement.z}</span>
    </div>
  );
}

function PlacedList({ placements, selected, onSelect }) {
  if (placements.length === 0) {
    return <p className="muted">No box was placed.</p>;
  }
  return (
    <ol className="plan-list" aria-label="Placed boxes">
      {placements.map((p, index) => (
        <li
          className={`plan-item${selected === p.id ? " plan-item--selected" : ""}`}
          key={p.id}
          data-testid="placed-box"
          onClick={() => onSelect(p.id)}
        >
          <span className="plan-swatch" style={{ background: colourFor(index) }}
                aria-hidden="true" />
          <span className="plan-order" aria-hidden="true">{index + 1}</span>
          <span className="plan-id">{p.id}</span>
          <span className="plan-dims data">
            {p.dx} × {p.dy} × {p.dz}
          </span>
          <span className="plan-at data muted">
            at {p.x}, {p.y}, {p.z}
          </span>
        </li>
      ))}
    </ol>
  );
}

function UnplacedList({ unplaced }) {
  /* Always rendered, never conditional on there being something to say. An empty section that says
     "everything fitted" and a missing section look the same to a reader who is scrolling. */
  return (
    <section className="plan-unplaced" aria-label="Boxes that were not placed">
      <h2>Not placed</h2>
      {unplaced.length === 0 ? (
        <p className="muted" data-testid="all-placed">Everything fitted.</p>
      ) : (
        <ul className="plan-list">
          {unplaced.map((id) => (
            <li className="plan-item plan-item--unplaced" key={id} data-testid="unplaced-box">
              <span className="plan-id">{id}</span>
              <span className="muted">did not fit</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function Failure({ error, onRetry }) {
  const unreachable = error.kind === "unreachable";
  return (
    <section className="plan-failure" role="alert">
      <h2>No plan to show</h2>
      <p>{error.message}</p>
      {unreachable && (
        <p className="muted">
          The solver runs separately: <code className="data">uvicorn server:app --app-dir src</code>
        </p>
      )}
      {/* The server's own words, when they add something. A refused load usually has the detail
          *as* the message, and printing the same sentence twice reads like two problems. */}
      {error.detail && !unreachable && error.detail !== error.message && (
        <p className="muted data">{error.detail}</p>
      )}
      <button className="button" type="button" onClick={onRetry}>Try again</button>
    </section>
  );
}

export default function PlanScreen({ loadPlan = postPlan, request = DEMO_REQUEST }) {
  const [state, setState] = useState({ status: "loading" });
  const [attempt, setAttempt] = useState(0);
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    let live = true;
    setState({ status: "loading" });
    Promise.resolve()
      .then(() => loadPlan(request))
      .then((plan) => live && setState({ status: "ready", plan }))
      .catch((error) => {
        if (!live) return;
        const failure =
          error instanceof ApiError
            ? error
            : new ApiError("server", "The plan could not be loaded.", String(error));
        setState({ status: "failed", error: failure });
      });
    return () => {
      live = false;
    };
  }, [loadPlan, request, attempt]);

  const requested = request.boxes.length;

  return (
    <div className="page plan-page">
      <header className="plan-header">
        <Link className="plan-back" to="/app">Back</Link>
        <h1>Load plan</h1>
      </header>

      <main className="plan-main">
        <p className="muted note">
          A demo load of {DEMO_BOXES.length} boxes, planned by the solver. Entering your own
          boxes is issue #8.
        </p>

        {state.status === "loading" && <p role="status">Asking the solver…</p>}

        {state.status === "failed" && (
          <Failure error={state.error} onRetry={() => setAttempt((n) => n + 1)} />
        )}

        {state.status === "ready" && (
          <>
            <section className="plan-scene" aria-label="The load in three dimensions">
              <LoadScene
                plan={state.plan}
                container={request.container}
                selected={selected}
                onSelect={setSelected}
              />
            </section>
            <Inspector
              placement={state.plan.placements.find((p) => p.id === selected) || null}
              index={state.plan.placements.findIndex((p) => p.id === selected)}
            />
            <Summary plan={state.plan} requested={requested} />
            <section aria-label="Where each box goes">
              <h2>In the van</h2>
              <p className="muted note">
                Positions are the back-left floor corner of each box, in centimetres.
              </p>
              <PlacedList
                placements={state.plan.placements}
                selected={selected}
                onSelect={setSelected}
              />
            </section>
            <UnplacedList unplaced={state.plan.unplaced} />
          </>
        )}
      </main>
    </div>
  );
}
