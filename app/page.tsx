"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type Project = { id: string; code?: string; name?: string; status?: string };
type Document = { id: string; title?: string; documentType?: string; revision?: string | null; createdAt?: string; projectId?: string | null; isApproved?: boolean };
type Task = { id: string; title?: string; status?: string; priority?: string; projectId?: string | null };
type Rfi = { id: string; rfiNumber?: string; subject?: string; status?: string; projectId?: string | null };
type Commercial = { projectId?: string; budget?: number; committed?: number; actual?: number; earnedValue?: number; forecast?: number; variance?: number; cpi?: number | null; budgetUtilisation?: number };
type Summary = {
  projects: number; drawings: number; boqItems: number; activeWorks: number; boqValue?: number; averageProgress?: number;
  domainProgress?: { architecture?: number; engineering?: number; mep?: number; construction?: number };
  projectProgress?: { projectId: string; progress: number; activityCount: number }[];
  commercial?: Commercial;
  commercialByProject?: Commercial[];
};

const money = (n = 0) => `$${Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
const pct = (n = 0) => `${Math.round(Number(n))}%`;
const label = (s?: string) => (s || "Open").replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
const statusClass = (s?: string) => {
  const v = (s || "").toLowerCase();
  if (["completed", "approved", "closed"].includes(v)) return "positive";
  if (["active", "in_progress", "under_review", "review"].includes(v)) return "info";
  if (["on_hold", "returned", "rejected", "cancelled"].includes(v)) return "warning";
  return "neutral";
};

async function json<T>(r: Response): Promise<T | null> {
  try { return await r.json() as T; } catch { return null; }
}

export default function Home() {
  const [summary, setSummary] = useState<Summary>({ projects: 0, drawings: 0, boqItems: 0, activeWorks: 0 });
  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [rfis, setRfis] = useState<Rfi[]>([]);
  const [databaseReady, setDatabaseReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [projectFilter, setProjectFilter] = useState("All Projects");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    const results = await Promise.allSettled([
      fetch("/api/health", { cache: "no-store" }),
      fetch("/api/dashboard/summary", { cache: "no-store" }),
      fetch("/api/projects", { cache: "no-store" }),
      fetch("/api/workspace?module=documents", { cache: "no-store" }),
      fetch("/api/workspace?module=tasks", { cache: "no-store" }),
      fetch("/api/workspace?module=rfis", { cache: "no-store" }),
    ]);
    const rows = await Promise.all(results.map(async x => x.status === "fulfilled" ? { response: x.value, data: await json<any>(x.value) } : { response: null, data: null }));
    const [health, dashboard, projectRows, documentRows, taskRows, rfiRows] = rows;
    setDatabaseReady(Boolean(health.response?.ok && health.data?.database));
    if (dashboard.response?.ok && dashboard.data?.data) setSummary(dashboard.data.data);
    if (projectRows.response?.ok && Array.isArray(projectRows.data?.data)) setProjects(projectRows.data.data);
    if (documentRows.response?.ok && Array.isArray(documentRows.data?.data)) setDocuments(documentRows.data.data);
    if (taskRows.response?.ok && Array.isArray(taskRows.data?.data)) setTasks(taskRows.data.data);
    if (rfiRows.response?.ok && Array.isArray(rfiRows.data?.data)) setRfis(rfiRows.data.data);
    setLastUpdated(new Date());
    setLoading(false);
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const selectedProject = projects.find(p => p.id === projectFilter);
  const scoped = <T extends { projectId?: string | null }>(rows: T[]) => selectedProject ? rows.filter(row => row.projectId === selectedProject.id) : rows;
  const filteredDocuments = scoped(documents);
  const filteredTasks = scoped(tasks);
  const filteredRfis = scoped(rfis);
  const projectProgress = useMemo(() => new Map((summary.projectProgress || []).map(x => [x.projectId, x])), [summary.projectProgress]);
  // Commercial records are project-scoped when a project is selected.
  const commercial = useMemo(() => selectedProject
    ? (summary.commercialByProject || []).find(x => x.projectId === selectedProject.id) || { projectId: selectedProject.id }
    : summary.commercial || {}, [selectedProject, summary.commercial, summary.commercialByProject]);
  const selectedProjectProgress = selectedProject ? (projectProgress.get(selectedProject.id)?.progress || 0) : Number(summary.averageProgress || 0);
  const activeTasks = filteredTasks.filter(t => ["open", "in_progress", "review"].includes((t.status || "").toLowerCase()));
  const openRfis = filteredRfis.filter(r => !["closed", "answered", "completed"].includes((r.status || "").toLowerCase()));
  const completedTasks = filteredTasks.filter(t => ["completed", "closed"].includes((t.status || "").toLowerCase())).length;
  const approvedDocuments = filteredDocuments.filter(d => d.isApproved).length;
  const budget = Number(commercial.budget || (!selectedProject ? summary.boqValue : 0));
  const committed = Number(commercial.committed || 0);
  const actual = Number(commercial.actual || 0);
  const ev = Number(commercial.earnedValue || 0);
  const forecast = Number(commercial.forecast || 0);
  const variance = Number(commercial.variance || 0);
  const cpi = commercial.cpi == null ? null : Number(commercial.cpi);
  const utilisation = Number(commercial.budgetUtilisation || 0);
  const domains = summary.domainProgress || {};
  const domainRows = selectedProject ? [{ name: "Construction", value: selectedProjectProgress }] : [
    { name: "Architecture", value: Number(domains.architecture || 0) },
    { name: "Engineering", value: Number(domains.engineering || 0) },
    { name: "MEP", value: Number(domains.mep || 0) },
    { name: "Construction", value: Number(domains.construction || 0) },
  ];

  return (
    <main className="cs-exec">
      <style>{`/* Executive dashboard presentation */
        .cs-exec{min-height:100vh;background:#f5f7fa;color:#0f172a;padding:78px 22px 34px}.cs-wrap{max-width:1500px;margin:auto}.cs-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:14px}.cs-eyebrow{font-size:9px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#64748b}.cs-head h1{font-size:27px;letter-spacing:-.04em;margin:4px 0;font-weight:850}.cs-head p{margin:0;color:#64748b;font-size:10px}.cs-actions{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.cs-select,.cs-btn,.cs-link{height:33px;border:1px solid #dce2e9;border-radius:8px;background:#fff;color:#334155;padding:0 10px;font-size:9px;font-weight:700;text-decoration:none}.cs-btn{cursor:pointer}.cs-health{height:33px;display:flex;align-items:center;gap:6px;border:1px solid #dce2e9;border-radius:8px;background:#fff;padding:0 10px;color:#64748b;font-size:8px}.cs-health i{width:7px;height:7px;border-radius:50%;background:#94a3b8}.cs-health i.ready{background:#22c55e}.cs-kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:9px}.cs-kpi,.cs-panel{background:#fff;border:1px solid #e1e6ec;border-radius:11px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-kpi{padding:11px;min-height:82px}.cs-kpi small{font-size:8px;color:#64748b}.cs-kpi strong{display:block;font-size:19px;letter-spacing:-.025em;margin-top:7px}.cs-kpi span{font-size:7px;color:#94a3b8}.cs-commercial{display:grid;grid-template-columns:1.45fr .8fr;gap:9px;margin-bottom:9px}.cs-panel{padding:13px}.cs-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.cs-title strong{font-size:10px}.cs-title span{font-size:7px;color:#94a3b8}.cs-money-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.cs-money{border:1px solid #edf0f4;border-radius:9px;padding:10px}.cs-money small{display:block;font-size:7px;color:#64748b}.cs-money b{display:block;font-size:15px;margin-top:6px}.cs-money em{display:block;font-style:normal;font-size:7px;color:#94a3b8;margin-top:3px}.cs-meter{margin-top:12px}.cs-meter-top{display:flex;justify-content:space-between;font-size:8px;color:#64748b;margin-bottom:5px}.cs-track{height:8px;border-radius:99px;background:#edf1f5;overflow:hidden}.cs-fill{height:100%;border-radius:99px;background:#3b82f6}.cs-fill.warn{background:#f59e0b}.cs-eval{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.cs-eval-card{border:1px solid #edf0f4;border-radius:9px;padding:10px;text-align:center}.cs-eval-card small{display:block;font-size:7px;color:#64748b}.cs-eval-card b{font-size:18px;display:block;margin-top:6px}.cs-eval-card span{font-size:7px;color:#94a3b8}.cs-positive{color:#15803d}.cs-warning{color:#b45309}.cs-neutral{color:#334155}.cs-health-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:9px}.cs-health-card{border:1px solid #e1e6ec;border-radius:11px;background:#fff;padding:12px}.cs-health-label{font-size:8px;color:#64748b}.cs-health-value{font-size:18px;font-weight:800;margin-top:6px}.cs-health-note{font-size:7px;color:#94a3b8;margin-top:3px}.cs-bars{margin-top:12px;display:grid;gap:8px}.cs-bar{display:grid;grid-template-columns:92px 1fr 32px;gap:7px;align-items:center;font-size:7px;color:#64748b}.cs-bar .cs-track{height:7px}.cs-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.cs-list{display:grid;gap:7px}.cs-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #f0f2f5;font-size:8px}.cs-row:last-child{border-bottom:0}.cs-row-main{min-width:0}.cs-row-main b{display:block;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cs-row-main span{display:block;color:#94a3b8;font-size:7px;margin-top:2px}.cs-pill{padding:4px 6px;border-radius:999px;background:#f1f5f9;color:#475569;font-size:7px;font-weight:750;white-space:nowrap}.cs-pill.info{background:#eff6ff;color:#2563eb}.cs-pill.positive{background:#ecfdf5;color:#15803d}.cs-pill.warning{background:#fffbeb;color:#b45309}.cs-table{width:100%;border-collapse:collapse;font-size:8px}.cs-table th{text-align:left;color:#94a3b8;font-size:7px;padding:7px;border-bottom:1px solid #e9edf1}.cs-table td{padding:8px 7px;border-bottom:1px solid #f0f2f5;color:#334155}.cs-project{font-weight:750;color:#0f172a}.cs-progress{display:grid;grid-template-columns:1fr 30px;gap:6px;align-items:center;min-width:120px}.cs-mini{height:6px;border-radius:99px;background:#edf1f5;overflow:hidden}.cs-mini i{display:block;height:100%;background:#3b82f6}.cs-modules{display:grid;grid-template-columns:repeat(8,1fr);gap:7px;margin-top:9px}.cs-module{border:1px solid #e1e6ec;background:#fff;border-radius:9px;padding:10px;text-decoration:none;color:#334155}.cs-module b{font-size:8px}.cs-module span{display:block;font-size:7px;color:#94a3b8;margin-top:4px}.cs-foot{display:flex;justify-content:space-between;margin-top:9px;color:#94a3b8;font-size:7px}@media(max-width:1050px){.cs-kpis{grid-template-columns:repeat(3,1fr)}.cs-commercial,.cs-grid{grid-template-columns:1fr}.cs-modules{grid-template-columns:repeat(4,1fr)}}@media(max-width:650px){.cs-exec{padding:72px 10px 20px}.cs-head{align-items:flex-start;flex-direction:column}.cs-kpis{grid-template-columns:repeat(2,1fr)}.cs-money-grid,.cs-health-grid{grid-template-columns:1fr 1fr}.cs-modules{grid-template-columns:repeat(2,1fr)}.cs-eval{grid-template-columns:1fr 1fr 1fr}.cs-panel{padding:10px}}
      `}</style>
      <div className="cs-wrap">
        <header className="cs-head"><div><div className="cs-eyebrow">Creative Studios · Executive Workspace</div><h1>Project Controls Dashboard</h1><p>{selectedProject ? `${selectedProject.code || "Project"} · ${selectedProject.name || "Selected project"}` : "Live portfolio, delivery, commercial and earned-value intelligence."}</p></div><div className="cs-actions"><select className="cs-select" value={projectFilter} onChange={e => setProjectFilter(e.target.value)}><option value="All Projects">All Projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.code ? `${p.code} · ` : ""}{p.name || "Untitled"}</option>)}</select><button className="cs-btn" onClick={() => void refresh()}>{loading ? "Refreshing…" : "Refresh"}</button><span className="cs-health"><i className={databaseReady ? "ready" : ""} />{databaseReady ? "Database connected" : "Database unavailable"}</span></div></header>
        <section className="cs-kpis">{[["Projects", selectedProject ? 1 : summary.projects, selectedProject ? "Selected project" : "Portfolio"],["Active Work", selectedProject ? (projectProgress.get(selectedProject.id)?.activityCount || 0) : summary.activeWorks, "Execution"],["Work Progress", pct(selectedProjectProgress), "Actual construction / work data"],["BOQ Value", money(budget), selectedProject ? "Project BOQ" : `${summary.boqItems} items`],["Documents", filteredDocuments.length, `${approvedDocuments} approved`],["Open RFIs", openRfis.length, "Attention queue"]].map(([a,b,c]) => <div className="cs-kpi" key={String(a)}><small>{a}</small><strong>{b}</strong><span>{c}</span></div>)}</section>
        <section className="cs-commercial"><div className="cs-panel"><div className="cs-title"><strong>Commercial Position</strong><span>{selectedProject ? "Project-scoped" : "Portfolio-scoped"}</span></div><div className="cs-money-grid"><div className="cs-money"><small>Budget / BAC</small><b>{money(budget)}</b><em>BOQ basis</em></div><div className="cs-money"><small>Committed</small><b>{money(committed)}</b><em>Non-draft procurement</em></div><div className="cs-money"><small>Actual Cost</small><b>{money(actual)}</b><em>Recorded actuals</em></div><div className="cs-money"><small>Forecast / EAC</small><b>{money(forecast)}</b><em>Current estimate</em></div></div><div className="cs-meter"><div className="cs-meter-top"><span>Actual budget utilisation</span><b>{pct(utilisation)}</b></div><div className="cs-track"><div className="cs-fill" style={{width:`${Math.min(100,Math.max(0,utilisation))}%`}}/></div></div></div><div className="cs-panel"><div className="cs-title"><strong>Earned Value</strong><span>Current control indicators</span></div><div className="cs-eval"><div className="cs-eval-card"><small>EV</small><b>{money(ev)}</b><span>Earned value</span></div><div className="cs-eval-card"><small>CPI</small><b className={cpi != null && cpi < 1 ? "cs-warning" : "cs-positive"}>{cpi == null ? "N/A" : cpi.toFixed(2)}</b><span>Cost efficiency</span></div><div className="cs-eval-card"><small>Variance</small><b className={variance < 0 ? "cs-warning" : "cs-positive"}>{money(variance)}</b><span>Budget minus EAC</span></div></div></div></section>
        <section className="cs-health-grid"><div className="cs-health-card"><div className="cs-health-label">Delivery progress</div><div className="cs-health-value">{pct(selectedProjectProgress)}</div><div className="cs-health-note">{selectedProject ? "Selected project construction progress" : "Portfolio work progress"}</div><div className="cs-bars">{domainRows.map(x => <div className="cs-bar" key={x.name}><span>{x.name}</span><div className="cs-track"><div className="cs-fill" style={{width:`${Math.min(100,Math.max(0,x.value))}%`}}/></div><b>{pct(x.value)}</b></div>)}</div></div><div className="cs-health-card"><div className="cs-health-label">Task execution</div><div className="cs-health-value">{filteredTasks.length ? pct(completedTasks / filteredTasks.length * 100) : "0%"}</div><div className="cs-health-note">{activeTasks.length} active · {completedTasks} completed</div><div className="cs-bars"><div className="cs-bar"><span>Active</span><div className="cs-track"><div className="cs-fill" style={{width:`${filteredTasks.length ? activeTasks.length/filteredTasks.length*100 : 0}%`}}/></div><b>{activeTasks.length}</b></div><div className="cs-bar"><span>Completed</span><div className="cs-track"><div className="cs-fill" style={{width:`${filteredTasks.length ? completedTasks/filteredTasks.length*100 : 0}%`}}/></div><b>{completedTasks}</b></div></div></div><div className="cs-health-card"><div className="cs-health-label">Information control</div><div className="cs-health-value">{filteredDocuments.length ? pct(approvedDocuments / filteredDocuments.length * 100) : "0%"}</div><div className="cs-health-note">Approved documents · {openRfis.length} open RFIs</div><div className="cs-bars"><div className="cs-bar"><span>Approved</span><div className="cs-track"><div className="cs-fill" style={{width:`${filteredDocuments.length ? approvedDocuments/filteredDocuments.length*100 : 0}%`}}/></div><b>{approvedDocuments}</b></div><div className="cs-bar"><span>Open RFIs</span><div className="cs-track"><div className="cs-fill warn" style={{width:`${Math.min(100,openRfis.length*10)}%`}}/></div><b>{openRfis.length}</b></div></div></div></section>
        <section className="cs-grid"><div className="cs-panel"><div className="cs-title"><strong>{selectedProject ? "Project control snapshot" : "Portfolio snapshot"}</strong><span>{projects.length} project records</span></div><table className="cs-table"><thead><tr><th>Project</th><th>Status</th><th>Progress</th><th>BOQ</th><th>RFIs</th></tr></thead><tbody>{projects.filter(p => !selectedProject || p.id === selectedProject.id).map(p => { const pp = projectProgress.get(p.id)?.progress || 0; const pc = summary.commercialByProject?.find(x => x.projectId === p.id); const pr = rfis.filter(r => r.projectId === p.id && !["closed","answered","completed"].includes((r.status || "").toLowerCase())).length; return <tr key={p.id}><td className="cs-project">{p.code || ""} {p.name || "Untitled"}</td><td><span className={`cs-pill ${statusClass(p.status)}`}>{label(p.status)}</span></td><td><div className="cs-progress"><div className="cs-mini"><i style={{width:`${pp}%`}}/></div><b>{pct(pp)}</b></div></td><td>{money(pc?.budget || 0)}</td><td>{pr}</td></tr>})}</tbody></table></div><div className="cs-panel"><div className="cs-title"><strong>Attention queue</strong><span>Live records</span></div><div className="cs-list">{openRfis.slice(0,5).map(r => <div className="cs-row" key={r.id}><div className="cs-row-main"><b>{r.rfiNumber || "RFI"} · {r.subject || "Untitled request"}</b><span>Information request requiring action</span></div><span className="cs-pill warning">{label(r.status)}</span></div>)}{!openRfis.length && <div className="cs-row"><div className="cs-row-main"><b>No open RFIs</b><span>The current scope has no outstanding information requests.</span></div><span className="cs-pill positive">Clear</span></div>}{activeTasks.slice(0,3).map(t => <div className="cs-row" key={`task-${t.id}`}><div className="cs-row-main"><b>{t.title || "Untitled task"}</b><span>Task · {label(t.priority)}</span></div><span className={`cs-pill ${statusClass(t.status)}`}>{label(t.status)}</span></div>)}</div></div></section>
        <section className="cs-modules">{[["Projects","/projects","Portfolio"],["Documents","/documents","Information"],["Drawings","/drawings","Design register"],["BOQ","/boq","Quantities"],["Procurement","/procurement","Purchasing"],["Construction","/construction","Execution"],["Cost Control","/cost-control","Commercial"],["RFIs","/rfis","Governance"]].map(([a,b,c]) => <Link className="cs-module" href={b} key={a}><b>{a}</b><span>{c}</span></Link>)}</section>
        <footer className="cs-foot"><span>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"})}` : "Loading live data"}</span><span>Creative Studios · Project Controls</span></footer>
      </div>
    </main>
  );
}
