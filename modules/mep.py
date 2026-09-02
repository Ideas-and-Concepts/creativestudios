"""Creative Studios MEP Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

DISCIPLINES = ["Mechanical", "Electrical", "Plumbing"]
STATUSES = ["Draft", "In Coordination", "In Review", "Approved", "Issued"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("mep", []); records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
        elif isinstance(item, str):
            records.append({"id": index, "project_id": None, "title": item, "discipline": "Mechanical", "system": "", "status": "Draft", "notes": ""})
    database["mep"] = records; return records


def render_mep_module(database: dict[str, Any]) -> None:
    st.title("MEP")
    st.caption("Project-linked mechanical, electrical and plumbing coordination.")
    records = _normalize(database); projects = project_options(database)
    if not projects: st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="mep_project")
    project_id = int(projects[labels.index(selected)]["id"]); project_records = filter_project_records(records, project_id)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MEP Items", len(project_records)); c2.metric("Mechanical", sum(r.get("discipline") == "Mechanical" for r in project_records)); c3.metric("Electrical", sum(r.get("discipline") == "Electrical" for r in project_records)); c4.metric("Plumbing", sum(r.get("discipline") == "Plumbing" for r in project_records))
    for record in list(project_records):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'MEP Item')} | {record.get('discipline', 'Mechanical')}"):
            with st.form(f"mep_edit_{rid}"):
                title = st.text_input("MEP Work Item", value=str(record.get("title", "")))
                discipline = st.selectbox("Discipline", DISCIPLINES, index=DISCIPLINES.index(record.get("discipline", "Mechanical")) if record.get("discipline", "Mechanical") in DISCIPLINES else 0)
                system = st.text_input("System", value=str(record.get("system", "")))
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Draft")) if record.get("status", "Draft") in STATUSES else 0)
                notes = st.text_area("Coordination Notes", value=str(record.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                if not title.strip(): st.error("MEP work item is required.")
                else:
                    record.update({"title": title.strip(), "discipline": discipline, "system": system.strip(), "status": status, "notes": notes.strip(), "updated_at": datetime.now().isoformat(timespec="seconds")})
                    save_memory(database); st.success("MEP record updated."); st.rerun()
            if st.button("Delete Record", key=f"mep_delete_{rid}", use_container_width=True): records.remove(record); save_memory(database); st.rerun()
    st.divider()
    with st.form("mep_add", clear_on_submit=True):
        title = st.text_input("MEP Work Item"); discipline = st.selectbox("Discipline", DISCIPLINES); system = st.text_input("System"); status = st.selectbox("Status", STATUSES); notes = st.text_area("Coordination Notes")
        submitted = st.form_submit_button("Add MEP Element", use_container_width=True)
    if submitted:
        if not title.strip(): st.error("MEP work item is required.")
        else:
            records.append({"id": next_id("mep", database), "project_id": project_id, "title": title.strip(), "discipline": discipline, "system": system.strip(), "status": status, "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            save_memory(database); st.success("MEP element added."); st.rerun()
