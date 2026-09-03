"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string; group: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number };
type WorkspaceState = { pageConfig?: Record<string, Partial<Module>>; theme?: "dark" | "light"; settings?: Record<string, unknown> };

const PRODUCTION_PWA_URL = "https://creativestudios-app.vercel.app/";
const CREATIVE_STUDIOS_AI_URL = "https://creativestudios-ai.vercel.app/";
const STREAMLIT_CLOUD_URL = "https://creativestudios.streamlit.app/";

const defaultModules: Module[] = [
  { name: "Dashboard", description: "Project and workspace overview.", href: "/", group: "Workspace" },
  { name: "Projects", description: "Manage projects, phases and project status.", href: "/projects", group: "Architecture" },
  { name: "Documents", description: "Central project documentation and records.", href: "/documents", group: "Architecture" },
  { name: "Architecture", description: "Architectural works, design records and progress.", href: "/architecture", group: "Architecture" },
  { name: "Drawings", description: "Architectural and structural drawing registers.", href: "/drawings", group: "Architecture" },
  { name: "Engineering", description: "Structural, civil and technical engineering works.", href: "/engineering", group: "Engineering" },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination.", href: "/mep", group: "Engineering" },
  { name: "BOQ", description: "Bill of Quantities and construction cost items.", href: "/boq", group: "Engineering" },
  { name: "RFIs", description: "Requests for information and responses.", href: "/rfis", group: "Engineering" },
  { name: "Approvals", description: "Controlled review and approval workflow.", href: "/approvals", group: "Engineering" },
  { name: "Procurement", description: "Materials, suppliers and purchasing workflow.", href: "/procurement", group: "Construction" },
  { name: "Construction", description: "Construction activities, progress and site records.", href: "/construction", group: "Construction" },
  { name: "Cost Control", description: "Project budgets, commitments and actual costs.", href: "/cost-control", group: "Construction" },
  { name: "Tasks", description: "Assignments, deadlines and project actions.", href: "/tasks", group: "Construction" },
  { name: "Reports", description: "Project, progress and commercial reporting.", href: "/reports", group: "Construction" },
  { name: "Settings", description: "Workspace configuration and administration.", href: "/settings", group: "Workspace" },
];

const groups = ["Architecture", "Engineering", "Construction", "Workspace"];

export default function Home() {
  const [active, setActive] = useState("Dashboard");
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [summary, setSummary] = useState<Summary>({ projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 });
  const [editingPages, setEditingPages] = useState(false);
  const [modules, setModules] = useState<Module[]>(defaultModules);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const refresh = async () => {
      try {
        const stateResponse = await fetch("/api/workspace-state", { cache: "no-store" });
        if (stateResponse.ok) {
          const state = (await stateResponse.json()).data as WorkspaceState;
          const config = state?.pageConfig ?? {};
          setModules(defaultModules.map((item) => ({ ...item, ...(config[item.href] ?? {}) })));
          if (state?.theme === "light" || state?.theme === "dark") setTheme(state.theme);
        }
      } catch {
        // Keep safe local defaults when the database is temporarily unavailable.
      }

      try {
        const health = await fetch("/api/health", { cache: "no-store" });
        const data = await health.json();
        setDatabaseReady(Boolean(data.ok && data.database));
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

  const activeModule = useMemo(() => modules.find((item) => item.name === active) ?? modules[0], [active, modules]);
  const grouped = useMemo(() => groups.map((group) => ({ group, items: modules.filter((item) => item.group === group) })), [modules]);

  const changeTheme = async () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    try { await fetch("/api/workspace-state", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ theme: next }) }); } catch { /* UI remains responsive if save is unavailable. */ }
  };

  const updatePage = (href: string, field: "name" | "description", value: string) => {
    setModules((current) => current.map((item) => item.href === href ? { ...item, [field]: value } : item));
  };

  const savePageConfig = async () => {
    setSaving(true); setSaveMessage("");
    try {
      const pageConfig = Object.fromEntries(modules.map((item) => [item.href, { name: item.name, description: item.description }]));
      const response = await fetch("/api/workspace-state", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pageConfig }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to save page settings.");
      setSaveMessage("Saved to shared workspace.");
      setEditingPages(false);
    } catch (error) {
      setSaveMessage(error instanceof Error ? error.message : "Unable to save page settings.");
    } finally { setSaving(false); }
  };

  const resetPageConfig = async () => {
    setModules(defaultModules);
    setSaveMessage("");
    try {
      const pageConfig = Object.fromEntries(defaultModules.map((item) => [item.href, { name: item.name, description: item.description }]));
      await fetch("/api/workspace-state", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ pageConfig }) });
    } catch { setSaveMessage("Reset locally. Shared reset could not be saved."); }
  };

  const navigate = (name: string) => { setActive(name); setMobileOpen(false); };

  return <main className={theme === "light" ? "app light" : "app"}>
    <button className="mobile-menu" onClick={() => setMobileOpen((value) => !value)} aria-label="Toggle navigation">Menu</button>
    <aside className={mobileOpen ? "sidebar mobile-open" : "sidebar"}>
      <div className="brand"><img src="/assets/creative_studios.png" alt="Creative Studios" className="logo" /><div className="brand-title">Creative Studios</div><div className="brand-subtitle">AEC Collaboration Platform</div></div>
      <div className="divider" />
      <div className="sidebar-links">
        <a className="streamlit-link primary" href={PRODUCTION_PWA_URL} target="_blank" rel="noreferrer">Open Production PWA</a>
        <a className="streamlit-link" href={CREATIVE_STUDIOS_AI_URL} target="_blank" rel="noreferrer">Open Creative Studios AI</a>
        <a className="streamlit-link" href={STREAMLIT_CLOUD_URL} target="_blank" rel="noreferrer">Open Streamlit Cloud</a>
      </div>
      <div className="divider" />
      <nav className="nav" aria-label="Workspace navigation">
        <div><div className="section-label">Workspace</div>{modules.filter((item) => item.group === "Workspace").map((item) => <Link key={item.href} href={item.href} className={item.name === active ? "nav-item active" : "nav-item"} onClick={() => navigate(item.name)}>{item.name}</Link>)}</div>
        {grouped.filter(({ group }) => group !== "Workspace").map(({ group, items }) => <div key={group}><div className="section-label">{group}</div>{items.map((item) => <Link key={item.href} href={item.href} className={item.name === active ? "nav-item active" : "nav-item"} onClick={() => navigate(item.name)}>{item.name}</Link>)}</div>)}
      </nav>
      <div className="sidebar-bottom"><button className="theme-button" onClick={() => void changeTheme()}>{theme === "dark" ? "Light mode" : "Dark mode"}</button><button className="edit-page-button" onClick={() => setEditingPages((value) => !value)}>{editingPages ? "Close page editor" : "Edit pages"}</button></div>
    </aside>

    <section className="content">
      <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>{activeModule.name}</h1><p>{activeModule.description}</p></div><div className={databaseReady ? "status ready" : "status"}>{databaseReady ? "Database connected" : "Database pending"}</div></header>

      {editingPages && <section className="page-editor"><div className="page-editor-header"><div><div className="section-label">Shared page editor</div><h2>Edit workspace pages</h2><p>Changes are stored in the shared Neon workspace state and apply to the PWA dashboard.</p></div><div className="editor-actions"><button className="secondary-button" onClick={() => void resetPageConfig()}>Reset</button><button className="primary-button" disabled={saving} onClick={() => void savePageConfig()}>{saving ? "Saving..." : "Save page settings"}</button></div></div><div className="page-editor-grid">{modules.map((item) => <div className="page-editor-row" key={item.href}><label>Page name<input value={item.name} onChange={(event) => updatePage(item.href, "name", event.target.value)} /></label><label>Description<input value={item.description} onChange={(event) => updatePage(item.href, "description", event.target.value)} /></label></div>)}</div>{saveMessage && <p className="form-message">{saveMessage}</p>}</section>}

      <section className="hero-card"><div><div className="eyebrow">AEC project workspace</div><h2>One connected workspace for the project lifecycle.</h2><p>Projects, design, drawings, BOQ, procurement, construction and cost control in a compact Streamlit-style interface.</p><div className="workflow"><Link href="/projects">Open Projects</Link><Link href="/drawings">Open Drawings</Link><Link href="/boq">Open BOQ</Link><Link href="/construction">Open Construction</Link></div></div></section>
      <div className="kpi-grid"><Link href="/projects" className="kpi-card"><span>Projects</span><strong>{summary.projects}</strong></Link><Link href="/drawings" className="kpi-card"><span>Drawings</span><strong>{summary.drawings}</strong></Link><Link href="/boq" className="kpi-card"><span>BOQ Items</span><strong>{summary.boqItems}</strong></Link><Link href="/construction" className="kpi-card"><span>Active Works</span><strong>{summary.activeWorks}</strong></Link></div>
      <div className="workspace-card"><div><div className="section-label">Quick actions</div><h2>{activeModule.name}</h2><p>{activeModule.description}</p></div><div className="workflow">{modules.filter((item) => item.name !== "Dashboard").map((item) => <Link key={item.href} href={item.href}>{item.name}</Link>)}</div></div>
    </section>
  </main>;
}
