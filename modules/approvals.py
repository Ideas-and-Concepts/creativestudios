"""
Creative Studios
Approvals Module
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from modules.branding import render_module_header
from modules.database import (
    add_record,
    delete_record,
    next_id,
    update_record,
)


APPROVAL_STATUSES = [
    "Pending",
    "Approved",
    "Rejected",
    "Returned",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_approvals_module(database: dict[str, Any]) -> None:
    render_module_header(
        "Approvals",
        "Review and manage project approval workflows.",
    )

    approvals = database.get("approvals", [])
    if not isinstance(approvals, list):
        approvals = []

    search = st.text_input(
        "Search approvals",
        placeholder="Search item, project, requester or approver...",
        key="approvals_search",
    )

    if st.button("New Approval", key="new_approval"):
        st.session_state["show_approval_form"] = True

    if st.session_state.get("show_approval_form", False):
        with st.form("approval_form", clear_on_submit=True):
            item = st.text_input("Approval Item")
            project = st.text_input("Project")
            requester = st.text_input("Requested By")
            approver = st.text_input("Approver")
            comments = st.text_area("Comments")
            status = st.selectbox("Status", APPROVAL_STATUSES)

            submitted = st.form_submit_button("Create Approval", use_container_width=True)

            if submitted:
                if not item.strip():
                    st.error("Approval item is required.")
                else:
                    approval = {
                        "id": next_id("approvals", database),
                        "item": item.strip(),
                        "project": project.strip(),
                        "requester": requester.strip(),
                        "approver": approver.strip(),
                        "comments": comments.strip(),
                        "status": status,
                    }
                    add_record("approvals", approval, database)  # ✅ correct order
                    st.session_state["show_approval_form"] = False
                    st.success("Approval created.")
                    st.rerun()

    search_value = search.lower().strip()
    filtered = []

    for approval in approvals:
        if not isinstance(approval, dict):
            continue
        searchable = " ".join([
            _text(approval.get("item")),
            _text(approval.get("project")),
            _text(approval.get("requester")),
            _text(approval.get("approver")),
            _text(approval.get("status")),
        ]).lower()

        if not search_value or search_value in searchable:
            filtered.append(approval)

    cols = st.columns(4)
    metrics = [
        ("Total", len(approvals)),
        ("Pending", sum(1 for a in approvals if _text(a.get("status")).lower() == "pending")),
        ("Approved", sum(1 for a in approvals if _text(a.get("status")).lower() == "approved")),
        ("Rejected", sum(1 for a in approvals if _text(a.get("status")).lower() == "rejected")),
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            st.metric(label, value)

    st.write("")

    if not filtered:
        st.info("No approvals found.")
        return

    for approval in filtered:
        approval_id = approval.get("id")
        item = html.escape(_text(approval.get("item", "Untitled Approval")))
        project = html.escape(_text(approval.get("project", "")))
        requester = html.escape(_text(approval.get("requester", "")))
        approver = html.escape(_text(approval.get("approver", "")))
        status = html.escape(_text(approval.get("status", "Pending")))

        # ✅ KEY: unsafe_allow_html=True
        st.markdown(
            f"""
            <div class="cs-card">
                <div class="cs-card-title">{item}</div>
                <div class="cs-card-subtitle">
                    {project} &nbsp; • &nbsp;
                    Requested by: {requester} &nbsp; • &nbsp;
                    Approver: {approver} &nbsp; • &nbsp;
                    {status}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(f"Manage Approval #{approval_id}"):
            with st.form(f"edit_approval_{approval_id}"):
                edit_item = st.text_input("Approval Item", value=_text(approval.get("item")))
                edit_project = st.text_input("Project", value=_text(approval.get("project")))
                edit_requester = st.text_input("Requested By", value=_text(approval.get("requester")))
                edit_approver = st.text_input("Approver", value=_text(approval.get("approver")))

                current_status = _text(approval.get("status", "Pending"))
                status_index = APPROVAL_STATUSES.index(current_status) if current_status in APPROVAL_STATUSES else 0
                edit_status = st.selectbox("Status", APPROVAL_STATUSES, index=status_index)

                edit_comments = st.text_area("Comments", value=_text(approval.get("comments")))

                save = st.form_submit_button("Save Changes", use_container_width=True)

                if save:
                    update_record(
                        "approvals",
                        approval_id,
                        {
                            "item": edit_item.strip(),
                            "project": edit_project.strip(),
                            "requester": edit_requester.strip(),
                            "approver": edit_approver.strip(),
                            "status": edit_status,
                            "comments": edit_comments.strip(),
                        },
                        database,
                    )
                    st.success("Approval updated.")
                    st.rerun()

            if st.button("Delete Approval", key=f"delete_approval_{approval_id}"):
                delete_record("approvals", approval_id, database)
                st.success("Approval deleted.")
                st.rerun()