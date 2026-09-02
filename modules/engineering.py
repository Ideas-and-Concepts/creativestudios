"""Creative Studios Engineering Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

DISCIPLINES = ["Structural", "Civil", "Geotechnical", "Transportation", "Infrastructure", "Environmental", "Other"]
STATUSES = ["Draft", "In Review", "Approved", "Issued"]
ELEMENTS = ["Foundation", "Footing", "Column", "Beam", "Slab", "Structural Wall", "Stair", "Retaining Wall", "Earthworks", "Drainage", "Roadwork", "Infrastructure", "Other"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("engineering", []); records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
        elif isinstance(item, str):
            records.append({"id": index, "project_id": None, "title": item, "discipline": "Other", "element": "Other", "status": "Draft", "notes": ""})
    database["engineering"] = records
    return records


def render_engineering_module(database: dict[str, Any]) -> None:
    st.title("Engineering")
    st.caption("Project-linked structural, civil and technical engineering work.")
    records = _normalize(database)
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects."); return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="engineering_project")
    project_id = int(projects[labels.index(selected)]["id"])
    project_records = filter_project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Engineering Items", len(project_records))
    c2.metric("Structural", sum(r.get("discipline") == "Structural" for r in project_records))
    c3.metric("Civil", sum(r.get("discipline") == "Civil" for r in project_records))
    c4.metric("Issued", sum(r.get("status") == "Issued" for r in project_records))

    st.subheader("Engineering Elements")
    for record in list(project_records):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'Engineering Item')} | {record.get('element', 'Other')}"):
            with st.form(f"engineering_edit_{rid}"):
                title = st.text_input("Engineering Work Item", value=str(record.get("title", "")))
                discipline = st.selectbox("Discipline", DISCIPLINES, index=DISCIPLINES.index(record.get("discipline", "Other")) if record.get("discipline", "Other") in DISCIPLINES else len(DISCIPLINES)-1)
                element = st.selectbox("Engineering Element", ELEMENTS, index=ELEMENTS.index(record.get("element", "Other")) if record.get("element", "Other") in ELEMENTS else len(ELEMENTS)-1)
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Draft")) if record.get("status", "Draft") in STATUSES else 0)
                notes = st.text_area("Technical Notes", value=str(record.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                if not title.strip(): st.error("Engineering work item is required.")
                else:
                    record.update({"title": title.strip(), "discipline": discipline, "element": element, "status": status, "notes": notes.strip(), "updated_at": datetime.now().isoformat(timespec="seconds")})
                    save_memory(database); st.success("Engineering record updated."); st.rerun()
            if st.button("Delete Record", key=f"engineering_delete_{rid}", use_container_width=True):
                records.remove(record); save_memory(database); st.rerun()

    st.divider()
    with st.form("engineering_add", clear_on_submit=True):
        title = st.text_input("Engineering Work Item")
        discipline = st.selectbox("Discipline", DISCIPLINES)
        element = st.selectbox("Engineering Element", ELEMENTS)
        status = st.selectbox("Status", STATUSES)
        notes = st.text_area("Technical Notes")
        submitted = st.form_submit_button("Add Engineering Element", use_container_width=True)
    if submitted:
        if not title.strip(): st.error("Engineering work item is required.")
        else:
            records.append({"id": next_id("engineering", database), "project_id": project_id, "title": title.strip(), "discipline": discipline, "element": element, "status": status, "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            save_memory(database); st.success("Engineering element added."); st.rerun()
