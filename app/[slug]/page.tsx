"use client";

import Link from "next/link";
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

type Row = Record<string, string | number | boolean | null> & { id: string };

export default function WorkspaceModule({ params }: { params: { slug: string } }) {
  const definition = definitions[params.slug];
  const [projects, setProjects] = useState<Project[]>([]);
  const [rows, setRows] = useState<Row[]>([]);
  const [projectId, setProjectId] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [number, setNumber] = useState("");

  useEffect(() => {
    void fetch("/api/projects", { cache: "no-store" }).then((r) => r.json()).then((d) => {
      const list = Array.isArray(d.data) ? d.data : [];
      setProjects(list);
      if (list[0]) setProjectId(list[0].id);
    }).catch(() => undefined);
  }, []);

  const loadRows = async () => {
    if (!definition?.kind || ["cost", "reports", "settings"].includes(definition.kind)) return;
    const response = await fetch(`/api/workspace?module=${definition.kind}${projectId ? `&projectId=${projectId}` : ""}`, { cache: "no-store" });
    const data = await response.json();
    setRows(Array.isArray(data.data) ? data.data : []);
  };

  useEffect(() => { void loadRows(); }, [definition?.kind, projectId]);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!definition?.kind || !projectId) return;
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
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to save record.");
      setTitle(""); setDescription(""); setCategory(""); setNumber("");
      setMessage("Record saved.");
      await loadRows();
    } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to save record."); }
    finally { setBusy(false); }
  };

  const cards = useMemo(() => {
    if (definition?.kind === "cost") return ["BOQ values", "Purchase orders", "Construction progress", "Commercial visibility"];
    if (definition?.kind === "reports") return ["Project status", "Design progress", "Procurement", "Construction"];
    if (definition?.kind === "settings") return ["Theme", "Workspace navigation", "Platform links", "PWA preferences"];
    return ["Create", "Review", "Edit", "Track"];
  }, [definition?.kind]);

  if (!definition) return <main className="content standalone"><div className="workspace-card"><h1>Module not found</h1><Link href="/">Return to Dashboard</Link></div></main>;

  return <main className="content standalone">
    <header className="topbar"><div><div className="eyebrow">Creative Studios</div><h1>{definition.title}</h1><p>{definition.description}</p></div><Link className="secondary-button" href="/">Dashboard</Link></header>
    <section className="kpi-grid">{cards.map((card) => <div className="kpi-card" key={card}><span>{card}</span><strong>{definition.kind === "settings" ? "Ready" : definition.kind === "cost" || definition.kind === "reports" ? "Live" : rows.length}</strong></div>)}</section>
    {definition.kind !== "cost" && definition.kind !== "reports" && definition.kind !== "settings" && <>
      <section className="workspace-card">
        <div className="page-editor-header"><div><div className="section-label">New record</div><h2>Add {definition.title.slice(0, -1) || definition.title}</h2></div></div>
        <form className="form-grid" onSubmit={submit}>
          <label>Project<select value={projectId} onChange={(e) => setProjectId(e.target.value)} required><option value="">Select project</option>{projects.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.name}</option>)}</select></label>
          <label>Title / Subject<input value={title} onChange={(e) => setTitle(e.target.value)} required /></label>
          <label>{definition.kind === "rfis" ? "RFI Number" : definition.kind === "documents" ? "Revision" : "Category / Priority"}<input value={number || category} onChange={(e) => definition.kind === "rfis" || definition.kind === "documents" ? setNumber(e.target.value) : setCategory(e.target.value)} /></label>
          <label>Description / Question<textarea value={description} onChange={(e) => setDescription(e.target.value)} /></label>
          <div><button className="primary-button" disabled={busy}>{busy ? "Saving..." : "Save record"}</button></div>
        </form>
        {message && <p className="form-message">{message}</p>}
      </section>
      <section className="workspace-card"><div className="section-label">Records</div><h2>{rows.length} records</h2><div className="table-wrap"><table><thead><tr><th>Record</th><th>Project</th><th>Status</th><th>Created</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}><td>{String(row.title ?? row.subject ?? row.category ?? row.rfiNumber ?? row.documentType ?? "Record")}</td><td>{projects.find((p) => p.id === row.projectId)?.name ?? ""}</td><td>{String(row.status ?? "active")}</td><td>{String(row.createdAt ?? "").slice(0, 10)}</td></tr>)}</tbody></table></div></section>
    </>}
    {definition.kind === "cost" && <section className="workspace-card"><div className="section-label">Commercial workflow</div><h2>BOQ → Procurement → Construction → Cost</h2><p>Use BOQ values, purchase orders and construction progress as the connected cost-control source of truth.</p><div className="workflow">{["/boq", "/procurement", "/construction", "/projects"].map((href) => <Link key={href} href={href}>{href.slice(1).replace("-", " ")}</Link>)}</div></section>}
    {definition.kind === "reports" && <section className="workspace-card"><div className="section-label">Reporting center</div><h2>Live workspace reporting</h2><p>Open the operational modules below to review the underlying records and return here for the consolidated view.</p><div className="workflow">{["/projects", "/engineering", "/drawings", "/boq", "/procurement", "/construction"].map((href) => <Link key={href} href={href}>{href.slice(1).replace("-", " ")}</Link>)}</div></section>}
    {definition.kind === "settings" && <section className="workspace-card"><div className="section-label">Workspace controls</div><h2>Creative Studios configuration</h2><p>Use the Dashboard page editor for navigation labels and descriptions. Theme and PWA links are available from the main workspace shell.</p><Link className="primary-button" href="/">Open Dashboard settings</Link></section>}
  </main>;
}
