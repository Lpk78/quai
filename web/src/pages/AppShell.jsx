import { Outlet } from "react-router-dom";

import { OperatorBadge, SiteFooter, SiteHeader } from "../components.jsx";
import { OPERATOR_NAME } from "../data/manifest.js";
import "../app.css";

export default function AppShell() {
  return (
    <div className="page">
      {/* The badge sits in the shell rather than on Home alone: who is driving is true on every
          screen inside the app, and the mockup's header is the same lockup throughout. */}
      <SiteHeader logoTo="/app" action={<OperatorBadge name={OPERATOR_NAME} />} />
      <main className="shell-main">
        <div className="wrap wrap--app">
          <Outlet />
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
