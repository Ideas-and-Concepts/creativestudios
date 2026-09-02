"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Status = "planned" | "in_progress" | "completed" | "on_hold";
type Project = { id: string; code: string; name: string };
type Drawing = { id: string; projectId: string; drawingNumber: string; title: string; discipline: string; revision: string };
type BoqItem = { id: string; projectId: string; drawingId: string | null; itemCode: string; category: string; element: string; description: string; quantity: string; unit: string; rate: string; amount: string; status: Status; createdAt: string; updatedAt: string };
type FormState = { projectId: string; drawingId: string; itemCode: string; category: string; element: string; description: string; quantity: string; unit: string; rate: string; status: Status };

const statuses: Status[] = ["planned", "in_progress", "completed", "on_hold"];
const statusLabel: Record<Status, string> = { planned: "Planned", in_progress: "In progress", completed: "Completed", on_hold: "On hold" };
const categories = ["Preliminaries", "Substructure", "Superstructure", "Roofing", "Finishes", "Doors and windows", "External works", "Civil works", "Structural works", "MEP works", "Other"];
const emptyForm: FormState = { projectId: "", drawingId: "", itemCode: "", category: "Substructure", element: "", description: "", quantity: "", unit: "m³", rate: "", status: "planned" };

function money(value: string | number) { const n = Number(value); return Number.isFinite(n) ? new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) : "0.00"; }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date); }

export default function BoqPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [drawings, setDrawings] = useState<Drawing[]>([]);
  const [items, setItems] = useState<BoqItem[]>([]);
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
      const [projectResponse, drawingResponse, boqResponse] = await Promise.all([
        fetch("/api/projects", { cache: "no-store" }),
        fetch("/api/drawings", { cache: "no-store" }),
        fetch("/api/boq", { cache: "no-store" }),
      ]);
      const [projectData, drawingData, boqData] = await Promise.all([projectResponse.json(), drawingResponse.json(), boqResponse.json()]);
      if (!projectResponse.ok) throw new Error(projectData.error ?? "Unable to load projects.");
      if (!drawingResponse.ok) throw new Error(drawingData.error ?? "Unable to load drawings.");
      if (!boqResponse.ok) throw new Error(boqData.error ?? "Unable to load BOQ.");
      const projectRows = Array.isArray(projectData.data) ? projectData.data : [];
      setProjects(projectRows); setDrawings(Array.isArray(drawingData.data) ? drawingData.data : []); setItems(Array.isArray(boqData.data) ? boqData.data : []);
      if (!form.projectId && projectRows[0]?.id) setForm((current) => ({ ...current, projectId: projectRows[0].id }));
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load BOQ data."); }
    finally { setLoading(false); }
  }, [form.projectId]);

  useEffect(() => { void load(); }, [load]);

  const availableDrawings = useMemo(() => drawings.filter((drawing) => drawing.projectId === form.projectId), [drawings, form.projectId]);
  const filtered = useMemo(() => { const q = query.trim().toLowerCase(); return items.filter((item) => { const projectMatch = filterProject === "all" || item.projectId === filterProject; const statusMatch = filterStatus === "all" || item.status === filterStatus; const text = `${item.itemCode} ${item.category} ${item.element} ${item.description} ${item.unit}`.toLowerCase(); return projectMatch && statusMatch && (!q || text.includes(q)); }); }, [filterProject, filterStatus, query, items]);
  const totalValue = useMemo(() => filtered.reduce((sum, item) => sum + Number(item.amount || 0), 0), [filtered]);
  const projectName = (id: string) => projects.find((project) => project.id === id)?.name ?? "Unknown project";
  const drawingLabel = (id: string | null) => { if (!id) return "Not linked"; const drawing = drawings.find((row) => row.id === id); return drawing ? `${drawing.drawingNumber} · ${drawing.title}` : "Unknown drawing"; };

  const reset = () => { setForm(projects[0]?.id ? { ...emptyForm, projectId: projects[0].id } : emptyForm); setEditingId(null); };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const payload = { ...form, drawingId: form.drawingId || null, quantity: Number(form.quantity), rate: Number(form.rate) };
      const response = await fetch(editingId ? `/api/boq/${editingId}` : "/api/boq", { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to save BOQ item.");
      setMessage(editingId ? "BOQ item updated successfully." : "BOQ item created successfully."); reset(); await load();
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save BOQ item."); }
    finally { setSaving(false); }
  };

  const edit = (item: BoqItem) => { setEditingId(item.id); setForm({ projectId: item.projectId, drawingId: item.drawingId ?? "", itemCode: item.itemCode, category: item.category, element: item.element, description: item.description, quantity: item.quantity, unit: item.unit, rate: item.rate, status: item.status }); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const remove = async (item: BoqItem) => { if (!window.confirm(`Delete BOQ item ${item.itemCode} from ${projectName(item.projectId)}?`)) return; setError(""); setMessage(""); try { const response = await fetch(`/api/boq/${item.id}`, { method: "DELETE" }); const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to delete BOQ item."); setMessage("BOQ item deleted successfully."); if (editingId === item.id) reset(); await load(); } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete BOQ item."); } };

  const plannedValue = items.filter((item) => item.status === "planned").reduce((sum, item) => sum + Number(item.amount || 0), 0);
  const completedValue = items.filter((item) => item.status === "completed").reduce((sum, item) => sum + Number(item.amount || 0), 0);

  return (
    <main className="projects-page boq-page">
      <header className="projects-header"><div><div className="eyebrow">Creative Studios / BOQ</div><h1>Bill of Quantities</h1><p>Build project cost quantities from drawings, with calculated amounts for procurement and construction control.</p></div><a className="back-link" href="/">Dashboard</a></header>
      <section className="project-stats" aria-label="BOQ summary"><div className="project-stat"><span>Total items</span><strong>{items.length}</strong></div><div className="project-stat"><span>Visible value</span><strong>{money(totalValue)}</strong></div><div className="project-stat"><span>Planned value</span><strong>{money(plannedValue)}</strong></div><div className="project-stat"><span>Completed value</span><strong>{money(completedValue)}</strong></div></section>
      {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}
      {projects.length === 0 && !loading ? <section className="project-empty"><strong>Create a project first</strong><span>BOQ items must belong to a project. Open Projects to create the project record.</span><a className="back-link" href="/projects">Open Projects</a></section> : (
        <section className="project-layout">
          <form className="project-form" onSubmit={submit}>
            <div className="section-label">{editingId ? "Edit BOQ item" : "New BOQ item"}</div><h2>{editingId ? "Update quantity item" : "Add quantity item"}</h2><p>Amounts are calculated automatically as quantity × rate.</p>
            <div className="form-grid">
              <label>Project<select value={form.projectId} onChange={(event) => setForm({ ...form, projectId: event.target.value, drawingId: "" })} required><option value="" disabled>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code} · {project.name}</option>)}</select></label>
              <label>Drawing<select value={form.drawingId} onChange={(event) => setForm({ ...form, drawingId: event.target.value })}><option value="">Not linked</option>{availableDrawings.map((drawing) => <option key={drawing.id} value={drawing.id}>{drawing.drawingNumber} · {drawing.title}</option>)}</select></label>
              <label>Item code<input value={form.itemCode} onChange={(event) => setForm({ ...form, itemCode: event.target.value })} placeholder="e.g. BQ-001" maxLength={100} required /></label>
              <label>Category<select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>{categories.map((category) => <option key={category}>{category}</option>)}</select></label>
              <label>Element<input value={form.element} onChange={(event) => setForm({ ...form, element: event.target.value })} placeholder="e.g. Reinforced concrete footings" maxLength={160} required /></label>
              <label>Unit<input value={form.unit} onChange={(event) => setForm({ ...form, unit: event.target.value })} placeholder="m³, m², kg, No." maxLength={30} required /></label>
              <label className="full-width">Description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Detailed specification and measurement description" rows={4} maxLength={2000} required /></label>
              <label>Quantity<input type="number" min="0" step="0.001" value={form.quantity} onChange={(event) => setForm({ ...form, quantity: event.target.value })} required /></label>
              <label>Rate<input type="number" min="0" step="0.01" value={form.rate} onChange={(event) => setForm({ ...form, rate: event.target.value })} required /></label>
              <label>Status<select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as Status })}>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></label>
              <label>Calculated amount<input value={money((Number(form.quantity) || 0) * (Number(form.rate) || 0))} readOnly /></label>
            </div>
            <div className="form-actions">{editingId && <button type="button" className="secondary-button" onClick={reset}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingId ? "Save changes" : "Add BOQ item"}</button></div>
          </form>
          <section className="project-list-panel">
            <div className="list-toolbar"><div><div className="section-label">BOQ register</div><h2>{filtered.length} item{filtered.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
            <div className="filters"><input aria-label="Search BOQ" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search item, element or description" /><select value={filterProject} onChange={(event) => setFilterProject(event.target.value)}><option value="all">All projects</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code}</option>)}</select><select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value as "all" | Status)}><option value="all">All statuses</option>{statuses.map((status) => <option key={status} value={status}>{statusLabel[status]}</option>)}</select></div>
            {loading ? <div className="project-empty"><strong>Loading BOQ register...</strong><span>Reading quantities and cost records.</span></div> : filtered.length === 0 ? <div className="project-empty"><strong>No BOQ items found</strong><span>Create an item or change the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Code</th><th>Project / Drawing</th><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th><th>Status</th><th>Updated</th><th /></tr></thead><tbody>{filtered.map((item) => <tr key={item.id}><td><strong>{item.itemCode}</strong></td><td><strong>{projects.find((project) => project.id === item.projectId)?.code ?? "Unknown"}</strong><div className="project-description">{drawingLabel(item.drawingId)}</div></td><td><div className="project-name">{item.element}</div><div className="project-description">{item.description}</div><div className="project-description">{item.category}</div></td><td>{item.quantity} {item.unit}</td><td>{money(item.rate)}</td><td><strong>{money(item.amount)}</strong></td><td><span className={`project-status ${item.status}`}>{statusLabel[item.status]}</span></td><td>{formatDate(item.updatedAt)}</td><td><div className="row-actions"><button onClick={() => edit(item)}>Edit</button><button className="danger-link" onClick={() => void remove(item)}>Delete</button></div></td></tr>)}</tbody></table></div>}
          </section>
        </section>
      )}
    </main>
  );
}
