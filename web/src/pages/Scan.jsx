import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { SCANNED_PARCEL, loadWith } from "../data/manifest.js";
import { identify } from "../scan/scanCode.js";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

/* The step before dictating: read the label on the package in the operator's hands, so the sentence
   they say next is about something QUAI can name.

   The camera is not here yet. `LP-20` chose the QR library and had not landed when this was written,
   so rather than guess at a dependency and rip it out later the code arrives through `identify()` from
   whatever feeds it — a typed field today, decoded frames once #55's `jsqr` loop is shared out of
   `Login.jsx`. The field is
   not a placeholder for the demo's sake either: it is the fallback a dock needs when a label is
   scuffed, wet, or the phone has no camera permission.

   A scan puts the parcel into the load (`SA-17b`). `SCANNED_PARCEL` is held out of `BOXES` so that
   there is something to add: reading its label is what moves it from "in the operator's hands" to "in
   the van", and /app/dictate then plans nineteen boxes rather than eighteen. A label for a box that is
   already aboard is recognised and shown, but adds nothing — it was never outside the load.

   No new class names: HY-15 is visual polish across these screens, so this screen is built from the
   shared ones already in `app.css` rather than adding selectors into a file being reworked underneath
   it. Styling hooks are his to add. */
export default function Scan() {
  const [code, setCode] = useState("");
  const [found, setFound] = useState(null);
  const { parcel, scan } = useScannedParcel();
  const navigate = useNavigate();

  const box = found?.status === "known" ? found.box : null;
  // Reading the parcel's label is what puts it in the van; a box that was already loaded is simply
  // confirmed. `alreadyAboard` is the second scan of the same label — nothing to add twice.
  const isParcel = box?.id === SCANNED_PARCEL.id;
  const alreadyAboard = isParcel && Boolean(parcel);

  function handleSubmit(event) {
    event.preventDefault();
    // Matched against the whole load, parcel included, so a second scan of the same label is
    // recognised rather than reported as a box this van is not carrying.
    setFound(identify(code, loadWith(SCANNED_PARCEL)));
  }

  function handleContinue() {
    if (isParcel) scan(SCANNED_PARCEL);
    navigate("/app/dictate");
  }

  return (
    <>
      <Link className="muted back-link" to="/app">
        ← Home
      </Link>

      <h1>Scan the package</h1>
      <p className="muted">
        Point the label at the camera, or type the code underneath it.
      </p>

      <div className="card">
        <p className="muted">
          The camera step is still being built. Until it lands, the code under the QR square does the
          same job.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <label className="field">
          <span className="field__label">Package code</span>
          <input
            type="text"
            inputMode="text"
            autoCapitalize="characters"
            spellCheck={false}
            value={code}
            onChange={(event) => setCode(event.target.value)}
            placeholder="QUAI:BOX:QUAI-BOX-0001"
          />
        </label>
        <button type="submit" className="button button--block" disabled={!code.trim()}>
          Read code
        </button>
      </form>

      {found?.status === "unreadable" && (
        <div className="card status-card" role="alert">
          <p>That is not a QUAI package label.</p>
          <p className="muted">
            A label reads <code className="data">QUAI:BOX:</code> followed by the box code.
          </p>
        </div>
      )}

      {found?.status === "unknown" && (
        <div className="card status-card" role="alert">
          <p>
            <span className="badge badge--warning">{found.id}</span> is not in today’s manifest.
          </p>
          <p className="muted">
            It is a QUAI label, but this box is not on this van. Check the round before loading it.
          </p>
        </div>
      )}

      {box && (
        <>
          <section className="card" aria-label="Scanned package">
            <h2>{box.label}</h2>
            <p>
              <span className="badge">{box.id}</span>
            </p>
            <p className="data muted">
              {box.length} × {box.width} × {box.height} cm · {box.weight} kg
            </p>
            <p className="muted">
              {alreadyAboard
                ? "Already added to this load."
                : isParcel
                  ? "Not loaded yet. Continue to say where it goes."
                  : "Already in the van."}
            </p>
          </section>

          <button
            type="button"
            className="button button--block"
            onClick={handleContinue}
          >
            Say what to do with it <span aria-hidden="true">→</span>
          </button>
        </>
      )}
    </>
  );
}
