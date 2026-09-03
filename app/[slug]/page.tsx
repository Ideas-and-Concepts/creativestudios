"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { FormEvent, useEffect, useMemo, useState } from "react";

const definitions: Record<string, { title: string; description: string; kind?: string }> = {
  documents: { title: "Documents", description: "Central project documentation and controlled records.", kind: "documents" },
  architecture: { title: "Architecture", description: "Architectural works, design records and progress.", kind: "architecture" },
  "cost-control": { title: "Cost Control", description: "Commercial overview across BOQ, procurement and construction.", kind: "cost" },
  tasks: { title: "Tasks", description: "Assignments, priorities, deadlines and project actions.", kind: "tasks" },
  rfis: { title: "RFIs", description: "Requests for information, responses and status control.", kind: "rfis" },
  approvals: { title: "Approvals", description: "Controlled review and approval workflow.", kind: "approvals" },
  reports: { title: "Reports", description: "Live project and commercial reporting.", kind: "reports" },
  settings: { title: "Settings", description: "Workspace preferences and platform configuration.", kind: "settings" },
};

type Project = { id: string; code: string; name: string };
type Row = Record<string, string | number | boolean | null> & { id: string; projectId?: string | null };

async function readJson(response: Response): Promise<Record<string, any>> {
  const text = await response.text();
  if (!text) return {};
  try { return JSON.parse(text); } catch { return {}; }
}

export default function WorkspaceModule() {
  const params = useParams<{ slug: string }>();
  const slug = Array.isArray(params?.slug) ? params.slug[0] : params?.slug;
  const definition = definitions[slug ?? ""];
  const [projects, setProjects] = useState<Project[]>([]);
  const [rows, setRows] = useState<Row[]>([]);
  const [projectId, setProjectId] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [number, setNumber] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const response = await fetch("/api/projects", { cache: "no-store" });
        const data = await readJson(response);
        if (!response.ok) throw new Error(data.error || "Unable to load projects.");
        const list = Array.isArray(data.data) ? data.data : [];
        setProjects(list);
        if (list[0]) setProjectId((current) => current || list[0].id);
      } catch (error) {
        setMessage(error instanceof Error ? error.message : "Unable to load projects.");
      }
    };
    void loadProjects();
  }, []);

  const loadRows = async () => {
    if (!definition?.kind || ["cost", "reports", "settings"].includes(definition.kind)) return;
    try {
      const query = new URLSearchParams({ module: definition.kind });
      if (projectId) query.set("projectId", projectId);
      const response = await fetch(`/api/workspace?${query.toString()}`, { cache: "no-store" });
      const data = await readJson(response);
      if (!response.ok) throw new Error(data.error || "Unable to load records.");
      setRows(Array.isArray(data.data) ? data.data : []);
    } catch (error) {
      setRows([]);
      setMessage(error instanceof Error ? error.message : "Unable to load records.");
    }
  };

  useEffect(() => { void loadRows(); }, [definition?.kind, projectId]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!definition?.kind || !projectId) {
      setMessage("Create or select a project before adding a record.");
      return;
    }
    setBusy(true); setMessage("");
    const payload = definition.kind === "documents"
      ? { projectId, title, documentType: category || "General", revision: number || "A" }
      : definition.kind === "architecture"
        ? { projectId, category: category || "General", description: description || title }
        : definition.kind === "tasks"
          ? { projectId, title, description, priority: category || "normal" }
          : definition.kind === "rfis"
            ? { projectId, rfiNumber: number || `RFI-${rows.length + 1}`, subject: title, question: description }
            : { projectId, subject: title, approvalType: category || "General", comments: description };
    try {
      const response = await fetch(`/api/workspace?module=${definition.kind}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      const data = await readJson(response);
      if (!response.ok) throw new Error(data.error || "Unable to save record.");
      setTitle(""); setDescription(""); setCategory(""); setNumber("");
      setMessage("Record saved.");
      await loadRows();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to save record."); }
    finally { setBusy(false); }
  };

  const removeRecord = async (id: string) => {
    if (!definition?.kind || !window.confirm("Delete this record? This cannot be undone.")) return;
    setBusy(true); setMessage("");
    try {
      const response = await fetch(`/api/workspace?module=${definition.kind}&id=${encodeURIComponent(id)}`, { method: "DELETE" });
      const data = await readJson(response);
      if (!response.ok) throw new Error(data.error || "Unable to delete record.");
      setMessage("Record deleted.");
      await loadRows();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to delete record."); }
    finally { setBusy(false); }
  };

  const filteredRows = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return rows;
    return rows.filter((row) => Object.values(row).some((value) => String(value ?? "").toLowerCase().includes(query)));
  }, [rows, search]);

  const cards = useMemo(() => {
    if (definition?.kind === "cost") return ["BOQ values", "Purchase orders", "Construction progress", "Commercial visibility"];
    if (definition?.kind === "reports") return ["Project status", "Design progress", "Procurement", "Construction"];
    if (definition?.kind === "settings") return ["Theme", "Workspace navigation", "Platform links", "PWA preferences"];
    return ["Create", "Review", "Edit", "Track"];
  }, [definition?.kind]);

  if (!definition) return <main className="content standalone"><div className="workspace-card"><h1>Module not found</h1><Link href="/">Return to Dashboard</Link></div></main>;

  const isVercelColourModule = ["reports", "architecture", "tasks"].includes(slug ?? "");
  const pageClassName = `content standalone${isVercelColourModule ? " vercel-colour-module" : ""}`;

  return <main className={pageClassName}>
    <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>{definition.title}</h1><p>{definition.description}</p></div><Link className="secondary-button" href="/">Dashboard</Link></header>
    <section className="kpi-grid">{cards.map((card) => <div className="kpi-card" key={card}><span>{card}</span><strong>{definition.kind === "settings" ? "Ready" : definition.kind === "cost" || definition.kind === "reports" ? "Live" : rows.length}</strong></div>)}</section>
    {definition.kind !== "cost" && definition.kind !== "reports" && definition.kind !== "settings" && <>
      <section className="workspace-card">
        <div className="page-editor-header"><div><div className="section-label">New record</div><h2>Add {definition.title.replace(/s$/, "")}</h2><p>Records are saved to the shared database and remain available after refresh.</p></div></div>
        <form className="form-grid" onSubmit={submit}>
          <label>Project<select value={projectId} onChange={(e) => setProjectId(e.target.value)} required><option value="">Select project</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.name}</option>)}</select></label>
          <label>Title / Subject<input value={title} onChange={(e) => setTitle(e.target.value)} required /></label>
          <label>{definition.kind === "rfis" ? "RFI Number" : definition.kind === "documents" ? "Revision" : "Category / Priority"}<input value={definition.kind === "rfis" || definition.kind === "documents" ? number : category} onChange={(e) => definition.kind === "rfis" || definition.kind === "documents" ? setNumber(e.target.value) : setCategory(e.target.value)} /></label>
          <label>Description / Question<textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label>
          <div><button className="primary-button" disabled={busy}>{busy ? "Saving..." : "Save record"}</button></div>
        </form>
        {message && <p className="form-message">{message}</p>}
      </section>
      <section className="workspace-card"><div className="list-toolbar"><div><div className="section-label">Records</div><h2>{filteredRows.length} of {rows.length} records</h2></div><input aria-label="Search records" placeholder="Search records" value={search} onChange={(e) => setSearch(e.target.value)} /></div><div className="table-wrap"><table><thead><tr><th>Record</th><th>Project</th><th>Status</th><th>Created</th><th>Actions</th></tr></thead><tbody>{filteredRows.map((row) => <tr key={row.id}><td>{String(row.title ?? row.subject ?? row.category ?? row.rfiNumber ?? row.documentType ?? "Record")}</td><td>{projects.find((p) => p.id === row.projectId)?.name ?? ""}</td><td>{String(row.status ?? "active")}</td><td>{String(row.createdAt ?? "").slice(0, 10)}</td><td><button className="secondary-button" disabled={busy} onClick={() => void removeRecord(row.id)}>Delete</button></td></tr>)}</tbody></table></div></section>
    </>}
    {definition.kind === "cost" && <section className="workspace-card"><div className="section-label">Commercial workflow</div><h2>BOQ → Procurement → Construction → Cost</h2><p>Use BOQ values, purchase orders and construction progress as the connected cost-control source of truth.</p><div className="workflow">{["/boq", "/procurement", "/construction", "/projects"].map((href) => <Link key={href} href={href}>{href.slice(1).replace("-", " ")}</Link>)}</div></section>}
    {definition.kind === "reports" && <section className="workspace-card"><div className="section-label">Reporting center</div><h2>Live workspace reporting</h2><p>Open the operational modules below to review the underlying records and return here for the consolidated view.</p><div className="workflow">{["/projects", "/engineering", "/drawings", "/boq", "/procurement", "/construction"].map((href) => <Link key={href} href={href}>{href.slice(1).replace("-", " ")}</Link>)}</div></section>}
    {definition.kind === "settings" && <section className="workspace-card"><div className="section-label">Workspace controls</div><h2>Creative Studios configuration</h2><p>Use the Dashboard page editor for navigation labels and descriptions. Theme and PWA links are available from the main workspace shell.</p><Link className="primary-button" href="/">Open Dashboard settings</Link></section>}
  </main>;
}
