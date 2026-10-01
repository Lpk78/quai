import { Link } from "react-router-dom";

import logoLight from "../../../assets/brand/logo/quai-logo-light.svg";
import logoOnNavy from "../../../assets/brand/logo/quai-logo-on-navy.svg";
import {
  IconBraces,
  IconClock,
  IconBox,
  IconCube,
  IconMic,
  IconPin,
  IconPlay,
  IconRule,
  IconSpeech,
  IconTick,
} from "./icons.jsx";

/* Layout and visual treatment follow `assets/brand/reference/website-mockup-v2.jpg` and
   `marketing-board.jpg`. The words do not: every one of them follows the copy rules in
   documentation/design.md, which those same mockups break. */

export const NAV_LINKS = [
  ["How it works", "#how-it-works"],
  ["Features", "#features"],
  ["Why QUAI", "#why-quai"],
];

/** A responsive <img>: several WebP widths, so a phone never downloads the desktop file. */
function Picture({ name, widths, sizes, alt, className = "", loading = "lazy" }) {
  return (
    <img
      className={className}
      src={`/images/${name}-${widths[widths.length - 1]}.webp`}
      srcSet={widths.map((w) => `/images/${name}-${w}.webp ${w}w`).join(", ")}
      sizes={sizes}
      alt={alt}
      loading={loading}
      decoding="async"
    />
  );
}

/** A supplied phone render, cut out of its studio background by assets/brand/cutout.py, so the page
    can give it a shadow that follows the phone rather than a grey box. */
function PhoneShot({ name, alt, className = "" }) {
  return (
    <Picture
      className={`phone-shot ${className}`}
      name={`${name}-cut`}
      widths={[320, 640]}
      sizes="(max-width: 760px) 60vw, 22vw"
      alt={alt}
    />
  );
}

/* 1 — the floating white bar ------------------------------------------------------------------ */

export function Nav() {
  return (
    <header className="nav">
      <nav className="nav__bar" aria-label="Main">
        <a className="nav__logo" href="#top" aria-label="QUAI, top of page">
          <img src={logoLight} alt="QUAI" width="845" height="280" />
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

/* 2 — hero: one card, the photograph across the whole of it, the text on its faded left --------- */

const HERO_POINTS = [
  [<IconMic key="i" />, "Voice rules", "Just say it"],
  [<IconCube key="i" />, "3D load plan", "Every parcel placed"],
  [<IconPin key="i" />, "Stop order", "Right parcels at the doors"],
];

export function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero__card">
        <Picture
          className="hero__image"
          name="hero_branded"
          widths={[640, 1024, 1600]}
          sizes="100vw"
          alt="A QUAI depot: an operator checking a phone beside a van loaded with parcels."
          loading="eager"
        />
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
            <Link className="button button--lg" to="/app">
              Get started <span aria-hidden="true">→</span>
            </Link>
            <a className="button button--lg button--film" href="#how-it-works">
              <span className="button__play" aria-hidden="true">
                <IconPlay width="14" height="14" />
              </span>
              Watch the film
            </a>
          </div>
          <ul className="hero__points">
            {HERO_POINTS.map(([icon, title, body]) => (
              <li key={title}>
                <span className="hero__point-icon" aria-hidden="true">
                  {icon}
                </span>
                <span>
                  <strong>{title}</strong>
                  <span>{body}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

/* 3 — how QUAI works --------------------------------------------------------------------------- */

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
          <ol className="how__steps">
            {STEPS.slice(0, 2).map(([title, body], i) => (
              <Step key={title} n={i + 1} title={title} body={body} />
            ))}
          </ol>
          <div className="how__phone">
            <PhoneShot name="phone_home" alt="The QUAI app home screen on a phone." />
          </div>
          <ol className="how__steps" start="3">
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

/* 4 — the three feature panels: text and bullets left, phone right ------------------------------ */

const PANELS = [
  {
    eyebrow: "Voice to plan",
    title: "Just tell QUAI how to load",
    bullets: [
      "Say it the way you would on the dock",
      "Read back before anything is planned",
      "A question when it is not sure, never a guess",
    ],
    shot: "phone_voice_rules",
    alt: "The QUAI app showing the loading rules it understood.",
  },
  {
    eyebrow: "3D loading plan",
    title: "See every parcel in place",
    bullets: ["Respects your rules", "Clear visual guidance", "Replans when a parcel is missing"],
    shot: "phone_3d_plan",
    alt: "The QUAI app showing the 3D load plan with the next parcel highlighted.",
  },
  {
    eyebrow: "Route and stop order",
    title: "The right parcels at the right doors",
    bullets: [
      "Your delivery list sets the stop order",
      "Loaded to match it, first stop at the doors",
      "Hands off to your navigation app",
    ],
    shot: "phone_route_map",
    alt: "The QUAI app showing the stops for the day and the route between them.",
    planned: "planned, not shipped",
  },
];

export function Features() {
  return (
    <section className="features" id="features">
      {PANELS.map((panel) => (
        <article className="panel" key={panel.eyebrow}>
          <div className="panel__text">
            <p className="eyebrow">{panel.eyebrow}</p>
            {/* Its own row, the same height in every card so the titles still line up. "planned"
                alone read as *planned route* on this card, which is the one claim design.md
                forbids — a label that can be read as the feature is not a label (#34). */}
            <p className="panel__badge">
              {panel.planned && <span className="tag">{panel.planned}</span>}
            </p>
            <h2>{panel.title}</h2>
            <ul className="panel__list">
              {panel.bullets.map((b) => (
                <li key={b}>
                  <IconTick />
                  <span>{b}</span>
                </li>
              ))}
            </ul>

          </div>
          <PhoneShot name={panel.shot} alt={panel.alt} />
        </article>
      ))}
    </section>
  );
}

/* 5 — the compact navy banner, between sections (landing_ref_1) --------------------------------

   The reference carries "Smarter loading for a smoother day." and "Voice. Optimisation. Delivery."
   Neither is used: design.md allows one tagline, and "optimisation" is the claim the copy rules
   forbid. The layout is the reference's; the words are ours. */

export function NavyBanner() {
  return (
    <section className="banner">
      <img className="banner__logo" src={logoOnNavy} alt="QUAI" width="970" height="314" />
      <p className="banner__line">People talk. We load.</p>
      <Picture
        className="banner__image"
        name="operator_bust"
        widths={[360, 720]}
        sizes="(max-width: 760px) 30vw, 14vw"
        alt="An operator checking a parcel on a phone."
      />
    </section>
  );
}

/* 5b — loading plan ready (landing_ref_3) ------------------------------------------------------- */

const EXAMPLE_VAN = [
  [<IconBox key="i" />, "124", "Parcels"],
  [<IconPin key="i" />, "28", "Stops"],
  [<IconClock key="i" />, "4h 20m", "Estimated route time"],
];

export function LoadingPlanReady() {
  return (
    <section className="plan">
      <div className="plan__text">
        <h2>Loading plan ready</h2>
        <p className="plan__body">
          Built from the rules you said and the stop order on your delivery list. Every parcel has a
          place before anyone picks one up.
        </p>
        <ul className="plan__tiles">
          {EXAMPLE_VAN.map(([icon, value, label]) => (
            <li key={label}>
              <span className="plan__icon" aria-hidden="true">{icon}</span>
              <span>
                <strong className="data">{value}</strong>
                <span>{label}</span>
              </span>
            </li>
          ))}
        </ul>
        {/* design.md: figures that are not measurements must say so. These are one example van. */}
        <p className="tag">Example van — not a measured result</p>
      </div>
      <PhoneShot name="phone_home" alt="The QUAI app home screen on a phone." />
    </section>
  );
}

/* 5c — route and delivery order (landing_ref_2) -------------------------------------------------- */

const STOP_GROUPS = [
  ["one", "At the doors", "comes off first"],
  ["two", "Middle", "the stops after it"],
  ["three", "At the back", "comes off last"],
];

export function RouteOrder() {
  return (
    <section className="route">
      <div className="route__text">
        <h2>Route &amp; delivery order</h2>
        <p className="route__body">
          QUAI groups and places your parcels so the right ones are near the right doors. The order is
          your delivery list&rsquo;s, not ours.
        </p>
        <ul className="route__legend">
          {STOP_GROUPS.map(([tone, where, when]) => (
            <li key={where}>
              <span className={`route__dot route__dot--${tone}`} aria-hidden="true" />
              <span>
                <strong>{where}</strong> — {when}
              </span>
            </li>
          ))}
        </ul>
      </div>
      <Picture
        className="route__van"
        name="van_topdown"
        widths={[640, 1024, 1600]}
        sizes="(max-width: 900px) 95vw, 55vw"
        alt="A van seen from above, its parcels grouped in three colours by delivery stop."
      />
    </section>
  );
}

/* 6 — the icon strip, as on the marketing board -------------------------------------------------- */

const STRIP = [
  [<IconMic key="i" />, "Voice instructions", "Say it, QUAI writes the rules"],
  [<IconCube key="i" />, "3D loading plans", "Every parcel has a place"],
  [<IconPin key="i" />, "Stop-order loading", "First stop behind the doors"],
  [<IconRule key="i" />, "Replan on incident", "A missing parcel is not a stuck plan"],
];

export function IconStrip() {
  return (
    <section className="strip">
      <Picture
        className="strip__boxes"
        name="boxes_quai"
        widths={[480, 960]}
        sizes="(max-width: 1100px) 0px, 12vw"
        alt=""
      />
      <ul>
        {STRIP.map(([icon, title, body]) => (
          <li key={title}>
            <span className="strip__icon" aria-hidden="true">
              {icon}
            </span>
            <span>
              <strong>{title}</strong>
              <span>{body}</span>
            </span>
          </li>
        ))}
      </ul>
      <Picture
        className="strip__operator"
        name="operator_thumbsup"
        widths={[400, 800]}
        sizes="(max-width: 1100px) 0px, 10vw"
        alt=""
      />
    </section>
  );
}

/* 7 — why the model never places a box ------------------------------------------------------------ */

const CHAIN = [
  [<IconSpeech key="i" />, "You say", "“Paint cans last, nothing on the glass.”"],
  [<IconBraces key="i" />, "Validated JSON", "Checked against the contract, or refused."],
  [<IconBox key="i" />, "3D plan", "Computed by the solver, the same way every time."],
];

export function WhyQuai() {
  return (
    <section className="why" id="why-quai">
      <h2>The model never places a box.</h2>
      <p className="why__lead">
        QUAI follows your delivery list: it never chooses or reorders your stops.
      </p>
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

/* 8 — a day on the dock ---------------------------------------------------------------------------- */

const TILES = [
  ["scan_parcel", [400, 640, 1024], "Scan the parcels",
    "An operator scanning a parcel with a phone."],
  ["van_interior_next", [480, 720], "Follow the plan",
    "The inside of a loaded van, the next parcel picked out in orange."],
  ["van_stops_colours", [400, 640, 1024], "Loaded in stop order",
    "The back of a loaded van, parcels grouped by colour for each stop."],
  ["customer", [400, 800], "The right parcel, first time",
    "A customer taking her parcel at the door.", "cutout"],
];

export function DayOnTheDock() {
  return (
    <section className="dock">
      <h2>A day on the dock</h2>
      <div className="dock__tiles">
        {TILES.map(([name, widths, caption, alt, kind]) => (
          <figure className={`dock__tile ${kind === "cutout" ? "dock__tile--cutout" : ""}`} key={name}>
            <Picture name={name} widths={widths} sizes="(max-width: 760px) 90vw, 23vw" alt={alt} />
            <figcaption>{caption}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

/* 9 — closing call to action and footer ------------------------------------------------------------- */

export function FinalCta() {
  return (
    <section className="cta">
      <h2>Next van, fewer surprises.</h2>
      <div className="cta__actions">
        <Link className="button button--lg" to="/app">
          Get started <span aria-hidden="true">→</span>
        </Link>
        <Link className="button button--lg button--quiet" to="/app">
          Log in
        </Link>
      </div>
    </section>
  );
}

/* 10 — a plain light footer: the navy is spent on the banner above, not here ---------------------- */

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
        <li>
          <Link to="/app">Log in</Link>
        </li>
      </ul>
    </footer>
  );
}
