"""
Creative Studios
Sign-Off & Approvals Module

Controls technical and project document approvals.

Current supported document types:
- Drawings
- BOQ
- RFI
- Other Project Documents

Approval lifecycle:
Pending Review
Approved
Rejected
Returned for Revision
Superseded
"""

from datetime import date

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    update_record,
)


APPROVAL_STATUSES = [
    "Pending Review",
    "Approved",
    "Rejected",
    "Returned for Revision",
    "Superseded",
]

DOCUMENT_TYPES = [
    "Drawing",
    "BOQ",
    "RFI",
    "Specification",
    "Report",
    "Other",
]

APPROVAL_ACTIONS = [
    "Approve",
    "Reject",
    "Return for Revision",
]


# ============================================================
# HELPERS
# ============================================================

def _get_approvals(db):
    return get_collection(db, "approvals")


def _get_projects(db):
    return get_collection(db, "projects")


def _get_drawings(db):
    return get_collection(db, "drawings")


def _get_project_name(db, project_id):

    for project in _get_projects(db):

        if str(project.get("id")) == str(project_id):
            return project.get(
                "name",
                project_id,
            )

    return project_id


def _current_user():

    user = st.session_state.get("user")

    if isinstance(user, dict):
        return user.get(
            "username",
            "System",
        )

    return str(
        user or "System"
    )


def _approval_exists(
    db,
    project_id,
    document_type,
    document_id,
):

    for approval in _get_approvals(db):

        if (
            str(
                approval.get("project_id")
            )
            == str(project_id)
            and str(
                approval.get("document_type")
            )
            == str(document_type)
            and str(
                approval.get("document_id")
            )
            == str(document_id)
            and approval.get("status")
            == "Pending Review"
        ):
            return True

    return False


def _status_badge(status):

    if status == "Approved":

        st.success(
            status,
            icon="✓",
        )

    elif status == "Rejected":

        st.error(
            status,
            icon="×",
        )

    elif status == "Returned for Revision":

        st.warning(
            status,
            icon="↻",
        )

    elif status == "Pending Review":

        st.info(
            status,
            icon="◌",
        )

    elif status == "Superseded":

        st.caption(
            status
        )

    else:

        st.caption(
            status
        )


def _document_label(db, approval):

    document_type = approval.get(
        "document_type",
        "Document",
    )

    document_number = approval.get(
        "document_number",
        approval.get(
            "document_id",
            "N/A",
        ),
    )

    title = approval.get(
        "document_title",
        "",
    )

    if title:

        return (
            f"{document_type}: "
            f"{document_number} — {title}"
        )

    return (
        f"{document_type}: "
        f"{document_number}"
    )


# ============================================================
# APPROVAL CARD
# ============================================================

def _render_approval_card(
    db,
    approval,
):

    approval_id = approval.get(
        "id",
        "",
    )

    project_id = approval.get(
        "project_id",
        "",
    )

    status = approval.get(
        "status",
        "Pending Review",
    )

    with st.container(border=True):

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:

            st.markdown(
                f"### {_document_label(db, approval)}"
            )

            st.caption(
                f"Project: "
                f"{_get_project_name(db, project_id)}"
                f" • Approval ID: {approval_id}"
            )

        with top_right:

            _status_badge(
                status
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                "**Submitted By**"
            )

            st.write(
                approval.get(
                    "submitted_by",
                    "Unknown",
                )
            )

        with col2:

            st.markdown(
                "**Submitted Date**"
            )

            st.write(
                approval.get(
                    "submitted_date",
                    "",
                )
            )

        with col3:

            st.markdown(
                "**Reviewer**"
            )

            st.write(
                approval.get(
                    "reviewer",
                    "Not assigned",
                )
            )

        with col4:

            st.markdown(
                "**Decision Date**"
            )

            st.write(
                approval.get(
                    "decision_date",
                    "Pending",
                )
            )

        with st.expander(
            "Approval Details"
        ):

            st.markdown(
                f"**Document Type:** "
                f"{approval.get('document_type', '')}"
            )

            st.markdown(
                f"**Document ID:** "
                f"{approval.get('document_id', '')}"
            )

            st.markdown(
                f"**Revision:** "
                f"{approval.get('revision', 'N/A')}"
            )

            st.markdown(
                f"**Approval Level:** "
                f"{approval.get('approval_level', 'Standard')}"
            )

            comments = approval.get(
                "comments",
                "",
            )

            if comments:

                st.markdown(
                    f"**Comments:** {comments}"
                )

        if status == "Pending Review":

            review_col, delete_col = st.columns(
                2
            )

            with review_col:

                if st.button(
                    "Review",
                    key=f"review_{approval_id}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "review_approval_id"
                    ] = approval_id

                    st.rerun()

            with delete_col:

                if st.button(
                    "Cancel Request",
                    key=f"cancel_{approval_id}",
                    use_container_width=True,
                ):

                    st.session_state[
                        "delete_approval_id"
                    ] = approval_id

                    st.rerun()

        else:

            if st.button(
                "View Approval",
                key=f"view_{approval_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "view_approval_id"
                ] = approval_id

                st.rerun()


# ============================================================
# SUBMIT DRAWING FOR APPROVAL
# ============================================================

def _render_submit_drawing(db):

    projects = _get_projects(db)
    drawings = _get_drawings(db)

    st.subheader(
        "Submit Drawing for Approval"
    )

    if not projects:

        st.warning(
            "Create a project before submitting "
            "documents for approval."
        )

        return

    if not drawings:

        st.info(
            "No drawings are available for approval."
        )

        return

    project_options = {
        _get_project_name(
            db,
            project.get("id"),
        ):
            project.get("id")
        for project in projects
    }

    project_label = st.selectbox(
        "Project",
        list(project_options.keys()),
        key="approval_project_select",
    )

    project_id = project_options[
        project_label
    ]

    project_drawings = [
        drawing
        for drawing in drawings
        if str(
            drawing.get("project_id")
        )
        == str(project_id)
    ]

    if not project_drawings:

        st.info(
            "This project does not have any drawings."
        )

        return

    drawing_options = {
        (
            f"{drawing.get('drawing_number', '')} "
            f"— {drawing.get('title', '')} "
            f"(Rev {drawing.get('revision', '0')})"
        ):
            drawing
        for drawing in project_drawings
    }

    with st.form(
        "submit_drawing_approval"
    ):

        drawing_label = st.selectbox(
            "Drawing",
            list(drawing_options.keys()),
        )

        drawing = drawing_options[
            drawing_label
        ]

        st.info(
            f"Current drawing status: "
            f"**{drawing.get('status', 'Draft')}**"
        )

        reviewer = st.text_input(
            "Reviewer / Approver",
            placeholder="e.g. Lead Architect",
        )

        approval_level = st.selectbox(
            "Approval Level",
            [
                "Technical Review",
                "Lead Consultant",
                "Client Review",
                "Final Approval",
            ],
        )

        comments = st.text_area(
            "Submission Notes",
            placeholder=(
                "Describe the purpose of this "
                "submission or key changes."
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "Submit for Approval",
            use_container_width=True,
        )

    if not submitted:
        return

    document_id = drawing.get(
        "id"
    )

    if _approval_exists(
        db,
        project_id,
        "Drawing",
        document_id,
    ):

        st.error(
            "This drawing already has a pending "
            "approval request."
        )

        return

    approval_id = (
        f"APR-{project_id}-"
        f"{drawing.get('drawing_number')}-"
        f"REV{drawing.get('revision', '0')}"
    )

    approval = {
        "id": approval_id,
        "project_id": project_id,
        "document_type": "Drawing",
        "document_id": document_id,
        "document_number": drawing.get(
            "drawing_number",
            "",
        ),
        "document_title": drawing.get(
            "title",
            "",
        ),
        "revision": drawing.get(
            "revision",
            "0",
        ),
        "status": "Pending Review",
        "approval_level": approval_level,
        "submitted_by": _current_user(),
        "submitted_date": str(date.today()),
        "reviewer": reviewer.strip(),
        "decision_date": "",
        "decision_by": "",
        "comments": comments.strip(),
    }

    add_record(
        db,
        "approvals",
        approval,
    )

    st.success(
        f"{drawing.get('drawing_number')} "
        f"submitted for approval."
    )

    st.rerun()


# ============================================================
# REVIEW APPROVAL
# ============================================================

def _render_review_approval(
    db,
    approval,
):

    st.subheader(
        "Approval Review"
    )

    st.markdown(
        f"### {_document_label(db, approval)}"
    )

    st.caption(
        f"Project: "
        f"{_get_project_name(db, approval.get('project_id'))}"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "**Revision**"
        )

        st.write(
            approval.get(
                "revision",
                "N/A",
            )
        )

    with col2:

        st.markdown(
            "**Approval Level**"
        )

        st.write(
            approval.get(
                "approval_level",
                "Standard",
            )
        )

    with col3:

        st.markdown(
            "**Submitted By**"
        )

        st.write(
            approval.get(
                "submitted_by",
                "Unknown",
            )
        )

    st.divider()

    existing_comments = approval.get(
        "comments",
        "",
    )

    if existing_comments:

        st.markdown(
            "**Submission Notes**"
        )

        st.info(
            existing_comments
        )

    with st.form(
        f"review_form_{approval.get('id')}"
    ):

        decision = st.selectbox(
            "Decision",
            APPROVAL_ACTIONS,
        )

        reviewer = st.text_input(
            "Reviewed By",
            value=approval.get(
                "reviewer",
                "",
            ),
        )

        review_comments = st.text_area(
            "Review Comments",
            placeholder=(
                "Enter your review comments, "
                "conditions or reasons for rejection."
            ),
            height=150,
        )

        submitted = st.form_submit_button(
            "Record Decision",
            use_container_width=True,
        )

    if not submitted:
        return

    if not reviewer.strip():

        st.error(
            "Reviewer name is required."
        )

        return

    if not review_comments.strip():

        st.error(
            "Review comments are required."
        )

        return

    if decision == "Approve":
        new_status = "Approved"

    elif decision == "Reject":
        new_status = "Rejected"

    else:
        new_status = "Returned for Revision"

    updates = {
        "status": new_status,
        "reviewer": reviewer.strip(),
        "decision_date": str(date.today()),
        "decision_by": _current_user(),
        "comments": review_comments.strip(),
    }

    update_record(
        db,
        "approvals",
        approval.get("id"),
        updates,
    )

    # --------------------------------------------------------
    # Synchronize drawing status.
    # --------------------------------------------------------

    if (
        approval.get("document_type")
        == "Drawing"
    ):

        drawing_id = approval.get(
            "document_id"
        )

        if new_status == "Approved":

            drawing_status = "Approved"

        elif new_status == "Rejected":

            drawing_status = "For Review"

        else:

            drawing_status = "For Review"

        update_record(
            db,
            "drawings",
            drawing_id,
            {
                "status": drawing_status
            },
        )

    st.success(
        f"Decision recorded: {new_status}"
    )

    st.session_state.pop(
        "review_approval_id",
        None,
    )

    st.rerun()


# ============================================================
# VIEW APPROVAL
# ============================================================

def _render_view_approval(
    db,
    approval,
):

    st.subheader(
        "Approval Record"
    )

    _status_badge(
        approval.get(
            "status",
            "Pending Review",
        )
    )

    st.markdown(
        f"### {_document_label(db, approval)}"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"**Project:** "
            f"{_get_project_name(db, approval.get('project_id'))}"
        )

        st.markdown(
            f"**Document Type:** "
            f"{approval.get('document_type', '')}"
        )

        st.markdown(
            f"**Document ID:** "
            f"{approval.get('document_id', '')}"
        )

        st.markdown(
            f"**Revision:** "
            f"{approval.get('revision', 'N/A')}"
        )

    with col2:

        st.markdown(
            f"**Submitted By:** "
            f"{approval.get('submitted_by', '')}"
        )

        st.markdown(
            f"**Submitted Date:** "
            f"{approval.get('submitted_date', '')}"
        )

        st.markdown(
            f"**Reviewer:** "
            f"{approval.get('reviewer', '')}"
        )

        st.markdown(
            f"**Decision Date:** "
            f"{approval.get('decision_date', 'Pending')}"
        )

    comments = approval.get(
        "comments",
        "",
    )

    if comments:

        st.divider()

        st.markdown(
            "**Review Comments**"
        )

        st.info(
            comments
        )

    if st.button(
        "Close",
        use_container_width=True,
    ):

        st.session_state.pop(
            "view_approval_id",
            None,
        )

        st.rerun()


# ============================================================
# DELETE APPROVAL
# ============================================================

def _render_delete_confirmation(
    db,
    approval,
):

    st.warning(
        f"Cancel approval request "
        f"**{approval.get('id', '')}**?"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Cancel Approval Request",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "approvals",
                approval.get("id"),
            )

            st.session_state.pop(
                "delete_approval_id",
                None,
            )

            st.success(
                "Approval request cancelled."
            )

            st.rerun()

    with col2:

        if st.button(
            "Keep Request",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_approval_id",
                None,
            )

            st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_approvals_module(db):

    approvals = _get_approvals(db)

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                Sign-Off & Approvals
            </div>
            <div class="module-subtitle">
                Controlled review and approval workflow
                for project documents.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI DASHBOARD
    # ========================================================

    total = len(approvals)

    pending = sum(
        1
        for approval in approvals
        if approval.get("status")
        == "Pending Review"
    )

    approved = sum(
        1
        for approval in approvals
        if approval.get("status")
        == "Approved"
    )

    returned = sum(
        1
        for approval in approvals
        if approval.get("status")
        == "Returned for Revision"
    )

    rejected = sum(
        1
        for approval in approvals
        if approval.get("status")
        == "Rejected"
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Requests",
            total,
        )

    with col2:
        st.metric(
            "Pending",
            pending,
        )

    with col3:
        st.metric(
            "Approved",
            approved,
        )

    with col4:
        st.metric(
            "Returned",
            returned,
        )

    with col5:
        st.metric(
            "Rejected",
            rejected,
        )

    st.divider()

    # ========================================================
    # ACTIVE REVIEW
    # ========================================================

    review_id = st.session_state.get(
        "review_approval_id"
    )

    if review_id:

        approval = next(
            (
                item
                for item in approvals
                if str(item.get("id"))
                == str(review_id)
            ),
            None,
        )

        if approval:

            _render_review_approval(
                db,
                approval,
            )

            st.divider()

    # ========================================================
    # VIEW APPROVAL
    # ========================================================

    view_id = st.session_state.get(
        "view_approval_id"
    )

    if view_id:

        approval = next(
            (
                item
                for item in approvals
                if str(item.get("id"))
                == str(view_id)
            ),
            None,
        )

        if approval:

            _render_view_approval(
                db,
                approval,
            )

            st.divider()

    # ========================================================
    # DELETE APPROVAL
    # ========================================================

    delete_id = st.session_state.get(
        "delete_approval_id"
    )

    if delete_id:

        approval = next(
            (
                item
                for item in approvals
                if str(item.get("id"))
                == str(delete_id)
            ),
            None,
        )

        if approval:

            _render_delete_confirmation(
                db,
                approval,
            )

            st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_requests, tab_submit = st.tabs(
        [
            "Approval Register",
            "Submit for Approval",
        ]
    )

    # ========================================================
    # APPROVAL REGISTER
    # ========================================================

    with tab_requests:

        if not approvals:

            st.info(
                "No approval requests have been created."
            )

        else:

            search = st.text_input(
                "Search Approvals",
                placeholder=(
                    "Approval ID, document number, "
                    "project or reviewer..."
                ),
            )

            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"]
                    + APPROVAL_STATUSES,
                )

            with filter_col2:

                document_filter = st.selectbox(
                    "Document Type",
                    ["All"]
                    + DOCUMENT_TYPES,
                )

            search_term = (
                search.strip().lower()
            )

            filtered = []

            for approval in approvals:

                searchable = " ".join(
                    [
                        str(
                            approval.get(
                                "id",
                                "",
                            )
                        ),
                        str(
                            approval.get(
                                "document_number",
                                "",
                            )
                        ),
                        str(
                            approval.get(
                                "document_title",
                                "",
                            )
                        ),
                        str(
                            approval.get(
                                "project_id",
                                "",
                            )
                        ),
                        str(
                            approval.get(
                                "reviewer",
                                "",
                            )
                        ),
                    ]
                ).lower()

                if (
                    search_term
                    and search_term
                    not in searchable
                ):
                    continue

                if (
                    status_filter != "All"
                    and approval.get(
                        "status"
                    )
                    != status_filter
                ):
                    continue

                if (
                    document_filter != "All"
                    and approval.get(
                        "document_type"
                    )
                    != document_filter
                ):
                    continue

                filtered.append(
                    approval
                )

            st.caption(
                f"Showing {len(filtered)} "
                f"of {len(approvals)} approval records"
            )

            for approval in filtered:

                _render_approval_card(
                    db,
                    approval,
                )

    # ========================================================
    # SUBMIT FOR APPROVAL
    # ========================================================

    with tab_submit:

        _render_submit_drawing(
            db
        )