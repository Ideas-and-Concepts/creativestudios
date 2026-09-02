"use client";

import { useEffect, useMemo, useState } from "react";

const modules = [
  { name: "Dashboard", description: "Project and workspace overview." },
  { name: "Projects", description: "Manage projects, phases and project status." },
  { name: "Documents", description: "Central project documentation and records." },
  { name: "Architecture", description: "Architectural works and construction information." },
  { name: "Engineering", description: "Structural, civil and technical engineering works." },
  { name: "Drawings", description: "Architectural and structural drawing registers." },
  { name: "BOQ", description: "Bill of Quantities and construction cost items." },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination." },
  { name: "Procurement", description: "Materials, suppliers and purchasing workflow." },
  { name: "Construction", description: "Construction activities, progress and site records." },
  { name: "Cost Control", description: "Project budgets, commitments and actual costs." },
  { name: "Tasks", description: "Assignments, deadlines and project actions." },
  { name: "RFIs", description: "Requests for information and responses." },
  { name: "Approvals", description: "Controlled review and approval workflow." },
  { name: "Reports", description: "Project, progress and commercial reporting." },
  { name: "Settings", description: "Workspace configuration and administration." },
];

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [projectCount, setProjectCount] = useState(0);

  useEffect(() => {
    void fetch("/api/health")
      .then((response) => response.json())
      .then((data) => setDatabaseReady(Boolean(data.database)))
      .catch(() => setDatabaseReady(false));

    void fetch("/api/projects")
      .then((response) => response.ok ? response.json() : null)
      .then((data) => setProjectCount(Array.isArray(data?.data) ? data.data.length : 0))
      .catch(() => setProjectCount(0));
  }, []);

  const activeModule = useMemo(
    () => modules.find((item) => item.name === active) ?? modules[0],
    [active],
  );

  const selectModule = (name: string) => {
    setActive(name);
    if (name === "Projects") window.location.href = "/projects";
  };

  return (
    <main className={theme === "light" ? "app light" : "app"}>
      <aside className="sidebar">
        <div className="brand">
          <img src="/assets/creative_studios.png" alt="Creative Studios" className="logo" />
          <div className="brand-title">Creative Studios</div>
          <div className="brand-subtitle">AEC Collaboration Platform</div>
        </div>

        <div className="divider" />
        <div className="section-label">Workspace</div>

        <nav className="nav" aria-label="Workspace navigation">
          {modules.map((item) => (
            <button
              key={item.name}
              className={item.name === active ? "nav-item active" : "nav-item"}
              onClick={() => selectModule(item.name)}
            >
              {item.name}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button
            className="theme-button"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            aria-label="Toggle theme"
          >
            {theme === "dark" ? "Light mode" : "Dark mode"}
          </button>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <div className="eyebrow">Creative Studios</div>
            <h1>{activeModule.name}</h1>
            <p>{activeModule.description}</p>
          </div>
          <div className={databaseReady ? "status ready" : "status"}>
            {databaseReady ? "Database connected" : "Database pending"}
          </div>
        </header>

        <div className="hero-card">
          <div>
            <div className="eyebrow">AEC project workspace</div>
            <h2>One connected workspace for the project lifecycle.</h2>
            <p>
              Connect projects, architecture, engineering, drawings, BOQ, procurement,
              construction and cost control through a single progressive web application.
            </p>
          </div>
        </div>

        <div className="kpi-grid">
          <div className="kpi-card"><span>Projects</span><strong>{projectCount}</strong></div>
          <div className="kpi-card"><span>Drawings</span><strong>0</strong></div>
          <div className="kpi-card"><span>BOQ Items</span><strong>0</strong></div>
          <div className="kpi-card"><span>Active Works</span><strong>0</strong></div>
        </div>

        <div className="workspace-card">
          <div>
            <div className="section-label">Current workspace</div>
            <h2>{activeModule.name}</h2>
            <p>
              Module navigation is live. The next implementation stage connects each
              module to the shared PostgreSQL data model and project relationships.
            </p>
          </div>
          <div className="workflow" aria-label="Project workflow">
            {modules.slice(1, 11).map((item) => <span key={item.name}>{item.name}</span>)}
          </div>
        </div>
      </section>
    </main>
  );
}
