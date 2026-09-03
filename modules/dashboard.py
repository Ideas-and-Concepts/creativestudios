"""Creative Studios reference dashboard for the Streamlit workspace."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .database import get_records, save_memory

BLUE = "#3B82F6"
INK = "#111827"
MUTED = "#64748B"
GRID = "#E5E7EB"
PALETTE = ["#3B82F6", "#64748B", "#CBD5E1", "#94A3B8"]


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _records(database: dict[str, Any], key: str) -> list[dict[str, Any]]:
    rows = get_records(key, database)
    return rows if isinstance(rows, list) else []


def _progress(project: dict[str, Any]) -> float:
    for key in ("progress", "completion", "percent_complete"):
        if key in project:
            return max(0, min(100, _number(project.get(key))))
    return {"completed": 100, "active": 74, "on_hold": 56, "planning": 28, "cancelled": 12}.get(str(project.get("status", "")).lower(), 42)


def _status_counts(rows: list[dict[str, Any]], allowed: tuple[str, ...]) -> dict[str, int]:
    counts = {key: 0 for key in allowed}
    for row in rows:
        value = str(row.get("status", "")).strip().lower().replace(" ", "_")
        if value == "completed" and "complete" in counts:
            value = "complete"
        if value in counts:
            counts[value] += 1
    return counts


def _donut(frame: pd.DataFrame, name: str, value: str, total: int, height: int = 220) -> go.Figure:
    fig = px.pie(frame, names=name, values=value, hole=.64, color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="none", marker_line_width=0)
    fig.update_layout(height=height, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial", size=9, color=INK), showlegend=True, legend=dict(font=dict(size=8), orientation="v", x=.62, y=.5))
    fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=16, color=INK))
    return fig


def _inject_dashboard_css() -> None:
    st.markdown("""
    <style>
    .cs-dashboard{color:#111827}
    .cs-dash-head{display:flex;justify-content:space-between;align-items:flex-end;gap:18px;margin:0 0 16px}.cs-dash-title{font-size:1.55rem;line-height:1.15;font-weight:750;letter-spacing:-.035em;margin:0}.cs-dash-subtitle{font-size:.7rem;color:#64748b;margin-top:.25rem}
    .cs-dash-kpi{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.72rem .78rem;min-height:82px;box-shadow:0 1px 2px rgba(15,23,42,.025)}.cs-dash-kpi-label{font-size:.61rem;color:#64748b}.cs-dash-kpi-value{font-size:1.3rem;font-weight:750;line-height:1.15;margin-top:.4rem}.cs-dash-kpi-trend{font-size:.58rem;color:#16a34a;margin-top:.35rem}.cs-dash-kpi-trend.down{color:#dc2626}
    .cs-dash-panel{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;margin-bottom:.65rem}.cs-dash-panel-title{font-size:.68rem;font-weight:750;margin-bottom:.3rem}.cs-dash-table{width:100%;border-collapse:collapse;font-size:.56rem;color:#334155}.cs-dash-table th{font-size:.5rem;color:#64748b;text-align:left;padding:.4rem .3rem;border-bottom:1px solid #e5e7eb}.cs-dash-table td{padding:.45rem .3rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}.cs-dash-table tr:last-child td{border-bottom:0}.cs-dash-empty{text-align:center;color:#94a3b8;font-size:.62rem;padding:1.5rem 0}
    </style>
    """, unsafe_allow_html=True)


def _recent_documents(documents: list[dict[str, Any]], projects: list[dict[str, Any]]) -> None:
    project_map = {str(p.get("id")): p.get("name", "Unassigned") for p in projects}
    rows = sorted(documents, key=lambda x: str(x.get("date", x.get("created_at", ""))), reverse=True)[:5]
    if not rows:
        st.markdown('<div class="cs-dash-empty">No documents have been recorded yet.</div>', unsafe_allow_html=True)
        return
    body = "".join(f"<tr><td>{r.get('name') or r.get('title') or 'Untitled document'}</td><td>{r.get('project_name') or project_map.get(str(r.get('project_id')), 'Unassigned')}</td><td>{r.get('type') or r.get('document_type') or 'Document'}</td><td>{r.get('uploaded_by') or r.get('author') or 'System'}</td><td>{str(r.get('date') or r.get('created_at') or '')[:10]}</td><td>{r.get('size') or r.get('file_size') or ''}</td></tr>" for r in rows)
    st.markdown(f'<table class="cs-dash-table"><thead><tr><th>Name</th><th>Project</th><th>Type</th><th>Uploaded By</th><th>Date</th><th>Size</th></tr></thead><tbody>{body}</tbody></table>', unsafe_allow_html=True)


def _log_activity(database: dict[str, Any], action: str, details: str = "") -> None:
    database.setdefault("activity_log", []).append({"timestamp": datetime.now().isoformat(timespec="seconds"), "action": action, "details": details, "user": "System"})
    save_memory(database)


def _go_to(module_name: str) -> None:
    st.session_state.active_module = module_name
    st.session_state.navigation = module_name
    st.rerun()


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_dashboard_css()
    projects = _records(database, "projects")
    documents = _records(database, "documents")
    drawings = _records(database, "drawings")
    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    activity = _records(database, "activity_log")

    st.markdown('<div class="cs-dashboard">', unsafe_allow_html=True)
    st.markdown('<div class="cs-dash-head"><div><div class="cs-dash-title">Project Dashboard</div><div class="cs-dash-subtitle">Welcome back, Creative Studios</div></div></div>', unsafe_allow_html=True)
    filter_col, date_col = st.columns([1, 1])
    with filter_col:
        st.selectbox("Project", ["All Projects"] + [str(p.get("name", "Untitled")) for p in projects], label_visibility="collapsed", key="dashboard_project_filter")
    with date_col:
        today = datetime.now().date()
        st.date_input("Date range", value=(today - timedelta(days=7), today), label_visibility="collapsed", key="dashboard_date_range")

    budget = sum(_number(p.get("estimated_budget", p.get("budget", 0))) for p in projects)
    kpis = [("Projects", len(projects), "↑ 8%", False), ("Documents", len(documents), "↑ 15%", False), ("Drawings", len(drawings), "↑ 12%", False), ("RFIs", len(rfis), "↓ 3%", True), ("Tasks", len(tasks), "↑ 6%", False), ("Budget", f"${budget / 1_000_000:.2f}M" if budget else "$0.00", "↑ 9%", False)]
    cols = st.columns(6)
    for col, (label, value, trend, down) in zip(cols, kpis):
        with col:
            st.markdown(f'<div class="cs-dash-kpi"><div class="cs-dash-kpi-label">{label}</div><div class="cs-dash-kpi-value">{value}</div><div class="cs-dash-kpi-trend{" down" if down else ""}">{trend}</div></div>', unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Project Progress</div>', unsafe_allow_html=True)
        if projects:
            days = ["May 25", "May 26", "May 27", "May 28", "May 29", "May 30", "May 31", "Jun 1"]
            frames = []
            for index, project in enumerate(projects[:3]):
                end = _progress(project)
                start = max(5, end - 35)
                frames.append(pd.DataFrame({"Date": days, "Progress": [round(start + (end - start) * i / 7, 1) for i in range(8)], "Project": str(project.get("name", "Untitled"))}))
            fig = px.line(pd.concat(frames, ignore_index=True), x="Date", y="Progress", color="Project", markers=True, range_y=[0, 100], color_discrete_sequence=PALETTE)
            fig.update_layout(height=225, margin=dict(l=0, r=0, t=8, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8, color=INK), legend=dict(orientation="h", y=-.18, x=0))
            fig.update_xaxes(showgrid=False, title=None, linecolor=GRID, tickfont=dict(size=7))
            fig.update_yaxes(showgrid=True, gridcolor=GRID, title=None, tickfont=dict(size=7), range=[0, 100])
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-dash-empty">Add projects to populate the progress chart.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Documents by Type</div>', unsafe_allow_html=True)
        counts: dict[str, int] = {}
        for doc in documents:
            key = str(doc.get("type") or doc.get("document_type") or "Other")
            counts[key] = counts.get(key, 0) + 1
        if counts:
            frame = pd.DataFrame({"Type": list(counts), "Count": list(counts.values())})
            st.plotly_chart(_donut(frame, "Type", "Count", len(documents)), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-dash-empty">No document types recorded.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Recent Documents</div>', unsafe_allow_html=True)
    _recent_documents(documents, projects)
    st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">Tasks by Status</div>', unsafe_allow_html=True)
        counts = _status_counts(tasks, ("complete", "in_progress", "review", "not_started"))
        if tasks:
            frame = pd.DataFrame({"Status": list(counts), "Count": list(counts.values())})
            st.plotly_chart(_donut(frame, "Status", "Count", len(tasks)), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-dash-empty">No tasks recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="cs-dash-panel"><div class="cs-dash-panel-title">RFI Status</div>', unsafe_allow_html=True)
        counts = _status_counts(rfis, ("open", "in_review", "awaiting_response", "closed"))
        if rfis:
            frame = pd.DataFrame({"Status": list(counts), "Count": list(counts.values())})
            fig = px.bar(frame, x="Status", y="Count")
            fig.update_traces(marker_color=BLUE)
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=8, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=8, color=INK), showlegend=False)
            fig.update_xaxes(showgrid=False, title=None, tickfont=dict(size=7))
            fig.update_yaxes(showgrid=True, gridcolor=GRID, title=None, tickfont=dict(size=7))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-dash-empty">No RFIs recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    if activity:
        with st.expander("Activity", expanded=False):
            st.write(activity[-10:])
