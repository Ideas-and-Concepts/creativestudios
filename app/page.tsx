"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type Module = { name: string; description: string; href: string; group: string };
type Summary = { projects: number; drawings: number; boqItems: number; activeWorks: number };
type Project = { id: string; code?: string; name?: string; status?: string; description?: string | null };
type Document = { id: string; title?: string; documentType?: string; revision?: string | null; createdAt?: string; projectId?: string | null; isApproved?: boolean };
type Task = { id: string; title?: string; status?: string; priority?: string; createdAt?: string };
type Rfi = { id: string; rfiNumber?: string; subject?: string; status?: string; createdAt?: string };
type WorkspaceState = { pageConfig?: Record<string, Partial<Module>>; theme?: "dark" | "light" };

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

async function readJson<T>(response: Response): Promise<T | null> {
  const text = await response.text();
  if (!text) return null;
  try { return JSON.parse(text) as T; } catch { return null; }
}

function statusLabel(status?: string) {
  return (status || "open").replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function projectProgress(status?: string) {
  return ({ completed: 100, active: 74, on_hold: 56, planning: 28, cancelled: 12 } as Record<string, number>)[status || ""] ?? 42;
}

export default function Home() {
  const [theme, setTheme] = useState<"dark" | "light">("light");
  const [databaseReady, setDatabaseReady] = useState(false);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [rfis, setRfis] = useState<Rfi[]>([]);
  const [modules, setModules] = useState<Module[]>(defaultModules);
  const [projectFilter, setProjectFilter] = useState("All Projects");

  useEffect(() => {
    let cancelled = false;
    const refresh = async () => {
      const requests = await Promise.allSettled([
        fetch("/api/workspace-state", { cache: "no-store" }),
        fetch("/api/health", { cache: "no-store" }),
        fetch("/api/dashboard/summary", { cache: "no-store" }),
        fetch("/api/projects", { cache: "no-store" }),
        fetch("/api/workspace?module=documents", { cache: "no-store" }),
        fetch("/api/workspace?module=tasks", { cache: "no-store" }),
        fetch("/api/workspace?module=rfis", { cache: "no-store" }),
      ]);
      if (cancelled) return;

      const [workspace, health, dashboard, projectRows, documentRows, taskRows, rfiRows] = await Promise.all(
        requests.map(async (item) => item.status === "fulfilled" ? { response: item.value, data: await readJson<Record<string, any>>(item.value) } : { response: null, data: null }),
      );

      if (workspace.response?.ok) {
        const state = (workspace.data?.data || {}) as WorkspaceState;
        setModules(defaultModules.map((item) => ({ ...item, ...(state.pageConfig?.[item.href] ?? {}) })));
        if (state.theme === "dark" || state.theme === "light") setTheme(state.theme);
      }
      setDatabaseReady(Boolean(health.response?.ok && health.data?.ok && health.data?.database));
      if (dashboard.response?.ok && dashboard.data?.data) setSummary({ ...emptySummary, ...dashboard.data.data });
      if (projectRows.response?.ok && Array.isArray(projectRows.data?.data)) setProjects(projectRows.data!.data as Project[]);
      if (documentRows.response?.ok && Array.isArray(documentRows.data?.data)) setDocuments(documentRows.data!.data as Document[]);
      if (taskRows.response?.ok && Array.isArray(taskRows.data?.data)) setTasks(taskRows.data!.data as Task[]);
      if (rfiRows.response?.ok && Array.isArray(rfiRows.data?.data)) setRfis(rfiRows.data!.data as Rfi[]);
    };
    void refresh();
    return () => { cancelled = true; };
  }, []);

  const grouped = useMemo(() => groups.map((group) => ({ group, items: modules.filter((item) => item.group === group) })), [modules]);
  const projectMap = useMemo(() => new Map(projects.map((project) => [project.id, project.name || "Unassigned"])), [projects]);
  const filteredDocuments = useMemo(() => projectFilter === "All Projects" ? documents : documents.filter((doc) => projectMap.get(doc.projectId || "") === projectFilter), [documents, projectFilter, projectMap]);
  const activeTasks = tasks.filter((task) => ["open", "in_progress", "review"].includes((task.status || "").toLowerCase())).length;
  const completeTasks = tasks.filter((task) => (task.status || "").toLowerCase() === "completed").length;
  const openRfis = rfis.filter((rfi) => !["closed", "completed"].includes((rfi.status || "").toLowerCase())).length;
  const documentTypeCounts = useMemo(() => filteredDocuments.reduce<Record<string, number>>((acc, doc) => { const key = doc.documentType || "Other"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [filteredDocuments]);
  const taskStatusCounts = useMemo(() => tasks.reduce<Record<string, number>>((acc, task) => { const key = task.status || "open"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [tasks]);
  const rfiStatusCounts = useMemo(() => rfis.reduce<Record<string, number>>((acc, rfi) => { const key = rfi.status || "open"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [rfis]);

  const palette = ["#3B82F6", "#64748B", "#CBD5E1", "#94A3B8"];
  const documentTotal = Math.max(filteredDocuments.length, 1);
  const taskTotal = Math.max(tasks.length, 1);
  const donutStops = (counts: Record<string, number>) => {
    let cursor = 0;
    return Object.entries(counts).slice(0, 4).map(([key, value], index) => { const start = cursor; cursor += (value / Math.max(Object.values(counts).reduce((a, b) => a + b, 0), 1)) * 360; return `${palette[index]} ${start}deg ${cursor}deg`; }).join(", ");
  };

  return (
    <main className={theme === "dark" ? "cs-dashboard-page dark" : "cs-dashboard-page"}>
      <style>{`
        .cs-dashboard-page{min-height:100vh;background:#f7f8fa;color:#111827;margin-left:250px;padding:88px 20px 28px}
        .cs-dashboard-inner{max-width:1370px;margin:0 auto}.cs-dashboard-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:18px}.cs-dashboard-head h1{font-size:20px;line-height:1.2;margin:0;font-weight:700;letter-spacing:-.025em}.cs-dashboard-head p{font-size:11px;color:#64748b;margin:4px 0 0}.cs-controls{display:flex;gap:9px;align-items:center}.cs-select,.cs-date{height:31px;border:1px solid #e2e6eb;background:#fff;border-radius:7px;padding:0 10px;color:#334155;font-size:10px;min-width:135px}.cs-date{min-width:170px}.cs-status{font-size:9px;border:1px solid #e5e7eb;border-radius:999px;padding:7px 10px;background:#fff;color:#64748b}.cs-status.ready{color:#15803d}
        .cs-kpis{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin-bottom:12px}.cs-kpi{background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:12px;min-height:78px}.cs-kpi-label{font-size:9px;color:#64748b}.cs-kpi-value{font-size:20px;font-weight:700;line-height:1.15;margin-top:7px;color:#111827}.cs-kpi-trend{font-size:8px;color:#16a34a;margin-top:5px}.cs-kpi-trend.down{color:#dc2626}
        .cs-grid-two{display:grid;grid-template-columns:1.35fr 1fr;gap:10px}.cs-grid-bottom{display:grid;grid-template-columns:1fr 1fr;gap:10px}.cs-panel{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:12px;min-width:0;margin-bottom:10px}.cs-panel-title{font-size:10px;font-weight:700;color:#111827;margin-bottom:7px}.cs-chart{height:205px}.cs-chart svg{width:100%;height:100%}.cs-legend{display:flex;gap:15px;flex-wrap:wrap;margin-top:-3px;font-size:8px;color:#64748b}.cs-legend span{display:flex;align-items:center;gap:4px}.cs-dot{width:7px;height:7px;border-radius:50%;display:inline-block}.cs-donut-row{display:flex;align-items:center;gap:16px;height:205px}.cs-donut{width:125px;height:125px;border-radius:50%;position:relative;flex:0 0 auto}.cs-donut:after{content:"";position:absolute;inset:32px;border-radius:50%;background:#fff}.cs-donut-center{position:absolute;inset:0;display:grid;place-items:center;z-index:1;text-align:center;font-size:9px;color:#64748b}.cs-donut-center strong{display:block;font-size:18px;color:#111827}.cs-list{display:grid;gap:10px;min-width:150px}.cs-list-row{display:grid;grid-template-columns:8px 1fr auto;gap:7px;align-items:center;font-size:8px;color:#64748b}.cs-list-row strong{font-size:9px;color:#334155}.cs-table-wrap{overflow:auto}.cs-table{width:100%;border-collapse:collapse;font-size:8px;min-width:620px}.cs-table th{padding:7px 5px;text-align:left;color:#64748b;font-size:7px;font-weight:700;border-bottom:1px solid #e5e7eb}.cs-table td{padding:8px 5px;border-bottom:1px solid #f1f5f9;color:#334155}.cs-table td:first-child{font-weight:600;color:#1f2937}.cs-pill{display:inline-block;border-radius:999px;padding:3px 6px;background:#eff6ff;color:#2563eb;font-weight:700;font-size:7px}.cs-bar-chart{height:205px;display:flex;align-items:flex-end;gap:17px;padding:14px 10px 26px;border-bottom:1px solid #e5e7eb}.cs-bar-item{height:100%;flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:5px}.cs-bar{width:32px;max-width:100%;background:#3b82f6;border-radius:3px 3px 0 0;min-height:4px}.cs-bar-label{font-size:7px;color:#64748b;text-align:center}.cs-empty{font-size:9px;color:#94a3b8;padding:30px 0;text-align:center}
        .cs-dark{background:#0b1018}.cs-dashboard-page.dark{background:#0b1018;color:#f8fafc}.cs-dashboard-page.dark .cs-panel,.cs-dashboard-page.dark .cs-kpi,.cs-dashboard-page.dark .cs-select,.cs-dashboard-page.dark .cs-date,.cs-dashboard-page.dark .cs-status{background:#111827;border-color:#1e293b;color:#e2e8f0}.cs-dashboard-page.dark .cs-dashboard-head h1,.cs-dashboard-page.dark .cs-kpi-value,.cs-dashboard-page.dark .cs-panel-title,.cs-dashboard-page.dark .cs-list-row strong{color:#f8fafc}.cs-dashboard-page.dark .cs-table td{color:#cbd5e1;border-color:#1e293b}.cs-dashboard-page.dark .cs-table th,.cs-dashboard-page.dark .cs-dashboard-head p,.cs-dashboard-page.dark .cs-kpi-label,.cs-dashboard-page.dark .cs-list-row{color:#94a3b8}.cs-dashboard-page.dark .cs-donut:after{background:#111827}.cs-dashboard-page.dark .cs-donut-center strong{color:#f8fafc}
        @media(max-width:1100px){.cs-kpis{grid-template-columns:repeat(3,1fr)}.cs-grid-two{grid-template-columns:1fr}}@media(max-width:800px){.cs-dashboard-page{margin-left:0;padding:78px 10px 20px}.cs-dashboard-head{display:block}.cs-controls{margin-top:12px;flex-wrap:wrap}.cs-kpis{grid-template-columns:repeat(2,1fr)}.cs-grid-bottom{grid-template-columns:1fr}.cs-donut-row{justify-content:center}.cs-list{min-width:130px}}@media(max-width:480px){.cs-kpis{grid-template-columns:1fr 1fr}.cs-select,.cs-date{flex:1;min-width:120px}}
      `}</style>

      <div className="cs-dashboard-inner">
        <header className="cs-dashboard-head">
          <div><h1>Dashboard</h1><p>Project Overview</p></div>
          <div className="cs-controls">
            <select className="cs-select" value={projectFilter} onChange={(event) => setProjectFilter(event.target.value)} aria-label="Project filter">
              <option>All Projects</option>{projects.map((project) => <option key={project.id}>{project.name || project.code || "Untitled"}</option>)}
            </select>
            <input className="cs-date" type="text" value="May 25 - Jun 1, 2025" readOnly aria-label="Date range" />
            <span className={`cs-status${databaseReady ? " ready" : ""}`}>{databaseReady ? "Database connected" : "Database unavailable"}</span>
          </div>
        </header>

        <section className="cs-kpis" aria-label="Dashboard metrics">
          {[
            ["Projects", summary.projects, "↑ 8%", false], ["Documents", filteredDocuments.length, "↑ 15%", false], ["Drawings", summary.drawings, "↑ 12%", false], ["RFIs", rfis.length || summary.activeWorks, "↓ 3%", true], ["Tasks", tasks.length, "↑ 6%", false], ["Budget", "$2.45M", "↑ 9%", false],
          ].map(([label, value, trend, down]) => <div className="cs-kpi" key={String(label)}><div className="cs-kpi-label">{label}</div><div className="cs-kpi-value">{value}</div><div className={`cs-kpi-trend${down ? " down" : ""}`}>{trend}</div></div>)}
        </section>

        <div className="cs-grid-two">
          <section className="cs-panel"><div className="cs-panel-title">Project Progress</div><div className="cs-chart">
            {projects.length ? <svg viewBox="0 0 720 210" role="img" aria-label="Project progress chart"><g stroke="#e5e7eb" strokeWidth="1">{[25,50,75,100].map((value) => <line key={value} x1="42" x2="705" y1={185 - value * 1.45} y2={185 - value * 1.45} />)}</g><g fill="#94a3b8" fontSize="8"><text x="8" y="185">0%</text><text x="4" y="149">25%</text><text x="4" y="112">50%</text><text x="4" y="76">75%</text><text x="0" y="39">100%</text></g>{projects.slice(0,3).map((project,index)=>{const progress=projectProgress(project.status);const values=[Math.max(8,progress-34),Math.max(15,progress-23),Math.max(20,progress-14),Math.max(25,progress-10),Math.max(30,progress-7),Math.max(35,progress-5),Math.max(40,progress-3),progress];const points=values.map((value,i)=>`${50+i*92},${185-value*1.45}`).join(" ");return <g key={project.id}><polyline fill="none" stroke={palette[index]} strokeWidth="2" points={points}/>{values.map((value,i)=><circle key={i} cx={50+i*92} cy={185-value*1.45} r="2.5" fill={palette[index]}/>)}</g>})}<g fill="#64748b" fontSize="7">{["May 25","May 26","May 27","May 28","May 29","May 30","May 31","Jun 1"].map((label,index)=><text key={label} x={42+index*92} y="204">{label}</text>)}</g></svg> : <div className="cs-empty">Add projects to populate the progress chart.</div>}
          </div><div className="cs-legend">{projects.slice(0,3).map((project,index)=><span key={project.id}><i className="cs-dot" style={{background:palette[index]}} />{project.name || "Untitled"}</span>)}</div></section>

          <section className="cs-panel"><div className="cs-panel-title">Documents by Type</div><div className="cs-donut-row"><div className="cs-donut" style={{background: `conic-gradient(${donutStops(documentTypeCounts) || "#3b82f6 0deg 360deg"})`}}><div className="cs-donut-center"><div><strong>{filteredDocuments.length}</strong>Total</div></div></div><div className="cs-list">{Object.entries(documentTypeCounts).slice(0,4).map(([key,value],index)=><div className="cs-list-row" key={key}><i className="cs-dot" style={{background:palette[index]}} /><span>{key}</span><strong>{value} ({Math.round(value/documentTotal*100)}%)</strong></div>)}{!filteredDocuments.length && <div className="cs-empty">No documents yet.</div>}</div></div></section>
        </div>

        <section className="cs-panel"><div className="cs-panel-title">Recent Documents</div><div className="cs-table-wrap"><table className="cs-table"><thead><tr><th>Name</th><th>Project</th><th>Type</th><th>Revision</th><th>Date</th><th>Status</th></tr></thead><tbody>{filteredDocuments.slice(0,5).map((doc)=><tr key={doc.id}><td>{doc.title || "Untitled document"}</td><td>{projectMap.get(doc.projectId || "") || "Unassigned"}</td><td>{doc.documentType || "Document"}</td><td>{doc.revision || "A"}</td><td>{doc.createdAt ? new Date(doc.createdAt).toLocaleDateString("en-US", {month:"short",day:"numeric",year:"numeric"}) : ""}</td><td><span className="cs-pill">{doc.isApproved ? "Approved" : "Draft"}</span></td></tr>)}{!filteredDocuments.length && <tr><td colSpan={6}><div className="cs-empty">No documents have been recorded yet.</div></td></tr>}</tbody></table></div></section>

        <div className="cs-grid-bottom">
          <section className="cs-panel"><div className="cs-panel-title">Tasks by Status</div><div className="cs-donut-row"><div className="cs-donut" style={{background:`conic-gradient(${donutStops(taskStatusCounts) || "#3b82f6 0deg 360deg"})`}}><div className="cs-donut-center"><div><strong>{tasks.length}</strong>Total</div></div></div><div className="cs-list">{Object.entries(taskStatusCounts).slice(0,4).map(([key,value],index)=><div className="cs-list-row" key={key}><i className="cs-dot" style={{background:palette[index]}}/><span>{statusLabel(key)}</span><strong>{value} ({Math.round(value/taskTotal*100)}%)</strong></div>)}{!tasks.length && <div className="cs-empty">No tasks yet.</div>}</div></div></section>

          <section className="cs-panel"><div className="cs-panel-title">RFI Status</div><div className="cs-bar-chart">{Object.entries(rfiStatusCounts).slice(0,4).map(([key,value])=><div className="cs-bar-item" key={key}><div className="cs-bar" style={{height:`${Math.max(4,(value/Math.max(...Object.values(rfiStatusCounts),1))*150)}px`}} title={`${statusLabel(key)}: ${value}`} /><div className="cs-bar-label">{statusLabel(key)}</div></div>)}{!rfis.length && <div className="cs-empty" style={{width:"100%"}}>No RFIs yet.</div>}</div></section>
        </div>

        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",fontSize:8,color:"#94a3b8",padding:"5px 2px 0"}}><span>{activeTasks} active tasks · {completeTasks} completed · {openRfis} open RFIs · {summary.activeWorks} active works</span><Link href="/settings" style={{color:"#64748b",textDecoration:"none"}}>Workspace settings</Link></div>
      </div>
    </main>
  );
}
