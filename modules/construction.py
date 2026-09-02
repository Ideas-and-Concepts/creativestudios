"""
Creative Studios
Construction Management Module
"""

import streamlit as st
from datetime import datetime, date
from .database import save_memory


def _get_collection(collection, db):
    """Local helper that returns a list from the database."""
    if collection not in db:
        db[collection] = []
    if not isinstance(db[collection], list):
        db[collection] = []
    return db[collection]


def _log_activity(database, action, details=""):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "user": "System",
    }
    database.setdefault("activity_log", []).append(entry)
    save_memory(database)


def render_construction_module(database):
    st.header("Construction Management")

    projects = _get_collection("projects", database)
    if not projects:
        st.warning("No projects found. Create a project first in the Projects module.")
        return

    project_names = {p.get("name", f"Project {p.get('id')}"): p.get("id") for p in projects}
    selected_project_name = st.selectbox("Select Project", list(project_names.keys()))
    project_id = project_names[selected_project_name]

    all_phases = _get_collection("construction", database)
    phases = [p for p in all_phases if p.get("project_id") == project_id]

    # Add phase
    st.subheader("Add New Construction Phase")
    with st.form("add_phase_form", clear_on_submit=True):
        phase_name = st.text_input("Phase Name", placeholder="e.g., Foundation")
        boq_ref = st.text_input("BoQ Reference", placeholder="e.g., 02.01.001")
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"], index=0)
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        submitted = st.form_submit_button("Add Phase")

    if submitted:
        if not phase_name.strip():
            st.error("Phase name is required.")
        else:
            new_phase = {
                "id": len(all_phases) + 1,
                "project_id": project_id,
                "phase": phase_name.strip(),
                "boq": boq_ref.strip(),
                "status": status,
                "start": str(start_date),
                "end": str(end_date),
                "created_at": datetime.now().isoformat(),
            }
            all_phases.append(new_phase)
            database["construction"] = all_phases
            save_memory(database)
            _log_activity(database, "Construction phase added", phase_name)
            st.success(f"Phase '{phase_name}' added!")
            st.rerun()

    if phases:
        st.subheader("Manage Construction Phases")
        for phase in phases:
            with st.expander(f"{phase['phase']} ({phase['status']})"):
                col1, col2 = st.columns(2)
                with col1:
                    new_phase = st.text_input("Phase Name", value=phase["phase"], key=f"pname_{phase['id']}")
                    new_boq = st.text_input("BoQ Reference", value=phase["boq"], key=f"boq_{phase['id']}")
                    status_options = ["Pending", "In Progress", "Completed"]
                    idx = status_options.index(phase["status"]) if phase["status"] in status_options else 0
                    new_status = st.selectbox("Status", status_options, index=idx, key=f"status_{phase['id']}")
                with col2:
                    new_start = st.date_input("Start Date", value=datetime.strptime(phase["start"], "%Y-%m-%d").date() if phase.get("start") else date.today(), key=f"start_{phase['id']}")
                    new_end = st.date_input("End Date", value=datetime.strptime(phase["end"], "%Y-%m-%d").date() if phase.get("end") else date.today(), key=f"end_{phase['id']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"upd_{phase['id']}"):
                        phase.update({
                            "phase": new_phase.strip(),
                            "boq": new_boq.strip(),
                            "status": new_status,
                            "start": str(new_start),
                            "end": str(new_end),
                        })
                        save_memory(database)
                        _log_activity(database, "Construction phase updated", new_phase)
                        st.success("Phase updated!")
                        st.rerun()
                with col2:
                    if st.button("Delete", key=f"del_{phase['id']}"):
                        all_phases = [p for p in all_phases if p["id"] != phase["id"]]
                        database["construction"] = all_phases
                        save_memory(database)
                        _log_activity(database, "Construction phase deleted", phase["phase"])
                        st.warning("Phase deleted!")
                        st.rerun()

        st.subheader("Phase Summary")
        table_data = []
        for p in phases:
            table_data.append({
                "Phase": p["phase"],
                "BoQ": p["boq"],
                "Status": p["status"],
                "Start": p["start"],
                "End": p["end"],
            })
        st.dataframe(table_data, use_container_width=True)
    else:
        st.info("No construction phases for this project yet.")