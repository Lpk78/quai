import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";

import { ApiError, postPlan } from "../api.js";
import LoadScene, { VIEWS, colourFor } from "../plan/LoadScene.jsx";
import { BOXES } from "../data/manifest.js";
import { DEMO_REQUEST } from "../plan/demoLoad.js";

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
    <section className="card plan-summary" aria-label="Plan summary">
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

function NotAppliedList({ notApplied }) {
  /* A rule the operator dictated that did not reach the solver — read straight off the response
     rather than guessed at, same as `unplaced`. Shown, never dropped: the honesty rule this screen
     already follows for a box that did not fit applies just as much to a rule that did not apply. */
  if (!notApplied || notApplied.length === 0) return null;
  return (
    <section className="plan-unplaced" aria-label="Rules that were not applied">
      <h2>Not applied</h2>
      <ul className="plan-list">
        {notApplied.map((entry, index) => (
          <li className="plan-item plan-item--unplaced" key={index} data-testid="not-applied">
            <span className="plan-id">
              {entry.type}
              {entry.item ? `: ${entry.item}` : ""}
            </span>
            <span className="muted">{entry.reason}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function Failure({ error, onRetry }) {
  const unreachable = error.kind === "unreachable";
  return (
    <section className="card plan-failure" role="alert">
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

/* The two faces of one round: what goes in the van, and where the van goes. A link, not a tab bar —
   the screens are separate routes and this does not restructure them. */
function ViewSwitch() {
  return (
    <nav className="plan-switch" aria-label="Plan views">
      <span className="plan-switch__tab plan-switch__tab--on" aria-current="page">Load view</span>
      <Link className="plan-switch__tab" to="/app/route">Delivery order</Link>
    </nav>
  );
}

/* Which stop a box comes off at, read from the manifest the plan was built from.
 *
 * `POST /plan` carries no stop — the solver is given dimensions and weights, nothing else — so this is
 * a lookup, not a field of the response, and it returns nothing when the plan is the eleven-box demo
 * whose ids the manifest has never heard of. Omitted rather than guessed in that case, the same rule
 * that keeps the mockup's "A-12" off this screen.
 */
function stopOf(boxId) {
  return BOXES.find((box) => box.id === boxId)?.stop ?? null;
}

/* The box the operator should pick up next, and what they need to know to find it.
 *
 * The mockup reads "Stop 3 · A-12 / Medium · 8 kg". `A-12` is a storage reference we have nowhere in
 * the data, so it is not shown. "Medium" is a size bucket we do not have either: the real dimensions
 * are what the plan holds, so those are what this says.
 */
function NextBox({ placement, position, total, weight, stop }) {
  if (!placement) {
    return (
      <aside className="card plan-next plan-next--done" aria-label="Next box">
        <h2>All loaded</h2>
        <p className="muted">Every box in the plan has been marked loaded.</p>
      </aside>
    );
  }
  return (
    <aside className="card plan-next" aria-label="Next box">
      <h2>Next box</h2>
      <p className="plan-next__who">
        {stop && <span className="plan-next__stop">{stop}</span>}
        <strong className="data">{placement.id}</strong>
      </p>
      <p className="muted data">
        {placement.dx} × {placement.dy} × {placement.dz} cm
        {weight != null && <> · {weight} kg</>}
      </p>
      <p className="muted plan-next__rank">{position} of {total} in the loading order</p>
    </aside>
  );
}

/* 3D, Top, Left, Right. Large targets on purpose: this is read through handling gloves. */
function ViewControls({ view, onView }) {
  return (
    <div className="plan-views" role="group" aria-label="Camera view">
      {Object.keys(VIEWS).map((name) => (
        <button
          type="button"
          key={name}
          className={`plan-view${view === name ? " plan-view--on" : ""}`}
          aria-pressed={view === name}
          onClick={() => onView(name)}
        >
          {name}
        </button>
      ))}
    </div>
  );
}

/* How far through the load the operator is, and whether the plan they are following is complete.
 *
 * Two different facts, kept apart. The bar is progress through the loading order; the line beside it
 * is about the plan itself. "All items placed" appears only when nothing was left unplaced **and** no
 * constraint went unapplied — a green tick over an incomplete plan is the exact lie this project
 * refuses, and the counts are shown instead whenever there is one.
 */
function LoadProgress({ loaded, total, unplaced, notApplied }) {
  const complete = unplaced.length === 0 && notApplied.length === 0;
  const percent = total === 0 ? 0 : Math.round((loaded / total) * 100);
  return (
    <section className="card plan-progress" aria-label="Loading progress">
      <div className="plan-progress__count">
        <strong data-testid="loaded-count">{loaded} / {total} loaded</strong>
        <div className="plan-progress__bar">
          <div className="plan-progress__fill" style={{ width: `${percent}%` }} />
        </div>
      </div>
      {complete ? (
        <p className="plan-progress__state plan-progress__state--ok" data-testid="plan-state">
          <span aria-hidden="true">✓</span> All items placed
        </p>
      ) : (
        <p className="plan-progress__state plan-progress__state--warn" data-testid="plan-state">
          {unplaced.length > 0 && <>{unplaced.length} not placed</>}
          {unplaced.length > 0 && notApplied.length > 0 && <> · </>}
          {notApplied.length > 0 && <>{notApplied.length} rule{notApplied.length > 1 ? "s" : ""} not applied</>}
        </p>
      )}
    </section>
  );
}

export default function PlanScreen({ loadPlan = postPlan, request: requestProp }) {
  const location = useLocation();
  // Dictate.jsx already called `postPlan` before navigating here with the result in `state`, so
  // this screen shows it rather than asking the solver the same question twice. Visited directly —
  // the URL bar, a reload — there is no `state`, and the screen falls back to its own demo request.
  const seededPlan = location.state?.plan ?? null;
  const request = requestProp ?? location.state?.request ?? DEMO_REQUEST;

  const [state, setState] = useState(() =>
    seededPlan ? { status: "ready", plan: seededPlan } : { status: "loading" },
  );
  const [attempt, setAttempt] = useState(0);
  const [selected, setSelected] = useState(null);
  const [view, setView] = useState("3D");
  // How many boxes the operator has marked loaded. The solver's placement order *is* the loading
  // order, so advancing this index is not an invention — it is what that order means.
  const [loaded, setLoaded] = useState(0);

  useEffect(() => {
    if (attempt === 0 && seededPlan) {
      setState({ status: "ready", plan: seededPlan });
      return;
    }
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
  }, [loadPlan, request, attempt, seededPlan]);

  const requested = request.boxes.length;
  const placements = state.status === "ready" ? state.plan.placements : [];
  // The next box is the one at the loading index; past the end there is none and the screen says so.
  const nextPlacement = placements[loaded] ?? null;
  // Weight is on the request, not on the placement `POST /plan` returns, so it is read from what was
  // sent. Absent — a demo load without weights — it is left off rather than shown as zero.
  const weightOf = (id) => request.boxes.find((box) => box.id === id)?.weight ?? null;

  return (
    <div className="page plan-page">
      <header className="plan-header">
        <Link className="plan-back" to="/app">Back</Link>
        <h1>Load plan</h1>
      </header>

      <ViewSwitch />

      <main className="plan-main">
        <p className="muted note">
          A load of {requested} boxes, planned by the solver. Entering your own boxes is issue #8.
        </p>

        {state.status === "loading" && <p role="status">Asking the solver…</p>}

        {state.status === "failed" && (
          <Failure error={state.error} onRetry={() => setAttempt((n) => n + 1)} />
        )}

        {state.status === "ready" && (
          <>
            <div className="plan-stage">
              <section className="plan-scene" aria-label="The load in three dimensions">
                <LoadScene
                  plan={state.plan}
                  container={request.container}
                  selected={selected ?? nextPlacement?.id ?? null}
                  onSelect={setSelected}
                  view={view}
                />
              </section>
              <NextBox
                placement={nextPlacement}
                position={Math.min(loaded + 1, state.plan.placements.length)}
                total={state.plan.placements.length}
                weight={weightOf(nextPlacement?.id)}
                stop={nextPlacement ? stopOf(nextPlacement.id) : null}
              />
              <ViewControls view={view} onView={setView} />
            </div>

            <LoadProgress
              loaded={loaded}
              total={state.plan.placements.length}
              unplaced={state.plan.unplaced}
              notApplied={state.plan.not_applied ?? []}
            />

            <button
              type="button"
              className="button button--block"
              disabled={loaded >= state.plan.placements.length}
              onClick={() => setLoaded((n) => Math.min(n + 1, state.plan.placements.length))}
            >
              Loaded, next <span aria-hidden="true">→</span>
            </button>
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
            <NotAppliedList notApplied={state.plan.not_applied} />
          </>
        )}
      </main>
    </div>
  );
}
