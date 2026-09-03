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

async function json(response: Response) {
  const text = await response.text();
  try { return text ? JSON.parse(text) : {}; } catch { return {}; }
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
  const maxStatus = Math.max(1, ...Object.values(statusCounts));
  const maxType = Math.max(1, ...Object.values(typeCounts));

  const projectName = (id?: string | null, fallback?: string | null) => projects.find((p) => p.id === id)?.name || fallback || "Unassigned";

  return <main className="content standalone">
    <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>Documents</h1><p>Controlled project documents, revisions, status and document intelligence.</p></div><Link className="secondary-button" href="/">Dashboard</Link></header>

    {error && <div className="workspace-card"><strong>Database unavailable</strong><p>{error}</p><button className="primary-button" onClick={() => void load()}>Retry</button></div>}

    <section className="kpi-grid">
      <div className="kpi-card"><span>Total documents</span><strong>{documents.length}</strong></div>
      <div className="kpi-card"><span>Approved</span><strong>{statusCounts.Approved || 0}</strong></div>
      <div className="kpi-card"><span>Under review</span><strong>{statusCounts["Under Review"] || 0}</strong></div>
      <div className="kpi-card"><span>Active disciplines</span><strong>{new Set(documents.map((d) => d.discipline).filter(Boolean)).size}</strong></div>
    </section>

    <section className="analytics-grid">
      <div className="workspace-card"><div className="section-label">Status distribution</div><h2>Document status</h2>{Object.entries(statusCounts).length ? <div className="bar-list">{Object.entries(statusCounts).map(([key, value]) => <div className="bar-row" key={key}><span>{key}</span><div className="bar-track"><div className="bar-fill" style={{ width: `${(value / maxStatus) * 100}%` }} /></div><strong>{value}</strong></div>)}</div> : <p>No status data yet.</p>}</div>
      <div className="workspace-card"><div className="section-label">File classification</div><h2>Document types</h2>{Object.entries(typeCounts).length ? <div className="bar-list">{Object.entries(typeCounts).map(([key, value]) => <div className="bar-row" key={key}><span>{key}</span><div className="bar-track"><div className="bar-fill" style={{ width: `${(value / maxType) * 100}%` }} /></div><strong>{value}</strong></div>)}</div> : <p>No file type data yet.</p>}</div>
    </section>

    <section className="workspace-card">
      <div className="list-toolbar"><div><div className="section-label">Document register</div><h2>{filtered.length} records</h2></div><div className="toolbar-actions"><input placeholder="Search title, project, discipline..." value={search} onChange={(e) => setSearch(e.target.value)} /> <select value={status} onChange={(e) => setStatus(e.target.value)}>{statuses.map((item) => <option key={item}>{item}</option>)}</select></div></div>
      <div className="table-wrap"><table><thead><tr><th>Title</th><th>Project</th><th>Discipline</th><th>Type</th><th>Revision</th><th>Status</th><th>Updated</th></tr></thead><tbody>{filtered.map((doc) => <tr key={doc.id}><td><strong>{doc.title || "Untitled"}</strong><div className="muted-cell">{doc.fileName || doc.file_name || ""}</div></td><td>{projectName(doc.projectId, doc.project)}</td><td>{doc.discipline || "Unspecified"}</td><td>{doc.documentType || doc.document_type || "Other"}</td><td>v{doc.version || 1}</td><td><span className="status-badge">{doc.status || "Draft"}</span></td><td>{String(doc.updatedAt || doc.updated_at || "").slice(0, 10)}</td></tr>)}</tbody></table></div>
      {!loading && !filtered.length && <div className="empty-state">No documents match the current filters.</div>}
    </section>

    <style jsx>{` .analytics-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:16px}.bar-list{display:grid;gap:12px;margin-top:18px}.bar-row{display:grid;grid-template-columns:120px 1fr 28px;align-items:center;gap:10px;font-size:13px}.bar-track{height:9px;border-radius:99px;background:#eef2f7;overflow:hidden}.bar-fill{height:100%;border-radius:99px;background:#111827}.toolbar-actions{display:flex;gap:8px;align-items:center}.toolbar-actions input,.toolbar-actions select{min-width:180px;padding:9px 10px;border:1px solid #dbe2ea;border-radius:8px;background:#fff}.table-wrap{overflow-x:auto;margin-top:14px}.table-wrap table{width:100%;border-collapse:collapse;font-size:12px}.table-wrap th,.table-wrap td{text-align:left;padding:11px 10px;border-bottom:1px solid #edf0f3;white-space:nowrap}.table-wrap th{font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.05em}.muted-cell{font-size:10px;color:#9ca3af;margin-top:3px}.status-badge{display:inline-block;padding:4px 7px;border:1px solid #d7dde5;border-radius:999px;background:#f8fafc;color:#374151;font-size:10px}.empty-state{padding:30px;text-align:center;color:#6b7280}.workspace-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px}.kpi-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:16px}.kpi-card{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:15px}.kpi-card span{display:block;color:#6b7280;font-size:11px}.kpi-card strong{display:block;margin-top:7px;font-size:24px;color:#111827}.section-label{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#9ca3af;font-weight:700}.workspace-card h2{margin:5px 0 0;font-size:17px;color:#111827}.topbar{display:flex;justify-content:space-between;gap:16px;align-items:flex-end;margin-bottom:16px}.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#6b7280}.topbar h1{margin:4px 0;font-size:30px;color:#111827}.topbar p{margin:0;color:#6b7280}.secondary-button,.primary-button{display:inline-block;padding:9px 12px;border-radius:8px;border:1px solid #d1d5db;background:#fff;color:#111827;text-decoration:none;font-size:12px;font-weight:700}.primary-button{background:#111827;color:#fff;border-color:#111827}.standalone{max-width:1480px;margin:0 auto;padding:24px 20px 50px}@media(max-width:900px){.analytics-grid,.kpi-grid{grid-template-columns:1fr 1fr}.topbar{align-items:flex-start}.toolbar-actions{flex-direction:column;align-items:stretch}}@media(max-width:620px){.analytics-grid,.kpi-grid{grid-template-columns:1fr}.topbar{flex-direction:column}.toolbar-actions{width:100%}.toolbar-actions input,.toolbar-actions select{width:100%;min-width:0}.bar-row{grid-template-columns:90px 1fr 24px}}`}</style>
  </main>;
}
