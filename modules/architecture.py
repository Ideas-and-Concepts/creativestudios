"""Creative Studios Architecture Module."""
from __future__ import annotations
from datetime import datetime
from typing import Any
import streamlit as st
from modules.database import get_records, next_id, save_memory
from modules.project_context import filter_project_records, project_label, project_options

STAGES = ["Concept", "Schematic Design", "Design Development", "Construction Documentation", "Issued"]
STATUSES = ["Draft", "In Review", "Approved", "Issued"]
ELEMENTS = ["Site Planning", "Building Layout", "Floor Plan", "Room", "Wall", "Door", "Window", "Stair", "Roof", "Ceiling", "Floor Finish", "Wall Finish", "External Works", "Other"]
BUILDING_TYPES = ["General", "Residential", "Commercial", "Office", "Industrial", "Institutional", "Hospitality", "Education", "Mixed Use"]


def _normalize(database: dict[str, Any]) -> list[dict[str, Any]]:
    raw = database.get("architecture", [])
    records: list[dict[str, Any]] = []
    if not isinstance(raw, list): raw = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            r = dict(item); r.setdefault("id", index); r.setdefault("project_id", None); records.append(r)
        elif isinstance(item, str):
            records.append({"id": index, "project_id": None, "title": item, "element": "Other", "building_type": "General", "stage": "Concept", "status": "Draft", "notes": ""})
    database["architecture"] = records
    return records


def render_architecture_module(database: dict[str, Any]) -> None:
    st.title("Architecture")
    st.caption("Project-linked architectural design and construction documentation.")
    records = _normalize(database)
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects.")
        return
    labels = [project_label(p) for p in projects]
    selected = st.selectbox("Project", labels, key="architecture_project")
    project_id = int(projects[labels.index(selected)]["id"])
    project_records = filter_project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project Designs", len(project_records))
    c2.metric("Rooms", sum(r.get("element") == "Room" for r in project_records))
    c3.metric("Open Reviews", sum(r.get("status") == "In Review" for r in project_records))
    c4.metric("Issued", sum(r.get("status") == "Issued" for r in project_records))

    st.subheader("Architectural Elements")
    for record in list(project_records):
        rid = record.get("id")
        with st.expander(f"{record.get('title', 'Untitled')} | {record.get('element', 'Other')}"):
            with st.form(f"architecture_edit_{rid}"):
                title = st.text_input("Design Item", value=str(record.get("title", "")))
                element = st.selectbox("Element", ELEMENTS, index=ELEMENTS.index(record.get("element", "Other")) if record.get("element", "Other") in ELEMENTS else len(ELEMENTS)-1)
                building = st.selectbox("Building Type", BUILDING_TYPES, index=BUILDING_TYPES.index(record.get("building_type", "General")) if record.get("building_type", "General") in BUILDING_TYPES else 0)
                stage = st.selectbox("Design Stage", STAGES, index=STAGES.index(record.get("stage", "Concept")) if record.get("stage", "Concept") in STAGES else 0)
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Draft")) if record.get("status", "Draft") in STATUSES else 0)
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                save = st.form_submit_button("Save Changes", use_container_width=True)
            if save:
                if not title.strip(): st.error("Design item is required.")
                else:
                    record.update({"title": title.strip(), "element": element, "building_type": building, "stage": stage, "status": status, "notes": notes.strip(), "updated_at": datetime.now().isoformat(timespec="seconds")})
                    save_memory(database); st.success("Architecture record updated."); st.rerun()
            if st.button("Delete Record", key=f"architecture_delete_{rid}", use_container_width=True):
                records.remove(record); save_memory(database); st.rerun()

    st.divider()
    with st.form("architecture_add", clear_on_submit=True):
        title = st.text_input("Design Item")
        element = st.selectbox("Element", ELEMENTS)
        building = st.selectbox("Building Type", BUILDING_TYPES)
        stage = st.selectbox("Design Stage", STAGES)
        status = st.selectbox("Status", STATUSES)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Architectural Element", use_container_width=True)
    if submitted:
        if not title.strip(): st.error("Design item is required.")
        else:
            records.append({"id": next_id("architecture", database), "project_id": project_id, "title": title.strip(), "element": element, "building_type": building, "stage": stage, "status": status, "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
            save_memory(database); st.success("Architectural element added."); st.rerun()
