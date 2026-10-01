import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import jsQR from "jsqr";

import { SiteFooter, SiteHeader } from "../components.jsx";
import { OPERATOR_CARD_ID, OPERATOR_NAME } from "../data/manifest.js";
import "../app.css";

/* The way into the app: the operator points the camera at the QR code on their card.
 *
 * `jsqr` decodes a still image and nothing else — no camera handling, no DOM of its own — so the
 * video element, the framing and every failure state below are ours, styled from tokens.css like
 * the rest of the app.
 *
 * The camera needs a secure context. The phone demo serves HTTPS for that reason (README, "Phone
 * demo"), but a machine with no certificate, a phone that does not trust the one there is, and jsdom
 * all land in the same place: `navigator.mediaDevices` absent. That is not an error state to
 * apologise for — it is the manual-entry state, the same shape as the dictate screen's text field
 * when speech recognition is missing, and it is how the tests reach this path.
 */

// How long the operator's name stays on screen before the app opens. Long enough to read who was
// signed in, short enough that nobody taps "Continue" first.
const WELCOME_MS = 1200;

const OPERATORS = { [OPERATOR_CARD_ID]: OPERATOR_NAME };

const CODE_PATTERN = /^QUAI:OPERATOR:([A-Za-z0-9-]+)$/;

/* Reads one scanned or typed string. Exported because this is the whole contract of the screen:
   what counts as a card, and what the operator is told when it is not one. */
export function readOperatorCode(text) {
  const match = CODE_PATTERN.exec(String(text ?? "").trim());
  if (!match) return { ok: false, reason: "not-a-card" };
  const id = match[1];
  const name = OPERATORS[id];
  if (!name) return { ok: false, reason: "unknown-card", id };
  return { ok: true, id, name };
}

const REFUSAL_TEXT = {
  "not-a-card": "That is not a QUAI operator card.",
  "unknown-card": "That card is not on this van’s round.",
};

export default function Login() {
  const [status, setStatus] = useState("starting"); // starting | scanning | no-camera | signed-in
  const [refusal, setRefusal] = useState(null);
  const [operator, setOperator] = useState(null);
  const [typed, setTyped] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const navigate = useNavigate();

  // Held in a ref as well as in state: the scan loop runs outside React and must stop on the first
  // good code rather than on the next render.
  const doneRef = useRef(false);

  function accept(result) {
    if (result.ok) {
      doneRef.current = true;
      setRefusal(null);
      setOperator(result);
      setStatus("signed-in");
      return;
    }
    setRefusal(result);
  }

  useEffect(() => {
    if (status !== "signed-in") return undefined;
    const timer = setTimeout(() => navigate("/app"), WELCOME_MS);
    return () => clearTimeout(timer);
  }, [status, navigate]);

  useEffect(() => {
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("no-camera");
      return undefined;
    }

    let live = true;
    let stream = null;
    let frame = 0;

    function scan() {
      frame = requestAnimationFrame(scan);
      const video = videoRef.current;
      const canvas = canvasRef.current;
      if (doneRef.current || !video || !canvas || !video.videoWidth) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const context = canvas.getContext("2d");
      // A browser with no 2D context is a browser that cannot decode a frame: the typed field
      // below still works, and the screen must not fall over on the way to telling them so.
      if (!context) return;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);

      let found = null;
      try {
        const { data, width, height } = context.getImageData(0, 0, canvas.width, canvas.height);
        // A frame with no code in it decodes to null, which is the common case, not a failure.
        found = jsQR(data, width, height);
      } catch {
        // A frame that cannot be read at all is one dropped frame, not a broken screen: the next
        // one is 16 ms away. Nothing here is allowed to take the screen down.
        found = null;
      }
      if (found?.data) accept(readOperatorCode(found.data));
    }

    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" } })
      .then((opened) => {
        if (!live) {
          opened.getTracks().forEach((track) => track.stop());
          return;
        }
        stream = opened;
        if (videoRef.current) {
          videoRef.current.srcObject = opened;
          videoRef.current.play().catch(() => {});
        }
        setStatus("scanning");
        scan();
      })
      .catch(() => {
        // Refused, in use, or no camera on this device: all one thing to the operator, who has a
        // card to type in either way.
        if (live) setStatus("no-camera");
      });

    return () => {
      live = false;
      cancelAnimationFrame(frame);
      stream?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  function handleTyped(event) {
    event.preventDefault();
    accept(readOperatorCode(typed));
  }

  return (
    <div className="page">
      <SiteHeader />
      <main className="shell-main">
        <div className="wrap wrap--app">
          {status === "signed-in" ? (
            <SignedIn name={operator.name} />
          ) : (
            <>
              <h1>Scan your operator card</h1>
              <p className="muted">
                Point the camera at the QR code on the card. QUAI reads who is driving — nothing
                else.
              </p>

              <div className="scanner" data-status={status}>
                {/* Kept mounted while starting so the stream has somewhere to go the moment the
                    camera opens; hidden from assistive tech, which has nothing to read in it. */}
                <video
                  ref={videoRef}
                  className="scanner__video"
                  autoPlay
                  playsInline
                  muted
                  aria-hidden="true"
                />
                <canvas ref={canvasRef} className="scanner__canvas" aria-hidden="true" />
                {status === "scanning" && <div className="scanner__frame" aria-hidden="true" />}
                {status === "no-camera" && (
                  <p className="muted scanner__fallback">
                    No camera here. Over the phone demo’s <code className="data">http://</code>
                    {" "}address there cannot be one — type the code on the card instead.
                  </p>
                )}
              </div>

              {status === "scanning" && (
                <p className="muted" role="status">
                  Looking for a card…
                </p>
              )}

              {refusal && (
                <div className="card status-card" role="alert">
                  <p>{REFUSAL_TEXT[refusal.reason]}</p>
                  {refusal.id && <p className="muted data">{refusal.id}</p>}
                  <p className="muted">
                    {status === "scanning"
                      ? "Still looking — hold the card flat, or type it in below."
                      : "Check the code and try again."}
                  </p>
                </div>
              )}

              <form className="field" onSubmit={handleTyped}>
                <label className="field__label" htmlFor="operator-code">
                  Operator code
                </label>
                <input
                  id="operator-code"
                  className="field__input"
                  value={typed}
                  onChange={(event) => setTyped(event.target.value)}
                  placeholder="QUAI:OPERATOR:…"
                  autoComplete="off"
                  spellCheck="false"
                />
                <button type="submit" className="button button--block" disabled={!typed.trim()}>
                  Sign in <span aria-hidden="true">→</span>
                </button>
              </form>
            </>
          )}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}

function SignedIn({ name }) {
  return (
    <div className="signed-in">
      <h1>Good morning, {name}.</h1>
      <p className="muted" role="status">
        Card read. Opening your van…
      </p>
      <Link className="button button--block" to="/app">
        Continue <span aria-hidden="true">→</span>
      </Link>
    </div>
  );
}
