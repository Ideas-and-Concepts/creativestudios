"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

type Project = { id: string; code?: string; name?: string; status?: string };
type Document = { id: string; title?: string; documentType?: string; revision?: string | null; createdAt?: string; projectId?: string | null; isApproved?: boolean };
type Task = { id: string; title?: string; status?: string; priority?: string };
type Rfi = { id: string; rfiNumber?: string; subject?: string; status?: string };
type Summary = {
  projects: number; drawings: number; boqItems: number; activeWorks: number; boqValue?: number; averageProgress?: number;
  domainProgress?: { architecture?: number; engineering?: number; mep?: number; construction?: number };
  projectProgress?: { projectId: string; progress: number; activityCount: number }[];
  commercial?: { budget?: number; committed?: number; actual?: number; earnedValue?: number; forecast?: number; variance?: number; cpi?: number | null; budgetUtilisation?: number };
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

  const selectedProject = projects.find(p => (p.name || p.code || "Untitled") === projectFilter);
  const filteredProjectIds = selectedProject ? new Set([selectedProject.id]) : null;
  const filteredDocuments = filteredProjectIds ? documents.filter(d => filteredProjectIds.has(d.projectId || "")) : documents;
  const projectProgress = useMemo(() => new Map((summary.projectProgress || []).map(x => [x.projectId, x])), [summary.projectProgress]);
  const commercial = summary.commercial || {};
  const activeTasks = tasks.filter(t => ["open", "in_progress", "review"].includes((t.status || "").toLowerCase()));
  const openRfis = rfis.filter(r => !["closed", "answered", "completed"].includes((r.status || "").toLowerCase()));
  const completedTasks = tasks.filter(t => ["completed", "closed"].includes((t.status || "").toLowerCase())).length;
  const approvedDocuments = filteredDocuments.filter(d => d.isApproved).length;
  const domains = summary.domainProgress || {};
  const designProgress = Math.round((Number(domains.architecture || 0) + Number(domains.engineering || 0)) / 2);
  const constructionProgress = Number(domains.construction || 0);
  const overallProgress = Number(summary.averageProgress || 0);
  const budget = Number(commercial.budget || summary.boqValue || 0);
  const committed = Number(commercial.committed || 0);
  const actual = Number(commercial.actual || 0);
  const ev = Number(commercial.earnedValue || 0);
  const forecast = Number(commercial.forecast || 0);
  const variance = Number(commercial.variance || 0);
  const cpi = commercial.cpi == null ? null : Number(commercial.cpi);
  const utilisation = Number(commercial.budgetUtilisation || 0);

  return (
    <main className="cs-exec">
      <style>{`
        .cs-exec{min-height:100vh;background:#f5f7fa;color:#0f172a;padding:78px 22px 34px}.cs-wrap{max-width:1500px;margin:auto}.cs-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:14px}.cs-eyebrow{font-size:9px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#64748b}.cs-head h1{font-size:27px;letter-spacing:-.04em;margin:4px 0;font-weight:850}.cs-head p{margin:0;color:#64748b;font-size:10px}.cs-actions{display:flex;gap:7px;align-items:center;flex-wrap:wrap}.cs-select,.cs-btn,.cs-link{height:33px;border:1px solid #dce2e9;border-radius:8px;background:#fff;color:#334155;padding:0 10px;font-size:9px;font-weight:700;text-decoration:none}.cs-btn{cursor:pointer}.cs-health{height:33px;display:flex;align-items:center;gap:6px;border:1px solid #dce2e9;border-radius:8px;background:#fff;padding:0 10px;color:#64748b;font-size:8px}.cs-health i{width:7px;height:7px;border-radius:50%;background:#94a3b8}.cs-health i.ready{background:#22c55e}.cs-kpis{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-bottom:9px}.cs-kpi,.cs-panel{background:#fff;border:1px solid #e1e6ec;border-radius:11px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-kpi{padding:11px;min-height:82px}.cs-kpi small{font-size:8px;color:#64748b}.cs-kpi strong{display:block;font-size:19px;letter-spacing:-.025em;margin-top:7px}.cs-kpi span{font-size:7px;color:#94a3b8}.cs-commercial{display:grid;grid-template-columns:1.45fr .8fr;gap:9px;margin-bottom:9px}.cs-panel{padding:13px}.cs-title{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}.cs-title strong{font-size:10px}.cs-title span{font-size:7px;color:#94a3b8}.cs-money-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.cs-money{border:1px solid #edf0f4;border-radius:9px;padding:10px}.cs-money small{display:block;font-size:7px;color:#64748b}.cs-money b{display:block;font-size:15px;margin-top:6px}.cs-money em{display:block;font-style:normal;font-size:7px;color:#94a3b8;margin-top:3px}.cs-meter{margin-top:12px}.cs-meter-top{display:flex;justify-content:space-between;font-size:8px;color:#64748b;margin-bottom:5px}.cs-track{height:8px;border-radius:99px;background:#edf1f5;overflow:hidden}.cs-fill{height:100%;border-radius:99px;background:#3b82f6}.cs-fill.warn{background:#f59e0b}.cs-eval{display:grid;grid-template-columns:repeat(3,1fr);gap:7px}.cs-eval-card{border:1px solid #edf0f4;border-radius:9px;padding:10px;text-align:center}.cs-eval-card small{display:block;font-size:7px;color:#64748b}.cs-eval-card b{font-size:18px;display:block;margin-top:6px}.cs-eval-card span{font-size:7px;color:#94a3b8}.cs-positive{color:#15803d}.cs-warning{color:#b45309}.cs-neutral{color:#334155}.cs-health-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-bottom:9px}.cs-health-card{border:1px solid #e1e6ec;border-radius:11px;background:#fff;padding:12px}.cs-health-label{font-size:8px;color:#64748b}.cs-health-value{font-size:18px;font-weight:800;margin-top:6px}.cs-health-note{font-size:7px;color:#94a3b8;margin-top:3px}.cs-bars{margin-top:12px;display:grid;gap:8px}.cs-bar{display:grid;grid-template-columns:92px 1fr 32px;gap:7px;align-items:center;font-size:7px;color:#64748b}.cs-bar .cs-track{height:7px}.cs-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}.cs-list{display:grid;gap:7px}.cs-row{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #f0f2f5;font-size:8px}.cs-row:last-child{border-bottom:0}.cs-row-main{min-width:0}.cs-row-main b{display:block;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.cs-row-main span{display:block;color:#94a3b8;font-size:7px;margin-top:2px}.cs-pill{padding:4px 6px;border-radius:999px;background:#f1f5f9;color:#475569;font-size:7px;font-weight:750;white-space:nowrap}.cs-pill.info{background:#eff6ff;color:#2563eb}.cs-pill.positive{background:#ecfdf5;color:#15803d}.cs-pill.warning{background:#fffbeb;color:#b45309}.cs-table{width:100%;border-collapse:collapse;font-size:8px}.cs-table th{text-align:left;color:#94a3b8;font-size:7px;padding:7px;border-bottom:1px solid #e9edf1}.cs-table td{padding:8px 7px;border-bottom:1px solid #f0f2f5;color:#334155}.cs-project{font-weight:750;color:#0f172a}.cs-progress{display:grid;grid-template-columns:1fr 30px;gap:6px;align-items:center;min-width:120px}.cs-mini{height:6px;border-radius:99px;background:#edf1f5;overflow:hidden}.cs-mini i{display:block;height:100%;background:#3b82f6}.cs-modules{display:grid;grid-template-columns:repeat(8,1fr);gap:7px;margin-top:9px}.cs-module{border:1px solid #e1e6ec;background:#fff;border-radius:9px;padding:10px;text-decoration:none;color:#334155}.cs-module b{font-size:8px}.cs-module span{display:block;font-size:7px;color:#94a3b8;margin-top:4px}.cs-foot{display:flex;justify-content:space-between;margin-top:9px;color:#94a3b8;font-size:7px}@media(max-width:1050px){.cs-kpis{grid-template-columns:repeat(3,1fr)}.cs-commercial,.cs-grid{grid-template-columns:1fr}.cs-modules{grid-template-columns:repeat(4,1fr)}}@media(max-width:650px){.cs-exec{padding:72px 10px 20px}.cs-head{align-items:flex-start;flex-direction:column}.cs-kpis{grid-template-columns:repeat(2,1fr)}.cs-money-grid,.cs-health-grid{grid-template-columns:1fr 1fr}.cs-modules{grid-template-columns:repeat(2,1fr)}.cs-eval{grid-template-columns:1fr 1fr 1fr}.cs-panel{padding:10px}}
      `}</style>

      <div className="cs-wrap">
        <header className="cs-head">
          <div><div className="cs-eyebrow">Creative Studios · Executive Workspace</div><h1>Project Controls Dashboard</h1><p>Live portfolio, delivery, commercial and earned-value intelligence.</p></div>
          <div className="cs-actions">
            <select className="cs-select" value={projectFilter} onChange={e => setProjectFilter(e.target.value)}><option>All Projects</option>{projects.map(p => <option key={p.id}>{p.name || p.code || "Untitled"}</option>)}</select>
            <button className="cs-btn" onClick={() => void refresh()}>{loading ? "Refreshing…" : "Refresh"}</button>
            <span className="cs-health"><i className={databaseReady ? "ready" : ""} />{databaseReady ? "Database connected" : "Database unavailable"}</span>
          </div>
        </header>

        <section className="cs-kpis">
          {[["Projects", summary.projects, "Portfolio"],["Active Work", summary.activeWorks, "Execution"],["Work Progress", pct(overallProgress), "Actual construction / work data"],["BOQ Value", money(budget), `${summary.boqItems} items`],["Drawings", summary.drawings, "Controlled register"],["Open RFIs", openRfis.length, "Attention queue"]].map(([a,b,c]) => <div className="cs-kpi" key={String(a)}><small>{a}</small><strong>{b}</strong><span>{c}</span></div>)}
        </section>

        <section className="cs-commercial">
          <div className="cs-panel">
            <div className="cs-title"><strong>Commercial Position</strong><span>BOQ → Procurement → Actual Cost → Forecast</span></div>
            <div className="cs-money-grid">
              <div className="cs-money"><small>Budget / BAC</small><b>{money(budget)}</b><em>Approved BOQ basis</em></div>
              <div className="cs-money"><small>Committed</small><b>{money(committed)}</b><em>Non-draft procurement</em></div>
              <div className="cs-money"><small>Actual Cost</small><b>{money(actual)}</b><em>Recorded actuals</em></div>
              <div className="cs-money"><small>Forecast / EAC</small><b>{money(forecast)}</b><em>Current completion forecast</em></div>
            </div>
            <div className="cs-meter"><div className="cs-meter-top"><span>Actual budget utilisation</span><b>{pct(utilisation)}</b></div><div className="cs-track"><div className={`cs-fill ${utilisation > 100 ? "warn" : ""}`} style={{width:`${Math.min(100, Math.max(0, utilisation))}%`}} /></div></div>
          </div>
          <div className="cs-panel">
            <div className="cs-title"><strong>Earned Value</strong><span>Live EVM signal</span></div>
            <div className="cs-eval">
              <div className="cs-eval-card"><small>EV</small><b>{money(ev)}</b><span>Earned value</span></div>
              <div className="cs-eval-card"><small>CPI</small><b className={cpi != null && cpi < 1 ? "cs-warning" : "cs-positive"}>{cpi == null ? "—" : cpi.toFixed(2)}</b><span>{cpi == null ? "Insufficient actual cost" : cpi >= 1 ? "Cost efficient" : "Cost pressure"}</span></div>
              <div className="cs-eval-card"><small>VAC</small><b className={variance < 0 ? "cs-warning" : "cs-positive"}>{money(variance)}</b><span>Budget less EAC</span></div>
            </div>
          </div>
        </section>

        <section className="cs-health-grid">
          {[['Overall Delivery', overallProgress, 'Portfolio delivery signal'],['Design & Engineering', designProgress, 'Architecture + engineering'],['Construction', constructionProgress, 'Construction work records']].map(([name,value,note]) => <div className="cs-health-card" key={String(name)}><div className="cs-health-label">{name}</div><div className="cs-health-value">{pct(Number(value))}</div><div className="cs-track" style={{marginTop:8}}><div className="cs-fill" style={{width:`${Math.min(100, Math.max(0, Number(value)))}%`}} /></div><div className="cs-health-note">{note}</div></div>)}
        </section>

        <section className="cs-grid">
          <div className="cs-panel">
            <div className="cs-title"><strong>Project Portfolio</strong><span>{projects.length} projects</span></div>
            <div style={{overflowX:"auto"}}><table className="cs-table"><thead><tr><th>Project</th><th>Status</th><th>Progress</th><th>Activities</th></tr></thead><tbody>{projects.slice(0,12).map(p => { const row = projectProgress.get(p.id); const progress = row?.progress || 0; return <tr key={p.id}><td className="cs-project">{p.code ? `${p.code} · ` : ""}{p.name || "Untitled"}</td><td><span className={`cs-pill ${statusClass(p.status)}`}>{label(p.status)}</span></td><td><div className="cs-progress"><div className="cs-mini"><i style={{width:`${progress}%`}} /></div><b>{progress}%</b></div></td><td>{row?.activityCount || 0}</td></tr>; })}{!projects.length && <tr><td colSpan={4}>No projects available.</td></tr>}</tbody></table></div>
          </div>

          <div className="cs-panel">
            <div className="cs-title"><strong>Attention Queue</strong><span>Open actions</span></div>
            <div className="cs-list">
              {openRfis.slice(0,5).map(r => <div className="cs-row" key={r.id}><div className="cs-row-main"><b>{r.rfiNumber || "RFI"} · {r.subject || "Information request"}</b><span>RFI workflow</span></div><span className={`cs-pill ${statusClass(r.status)}`}>{label(r.status)}</span></div>)}
              {activeTasks.slice(0,5).map(t => <div className="cs-row" key={t.id}><div className="cs-row-main"><b>{t.title || "Task"}</b><span>Task · {label(t.priority)}</span></div><span className={`cs-pill ${statusClass(t.status)}`}>{label(t.status)}</span></div>)}
              {!openRfis.length && !activeTasks.length && <div className="cs-row"><div className="cs-row-main"><b>No open actions</b><span>The portfolio queue is clear.</span></div></div>}
            </div>
          </div>
        </section>

        <section className="cs-grid" style={{marginTop:9}}>
          <div className="cs-panel"><div className="cs-title"><strong>Document Control</strong><span>{approvedDocuments} approved · {filteredDocuments.length} visible</span></div><div className="cs-list">{filteredDocuments.slice(0,6).map(d => <div className="cs-row" key={d.id}><div className="cs-row-main"><b>{d.title || "Untitled document"}</b><span>{d.documentType || "Document"}{d.revision ? ` · Rev ${d.revision}` : ""}</span></div><span className={`cs-pill ${d.isApproved ? "positive" : "neutral"}`}>{d.isApproved ? "Approved" : "Controlled"}</span></div>)}{!filteredDocuments.length && <div className="cs-row"><div className="cs-row-main"><b>No documents</b><span>No controlled documents match the current scope.</span></div></div>}</div></div>
          <div className="cs-panel"><div className="cs-title"><strong>Workflow Pulse</strong><span>Operational throughput</span></div><div className="cs-bars"><div className="cs-bar"><span>Active tasks</span><div className="cs-track"><div className="cs-fill" style={{width:`${Math.min(100, activeTasks.length * 10)}%`}} /></div><b>{activeTasks.length}</b></div><div className="cs-bar"><span>Completed tasks</span><div className="cs-track"><div className="cs-fill" style={{width:`${Math.min(100, completedTasks * 10)}%`}} /></div><b>{completedTasks}</b></div><div className="cs-bar"><span>Approved docs</span><div className="cs-track"><div className="cs-fill" style={{width:`${filteredDocuments.length ? approvedDocuments / filteredDocuments.length * 100 : 0}%`}} /></div><b>{approvedDocuments}</b></div><div className="cs-bar"><span>Open RFIs</span><div className="cs-track"><div className="cs-fill warn" style={{width:`${Math.min(100, openRfis.length * 10)}%`}} /></div><b>{openRfis.length}</b></div></div></div>
        </section>

        <section className="cs-modules">{[["Projects","/projects","Portfolio"],["Documents","/documents","Document control"],["Drawings","/drawings","Design register"],["BOQ","/boq","Commercial basis"],["Procurement","/procurement","Commitments"],["Construction","/construction","Execution"],["Cost Control","/cost-control","EVM & costs"],["Reports","/reports","Reporting"]].map(([name,href,note]) => <Link className="cs-module" href={href} key={href}><b>{name}</b><span>{note}</span></Link>)}</section>
        <div className="cs-foot"><span>Creative Studios AEC Collaboration Platform</span><span>{lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : "Loading live data…"}</span></div>
      </div>
    </main>
  );
}
