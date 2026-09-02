"""Creative Studios Construction Management Module."""
from __future__ import annotations
from datetime import date, datetime
from typing import Any
import streamlit as st
from modules.database import next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

STATUSES = ["Pending", "In Progress", "Completed", "On Hold"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("construction", []); records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
    database["construction"] = records
    return records


def render_construction_module(database: dict[str, Any]) -> None:
    st.title("Construction")
    st.caption("Execute project work against BOQ items using the shared Project ID.")
    records = _normalize(database); projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="construction_project")
    project_id = int(projects[labels.index(selected)]["id"])
    project_records = filter_project_records(records, project_id)
    c1, c2, c3 = st.columns(3)
    c1.metric("Work Phases", len(project_records)); c2.metric("In Progress", sum(r.get("status") == "In Progress" for r in project_records)); c3.metric("Completed", sum(r.get("status") == "Completed" for r in project_records))

    for record in list(project_records):
        rid = record.get("id")
        with st.expander(f"{record.get('phase', 'Construction Phase')} | {record.get('status', 'Pending')}"):
            with st.form(f"construction_edit_{rid}"):
                phase = st.text_input("Phase", value=str(record.get("phase", "")))
                boq = st.text_input("BOQ Reference", value=str(record.get("boq_reference", "")))
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Pending")) if record.get("status", "Pending") in STATUSES else 0)
                progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=float(record.get("progress", 0) or 0))
                start = st.date_input("Start Date", value=datetime.fromisoformat(record["start"]).date() if record.get("start") else date.today())
                end = st.date_input("End Date", value=datetime.fromisoformat(record["end"]).date() if record.get("end") else date.today())
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                record.update({"phase": phase.strip(), "boq_reference": boq.strip(), "status": status, "progress": progress, "start": str(start), "end": str(end), "notes": notes.strip()})
                save_memory(database); st.success("Construction phase updated."); st.rerun()
            if st.button("Delete Phase", key=f"construction_delete_{rid}", use_container_width=True):
                records.remove(record); save_memory(database); st.rerun()

    st.divider()
    with st.form("construction_add", clear_on_submit=True):
        phase = st.text_input("Phase", placeholder="Foundation, Structure, Roofing, Finishes...")
        boq = st.text_input("BOQ Reference")
        status = st.selectbox("Status", STATUSES)
        progress = st.number_input("Progress %", min_value=0.0, max_value=100.0, value=0.0)
        start = st.date_input("Start Date", value=date.today())
        end = st.date_input("End Date", value=date.today())
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Construction Phase", use_container_width=True)
    if submitted:
        if not phase.strip(): st.error("Phase is required.")
        else:
            records.append({"id": next_id("construction", database), "project_id": project_id, "phase": phase.strip(), "boq_reference": boq.strip(), "status": status, "progress": progress, "start": str(start), "end": str(end), "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            save_memory(database); st.success("Construction phase added."); st.rerun()
