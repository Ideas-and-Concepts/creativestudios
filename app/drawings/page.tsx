"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Discipline = "architectural" | "structural";
type Status = "draft" | "in_review" | "approved" | "issued" | "superseded";
type Drawing = { id: string; projectId: string; drawingNumber: string; title: string; discipline: Discipline; revision: string; status: Status; fileUrl: string | null; createdAt: string; updatedAt: string };
type Project = { id: string; code: string; name: string };
type FormState = { projectId: string; drawingNumber: string; title: string; discipline: Discipline; revision: string; status: Status; fileUrl: string };

const disciplines: Discipline[] = ["architectural", "structural"];
const statuses: Status[] = ["draft", "in_review", "approved", "issued", "superseded"];
const disciplineLabel: Record<Discipline, string> = { architectural: "Architectural", structural: "Structural" };
const statusLabel: Record<Status, string> = { draft: "Draft", in_review: "In review", approved: "Approved", issued: "Issued", superseded: "Superseded" };
const emptyForm: FormState = { projectId: "", drawingNumber: "", title: "", discipline: "architectural", revision: "A", status: "draft", fileUrl: "" };

function formatDate(value: string) { const d = new Date(value); return Number.isNaN(d.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(d); }

export default function DrawingsPage() {
  const [projects, setProjects] = useState<Project[]>([]); const [drawings, setDrawings] = useState<Drawing[]>([]); const [form, setForm] = useState<FormState>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null); const [query, setQuery] = useState(""); const [filterProject, setFilterProject] = useState("all"); const [filterDiscipline, setFilterDiscipline] = useState<"all" | Discipline>("all"); const [filterStatus, setFilterStatus] = useState<"all" | Status>("all");
  const [loading, setLoading] = useState(true); const [saving, setSaving] = useState(false); const [error, setError] = useState(""); const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [p, d] = await Promise.all([fetch("/api/projects", { cache: "no-store" }), fetch("/api/drawings", { cache: "no-store" })]);
      const pd = await p.json(); const dd = await d.json(); if (!p.ok) throw new Error(pd.error ?? "Unable to load projects."); if (!d.ok) throw new Error(dd.error ?? "Unable to load drawings.");
      const rows = Array.isArray(pd.data) ? pd.data : []; setProjects(rows); setDrawings(Array.isArray(dd.data) ? dd.data : []);
      if (!form.projectId && rows[0]?.id) setForm((current) => ({ ...current, projectId: rows[0].id }));
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load drawings."); } finally { setLoading(false); }
  }, [form.projectId]);
  useEffect(() => { void load(); }, [load]);

  const filtered = useMemo(() => { const q = query.trim().toLowerCase(); return drawings.filter((d) => (filterProject === "all" || d.projectId === filterProject) && (filterDiscipline === "all" || d.discipline === filterDiscipline) && (filterStatus === "all" || d.status === filterStatus) && (!q || `${d.drawingNumber} ${d.title} ${d.revision}`.toLowerCase().includes(q))); }, [drawings, filterProject, filterDiscipline, filterStatus, query]);
  const projectName = (id: string) => projects.find((p) => p.id === id)?.name ?? "Unknown project";
  const projectCode = (id: string) => projects.find((p) => p.id === id)?.code ?? "Unknown";
  const reset = () => { setForm(projects[0]?.id ? { ...emptyForm, projectId: projects[0].id } : emptyForm); setEditingId(null); };

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const response = await fetch(editingId ? `/api/drawings/${editingId}` : "/api/drawings", { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, fileUrl: form.fileUrl || null }) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to save drawing."); setMessage(editingId ? "Drawing updated successfully." : "Drawing registered successfully."); reset(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save drawing."); } finally { setSaving(false); }
  }

  function edit(d: Drawing) { setEditingId(d.id); setForm({ projectId: d.projectId, drawingNumber: d.drawingNumber, title: d.title, discipline: d.discipline, revision: d.revision, status: d.status, fileUrl: d.fileUrl ?? "" }); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); }
  async function remove(d: Drawing) { if (!window.confirm(`Delete drawing ${d.drawingNumber} - ${d.title}?`)) return; setError(""); setMessage(""); try { const r = await fetch(`/api/drawings/${d.id}`, { method: "DELETE" }); const data = await r.json(); if (!r.ok) throw new Error(data.error ?? "Unable to delete drawing."); setMessage("Drawing deleted successfully."); if (editingId === d.id) reset(); await load(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete drawing."); } }

  const architectural = drawings.filter((d) => d.discipline === "architectural").length; const structural = drawings.filter((d) => d.discipline === "structural").length; const issued = drawings.filter((d) => d.status === "issued").length;

  return <main className="projects-page drawings-page">
    <header className="projects-header"><div><div className="eyebrow">Creative Studios / Drawings</div><h1>Drawings</h1><p>Controlled project drawing register for architectural and structural documentation.</p></div><a className="back-link" href="/">Dashboard</a></header>
    <section className="project-stats"><div className="project-stat"><span>Total drawings</span><strong>{drawings.length}</strong></div><div className="project-stat"><span>Architectural</span><strong>{architectural}</strong></div><div className="project-stat"><span>Structural</span><strong>{structural}</strong></div><div className="project-stat"><span>Issued</span><strong>{issued}</strong></div></section>
    {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}
    {projects.length === 0 && !loading ? <section className="project-empty"><strong>Create a project first</strong><span>Drawings must belong to a project. Create the project record before registering drawings.</span><a className="back-link" href="/projects">Open Projects</a></section> : <section className="project-layout">
      <form className="project-form" onSubmit={submit}><div className="section-label">{editingId ? "Edit drawing" : "Register drawing"}</div><h2>{editingId ? "Update drawing" : "New drawing"}</h2><p>Drawing records remain linked to their project throughout the delivery lifecycle.</p><div className="form-grid">
        <label>Project<select value={form.projectId} onChange={(e) => setForm({ ...form, projectId: e.target.value })} required><option value="" disabled>Select project</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.name}</option>)}</select></label>
        <label>Drawing number<input value={form.drawingNumber} onChange={(e) => setForm({ ...form, drawingNumber: e.target.value })} placeholder="A-101" required maxLength={100} /></label>
        <label className="full-width">Drawing title<input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="Ground Floor Plan" required maxLength={250} /></label>
        <label>Discipline<select value={form.discipline} onChange={(e) => setForm({ ...form, discipline: e.target.value as Discipline })}>{disciplines.map((d) => <option key={d} value={d}>{disciplineLabel[d]}</option>)}</select></label>
        <label>Revision<input value={form.revision} onChange={(e) => setForm({ ...form, revision: e.target.value })} placeholder="A" required maxLength={20} /></label>
        <label>Status<select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as Status })}>{statuses.map((s) => <option key={s} value={s}>{statusLabel[s]}</option>)}</select></label>
        <label className="full-width">File URL<input type="url" value={form.fileUrl} onChange={(e) => setForm({ ...form, fileUrl: e.target.value })} placeholder="https://..." maxLength={2000} /></label>
      </div><div className="form-actions">{editingId && <button type="button" className="secondary-button" onClick={reset}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingId ? "Save changes" : "Register drawing"}</button></div></form>
      <section className="project-list-panel"><div className="list-toolbar"><div><div className="section-label">Drawing register</div><h2>{filtered.length} drawing{filtered.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
        <div className="filters"><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search drawing number or title" aria-label="Search drawings" /><select value={filterProject} onChange={(e) => setFilterProject(e.target.value)}><option value="all">All projects</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.code}</option>)}</select><select value={filterDiscipline} onChange={(e) => setFilterDiscipline(e.target.value as "all" | Discipline)}><option value="all">All disciplines</option>{disciplines.map((d) => <option key={d} value={d}>{disciplineLabel[d]}</option>)}</select><select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value as "all" | Status)}><option value="all">All statuses</option>{statuses.map((s) => <option key={s} value={s}>{statusLabel[s]}</option>)}</select></div>
        {loading ? <div className="project-empty"><strong>Loading drawing register...</strong><span>Reading project drawing records.</span></div> : filtered.length === 0 ? <div className="project-empty"><strong>No drawings found</strong><span>Register a drawing or adjust the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Number</th><th>Title</th><th>Project</th><th>Discipline</th><th>Revision</th><th>Status</th><th>Updated</th><th /></tr></thead><tbody>{filtered.map((d) => <tr key={d.id}><td><strong>{d.drawingNumber}</strong></td><td><div className="project-name">{d.title}</div>{d.fileUrl && <div className="project-description">File linked</div>}</td><td><strong>{projectCode(d.projectId)}</strong><div className="project-description">{projectName(d.projectId)}</div></td><td>{disciplineLabel[d.discipline]}</td><td>{d.revision}</td><td><span className={`project-status ${d.status}`}>{statusLabel[d.status]}</span></td><td>{formatDate(d.updatedAt)}</td><td><div className="row-actions"><button onClick={() => edit(d)}>Edit</button><button className="danger-link" onClick={() => void remove(d)}>Delete</button></div></td></tr>)}</tbody></table></div>}
      </section></section>}
  </main>;
}
