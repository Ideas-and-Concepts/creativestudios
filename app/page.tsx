"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number };

const defaultModules: Module[] = [
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

const STORAGE_KEY = "creative-studios-page-config";
const THEME_KEY = "creative-studios-theme";

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [summary, setSummary] = useState<Summary>({ projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 });
  const [editingPages, setEditingPages] = useState(false);
  const [modules, setModules] = useState<Module[]>(defaultModules);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved) as Record<string, Partial<Module>>;
        setModules(defaultModules.map((item) => ({ ...item, ...(parsed[item.href] ?? {}) })));
      }
      const savedTheme = window.localStorage.getItem(THEME_KEY);
      if (savedTheme === "light" || savedTheme === "dark") setTheme(savedTheme);
    } catch {
      setModules(defaultModules);
    }

    const refresh = async () => {
      try {
        const health = await fetch("/api/health", { cache: "no-store" });
        const healthData = await health.json();
        setDatabaseReady(Boolean(healthData.database));
      } catch {
        setDatabaseReady(false);
      }
      try {
        const response = await fetch("/api/dashboard/summary", { cache: "no-store" });
        const data = await response.json();
        if (response.ok && data.data) setSummary(data.data);
      } catch {
        setSummary({ projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 });
      }
    };
    void refresh();
  }, []);

  const activeModule = useMemo(
    () => modules.find((item) => item.name === active) ?? modules[0],
    [active, modules],
  );

  const changeTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    window.localStorage.setItem(THEME_KEY, next);
  };

  const updatePage = (href: string, field: "name" | "description", value: string) => {
    setModules((current) => current.map((item) => item.href === href ? { ...item, [field]: value } : item));
  };

  const savePageConfig = () => {
    const config = Object.fromEntries(modules.map((item) => [item.href, { name: item.name, description: item.description }]));
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    setEditingPages(false);
  };

  const resetPageConfig = () => {
    window.localStorage.removeItem(STORAGE_KEY);
    setModules(defaultModules);
    setActive("Dashboard");
    setEditingPages(false);
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
        <div className="sidebar-links">
          <a className="streamlit-link primary" href="https://creativestudios-app.vercel.app/" target="_blank" rel="noreferrer">Open Production PWA</a>
          <a className="streamlit-link" href="https://creativestudios-ai.vercel.app/" target="_blank" rel="noreferrer">Creative Studios AI</a>
        </div>
        <div className="divider" />
        <div className="section-label">Workspace</div>
        <nav className="nav" aria-label="Workspace navigation">
          {modules.map((item) => (
            <Link key={item.href} href={item.href} className={item.name === active ? "nav-item active" : "nav-item"} onClick={() => setActive(item.name)}>
              {item.name}
            </Link>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <button className="theme-button" onClick={changeTheme}>{theme === "dark" ? "Light mode" : "Dark mode"}</button>
          <button className="edit-page-button" onClick={() => setEditingPages((value) => !value)}>{editingPages ? "Close page editor" : "Edit pages"}</button>
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <div className="eyebrow">Creative Studios</div>
            <h1>{activeModule.name}</h1>
            <p>{activeModule.description}</p>
          </div>
          <div className={databaseReady ? "status ready" : "status"}>{databaseReady ? "Database connected" : "Database pending"}</div>
        </header>

        {editingPages && (
          <section className="page-editor">
            <div className="page-editor-header">
              <div><div className="section-label">Page editor</div><h2>Edit workspace pages</h2><p>Change navigation labels and descriptions. These settings are stored in this browser.</p></div>
              <div className="editor-actions"><button className="secondary-button" onClick={resetPageConfig}>Reset</button><button className="primary-button" onClick={savePageConfig}>Save page settings</button></div>
            </div>
            <div className="page-editor-grid">
              {modules.map((item) => <div className="page-editor-row" key={item.href}><label>Page name<input value={item.name} onChange={(event) => updatePage(item.href, "name", event.target.value)} /></label><label>Description<input value={item.description} onChange={(event) => updatePage(item.href, "description", event.target.value)} /></label></div>)}
            </div>
          </section>
        )}

        <div className="hero-card">
          <div><div className="eyebrow">AEC project workspace</div><h2>One connected workspace for the project lifecycle.</h2><p>Projects, architecture, engineering, drawings, BOQ, procurement, construction and cost control in one Streamlit-style workspace.</p></div>
        </div>

        <div className="kpi-grid">
          <div className="kpi-card"><span>Projects</span><strong>{summary.projects}</strong></div>
          <div className="kpi-card"><span>Drawings</span><strong>{summary.drawings}</strong></div>
          <div className="kpi-card"><span>BOQ Items</span><strong>{summary.boqItems}</strong></div>
          <div className="kpi-card"><span>Active Works</span><strong>{summary.activeWorks}</strong></div>
        </div>

        <div className="workspace-card">
          <div><div className="section-label">Quick actions</div><h2>{activeModule.name}</h2><p>{activeModule.description}</p></div>
          <div className="workflow" aria-label="Project workflow">
            {modules.slice(1, 11).map((item) => <Link key={item.href} href={item.href}>{item.name}</Link>)}
          </div>
        </div>
      </section>
    </main>
  );
}
