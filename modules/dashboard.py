"""Database-backed Creative Studios dashboard for the Streamlit workspace."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .database import get_records

BLUE = "#3B82F6"
INK = "#111827"
MUTED = "#64748B"
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


def _progress(project: dict[str, Any]) -> float:
    for key in ("progress", "completion", "percent_complete"):
        if project.get(key) is not None:
            return max(0, min(100, _number(project.get(key))))
    return {"completed": 100, "active": 74, "on_hold": 56, "planning": 28, "cancelled": 0}.get(_status(project, "planning"), 42)


def _project_filter(projects: list[dict[str, Any]]) -> str:
    names = [str(p.get("name") or p.get("code") or "Untitled") for p in projects]
    return st.selectbox("Project", ["All Projects", *names], label_visibility="collapsed", key="dashboard_project_filter")


def _donut(frame: pd.DataFrame, name: str, value: str, total: int, height: int = 220) -> go.Figure:
    fig = px.pie(frame, names=name, values=value, hole=.64, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="none", marker_line_width=0)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial", size=9, color=INK), showlegend=True, legend=dict(font=dict(size=8), orientation="v", x=.62, y=.5))
    fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=16, color=INK))
    return fig


def _inject_dashboard_css() -> None:
    st.markdown("""
    <style>
    .cs-dashboard{color:#111827}.cs-dash-head{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:0 0 16px}.cs-dash-title{font-size:1.55rem;line-height:1.15;font-weight:750;letter-spacing:-.035em;margin:0}.cs-dash-subtitle{font-size:.7rem;color:#64748b;margin-top:.25rem}
    .cs-dash-kpi{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.72rem .78rem;min-height:82px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-dash-kpi-label{font-size:.61rem;color:#64748b}.cs-dash-kpi-value{font-size:1.3rem;font-weight:750;line-height:1.15;margin-top:.4rem}.cs-dash-kpi-note{font-size:.58rem;color:#64748b;margin-top:.35rem}
    .cs-dash-panel{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;margin-bottom:.65rem}.cs-dash-panel-title{font-size:.68rem;font-weight:750;margin-bottom:.3rem}.cs-dash-table{width:100%;border-collapse:collapse;font-size:.56rem;color:#334155}.cs-dash-table th{font-size:.5rem;color:#64748b;text-align:left;padding:.4rem .3rem;border-bottom:1px solid #e5e7eb}.cs-dash-table td{padding:.45rem .3rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}.cs-dash-empty{text-align:center;color:#94a3b8;font-size:.62rem;padding:1.5rem 0}.cs-progress-wrap{display:flex;align-items:center;gap:7px;min-width:90px}.cs-progress-track{height:6px;flex:1;background:#eef2f7;border-radius:99px;overflow:hidden}.cs-progress-fill{height:100%;background:#3b82f6;border-radius:99px}.cs-status-pill{display:inline-block;border-radius:999px;padding:3px 7px;background:#eff6ff;color:#2563eb;font-weight:700;font-size:.5rem}
    </style>
    """, unsafe_allow_html=True)


def _recent_documents(documents: list[dict[str, Any]], projects: list[dict[str, Any]]) -> None:
    project_map = {str(p.get("id")): p.get("name", "Unassigned") for p in projects}
    rows = sorted(documents, key=lambda x: str(x.get("date") or x.get("created_at") or ""), reverse=True)[:8]
    if not rows:
        st.markdown('<div class="cs-dash-empty">No documents have been recorded yet.</div>', unsafe_allow_html=True)
        return
    body = "".join(
        f"<tr><td>{r.get('name') or r.get('title') or 'Untitled document'}</td><td>{r.get('project_name') or project_map.get(str(r.get('project_id')), 'Unassigned')}</td><td>{r.get('type') or r.get('document_type') or 'Document'}</td><td>{r.get('revision') or 'A'}</td><td>{str(r.get('date') or r.get('created_at') or '')[:10]}</td><td><span class='cs-status-pill'>{'Approved' if r.get('is_approved') or r.get('isApproved') else 'Draft'}</span></td></tr>"
        for r in rows
    )
    st.markdown(f'<div style="overflow:auto"><table class="cs-dash-table"><thead><tr><th>Name</th><th>Project</th><th>Type</th><th>Revision</th><th>Date</th><th>Status</th></tr></thead><tbody>{body}</tbody></table></div>', unsafe_allow_html=True)


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_dashboard_css()
    projects = _records(database, "projects")
    documents = _records(database, "documents")
    drawings = _records(database, "drawings")
    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    boq = _records(database, "boq_items") or _records(database, "boq")
    construction = _records(database, "construction_activities")
    engineering = _records(database, "engineering_works")
    mep = _records(database, "mep_works")

    selected = _project_filter(projects)
    selected_project = next((p for p in projects if str(p.get("name") or p.get("code") or "Untitled") == selected), None)
    project_id = str(selected_project.get("id")) if selected_project else None

    def filter_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return rows if not project_id else [r for r in rows if str(r.get("project_id") or r.get("projectId")) == project_id]

    if project_id:
        documents, drawings, tasks, rfis, boq = map(filter_rows, [documents, drawings, tasks, rfis, boq])
        construction, engineering, mep = map(filter_rows, [construction, engineering, mep])
        projects_for_chart = [selected_project]
    else:
        projects_for_chart = projects

    today = datetime.now().date()
    st.date_input("Reporting period", value=(today - timedelta(days=30), today), label_visibility="collapsed", key="dashboard_date_range")

    boq_value = sum(_number(r.get("amount"), _number(r.get("quantity")) * _number(r.get("rate"))) for r in boq)
    active_tasks = sum(_status(r) in {"open", "in_progress", "review"} for r in tasks)
    open_rfis = sum(_status(r) not in {"closed", "completed"} for r in rfis)
    active_works = sum(_status(r) == "in_progress" for r in construction + engineering + mep)
    work_rows = construction + engineering + mep
    work_progress = round(sum(_number(r.get("progress")) for r in work_rows) / len(work_rows)) if work_rows else 0
    avg_project_progress = round(sum(_progress(p) for p in projects_for_chart) / len(projects_for_chart)) if projects_for_chart else 0

    st.markdown('<div class="cs-dash-head"><div><div class="cs-dash-title">Project Dashboard</div><div class="cs-dash-subtitle">Live project, design, construction and commercial intelligence</div></div></div>', unsafe_allow_html=True)
    kpis = [
        ("Projects", len(projects_for_chart), "Live database count"),
        ("Documents", len(documents), "Controlled records"),
        ("Drawings", len(drawings), "Drawing register"),
        ("Active Work", active_works, f"{work_progress}% avg work progress"),
        ("Open RFIs", open_rfis, "Requires attention"),
        ("BOQ Value", f"${boq_value:,.0f}" if boq_value else "$0", f"{len(boq)} BOQ items"),
    ]
    cols = st.columns(6)
    for col, (label, value, note) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="cs-dash-kpi"><div class="cs-dash-kpi-label">{label}</div><div class="cs-dash-kpi-value">{value}</div><div class="cs-dash-kpi-note">{note}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Project Status</div>', unsafe_allow_html=True)
        status_counts: dict[str, int] = {}
        for p in projects_for_chart:
            key = _status(p, "planning")
            status_counts[key] = status_counts.get(key, 0) + 1
        if status_counts:
            frame = pd.DataFrame({"Status": list(status_counts), "Count": list(status_counts.values())})
            fig = px.bar(frame, x="Status", y="Count", color="Status", color_discrete_sequence=PALETTE)
            fig.update_layout(height=220, margin=dict(l=0,r=0,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
            fig.update_xaxes(showgrid=False,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7),dtick=1)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-dash-empty">Add projects to populate the status chart.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Work Progress</div>', unsafe_allow_html=True)
        progress_frame = pd.DataFrame({"Metric": ["Design & Engineering", "Construction"], "Progress": [round(sum(_number(r.get("progress")) for r in engineering + mep) / max(len(engineering + mep), 1)), round(sum(_number(r.get("progress")) for r in construction) / max(len(construction), 1))]})
        fig = px.bar(progress_frame, x="Progress", y="Metric", orientation="h", range_x=[0,100], text="Progress")
        fig.update_traces(marker_color=BLUE, texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=220, margin=dict(l=0,r=20,t=8,b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8,color=INK), showlegend=False)
        fig.update_xaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=False,title=None,tickfont=dict(size=7))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.caption(f"Average project progress: {avg_project_progress}%")
        st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Documents by Type</div>', unsafe_allow_html=True)
        counts: dict[str, int] = {}
        for doc in documents:
            key = str(doc.get("type") or doc.get("document_type") or "Other")
            counts[key] = counts.get(key, 0) + 1
        if counts:
            frame = pd.DataFrame({"Type": list(counts), "Count": list(counts.values())})
            st.plotly_chart(_donut(frame, "Type", "Count", len(documents)), use_container_width=True, config={"displayModeBar": False})
        else: st.markdown('<div class="cs-dash-empty">No documents yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with right2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Tasks & RFIs</div>', unsafe_allow_html=True)
        frame = pd.DataFrame({"Metric": ["Active Tasks", "Completed Tasks", "Open RFIs", "Closed RFIs"], "Count": [active_tasks, sum(_status(r) == "completed" for r in tasks), open_rfis, sum(_status(r) in {"closed", "completed"} for r in rfis)]})
        fig = px.bar(frame, x="Metric", y="Count", color="Metric", color_discrete_sequence=PALETTE)
        fig.update_layout(height=220,margin=dict(l=0,r=0,t=8,b=0),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(size=8,color=INK),showlegend=False)
        fig.update_xaxes(showgrid=False,title=None,tickfont=dict(size=7)); fig.update_yaxes(showgrid=True,gridcolor=GRID,title=None,tickfont=dict(size=7),dtick=1)
        st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Project Performance</div>', unsafe_allow_html=True)
    if projects_for_chart:
        rows = []
        for p in projects_for_chart[:12]:
            rows.append({"Project": p.get("name") or p.get("code") or "Untitled", "Status": _status(p, "planning"), "Progress": round(_progress(p)), "BOQ Value": sum(_number(r.get("amount"), _number(r.get("quantity")) * _number(r.get("rate"))) for r in boq if str(r.get("project_id") or r.get("projectId")) == str(p.get("id"))) if not project_id else boq_value})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True, column_config={"Progress": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%d%%"), "BOQ Value": st.column_config.NumberColumn("BOQ Value", format="$%,.0f")})
    else: st.markdown('<div class="cs-dash-empty">No projects recorded yet.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Recent Documents</div>', unsafe_allow_html=True)
    _recent_documents(documents, projects)
    st.markdown('</div>', unsafe_allow_html=True)
