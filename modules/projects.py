"""
Creative Studios
Projects Module

Supports project management with templates.
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

# Predefined templates
PROJECT_TEMPLATES = {
    "None": {},
    "Residential Building": {
        "construction": ["Site Preparation", "Foundation", "Superstructure", "MEP Rough-in", "Finishes"],
        "boq_categories": ["Foundations", "Columns", "Beams", "Slabs", "Walls", "Doors", "Windows", "Finishes"],
    },
    "Commercial Complex": {
        "construction": ["Site Clearance", "Excavation", "Foundation", "Structural Frame", "MEP Installation", "Interior Fit-out"],
        "boq_categories": ["Foundations", "Columns", "Beams", "Slabs", "Walls", "Doors", "Windows", "Finishes", "Other"],
    },
    "Infrastructure": {
        "construction": ["Surveying", "Earthworks", "Road Base", "Pavement", "Drainage", "Markings"],
        "boq_categories": ["Earthworks", "Pavement", "Drainage", "Structures", "Other"],
    },
}


def _log_activity(database, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def _apply_template(database, project_id, template_name):
    """Create default construction phases and BOQ categories based on template."""
    template = PROJECT_TEMPLATES.get(template_name)
    if not template:
        return

    # Construction phases
    for phase_name in template.get("construction", []):
        phase = {
            "id": next_id("construction", database),
            "project_id": project_id,
            "phase": phase_name,
            "boq": "",
            "status": "Pending",
            "start": "",
            "end": "",
            "created_at": datetime.now().isoformat(),
        }
        add_record("construction", phase, database)

    # BOQ categories (simplified: create placeholder items with category)
    for cat in template.get("boq_categories", []):
        item = {
            "id": next_id("boq", database),
            "project_id": project_id,
            "category": cat,
            "item": f"{cat} - Template Item",
            "description": "",
            "unit": "",
            "quantity": 0,
            "rate": 0,
            "amount": 0,
        }
        add_record("boq", item, database)


def render_projects_module(database):
    st.header("Projects")

    projects = get_collection("projects", database)

    # -------- Create Project --------
    with st.expander("New Project", expanded=False):
        with st.form("create_project_form", clear_on_submit=True):
            name = st.text_input("Project Name")
            client = st.text_input("Client")
            location = st.text_input("Location")
            status = st.selectbox("Status", PROJECT_STATUSES, index=0)
            estimated_budget = st.number_input("Estimated Budget", min_value=0.0, step=1000.0)
            template = st.selectbox("Template", list(PROJECT_TEMPLATES.keys()))
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
                if template != "None":
                    _apply_template(database, project["id"], template)
                _log_activity(database, "Project created", name)
                st.success(f"Project '{name}' created.")
                st.rerun()

    # -------- Project List --------
    if not projects:
        st.info("No projects found. Create one above.")
        return

    st.subheader("Existing Projects")
    for project in projects:
        with st.expander(f"{project.get('name', 'Unnamed')} ({project.get('status', 'N/A')})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Client:** {project.get('client', 'N/A')}")
                st.write(f"**Location:** {project.get('location', 'N/A')}")
                st.write(f"**Budget:** ${project.get('estimated_budget', 0):,.2f}")
            with col2:
                st.write(f"**Description:** {project.get('description', '')[:200]}")

            # Edit and Delete buttons
            edit_col, delete_col = st.columns(2)
            with edit_col:
                if st.button("Edit", key=f"edit_{project['id']}"):
                    st.session_state["edit_project_id"] = project["id"]
            with delete_col:
                if st.button("Delete", key=f"del_{project['id']}"):
                    delete_record("projects", project["id"], database)
                    _log_activity(database, "Project deleted", project.get("name", ""))
                    st.success("Project deleted.")
                    st.rerun()

    # -------- Edit Modal (simplified inline) --------
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