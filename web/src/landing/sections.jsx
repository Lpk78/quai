import { Link } from "react-router-dom";

import logoLight from "../../../assets/brand/logo/quai-logo-light.svg";
import logoDark from "../../../assets/brand/logo/quai-logo-dark.svg";
import { IconBraces, IconBox, IconCube, IconMic, IconPin, IconPlay, IconSpeech } from "./icons.jsx";
import { HomeScreen, PlanScreen, StopsScreen, VoiceScreen } from "./screens.jsx";

/* Every word below is bound by the copy rules in documentation/design.md: one slogan, never claiming
   the AI plans the load or orders the stops, and nothing about a route, an ETA, live tracking,
   navigation, pricing, or a measured saving. The supplied mockups break all of those; they are
   followed for layout and colour only. */

export const NAV_LINKS = [
  ["How it works", "#how-it-works"],
  ["Features", "#features"],
  ["Why QUAI", "#why-quai"],
];

/* A responsive <img>: three WebP widths, so a phone does not download the desktop file. */
function Picture({ name, widths, sizes, alt, className = "", loading = "lazy" }) {
  const srcSet = widths.map((w) => `/images/${name}-${w}.webp ${w}w`).join(", ");
  return (
    <img
      className={className}
      src={`/images/${name}-${widths[widths.length - 1]}.webp`}
      srcSet={srcSet}
      sizes={sizes}
      alt={alt}
      loading={loading}
      decoding="async"
    />
  );
}

/* 1 — the floating white bar ------------------------------------------------------------------ */

export function Nav() {
  return (
    <header className="nav">
      <nav className="nav__bar" aria-label="Main">
        <a className="nav__logo" href="#top" aria-label="QUAI, top of page">
          <img src={logoLight} alt="QUAI" width="790" height="300" />
        </a>
        <ul className="nav__links">
          {NAV_LINKS.map(([label, href]) => (
            <li key={href}>
              <a href={href}>{label}</a>
            </li>
          ))}
        </ul>
        <div className="nav__actions">
          <Link className="button button--quiet" to="/app">
            Log in
          </Link>
          <Link className="button" to="/app">
            Get started <span aria-hidden="true">→</span>
          </Link>
        </div>
      </nav>
    </header>
  );
}

/* 2 — hero ------------------------------------------------------------------------------------ */

const HERO_POINTS = [
  [<IconMic key="i" />, "Voice rules", "Just say it"],
  [<IconCube key="i" />, "3D load plan", "Every parcel placed"],
  [<IconPin key="i" />, "Stop order", "Right parcels at the doors"],
];

export function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero__text">
        <p className="eyebrow">Load planning for delivery teams</p>
        <h1>
          People talk.
          <br />
          We load.
        </h1>
        <p className="hero__sub">
          Say how the load has to go. QUAI turns your words into rules it can check, and a solver
          works out where every parcel goes: last stop at the back, first stop at the doors.
        </p>
        <div className="hero__actions">
          <Link className="button" to="/app">
            Get started <span aria-hidden="true">→</span>
          </Link>
          <a className="button button--film" href="#how-it-works">
            <span className="button__play" aria-hidden="true">
              <IconPlay width="14" height="14" />
            </span>
            Watch the film
          </a>
        </div>
        <ul className="hero__points">
          {HERO_POINTS.map(([icon, title, body]) => (
            <li key={title}>
              {icon}
              <span>
                <strong>{title}</strong>
                <span>{body}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="hero__image">
        <Picture
          name="hero_dock_wide"
          widths={[640, 1024, 1600]}
          sizes="(max-width: 900px) 100vw, 60vw"
          alt="An operator on a loading dock, checking parcels on a phone beside an open van."
          loading="eager"
        />
      </div>
    </section>
  );
}

/* 3 — how QUAI works -------------------------------------------------------------------------- */

const STEPS = [
  ["Scan", "Scan each parcel. Size and weight come from your catalogue."],
  [
    "Say the rules",
    "“Paint cans last, nothing on the glass.” QUAI reads back what it understood and asks when it is not sure.",
  ],
  [
    "Get the 3D plan",
    "The solver places every parcel: no overlaps, every box supported, weight limits respected.",
  ],
  [
    "Load in stop order",
    "Follow the plan one parcel at a time. The first stop’s parcels end up right behind the doors.",
  ],
];

export function HowItWorks() {
  return (
    <section className="how" id="how-it-works">
      <div className="how__card">
        <h2>How QUAI works</h2>
        <div className="how__grid">
          <ol className="how__steps how__steps--first">
            {STEPS.slice(0, 2).map(([title, body], i) => (
              <Step key={title} n={i + 1} title={title} body={body} />
            ))}
          </ol>
          <div className="how__phone">
            <HomeScreen />
          </div>
          <ol className="how__steps how__steps--second" start="3">
            {STEPS.slice(2).map(([title, body], i) => (
              <Step key={title} n={i + 3} title={title} body={body} />
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}

function Step({ n, title, body }) {
  return (
    <li className="step">
      <span className="step__n data" aria-hidden="true">
        {n}
      </span>
      <div>
        <h3>{title}</h3>
        <p>{body}</p>
      </div>
    </li>
  );
}

/* 4 — the three feature panels ------------------------------------------------------------------ */

export function Features() {
  return (
    <section className="features" id="features">
      <article className="panel">
        <p className="eyebrow">Voice to plan</p>
        <h2>Just tell QUAI how to load</h2>
        <p className="panel__body">
          Say it the way you would say it on the dock. What QUAI is not sure about comes back as a
          question, never as a guess.
        </p>
        <VoiceScreen />
      </article>

      <article className="panel">
        <p className="eyebrow">3D loading plan</p>
        <h2>See every parcel in place</h2>
        <ul className="panel__list">
          <li>Respects your rules</li>
          <li>Clear visual guidance</li>
          <li>Replans when a parcel is missing</li>
        </ul>
        <PlanScreen />
      </article>

      <article className="panel">
        <p className="eyebrow">Stop order</p>
        <h2>The right parcels at the right doors</h2>
        <p className="panel__body">
          Your delivery list sets the stop order. QUAI loads to match it, so the first stop comes off
          first. <strong>QUAI does not plan your route</strong> — there is no map here, and there is
          not meant to be.
        </p>
        <StopsScreen />
        <Picture
          className="panel__image"
          name="van_stops_colours"
          widths={[400, 640, 1024]}
          sizes="(max-width: 900px) 90vw, 30vw"
          alt="The back of a loaded van, parcels grouped by colour for each stop."
        />
      </article>
    </section>
  );
}

/* 5 — the navy band ----------------------------------------------------------------------------- */

export function Band() {
  return (
    <section className="band">
      <div className="band__text">
        <img className="band__logo" src={logoDark} alt="QUAI" width="850" height="360" />
        <p className="band__line">People talk. We load.</p>
      </div>
      <Picture
        className="band__image"
        name="scan_parcel"
        widths={[400, 640, 1024]}
        sizes="(max-width: 900px) 60vw, 28vw"
        alt="An operator scanning a parcel with a phone."
      />
    </section>
  );
}

/* 6 — why the model never places a box ----------------------------------------------------------- */

const CHAIN = [
  [<IconSpeech key="i" />, "You say", "“Paint cans last, nothing on the glass.”"],
  [<IconBraces key="i" />, "Validated JSON", "Checked against the contract, or refused."],
  [<IconBox key="i" />, "3D plan", "Computed by the solver, the same way every time."],
];

export function WhyQuai() {
  return (
    <section className="why" id="why-quai">
      <h2>The model never places a box.</h2>
      <p className="why__body">
        Language models write layouts that look right and are not: boxes overlap, float, change from
        one run to the next. In QUAI the AI only translates what you say; placement comes from a
        solver that is checked, repeatable and explainable.
      </p>
      <ol className="why__chain">
        {CHAIN.map(([icon, title, body]) => (
          <li className="why__card" key={title}>
            <span className="why__icon" aria-hidden="true">
              {icon}
            </span>
            <h3>{title}</h3>
            <p>{body}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}

/* 7 — a day on the dock -------------------------------------------------------------------------- */

const TILES = [
  ["scan_parcel", "Scan the parcels", "An operator scanning a parcel with a phone."],
  [
    "van_stops_colours",
    "Loaded in stop order",
    "The back of a loaded van, parcels grouped by colour for each stop.",
  ],
  [
    "doorstep_handover",
    "The right parcel, first time",
    "An operator handing a parcel to someone at their door.",
  ],
];

export function DayOnTheDock() {
  return (
    <section className="dock">
      <h2>A day on the dock</h2>
      <div className="dock__tiles">
        {TILES.map(([name, caption, alt]) => (
          <figure className="dock__tile" key={name}>
            <Picture
              name={name}
              widths={[400, 640, 1024]}
              sizes="(max-width: 900px) 90vw, 30vw"
              alt={alt}
            />
            <figcaption>{caption}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

/* 8 — closing call to action and footer ----------------------------------------------------------- */

export function FinalCta() {
  return (
    <section className="cta">
      <h2>Next van, fewer surprises.</h2>
      <div className="cta__actions">
        <Link className="button" to="/app">
          Get started <span aria-hidden="true">→</span>
        </Link>
        <Link className="button button--quiet" to="/app">
          Log in
        </Link>
      </div>
    </section>
  );
}

export function LandingFooter() {
  return (
    <footer className="foot">
      <p>© 2026 QUAI · People talk. We load.</p>
      <ul>
        {NAV_LINKS.map(([label, href]) => (
          <li key={href}>
            <a href={href}>{label}</a>
          </li>
        ))}
      </ul>
    </footer>
  );
}
