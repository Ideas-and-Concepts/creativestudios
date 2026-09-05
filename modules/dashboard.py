"""Creative Studios executive dashboard.

The dashboard deliberately reads canonical relational records when Neon is
configured. This prevents the Streamlit dashboard from becoming stale when
Projects, Documents, Drawings, BOQ or Procurement are edited from either the
Streamlit or Next.js application.
"""
from __future__ import annotations

from html import escape
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from .database import database_backend, get_records, get_relational_documents, get_relational_drawings, get_relational_projects
from .boq_repository import get_relational_boq_items
from .procurement_repository import get_relational_purchase_orders


STATUS_ORDER = ["planning", "active", "on_hold", "completed", "cancelled"]
STATUS_LABELS = {
    "planning": "Planning",
    "active": "Active",
    "on_hold": "On hold",
    "completed": "Completed",
    "cancelled": "Cancelled",
}


def _records(database: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return records from the active source of truth."""
    if database_backend() == "neon":
        relational = {
            "projects": get_relational_projects,
            "documents": get_relational_documents,
            "drawings": get_relational_drawings,
            "boq": get_relational_boq_items,
            "boq_items": get_relational_boq_items,
            "purchase_orders": get_relational_purchase_orders,
        }.get(key)
        if relational:
            return relational()
    rows = get_records(key, database)
    return rows if isinstance(rows, list) else []


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _status(row: dict[str, Any], default: str = "open") -> str:
    return str(row.get("status") or default).strip().lower().replace(" ", "_")


def _progress(row: dict[str, Any]) -> float:
    for key in ("progress", "completion", "percent_complete", "percentComplete"):
        if row.get(key) is not None:
            return max(0.0, min(100.0, _number(row.get(key))))
    return 100.0 if _status(row, "planning") == "completed" else 0.0


def _project_name(row: dict[str, Any]) -> str:
    code = str(row.get("code") or "").strip()
    name = str(row.get("name") or "Untitled").strip()
    return f"{code} | {name}" if code else name


def _scope(rows: list[dict[str, Any]], project_id: str | None) -> list[dict[str, Any]]:
    if not project_id:
        return rows
    return [r for r in rows if str(r.get("project_id") or r.get("projectId")) == project_id]


def _panel(title: str, note: str = "") -> None:
    st.markdown(
        f'<div class="cs-dash-panel-title">{escape(title)}</div>'
        f'<div class="cs-dash-panel-note">{escape(note)}</div>',
        unsafe_allow_html=True,
    )


def _inject_css() -> None:
    st.markdown("""
    <style>
    .cs-dashboard{color:#111827}.cs-dash-head{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:0 0 14px}.cs-dash-title{font-size:1.55rem;line-height:1.15;font-weight:800;letter-spacing:-.035em}.cs-dash-subtitle{font-size:.7rem;color:#64748b;margin-top:.25rem}.cs-dash-kpi{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:.72rem .78rem;min-height:88px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-dash-kpi-label{font-size:.61rem;color:#64748b}.cs-dash-kpi-value{font-size:1.32rem;font-weight:800;line-height:1.15;margin-top:.4rem}.cs-dash-kpi-note{font-size:.58rem;color:#64748b;margin-top:.35rem}.cs-dash-panel{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:.8rem .85rem;margin-bottom:.7rem}.cs-dash-panel-title{font-size:.69rem;font-weight:800}.cs-dash-panel-note{font-size:.57rem;color:#94a3b8;margin-top:.15rem}.cs-empty{text-align:center;color:#94a3b8;font-size:.62rem;padding:1.4rem 0}.cs-insight{border-left:3px solid #3b82f6;background:#f8fafc;border-radius:7px;padding:9px 10px;font-size:.6rem;color:#475569;margin-bottom:7px}.cs-insight strong{color:#111827}
    </style>
    """, unsafe_allow_html=True)


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_css()

    try:
        projects = _records(database, "projects")
        documents = _records(database, "documents")
        drawings = _records(database, "drawings")
        boq = _records(database, "boq_items")
        if not boq:
            boq = _records(database, "boq")
        procurement = _records(database, "purchase_orders")
        if not procurement:
            procurement = _records(database, "procurement")
    except Exception as exc:
        st.error("Unable to load dashboard data from the shared workspace.")
        with st.expander("Technical details"):
            st.exception(exc)
        return

    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    construction = _records(database, "construction_activities")
    engineering = _records(database, "engineering_works")
    mep = _records(database, "mep_works")

    project_labels = ["All Projects", *[_project_name(p) for p in projects]]
    selected = st.selectbox("Project", project_labels, label_visibility="collapsed", key="dashboard_project_filter")
    selected_project = next((p for p in projects if _project_name(p) == selected), None)
    project_id = str(selected_project.get("id")) if selected_project else None

    if project_id:
        documents = _scope(documents, project_id)
        drawings = _scope(drawings, project_id)
        boq = _scope(boq, project_id)
        procurement = _scope(procurement, project_id)
        tasks = _scope(tasks, project_id)
        rfis = _scope(rfis, project_id)
        construction = _scope(construction, project_id)
        engineering = _scope(engineering, project_id)
        mep = _scope(mep, project_id)

    project_scope = [selected_project] if selected_project else projects
    work_rows = construction + engineering + mep
    design_rows = engineering + mep
    work_progress = round(sum(_progress(r) for r in work_rows) / len(work_rows)) if work_rows else 0
    design_progress = round(sum(_progress(r) for r in design_rows) / len(design_rows)) if design_rows else 0
    construction_progress = round(sum(_progress(r) for r in construction) / len(construction)) if construction else 0

    boq_value = sum(_number(r.get("amount"), _number(r.get("quantity")) * _number(r.get("rate"))) for r in boq)
    procurement_value = sum(_number(r.get("total"), _number(r.get("grand_total"), _number(r.get("amount")))) for r in procurement)
    active_tasks = sum(_status(r) in {"open", "in_progress", "review"} for r in tasks)
    completed_tasks = sum(_status(r) in {"completed", "closed"} for r in tasks)
    open_rfis = sum(_status(r) not in {"closed", "completed"} for r in rfis)
    approved_documents = sum(bool(r.get("is_approved") or r.get("isApproved") or _status(r) == "approved") for r in documents)
    active_works = sum(_status(r) in {"in_progress", "active"} for r in work_rows)

    st.markdown('<div class="cs-dashboard">', unsafe_allow_html=True)
    st.markdown('<div class="cs-dash-head"><div><div class="cs-dash-title">Project Intelligence Dashboard</div><div class="cs-dash-subtitle">A live operating view across projects, design, documentation, procurement, construction and project controls.</div></div></div>', unsafe_allow_html=True)

    kpis = [
        ("Projects", len(project_scope), "Portfolio scope"),
        ("Active Work", active_works, f"{work_progress}% recorded progress"),
        ("Work Progress", f"{work_progress}%", "Design + site signal"),
        ("BOQ Value", f"${boq_value:,.0f}", f"{len(boq)} cost items"),
        ("Drawings", len(drawings), "Drawing register"),
        ("Documents", len(documents), f"{approved_documents} approved"),
        ("Open RFIs", open_rfis, "Attention queue"),
        ("Active Tasks", active_tasks, f"{completed_tasks} completed"),
    ]
    cols = st.columns(4)
    for index, (label, value, note) in enumerate(kpis):
        with cols[index % 4]:
            st.markdown(f'<div class="cs-dash-kpi"><div class="cs-dash-kpi-label">{escape(label)}</div><div class="cs-dash-kpi-value">{escape(str(value))}</div><div class="cs-dash-kpi-note">{escape(note)}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown('<div class="cs-dash-panel">', unsafe_allow_html=True)
        _panel("Portfolio status", "Project mix within the selected scope")
        counts = {}
        for project in project_scope:
            state = _status(project, "planning")
            counts[state] = counts.get(state, 0) + 1
        ordered = [(s, counts[s]) for s in STATUS_ORDER if counts.get(s)]
        if ordered:
            frame = pd.DataFrame({"Status": [STATUS_LABELS.get(s, s.title()) for s, _ in ordered], "Projects": [n for _, n in ordered]})
            fig = px.bar(frame, x="Status", y="Projects", text="Projects")
            fig.update_traces(textposition="outside")
            fig.update_layout(height=245, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9))
            fig.update_xaxes(showgrid=False, title=None); fig.update_yaxes(showgrid=True, title=None, dtick=1)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">Create projects to populate the portfolio view.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cs-dash-panel">', unsafe_allow_html=True)
        _panel("Workstream progress", "Recorded progress, never inferred from missing data")
        frame = pd.DataFrame({"Workstream": ["Design & engineering", "Construction"], "Progress": [design_progress, construction_progress]})
        fig = px.bar(frame, x="Progress", y="Workstream", orientation="h", range_x=[0, 100], text="Progress")
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=245, margin=dict(l=0,r=24,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9))
        fig.update_xaxes(showgrid=True, title=None); fig.update_yaxes(showgrid=False, title=None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        source = "Neon PostgreSQL" if database_backend() == "neon" else "Local JSON"
        st.markdown(f'<div class="cs-insight"><strong>Source:</strong> {escape(source)}. Dashboard metrics are calculated from the current shared workspace records.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown('<div class="cs-dash-panel">', unsafe_allow_html=True)
        _panel("Documentation control", "Documents and drawing register health")
        frame = pd.DataFrame({"Metric": ["Documents", "Approved documents", "Drawings"], "Count": [len(documents), approved_documents, len(drawings)]})
        fig = px.bar(frame, x="Metric", y="Count", text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(height=230, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9))
        fig.update_xaxes(showgrid=False, title=None); fig.update_yaxes(showgrid=True, title=None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="cs-dash-panel">', unsafe_allow_html=True)
        _panel("Commercial snapshot", "BOQ and procurement values from the active project scope")
        frame = pd.DataFrame({"Metric": ["BOQ value", "Procurement value"], "Value": [boq_value, procurement_value]})
        fig = px.bar(frame, x="Metric", y="Value", text="Value")
        fig.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig.update_layout(height=230, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font=dict(size=9), yaxis_tickprefix="$", yaxis_tickformat=",")
        fig.update_xaxes(showgrid=False, title=None); fig.update_yaxes(showgrid=True, title=None)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
