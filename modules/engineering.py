"""Creative Studios Engineering Module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.module_utils import (
    ensure_collection,
    now_iso,
    project_records,
    project_selector,
    remove_record,
    save_new_record,
    save_updated_record,
)

DISCIPLINES = ["Structural", "Civil", "Geotechnical", "Transportation", "Infrastructure", "Environmental", "Other"]
STATUSES = ["planned", "in_progress", "completed", "on_hold"]
ELEMENTS = ["Foundation", "Footing", "Column", "Beam", "Slab", "Structural Wall", "Stair", "Retaining Wall", "Earthworks", "Drainage", "Roadwork", "Infrastructure", "Other"]


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def render_engineering_module(database: dict[str, Any]) -> None:
    st.title("Engineering")
    st.caption("Project-linked structural, civil and technical engineering work.")

    records = ensure_collection(database, "engineering_works")
    project_id, _ = project_selector(database, "engineering_project")
    if project_id is None:
        return
    items = project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Engineering Items", len(items))
    c2.metric("Structural", sum(r.get("category") == "Structural" for r in items))
    c3.metric("Civil", sum(r.get("category") == "Civil" for r in items))
    c4.metric("Completed", sum(r.get("status") == "completed" for r in items))

    st.subheader("Engineering Register")
    if not items:
        st.info("No engineering records exist for this project yet.")

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('description', 'Engineering Item')} | {record.get('category', 'Other')}"):
            with st.form(f"engineering_edit_{rid}"):
                description = st.text_input("Engineering Work Item", value=str(record.get("description", "")))
                category = st.selectbox("Discipline", DISCIPLINES, index=_index(DISCIPLINES, record.get("category"), len(DISCIPLINES) - 1))
                element = st.selectbox("Engineering Element", ELEMENTS, index=_index(ELEMENTS, record.get("element"), len(ELEMENTS) - 1))
                status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status"), 0), format_func=lambda value: value.replace("_", " ").title())
                progress = st.number_input("Progress %", min_value=0, max_value=100, value=max(0, min(100, int(record.get("progress", 0) or 0))))
                notes = st.text_area("Technical Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not description.strip():
                    st.error("Engineering work item is required.")
                else:
                    try:
                        saved = save_updated_record(database, "engineering_works", rid, {
                            "project_id": project_id,
                            "category": category,
                            "description": f"{description.strip()} [{element}]",
                            "status": status,
                            "progress": int(progress),
                            "notes": notes.strip(),
                            "updated_at": now_iso(),
                        })
                        if not saved:
                            st.error("The engineering record could not be found.")
                        else:
                            st.success("Engineering record updated.")
                            st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the engineering record.")
                        with st.expander("Technical details"):
                            st.exception(exc)
            if st.button("Delete Record", key=f"engineering_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "engineering_works", rid):
                        st.success("Engineering record deleted.")
                        st.rerun()
                except Exception as exc:
                    st.error("Unable to delete the engineering record.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    st.subheader("Add Engineering Work")
    with st.form("engineering_add", clear_on_submit=True):
        description = st.text_input("Engineering Work Item")
        category = st.selectbox("Discipline", DISCIPLINES)
        element = st.selectbox("Engineering Element", ELEMENTS)
        status = st.selectbox("Status", STATUSES, format_func=lambda value: value.replace("_", " ").title())
        progress = st.number_input("Progress %", min_value=0, max_value=100, value=0)
        notes = st.text_area("Technical Notes")
        submitted = st.form_submit_button("Add Engineering Work", use_container_width=True)

    if submitted:
        if not description.strip():
            st.error("Engineering work item is required.")
        else:
            try:
                save_new_record(database, "engineering_works", {
                    "project_id": project_id,
                    "category": category,
                    "description": f"{description.strip()} [{element}]",
                    "status": status,
                    "progress": int(progress),
                    "notes": notes.strip(),
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                })
                st.success("Engineering work added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the engineering record.")
                with st.expander("Technical details"):
                    st.exception(exc)
