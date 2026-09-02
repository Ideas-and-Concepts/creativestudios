"""
Creative Studios
Projects Module (simplified)
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
    return {"projects": []}


def _save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, default=str)


def _get_collection(collection, db):
    if collection not in db:
        db[collection] = []
    return db[collection]


def _next_id(collection, db):
    records = _get_collection(collection, db)
    highest = 0
    for rec in records:
        if isinstance(rec, dict) and "id" in rec:
            try:
                highest = max(highest, int(rec["id"]))
            except:
                pass
    return highest + 1


def render_projects_module(database):
    st.header("Projects")
    db = database

    # Add project form
    with st.form("add_project_form"):
        name = st.text_input("Project Name")
        client = st.text_input("Client")
        location = st.text_input("Location")
        status = st.selectbox("Status", PROJECT_STATUSES)
        budget = st.number_input("Budget", min_value=0.0, step=1000.0)
        submitted = st.form_submit_button("Add Project")

    if submitted:
        if not name.strip():
            st.error("Name required.")
        else:
            projects = _get_collection("projects", db)
            project = {
                "id": _next_id("projects", db),
                "name": name.strip(),
                "client": client.strip(),
                "location": location.strip(),
                "status": status,
                "estimated_budget": budget,
                "created_at": datetime.now().isoformat(),
            }
            projects.append(project)
            _save_db(db)
            st.success("Project added.")
            st.rerun()

    # Display projects
    projects = _get_collection("projects", db)
    if not projects:
        st.info("No projects yet.")
        return

    st.subheader("Existing Projects")
    for i, p in enumerate(projects):
        # Ensure p is dict
        if not isinstance(p, dict):
            continue
        with st.expander(f"{p.get('name','Unnamed')} ({p.get('status','N/A')})"):
            st.write(f"**Client:** {p.get('client','')}")
            st.write(f"**Location:** {p.get('location','')}")
            st.write(f"**Budget:** ${p.get('estimated_budget',0):,.2f}")
            if st.button("Delete", key=f"del_proj_{i}"):
                projects.pop(i)
                _save_db(db)
                st.success("Deleted.")
                st.rerun()