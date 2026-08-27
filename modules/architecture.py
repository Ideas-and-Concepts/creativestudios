"""Creative Studios - Architecture Module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

WORK_TYPES = ["Site Planning", "Floor Planning", "Elevations", "Sections", "Architectural Details", "Door and Window Schedules", "Finishes", "Specifications", "Design Coordination", "Site Observation", "Design Change", "As-Built Documentation", "Other"]
DESIGN_STAGES = ["Concept", "Schematic Design", "Design Development", "Construction Documentation", "Construction", "As-Built"]
STATUSES = ["Not Started", "In Progress", "Submitted", "Under Review", "Approved", "Issued for Construction", "Completed", "On Hold"]
PRIORITIES = ["Low", "Normal", "High", "Critical"]
APPROVAL_STATUSES = ["Not Required", "Pending", "Under Review", "Approved", "Rejected"]


def _text(value: Any, default: str = "") -> str:
    return default if value is None else str(value).strip()


def _normalize_records(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.get("architecture", [])
    if not isinstance(value, list):
        value = []
    records: list[dict[str, Any]] = []
    defaults = {
        "title": "", "project": "", "work_type": "Other", "stage": "Construction",
        "status": "Not Started", "priority": "Normal", "drawing_number": "", "revision": "",
        "responsible": "", "contractor": "", "start_date": "", "target_date": "",
        "completion_date": "", "rfi_reference": "", "approval_status": "Not Required", "notes": "",
    }
    for index, item in enumerate(value, 1):
        if isinstance(item, dict):
            record = {**defaults, **item}
            record["id"] = record.get("id") or index
            records.append(record)
        elif isinstance(item, str):
            records.append({"id": index, **defaults, "title": item.strip()})
    database["architecture"] = records
    return records


def _next_id(records: list[dict[str, Any]]) -> int:
    ids = []
    for record in records:
        try:
            ids.append(int(record.get("id", 0)))
        except (TypeError, ValueError):
            pass
    return max(ids, default=0) + 1


def _save(database: dict[str, Any]) -> None:
    save_memory(database)
    st.session_state.database = database


def _index(options: list[str], value: Any, default: int = 0) -> int:
    value = _text(value)
    return options.index(value) if value in options else min(default, len(options) - 1)


def render_architecture_module(database: dict[str, Any]) -> None:
    st.title("Architecture")
    st.caption("Manage architectural works, construction coordination, design deliverables and site activities.")
    records = _normalize_records(database)

    cols = st.columns(4)
    cols[0].metric("Architecture Works", len(records))
    cols[1].metric("In Progress", sum(1 for r in records if _text(r.get("status")).lower() == "in progress"))
    cols[2].metric("Under Review", sum(1 for r in records if _text(r.get("status")).lower() == "under review"))
    cols[3].metric("Completed", sum(1 for r in records if _text(r.get("status")).lower() == "completed"))
    st.divider()

    tab_register, tab_add, tab_summary = st.tabs(["Work Register", "Add Work", "Construction Summary"])

    with tab_register:
        if not records:
            st.info("No architectural construction works have been registered.")
        else:
            search = st.text_input("Search architectural works", placeholder="Search by title, project, drawing or responsible person", key="architecture_search")
            term = search.strip().lower()
            filtered = [r for r in records if not term or term in " ".join(_text(r.get(k)) for k in ("title", "project", "work_type", "drawing_number", "responsible", "contractor")).lower()]
            if not filtered:
                st.info("No architectural works match the search.")
            for index, record in enumerate(filtered):
                record_id = record.get("id", index + 1)
                title = _text(record.get("title"), "Untitled Architectural Work") or "Untitled Architectural Work"
                project = _text(record.get("project"))
                heading = f"{title} — {project}" if project else title
                with st.expander(heading, expanded=False):
                    st.caption(f"Status: {_text(record.get('status'), 'Not Started')}")
                    with st.form(f"architecture_edit_{record_id}"):
                        edited_title = st.text_input("Work Item", value=title)
                        edited_project = st.text_input("Project", value=_text(record.get("project")))
                        edited_work_type = st.selectbox("Work Type", WORK_TYPES, index=_index(WORK_TYPES, record.get("work_type"), len(WORK_TYPES)-1))
                        edited_stage = st.selectbox("Design / Construction Stage", DESIGN_STAGES, index=_index(DESIGN_STAGES, record.get("stage"), DESIGN_STAGES.index("Construction")))
                        edited_status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                        edited_priority = st.selectbox("Priority", PRIORITIES, index=_index(PRIORITIES, record.get("priority"), 1))
                        edited_drawing = st.text_input("Drawing / Reference Number", value=_text(record.get("drawing_number")))
                        edited_revision = st.text_input("Revision", value=_text(record.get("revision")))
                        edited_responsible = st.text_input("Responsible Architect", value=_text(record.get("responsible")))
                        edited_contractor = st.text_input("Contractor", value=_text(record.get("contractor")))
                        dates = st.columns(3)
                        edited_start = dates[0].text_input("Start Date", value=_text(record.get("start_date")), placeholder="YYYY-MM-DD")
                        edited_target = dates[1].text_input("Target Date", value=_text(record.get("target_date")), placeholder="YYYY-MM-DD")
                        edited_completion = dates[2].text_input("Completion Date", value=_text(record.get("completion_date")), placeholder="YYYY-MM-DD")
                        edited_rfi = st.text_input("RFI Reference", value=_text(record.get("rfi_reference")))
                        edited_approval = st.selectbox("Approval Status", APPROVAL_STATUSES, index=_index(APPROVAL_STATUSES, record.get("approval_status")))
                        edited_notes = st.text_area("Notes", value=_text(record.get("notes")))
                        submitted = st.form_submit_button("Save Changes", use_container_width=True)
                    if submitted:
                        if not edited_title.strip():
                            st.error("Work item is required.")
                        else:
                            record.update(title=edited_title.strip(), project=edited_project.strip(), work_type=edited_work_type, stage=edited_stage, status=edited_status, priority=edited_priority, drawing_number=edited_drawing.strip(), revision=edited_revision.strip(), responsible=edited_responsible.strip(), contractor=edited_contractor.strip(), start_date=edited_start.strip(), target_date=edited_target.strip(), completion_date=edited_completion.strip(), rfi_reference=edited_rfi.strip(), approval_status=edited_approval, notes=edited_notes.strip())
                            _save(database)
                            st.success("Architectural work updated.")
                            st.rerun()
                    if st.button("Delete Work", key=f"architecture_delete_{record_id}", use_container_width=True):
                        records[:] = [item for item in records if item is not record]
                        _save(database)
                        st.success("Architectural work deleted.")
                        st.rerun()

    with tab_add:
        with st.form("architecture_add_form", clear_on_submit=True):
            title = st.text_input("Work Item")
            project = st.text_input("Project")
            work_type = st.selectbox("Work Type", WORK_TYPES)
            stage = st.selectbox("Design / Construction Stage", DESIGN_STAGES, index=DESIGN_STAGES.index("Construction"))
            status = st.selectbox("Status", STATUSES)
            priority = st.selectbox("Priority", PRIORITIES, index=1)
            drawing_number = st.text_input("Drawing / Reference Number")
            revision = st.text_input("Revision")
            responsible = st.text_input("Responsible Architect")
            contractor = st.text_input("Contractor")
            start_date = st.text_input("Start Date", placeholder="YYYY-MM-DD")
            target_date = st.text_input("Target Date", placeholder="YYYY-MM-DD")
            completion_date = st.text_input("Completion Date", placeholder="YYYY-MM-DD")
            rfi_reference = st.text_input("RFI Reference")
            approval_status = st.selectbox("Approval Status", APPROVAL_STATUSES)
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add Architectural Work", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Work item is required.")
            else:
                records.append({"id": _next_id(records), "title": title.strip(), "project": project.strip(), "work_type": work_type, "stage": stage, "status": status, "priority": priority, "drawing_number": drawing_number.strip(), "revision": revision.strip(), "responsible": responsible.strip(), "contractor": contractor.strip(), "start_date": start_date.strip(), "target_date": target_date.strip(), "completion_date": completion_date.strip(), "rfi_reference": rfi_reference.strip(), "approval_status": approval_status, "notes": notes.strip()})
                _save(database)
                st.success("Architectural work added.")
                st.rerun()

    with tab_summary:
        if not records:
            st.info("No architectural construction data is available.")
        else:
            st.subheader("Work by Type")
            type_counts: dict[str, int] = {}
            for r in records:
                key = _text(r.get("work_type"), "Other") or "Other"
                type_counts[key] = type_counts.get(key, 0) + 1
            st.dataframe([{"Work Type": k, "Items": v} for k, v in sorted(type_counts.items())], use_container_width=True, hide_index=True)
            st.subheader("Work by Status")
            status_counts: dict[str, int] = {}
            for r in records:
                key = _text(r.get("status"), "Not Started") or "Not Started"
                status_counts[key] = status_counts.get(key, 0) + 1
            st.dataframe([{"Status": k, "Items": v} for k, v in sorted(status_counts.items())], use_container_width=True, hide_index=True)