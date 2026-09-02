"""
Creative Studios
Projects Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import get_records, next_id, save_memory

PROJECT_STATUSES = ["Planning", "Active", "On Hold", "Completed", "Cancelled"]


def render_projects_module(database: dict[str, Any]) -> None:
    st.title("Projects")
    st.caption("Create and manage the project records that connect the entire AEC workflow.")
    projects = get_records("projects", database)

    with st.form("add_project_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            location = st.text_input("Location")
        with c2:
            status = st.selectbox("Status", PROJECT_STATUSES)
            budget = st.number_input("Estimated Budget", min_value=0.0, step=1000.0)
            notes = st.text_area("Project Notes")
        submitted = st.form_submit_button("Add Project", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("Project name is required.")
        else:
            project_id = next_id("projects", database)
            projects.append({
                "id": project_id,
                "name": name.strip(),
                "client": client.strip(),
                "location": location.strip(),
                "status": status,
                "estimated_budget": budget,
                "notes": notes.strip(),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            })
            save_memory(database)
            st.success(f"Project {project_id} created successfully.")
            st.rerun()

    st.divider()
    if not projects:
        st.info("No projects yet. Create the first project above.")
        return

    st.subheader("Project Register")
    for project in list(projects):
        project_id = project.get("id")
        with st.expander(f"Project {project_id} | {project.get('name', 'Unnamed Project')}"):
            with st.form(f"edit_project_{project_id}"):
                c1, c2 = st.columns(2)
                with c1:
                    edited_name = st.text_input("Project Name", value=str(project.get("name", "")))
                    edited_client = st.text_input("Client", value=str(project.get("client", "")))
                    edited_location = st.text_input("Location", value=str(project.get("location", "")))
                with c2:
                    current_status = project.get("status", "Planning")
                    status_index = PROJECT_STATUSES.index(current_status) if current_status in PROJECT_STATUSES else 0
                    edited_status = st.selectbox("Status", PROJECT_STATUSES, index=status_index)
                    edited_budget = st.number_input("Estimated Budget", min_value=0.0, value=float(project.get("estimated_budget", 0) or 0), step=1000.0)
                    edited_notes = st.text_area("Project Notes", value=str(project.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                if not edited_name.strip():
                    st.error("Project name is required.")
                else:
                    project.update({
                        "name": edited_name.strip(),
                        "client": edited_client.strip(),
                        "location": edited_location.strip(),
                        "status": edited_status,
                        "estimated_budget": edited_budget,
                        "notes": edited_notes.strip(),
                    })
                    save_memory(database)
                    st.success("Project updated successfully.")
                    st.rerun()
            st.caption(f"Project ID: {project_id}. This ID is the relationship key across the AEC modules.")
            if st.button("Delete Project", key=f"delete_project_{project_id}", use_container_width=True):
                projects.remove(project)
                save_memory(database)
                st.success("Project deleted successfully.")
                st.rerun()
