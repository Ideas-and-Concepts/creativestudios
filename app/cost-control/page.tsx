"use client";

import EarnedValuePanel from "@/components/EarnedValuePanel";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

type Project = { id: string; code: string; name: string };
type CostType = "Budget" | "Committed Cost" | "Actual Cost" | "Forecast" | "Variation";
type Status = "Draft" | "Active" | "Approved" | "Closed";
type CostRecord = { id: string; projectId: string; costCode: string; description: string; costType: CostType; amount: string; status: Status; notes: string | null; createdAt: string; updatedAt: string };
type FormState = { projectId: string; costCode: string; description: string; costType: CostType; amount: string; status: Status; notes: string };
type Summary = { budget: number; committed: number; actual: number; forecast: number; variance: number; progress: number; remainingBudget: number; plannedQuantity: number; actualQuantity: number };

const costTypes: CostType[] = ["Budget", "Committed Cost", "Actual Cost", "Forecast", "Variation"];
const statuses: Status[] = ["Draft", "Active", "Approved", "Closed"];
const emptyForm: FormState = { projectId: "", costCode: "", description: "", costType: "Budget", amount: "", status: "Draft", notes: "" };
const emptySummary: Summary = { budget: 0, committed: 0, actual: 0, forecast: 0, variance: 0, progress: 0, remainingBudget: 0, plannedQuantity: 0, actualQuantity: 0 };

function money(value: string | number) { const n = Number(value); return Number.isFinite(n) ? new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n) : "0.00"; }
function formatDate(value: string) { const date = new Date(value); return Number.isNaN(date.getTime()) ? "Not set" : new Intl.DateTimeFormat(undefined, { year: "numeric", month: "short", day: "numeric" }).format(date); }

export default function CostControlPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [records, setRecords] = useState<CostRecord[]>([]);
  const [summary, setSummary] = useState<Summary>(emptySummary);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [filterProject, setFilterProject] = useState("all");
  const [filterType, setFilterType] = useState<"all" | CostType>("all");
  const [filterStatus, setFilterStatus] = useState<"all" | Status>("all");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadSummary = useCallback(async (projectId: string) => {
    if (!projectId) { setSummary(emptySummary); return; }
    setSummaryLoading(true);
    try {
      const response = await fetch(`/api/cost-control/summary?projectId=${encodeURIComponent(projectId)}`, { cache: "no-store" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to calculate project cost summary.");
      setSummary(data.data ?? emptySummary);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to calculate project cost summary."); }
    finally { setSummaryLoading(false); }
  }, []);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [projectResponse, costResponse] = await Promise.all([
        fetch("/api/projects", { cache: "no-store" }),
        fetch("/api/cost-control", { cache: "no-store" }),
      ]);
      const [projectData, costData] = await Promise.all([projectResponse.json(), costResponse.json()]);
      if (!projectResponse.ok) throw new Error(projectData.error ?? "Unable to load projects.");
      if (!costResponse.ok) throw new Error(costData.error ?? "Unable to load cost control records.");
      const projectRows = Array.isArray(projectData.data) ? projectData.data : [];
      setProjects(projectRows); setRecords(Array.isArray(costData.data) ? costData.data : []);
      const nextProject = form.projectId || projectRows[0]?.id || "";
      if (!form.projectId && nextProject) setForm((current) => ({ ...current, projectId: nextProject }));
      if (nextProject) await loadSummary(nextProject);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to load cost control data."); }
    finally { setLoading(false); }
  }, [form.projectId, loadSummary]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => { if (form.projectId) void loadSummary(form.projectId); }, [form.projectId, loadSummary]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return records.filter((record) => {
      const projectMatch = filterProject === "all" || record.projectId === filterProject;
      const typeMatch = filterType === "all" || record.costType === filterType;
      const statusMatch = filterStatus === "all" || record.status === filterStatus;
      const text = `${record.costCode} ${record.description} ${record.costType} ${record.status} ${record.notes ?? ""}`.toLowerCase();
      return projectMatch && typeMatch && statusMatch && (!q || text.includes(q));
    });
  }, [records, query, filterProject, filterType, filterStatus]);

  const totals = useMemo(() => {
    const sum = (type: CostType) => filtered.filter((record) => record.costType === type).reduce((total, record) => total + Number(record.amount || 0), 0);
    return { budget: sum("Budget"), committed: sum("Committed Cost"), actual: sum("Actual Cost"), forecast: sum("Forecast"), variation: sum("Variation") };
  }, [filtered]);

  const projectName = (id: string) => projects.find((project) => project.id === id)?.name ?? "Unknown project";
  const reset = () => { setForm(projects[0]?.id ? { ...emptyForm, projectId: projects[0].id } : emptyForm); setEditingId(null); };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setSaving(true); setError(""); setMessage("");
    try {
      const payload = { ...form, amount: Number(form.amount), notes: form.notes || null };
      const response = await fetch(editingId ? `/api/cost-control/${editingId}` : "/api/cost-control", { method: editingId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error ?? "Unable to save cost control record.");
      setMessage(editingId ? "Cost control record updated successfully." : "Cost control record created successfully.");
      const projectId = form.projectId;
      setEditingId(null); setForm({ ...emptyForm, projectId });
      await load();
      await loadSummary(projectId);
    } catch (err) { setError(err instanceof Error ? err.message : "Unable to save cost control record."); }
    finally { setSaving(false); }
  };

  const edit = (record: CostRecord) => { setEditingId(record.id); setForm({ projectId: record.projectId, costCode: record.costCode, description: record.description, costType: record.costType, amount: record.amount, status: record.status, notes: record.notes ?? "" }); setMessage(""); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const remove = async (record: CostRecord) => { if (!window.confirm(`Delete ${record.costCode} from ${projectName(record.projectId)}?`)) return; setError(""); setMessage(""); try { const response = await fetch(`/api/cost-control/${record.id}`, { method: "DELETE" }); const data = await response.json(); if (!response.ok) throw new Error(data.error ?? "Unable to delete cost control record."); setMessage("Cost control record deleted successfully."); if (editingId === record.id) reset(); await load(); await loadSummary(form.projectId || record.projectId); } catch (err) { setError(err instanceof Error ? err.message : "Unable to delete cost control record."); } };

  const selectedProject = form.projectId ? projectName(form.projectId) : "No project selected";
  const budgetUtilisation = summary.budget > 0 ? Math.min(100, Math.max(0, (summary.forecast / summary.budget) * 100)) : 0;

  return (
    <main className="projects-page cost-control-page">
      <header className="projects-header"><div><div className="eyebrow">Creative Studios / Commercial</div><h1>Cost Control</h1><p>Track budget, commitments, actual cost, forecast and variance against live project quantities and procurement.</p></div><a className="back-link" href="/">Dashboard</a></header>
      <section className="project-stats" aria-label="Project cost summary"><div className="project-stat"><span>BOQ Budget</span><strong>{summaryLoading ? "Loading..." : money(summary.budget)}</strong></div><div className="project-stat"><span>Committed Cost</span><strong>{summaryLoading ? "Loading..." : money(summary.committed)}</strong></div><div className="project-stat"><span>Actual Cost</span><strong>{summaryLoading ? "Loading..." : money(summary.actual)}</strong></div><div className="project-stat"><span>Forecast</span><strong>{summaryLoading ? "Loading..." : money(summary.forecast)}</strong></div><div className="project-stat"><span>Variance</span><strong>{summaryLoading ? "Loading..." : money(summary.variance)}</strong></div></section>
      <section className="workspace-card" style={{ marginBottom: "24px" }}><div className="list-toolbar"><div><div className="section-label">Live project commercial position</div><h2>{selectedProject}</h2><p>{summary.progress.toFixed(1)}% physical progress · {money(summary.actualQuantity)} of {money(summary.plannedQuantity)} planned quantity recorded.</p></div><strong>{budgetUtilisation.toFixed(1)}% forecast budget used</strong></div><div style={{ height: "8px", background: "#eef2f7", borderRadius: "999px", overflow: "hidden", marginTop: "14px" }}><div style={{ width: `${budgetUtilisation}%`, height: "100%", background: "#2563eb", borderRadius: "999px" }} /></div><div className="project-stats" style={{ marginTop: "16px" }}><div className="project-stat"><span>Remaining Budget</span><strong>{money(summary.remainingBudget)}</strong></div><div className="project-stat"><span>Physical Progress</span><strong>{summary.progress.toFixed(1)}%</strong></div></div></section>
      {form.projectId && <EarnedValuePanel projectId={form.projectId} />}
      {(error || message) && <div className={error ? "project-alert error" : "project-alert success"} role="status">{error || message}</div>}
      {projects.length === 0 && !loading ? <section className="project-empty"><strong>Create a project first</strong><span>Every cost record must belong to a project.</span><a className="back-link" href="/projects">Open Projects</a></section> : (
        <section className="project-layout">
          <form className="project-form" onSubmit={submit}>
            <div className="section-label">{editingId ? "Edit cost record" : "New cost record"}</div><h2>{editingId ? "Update commercial record" : "Add commercial record"}</h2><p>Use manual records for actual costs, approved variations and other commercial adjustments. BOQ budget and procurement commitments are calculated automatically.</p>
            <div className="form-grid">
              <label>Project<select value={form.projectId} onChange={(event) => setForm({ ...form, projectId: event.target.value })} required><option value="" disabled>Select project</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code} · {project.name}</option>)}</select></label>
              <label>Cost code<input value={form.costCode} onChange={(event) => setForm({ ...form, costCode: event.target.value })} placeholder="e.g. COST-001" maxLength={100} required /></label>
              <label>Cost type<select value={form.costType} onChange={(event) => setForm({ ...form, costType: event.target.value as CostType })}>{costTypes.map((type) => <option key={type}>{type}</option>)}</select></label>
              <label>Amount<input type="number" min="0" step="0.01" value={form.amount} onChange={(event) => setForm({ ...form, amount: event.target.value })} required /></label>
              <label>Status<select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as Status })}>{statuses.map((status) => <option key={status}>{status}</option>)}</select></label>
              <label className="full-width">Description<textarea value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} rows={3} maxLength={2000} required /></label>
              <label className="full-width">Notes<textarea value={form.notes} onChange={(event) => setForm({ ...form, notes: event.target.value })} rows={3} maxLength={4000} /></label>
            </div>
            <div className="form-actions">{editingId && <button type="button" className="secondary-button" onClick={reset}>Cancel</button>}<button type="submit" className="primary-button" disabled={saving}>{saving ? "Saving..." : editingId ? "Save changes" : "Add cost record"}</button></div>
          </form>
          <section className="project-list-panel">
            <div className="list-toolbar"><div><div className="section-label">Cost register</div><h2>{filtered.length} record{filtered.length === 1 ? "" : "s"}</h2></div><button className="secondary-button" onClick={() => void load()} disabled={loading}>Refresh</button></div>
            <div className="filters"><input aria-label="Search cost control" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search cost code, description or notes" /><select value={filterProject} onChange={(event) => setFilterProject(event.target.value)}><option value="all">All projects</option>{projects.map((project) => <option key={project.id} value={project.id}>{project.code}</option>)}</select><select value={filterType} onChange={(event) => setFilterType(event.target.value as "all" | CostType)}><option value="all">All cost types</option>{costTypes.map((type) => <option key={type}>{type}</option>)}</select><select value={filterStatus} onChange={(event) => setFilterStatus(event.target.value as "all" | Status)}><option value="all">All statuses</option>{statuses.map((status) => <option key={status}>{status}</option>)}</select></div>
            {loading ? <div className="project-empty"><strong>Loading cost register...</strong><span>Reading commercial records from Neon.</span></div> : filtered.length === 0 ? <div className="project-empty"><strong>No cost records found</strong><span>Create a record or change the filters.</span></div> : <div className="project-table-wrap"><table className="project-table"><thead><tr><th>Code</th><th>Project</th><th>Description</th><th>Type</th><th>Amount</th><th>Status</th><th>Updated</th><th /></tr></thead><tbody>{filtered.map((record) => <tr key={record.id}><td><strong>{record.costCode}</strong></td><td>{projectName(record.projectId)}</td><td><div className="project-name">{record.description}</div>{record.notes && <div className="project-description">{record.notes}</div>}</td><td>{record.costType}</td><td><strong>{money(record.amount)}</strong></td><td><span className={`project-status ${record.status.toLowerCase().replace(/\s+/g, "-")}`}>{record.status}</span></td><td>{formatDate(record.updatedAt)}</td><td><div className="row-actions"><button onClick={() => edit(record)}>Edit</button><button className="danger-link" onClick={() => void remove(record)}>Delete</button></div></td></tr>)}</tbody></table></div>}
          </section>
        </section>
      )}
    </main>
  );
}
