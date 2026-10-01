import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { BOXES } from "../data/manifest.js";
import { identify } from "../scan/scanCode.js";

/* The step before dictating: read the label on the package in the operator's hands, so the sentence
   they say next is about something QUAI can name.

   The camera is not here yet. `LP-20` chooses the QR library, and had not landed when this was
   written, so rather than guess at a dependency and rip it out later the code arrives through
   `identify()` from whatever feeds it — a typed field today, decoded frames tomorrow. The field is
   not a placeholder for the demo's sake either: it is the fallback a dock needs when a label is
   scuffed, wet, or the phone has no camera permission.

   What this screen does NOT do: change the manifest. `QUAI-BOX-0001` already sits in
   `data/manifest.js` alongside the eighteen loaded boxes, so there is nothing here to add it to.
   Modelling a parcel that is scanned *into* a load — out of the static list, into app state, marked
   not yet loaded — is a structural change to that module and to the dictate screen, and it is its own
   task rather than a side effect of this one. Agreed with MORHI11 while HY-15 was in flight.

   No new class names either, for the same reason: HY-15 is visual polish across these screens, so this
   screen is built from the shared ones already in `app.css` rather than adding selectors into a file
   being reworked underneath it. Styling hooks are his to add. */
export default function Scan() {
  const [code, setCode] = useState("");
  const [found, setFound] = useState(null);
  const navigate = useNavigate();

  function handleSubmit(event) {
    event.preventDefault();
    setFound(identify(code, BOXES));
  }

  const box = found?.status === "known" ? found.box : null;

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
          </section>

          <button
            type="button"
            className="button button--block"
            onClick={() => navigate("/app/dictate")}
          >
            Say what to do with it <span aria-hidden="true">→</span>
          </button>
        </>
      )}
    </>
  );
}
