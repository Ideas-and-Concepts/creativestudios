"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

const statuses = ["planning", "active", "on_hold", "completed", "cancelled"] as const;
type ProjectStatus = (typeof statuses)[number];

type Project = {
  id: string;
  code: string;
  name: string;
  clientName: string | null;
  location: string | null;
  description: string | null;
  status: ProjectStatus;
  startDate: string | null;
  targetEndDate: string | null;
  createdAt: string;
  updatedAt: string;
};

type FormState = {
  code: string;
  name: string;
  clientName: string;
  location: string;
  description: string;
  status: ProjectStatus;
  startDate: string;
  targetEndDate: string;
};

const emptyForm: FormState = {
  code: "",
  name: "",
  clientName: "",
  location: "",
  description: "",
  status: "planning",
  startDate: "",
  targetEndDate: "",
};

const statusLabel: Record<ProjectStatus, string> = {
  planning: "Planning",
  active: "Active",
  on_hold: "On hold",
  completed: "Completed",
  cancelled: "Cancelled",
};

function formatDate(value: string | null) {
  if (!value) return "Not set";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Not set"
    : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date);
}

function dateInputValue(value: string | null) {
  if (!value) return "";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "" : date.toISOString().slice(0, 10);
}

function toIsoDate(value: string) {
  return value ? new Date(`${value}T00:00:00.000Z`).toISOString() : null;
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | ProjectStatus>("all");
  const [form, setForm] = useState<FormState>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadProjects = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch("/api/projects", { cache: "no-store" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to load projects.");
      setProjects(Array.isArray(data.data) ? data.data : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load projects.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadProjects();
  }, [loadProjects]);

  const filteredProjects = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return projects.filter((project) => {
      const matchesStatus = filter === "all" || project.status === filter;
      const haystack = [project.code, project.name, project.clientName, project.location]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return matchesStatus && (!normalized || haystack.includes(normalized));
    });
  }, [filter, projects, query]);

  const resetForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setError("");
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    setMessage("");

    if (form.startDate && form.targetEndDate && form.targetEndDate < form.startDate) {
      setError("Target end date cannot be earlier than the start date.");
      setSaving(false);
      return;
    }

    const payload = {
      code: form.code,
      name: form.name,
      clientName: form.clientName || null,
      location: form.location || null,
      description: form.description || null,
      status: form.status,
      startDate: toIsoDate(form.startDate),
      targetEndDate: toIsoDate(form.targetEndDate),
    };

    try {
      const response = await fetch(editingId ? `/api/projects/${editingId}` : "/api/projects", {
        method: editingId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to save project.");

      setMessage(editingId ? "Project updated successfully." : "Project created successfully.");
      resetForm();
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save project.");
    } finally {
      setSaving(false);
    }
  };

  const editProject = (project: Project) => {
    setEditingId(project.id);
    setForm({
      code: project.code,
      name: project.name,
      clientName: project.clientName ?? "",
      location: project.location ?? "",
      description: project.description ?? "",
      status: project.status,
      startDate: dateInputValue(project.startDate),
      targetEndDate: dateInputValue(project.targetEndDate),
    });
    setMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const deleteProject = async (project: Project) => {
    if (!window.confirm(`Delete project ${project.code} - ${project.name}? This also removes its related project records.`)) return;

    setError("");
    setMessage("");
    try {
      const response = await fetch(`/api/projects/${project.id}`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to delete project.");
      if (editingId === project.id) resetForm();
      setMessage("Project deleted successfully.");
      await loadProjects();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete project.");
    }
  };

  const activeCount = projects.filter((project) => project.status === "active").length;
  const planningCount = projects.filter((project) => project.status === "planning").length;
  const completedCount = projects.filter((project) => project.status === "completed").length;

  return (
    <main className="projects-page">
      <header className="projects-header">
        <div>
          <div className="eyebrow">Creative Studios / Workspace</div>
          <h1>Projects</h1>
          <p>Create and manage the project records that connect the AEC delivery workflow.</p>
        </div>
        <a className="back-link" href="/">Dashboard</a>
      </header>

      <section className="project-stats" aria-label="Project summary">
        <div className="project-stat"><span>Total projects</span><strong>{projects.length}</strong></div>
        <div className="project-stat"><span>Active</span><strong>{activeCount}</strong></div>
        <div className="project-stat"><span>Planning</span><strong>{planningCount}</strong></div>
        <div className="project-stat"><span>Completed</span><strong>{completedCount}</strong></div>
      </section>

      {(error || message) && (
        <div className={error ? "project-alert error" : "project-alert success"} role="status">
          {error || message}
        </div>
      )}

      <section className="project-layout">
        <form className="project-form" onSubmit={submit}>
          <div className="section-label">{editingId ? "Edit project" : "New project"}</div>
          <h2>{editingId ? "Update project details" : "Create a project"}</h2>
          <p>Every downstream AEC module will reference this project.</p>

          <div className="form-grid">
            <label>
              Project code
              <input value={form.code} onChange={(event) => setForm({ ...form, code: event.target.value })} placeholder="PRJ-001" required maxLength={50} />
            </label>
            <label>
              Project name
              <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} placeholder="Residential Development" required maxLength={200} />
            </label>
            <label>
              Client
              <input value={form.clientName} onChange={(event) => setForm({ ...form, clientName: event.target.value })} placeholder="Client or organisation" maxLength={200} />
            </label>
            <label>
              Location
              <input value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} placeholder="Juba, South Sudan" maxLength={200} />
            </label>
            <label>
              Status
              <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as ProjectStatus })}>
                {statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}
              </select>
            </label>
            <label>
              Start date
              <input type="date" value={form.startDate} onChange={(event) => setForm({ ...form, startDate: event.target.value })} />
            </label>
            <label>
              Target end date
              <input type="date" value={form.targetEndDate} min={form.startDate || undefined} onChange={(event) => setForm({ ...form, targetEndDate: event.target.value })} />
            </label>
            <label className="full-width">
              Description
              <textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Project scope, objectives and key information" rows={4} maxLength={2000} />
            </label>
          </div>

          <div className="form-actions">
            {editingId && <button type="button" className="secondary-button" onClick={resetForm}>Cancel</button>}
            <button type="submit" className="primary-button" disabled={saving}>
              {saving ? "Saving..." : editingId ? "Save changes" : "Create project"}
            </button>
          </div>
        </form>

        <section className="project-list-panel">
          <div className="list-toolbar">
            <div>
              <div className="section-label">Project register</div>
              <h2>{filteredProjects.length} project{filteredProjects.length === 1 ? "" : "s"}</h2>
            </div>
            <button className="secondary-button" onClick={() => void loadProjects()} disabled={loading}>Refresh</button>
          </div>

          <div className="filters">
            <input aria-label="Search projects" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search code, name, client or location" />
            <select aria-label="Filter projects by status" value={filter} onChange={(event) => setFilter(event.target.value as "all" | ProjectStatus)}>
              <option value="all">All statuses</option>
              {statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}
            </select>
          </div>

          {loading ? (
            <div className="project-empty"><strong>Loading projects...</strong><span>Reading the project register.</span></div>
          ) : filteredProjects.length === 0 ? (
            <div className="project-empty">
              <strong>{projects.length === 0 ? "No projects yet" : "No matching projects"}</strong>
              <span>{projects.length === 0 ? "Create the first project to start the AEC workflow." : "Try a different search or status filter."}</span>
            </div>
          ) : (
            <div className="project-table-wrap">
              <table className="project-table">
                <thead>
                  <tr><th>Code</th><th>Project</th><th>Client</th><th>Location</th><th>Status</th><th>Updated</th><th /></tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project) => (
                    <tr key={project.id}>
                      <td><strong>{project.code}</strong></td>
                      <td><div className="project-name">{project.name}</div><div className="project-description">{project.description || "No description"}</div></td>
                      <td>{project.clientName || "Not set"}</td>
                      <td>{project.location || "Not set"}</td>
                      <td><span className={`project-status ${project.status}`}>{statusLabel[project.status]}</span></td>
                      <td>{formatDate(project.updatedAt)}</td>
                      <td><div className="row-actions"><button onClick={() => editProject(project)}>Edit</button><button className="danger-link" onClick={() => void deleteProject(project)}>Delete</button></div></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
