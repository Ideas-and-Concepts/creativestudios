"""Creative Studios - Engineering Module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

DISCIPLINES = ["Structural", "Civil", "Geotechnical", "Mechanical", "Electrical", "Plumbing", "Infrastructure", "Transportation", "Environmental", "Other"]
WORK_TYPES = ["Design", "Foundation Works", "Structural Frame", "Reinforcement", "Concrete Works", "Earthworks", "Drainage", "Road Works", "External Works", "Mechanical Installation", "Electrical Installation", "Plumbing Installation", "Inspection", "Testing and Commissioning", "Technical Review", "Site Engineering", "As-Built Documentation", "Other"]
STAGES = ["Design", "Tender", "Construction", "Testing and Commissioning", "As-Built"]
STATUSES = ["Not Started", "In Progress", "Submitted", "Under Review", "Approved", "Issued for Construction", "Completed", "On Hold"]
PRIORITIES = ["Low", "Normal", "High", "Critical"]
APPROVAL_STATUSES = ["Not Required", "Pending", "Under Review", "Approved", "Rejected"]


def _text(value: Any, default: str = "") -> str:
    return default if value is None else str(value).strip()


def _normalize_records(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.get("engineering", [])
    if not isinstance(value, list):
        value = []
    defaults = {"title": "", "project": "", "discipline": "Other", "work_type": "Other", "stage": "Construction", "status": "Not Started", "priority": "Normal", "drawing_number": "", "revision": "", "responsible": "", "contractor": "", "start_date": "", "target_date": "", "completion_date": "", "rfi_reference": "", "approval_status": "Not Required", "notes": ""}
    records: list[dict[str, Any]] = []
    for index, item in enumerate(value, 1):
        if isinstance(item, dict):
            record = {**defaults, **item}
            record["id"] = record.get("id") or index
            records.append(record)
        elif isinstance(item, str):
            records.append({"id": index, **defaults, "title": item.strip()})
    database["engineering"] = records
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


def render_engineering_module(database: dict[str, Any]) -> None:
    st.title("Engineering")
    st.caption("Manage structural, civil, MEP and other engineering works throughout construction.")
    records = _normalize_records(database)

    cols = st.columns(4)
    cols[0].metric("Engineering Works", len(records))
    cols[1].metric("Structural", sum(1 for r in records if _text(r.get("discipline")).lower() == "structural"))
    cols[2].metric("Civil", sum(1 for r in records if _text(r.get("discipline")).lower() == "civil"))
    cols[3].metric("Completed", sum(1 for r in records if _text(r.get("status")).lower() == "completed"))
    st.divider()

    tab_register, tab_add, tab_summary = st.tabs(["Work Register", "Add Work", "Engineering Summary"])
    with tab_register:
        if not records:
            st.info("No engineering construction works have been registered.")
        else:
            search = st.text_input("Search engineering works", placeholder="Search by title, project, discipline, drawing or engineer", key="engineering_search")
            term = search.strip().lower()
            filtered = [r for r in records if not term or term in " ".join(_text(r.get(k)) for k in ("title", "project", "discipline", "work_type", "drawing_number", "responsible", "contractor")).lower()]
            if not filtered:
                st.info("No engineering works match the search.")
            for index, record in enumerate(filtered):
                record_id = record.get("id", index + 1)
                title = _text(record.get("title"), "Untitled Engineering Work") or "Untitled Engineering Work"
                project = _text(record.get("project"))
                heading = f"{title} — {project}" if project else title
                with st.expander(heading, expanded=False):
                    st.caption(f"Discipline: {_text(record.get('discipline'), 'Other')}")
                    with st.form(f"engineering_edit_{record_id}"):
                        edited_title = st.text_input("Engineering Work Item", value=title)
                        edited_project = st.text_input("Project", value=_text(record.get("project")))
                        edited_discipline = st.selectbox("Engineering Discipline", DISCIPLINES, index=_index(DISCIPLINES, record.get("discipline"), len(DISCIPLINES)-1))
                        edited_work_type = st.selectbox("Work Type", WORK_TYPES, index=_index(WORK_TYPES, record.get("work_type"), len(WORK_TYPES)-1))
                        edited_stage = st.selectbox("Construction Stage", STAGES, index=_index(STAGES, record.get("stage"), STAGES.index("Construction")))
                        edited_status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                        edited_priority = st.selectbox("Priority", PRIORITIES, index=_index(PRIORITIES, record.get("priority"), 1))
                        edited_drawing = st.text_input("Drawing / Reference Number", value=_text(record.get("drawing_number")))
                        edited_revision = st.text_input("Revision", value=_text(record.get("revision")))
                        edited_responsible = st.text_input("Responsible Engineer", value=_text(record.get("responsible")))
                        edited_contractor = st.text_input("Contractor", value=_text(record.get("contractor")))
                        dates = st.columns(3)
                        edited_start = dates[0].text_input("Start Date", value=_text(record.get("start_date")), placeholder="YYYY-MM-DD")
                        edited_target = dates[1].text_input("Target Date", value=_text(record.get("target_date")), placeholder="YYYY-MM-DD")
                        edited_completion = dates[2].text_input("Completion Date", value=_text(record.get("completion_date")), placeholder="YYYY-MM-DD")
                        edited_rfi = st.text_input("RFI Reference", value=_text(record.get("rfi_reference")))
                        edited_approval = st.selectbox("Approval Status", APPROVAL_STATUSES, index=_index(APPROVAL_STATUSES, record.get("approval_status")))
                        edited_notes = st.text_area("Technical Notes", value=_text(record.get("notes")))
                        submitted = st.form_submit_button("Save Changes", use_container_width=True)
                    if submitted:
                        if not edited_title.strip():
                            st.error("Engineering work item is required.")
                        else:
                            record.update(title=edited_title.strip(), project=edited_project.strip(), discipline=edited_discipline, work_type=edited_work_type, stage=edited_stage, status=edited_status, priority=edited_priority, drawing_number=edited_drawing.strip(), revision=edited_revision.strip(), responsible=edited_responsible.strip(), contractor=edited_contractor.strip(), start_date=edited_start.strip(), target_date=edited_target.strip(), completion_date=edited_completion.strip(), rfi_reference=edited_rfi.strip(), approval_status=edited_approval, notes=edited_notes.strip())
                            _save(database)
                            st.success("Engineering work updated.")
                            st.rerun()
                    if st.button("Delete Work", key=f"engineering_delete_{record_id}", use_container_width=True):
                        records[:] = [item for item in records if item is not record]
                        _save(database)
                        st.success("Engineering work deleted.")
                        st.rerun()

    with tab_add:
        with st.form("engineering_add_form", clear_on_submit=True):
            title = st.text_input("Engineering Work Item")
            project = st.text_input("Project")
            discipline = st.selectbox("Engineering Discipline", DISCIPLINES)
            work_type = st.selectbox("Work Type", WORK_TYPES)
            stage = st.selectbox("Construction Stage", STAGES, index=STAGES.index("Construction"))
            status = st.selectbox("Status", STATUSES)
            priority = st.selectbox("Priority", PRIORITIES, index=1)
            drawing_number = st.text_input("Drawing / Reference Number")
            revision = st.text_input("Revision")
            responsible = st.text_input("Responsible Engineer")
            contractor = st.text_input("Contractor")
            start_date = st.text_input("Start Date", placeholder="YYYY-MM-DD")
            target_date = st.text_input("Target Date", placeholder="YYYY-MM-DD")
            completion_date = st.text_input("Completion Date", placeholder="YYYY-MM-DD")
            rfi_reference = st.text_input("RFI Reference")
            approval_status = st.selectbox("Approval Status", APPROVAL_STATUSES)
            notes = st.text_area("Technical Notes")
            submitted = st.form_submit_button("Add Engineering Work", use_container_width=True)
        if submitted:
            if not title.strip():
                st.error("Engineering work item is required.")
            else:
                records.append({"id": _next_id(records), "title": title.strip(), "project": project.strip(), "discipline": discipline, "work_type": work_type, "stage": stage, "status": status, "priority": priority, "drawing_number": drawing_number.strip(), "revision": revision.strip(), "responsible": responsible.strip(), "contractor": contractor.strip(), "start_date": start_date.strip(), "target_date": target_date.strip(), "completion_date": completion_date.strip(), "rfi_reference": rfi_reference.strip(), "approval_status": approval_status, "notes": notes.strip()})
                _save(database)
                st.success("Engineering work added.")
                st.rerun()

    with tab_summary:
        if not records:
            st.info("No engineering construction data is available.")
        else:
            discipline_counts: dict[str, int] = {}
            status_counts: dict[str, int] = {}
            for record in records:
                d = _text(record.get("discipline"), "Other") or "Other"
                s = _text(record.get("status"), "Not Started") or "Not Started"
                discipline_counts[d] = discipline_counts.get(d, 0) + 1
                status_counts[s] = status_counts.get(s, 0) + 1
            st.subheader("Works by Discipline")
            st.dataframe([{"Discipline": k, "Items": v} for k, v in sorted(discipline_counts.items())], use_container_width=True, hide_index=True)
            st.subheader("Works by Status")
            st.dataframe([{"Status": k, "Items": v} for k, v in sorted(status_counts.items())], use_container_width=True, hide_index=True)