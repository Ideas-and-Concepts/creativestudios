"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Status = "planned" | "in_progress" | "completed" | "on_hold";
type ConstructionActivity = {
  id: string;
  projectId: string;
  activityCode: string;
  name: string;
  discipline: string | null;
  status: Status;
  progress: number;
  plannedQuantity: string | number;
  actualQuantity: string | number;
  unit: string | null;
  notes: string | null;
  updatedAt: string;
};
type Project = { id: string; code: string; name: string };
type FormState = {
  projectId: string;
  activityCode: string;
  name: string;
  discipline: string;
  status: Status;
  progress: number;
  plannedQuantity: number;
  actualQuantity: number;
  unit: string;
  notes: string;
};

const statuses: Status[] = ["planned", "in_progress", "completed", "on_hold"];
const statusLabel: Record<Status, string> = { planned: "Planned", in_progress: "In progress", completed: "Completed", on_hold: "On hold" };
const disciplines = ["Site works", "Earthworks", "Foundations", "Concrete works", "Masonry", "Structural steel", "Roofing", "Finishes", "Doors and windows", "External works", "Roads and drainage", "MEP installation", "Testing and commissioning", "Other"];
const units = ["m3", "m2", "m", "kg", "t", "No.", "set", "lot", "item", "day", "hour"];
const emptyForm: FormState = { projectId: "", activityCode: "", name: "", discipline: "Site works", status: "planned", progress: 0, plannedQuantity: 0, actualQuantity: 0, unit: "m3", notes: "" };

function numberValue(value: string | number) { return Number(value ?? 0); }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date); }
function formatQuantity(value: string | number) { const n = numberValue(value); return new Intl.NumberFormat(undefined, { maximumFractionDigits: 3 }).format(n); }

export default function ConstructionPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [activities, setActivities] = useState<ConstructionActivity[]>([]);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [filterProject, setFilterProject] = useState("all");
  const [filterStatus, setFilterStatus] = useState<"all" | Status>("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [projectResponse, activityResponse] = await Promise.all([fetch("/api/projects", { cache: "no-store" }), fetch("/api/construction", { cache: "no-store" })]);
      const projectData = await projectResponse.json(); const activityData = await activityResponse.json();
      if (!projectResponse.ok) throw new Error(projectData.error ?? "Unable to load projects.");
      if (!activityResponse.ok) throw new Error(activityData.error ?? "Unable to load construction activities.");
      const projectRows = Array.isArray(projectData.data) ? projectData.data : [];
      setProjects(projectRows); setActivities(Array.isArray(activityData.data) ? activityData.data : []);
      if (!form.projectId && projectRows[0]?.id) setForm(current => ({ ...current, projectId: projectRows[0].id }));
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load construction data."); }
    finally { setLoading(false); }
  }, [form.projectId]);

  useEffect(() => { void load(); }, [load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return activities.filter(activity => {
      const projectMatch = filterProject === "all" || activity.projectId === filterProject;
      const statusMatch = filterStatus === "all" || activity.status === filterStatus;
      const text = `${activity.activityCode} ${activity.name} ${activity.discipline ?? ""} ${activity.unit ?? ""} ${activity.notes ?? ""}`.toLowerCase();
      return projectMatch && statusMatch && (!q || text.includes(q));
    });
  }, [activities, filterProject, filterStatus, query]);

  const reset = () => { setForm(projects[0]?.id ? { ...emptyForm, projectId: projects[0].id } : emptyForm); setEditingId(null); };
  const projectName = (id: string) => projects.find(project => project.id === id)?.name ?? "Unknown project";

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const response = await fetch(editingId ? `/api/construction/${editingId}` : "/api/construction", { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, progress: Number(form.progress), plannedQuantity: Number(form.plannedQuantity), actualQuantity: Number(form.actualQuantity), discipline: form.discipline || null, unit: form.unit || null, notes: form.notes || null }) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to save construction activity.");
      setMessage(editingId ? "Construction activity updated successfully." : "Construction activity created successfully."); reset(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save construction activity."); }
    finally { setSaving(false); }
  };

  const edit = (activity: ConstructionActivity) => { setEditingId(activity.id); setForm({ projectId: activity.projectId, activityCode: activity.activityCode, name: activity.name, discipline: activity.discipline ?? "", status: activity.status, progress: activity.progress, plannedQuantity: numberValue(activity.plannedQuantity), actualQuantity: numberValue(activity.actualQuantity), unit: activity.unit ?? "", notes: activity.notes ?? "" }); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const remove = async (activity: ConstructionActivity) => {
    if (!window.confirm(`Delete construction activity ${activity.activityCode} from ${projectName(activity.projectId)}?`)) return;
    setError(""); setMessage("");
    try { const response = await fetch(`/api/construction/${activity.id}`, { method: "DELETE" }); const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to delete construction activity."); setMessage("Construction activity deleted successfully."); if (editingId === activity.id) reset(); await load(); }
    catch (err) { setError(err instanceof Error ? err.message : "Unable to delete construction activity."); }
  };

  const inProgress = activities.filter(a => a.status === "in_progress").length;
  const completed = activities.filter(a => a.status === "completed").length;
  const averageProgress = activities.length ? Math.round(activities.reduce((sum, a) => sum + a.progress, 0) / activities.length) : 0;
  const plannedTotal = activities.reduce((sum, a) => sum + numberValue(a.plannedQuantity), 0);
  const actualTotal = activities.reduce((sum, a) => sum + numberValue(a.actualQuantity), 0);

  return <main className="projects-page construction-page">
    <header className="projects-header"><div><div className="eyebrow">Creative Studios / Construction</div><h1>Construction</h1><p>Track site execution against planned quantities, actual quantities and construction progress.</p></div><a className="back-link" href="/">Dashboard</a></header>
    <section className="project-stats" aria-label="Construction summary">
      <div className="project-stat"><span>Total activities</span><strong>{activities.length}</strong></div>
      <div className="project-stat"><span>In progress</span><strong>{inProgress}</strong></div>
      <div className="project-stat"><span>Completed</span><strong>{completed}</strong></div>
      <div className="project-stat"><span>Average progress</span><strong>{averageProgress}%</strong></div>
      <div className="project-stat"><span>Planned quantity</span><strong>{formatQuantity(plannedTotal)}</strong></div>
      <div className="project-stat"><span>Actual quantity</span><strong>{formatQuantity(actualTotal)}</strong></div>
    </section>
    {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}
    {projects.length === 0 && !loading ? <section className="project-empty"><strong>Create a project first</strong><span>Construction activities must belong to a project.</span><a className="back-link" href="/projects">Open Projects</a></section> : <section className="project-layout">
      <form className="project-form" onSubmit={submit}>
        <div className="section-label">{editingId ? "Edit activity" : "New activity"}</div><h2>{editingId ? "Update construction activity" : "Add construction activity"}</h2><p>Execution records are linked directly to the selected project.</p>
        <div className="form-grid">
          <label>Project<select value={form.projectId} onChange={e => setForm({ ...form, projectId: e.target.value })} required><option value="" disabled>Select project</option>{projects.map(p => <option key={p.id} value={p.id}>{p.code} · {p.name}</option>)}</select></label>
          <label>Activity code<input value={form.activityCode} onChange={e => setForm({ ...form, activityCode: e.target.value })} placeholder="CON-001" maxLength={80} required /></label>
          <label className="full-width">Activity name<input value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} placeholder="Excavate foundation trenches" maxLength={250} required /></label>
          <label>Discipline<select value={form.discipline} onChange={e => setForm({ ...form, discipline: e.target.value })}>{disciplines.map(d => <option key={d}>{d}</option>)}</select></label>
          <label>Status<select value={form.status} onChange={e => setForm({ ...form, status: e.target.value as Status })}>{statuses.map(s => <option key={s} value={s}>{statusLabel[s]}</option>)}</select></label>
          <label>Planned quantity<input type="number" min={0} step="0.001" value={form.plannedQuantity} onChange={e => setForm({ ...form, plannedQuantity: Math.max(0, Number(e.target.value)) })} /></label>
          <label>Actual quantity<input type="number" min={0} step="0.001" value={form.actualQuantity} onChange={e => setForm({ ...form, actualQuantity: Math.max(0, Number(e.target.value)) })} /></label>
          <label>Unit<select value={form.unit} onChange={e => setForm({ ...form, unit: e.target.value })}><option value="">Not specified</option>{units.map(u => <option key={u}>{u}</option>)}</select></label>
          <label>Progress (%)<input type="number" min={0} max={100} step={1} value={form.progress} onChange={e => setForm({ ...form, progress: Math.min(100, Math.max(0, Number(e.target.value))) })} /></label>
          <label className="full-width">Notes<textarea value={form.notes} onChange={e => setForm({ ...form, notes: e.target.value })} placeholder="Site notes, constraints, inspections or coordination comments" rows={4} maxLength={4000} /></label>
        </div>
        <div className="form-actions">{editingId && <button type="button" className="secondary-button" onClick={reset}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingId ? "Save changes" : "Add construction activity"}</button></div>
      </form>
      <section className="project-list-panel">
        <div className="list-toolbar"><div><div className="section-label">Construction register</div><h2>{filtered.length} activit{filtered.length === 1 ? "y" : "ies"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
        <div className="filters"><input aria-label="Search construction activities" value={query} onChange={e => setQuery(e.target.value)} placeholder="Search code, activity, discipline or notes" /><select value={filterProject} onChange={e => setFilterProject(e.target.value)}><option value="all">All projects</option>{projects.map(p => <option key={p.id} value={p.id}>{p.code}</option>)}</select><select value={filterStatus} onChange={e => setFilterStatus(e.target.value as "all" | Status)}><option value="all">All statuses</option>{statuses.map(s => <option key={s} value={s}>{statusLabel[s]}</option>)}</select></div>
        {loading ? <div className="project-empty"><strong>Loading construction register...</strong><span>Reading site execution records.</span></div> : filtered.length === 0 ? <div className="project-empty"><strong>No construction activities found</strong><span>Create an activity or change the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Code</th><th>Project</th><th>Activity</th><th>Status</th><th>Planned</th><th>Actual</th><th>Progress</th><th>Updated</th><th /></tr></thead><tbody>{filtered.map(a => <tr key={a.id}><td><strong>{a.activityCode}</strong></td><td><strong>{projects.find(p => p.id === a.projectId)?.code ?? "Unknown"}</strong><div className="project-description">{projectName(a.projectId)}</div></td><td><div className="project-name">{a.name}</div><div className="project-description">{a.discipline || "General"}</div></td><td><span className={`project-status ${a.status}`}>{statusLabel[a.status]}</span></td><td>{formatQuantity(a.plannedQuantity)} {a.unit ?? ""}</td><td>{formatQuantity(a.actualQuantity)} {a.unit ?? ""}</td><td><strong>{a.progress}%</strong></td><td>{formatDate(a.updatedAt)}</td><td><div className="row-actions"><button onClick={() => edit(a)}>Edit</button><button className="danger-link" onClick={() => void remove(a)}>Delete</button></div></td></tr>)}</tbody></table></div>}
      </section>
    </section>}
  </main>;
}
