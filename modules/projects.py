import streamlit as st
import pandas as pd
from typing import Any
from modules.database import save_memory

# ============================================================
# PROJECTS MODULE
# ============================================================

def render_projects_module(database: dict[str, Any]) -> None:
    """Render Projects module for managing portfolio."""

    st.header("Projects")

    projects = database.get("projects", [])
    if not projects:
        st.info("No projects available.")
    else:
        df = pd.DataFrame(projects)
        st.dataframe(df[["id", "name", "type", "status"]])

    # Add new project form
    with st.form("add_project", clear_on_submit=True):
        project_id = st.text_input("Project ID")
        name = st.text_input("Project Name")
        project_type = st.selectbox("Project Type", ["New", "Renovation", "Infrastructure"])
        status = st.selectbox("Status", ["Planning", "Design", "Execution", "Completed"])
        submitted = st.form_submit_button("Add Project")

        if submitted and project_id and name:
            new_project = {
                "id": project_id,
                "name": name,
                "type": project_type,
                "status": status,
                "boq": [],
                "team": [],
                "documents": [],
                "drawings": [],
                "spaces": [],
                "rfis": [],
                "site_logs": [],
                "tasks": [],
                "branding": {},
                "pending_approvals": []
            }
            projects.append(new_project)
            database["projects"] = projects
            save_memory(database)
            st.success(f"Added project: {name} ({project_type})")

    # Update project status
    if projects:
        st.subheader("Update Project Status")
        project_names = [p["name"] for p in projects]
        selected_project = st.selectbox("Select Project", project_names)
        new_status = st.selectbox("New Status", ["Planning", "Design", "Execution", "Completed"])
        if st.button("Update Status"):
            for p in projects:
                if p["name"] == selected_project:
                    p["status"] = new_status
                    save_memory(database)
                    st.success(f"Updated {selected_project} to {new_status}")