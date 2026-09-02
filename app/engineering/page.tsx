"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Status = "planned" | "in_progress" | "completed" | "on_hold";

type EngineeringWork = {
  id: string;
  projectId: string;
  category: string;
  description: string;
  status: Status;
  progress: number;
  notes: string | null;
  createdAt: string;
  updatedAt: string;
};

type Project = { id: string; code: string; name: string };

type FormState = {
  projectId: string;
  category: string;
  description: string;
  status: Status;
  progress: number;
  notes: string;
};

const statuses: Status[] = ["planned", "in_progress", "completed", "on_hold"];
const statusLabel: Record<Status, string> = {
  planned: "Planned",
  in_progress: "In progress",
  completed: "Completed",
  on_hold: "On hold",
};

const categories = [
  "Structural engineering",
  "Civil engineering",
  "Geotechnical engineering",
  "Hydraulic engineering",
  "Roads and external works",
  "Drainage and stormwater",
  "Foundation design",
  "Concrete structures",
  "Steel structures",
  "Site engineering",
  "Other",
];

const emptyForm: FormState = {
  projectId: "",
  category: "Structural engineering",
  description: "",
  status: "planned",
  progress: 0,
  notes: "",
};

function formatDate(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date);
}

export default function EngineeringPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [works, setWorks] = useState<EngineeringWork[]>([]);
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
      const [projectResponse, workResponse] = await Promise.all([fetch("/api/projects", { cache: "no-store" }), fetch("/api/engineering", { cache: "no-store" })]);
      const projectData = await projectResponse.json();
      const workData = await workResponse.json();
      if (!projectResponse.ok) throw new Error(projectData.error ?? "Unable to load projects.");
      if (!workResponse.ok) throw new Error(workData.error ?? "Unable to load engineering works.");
      const projectRows = Array.isArray(projectData.data) ? projectData.data : [];
      setProjects(projectRows);
      setWorks(Array.isArray(workData.data) ? workData.data : []);
      if (!form.projectId && projectRows[0]?.id) setForm((current) => ({ ...current, projectId: projectRows[0].id }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load engineering data.");
    } finally { setLoading(false); }
  }, [form.projectId]);

  useEffect(() => { void load(); }, [load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return works.filter((work) => {
      const projectMatch = filterProject === "all" || work.projectId === filterProject;
      const statusMatch = filterStatus === "all" || work.status === filterStatus;
      const text = `${work.category} ${work.description} ${work.notes ?? ""}`.toLowerCase();
      return projectMatch && statusMatch && (!q || text.includes(q));
    });
  }, [filterProject, filterStatus, query, works]);

  const projectName = (id: string) => projects.find((project) => project.id === id)?.name ?? "Unknown project";

  const reset = () => { setForm(projects[0]?.id ? { ...emptyForm, projectId: projects[0].id } : emptyForm); setEditingId(null); };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const response = await fetch(editingId ? `/api/engineering/${editingId}` : "/api/engineering", {
        method: editingId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, progress: Number(form.progress), notes: form.notes || null }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to save engineering work.");
      setMessage(editingId ? "Engineering work updated successfully." : "Engineering work created successfully.");
      reset(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save engineering work."); }
    finally { setSaving(false); }
  };

  const edit = (work: EngineeringWork) => {
    setEditingId(work.id);
    setForm({ projectId: work.projectId, category: work.category, description: work.description, status: work.status, progress: work.progress, notes: work.notes ?? "" });
    setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const remove = async (work: EngineeringWork) => {
    if (!window.confirm(`Delete this engineering work item from ${projectName(work.projectId)}?`)) return;
    setError(""); setMessage("");
    try {
      const response = await fetch(`/api/engineering/${work.id}`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to delete engineering work.");
      setMessage("Engineering work deleted successfully.");
      if (editingId === work.id) reset();
      await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete engineering work."); }
  };

  const inProgress = works.filter((work) => work.status === "in_progress").length;
  const completed = works.filter((work) => work.status === "completed").length;
  const averageProgress = works.length ? Math.round(works.reduce((sum, work) => sum + work.progress, 0) / works.length) : 0;

  return (
    <main className="projects-page engineering-page">
      <header className="projects-header">
        <div><div className="eyebrow">Creative Studios / Engineering</div><h1>Engineering</h1><p>Manage structural, civil and technical engineering works connected to project delivery.</p></div>
        <a className="back-link" href="/">Dashboard</a>
      </header>

      <section className="project-stats" aria-label="Engineering summary">
        <div className="project-stat"><span>Total work items</span><strong>{works.length}</strong></div>
        <div className="project-stat"><span>In progress</span><strong>{inProgress}</strong></div>
        <div className="project-stat"><span>Completed</span><strong>{completed}</strong></div>
        <div className="project-stat"><span>Average progress</span><strong>{averageProgress}%</strong></div>
      </section>

      {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}

      {projects.length === 0 && !loading ? <section className="project-empty engineering-empty"><strong>Create a project first</strong><span>Engineering works must belong to a project. Open Projects to create the project record.</span><a className="back-link" href="/projects">Open Projects</a></section> : (
        <section className="project-layout">
          <form className="project-form" onSubmit={submit}>
            <div className="section-label">{editingId ? "Edit work item" : "New work item"}</div>
            <h2>{editingId ? "Update engineering work" : "Add engineering work"}</h2>
            <p>Engineering records are linked directly to the selected project.</p>
            <div className="form-grid">
              <label>Project<select value={form.projectId} onChange={(event) => setForm({ ...form, projectId: event.target.value })} required><option value="" disabled>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code} · {project.name}</option>)}</select></label>
              <label>Engineering category<select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} required>{categories.map((category) => <option key={category}>{category}</option>)}</select></label>
              <label className="full-width">Work description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Describe the engineering scope, design work or construction engineering activity" rows={5} required maxLength={2000} /></label>
              <label>Status<select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as Status })}>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></label>
              <label>Progress (%)<input type="number" min={0} max={100} step={1} value={form.progress} onChange={(event) => setForm({ ...form, progress: Math.min(100, Math.max(0, Number(event.target.value))) })} /></label>
              <label className="full-width">Notes<textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} placeholder="Engineering notes, coordination requirements or technical comments" rows={4} maxLength={4000} /></label>
            </div>
            <div className="form-actions">{editingId && <button type="button" className="secondary-button" onClick={reset}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingId ? "Save changes" : "Add engineering work"}</button></div>
          </form>

          <section className="project-list-panel">
            <div className="list-toolbar"><div><div className="section-label">Engineering register</div><h2>{filtered.length} work item{filtered.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
            <div className="filters"><input aria-label="Search engineering works" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search category, description or notes" /><select value={filterProject} onChange={(event) => setFilterProject(event.target.value)}><option value="all">All projects</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code}</option>)}</select><select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value as "all" | Status)}><option value="all">All statuses</option>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></div>
            {loading ? <div className="project-empty"><strong>Loading engineering register...</strong><span>Reading project engineering records.</span></div> : filtered.length === 0 ? <div className="project-empty"><strong>No engineering work found</strong><span>Create an item or change the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Project</th><th>Category</th><th>Description</th><th>Status</th><th>Progress</th><th>Updated</th><th /></tr></thead><tbody>{filtered.map((work) => <tr key={work.id}><td><strong>{projects.find((project) => project.id === work.projectId)?.code ?? "Unknown"}</strong><div className="project-description">{projectName(work.projectId)}</div></td><td>{work.category}</td><td><div className="project-name">{work.description}</div><div className="project-description">{work.notes || "No notes"}</div></td><td><span className={`project-status ${work.status}`}>{statusLabel[work.status]}</span></td><td><strong>{work.progress}%</strong></td><td>{formatDate(work.updatedAt)}</td><td><div className="row-actions"><button onClick={() => edit(work)}>Edit</button><button className="danger-link" onClick={() => void remove(work)}>Delete</button></div></td></tr>)}</tbody></table></div>}
          </section>
        </section>
      )}
    </main>
  );
}
