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
