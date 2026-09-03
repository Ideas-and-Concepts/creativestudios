"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string; group: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number };
type WorkspaceState = { pageConfig?: Record<string, Partial<Module>>; theme?: "dark" | "light" };

const PRODUCTION_PWA_URL = "https://creativestudios-app.vercel.app/";
const CREATIVE_STUDIOS_AI_URL = "https://creativestudios-ai.vercel.app/";
const STREAMLIT_CLOUD_URL = "https://creativestudios.streamlit.app/";

const defaultModules: Module[] = [
  { name: "Dashboard", description: "Project and workspace overview.", href: "/", group: "Workspace" },
  { name: "Projects", description: "Manage projects, phases and project status.", href: "/projects", group: "Architecture" },
  { name: "Documents", description: "Central project documentation and controlled records.", href: "/documents", group: "Architecture" },
  { name: "Architecture", description: "Architectural works, design records and progress.", href: "/architecture", group: "Architecture" },
  { name: "Drawings", description: "Architectural and structural drawing registers.", href: "/drawings", group: "Architecture" },
  { name: "Engineering", description: "Structural, civil and technical engineering works.", href: "/engineering", group: "Engineering" },
  { name: "MEP", description: "Mechanical, electrical and plumbing coordination.", href: "/mep", group: "Engineering" },
  { name: "BOQ", description: "Bill of Quantities and construction cost items.", href: "/boq", group: "Engineering" },
  { name: "RFIs", description: "Requests for information, responses and status control.", href: "/rfis", group: "Engineering" },
  { name: "Approvals", description: "Controlled review and approval workflow.", href: "/approvals", group: "Engineering" },
  { name: "Procurement", description: "Materials, suppliers and purchasing workflow.", href: "/procurement", group: "Construction" },
  { name: "Construction", description: "Construction activities, progress and site records.", href: "/construction", group: "Construction" },
  { name: "Cost Control", description: "Project budgets, commitments and actual costs.", href: "/cost-control", group: "Construction" },
  { name: "Tasks", description: "Assignments, priorities, deadlines and project actions.", href: "/tasks", group: "Construction" },
  { name: "Reports", description: "Live project and commercial reporting.", href: "/reports", group: "Construction" },
  { name: "Settings", description: "Workspace preferences and platform configuration.", href: "/settings", group: "Workspace" },
];

const groups = ["Architecture", "Engineering", "Construction", "Workspace"];
const emptySummary: Summary = { projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 };

export default function Home() {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [editingPages, setEditingPages] = useState(false);
  const [modules, setModules] = useState<Module[]>(defaultModules);
  const [saving, setSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    const readJson = async (response: Response): Promise<Record<string, any>> => {
      const text = await response.text();
      if (!text) return {};
      try { return JSON.parse(text); } catch { return {}; }
    };

    const refresh = async () => {
      try {
        const response = await fetch("/api/workspace-state", { cache: "no-store" });
        const result = await readJson(response) as { data?: WorkspaceState };
        if (!cancelled && response.ok) {
          const workspace = result.data ?? {};
          const config = workspace.pageConfig ?? {};
          setModules(defaultModules.map((item) => ({ ...item, ...(config[item.href] ?? {}) })));
          if (workspace.theme === "light" || workspace.theme === "dark") setTheme(workspace.theme);
        }
      } catch { /* Keep safe local defaults. */ }

      try {
        const response = await fetch("/api/health", { cache: "no-store" });
        const data = await readJson(response) as { ok?: boolean; database?: boolean };
        if (!cancelled) setDatabaseReady(Boolean(response.ok && data.ok && data.database));
      } catch {
        if (!cancelled) setDatabaseReady(false);
      }

      try {
        const response = await fetch("/api/dashboard/summary", { cache: "no-store" });
        const data = await readJson(response) as { data?: Summary };
        if (!cancelled && response.ok && data.data) setSummary({ ...emptySummary, ...data.data });
      } catch {
        if (!cancelled) setSummary(emptySummary);
      }
    };

    void refresh();
    return () => { cancelled = true; };
  }, []);

  const grouped = useMemo(
    () => groups.map((group) => ({ group, items: modules.filter((item) => item.group === group) })),
    [modules],
  );

  const changeTheme = async () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    try {
      await fetch("/api/workspace-state", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ theme: next }),
      });
    } catch { /* Keep local state responsive. */ }
  };

  const updatePage = (href: string, field: "name" | "description", value: string) => {
    setModules((current) => current.map((item) => item.href === href ? { ...item, [field]: value } : item));
  };

  const savePageConfig = async () => {
    setSaving(true);
    setSaveMessage("");
    try {
      const pageConfig = Object.fromEntries(
        modules.map((item) => [item.href, { name: item.name.trim() || item.name, description: item.description.trim() }]),
      );
      const response = await fetch("/api/workspace-state", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pageConfig }),
      });
      const text = await response.text();
      const data = text ? JSON.parse(text) : {};
      if (!response.ok) throw new Error(data.error || "Unable to save page settings.");
      setSaveMessage("Saved to the shared workspace.");
      setEditingPages(false);
    } catch (error) {
      setSaveMessage(error instanceof Error ? error.message : "Unable to save page settings.");
    } finally {
      setSaving(false);
    }
  };

  const resetPageConfig = async () => {
    setModules(defaultModules);
    setSaveMessage("");
    try {
      const pageConfig = Object.fromEntries(defaultModules.map((item) => [item.href, { name: item.name, description: item.description }]));
      const response = await fetch("/api/workspace-state", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pageConfig }),
      });
      if (!response.ok) throw new Error("Shared reset could not be saved.");
      setSaveMessage("Page arrangement reset.");
    } catch (error) {
      setSaveMessage(error instanceof Error ? error.message : "Shared reset could not be saved.");
    }
  };

  return (
    <main className={theme === "dark" ? "app" : "app light"}>
      <section className="content dashboard-content">
        <header className="topbar">
          <div>
            <div className="eyebrow">Creative Studios</div>
            <h1>Project Dashboard</h1>
            <p>A simple, connected workspace for Architecture, Engineering and Construction.</p>
          </div>
          <div className={databaseReady ? "status ready" : "status"}>
            {databaseReady ? "Database connected" : "Database unavailable"}
          </div>
        </header>

        <section className="hero-card">
          <div>
            <div className="eyebrow">AEC Collaboration Platform</div>
            <h2>One workspace for the project lifecycle.</h2>
            <p>Move from design and documentation through engineering, procurement and construction without leaving the workspace.</p>
          </div>
          <div className="workflow">
            <Link href="/projects">Open Projects</Link>
            <Link href="/architecture">Architecture</Link>
            <Link href="/engineering">Engineering</Link>
            <Link href="/construction">Construction</Link>
          </div>
        </section>

        <div className="kpi-grid">
          <Link href="/projects" className="kpi-card"><span>Projects</span><strong>{summary.projects}</strong></Link>
          <Link href="/drawings" className="kpi-card"><span>Drawings</span><strong>{summary.drawings}</strong></Link>
          <Link href="/boq" className="kpi-card"><span>BOQ Items</span><strong>{summary.boqItems}</strong></Link>
          <Link href="/construction" className="kpi-card"><span>Active Works</span><strong>{summary.activeWorks}</strong></Link>
        </div>

        <section className="workspace-card">
          <div className="section-label">Workspace</div>
          <h2>Open a module</h2>
          <div className="module-grid">
            {grouped.map(({ group, items }) => (
              <div className="module-group" key={group}>
                <div className="section-label">{group}</div>
                {items.map((item) => (
                  <Link key={item.href} href={item.href} className="module-link">
                    <strong>{item.name}</strong><span>{item.description}</span>
                  </Link>
                ))}
              </div>
            ))}
          </div>
        </section>

        {editingPages && (
          <section className="page-editor">
            <div className="page-editor-header">
              <div><div className="section-label">Shared page editor</div><h2>Edit workspace pages</h2><p>Labels and descriptions are saved to the shared workspace state.</p></div>
              <div className="editor-actions">
                <button className="secondary-button" onClick={() => void resetPageConfig()}>Reset</button>
                <button className="primary-button" disabled={saving} onClick={() => void savePageConfig()}>{saving ? "Saving..." : "Save page settings"}</button>
              </div>
            </div>
            <div className="page-editor-grid">
              {modules.map((item) => (
                <div className="page-editor-row" key={item.href}>
                  <label>Page name<input value={item.name} onChange={(event) => updatePage(item.href, "name", event.target.value)} /></label>
                  <label>Description<input value={item.description} onChange={(event) => updatePage(item.href, "description", event.target.value)} /></label>
                </div>
              ))}
            </div>
            {saveMessage && <p className="form-message">{saveMessage}</p>}
          </section>
        )}

        <section className="workspace-card dashboard-tools">
          <div className="section-label">Platform</div>
          <div className="workflow">
            <a href={PRODUCTION_PWA_URL} target="_blank" rel="noreferrer">Production PWA</a>
            <a href={CREATIVE_STUDIOS_AI_URL} target="_blank" rel="noreferrer">Creative Studios AI</a>
            <a href={STREAMLIT_CLOUD_URL} target="_blank" rel="noreferrer">Streamlit Cloud</a>
            <button className="secondary-button" onClick={() => void changeTheme()}>{theme === "dark" ? "Use light mode" : "Use dark mode"}</button>
            <button className="secondary-button" onClick={() => setEditingPages((value) => !value)}>{editingPages ? "Close page editor" : "Edit pages"}</button>
          </div>
        </section>
      </section>
    </main>
  );
}
