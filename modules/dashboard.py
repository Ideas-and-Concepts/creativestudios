"""
Creative Studios
Dashboard Module

Displays project KPIs, charts, recent activity, and quick actions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from .database import get_collection, save_memory


def _log_activity(database, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def render_dashboard(database):
    st.header("Dashboard")

    # -------- KPIs --------
    projects = get_collection("projects", database)
    documents = get_collection("documents", database)
    construction = get_collection("construction", database)
    boq = get_collection("boq", database)
    activity = get_collection("activity_log", database)

    total_projects = len(projects)
    active_projects = sum(1 for p in projects if p.get("status", "").lower() == "active")
    total_documents = len(documents)
    total_construction_phases = len(construction)
    total_boq_items = len(boq)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Projects", total_projects)
    col2.metric("Active Projects", active_projects)
    col3.metric("Documents", total_documents)
    col4.metric("Construction Phases", total_construction_phases)
    col5.metric("BOQ Items", total_boq_items)

    st.markdown("---")

    # -------- Charts --------
    if projects:
        df_projects = pd.DataFrame(projects)
        # Budget vs actual if available
        if "estimated_budget" in df_projects.columns:
            df_projects["estimated_budget"] = pd.to_numeric(df_projects["estimated_budget"], errors="coerce").fillna(0)
            fig_budget = px.bar(
                df_projects,
                x="name",
                y="estimated_budget",
                color="status",
                title="Project Budgets",
                labels={"estimated_budget": "Estimated Budget", "name": "Project"},
            )
            st.plotly_chart(fig_budget, use_container_width=True)

        # Project status distribution
        status_counts = df_projects["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        fig_status = px.pie(
            status_counts,
            names="status",
            values="count",
            title="Project Status Distribution",
            hole=0.4,
        )
        st.plotly_chart(fig_status, use_container_width=True)

    # -------- Recent Activity --------
    st.subheader("Recent Activity")
    if activity:
        # Show last 10 entries
        recent = sorted(activity, key=lambda x: x.get("timestamp", ""), reverse=True)[:10]
        for entry in recent:
            ts = entry.get("timestamp", "")
            action = entry.get("action", "")
            details = entry.get("details", "")
            st.markdown(f"**{ts}** — {action} ({details})")
    else:
        st.info("No activity recorded yet.")

    # -------- Quick Actions --------
    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("New Project"):
            st.session_state.active_module = "Projects"
            st.rerun()
    with col2:
        if st.button("Upload Document"):
            st.session_state.active_module = "Documents"
            st.rerun()
    with col3:
        if st.button("Add Construction Phase"):
            st.session_state.active_module = "Construction"
            st.rerun()