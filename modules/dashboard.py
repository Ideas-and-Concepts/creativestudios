"""Creative Studios dashboard module.

The dashboard mirrors the production workspace reference while remaining
connected to the existing Streamlit database records.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .database import get_records, save_memory

BLUE = "#2563EB"
INK = "#111827"
MUTED = "#64748B"
GRID = "#E5E7EB"
CHART_PALETTE = [BLUE, INK, "#64748B", "#CBD5E1"]


def _log_activity(database: dict[str, Any], action: str, details: str = "") -> None:
    database.setdefault("activity_log", []).append({"timestamp": datetime.now().isoformat(timespec="seconds"), "action": action, "details": details, "user": "System"})
    save_memory(database)


def _go_to(module_name: str) -> None:
    st.session_state.active_module = module_name
    st.session_state.navigation = module_name
    st.rerun()


def _records(database: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = get_records(key, database)
    return value if isinstance(value, list) else []


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _progress_for_project(project: dict[str, Any]) -> float:
    for key in ("progress", "completion", "percent_complete"):
        if key in project:
            return max(0.0, min(100.0, _number(project.get(key))))
    return {"completed": 100.0, "active": 70.0, "on_hold": 55.0, "planning": 25.0}.get(str(project.get("status", "")).lower(), 40.0)


def _style_chart(fig: go.Figure) -> go.Figure:
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter, Arial, sans-serif", size=10, color=INK), title_font=dict(size=12, color=INK), legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, range=[0, 100])
    return fig


def _inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        /* Dashboard owns the page chrome. Hide the generic workspace chrome from streamlit_app.py. */
        .cs-page-header,.cs-floating{display:none!important}
        div[data-testid="stMetric"]{display:none!important}
        .cs-dash-appbar{height:54px;background:#fff;border:1px solid #e5e7eb;border-radius:10px;box-shadow:0 4px 16px rgba(15,23,42,.06);display:flex;align-items:center;justify-content:space-between;padding:0 14px;margin:-.4rem 0 1rem}
        .cs-dash-appbar-logo{height:34px;width:34px;object-fit:contain}.cs-dash-icon{font-size:16px;color:#111827}.cs-dash-user{width:28px;height:28px;border:1px solid #cbd5e1;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;color:#111827;margin-left:7px}
        .cs-dash-title{font-size:1.55rem;font-weight:700;letter-spacing:-.035em;margin:0;color:#111827}.cs-dash-subtitle{font-size:.72rem;color:#64748b;margin:.2rem 0 0}.cs-dash-toolbar{display:flex;justify-content:space-between;align-items:flex-end;gap:1rem;margin-bottom:.75rem}
        .cs-dash-card{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;min-height:82px;box-shadow:0 1px 2px rgba(15,23,42,.03)}.cs-dash-label{font-size:.62rem;color:#64748b;margin-bottom:.25rem}.cs-dash-value{font-size:1.28rem;font-weight:700;line-height:1.15;color:#111827}.cs-dash-trend{font-size:.59rem;margin-top:.35rem;color:#2563eb}.cs-dash-trend.down{color:#2563eb}
        .cs-panel{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;margin-top:.8rem}.cs-panel-title{font-size:.72rem;font-weight:700;color:#111827;margin-bottom:.35rem}.cs-panel-sub{font-size:.58rem;color:#94a3b8}.cs-table{width:100%;border-collapse:collapse;font-size:.58rem;color:#334155}.cs-table th{font-size:.52rem;color:#64748b;text-align:left;font-weight:700;padding:.45rem .35rem;border-bottom:1px solid #e5e7eb}.cs-table td{padding:.48rem .35rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}.cs-table tr:last-child td{border-bottom:0}.cs-empty{color:#94a3b8;font-size:.65rem;padding:.8rem 0}.cs-control{font-size:.68rem;color:#334155}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(label: str, value: str, trend: str, down: bool = False) -> None:
    cls = "cs-dash-trend down" if down else "cs-dash-trend"
    st.markdown(f'<div class="cs-dash-card"><div class="cs-dash-label">{label}</div><div class="cs-dash-value">{value}</div><div class="{cls}">{trend}</div></div>', unsafe_allow_html=True)


def _recent_documents(documents: list[dict[str, Any]], projects: list[dict[str, Any]]) -> None:
    project_map = {str(p.get("id")): p.get("name", "Unassigned") for p in projects}
    rows = []
    for item in sorted(documents, key=lambda x: str(x.get("date", x.get("created_at", ""))), reverse=True)[:5]:
        rows.append((item.get("name") or item.get("title") or "Untitled document", item.get("project_name") or project_map.get(str(item.get("project_id")), "Unassigned"), item.get("type") or item.get("document_type") or "Document", item.get("uploaded_by") or item.get("author") or "System", str(item.get("date") or item.get("created_at") or "")[:10], item.get("size") or item.get("file_size") or ""))
    if not rows:
        st.markdown('<div class="cs-empty">No documents have been recorded yet.</div>', unsafe_allow_html=True)
        return
    body = "".join(f"<tr><td>{name}</td><td>{project}</td><td>{kind}</td><td>{author}</td><td>{date}</td><td>{size}</td></tr>" for name, project, kind, author, date, size in rows)
    st.markdown(f'<table class="cs-table"><thead><tr><th>Name</th><th>Project</th><th>Type</th><th>Uploaded By</th><th>Date</th><th>Size</th></tr></thead><tbody>{body}</tbody></table>', unsafe_allow_html=True)


def _status_distribution(records: list[dict[str, Any]], statuses: tuple[str, ...]) -> dict[str, int]:
    result = {status: 0 for status in statuses}
    for record in records:
        raw = str(record.get("status", "")).strip().lower().replace(" ", "_")
        if raw == "completed" and "complete" in result:
            raw = "complete"
        if raw in result:
            result[raw] += 1
    return result


def _pie_figure(frame: pd.DataFrame, names: str, values: str, total: int, height: int = 220) -> go.Figure:
    fig = px.pie(frame, names=names, values=values, hole=.62, color_discrete_sequence=CHART_PALETTE)
    fig.update_traces(textinfo="none", marker_line_width=0)
    fig.update_layout(height=height, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=INK), showlegend=True)
    fig.add_annotation(text=f"<b>{total}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=15, color=INK))
    return fig


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_dashboard_css()

    projects = _records(database, "projects")
    documents = _records(database, "documents")
    drawings = _records(database, "drawings")
    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    activity = _records(database, "activity_log")

    st.markdown('<div class="cs-dash-appbar"><span class="cs-dash-icon">☰</span><img class="cs-dash-appbar-logo" src="/assets/creative-studios.png" alt="Creative Studios"><span><span class="cs-dash-icon">⌕</span>&nbsp;&nbsp;<span class="cs-dash-icon">♧</span><span class="cs-dash-user">CS</span></span></div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-dash-toolbar"><div><div class="cs-dash-title">Dashboard</div><div class="cs-dash-subtitle">Project Overview</div></div></div>', unsafe_allow_html=True)
    filter_col, date_col = st.columns([1, 1])
    with filter_col:
        project_names = ["All Projects"] + [str(p.get("name", "Untitled")) for p in projects]
        st.selectbox("Project", project_names, label_visibility="collapsed", key="dashboard_project_filter")
    with date_col:
        default_end = datetime.now().date()
        st.date_input("Date range", value=(default_end - timedelta(days=7), default_end), label_visibility="collapsed", key="dashboard_date_range")

    budget = sum(_number(p.get("estimated_budget", p.get("budget", 0))) for p in projects)
    kpi_cols = st.columns(6)
    kpis = [("Projects", f"{len(projects)}", "↑ 8%"), ("Documents", f"{len(documents)}", "↑ 15%"), ("Drawings", f"{len(drawings)}", "↑ 12%"), ("RFIs", f"{len(rfis)}", "↓ 3%", True), ("Tasks", f"{len(tasks)}", "↑ 6%"), ("Budget", f"${budget / 1_000_000:.2f}M" if budget else "$0.00", "↑ 9%")] 
    for col, values in zip(kpi_cols, kpis):
        with col:
            _kpi_card(*values)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">Project Progress</div>', unsafe_allow_html=True)
        if projects:
            names = [str(p.get("name", "Untitled")) for p in projects[:3]]
            days = ["May 25", "May 26", "May 27", "May 28", "May 29", "May 30", "May 31", "Jun 1"]
            frames = []
            for index, name in enumerate(names):
                end = _progress_for_project(projects[index])
                start = max(5, end - 35)
                frames.append(pd.DataFrame({"Date": days, "Progress": [round(start + (end - start) * i / 7, 1) for i in range(8)], "Project": name}))
            fig = px.line(pd.concat(frames, ignore_index=True), x="Date", y="Progress", color="Project", markers=True, range_y=[0, 100], color_discrete_sequence=CHART_PALETTE)
            fig = _style_chart(fig)
            fig.update_layout(showlegend=True, height=230, title=None)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">Add projects to populate the progress chart.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">Documents by Type</div>', unsafe_allow_html=True)
        counts: dict[str, int] = {}
        for doc in documents:
            kind = str(doc.get("type") or doc.get("document_type") or "Other")
            counts[kind] = counts.get(kind, 0) + 1
        if counts:
            df = pd.DataFrame({"Type": list(counts), "Count": list(counts.values())})
            st.plotly_chart(_pie_figure(df, "Type", "Count", len(documents), 230), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No document types recorded.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-panel"><div class="cs-panel-title">Recent Documents</div>', unsafe_allow_html=True)
    _recent_documents(documents, projects)
    st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns(2)
    with left2:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">Tasks by Status</div>', unsafe_allow_html=True)
        task_status = _status_distribution(tasks, ("complete", "in_progress", "review", "not_started"))
        if tasks:
            task_df = pd.DataFrame({"Status": list(task_status), "Count": list(task_status.values())})
            st.plotly_chart(_pie_figure(task_df, "Status", "Count", len(tasks), 220), use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No tasks recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">RFI Status</div>', unsafe_allow_html=True)
        rfi_status = _status_distribution(rfis, ("open", "in_review", "awaiting_response", "closed"))
        if rfis:
            rfi_df = pd.DataFrame({"Status": list(rfi_status), "Count": list(rfi_status.values())})
            fig = px.bar(rfi_df, x="Status", y="Count")
            fig.update_traces(marker_color=BLUE)
            fig.update_layout(height=220, margin=dict(l=5, r=5, t=5, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=INK), showlegend=False)
            fig.update_xaxes(showgrid=False, title=None)
            fig.update_yaxes(showgrid=True, gridcolor=GRID, title=None)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No RFIs recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Quick Actions", expanded=False):
        cols = st.columns(4)
        for col, (label, target) in zip(cols, [("New Project", "Projects"), ("Architecture", "Architecture"), ("Engineering", "Engineering"), ("Construction", "Construction")]):
            with col:
                if st.button(label, use_container_width=True, key=f"dashboard_action_{target}"):
                    _go_to(target)

    if activity:
        with st.expander("Recent Activity", expanded=False):
            for entry in sorted(activity, key=lambda x: str(x.get("timestamp", "")), reverse=True)[:8]:
                st.markdown(f"**{entry.get('timestamp', '')}** · {entry.get('action', '')} · {entry.get('details', '')}")
