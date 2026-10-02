import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { SiteFooter, SiteHeader } from "../components.jsx";
import { OPERATOR_CARD_ID, OPERATOR_NAME } from "../data/manifest.js";
import QrScanner from "../scan/QrScanner.jsx";
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
  const [signedIn, setSignedIn] = useState(false);
  const [refusal, setRefusal] = useState(null);
  const [operator, setOperator] = useState(null);
  const [typed, setTyped] = useState("");
  const navigate = useNavigate();

  /* Returns whether the code counted, which is what stops `QrScanner`'s loop. A card for someone
     else returns false on purpose: the screen says so and keeps looking, rather than going dead on
     the first thing held up to it. `Login` never resumes after a good card — it passes no
     `resumeToken` — because a visit signs in once. */
  function accept(result) {
    if (result.ok) {
      setRefusal(null);
      setOperator(result);
      setSignedIn(true);
      return true;
    }
    setRefusal(result);
    return false;
  }

  useEffect(() => {
    if (!signedIn) return undefined;
    const timer = setTimeout(() => navigate("/app"), WELCOME_MS);
    return () => clearTimeout(timer);
  }, [signedIn, navigate]);

  function handleTyped(event) {
    event.preventDefault();
    accept(readOperatorCode(typed));
  }

  return (
    <div className="page">
      <SiteHeader />
      <main className="shell-main">
        <div className="wrap wrap--app">
          {signedIn ? (
            <SignedIn name={operator.name} />
          ) : (
            <>
              <h1>Scan your operator card</h1>
              <p className="muted">
                Point the camera at the QR code on the card. QUAI reads who is driving — nothing
                else.
              </p>

              {/* No `resumeToken`: a visit reads one card. `accept` returning false for a card
                  that is not ours is what keeps the loop alive after a refusal. */}
              <QrScanner
                onCode={(text) => accept(readOperatorCode(text))}
                fallback={() => (
                  <p className="muted scanner__fallback">
                    No camera here. Over the phone demo’s <code className="data">http://</code>
                    {" "}address there cannot be one — type the code on the card instead.
                  </p>
                )}
              >
                {(status) => (
                  <>
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
                  </>
                )}
              </QrScanner>

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
