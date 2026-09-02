import streamlit as st
import plotly.express as px
import pandas as pd

def render_dashboard(database):
    st.header("📊 Dashboard")

    try:
        # --- KPI Cards ---
        total_projects = len(database.get("projects", []))
        total_docs = sum(len(p.get("documents", [])) for p in database.get("projects", []))
        total_drawings = sum(len(p.get("drawings", [])) for p in database.get("projects", []))
        total_mep = sum(len(p.get("mep", [])) for p in database.get("projects", []))

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Projects", total_projects)
        col2.metric("Documents", total_docs)
        col3.metric("Drawings", total_drawings)
        col4.metric("MEP Systems", total_mep)

        # --- Interactive Filters ---
        if database.get("projects"):
            project_names = [p["name"] for p in database["projects"]]
            selected_project = st.selectbox("Filter by Project", options=project_names)

            project = next((p for p in database["projects"] if p["name"] == selected_project), None)

            if project:
                # --- Documents Chart ---
                doc_counts = len(project.get("documents", []))
                fig_docs = px.bar(
                    x=[selected_project],
                    y=[doc_counts],
                    labels={"x": "Project", "y": "Documents"},
                    title=f"Documents in {selected_project}"
                )
                st.plotly_chart(fig_docs, use_container_width=True)

                # --- Drawings Chart ---
                drawing_counts = len(project.get("drawings", []))
                fig_drawings = px.pie(
                    names=["Drawings", "Remaining"],
                    values=[drawing_counts, max(1, total_drawings - drawing_counts)],
                    title=f"Drawings Distribution ({selected_project})"
                )
                st.plotly_chart(fig_drawings, use_container_width=True)

                # --- MEP Chart ---
                mep_counts = len(project.get("mep", []))
                fig_mep = px.bar(
                    x=["MEP Systems"],
                    y=[mep_counts],
                    title=f"MEP Systems in {selected_project}"
                )
                st.plotly_chart(fig_mep, use_container_width=True)

        else:
            st.info("No projects yet to display")

    except Exception as e:
        st.error(f"⚠️ Dashboard rendering failed: {e}")