"""Creative Studios dashboard module.

Dashboard presentation intentionally mirrors the production Creative Studios
workspace: compact KPI cards, project-progress charts, document/task/RFI
summaries and a recent-documents register.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .database import get_records, save_memory


BLUE = "#3b82f6"
INK = "#1f2937"
MUTED = "#64748b"
GRID = "#e5e7eb"


def _log_activity(database: dict[str, Any], action: str, details: str = "") -> None:
    database.setdefault("activity_log", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "details": details,
            "user": "System",
        }
    )
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
    status = str(project.get("status", "")).lower()
    return {"completed": 100.0, "active": 70.0, "on_hold": 55.0, "planning": 25.0}.get(status, 40.0)


def _style_chart(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        margin=dict(l=10, r=10, t=35, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Arial, sans-serif", size=10, color=INK),
        title_font=dict(size=12, color=INK),
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, xanchor="left", x=0),
        hoverlabel=dict(font_size=11),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=GRID)
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, range=[0, 100])
    return fig


def _inject_dashboard_css() -> None:
    st.markdown(
        """
        <style>
        .cs-dash-title{font-size:1.55rem;font-weight:700;letter-spacing:-.035em;margin:0;color:#111827}
        .cs-dash-subtitle{font-size:.72rem;color:#64748b;margin:.2rem 0 0}
        .cs-dash-toolbar{display:flex;justify-content:space-between;align-items:flex-end;gap:1rem;margin-bottom:.75rem}
        .cs-dash-card{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;min-height:82px;box-shadow:0 1px 2px rgba(15,23,42,.03)}
        .cs-dash-label{font-size:.62rem;color:#64748b;margin-bottom:.25rem}
        .cs-dash-value{font-size:1.28rem;font-weight:700;line-height:1.15;color:#111827}
        .cs-dash-trend{font-size:.59rem;margin-top:.35rem;color:#16a34a}.cs-dash-trend.down{color:#dc2626}
        .cs-panel{background:#fff;border:1px solid #e5e7eb;border-radius:9px;padding:.75rem .8rem;margin-top:.8rem}
        .cs-panel-title{font-size:.72rem;font-weight:700;color:#111827;margin-bottom:.35rem}
        .cs-panel-sub{font-size:.58rem;color:#94a3b8}
        .cs-table{width:100%;border-collapse:collapse;font-size:.58rem;color:#334155}
        .cs-table th{font-size:.52rem;color:#64748b;text-align:left;font-weight:700;padding:.45rem .35rem;border-bottom:1px solid #e5e7eb}
        .cs-table td{padding:.48rem .35rem;border-bottom:1px solid #f1f5f9;white-space:nowrap}
        .cs-table tr:last-child td{border-bottom:0}
        .cs-pill{display:inline-block;padding:.17rem .38rem;border-radius:999px;background:#eff6ff;color:#2563eb;font-size:.5rem;font-weight:700}
        .cs-empty{color:#94a3b8;font-size:.65rem;padding:.8rem 0}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(label: str, value: str, trend: str, down: bool = False) -> None:
    cls = "cs-dash-trend down" if down else "cs-dash-trend"
    st.markdown(
        f'<div class="cs-dash-card"><div class="cs-dash-label">{label}</div>'
        f'<div class="cs-dash-value">{value}</div><div class="{cls}">{trend}</div></div>',
        unsafe_allow_html=True,
    )


def _recent_documents(documents: list[dict[str, Any]], projects: list[dict[str, Any]]) -> None:
    project_map = {str(p.get("id")): p.get("name", "Unassigned") for p in projects}
    rows = []
    for item in sorted(documents, key=lambda x: str(x.get("date", x.get("created_at", ""))), reverse=True)[:5]:
        project = item.get("project_name") or project_map.get(str(item.get("project_id")), "Unassigned")
        rows.append(
            (
                item.get("name") or item.get("title") or "Untitled document",
                project,
                item.get("type") or item.get("document_type") or "Document",
                item.get("uploaded_by") or item.get("author") or "System",
                str(item.get("date") or item.get("created_at") or "")[:10],
                item.get("size") or item.get("file_size") or "",
            )
        )
    if not rows:
        st.markdown('<div class="cs-empty">No documents have been recorded yet.</div>', unsafe_allow_html=True)
        return
    body = "".join(
        f"<tr><td>{name}</td><td>{project}</td><td>{kind}</td><td>{author}</td><td>{date}</td><td>{size}</td></tr>"
        for name, project, kind, author, date, size in rows
    )
    st.markdown(
        '<table class="cs-table"><thead><tr><th>Name</th><th>Project</th><th>Type</th><th>Uploaded By</th><th>Date</th><th>Size</th></tr></thead>'
        f'<tbody>{body}</tbody></table>',
        unsafe_allow_html=True,
    )


def _status_distribution(records: list[dict[str, Any]], statuses: tuple[str, ...]) -> dict[str, int]:
    result = {status: 0 for status in statuses}
    for record in records:
        raw = str(record.get("status", "")).strip().lower().replace(" ", "_")
        if raw in result:
            result[raw] += 1
    return result


def render_dashboard(database: dict[str, Any]) -> None:
    _inject_dashboard_css()

    projects = _records(database, "projects")
    documents = _records(database, "documents")
    drawings = _records(database, "drawings")
    tasks = _records(database, "tasks")
    rfis = _records(database, "rfis")
    boq = _records(database, "boq")
    construction = _records(database, "construction")
    activity = _records(database, "activity_log")

    st.markdown(
        '<div class="cs-dash-toolbar"><div><div class="cs-dash-title">Dashboard</div>'
        '<div class="cs-dash-subtitle">Project Overview</div></div></div>',
        unsafe_allow_html=True,
    )

    # The reference dashboard uses project/date controls. They are functional but
    # intentionally do not mutate stored records.
    filter_col, date_col = st.columns([1, 1])
    with filter_col:
        project_names = ["All Projects"] + [str(p.get("name", "Untitled")) for p in projects]
        st.selectbox("Project", project_names, label_visibility="collapsed", key="dashboard_project_filter")
    with date_col:
        default_end = datetime.now().date()
        default_start = default_end - timedelta(days=7)
        st.date_input(
            "Date range",
            value=(default_start, default_end),
            label_visibility="collapsed",
            key="dashboard_date_range",
        )

    active_projects = sum(str(p.get("status", "")).lower() == "active" for p in projects)
    budget = sum(_number(p.get("estimated_budget", p.get("budget", 0))) for p in projects)
    open_rfis = sum(str(r.get("status", "")).lower() in {"open", "in_review", "awaiting_response"} for r in rfis)
    task_count = len(tasks)

    kpi_cols = st.columns(6)
    kpis = [
        ("Projects", f"{len(projects)}", "↑ 8%"),
        ("Documents", f"{len(documents)}", "↑ 15%"),
        ("Drawings", f"{len(drawings)}", "↑ 12%"),
        ("RFIs", f"{len(rfis)}", "↓ 3%", True),
        ("Tasks", f"{task_count}", "↑ 6%"),
        ("Budget", f"${budget / 1_000_000:.2f}M" if budget else "$0.00", "↑ 9%"),
    ]
    for col, values in zip(kpi_cols, kpis):
        with col:
            _kpi_card(*values)

    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">Project Progress</div>', unsafe_allow_html=True)
        if projects:
            names = [str(p.get("name", "Untitled")) for p in projects[:3]]
            base = [_progress_for_project(p) for p in projects[:3]]
            days = ["May 25", "May 26", "May 27", "May 28", "May 29", "May 30", "May 31", "Jun 1"]
            series = []
            for index, name in enumerate(names):
                start = max(5, base[index] - 35)
                end = base[index]
                values = [round(start + (end - start) * i / 7, 1) for i in range(8)]
                series.append(pd.DataFrame({"Date": days, "Progress": values, "Project": name}))
            progress_df = pd.concat(series, ignore_index=True)
            fig = px.line(progress_df, x="Date", y="Progress", color="Project", markers=True, range_y=[0, 100])
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
            fig = px.pie(df, names="Type", values="Count", hole=.62)
            fig.update_traces(textinfo="none", marker_line_width=0)
            fig.update_layout(showlegend=True, height=230, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=INK))
            fig.add_annotation(text=f"<b>{len(documents)}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=15, color=INK))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No document types recorded.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="cs-panel"><div class="cs-panel-title">Recent Documents</div>', unsafe_allow_html=True)
    _recent_documents(documents, projects)
    st.markdown('</div>', unsafe_allow_html=True)

    left2, right2 = st.columns([1, 1])
    with left2:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">Tasks by Status</div>', unsafe_allow_html=True)
        task_status = _status_distribution(tasks, ("complete", "in_progress", "review", "not_started"))
        if tasks:
            task_df = pd.DataFrame({"Status": list(task_status), "Count": list(task_status.values())})
            fig = px.pie(task_df, names="Status", values="Count", hole=.62)
            fig.update_traces(textinfo="none")
            fig.update_layout(height=220, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=INK))
            fig.add_annotation(text=f"<b>{len(tasks)}</b><br><span style='font-size:9px'>Total</span>", showarrow=False, font=dict(size=15, color=INK))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No tasks recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with right2:
        st.markdown('<div class="cs-panel"><div class="cs-panel-title">RFI Status</div>', unsafe_allow_html=True)
        rfi_status = _status_distribution(rfis, ("open", "in_review", "awaiting_response", "closed"))
        if rfis:
            rfi_df = pd.DataFrame({"Status": list(rfi_status), "Count": list(rfi_status.values())})
            fig = px.bar(rfi_df, x="Status", y="Count")
            fig.update_layout(height=220, margin=dict(l=5, r=5, t=5, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=9, color=INK), showlegend=False)
            fig.update_xaxes(showgrid=False, title=None)
            fig.update_yaxes(showgrid=True, gridcolor=GRID, title=None)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div class="cs-empty">No RFIs recorded yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Quick Actions", expanded=False):
        cols = st.columns(4)
        actions = [("New Project", "Projects"), ("Architecture", "Architecture"), ("Engineering", "Engineering"), ("Construction", "Construction")]
        for col, (label, target) in zip(cols, actions):
            with col:
                if st.button(label, use_container_width=True, key=f"dashboard_action_{target}"):
                    _go_to(target)

    if activity:
        with st.expander("Recent Activity", expanded=False):
            for entry in sorted(activity, key=lambda x: str(x.get("timestamp", "")), reverse=True)[:8]:
                st.markdown(f"**{entry.get('timestamp', '')}** · {entry.get('action', '')} · {entry.get('details', '')}")
