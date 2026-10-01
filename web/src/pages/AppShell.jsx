import { SiteFooter, SiteHeader } from "../components.jsx";

/* Deliberately empty: issue #18 says the 3D view (#7) and the box form (#8) fill it.
   The placeholders name what is coming rather than pretending it is here. */

const PANELS = [
  {
    issue: "#8",
    title: "Boxes and container",
    body: "The list of what has to go in, and the vehicle it has to go into.",
  },
  {
    issue: "#7",
    title: "3D view of the plan",
    body: "Where the solver put each box, and which ones did not fit.",
  },
];

export default function AppShell() {
  return (
    <div className="page">
      <SiteHeader />

      <main className="shell-main">
        <div className="wrap">
          <h1>Plan a load</h1>
          <p className="muted note">
            Nothing to show yet — this is the shell the rest of the application is built into.
          </p>

          <div className="grid" style={{ marginTop: "1.5rem" }}>
            {PANELS.map((panel) => (
              <section className="card placeholder" key={panel.issue}>
                <span className="badge">{panel.issue}</span>
                <h2>{panel.title}</h2>
                <p className="muted">{panel.body}</p>
              </section>
            ))}
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}
