"""Creative Studios Approvals module."""
from __future__ import annotations

from typing import Any

import streamlit as st

from modules.module_utils import ensure_collection, now_iso, project_records, project_selector, save_new_record, save_updated_record

STATUSES = ["Pending", "In Review", "Approved", "Rejected", "Cancelled"]


def render_approvals_module(database: dict[str, Any]) -> None:
    st.title("Approvals")
    st.caption("Controlled review and approval of project deliverables and decisions.")
    records = ensure_collection(database, "approvals")
    project_id, _ = project_selector(database, "approvals_project")
    if project_id is None:
        return
    items = project_records(records, project_id)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Requests", len(items))
    c2.metric("Pending", sum(r.get("status") == "Pending" for r in items))
    c3.metric("In Review", sum(r.get("status") == "In Review" for r in items))
    c4.metric("Approved", sum(r.get("status") == "Approved" for r in items))

    for record in list(items):
        rid = record.get("id")
        with st.expander(f"{record.get('approval_number', 'Approval')} | {record.get('title', 'Approval request')}"):
            with st.form(f"approval_edit_{rid}"):
                number = st.text_input("Approval Number", value=str(record.get("approval_number", "")))
                title = st.text_input("Title", value=str(record.get("title", "")))
                requested_by = st.text_input("Requested By", value=str(record.get("requested_by", "")))
                approver = st.text_input("Approver", value=str(record.get("approver", "")))
                status = st.selectbox("Status", STATUSES, index=STATUSES.index(record.get("status", "Pending")) if record.get("status") in STATUSES else 0)
                comments = st.text_area("Comments", value=str(record.get("comments", "")))
                submitted = st.form_submit_button("Save Changes", use_container_width=True)
            if submitted:
                if not number.strip() or not title.strip():
                    st.error("Approval Number and Title are required.")
                else:
                    save_updated_record(database, "approvals", rid, {"approval_number": number.strip(), "title": title.strip(), "requested_by": requested_by.strip(), "approver": approver.strip(), "status": status, "comments": comments.strip(), "updated_at": now_iso()})
                    st.success("Approval updated.")
                    st.rerun()
            if st.button("Delete Approval", key=f"approval_delete_{rid}", use_container_width=True):
                from modules.database import delete_record
                delete_record("approvals", rid, database)
                st.rerun()

    st.divider()
    with st.form("approval_add", clear_on_submit=True):
        number = st.text_input("Approval Number")
        title = st.text_input("Title")
        requested_by = st.text_input("Requested By")
        approver = st.text_input("Approver")
        status = st.selectbox("Status", STATUSES)
        comments = st.text_area("Comments")
        submitted = st.form_submit_button("Add Approval", use_container_width=True)
    if submitted:
        if not number.strip() or not title.strip():
            st.error("Approval Number and Title are required.")
        else:
            save_new_record(database, "approvals", {"project_id": project_id, "approval_number": number.strip(), "title": title.strip(), "requested_by": requested_by.strip(), "approver": approver.strip(), "status": status, "comments": comments.strip(), "created_at": now_iso(), "updated_at": now_iso()})
            st.success("Approval added.")
            st.rerun()
