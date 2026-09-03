"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type DocumentRow = {
  id: string;
  projectId?: string | null;
  title?: string | null;
  project?: string | null;
  discipline?: string | null;
  documentType?: string | null;
  document_type?: string | null;
  status?: string | null;
  version?: number | null;
  fileName?: string | null;
  file_name?: string | null;
  updatedAt?: string | null;
  updated_at?: string | null;
};

type Project = { id: string; name: string; code: string };

const CHART_COLORS = ["#2563EB", "#111827", "#64748B", "#CBD5E1", "#94A3B8"];

async function json(response: Response) {
  const text = await response.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {}; }
}

function donutStops(counts: Record<string, number>) {
  const total = Math.max(Object.values(counts).reduce((sum, value) => sum + value, 0), 1);
  let cursor = 0;
  return Object.entries(counts).slice(0, 5).map(([key, value], index) => {
    const start = cursor;
    cursor += (value / total) * 360;
    return `${CHART_COLORS[index % CHART_COLORS.length]} ${start}deg ${cursor}deg`;
  }).join(", ");
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRow[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const [docsResponse, projectsResponse] = await Promise.all([
        fetch("/api/workspace?module=documents", { cache: "no-store" }),
        fetch("/api/projects", { cache: "no-store" }),
      ]);
      const docs = await json(docsResponse);
      const projectData = await json(projectsResponse);
      if (!docsResponse.ok) throw new Error(docs.error || "Unable to load documents.");
      setDocuments(Array.isArray(docs.data) ? docs.data : []);
      setProjects(Array.isArray(projectData.data) ? projectData.data : []);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load documents.");
    } finally { setLoading(false); }
  };

  useEffect(() => { void load(); }, []);

  const filtered = useMemo(() => documents.filter((doc) => {
    const haystack = Object.values(doc).join(" ").toLowerCase();
    return (!search || haystack.includes(search.toLowerCase())) && (status === "All" || (doc.status || "Draft") === status);
  }), [documents, search, status]);

  const statuses = useMemo(() => Array.from(new Set(["All", ...documents.map((d) => d.status || "Draft")])), [documents]);
  const statusCounts = useMemo(() => documents.reduce<Record<string, number>>((acc, doc) => { const key = doc.status || "Draft"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [documents]);
  const typeCounts = useMemo(() => documents.reduce<Record<string, number>>((acc, doc) => { const key = doc.documentType || doc.document_type || "Other"; acc[key] = (acc[key] || 0) + 1; return acc; }, {}), [documents]);
  const projectCount = useMemo(() => new Set(documents.map((d) => d.projectId).filter(Boolean)).size, [documents]);

  const projectName = (id?: string | null, fallback?: string | null) => projects.find((p) => p.id === id)?.name || fallback || "Unassigned";

  return <main className="content standalone">
    <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>Documents</h1><p>Controlled project documents, revisions, status and document intelligence.</p></div><Link className="secondary-button" href="/">Dashboard</Link></header>

    {error && <div className="workspace-card"><strong>Database unavailable</strong><p>{error}</p><button className="primary-button" onClick={() => void load()}>Retry</button></div>}

    <section className="kpi-grid">
      <div className="kpi-card"><span>Total documents</span><strong>{documents.length}</strong></div>
      <div className="kpi-card"><span>Approved</span><strong>{statusCounts.Approved || 0}</strong></div>
      <div className="kpi-card"><span>Under review</span><strong>{statusCounts["Under Review"] || 0}</strong></div>
      <div className="kpi-card"><span>Projects represented</span><strong>{projectCount}</strong></div>
    </section>

    <section className="analytics-grid">
      <div className="workspace-card analytics-card"><div className="section-label">Status distribution</div><h2>Document status</h2><div className="donut-layout"><div className="donut" style={{ background: `conic-gradient(${donutStops(statusCounts) || "#CBD5E1 0deg 360deg"})` }}><div><strong>{documents.length}</strong><span>Total</span></div></div><div className="legend">{Object.entries(statusCounts).slice(0, 5).map(([key, value], index) => <div className="legend-row" key={key}><i style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} /><span>{key}</span><strong>{value}</strong></div>)}</div>{!documents.length && <p>No status data yet.</p>}</div></div>
      <div className="workspace-card analytics-card"><div className="section-label">File classification</div><h2>Document types</h2><div className="donut-layout"><div className="donut" style={{ background: `conic-gradient(${donutStops(typeCounts) || "#CBD5E1 0deg 360deg"})` }}><div><strong>{documents.length}</strong><span>Total</span></div></div><div className="legend">{Object.entries(typeCounts).slice(0, 5).map(([key, value], index) => <div className="legend-row" key={key}><i style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} /><span>{key}</span><strong>{value}</strong></div>)}</div>{!documents.length && <p>No file type data yet.</p>}</div></div>
    </section>

    <section className="workspace-card">
      <div className="list-toolbar"><div><div className="section-label">Document register</div><h2>{filtered.length} records</h2></div><div className="toolbar-actions"><input placeholder="Search title, project, discipline..." value={search} onChange={(e) => setSearch(e.target.value)} /> <select value={status} onChange={(e) => setStatus(e.target.value)}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></div></div>
      <div className="table-wrap"><table><thead><tr><th>Title</th><th>Project</th><th>Discipline</th><th>Type</th><th>Revision</th><th>Status</th><th>Updated</th></tr></thead><tbody>{filtered.map((doc) => <tr key={doc.id}><td><strong>{doc.title || "Untitled"}</strong><div className="muted-cell">{doc.fileName || doc.file_name || ""}</div></td><td>{projectName(doc.projectId, doc.project)}</td><td>{doc.discipline || "Unspecified"}</td><td>{doc.documentType || doc.document_type || "Other"}</td><td>v{doc.version || 1}</td><td><span className="status-badge">{doc.status || "Draft"}</span></td><td>{String(doc.updatedAt || doc.updated_at || "").slice(0, 10)}</td></tr>)}</tbody></table></div>
      {!loading && !filtered.length && <div className="empty-state">No documents match the current filters.</div>}
    </section>

    <style jsx>{` .analytics-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-bottom:12px}.analytics-card{min-height:245px}.donut-layout{display:flex;align-items:center;gap:22px;margin-top:18px}.donut{width:150px;height:150px;border-radius:50%;display:grid;place-items:center;flex:0 0 auto}.donut>div{width:84px;height:84px;border-radius:50%;background:#fff;display:grid;place-items:center;align-content:center;text-align:center}.donut strong{font-size:20px;line-height:1.1;color:#111827}.donut span{font-size:10px;color:#64748b;margin-top:3px}.legend{display:grid;gap:10px;min-width:150px}.legend-row{display:grid;grid-template-columns:8px 1fr auto;align-items:center;gap:7px;font-size:11px;color:#64748b}.legend-row i{width:8px;height:8px;border-radius:50%}.legend-row strong{color:#111827;font-size:11px}.bar-list{display:grid;gap:12px;margin-top:18px}.bar-row{display:grid;grid-template-columns:120px 1fr 28px;align-items:center;gap:10px;font-size:13px}.bar-track{height:9px;border-radius:99px;background:#eef2f7;overflow:hidden}.bar-fill{height:100%;border-radius:99px;background:#111827}.toolbar-actions{display:flex;gap:8px;align-items:center}.toolbar-actions input,.toolbar-actions select{min-width:180px;padding:9px 10px;border:1px solid #dbe2ea;border-radius:8px;background:#fff;color:#111827}.table-wrap{overflow-x:auto;margin-top:14px}.table-wrap table{width:100%;border-collapse:collapse;font-size:12px}.table-wrap th,.table-wrap td{text-align:left;padding:11px 10px;border-bottom:1px solid #edf0f3;white-space:nowrap}.table-wrap th{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em}.muted-cell{font-size:10px;color:#9ca3af;margin-top:3px}.status-badge{display:inline-block;padding:4px 7px;border:1px solid #bfdbfe;border-radius:999px;background:#eff6ff;color:#2563eb;font-size:10px;font-weight:700}.empty-state{padding:30px;text-align:center;color:#64748b}.workspace-card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px}.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-bottom:12px}.kpi-card{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:14px;min-height:82px}.kpi-card span{display:block;color:#64748b;font-size:10px}.kpi-card strong{display:block;margin-top:7px;font-size:22px;color:#111827}.section-label{font-size:9px;text-transform:uppercase;letter-spacing:.1em;color:#2563eb;font-weight:700}.workspace-card h2{margin:5px 0 0;font-size:16px;color:#111827}.topbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;margin-bottom:14px}.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#2563eb}.topbar h1{margin:4px 0;font-size:28px;color:#111827}.topbar p{margin:0;color:#64748b}.secondary-button,.primary-button{display:inline-block;padding:9px 12px;border-radius:8px;border:1px solid #d1d5db;background:#fff;color:#111827;text-decoration:none;font-size:12px;font-weight:700}.primary-button{background:#111827;color:#fff;border-color:#111827}.standalone{max-width:1480px;margin:0 auto;padding:24px 20px 50px}@media(max-width:900px){.analytics-grid,.kpi-grid{grid-template-columns:1fr 1fr}.topbar{align-items:flex-start}.toolbar-actions{flex-direction:column;align-items:stretch}.donut-layout{gap:14px}}@media(max-width:620px){.analytics-grid,.kpi-grid{grid-template-columns:1fr}.topbar{flex-direction:column}.toolbar-actions{width:100%}.toolbar-actions input,.toolbar-actions select{width:100%;min-width:0}.donut-layout{justify-content:center;flex-wrap:wrap}.legend{min-width:180px}}`}</style>
  </main>;
}
