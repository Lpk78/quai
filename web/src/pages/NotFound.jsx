import { Link } from "react-router-dom";

import { SiteFooter, SiteHeader } from "../components.jsx";

export default function NotFound() {
  return (
    <div className="page">
      <SiteHeader />
      <main className="shell-main">
        <div className="wrap">
          <h1>Nothing at this address</h1>
          <p className="muted note">
            The page you asked for does not exist. The application is at <code>/app</code>.
          </p>
          <div className="actions" style={{ marginTop: "1.5rem" }}>
            <Link className="button" to="/app">
              Open the app <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
