"""Database-backed Creative Studios executive dashboard for Streamlit."""
from __future__ import annotations

from datetime import datetime, timedelta
from html import escape
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .database import get_records

BLUE = "#3B82F6"
INK = "#111827"
GRID = "#E5E7EB"
PALETTE = ["#3B82F6", "#64748B", "#CBD5E1", "#94A3B8", "#475569", "#93C5FD"]


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _records(database: dict[str, Any], key: str) -> list[dict[str, Any]]:
    rows = get_records(key, database)
    return rows if isinstance(rows, list) else []


def _status(row: dict[str, Any], default: str = "open") -> str:
    return str(row.get("status") or default).strip().lower().replace(" ", "_")


def _label(value: str) -> str:
    return value.replace("_", " ").title()


def _progress(row: dict[str, Any]) -> float:
    """Return only recorded progress, with completion as the sole status fallback."""
    for key in ("progress", "completion", "percent_complete", "percentComplete"):
        if row.get(key) is not None:
            return max(0.0, min(100.0, _number(row.get(key))))
    return 100.0 if _status(row, "planning") == "completed" else 0.0


def _project_name(row: dict[str, Any]) -> str:
    return str(row.get("name") or row.get("code") or "Untitled")


def _inject_css() -> None:
    st.markdown("""
    <style>
    .cs-dashboard{color:#111827}.cs-dash-head{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:0 0 14px}.cs-dash-title{font-size:1.55rem;line-height:1.15;font-weight:800;letter-spacing:-.035em}.cs-dash-subtitle{font-size:.7rem;color:#64748b;margin-top:.25rem}.cs-dash-kpi{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:.72rem .78rem;min-height:88px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-dash-kpi-label{font-size:.61rem;color:#64748b}.cs-dash-kpi-value{font-size:1.32rem;font-weight:800;line-height:1.15;margin-top:.4rem}.cs-dash-kpi-note{font-size:.58rem;color:#64748b;margin-top:.35rem}.cs-dash-panel{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:.8rem .85rem;margin-bottom:.7rem}.cs-dash-panel-title{font-size:.69rem;font-weight:800}.cs-dash-panel-note{font-size:.57rem;color:#94a3b8;margin-top:.15rem}.cs-dash-table{width:100%;border-collapse:collapse;font-size:.56rem;color:#334155}.cs-dash-table th{font-size:.5rem;color:#64748b;text-align:left;padding:.42rem .3rem;border-bottom:1px solid #e5e7eb}.cs-dash-table td{padding:.46rem .3rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}.cs-status-pill{display:inline-block;border-radius:999px;padding:3px 7px;background:#eff6ff;color:#2563eb;font-weight:700;font-size:.5rem}.cs-alert{border:1px solid #edf0f4;border-radius:8px;padding:8px 9px;margin-bottom:7px}.cs-alert strong{font-size:.59rem}.cs-alert small{display:block;color:#94a3b8;font-size:.52rem;margin-top:2px}.cs-empty{text-align:center;color:#94a3b8;font-size:.62rem;padding:1.4rem 0}.cs-insight{border-left:3px solid #3b82f6;background:#f8fafc;border-radius:7px;padding:9px 10px;font-size:.6rem;color:#475569;margin-bottom:7px}.cs-insight strong{color:#111827}.cs-footer{font-size:.56rem;color:#94a3b8;display:flex;justify-content:space-between;padding:.1rem .1rem}
    </style>
    """, unsafe_allow_html=True)


def _donut(frame: pd.DataFrame, name: str, value: str, total: int) -> go.Figure:
    fig = px.pie(frame, names=name, values=value, hole=.68, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="none", marker_line_width=0)
    fig.update_layout(height=220, margin=dict(l=0, r=0, t=4, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial", size=9, color=INK), showlegend=True, legend=dict(font=dict(size=8), orientation="v", x=.62, y=.5))
    fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=16, color=INK))
    return fig


def _safe_date(value: Any) -> str:
    return str(value or "")[:10]


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_css()
    projects = _records(database, "projects")
    documents = _records(database, "documents")
    drawings = _records(database, "drawings")
    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    boq = _records(database, "boq_items") or _records(database, "boq")
    construction = _records(database, "construction_activities")
    engineering = _records(database, "engineering_works")
    mep = _records(database, "mep_works")
    procurement = _records(database, "purchase_orders") or _records(database, "procurement")

    st.markdown('<div class="cs-dashboard">', unsafe_allow_html=True)
    selected = st.selectbox("Project", ["All Projects", *[_project_name(p) for p in projects]], label_visibility="collapsed", key="dashboard_project_filter")
    selected_project = next((p for p in projects if _project_name(p) == selected), None)
    project_id = str(selected_project.get("id")) if selected_project else None

    def scoped(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not project_id:
            return rows
        return [r for r in rows if str(r.get("project_id") or r.get("projectId")) == project_id]

    documents, drawings, tasks, rfis, boq = map(scoped, [documents, drawings, tasks, rfis, boq])
    construction, engineering, mep, procurement = map(scoped, [construction, engineering, mep, procurement])
    project_scope = [selected_project] if selected_project else projects

    today = datetime.now().date()
    period = st.date_input("Reporting period", value=(today - timedelta(days=30), today), label_visibility="collapsed", key="dashboard_date_range")
    period_start, period_end = (period if isinstance(period, tuple) and len(period) == 2 else (today - timedelta(days=30), today))

    boq_value = sum(_number(r.get("amount"), _number(r.get("quantity")) * _number(r.get("rate"))) for r in boq)
    active_tasks = sum(_status(r) in {"open", "in_progress", "review"} for r in tasks)
    completed_tasks = sum(_status(r) in {"completed", "closed"} for r in tasks)
    open_rfis = sum(_status(r) not in {"closed", "completed"} for r in rfis)
    active_works = sum(_status(r) == "in_progress" for r in construction + engineering + mep)
    work_rows = construction + engineering + mep
    work_progress = round(sum(_progress(r) for r in work_rows) / len(work_rows)) if work_rows else 0
    approved_documents = sum(bool(r.get("is_approved") or r.get("isApproved")) for r in documents)
    procurement_value = sum(_number(r.get("total"), _number(r.get("grand_total"), _number(r.get("amount")))) for r in procurement)

    st.markdown('<div class="cs-dash-head"><div><div class="cs-dash-title">Project Intelligence Dashboard</div><div class="cs-dash-subtitle">A single operating view across design, documentation, execution, procurement and project controls.</div></div></div>', unsafe_allow_html=True)

    kpis = [("Projects", len(project_scope), "Portfolio scope"), ("Active Work", active_works, f"{work_progress}% average work progress"), ("Work Progress", f"{work_progress}%", "Design + site signal"), ("BOQ Value", f"${boq_value:,.0f}", f"{len(boq)} cost items"), ("Drawings", len(drawings), "Drawing register"), ("Documents", len(documents), f"{approved_documents} approved"), ("Open RFIs", open_rfis, "Attention queue"), ("Active Tasks", active_tasks, f"{completed_tasks} completed")]
    cols = st.columns(4)
    for i, (label, value, note) in enumerate(kpis):
        with cols[i % 4]:
            st.markdown(f'<div class="cs-dash-kpi"><div class="cs-dash-kpi-label">{escape(label)}</div><div class="cs-dash-kpi-value">{escape(str(value))}</div><div class="cs-dash-kpi-note">{escape(note)}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Portfolio status</div><div class="cs-dash-panel-note">Project mix within the selected scope</div>', unsafe_allow_html=True)
        counts: dict[str, int] = {}
        for project in project_scope:
            key = _status(project, "planning")
            counts[key] = counts.get(key, 0) + 1
        if counts:
            frame = pd.DataFrame({"Status": list(counts), "Count": list(counts.values())})
            fig = px.bar(frame, x="Status", y="Count", color="Status", color_discrete_sequence=PALETTE, text="Count")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=230, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
            fig.update_xaxes(showgrid=False,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7),dtick=1)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">Create projects to populate the portfolio view.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Workstream progress</div><div class="cs-dash-panel-note">Average progress from recorded work items</div>', unsafe_allow_html=True)
        design_rows = engineering + mep
        design_progress = round(sum(_progress(r) for r in design_rows) / len(design_rows)) if design_rows else 0
        construction_progress = round(sum(_progress(r) for r in construction) / len(construction)) if construction else 0
        frame = pd.DataFrame({"Workstream": ["Design & engineering", "Construction"], "Progress": [design_progress, construction_progress]})
        fig = px.bar(frame, x="Progress", y="Workstream", orientation="h", range_x=[0,100], text="Progress")
        fig.update_traces(marker_color=BLUE, texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=230, margin=dict(l=0,r=22,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
        fig.update_xaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=False,title=None,tickfont=dict(size=7))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="cs-insight"><strong>Reporting window:</strong> {period_start} to {period_end}. Overall recorded work progress is <strong>{work_progress}%</strong>.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Documentation control</div><div class="cs-dash-panel-note">Document mix and approval state</div>', unsafe_allow_html=True)
        doc_counts: dict[str, int] = {}
        for doc in documents:
            key = str(doc.get("type") or doc.get("document_type") or "Other")
            doc_counts[key] = doc_counts.get(key, 0) + 1
        if doc_counts:
            frame = pd.DataFrame({"Type": list(doc_counts), "Count": list(doc_counts.values())})
            st.plotly_chart(_donut(frame, "Type", "Count", len(documents)), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No documents have been recorded.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Workflow distribution</div><div class="cs-dash-panel-note">Tasks and RFIs by current state</div>', unsafe_allow_html=True)
        task_states = sorted({_status(t) for t in tasks})
        rfi_states = sorted({_status(r) for r in rfis})
        workflow = [(f"Task · {_label(state)}", sum(_status(t) == state for t in tasks)) for state in task_states]
        workflow += [(f"RFI · {_label(state)}", sum(_status(r) == state for r in rfis)) for state in rfi_states]
        workflow = [(name, count) for name, count in workflow if count > 0][:8]
        if workflow:
            frame = pd.DataFrame({"State": [x[0] for x in workflow], "Count": [x[1] for x in workflow]})
            fig = px.bar(frame, x="Count", y="State", orientation="h", text="Count")
            fig.update_traces(marker_color=BLUE, textposition="outside")
            fig.update_layout(height=220, margin=dict(l=0,r=24,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
            fig.update_xaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=False,title=None,tickfont=dict(size=7))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No workflow records yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left3, right3 = st.columns(2)
    with left3:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Commercial snapshot</div><div class="cs-dash-panel-note">Recorded BOQ and procurement signals</div>', unsafe_allow_html=True)
        commercial = pd.DataFrame({"Metric": ["BOQ value", "Procurement value"], "Value": [boq_value, procurement_value]})
        fig = px.bar(commercial, x="Metric", y="Value", text="Value")
        fig.update_traces(marker_color=BLUE, texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(height=210, margin=dict(l=0,r=20,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
        fig.update_xaxes(showgrid=False,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div class="cs-insight"><strong>BOQ basis:</strong> {len(boq)} items totaling <strong>${boq_value:,.0f}</strong>. Procurement records total <strong>${procurement_value:,.0f}</strong>.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right3:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Attention queue</div><div class="cs-dash-panel-note">Open RFIs and active tasks</div>', unsafe_allow_html=True)
        alerts = []
        for rfi in rfis:
            if _status(rfi) not in {"closed", "completed"}:
                alerts.append(("RFI", rfi.get("rfi_number") or rfi.get("rfiNumber") or "RFI", rfi.get("subject") or "Open information request", _status(rfi)))
        for task in tasks:
            if _status(task) not in {"closed", "completed"}:
                alerts.append(("Task", task.get("title") or "Untitled task", task.get("priority") or "Open project action", _status(task)))
        if alerts:
            for kind, title, detail, state in alerts[:8]:
                st.markdown(f'<div class="cs-alert"><strong>{escape(str(kind))}: {escape(str(title))}</strong><small>{escape(str(detail))} · {_label(str(state))}</small></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="cs-empty">No open workflow items. The queue is clear.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Portfolio register</div><div class="cs-dash-panel-note">Compact management view of current projects</div>', unsafe_allow_html=True)
    if project_scope:
        rows = []
        all_boq = _records(database, "boq_items") or _records(database, "boq")
        all_construction = _records(database, "construction_activities")
        for project in project_scope[:15]:
            pid = str(project.get("id"))
            project_boq = sum(_number(r.get("amount"), _number(r.get("quantity")) * _number(r.get("rate"))) for r in all_boq if str(r.get("project_id") or r.get("projectId")) == pid)
            project_work = [r for r in all_construction if str(r.get("project_id") or r.get("projectId")) == pid]
            project_progress = round(sum(_progress(r) for r in project_work) / len(project_work)) if project_work else (100 if _status(project, "planning") == "completed" else 0)
            rows.append({"Project": _project_name(project), "Code": project.get("code") or "", "Status": _label(_status(project, "planning")), "Progress": project_progress, "BOQ Value": project_boq})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, column_config={"Progress": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%d%%"), "BOQ Value": st.column_config.NumberColumn("BOQ Value", format="$%,.0f")})
    else:
        st.markdown('<div class="cs-empty">No projects recorded yet.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Recent documents</div><div class="cs-dash-panel-note">Latest controlled records</div>', unsafe_allow_html=True)
    project_map = {str(p.get("id")): _project_name(p) for p in projects}
    recent = sorted(documents, key=lambda x: str(x.get("date") or x.get("created_at") or x.get("createdAt") or ""), reverse=True)[:10]
    if recent:
        body = "".join(f"<tr><td>{escape(str(d.get('name') or d.get('title') or 'Untitled document'))}</td><td>{escape(str(d.get('project_name') or project_map.get(str(d.get('project_id') or d.get('projectId')), 'Unassigned')))}</td><td>{escape(str(d.get('type') or d.get('document_type') or 'Document'))}</td><td>{escape(str(d.get('revision') or 'A'))}</td><td>{escape(_safe_date(d.get('date') or d.get('created_at') or d.get('createdAt')))}</td><td><span class='cs-status-pill'>{'Approved' if d.get('is_approved') or d.get('isApproved') else 'Draft'}</span></td></tr>" for d in recent)
        st.markdown(f'<div style="overflow:auto"><table class="cs-dash-table"><thead><tr><th>Document</th><th>Project</th><th>Type</th><th>Revision</th><th>Date</th><th>Status</th></tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="cs-empty">No documents have been recorded.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="cs-footer"><span>Reporting window: {period_start} to {period_end}</span><span>{active_tasks} active tasks · {open_rfis} open RFIs · {work_progress}% work progress</span></div></div>', unsafe_allow_html=True)
