"""
Creative Studios
Projects Module

Supports project management with basic CRUD.
"""

import streamlit as st
from datetime import datetime
from .database import (
    get_collection,
    add_record,
    update_record,
    delete_record,
    next_id,
    save_memory,
)


PROJECT_STATUSES = ["Planning", "Active", "On Hold", "Completed", "Cancelled"]


def _log_activity(database, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def render_projects_module(database):
    st.header("Projects")

    projects = get_collection("projects", database)

    # Create project
    with st.expander("New Project", expanded=False):
        with st.form("create_project_form", clear_on_submit=True):
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            location = st.text_input("Location")
            status = st.selectbox("Status", PROJECT_STATUSES, index=0)
            estimated_budget = st.number_input("Estimated Budget", min_value=0.0, step=1000.0)
            description = st.text_area("Description")

            submitted = st.form_submit_button("Create Project")

        if submitted:
            if not name.strip():
                st.error("Project name is required.")
            else:
                project = {
                    "id": next_id("projects", database),
                    "name": name.strip(),
                    "client": client.strip(),
                    "location": location.strip(),
                    "status": status,
                    "estimated_budget": estimated_budget,
                    "description": description.strip(),
                    "created_at": datetime.now().isoformat(),
                }
                add_record("projects", project, database)
                _log_activity(database, "Project created", name)
                st.success(f"Project '{name}' created.")
                st.rerun()

    # Project list
    if not projects:
        st.info("No projects found. Create one above.")
        return

    st.subheader("Existing Projects")
    for project in projects:
        with st.expander(f"{project.get('name', 'Unnamed')} ({project.get('status', 'N/A')})"):
            st.write(f"**Client:** {project.get('client', 'N/A')}")
            st.write(f"**Location:** {project.get('location', 'N/A')}")
            st.write(f"**Budget:** ${project.get('estimated_budget', 0):,.2f}")
            if project.get("description"):
                st.write(f"**Description:** {project['description'][:200]}")

            # Edit and Delete buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{project['id']}"):
                    st.session_state["edit_project_id"] = project["id"]
            with col2:
                if st.button("Delete", key=f"del_{project['id']}"):
                    delete_record("projects", project["id"], database)
                    _log_activity(database, "Project deleted", project.get("name", ""))
                    st.success("Project deleted.")
                    st.rerun()

    # Edit form (if requested)
    if "edit_project_id" in st.session_state:
        pid = st.session_state["edit_project_id"]
        project = next((p for p in projects if p["id"] == pid), None)
        if project:
            st.subheader(f"Edit Project: {project['name']}")
            with st.form("edit_project_form"):
                name = st.text_input("Name", value=project.get("name", ""))
                client = st.text_input("Client", value=project.get("client", ""))
                location = st.text_input("Location", value=project.get("location", ""))
                status_idx = PROJECT_STATUSES.index(project.get("status", "Planning")) if project.get("status") in PROJECT_STATUSES else 0
                status = st.selectbox("Status", PROJECT_STATUSES, index=status_idx)
                budget = st.number_input("Estimated Budget", value=float(project.get("estimated_budget", 0)), min_value=0.0, step=1000.0)
                description = st.text_area("Description", value=project.get("description", ""))
                update = st.form_submit_button("Update Project")

            if update:
                update_record(
                    "projects",
                    pid,
                    {
                        "name": name.strip(),
                        "client": client.strip(),
                        "location": location.strip(),
                        "status": status,
                        "estimated_budget": budget,
                        "description": description.strip(),
                    },
                    database,
                )
                _log_activity(database, "Project updated", name)
                st.success("Project updated.")
                del st.session_state["edit_project_id"]
                st.rerun()