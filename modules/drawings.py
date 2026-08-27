"""Creative Studios - Construction Drawings Module."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory

DRAWING_CATEGORIES = ["Architectural", "Structural"]
DISCIPLINES = ["Architectural", "Structural", "Civil", "Electrical", "Mechanical", "Plumbing", "Other"]
ARCHITECTURAL_TYPES = ["Site Plan", "Floor Plan", "Roof Plan", "Elevation", "Section", "Architectural Detail", "Door Schedule", "Window Schedule", "Finishes Schedule", "Reflected Ceiling Plan", "As-Built", "Other"]
STRUCTURAL_TYPES = ["Foundation Plan", "Column Layout", "Beam Layout", "Slab Plan", "Roof Structure", "Reinforcement Detail", "Structural Section", "Structural Detail", "Connection Detail", "As-Built", "Other"]
STATUSES = ["Draft", "In Review", "Approved", "Issued for Construction", "As-Built", "Superseded"]
SCALES = ["1:20", "1:25", "1:50", "1:75", "1:100", "1:200", "1:500", "NTS", "Other"]


def _text(value: Any, default: str = "") -> str:
    return default if value is None else str(value).strip()


def _normalize_drawings(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.get("drawings", [])
    if not isinstance(value, list):
        value = []
    defaults = {"drawing_number": "", "title": "", "project": "", "category": "Architectural", "discipline": "Architectural", "drawing_type": "Other", "revision": "A", "status": "Draft", "scale": "1:100", "prepared_by": "", "checked_by": "", "approved_by": "", "issue_date": "", "notes": "", "created_at": ""}
    drawings: list[dict[str, Any]] = []
    for index, item in enumerate(value, 1):
        if isinstance(item, dict):
            record = {**defaults, **item}
            record["id"] = record.get("id") or index
            if not _text(record.get("category")):
                record["category"] = "Structural" if _text(record.get("discipline")).lower() == "structural" else "Architectural"
            drawings.append(record)
        elif isinstance(item, str):
            drawings.append({"id": index, **defaults, "title": item.strip()})
    database["drawings"] = drawings
    return drawings


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


def _types(category: str) -> list[str]:
    return STRUCTURAL_TYPES if category == "Structural" else ARCHITECTURAL_TYPES


def render_drawings_module(database: dict[str, Any]) -> None:
    st.title("Drawings")
    st.caption("Manage controlled architectural and structural construction drawings, revisions, approvals and issue status.")
    drawings = _normalize_drawings(database)
    architectural = [d for d in drawings if _text(d.get("category")) == "Architectural"]
    structural = [d for d in drawings if _text(d.get("category")) == "Structural"]
    issued = sum(1 for d in drawings if _text(d.get("status")).lower() == "issued for construction")
    superseded = sum(1 for d in drawings if _text(d.get("status")).lower() == "superseded")
    cols = st.columns(5)
    cols[0].metric("Total Drawings", len(drawings))
    cols[1].metric("Architectural", len(architectural))
    cols[2].metric("Structural", len(structural))
    cols[3].metric("Issued", issued)
    cols[4].metric("Superseded", superseded)
    st.divider()

    tab_architectural, tab_structural, tab_all, tab_add = st.tabs(["Architectural Drawings", "Structural Drawings", "All Drawings", "Register Drawing"])

    def render_records(records: list[dict[str, Any]], prefix: str) -> None:
        if not records:
            st.info("No drawings are registered in this category.")
            return
        search = st.text_input("Search drawings", placeholder="Search by drawing number, title, project or revision", key=f"drawing_search_{prefix}")
        term = search.strip().lower()
        filtered = [d for d in records if not term or term in " ".join(_text(d.get(k)) for k in ("drawing_number", "title", "project", "discipline", "drawing_type", "revision", "status", "prepared_by")).lower()]
        if not filtered:
            st.info("No drawings match the search.")
            return
        for index, drawing in enumerate(filtered):
            drawing_id = drawing.get("id", index + 1)
            number = _text(drawing.get("drawing_number"))
            title = _text(drawing.get("title"), "Untitled Drawing") or "Untitled Drawing"
            heading = f"{number} — {title}" if number else title
            with st.expander(heading, expanded=False):
                st.caption(f"Revision {_text(drawing.get('revision'), 'A')} | {_text(drawing.get('status'), 'Draft')}")
                category = _text(drawing.get("category"), "Architectural")
                if category not in DRAWING_CATEGORIES:
                    category = "Architectural"
                with st.form(f"drawing_edit_{prefix}_{drawing_id}"):
                    edited_number = st.text_input("Drawing Number", value=number)
                    edited_title = st.text_input("Drawing Title", value=title)
                    edited_project = st.text_input("Project", value=_text(drawing.get("project")))
                    edited_category = st.selectbox("Drawing Category", DRAWING_CATEGORIES, index=DRAWING_CATEGORIES.index(category))
                    available_types = _types(edited_category)
                    current_type = _text(drawing.get("drawing_type"), "Other")
                    if current_type not in available_types:
                        current_type = "Other"
                    edited_type = st.selectbox("Drawing Type", available_types, index=available_types.index(current_type))
                    discipline_options = ["Structural", "Civil", "Geotechnical", "Other"] if edited_category == "Structural" else ["Architectural", "Other"]
                    current_discipline = _text(drawing.get("discipline"), discipline_options[0])
                    if current_discipline not in discipline_options:
                        current_discipline = discipline_options[0]
                    edited_discipline = st.selectbox("Discipline", discipline_options, index=discipline_options.index(current_discipline))
                    edited_revision = st.text_input("Revision", value=_text(drawing.get("revision"), "A"))
                    edited_status = st.selectbox("Status", STATUSES, index=_index(STATUSES, drawing.get("status")))
                    edited_scale = st.selectbox("Scale", SCALES, index=_index(SCALES, drawing.get("scale"), SCALES.index("1:100")))
                    edited_prepared = st.text_input("Prepared By", value=_text(drawing.get("prepared_by")))
                    edited_checked = st.text_input("Checked By", value=_text(drawing.get("checked_by")))
                    edited_approved = st.text_input("Approved By", value=_text(drawing.get("approved_by")))
                    edited_issue_date = st.text_input("Issue Date", value=_text(drawing.get("issue_date")), placeholder="YYYY-MM-DD")
                    edited_notes = st.text_area("Notes", value=_text(drawing.get("notes")))
                    submitted = st.form_submit_button("Save Changes", use_container_width=True)
                if submitted:
                    if not edited_number.strip():
                        st.error("Drawing number is required.")
                    elif not edited_title.strip():
                        st.error("Drawing title is required.")
                    else:
                        drawing.update(drawing_number=edited_number.strip(), title=edited_title.strip(), project=edited_project.strip(), category=edited_category, discipline=edited_discipline, drawing_type=edited_type, revision=edited_revision.strip() or "A", status=edited_status, scale=edited_scale, prepared_by=edited_prepared.strip(), checked_by=edited_checked.strip(), approved_by=edited_approved.strip(), issue_date=edited_issue_date.strip(), notes=edited_notes.strip())
                        _save(database)
                        st.success("Drawing updated.")
                        st.rerun()
                if st.button("Delete Drawing", key=f"drawing_delete_{prefix}_{drawing_id}", use_container_width=True):
                    drawings[:] = [item for item in drawings if item is not drawing]
                    _save(database)
                    st.success("Drawing deleted.")
                    st.rerun()

    with tab_architectural:
        render_records(architectural, "architectural")
    with tab_structural:
        render_records(structural, "structural")
    with tab_all:
        render_records(drawings, "all")

    with tab_add:
        with st.form("drawing_register_form", clear_on_submit=True):
            drawing_number = st.text_input("Drawing Number", placeholder="Example: A-101")
            title = st.text_input("Drawing Title")
            project = st.text_input("Project")
            category = st.selectbox("Drawing Category", DRAWING_CATEGORIES)
            drawing_type = st.selectbox("Drawing Type", _types(category))
            discipline_options = ["Structural", "Civil", "Geotechnical", "Other"] if category == "Structural" else ["Architectural", "Other"]
            discipline = st.selectbox("Discipline", discipline_options)
            revision = st.text_input("Revision", value="A")
            status = st.selectbox("Status", STATUSES)
            scale = st.selectbox("Scale", SCALES, index=SCALES.index("1:100"))
            prepared_by = st.text_input("Prepared By")
            checked_by = st.text_input("Checked By")
            approved_by = st.text_input("Approved By")
            issue_date = st.text_input("Issue Date", placeholder="YYYY-MM-DD")
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Register Drawing", use_container_width=True)
        if submitted:
            if not drawing_number.strip():
                st.error("Drawing number is required.")
            elif not title.strip():
                st.error("Drawing title is required.")
            else:
                drawings.append({"id": _next_id(drawings), "drawing_number": drawing_number.strip(), "title": title.strip(), "project": project.strip(), "category": category, "discipline": discipline, "drawing_type": drawing_type, "revision": revision.strip() or "A", "status": status, "scale": scale, "prepared_by": prepared_by.strip(), "checked_by": checked_by.strip(), "approved_by": approved_by.strip(), "issue_date": issue_date.strip(), "notes": notes.strip(), "created_at": datetime.now().isoformat(timespec="seconds")})
                _save(database)
                st.success("Drawing registered.")
                st.rerun()