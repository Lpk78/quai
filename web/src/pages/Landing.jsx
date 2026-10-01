import { Link } from "react-router-dom";

import { SiteFooter, SiteHeader } from "../components.jsx";

/* Every word on this page is bound by the copy rules in documentation/design.md:
   one slogan, never saying the AI plans the load or orders the stops, and nothing about
   features the app does not have — no route, no ETA, no tracking, no pricing. */

const STEPS = [
  {
    title: "You say it",
    body: "Tell QUAI how the load has to go, in the words you would use on the dock. " +
      "Nothing on the glass table. The toolbox last. Nothing over 20 kg on the cartons.",
  },
  {
    title: "It becomes rules",
    body: "What you said is turned into constraints QUAI can check. Anything it is not sure " +
      "about comes back as a question rather than a guess.",
  },
  {
    title: "The solver places",
    body: "A deterministic solver works out where every box goes, and tells you plainly which " +
      "ones it could not fit and why.",
  },
];

export default function Landing() {
  return (
    <div className="page">
      <SiteHeader
        action={
          <Link className="button" to="/app">
            Open the app <span aria-hidden="true">→</span>
          </Link>
        }
      />

      <main>
        <section className="hero">
          <div className="wrap">
            <h1 className="slogan">People talk. We load.</h1>
            <p>
              Say how the load has to go. QUAI turns what you said into rules it can check, and a
              solver works out where every box fits.
            </p>
            <div className="actions">
              <Link className="button" to="/app">
                Open the app <span aria-hidden="true">→</span>
              </Link>
              <a className="button button--quiet" href="https://github.com/Lpk78/quai">
                See the code
              </a>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="wrap">
            <h2>How it works</h2>
            <div className="grid">
              {STEPS.map((step, index) => (
                <article className="card" key={step.title}>
                  <span className="step-number" aria-hidden="true">{index + 1}</span>
                  <h3>{step.title}</h3>
                  <p className="muted">{step.body}</p>
                </article>
              ))}
            </div>
            <p className="note muted">
              <strong>QUAI does not plan your route.</strong> The delivery order arrives with your
              manifest. The loading order follows from it, so the first stop comes off first.
            </p>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
