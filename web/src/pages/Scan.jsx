import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { SCANNED_PARCEL, loadWith } from "../data/manifest.js";
import { identify } from "../scan/scanCode.js";
import QrScanner from "../scan/QrScanner.jsx";
import { useScannedParcel } from "../scan/scannedParcel.jsx";

/* The step before dictating: read the label on the package in the operator's hands, so the sentence
   they say next is about something QUAI can name.

   The camera arrived in `HY-18`, through the `QrScanner` lifted out of `Login.jsx` — which is what
   this file was written against and said so. It feeds `read()`, the same function the typed field
   feeds, so a decoded label and a typed one are the same event from here on: same `identify()`, same
   result card, same confirmation. The camera fills the field the finger used to fill, and nothing
   more.

   The field stays, above all else. It is what makes this screen safe to demo: a label on a dock is
   scuffed, wet, in the dark, or behind a camera permission someone declined, and every one of those
   ends at the same place — type the code under the QR square. The camera is the fast path, never the
   only one.

   A scan puts the parcel into the load (`SA-17b`). `SCANNED_PARCEL` is held out of `BOXES` so that
   there is something to add: reading its label is what moves it from "in the operator's hands" to "in
   the van", and /app/dictate then plans nineteen boxes rather than eighteen. A label for a box that is
   already aboard is recognised and shown, but adds nothing — it was never outside the load. */
/* Why there is no viewfinder, in this screen's own words — the operator card is `/login`'s problem,
   a package label is this one's. Each says what happened and sends the operator to the field below,
   because a camera that silently does nothing is the failure this project refuses. */
const NO_CAMERA_TEXT = {
  insecure: "This page is not on a secure address, so the camera cannot open. "
    + "Type the code under the QR square instead.",
  unsupported: "No camera on this device. Type the code under the QR square instead.",
  refused: "The camera was not allowed. Type the code under the QR square instead, "
    + "or allow the camera and reload.",
};

export default function Scan() {
  const [code, setCode] = useState("");
  const [found, setFound] = useState(null);
  // Bumped to let the camera decode again after it has stopped on a label. See `QrScanner`.
  const [resumeToken, setResumeToken] = useState(0);
  const { parcel, scan } = useScannedParcel();
  const navigate = useNavigate();

  const box = found?.status === "known" ? found.box : null;
  // Reading the parcel's label is what puts it in the van; a box that was already loaded is simply
  // confirmed. `alreadyAboard` is the second scan of the same label — nothing to add twice.
  const isParcel = box?.id === SCANNED_PARCEL.id;
  const alreadyAboard = isParcel && Boolean(parcel);

  /* The one way a code becomes a result, whether a finger typed it or the camera read it.
     `HY-18` put the camera on this screen by pointing it at this function rather than giving it a
     path of its own: the field shows what was decoded, the same `identify()` judges it, and the
     same confirmation button below sends it on. A camera that skipped the confirmation would be one
     gesture shorter and a second source of truth, which is the worse trade. */
  function read(raw) {
    setCode(raw);
    // Matched against the whole load, parcel included, so a second scan of the same label is
    // recognised rather than reported as a box this van is not carrying.
    setFound(identify(raw, loadWith(SCANNED_PARCEL)));
  }

  function handleSubmit(event) {
    event.preventDefault();
    read(code);
  }

  /* The explicit resume. A label is read, shown, and the camera stops — so the operator reads the
     result rather than watching it flicker between whatever passes the lens. This is what lets them
     read the next parcel without leaving the screen. */
  function readAnother() {
    setFound(null);
    setCode("");
    setResumeToken((n) => n + 1);
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

      {/* The viewfinder sits above the field, and never replaces it: a label on a dock is scuffed,
          wet or in the dark often enough that typing the code has to stay one glance away. */}
      <QrScanner
        onCode={(text) => { read(text); return true; }}
        resumeToken={resumeToken}
        fallback={(why) => (
          <p className="muted scanner__fallback">{NO_CAMERA_TEXT[why] ?? NO_CAMERA_TEXT.unsupported}</p>
        )}
      >
        {(status) => (status === "scanning" ? (
          <>
            <p className="muted" role="status">
              {found
                ? "Label read. Check it below, or read another."
                : "Hold the label inside the frame…"}
            </p>
            {/* Only while a camera is actually running: with no camera there is nothing to resume,
                and the field below is already the way to read the next one. */}
            {found && (
              <button type="button" className="button button--quiet" onClick={readAnother}>
                Read another label
              </button>
            )}
          </>
        ) : null)}
      </QrScanner>

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
