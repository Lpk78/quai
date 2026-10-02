import { Link } from "react-router-dom";

import logoLight from "../../assets/brand/logo/quai-logo-light.svg";

/** The lockup, from assets/brand/logo/. Never retyped, never recoloured — see design.md, Logo. */
export function Logo({ to = "/" }) {
  return (
    <Link to={to} aria-label="QUAI, home">
      <img className="logo" src={logoLight} alt="QUAI" width="790" height="300" />
    </Link>
  );
}

/** Who is signed in, as the mockup's round avatar in the top right.
 *
 * Deliberately not a button or a link: there is no profile screen to open, and a control that does
 * nothing is the interface version of a claim we cannot back. It carries the operator's initial
 * rather than a generic person glyph so that it says something true — which operator — instead of
 * being decoration in the shape of a feature. */
export function OperatorBadge({ name }) {
  if (!name) return null;
  return (
    <span className="operator-badge" title={`Signed in as ${name}`}>
      <span aria-hidden="true">{[...name][0]}</span>
      <span className="visually-hidden">Signed in as {name}</span>
    </span>
  );
}

export function SiteHeader({ action = null, logoTo = "/" }) {
  return (
    <header className="site-header">
      <div className="wrap">
        <Logo to={logoTo} />
        {action}
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="wrap muted">
        <p>QUAI — People talk. We load.</p>
      </div>
    </footer>
  );
}
