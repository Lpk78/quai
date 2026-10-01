import { Outlet } from "react-router-dom";

import { SiteFooter, SiteHeader } from "../components.jsx";
import "../app.css";

export default function AppShell() {
  return (
    <div className="page">
      <SiteHeader logoTo="/app" />
      <main className="shell-main">
        <div className="wrap wrap--app">
          <Outlet />
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
