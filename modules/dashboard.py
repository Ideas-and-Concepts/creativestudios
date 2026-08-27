import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Any

# ============================================================
# DASHBOARD MODULE
# ============================================================

def render_dashboard_module(database: dict[str, Any]) -> None:
    """Render Dashboard with analytics across modules."""

    st.header("Project Dashboard")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
        return

    # ---------------- Documents Overview ----------------
    st.subheader("Documents Overview")
    docs = [doc for p in projects for doc in p.get("documents", [])]
    if docs:
        df_docs = pd.DataFrame(docs)
        status_count = df_docs["status"].value_counts()
        fig_docs = px.pie(values=status_count.values, names=status_count.index,
                          title="Documents Approval Status")
        st.plotly_chart(fig_docs)

        phase_count = df_docs["phase"].value_counts()
        fig_phase = px.bar(x=phase_count.index, y=phase_count.values,
                           title="Documents by Phase")
        st.plotly_chart(fig_phase)
    else:
        st.caption("No documents uploaded yet.")

    # ---------------- Drawings Overview ----------------
    st.subheader("Drawings Overview")
    drawings = []
    for p in projects:
        for d in p.get("architecture_drawings", []):
            drawings.append({"discipline": "Architecture", "title": d["title"]})
        for d in p.get("engineering_drawings", []):
            drawings.append({"discipline": "Engineering", "title": d["title"]})

    if drawings:
        df_drawings = pd.DataFrame(drawings)
        fig_drawings = px.histogram(df_drawings, x="discipline",
                                    title="Drawings by Discipline")
        st.plotly_chart(fig_drawings)
    else:
        st.caption("No drawings uploaded yet.")

    # ---------------- MEP Overview ----------------
    st.subheader("MEP Overview")
    mep_items = [item for p in projects for item in p.get("mep", [])]
    if mep_items:
        df_mep = pd.DataFrame(mep_items)
        fig_mep = px.pie(df_mep, names="system_type", title="MEP System Breakdown")
        st.plotly_chart(fig_mep)

        total_cost = df_mep["cost"].sum()
        st.metric("Total MEP Cost", f"${total_cost:,.2f}")
    else:
        st.caption("No MEP items recorded yet.")

    # ---------------- Projects Portfolio ----------------
    st.subheader("Projects Portfolio")
    df_projects = pd.DataFrame(projects)
    if not df_projects.empty:
        fig_status = px.pie(df_projects, names="status", title="Projects by Status")
        st.plotly_chart(fig_status)

        fig_type = px.bar(df_projects, x="type", title="Projects by Type")
        st.plotly_chart(fig_type)
    else:
        st.caption("No projects created yet.")