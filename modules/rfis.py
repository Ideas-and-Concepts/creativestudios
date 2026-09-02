"""Creative Studios Requests for Information module."""
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

STATUSES = ["Open", "Under Review", "Answered", "Closed", "Cancelled"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]


def _index(options: list[str], value: Any, default: int = 0) -> int:
    return options.index(value) if value in options else default


def render_rfis_module(database: dict[str, Any]) -> None:
    st.title("RFIs")
    st.caption("Requests for Information, technical queries, responses and close-out.")
    records = ensure_collection(database, "rfis")
    project_id, _ = project_selector(database, "rfis_project")
    if project_id is None:
        return
    items = project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RFIs", len(items))
    c2.metric("Open", sum(r.get("status") == "Open" for r in items))
    c3.metric("Under Review", sum(r.get("status") == "Under Review" for r in items))
    c4.metric("Closed", sum(r.get("status") == "Closed" for r in items))

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('rfi_number', 'RFI')} | {record.get('subject', 'Information request')}"):
            with st.form(f"rfi_edit_{rid}"):
                number = st.text_input("RFI Number", value=str(record.get("rfi_number", "")))
                subject = st.text_input("Subject", value=str(record.get("subject", "")))
                raised_by = st.text_input("Raised By", value=str(record.get("raised_by", "")))
                priority = st.selectbox("Priority", PRIORITIES, index=_index(PRIORITIES, record.get("priority"), 1))
                status = st.selectbox("Status", STATUSES, index=_index(STATUSES, record.get("status")))
                question = st.text_area("Question", value=str(record.get("question", "")))
                response = st.text_area("Response", value=str(record.get("response", "")))
                notes = st.text_area("Notes", value=str(record.get("notes", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not number.strip() or not subject.strip() or not question.strip():
                    st.error("RFI Number, Subject and Question are required.")
                else:
                    try:
                        save_updated_record(
                            database,
                            "rfis",
                            rid,
                            {
                                "project_id": project_id,
                                "rfi_number": number.strip(),
                                "subject": subject.strip(),
                                "raised_by": raised_by.strip(),
                                "priority": priority,
                                "status": status,
                                "question": question.strip(),
                                "response": response.strip(),
                                "notes": notes.strip(),
                                "updated_at": now_iso(),
                            },
                        )
                        st.success("RFI updated.")
                        st.rerun()
                    except Exception as exc:
                        st.error("Unable to update the RFI.")
                        with st.expander("Technical details"):
                            st.exception(exc)
            if st.button("Delete RFI", key=f"rfi_delete_{rid}", use_container_width=True):
                try:
                    remove_record(database, "rfis", rid)
                    st.success("RFI deleted.")
                    st.rerun()
                except Exception as exc:
                    st.error("Unable to delete the RFI.")
                    with st.expander("Technical details"):
                        st.exception(exc)

    st.divider()
    with st.form("rfi_add", clear_on_submit=True):
        number = st.text_input("RFI Number")
        subject = st.text_input("Subject")
        raised_by = st.text_input("Raised By")
        priority = st.selectbox("Priority", PRIORITIES, index=1)
        status = st.selectbox("Status", STATUSES)
        question = st.text_area("Question")
        response = st.text_area("Response")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add RFI", use_container_width=True)
    if submitted:
        if not number.strip() or not subject.strip() or not question.strip():
            st.error("RFI Number, Subject and Question are required.")
        else:
            try:
                save_new_record(
                    database,
                    "rfis",
                    {
                        "project_id": project_id,
                        "rfi_number": number.strip(),
                        "subject": subject.strip(),
                        "raised_by": raised_by.strip(),
                        "priority": priority,
                        "status": status,
                        "question": question.strip(),
                        "response": response.strip(),
                        "notes": notes.strip(),
                        "created_at": now_iso(),
                        "updated_at": now_iso(),
                    },
                )
                st.success("RFI added.")
                st.rerun()
            except Exception as exc:
                st.error("Unable to add the RFI.")
                with st.expander("Technical details"):
                    st.exception(exc)
