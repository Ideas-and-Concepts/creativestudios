"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string; group: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number };

const defaultModules: Module[] = [
  { name: "Dashboard", description: "Project and workspace overview.", href: "/", group: "Workspace" },
  { name: "Projects", description: "Manage projects, phases and project status.", href: "/projects", group: "Workspace" },
  { name: "Documents", description: "Central project documentation and records.", href: "/documents", group: "Workspace" },
  { name: "Architecture", description: "Architectural works and construction information.", href: "/architecture", group: "Design" },
  { name: "Engineering", description: "Structural, civil and technical engineering works.", href: "/engineering", group: "Design" },
  { name: "Drawings", description: "Architectural and structural drawing registers.", href: "/drawings", group: "Design" },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination.", href: "/mep", group: "Design" },
  { name: "BOQ", description: "Bill of Quantities and construction cost items.", href: "/boq", group: "Commercial" },
  { name: "Procurement", description: "Materials, suppliers and purchasing workflow.", href: "/procurement", group: "Commercial" },
  { name: "Cost Control", description: "Project budgets, commitments and actual costs.", href: "/cost-control", group: "Commercial" },
  { name: "Construction", description: "Construction activities, progress and site records.", href: "/construction", group: "Delivery" },
  { name: "Tasks", description: "Assignments, deadlines and project actions.", href: "/tasks", group: "Delivery" },
  { name: "RFIs", description: "Requests for information and responses.", href: "/rfis", group: "Delivery" },
  { name: "Approvals", description: "Controlled review and approval workflow.", href: "/approvals", group: "Delivery" },
  { name: "Reports", description: "Project, progress and commercial reporting.", href: "/reports", group: "Administration" },
  { name: "Settings", description: "Workspace configuration and administration.", href: "/settings", group: "Administration" },
];

const STORAGE_KEY = "creative-studios-page-config";
const THEME_KEY = "creative-studios-theme";
const groups = ["Workspace", "Design", "Commercial", "Delivery", "Administration"];

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
    } catch { setModules(defaultModules); }

    const refresh = async () => {
      try {
        const health = await fetch("/api/health", { cache: "no-store" });
        const healthData = await health.json();
        setDatabaseReady(Boolean(healthData.ok && healthData.database));
      } catch { setDatabaseReady(false); }
      try {
        const response = await fetch("/api/dashboard/summary", { cache: "no-store" });
        const data = await response.json();
        if (response.ok && data.data) setSummary(data.data);
      } catch { setSummary({ projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 }); }
    };
    void refresh();
  }, []);

  const activeModule = useMemo(() => modules.find((item) => item.name === active) ?? modules[0], [active, modules]);
  const grouped = useMemo(() => groups.map((group) => ({ group, items: modules.filter((item) => item.group === group) })), [modules]);

  const changeTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    window.localStorage.setItem(THEME_KEY, next);
  };

  const updatePage = (href: string, field: "name" | "description", value: string) => setModules((current) => current.map((item) => item.href === href ? { ...item, [field]: value } : item));
  const savePageConfig = () => {
    const config = Object.fromEntries(modules.map((item) => [item.href, { name: item.name, description: item.description }]));
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
    setEditingPages(false);
  };
  const resetPageConfig = () => { window.localStorage.removeItem(STORAGE_KEY); setModules(defaultModules); setActive("Dashboard"); setEditingPages(false); };

  return <main className={theme === "light" ? "app light" : "app"}>
    <aside className="sidebar">
      <div className="brand"><img src="/assets/creative_studios.png" alt="Creative Studios" className="logo" /><div className="brand-title">Creative Studios</div><div className="brand-subtitle">AEC Collaboration Platform</div></div>
      <div className="divider" />
      <div className="sidebar-links"><a className="streamlit-link primary" href="https://creativestudios-app.vercel.app/" target="_blank" rel="noreferrer">Open Production PWA</a><a className="streamlit-link" href="https://creativestudios-ai.vercel.app/" target="_blank" rel="noreferrer">Creative Studios AI</a></div>
      <div className="divider" />
      <nav className="nav" aria-label="Workspace navigation">
        {grouped.map(({ group, items }) => <div key={group}><div className="section-label">{group}</div>{items.map((item) => <Link key={item.href} href={item.href} className={item.name === active ? "nav-item active" : "nav-item"} onClick={() => setActive(item.name)}>{item.name}</Link>)}</div>)}
      </nav>
      <div className="sidebar-bottom"><button className="theme-button" onClick={changeTheme}>{theme === "dark" ? "Light mode" : "Dark mode"}</button><button className="edit-page-button" onClick={() => setEditingPages((value) => !value)}>{editingPages ? "Close page editor" : "Edit pages"}</button></div>
    </aside>

    <section className="content">
      <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>{activeModule.name}</h1><p>{activeModule.description}</p></div><div className={databaseReady ? "status ready" : "status"}>{databaseReady ? "Database connected" : "Database pending"}</div></header>

      {editingPages && <section className="page-editor"><div className="page-editor-header"><div><div className="section-label">Page editor</div><h2>Edit workspace pages</h2><p>Change navigation labels and descriptions for this browser.</p></div><div className="editor-actions"><button className="secondary-button" onClick={resetPageConfig}>Reset</button><button className="primary-button" onClick={savePageConfig}>Save page settings</button></div></div><div className="page-editor-grid">{modules.map((item) => <div className="page-editor-row" key={item.href}><label>Page name<input value={item.name} onChange={(event) => updatePage(item.href, "name", event.target.value)} /></label><label>Description<input value={item.description} onChange={(event) => updatePage(item.href, "description", event.target.value)} /></label></div>)}</div></section>}

      <div className="hero-card"><div><div className="eyebrow">AEC project workspace</div><h2>One connected workspace for the project lifecycle.</h2><p>Projects, design, drawings, BOQ, procurement, construction and cost control in a compact Streamlit-style interface.</p><div className="workflow"><Link href="/projects">Open Projects</Link><Link href="/drawings">Open Drawings</Link><Link href="/boq">Open BOQ</Link><Link href="/construction">Open Construction</Link></div></div></div>
      <div className="kpi-grid"><Link href="/projects" className="kpi-card"><span>Projects</span><strong>{summary.projects}</strong></Link><Link href="/drawings" className="kpi-card"><span>Drawings</span><strong>{summary.drawings}</strong></Link><Link href="/boq" className="kpi-card"><span>BOQ Items</span><strong>{summary.boqItems}</strong></Link><Link href="/construction" className="kpi-card"><span>Active Works</span><strong>{summary.activeWorks}</strong></Link></div>
      <div className="workspace-card"><div><div className="section-label">Quick actions</div><h2>{activeModule.name}</h2><p>{activeModule.description}</p></div><div className="workflow">{modules.filter((item) => item.name !== "Dashboard").slice(0, 12).map((item) => <Link key={item.href} href={item.href}>{item.name}</Link>)}</div></div>
    </section>
  </main>;
}
