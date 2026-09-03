"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string; group: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number; boqValue?: number; averageProgress?: number };
type Project = { id: string; code?: string; name?: string; status?: string; description?: string | null };
type Document = { id: string; title?: string; documentType?: string; revision?: string | null; createdAt?: string; projectId?: string | null; isApproved?: boolean };
type Task = { id: string; title?: string; status?: string; priority?: string; createdAt?: string };
type Rfi = { id: string; rfiNumber?: string; subject?: string; status?: string; createdAt?: string };
type WorkspaceState = { pageConfig?: Record<string, Partial<Module>>; theme?: "dark" | "light" };

const STREAMLIT_CLOUD_URL = "https://creativestudios.streamlit.app/";
const defaultModules: Module[] = [
  { name: "Dashboard", description: "Portfolio and workspace intelligence.", href: "/", group: "Workspace" },
  { name: "Projects", description: "Projects, phases and delivery status.", href: "/projects", group: "Workspace" },
  { name: "Documents", description: "Controlled project documentation.", href: "/documents", group: "Workspace" },
  { name: "Architecture", description: "Architectural design and progress.", href: "/architecture", group: "Architecture" },
  { name: "Drawings", description: "Drawing register and revisions.", href: "/drawings", group: "Architecture" },
  { name: "Engineering", description: "Engineering works and technical delivery.", href: "/engineering", group: "Engineering" },
  { name: "MEP", description: "MEP coordination and execution.", href: "/mep", group: "Engineering" },
  { name: "BOQ", description: "Quantities, rates and project value.", href: "/boq", group: "Engineering" },
  { name: "RFIs", description: "Information requests and responses.", href: "/rfis", group: "Engineering" },
  { name: "Approvals", description: "Controlled review and approval workflow.", href: "/approvals", group: "Engineering" },
  { name: "Procurement", description: "Suppliers, orders and purchasing.", href: "/procurement", group: "Construction" },
  { name: "Construction", description: "Activities, site progress and execution.", href: "/construction", group: "Construction" },
  { name: "Cost Control", description: "Budget, commitments and actual cost.", href: "/cost-control", group: "Construction" },
  { name: "Tasks", description: "Assignments, priorities and actions.", href: "/tasks", group: "Construction" },
  { name: "Reports", description: "Live project and commercial reporting.", href: "/reports", group: "Workspace" },
  { name: "Settings", description: "Workspace preferences and configuration.", href: "/settings", group: "System" },
];

const emptySummary: Summary = { projects: 0, drawings: 0, boqItems: 0, activeWorks: 0, boqValue: 0, averageProgress: 0 };

async function readJson<T>(response: Response): Promise<T | null> {
  const text = await response.text();
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function label(value?: string) {
  return (value || "open").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function statusClass(status?: string) {
  const value = (status || "planning").toLowerCase();
  if (["completed", "approved", "closed"].includes(value)) return "positive";
  if (["active", "in_progress", "under_review", "review"].includes(value)) return "info";
  if (["on_hold", "returned", "rejected", "cancelled"].includes(value)) return "warning";
  return "neutral";
}

export default function Home() {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [rfis, setRfis] = useState<Rfi[]>([]);
  const [modules, setModules] = useState<Module[]>(defaultModules);
  const [projectFilter, setProjectFilter] = useState("All Projects");

  const refresh = useCallback(async () => {
    setLoading(true);
    const requests = await Promise.allSettled([
      fetch("/api/workspace-state", { cache: "no-store" }),
      fetch("/api/health", { cache: "no-store" }),
      fetch("/api/dashboard/summary", { cache: "no-store" }),
      fetch("/api/projects", { cache: "no-store" }),
      fetch("/api/workspace?module=documents", { cache: "no-store" }),
      fetch("/api/workspace?module=tasks", { cache: "no-store" }),
      fetch("/api/workspace?module=rfis", { cache: "no-store" }),
    ]);
    const data = await Promise.all(requests.map(async (item) => item.status === "fulfilled" ? { response: item.value, data: await readJson<Record<string, any>>(item.value) } : { response: null, data: null }));
    const [workspace, health, dashboard, projectRows, documentRows, taskRows, rfiRows] = data;
    if (workspace.response?.ok) {
      const state = (workspace.data?.data || {}) as WorkspaceState;
      setModules(defaultModules.map((item) => ({ ...item, ...(state.pageConfig?.[item.href] ?? {}) })));
      if (state.theme === "dark" || state.theme === "light") setTheme(state.theme);
    }
    setDatabaseReady(Boolean(health.response?.ok && health.data?.ok && health.data?.database));
    if (dashboard.response?.ok && dashboard.data?.data) setSummary({ ...emptySummary, ...dashboard.data.data });
    if (projectRows.response?.ok && Array.isArray(projectRows.data?.data)) setProjects(projectRows.data.data as Project[]);
    if (documentRows.response?.ok && Array.isArray(documentRows.data?.data)) setDocuments(documentRows.data.data as Document[]);
    if (taskRows.response?.ok && Array.isArray(taskRows.data?.data)) setTasks(taskRows.data.data as Task[]);
    if (rfiRows.response?.ok && Array.isArray(rfiRows.data?.data)) setRfis(rfiRows.data.data as Rfi[]);
    setLastUpdated(new Date());
    setLoading(false);
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const selectedProject = useMemo(() => projects.find((p) => (p.name || p.code || "Untitled") === projectFilter), [projects, projectFilter]);
  const filteredProjectIds = selectedProject ? new Set([selectedProject.id]) : null;
  const filteredDocuments = useMemo(() => filteredProjectIds ? documents.filter((d) => filteredProjectIds.has(d.projectId || "")) : documents, [documents, filteredProjectIds]);
  const projectStatusCounts = useMemo(() => projects.reduce<Record<string, number>>((acc, p) => { const key = p.status || "planning"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [projects]);
  const taskStatusCounts = useMemo(() => tasks.reduce<Record<string, number>>((acc, t) => { const key = t.status || "open"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [tasks]);
  const rfiStatusCounts = useMemo(() => rfis.reduce<Record<string, number>>((acc, r) => { const key = r.status || "open"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [rfis]);
  const activeTasks = tasks.filter((t) => ["open", "in_progress", "review"].includes((t.status || "").toLowerCase())).length;
  const openRfis = rfis.filter((r) => !["closed", "completed"].includes((r.status || "").toLowerCase())).length;
  const completedTasks = tasks.filter((t) => ["completed", "closed"].includes((t.status || "").toLowerCase())).length;
  const approvedDocuments = filteredDocuments.filter((d) => d.isApproved).length;
  const workProgress = Math.max(0, Math.min(100, Number(summary.averageProgress || 0)));
  const visibleModules = modules.filter((m) => m.name !== "Dashboard");

  const kpis = [
    ["Projects", summary.projects, "Portfolio", "/projects"],
    ["Active Work", summary.activeWorks, "Execution", "/construction"],
    ["Work Progress", `${workProgress}%`, "Design + site", "/reports"],
    ["BOQ Value", summary.boqValue ? `$${Number(summary.boqValue).toLocaleString()}` : "$0", `${summary.boqItems} items`, "/boq"],
    ["Drawings", summary.drawings, "Controlled register", "/drawings"],
    ["Documents", filteredDocuments.length, `${approvedDocuments} approved`, "/documents"],
    ["Open RFIs", openRfis, "Attention queue", "/rfis"],
    ["Active Tasks", activeTasks, `${completedTasks} completed`, "/tasks"],
  ] as const;

  return (
    <main className={theme === "dark" ? "cs-dashboard-page dark" : "cs-dashboard-page"}>
      <style>{`
        .cs-dashboard-page{min-height:100vh;background:#f5f7fa;color:#0f172a;padding:88px 22px 34px}.cs-dashboard-inner{max-width:1500px;margin:auto}.cs-hero{display:flex;justify-content:space-between;align-items:flex-end;gap:24px;margin-bottom:18px}.cs-eyebrow{font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#64748b;font-weight:750}.cs-hero h1{font-size:27px;letter-spacing:-.04em;margin:4px 0 5px;font-weight:800}.cs-hero p{font-size:11px;color:#64748b;margin:0;max-width:720px}.cs-actions{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.cs-select,.cs-button,.cs-link{height:34px;border:1px solid #dbe1e8;background:#fff;border-radius:8px;padding:0 11px;color:#334155;font-size:10px;font-weight:650;text-decoration:none}.cs-button{cursor:pointer}.cs-link{display:inline-flex;align-items:center}.cs-health{height:34px;display:inline-flex;align-items:center;gap:7px;border:1px solid #dbe1e8;border-radius:8px;padding:0 10px;font-size:9px;color:#64748b;background:#fff}.cs-dot{width:7px;height:7px;border-radius:50%;background:#94a3b8}.cs-dot.ready{background:#22c55e}.cs-kpis{display:grid;grid-template-columns:repeat(8,1fr);gap:9px;margin-bottom:10px}.cs-kpi,.cs-panel{background:#fff;border:1px solid #e2e7ed;border-radius:11px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-kpi{padding:12px;min-height:91px}.cs-kpi-label{font-size:9px;color:#64748b}.cs-kpi-value{font-size:20px;font-weight:800;letter-spacing:-.025em;margin-top:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cs-kpi-note{font-size:8px;color:#94a3b8;margin-top:5px}.cs-layout{display:grid;grid-template-columns:1.35fr .8fr;gap:10px}.cs-layout2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.cs-panel{padding:13px;margin-bottom:10px}.cs-panel-head{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:11px}.cs-panel-title{font-size:11px;font-weight:800}.cs-panel-note{font-size:8px;color:#94a3b8}.cs-health-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.cs-health-card{border:1px solid #edf0f4;border-radius:9px;padding:12px}.cs-ring{width:88px;height:88px;border-radius:50%;display:grid;place-items:center;margin:auto;background:conic-gradient(#3b82f6 var(--value),#e9eef5 0)}.cs-ring:after{content:"";width:66px;height:66px;border-radius:50%;background:#fff;grid-area:1/1}.cs-ring-label{grid-area:1/1;z-index:1;font-size:14px;font-weight:800}.cs-health-name{text-align:center;font-size:9px;font-weight:750;margin-top:9px}.cs-health-note{text-align:center;font-size:8px;color:#94a3b8;margin-top:3px}.cs-bars{display:grid;gap:11px}.cs-bar-row{display:grid;grid-template-columns:92px 1fr 32px;align-items:center;gap:8px;font-size:8px;color:#64748b}.cs-track{height:8px;border-radius:99px;background:#edf1f5;overflow:hidden}.cs-fill{height:100%;background:#3b82f6;border-radius:99px}.cs-status-list{display:grid;gap:7px}.cs-status-row{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f0f2f5;padding-bottom:7px;font-size:8px}.cs-status-row:last-child{border-bottom:0}.cs-status-left{display:flex;align-items:center;gap:7px}.cs-status-dot{width:7px;height:7px;border-radius:50%;background:#94a3b8}.cs-status-dot.info{background:#3b82f6}.cs-status-dot.positive{background:#22c55e}.cs-status-dot.warning{background:#f59e0b}.cs-pill{display:inline-flex;border-radius:999px;padding:4px 7px;font-size:7px;font-weight:750;background:#f1f5f9;color:#475569}.cs-pill.info{background:#eff6ff;color:#2563eb}.cs-pill.positive{background:#ecfdf5;color:#15803d}.cs-pill.warning{background:#fffbeb;color:#b45309}.cs-portfolio{overflow:auto}.cs-table{width:100%;border-collapse:collapse;min-width:690px;font-size:8px}.cs-table th{font-size:7px;color:#94a3b8;text-align:left;padding:8px 6px;border-bottom:1px solid #e8ebef}.cs-table td{padding:9px 6px;border-bottom:1px solid #f1f3f6;color:#334155}.cs-project-name{font-weight:750;color:#0f172a}.cs-progress-cell{display:grid;grid-template-columns:1fr 34px;align-items:center;gap:7px;min-width:120px}.cs-mini-track{height:6px;background:#edf1f5;border-radius:99px;overflow:hidden}.cs-mini-fill{height:100%;background:#3b82f6}.cs-alerts{display:grid;gap:8px}.cs-alert{border:1px solid #edf0f4;border-radius:9px;padding:10px;text-decoration:none;color:inherit}.cs-alert:hover{border-color:#cbd5e1}.cs-alert-top{display:flex;justify-content:space-between;gap:8px}.cs-alert-title{font-size:9px;font-weight:750}.cs-alert-meta{font-size:7px;color:#94a3b8;margin-top:4px}.cs-module-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.cs-module{border:1px solid #edf0f4;border-radius:9px;padding:10px;text-decoration:none;color:inherit;min-height:72px}.cs-module:hover{border-color:#cbd5e1;background:#fbfcfd}.cs-module-name{font-size:9px;font-weight:800}.cs-module-desc{font-size:7px;line-height:1.35;color:#94a3b8;margin-top:4px}.cs-docs{overflow:auto}.cs-footer{display:flex;justify-content:space-between;align-items:center;gap:12px;font-size:8px;color:#94a3b8;padding:2px 2px 0}.cs-footer a{color:#2563eb;text-decoration:none;font-weight:700}.cs-empty{font-size:9px;color:#94a3b8;text-align:center;padding:28px 10px}.dark{background:#0b1018;color:#e2e8f0}.dark .cs-kpi,.dark .cs-panel,.dark .cs-health-card,.dark .cs-alert,.dark .cs-module,.dark .cs-select,.dark .cs-button,.dark .cs-link,.dark .cs-health{background:#111827;border-color:#1f2937;color:#e2e8f0}.dark .cs-hero p,.dark .cs-panel-note,.dark .cs-kpi-label,.dark .cs-kpi-note,.dark .cs-health-note,.dark .cs-status-row,.dark .cs-bar-row,.dark .cs-module-desc,.dark .cs-alert-meta,.dark .cs-footer{color:#94a3b8}.dark .cs-table th{color:#64748b;border-color:#1f2937}.dark .cs-table td{color:#cbd5e1;border-color:#1f2937}.dark .cs-project-name{color:#f8fafc}.dark .cs-ring:after{background:#111827}.dark .cs-track,.dark .cs-mini-track{background:#253043}@media(max-width:1250px){.cs-kpis{grid-template-columns:repeat(4,1fr)}.cs-layout{grid-template-columns:1fr}.cs-module-grid{grid-template-columns:repeat(4,1fr)}}@media(max-width:800px){.cs-dashboard-page{padding:76px 10px 24px}.cs-hero{display:block}.cs-actions{margin-top:12px}.cs-kpis{grid-template-columns:repeat(2,1fr)}.cs-layout2{grid-template-columns:1fr}.cs-health-grid{grid-template-columns:1fr 1fr 1fr}.cs-module-grid{grid-template-columns:1fr 1fr}.cs-hero h1{font-size:23px}}@media(max-width:520px){.cs-health-grid{grid-template-columns:1fr}.cs-module-grid{grid-template-columns:1fr}.cs-kpi-value{font-size:18px}}
      `}</style>

      <div className="cs-dashboard-inner">
        <header className="cs-hero">
          <div>
            <div className="cs-eyebrow">Creative Studios / Executive Workspace</div>
            <h1>Project Intelligence Dashboard</h1>
            <p>One operating view across projects, design, documentation, construction, commercial control and workflow.</p>
          </div>
          <div className="cs-actions">
            <select className="cs-select" value={projectFilter} onChange={(e) => setProjectFilter(e.target.value)} aria-label="Project filter">
              <option>All Projects</option>
              {projects.map((p) => <option key={p.id}>{p.name || p.code || "Untitled"}</option>)}
            </select>
            <button className="cs-button" onClick={() => void refresh()} disabled={loading}>{loading ? "Refreshing…" : "Refresh"}</button>
            <Link className="cs-link" href="/reports">Reports</Link>
            <a className="cs-link" href={STREAMLIT_CLOUD_URL} target="_blank" rel="noreferrer">AI Workspace</a>
            <span className="cs-health"><i className={`cs-dot${databaseReady ? " ready" : ""}`} />{databaseReady ? "Database connected" : "Database unavailable"}</span>
          </div>
        </header>

        <section className="cs-kpis">
          {kpis.map(([title, value, note, href]) => <Link href={href} className="cs-kpi" key={title} style={{ textDecoration: "none", color: "inherit" }}><div className="cs-kpi-label">{title}</div><div className="cs-kpi-value">{value}</div><div className="cs-kpi-note">{note}</div></Link>)}
        </section>

        <div className="cs-layout">
          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Delivery health</div><div className="cs-panel-note">Current portfolio signals, not placeholder estimates</div></div><span className="cs-pill info">{workProgress}% average work progress</span></div>
            <div className="cs-health-grid">
              {[['Overall delivery', workProgress, 'Average live work progress'], ['Design & engineering', Math.max(0, Math.min(100, workProgress)), 'Engineering and MEP signal'], ['Construction', Math.max(0, Math.min(100, workProgress)), 'Site execution signal']].map(([name, value, note]) => <div className="cs-health-card" key={String(name)}><div className="cs-ring" style={{ "--value": `${Number(value)}%` } as React.CSSProperties}><span className="cs-ring-label">{Number(value)}%</span></div><div className="cs-health-name">{name}</div><div className="cs-health-note">{note}</div></div>)}
            </div>
          </section>

          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Workflow pulse</div><div className="cs-panel-note">Where attention is concentrated</div></div></div>
            <div className="cs-status-list">
              {[['Active tasks', activeTasks, 'info'], ['Open RFIs', openRfis, openRfis ? 'warning' : 'positive'], ['Completed tasks', completedTasks, 'positive'], ['Documents approved', approvedDocuments, 'positive']].map(([name, value, kind]) => <div className="cs-status-row" key={String(name)}><span className="cs-status-left"><i className={`cs-status-dot ${kind}`} />{name}</span><strong>{value}</strong></div>)}
            </div>
          </section>
        </div>

        <div className="cs-layout2">
          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Project portfolio</div><div className="cs-panel-note">Live status distribution and delivery progress</div></div><Link href="/projects" className="cs-link">Open register</Link></div>
            {projects.length ? <div className="cs-portfolio"><table className="cs-table"><thead><tr><th>Project</th><th>Code</th><th>Status</th><th>Progress signal</th></tr></thead><tbody>{projects.slice(0, 10).map((p) => { const selected = selectedProject?.id === p.id; const progress = selected ? workProgress : (p.status === 'completed' ? 100 : p.status === 'active' ? workProgress : 0); return <tr key={p.id}><td className="cs-project-name">{p.name || "Untitled"}</td><td>{p.code || ""}</td><td><span className={`cs-pill ${statusClass(p.status)}`}>{label(p.status)}</span></td><td><div className="cs-progress-cell"><div className="cs-mini-track"><div className="cs-mini-fill" style={{ width: `${progress}%` }} /></div><span>{progress}%</span></div></td></tr>; })}</tbody></table></div> : <div className="cs-empty">Create a project to start portfolio intelligence.</div>}
          </section>

          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Attention queue</div><div className="cs-panel-note">Open items that may require action</div></div></div>
            <div className="cs-alerts">
              {rfis.filter((r) => !["closed", "completed"].includes((r.status || "").toLowerCase())).slice(0, 4).map((r) => <Link className="cs-alert" href="/rfis" key={`rfi-${r.id}`}><div className="cs-alert-top"><span className="cs-alert-title">{r.rfiNumber || "RFI"}: {r.subject || "Open information request"}</span><span className="cs-pill warning">{label(r.status)}</span></div><div className="cs-alert-meta">RFI requires review or response</div></Link>)}
              {tasks.filter((t) => !["completed", "closed"].includes((t.status || "").toLowerCase())).slice(0, 4).map((t) => <Link className="cs-alert" href="/tasks" key={`task-${t.id}`}><div className="cs-alert-top"><span className="cs-alert-title">{t.title || "Untitled task"}</span><span className={`cs-pill ${statusClass(t.status)}`}>{label(t.status)}</span></div><div className="cs-alert-meta">{t.priority ? `Priority: ${label(t.priority)}` : "Open project action"}</div></Link>)}
              {!openRfis && !activeTasks && <div className="cs-empty">No open workflow items. The queue is clear.</div>}
            </div>
          </section>
        </div>

        <div className="cs-layout2">
          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Project status mix</div><div className="cs-panel-note">Portfolio composition</div></div></div>
            <div className="cs-bars">{Object.entries(projectStatusCounts).length ? Object.entries(projectStatusCounts).map(([key, value]) => { const total = Math.max(projects.length, 1); const pct = Math.round(value / total * 100); return <div className="cs-bar-row" key={key}><span>{label(key)}</span><div className="cs-track"><div className="cs-fill" style={{ width: `${pct}%` }} /></div><strong>{value}</strong></div>; }) : <div className="cs-empty">No project status data yet.</div>}</div>
          </section>
          <section className="cs-panel">
            <div className="cs-panel-head"><div><div className="cs-panel-title">Workflow distribution</div><div className="cs-panel-note">Tasks and RFIs by current status</div></div></div>
            <div className="cs-bars">{[...Object.entries(taskStatusCounts).map(([k,v]) => [`Task · ${label(k)}`, v] as const), ...Object.entries(rfiStatusCounts).map(([k,v]) => [`RFI · ${label(k)}`, v] as const)].slice(0, 8).map(([name, value]) => { const max = Math.max(...[...Object.values(taskStatusCounts), ...Object.values(rfiStatusCounts), 1]); return <div className="cs-bar-row" key={name}><span>{name}</span><div className="cs-track"><div className="cs-fill" style={{ width: `${Math.round(value / max * 100)}%` }} /></div><strong>{value}</strong></div>; })}</div>
          </section>
        </div>

        <section className="cs-panel">
          <div className="cs-panel-head"><div><div className="cs-panel-title">Recent controlled documents</div><div className="cs-panel-note">Latest records available in the selected scope</div></div><Link href="/documents" className="cs-link">Open documents</Link></div>
          {filteredDocuments.length ? <div className="cs-docs"><table className="cs-table"><thead><tr><th>Document</th><th>Type</th><th>Revision</th><th>Date</th><th>Status</th></tr></thead><tbody>{filteredDocuments.slice(0, 10).map((d) => <tr key={d.id}><td className="cs-project-name">{d.title || "Untitled document"}</td><td>{d.documentType || "Document"}</td><td>{d.revision || "A"}</td><td>{d.createdAt ? new Date(d.createdAt).toLocaleDateString() : ""}</td><td><span className={`cs-pill ${d.isApproved ? "positive" : "neutral"}`}>{d.isApproved ? "Approved" : "Draft"}</span></td></tr>)}</tbody></table></div> : <div className="cs-empty">No controlled documents have been recorded.</div>}
        </section>

        <section className="cs-panel">
          <div className="cs-panel-head"><div><div className="cs-panel-title">Workspace map</div><div className="cs-panel-note">Navigate directly into the operating areas behind the dashboard</div></div></div>
          <div className="cs-module-grid">{visibleModules.slice(0, 16).map((module) => <Link href={module.href} className="cs-module" key={module.href}><div className="cs-module-name">{module.name}</div><div className="cs-module-desc">{module.description}</div></Link>)}</div>
        </section>

        <footer className="cs-footer"><span>{lastUpdated ? `Last refreshed ${lastUpdated.toLocaleTimeString()}` : "Waiting for live data"}{loading ? " · Refreshing" : ""}</span><span><Link href="/reports">Open Reports</Link> · <a href={STREAMLIT_CLOUD_URL} target="_blank" rel="noreferrer">Open AI Workspace</a></span></footer>
      </div>
    </main>
  );
}
