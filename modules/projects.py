"""
Creative Studios
Projects Module (self-contained)
"""

import json
import streamlit as st
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "creativestudios_db.json"
PROJECT_STATUSES = ["Planning", "Active", "On Hold", "Completed", "Cancelled"]


def _load_db():
    if DB_FILE.exists():
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": [], "documents": [], "construction": [], "activity_log": []}


def _save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, default=str)


def _get_collection(collection, db):
    if collection not in db:
        db[collection] = []
    if not isinstance(db[collection], list):
        db[collection] = []
    return db[collection]


def _next_id(collection, db):
    records = _get_collection(collection, db)
    highest = 0
    for rec in records:
        if isinstance(rec, dict) and "id" in rec:
            try:
                highest = max(highest, int(rec["id"]))
            except (ValueError, TypeError):
                pass
    return highest + 1


def _add_record(collection, record, db):
    records = _get_collection(collection, db)
    record = dict(record)
    if "id" not in record or record["id"] is None:
        record["id"] = _next_id(collection, db)
    records.append(record)
    _save_db(db)
    return record


def _update_record(collection, record_id, updates, db):
    records = _get_collection(collection, db)
    for idx, rec in enumerate(records):
        if str(rec.get("id")) == str(record_id):
            rec.update(updates)
            _save_db(db)
            return rec
    return None


def _delete_record(collection, record_id, db):
    records = _get_collection(collection, db)
    for idx, rec in enumerate(records):
        if str(rec.get("id")) == str(record_id):
            records.pop(idx)
            _save_db(db)
            return True
    return False


def _log_activity(db, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    _get_collection("activity_log", db).append(entry)
    _save_db(db)


def render_projects_module(database):
    st.header("Projects")
    db = database  # database passed from main

    projects = _get_collection("projects", db)

    # Create project form
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
                    "id": _next_id("projects", db),
                    "name": name.strip(),
                    "client": client.strip(),
                    "location": location.strip(),
                    "status": status,
                    "estimated_budget": estimated_budget,
                    "description": description.strip(),
                    "created_at": datetime.now().isoformat(),
                }
                _add_record("projects", project, db)
                _log_activity(db, "Project created", name)
                st.success(f"Project '{name}' created.")
                st.rerun()

    # List projects
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

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", key=f"edit_{project['id']}"):
                    st.session_state["edit_project_id"] = project["id"]
            with col2:
                if st.button("Delete", key=f"del_{project['id']}"):
                    _delete_record("projects", project["id"], db)
                    _log_activity(db, "Project deleted", project.get("name", ""))
                    st.success("Project deleted.")
                    st.rerun()

    # Edit form
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
                _update_record(
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
                    db,
                )
                _log_activity(db, "Project updated", name)
                st.success("Project updated.")
                del st.session_state["edit_project_id"]
                st.rerun()