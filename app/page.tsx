"use client";

import { useMemo, useState } from "react";

const modules = [
  { name: "Dashboard", description: "Project and workspace overview." },
  { name: "Projects", description: "Manage projects, phases and project status." },
  { name: "Documents", description: "Central project documentation and records." },
  { name: "Architecture", description: "Architectural design and construction information." },
  { name: "Engineering", description: "Structural, civil and technical engineering work." },
  { name: "Drawings", description: "Architectural and structural drawing registers." },
  { name: "BOQ", description: "Bill of Quantities and construction cost items." },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination." },
  { name: "Construction", description: "Construction activities and site information." },
];

const logoUrl = "https://raw.githubusercontent.com/Ideas-and-Concepts/creativestudios/main/assets/creative_studios.png";

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  const activeModule = useMemo(
    () => modules.find((item) => item.name === active) ?? modules[0],
    [active],
  );

  return (
    <main className={theme === "light" ? "app light" : "app"}>
      <aside className="sidebar">
        <div className="brand">
          <img src={logoUrl} alt="Creative Studios" className="logo" />
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
              onClick={() => setActive(item.name)}
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
          <div className="status">Workspace ready</div>
        </header>

        <div className="hero-card">
          <h2>Creative Studios Workspace</h2>
          <p>
            Manage projects, documents, drawings, BOQ and construction information
            from one connected AEC workspace.
          </p>
        </div>

        <div className="kpi-grid">
          <div className="kpi-card"><span>Projects</span><strong>0</strong></div>
          <div className="kpi-card"><span>Drawings</span><strong>0</strong></div>
          <div className="kpi-card"><span>BOQ Items</span><strong>0</strong></div>
          <div className="kpi-card"><span>Active Works</span><strong>0</strong></div>
        </div>

        <div className="workspace-card">
          <div>
            <h2>{activeModule.name} workspace</h2>
            <p>
              The new PWA foundation is in place. Data services will be connected
              to PostgreSQL in the next migration stage.
            </p>
          </div>
          <div className="workflow">
            <span>Projects</span><span>Architecture</span><span>Engineering</span>
            <span>Drawings</span><span>BOQ</span><span>Construction</span>
          </div>
        </div>
      </section>
    </main>
  );
}
