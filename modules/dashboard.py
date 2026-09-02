"""Creative Studios dashboard module."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from .database import get_records, save_memory


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


def render_dashboard(database: dict[str, Any]) -> None:
    st.header("Dashboard")
    st.caption("Project overview and AEC workflow status.")

    projects = get_records("projects", database)
    documents = get_records("documents", database)
    architecture = get_records("architecture", database)
    engineering = get_records("engineering", database)
    drawings = get_records("drawings", database)
    mep = get_records("mep", database)
    boq = get_records("boq", database)
    construction = get_records("construction", database)
    activity = get_records("activity_log", database)

    total_projects = len(projects)
    active_projects = sum(
        str(project.get("status", "")).lower() == "active"
        for project in projects
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Projects", total_projects)
    c2.metric("Active Projects", active_projects)
    c3.metric("Documents", len(documents))
    c4.metric("Drawings", len(drawings))
    c5.metric("BOQ Items", len(boq))

    st.divider()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Architecture", len(architecture))
    c2.metric("Engineering", len(engineering))
    c3.metric("MEP", len(mep))
    c4.metric("Construction Phases", len(construction))

    if projects:
        st.subheader("Project Portfolio")
        df_projects = pd.DataFrame(projects)

        if "estimated_budget" in df_projects.columns:
            df_projects["estimated_budget"] = pd.to_numeric(
                df_projects["estimated_budget"], errors="coerce"
            ).fillna(0)
            fig_budget = px.bar(
                df_projects,
                x="name",
                y="estimated_budget",
                color="status" if "status" in df_projects.columns else None,
                title="Estimated Project Budgets",
                labels={
                    "estimated_budget": "Estimated Budget",
                    "name": "Project",
                },
            )
            st.plotly_chart(fig_budget, use_container_width=True)

        if "status" in df_projects.columns:
            status_counts = (
                df_projects["status"]
                .fillna("Unknown")
                .value_counts()
                .rename_axis("status")
                .reset_index(name="count")
            )
            fig_status = px.pie(
                status_counts,
                names="status",
                values="count",
                title="Project Status Distribution",
                hole=0.4,
            )
            st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Recent Activity")
    if activity:
        recent = sorted(
            activity,
            key=lambda entry: str(entry.get("timestamp", "")),
            reverse=True,
        )[:10]
        for entry in recent:
            timestamp = entry.get("timestamp", "")
            action = entry.get("action", "")
            details = entry.get("details", "")
            st.markdown(f"**{timestamp}** | {action} ({details})")
    else:
        st.info("No activity recorded yet.")

    st.divider()
    st.subheader("Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("New Project", use_container_width=True):
            _go_to("Projects")
    with c2:
        if st.button("Architecture", use_container_width=True):
            _go_to("Architecture")
    with c3:
        if st.button("Engineering", use_container_width=True):
            _go_to("Engineering")
    with c4:
        if st.button("Construction", use_container_width=True):
            _go_to("Construction")
