"use client";

import { useEffect, useMemo, useState } from "react";

const modules = [
  { name: "Dashboard", description: "Project and workspace overview.", href: "/" },
  { name: "Projects", description: "Manage projects, phases and project status.", href: "/projects" },
  { name: "Documents", description: "Central project documentation and records.", href: "/documents" },
  { name: "Architecture", description: "Architectural works and construction information.", href: "/architecture" },
  { name: "Engineering", description: "Structural, civil and technical engineering works.", href: "/engineering" },
  { name: "Drawings", description: "Architectural and structural drawing registers.", href: "/drawings" },
  { name: "BOQ", description: "Bill of Quantities and construction cost items.", href: "/boq" },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination.", href: "/mep" },
  { name: "Procurement", description: "Materials, suppliers and purchasing workflow.", href: "/procurement" },
  { name: "Construction", description: "Construction activities, progress and site records.", href: "/construction" },
  { name: "Cost Control", description: "Project budgets, commitments and actual costs.", href: "/cost-control" },
  { name: "Tasks", description: "Assignments, deadlines and project actions.", href: "/tasks" },
  { name: "RFIs", description: "Requests for information and responses.", href: "/rfis" },
  { name: "Approvals", description: "Controlled review and approval workflow.", href: "/approvals" },
  { name: "Reports", description: "Project, progress and commercial reporting.", href: "/reports" },
  { name: "Settings", description: "Workspace configuration and administration.", href: "/settings" },
];

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [projectCount, setProjectCount] = useState(0);

  useEffect(() => {
    void fetch("/api/health").then((response) => response.json()).then((data) => setDatabaseReady(Boolean(data.database))).catch(() => setDatabaseReady(false));
    void fetch("/api/projects").then((response) => response.ok ? response.json() : null).then((data) => setProjectCount(Array.isArray(data?.data) ? data.data.length : 0)).catch(() => setProjectCount(0));
  }, []);

  const activeModule = useMemo(() => modules.find((item) => item.name === active) ?? modules[0], [active]);
  const selectModule = (item: (typeof modules)[number]) => {
    setActive(item.name);
    if (item.href !== "/") window.location.href = item.href;
  };

  return (
    <main className={theme === "light" ? "app light" : "app"}>
      <aside className="sidebar">
        <div className="brand"><img src="/assets/creative_studios.png" alt="Creative Studios" className="logo" /><div className="brand-title">Creative Studios</div><div className="brand-subtitle">AEC Collaboration Platform</div></div>
        <div className="divider" /><div className="section-label">Workspace</div>
        <nav className="nav" aria-label="Workspace navigation">
          {modules.map((item) => <button key={item.name} className={item.name === active ? "nav-item active" : "nav-item"} onClick={() => selectModule(item)}>{item.name}</button>)}
        </nav>
        <div className="sidebar-bottom"><button className="theme-button" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} aria-label="Toggle theme">{theme === "dark" ? "Light mode" : "Dark mode"}</button></div>
      </aside>
      <section className="content">
        <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>{activeModule.name}</h1><p>{activeModule.description}</p></div><div className={databaseReady ? "status ready" : "status"}>{databaseReady ? "Database connected" : "Database pending"}</div></header>
        <div className="hero-card"><div><div className="eyebrow">AEC project workspace</div><h2>One connected workspace for the project lifecycle.</h2><p>Connect projects, architecture, engineering, drawings, BOQ, procurement, construction and cost control through a single progressive web application.</p></div></div>
        <div className="kpi-grid"><div className="kpi-card"><span>Projects</span><strong>{projectCount}</strong></div><div className="kpi-card"><span>Drawings</span><strong>0</strong></div><div className="kpi-card"><span>BOQ Items</span><strong>0</strong></div><div className="kpi-card"><span>Active Works</span><strong>0</strong></div></div>
        <div className="workspace-card"><div><div className="section-label">Current workspace</div><h2>{activeModule.name}</h2><p>Module navigation is live. Engineering is now connected to the shared project data model; the remaining modules will follow the same relational workflow.</p></div><div className="workflow" aria-label="Project workflow">{modules.slice(1, 11).map((item) => <a key={item.name} href={item.href}>{item.name}</a>)}</div></div>
      </section>
    </main>
  );
}
