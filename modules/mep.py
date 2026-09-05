"""Creative Studios MEP Module."""
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

DISCIPLINES = ["mechanical", "electrical", "plumbing", "fire_protection", "hvac", "public_health", "other"]
STATUSES = ["planned", "in_progress", "completed", "on_hold"]


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def _label(value: str) -> str:
    return value.replace("_", " ").title()


def render_mep_module(database: dict[str, Any]) -> None:
    st.title("MEP")
    st.caption("Project-linked mechanical, electrical, plumbing and specialist building-services coordination.")

    records = ensure_collection(database, "mep_works")
    project_id, _ = project_selector(database, "mep_project")
    if project_id is None:
        return
    items = project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MEP Items", len(items))
    c2.metric("Mechanical", sum(r.get("discipline") == "mechanical" for r in items))
    c3.metric("Electrical", sum(r.get("discipline") == "electrical" for r in items))
    c4.metric("Plumbing", sum(r.get("discipline") == "plumbing" for r in items))

    st.subheader("MEP Coordination Register")
    if not items:
        st.info("No MEP records exist for this project yet.")

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('description', 'MEP Item')} | {_label(str(record.get('discipline', 'other')))}"):
            with st.form(f"mep_edit_{rid}"):
                description = st.text_input("MEP Work Item", value=str(record.get("description", "")))
                discipline = st.selectbox("Discipline", DISCIPLINES, index=_index(DISCIPLINES, record.get("discipline"), 0), format_func=_label)
                category = st.text_input("System / Category", value=str(record.get("category", "")))
                specification = st.text_area("Specification", value=str(record.get("specification", "")))
                status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status"), 0), format_func=_label)
                progress = st.number_input("Progress %", min_value=0, max_value=100, value=max(0, min(100, int(record.get("progress", 0) or 0))))
                notes = st.text_area("Coordination Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not description.strip() or not category.strip():
                    st.error("MEP Work Item and System / Category are required.")
                else:
                    try:
                        saved = save_updated_record(database, "mep_works", rid, {
                            "project_id": project_id,
                            "discipline": discipline,
                            "category": category.strip(),
                            "description": description.strip(),
                            "specification": specification.strip(),
                            "status": status,
                            "progress": int(progress),
                            "notes": notes.strip(),
                            "updated_at": now_iso(),
                        })
                        if not saved:
                            st.error("The MEP record could not be found.")
                        else:
                            st.success("MEP record updated.")
                            st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the MEP record.")
                        with st.expander("Technical details"):
                            st.exception(exc)
            if st.button("Delete Record", key=f"mep_delete_{rid}", use_container_width=True):
                try:
                    if remove_record(database, "mep_works", rid):
                        st.success("MEP record deleted.")
                        st.rerun()
                except Exception as exc:
                    st.error("Unable to delete the MEP record.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    st.subheader("Add MEP Work")
    with st.form("mep_add", clear_on_submit=True):
        description = st.text_input("MEP Work Item")
        discipline = st.selectbox("Discipline", DISCIPLINES, format_func=_label)
        category = st.text_input("System / Category", placeholder="HVAC, Lighting, Water Supply, Fire Protection...")
        specification = st.text_area("Specification")
        status = st.selectbox("Status", STATUSES, format_func=_label)
        progress = st.number_input("Progress %", min_value=0, max_value=100, value=0)
        notes = st.text_area("Coordination Notes")
        submitted = st.form_submit_button("Add MEP Work", use_container_width=True)

    if submitted:
        if not description.strip() or not category.strip():
            st.error("MEP Work Item and System / Category are required.")
        else:
            try:
                save_new_record(database, "mep_works", {
                    "project_id": project_id,
                    "discipline": discipline,
                    "category": category.strip(),
                    "description": description.strip(),
                    "specification": specification.strip(),
                    "status": status,
                    "progress": int(progress),
                    "notes": notes.strip(),
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                })
                st.success("MEP work added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the MEP record.")
                with st.expander("Technical details"):
                    st.exception(exc)
