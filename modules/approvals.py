"""
Creative Studios
AEC Collaboration Platform
Approvals Module

Approval request management for the AEC workspace.

Uses the existing JSON database contract:

    add_record()
    update_record()
    delete_record()
    get_records()
    get_record()
    next_id()

The module receives the already-loaded database dictionary
from streamlit_app.py.

No authentication, sidebar, branding, or database initialization
is performed here.
"""

from modules.branding import render_module_header

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    get_record,
    get_records,
    update_record,
)


# ============================================================
# CONSTANTS
# ============================================================

COLLECTION = "approvals"

APPROVAL_STATUSES = [
    "Pending",
    "Under Review",
    "Approved",
    "Rejected",
    "Returned",
    "Cancelled",
]

APPROVAL_TYPES = [
    "Document",
    "Drawing",
    "Design",
    "Material",
    "Submittal",
    "Variation",
    "Method Statement",
    "Other",
]


# ============================================================
# HELPERS
# ============================================================

def _safe_text(value: Any) -> str:
    """Return a clean display string."""

    if value is None:
        return ""

    return str(value).strip()


def _format_date(value: Any) -> str:
    """Format a stored date for display."""

    if not value:
        return "Not set"

    value = _safe_text(value)

    try:
        return datetime.fromisoformat(
            value
        ).strftime("%d %b %Y")
    except ValueError:
        return value


def _now() -> str:
    """Return an ISO timestamp."""

    return datetime.now().isoformat(
        timespec="seconds"
    )


def _project_options(
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return valid project records."""

    return get_records(
        "projects",
        db,
    )


def _document_options(
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return valid document records."""

    return get_records(
        "documents",
        db,
    )


def _drawing_options(
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return valid drawing records."""

    return get_records(
        "drawings",
        db,
    )


def _user_options(
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return valid users."""

    return get_records(
        "users",
        db,
    )


def _project_name(
    project_id: Any,
    db: dict[str, Any],
) -> str:
    """Resolve project name."""

    if not project_id:
        return "Unlinked"

    project = get_record(
        "projects",
        project_id,
        db,
    )

    if not project:
        return f"Missing project #{project_id}"

    return (
        _safe_text(
            project.get("name")
        )
        or _safe_text(
            project.get("project_name")
        )
        or f"Project #{project_id}"
    )


def _document_name(
    document_id: Any,
    db: dict[str, Any],
) -> str:
    """Resolve document name."""

    if not document_id:
        return "None"

    document = get_record(
        "documents",
        document_id,
        db,
    )

    if not document:
        return f"Missing document #{document_id}"

    return (
        _safe_text(
            document.get("title")
        )
        or _safe_text(
            document.get("name")
        )
        or f"Document #{document_id}"
    )


def _drawing_name(
    drawing_id: Any,
    db: dict[str, Any],
) -> str:
    """Resolve drawing name."""

    if not drawing_id:
        return "None"

    drawing = get_record(
        "drawings",
        drawing_id,
        db,
    )

    if not drawing:
        return f"Missing drawing #{drawing_id}"

    return (
        _safe_text(
            drawing.get("title")
        )
        or _safe_text(
            drawing.get("name")
        )
        or _safe_text(
            drawing.get("drawing_number")
        )
        or f"Drawing #{drawing_id}"
    )


def _user_name(
    user_id: Any,
    db: dict[str, Any],
) -> str:
    """Resolve a user name."""

    if not user_id:
        return "Unassigned"

    user = get_record(
        "users",
        user_id,
        db,
    )

    if not user:
        return f"Missing user #{user_id}"

    return (
        _safe_text(
            user.get("full_name")
        )
        or _safe_text(
            user.get("name")
        )
        or _safe_text(
            user.get("username")
        )
        or f"User #{user_id}"
    )


def _status_message(
    status: str,
) -> str:
    """Return a compact status description."""

    messages = {
        "Pending": "Awaiting review.",
        "Under Review": "Currently being reviewed.",
        "Approved": "Approval granted.",
        "Rejected": "Approval rejected.",
        "Returned": "Returned for correction.",
        "Cancelled": "Approval request cancelled.",
    }

    return messages.get(
        status,
        "Approval status.",
    )


def _reset_form_state() -> None:
    """Clear approval form session state."""

    for key in (
        "approval_edit_id",
        "approval_view_id",
    ):
        st.session_state.pop(
            key,
            None,
        )


# ============================================================
# VALIDATION
# ============================================================

def _validate_approval(
    title: str,
    approval_type: str,
    project_id: Any,
    due_date: str,
) -> list[str]:
    """Validate an approval record."""

    errors: list[str] = []

    if not title.strip():
        errors.append(
            "Approval title is required."
        )

    if not approval_type.strip():
        errors.append(
            "Approval type is required."
        )

    if not project_id:
        errors.append(
            "A project must be selected."
        )

    if due_date:

        try:

            date.fromisoformat(
                due_date
            )

        except ValueError:

            errors.append(
                "Due date is invalid."
            )

    return errors


# ============================================================
# CREATE
# ============================================================

def _create_approval(
    db: dict[str, Any],
) -> None:

    st.markdown(
        "### New Approval"
    )

    projects = _project_options(db)
    documents = _document_options(db)
    drawings = _drawing_options(db)
    users = _user_options(db)

    if not projects:

        st.warning(
            "Create a project before creating an approval."
        )

        return

    project_labels = [
        f"{p.get('id')} · "
        f"{p.get('name', p.get('project_name', 'Unnamed Project'))}"
        for p in projects
    ]

    document_labels = [
        "None"
    ] + [
        f"{d.get('id')} · "
        f"{d.get('title', d.get('name', 'Untitled Document'))}"
        for d in documents
    ]

    drawing_labels = [
        "None"
    ] + [
        f"{d.get('id')} · "
        f"{d.get('drawing_number', d.get('title', d.get('name', 'Untitled Drawing')))}"
        for d in drawings
    ]

    user_labels = [
        "Unassigned"
    ] + [
        f"{u.get('id')} · "
        f"{u.get('full_name', u.get('username', 'Unknown User'))}"
        for u in users
    ]

    with st.form(
        "approval_create_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            title = st.text_input(
                "Approval Title",
                placeholder="e.g. Structural Drawing Approval",
            )

            approval_type = st.selectbox(
                "Approval Type",
                APPROVAL_TYPES,
            )

            project_label = st.selectbox(
                "Project",
                project_labels,
            )

            status = st.selectbox(
                "Status",
                APPROVAL_STATUSES,
            )

        with col2:

            reviewer_label = st.selectbox(
                "Reviewer / Approver",
                user_labels,
            )

            due_date = st.date_input(
                "Due Date",
                value=None,
            )

            document_label = st.selectbox(
                "Linked Document",
                document_labels,
            )

            drawing_label = st.selectbox(
                "Linked Drawing",
                drawing_labels,
            )

        description = st.text_area(
            "Description",
            placeholder=(
                "Describe what requires approval..."
            ),
        )

        submitted = st.form_submit_button(
            "Create Approval",
            use_container_width=True,
        )

        if submitted:

            project_id = project_label.split(
                " · ",
                1,
            )[0]

            reviewer_id = None

            if reviewer_label != "Unassigned":

                reviewer_id = reviewer_label.split(
                    " · ",
                    1,
                )[0]

            document_id = None

            if document_label != "None":

                document_id = document_label.split(
                    " · ",
                    1,
                )[0]

            drawing_id = None

            if drawing_label != "None":

                drawing_id = drawing_label.split(
                    " · ",
                    1,
                )[0]

            due_value = ""

            if due_date:

                due_value = due_date.isoformat()

            errors = _validate_approval(
                title,
                approval_type,
                project_id,
                due_value,
            )

            if errors:

                for error in errors:
                    st.error(error)

                return

            record = {
                "title": title.strip(),
                "approval_type": approval_type,
                "project_id": project_id,
                "document_id": document_id,
                "drawing_id": drawing_id,
                "assigned_to": reviewer_id,
                "status": status,
                "due_date": due_value,
                "description": description.strip(),
                "decision": "",
                "decision_notes": "",
                "created_at": _now(),
                "updated_at": _now(),
            }

            try:

                created = add_record(
                    COLLECTION,
                    record,
                    db,
                )

                st.session_state[
                    "approval_view_id"
                ] = created.get("id")

                st.success(
                    "Approval created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to create approval."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ============================================================
# LIST
# ============================================================

def _render_approval_list(
    db: dict[str, Any],
) -> None:

    approvals = get_records(
        COLLECTION,
        db,
    )

    projects = _project_options(db)

    st.markdown(
        "### Approval Register"
    )

    search = st.text_input(
        "Search approvals",
        placeholder=(
            "Search title, type, project or status..."
        ),
        key="approval_search",
    )

    col1, col2 = st.columns(2)

    with col1:

        status_filter = st.selectbox(
            "Status",
            ["All"] + APPROVAL_STATUSES,
            key="approval_status_filter",
        )

    with col2:

        project_filter_options = [
            "All"
        ] + [
            f"{p.get('id')} · "
            f"{p.get('name', p.get('project_name', 'Unnamed Project'))}"
            for p in projects
        ]

        project_filter = st.selectbox(
            "Project",
            project_filter_options,
            key="approval_project_filter",
        )

    search_text = search.strip().lower()

    filtered: list[dict[str, Any]] = []

    for approval in approvals:

        if status_filter != "All":

            if approval.get("status") != status_filter:
                continue

        if project_filter != "All":

            selected_project_id = (
                project_filter.split(
                    " · ",
                    1,
                )[0]
            )

            if str(
                approval.get("project_id")
            ) != str(
                selected_project_id
            ):
                continue

        searchable = " ".join(
            [
                _safe_text(
                    approval.get("title")
                ),
                _safe_text(
                    approval.get("approval_type")
                ),
                _project_name(
                    approval.get("project_id"),
                    db,
                ),
                _safe_text(
                    approval.get("status")
                ),
            ]
        ).lower()

        if search_text and search_text not in searchable:
            continue

        filtered.append(
            approval
        )

    st.caption(
        f"{len(filtered)} approval(s)"
    )

    if not filtered:

        st.info(
            "No approvals match the current filters."
        )

        return

    for approval in filtered:

        approval_id = approval.get(
            "id"
        )

        title = (
            _safe_text(
                approval.get("title")
            )
            or f"Approval #{approval_id}"
        )

        status = (
            _safe_text(
                approval.get("status")
            )
            or "Pending"
        )

        project = _project_name(
            approval.get("project_id"),
            db,
        )

        due = _format_date(
            approval.get("due_date")
        )

        st.markdown(
            f"""
            <div class="cs-card" style="
                margin-bottom:10px;
            ">
                <div style="
                    color:#FFFFFF;
                    font-size:17px;
                    font-weight:850;
                ">
                    {title}
                </div>

                <div style="
                    color:#64748B;
                    font-size:11px;
                    margin-top:5px;
                ">
                    #{approval_id}
                    · {approval.get("approval_type", "Other")}
                    · {project}
                </div>

                <div style="
                    margin-top:10px;
                    color:#94A3B8;
                    font-size:12px;
                ">
                    Status:
                    <strong style="color:#60A5FA;">
                        {status}
                    </strong>
                    &nbsp; · &nbsp;
                    Due:
                    <strong style="color:#CBD5E1;">
                        {due}
                    </strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(
            [1, 1, 1]
        )

        with c1:

            if st.button(
                "View",
                key=f"approval_view_{approval_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "approval_view_id"
                ] = approval_id

                st.rerun()

        with c2:

            if st.button(
                "Edit",
                key=f"approval_edit_{approval_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "approval_edit_id"
                ] = approval_id

                st.session_state.pop(
                    "approval_view_id",
                    None,
                )

                st.rerun()

        with c3:

            if st.button(
                "Delete",
                key=f"approval_delete_{approval_id}",
                use_container_width=True,
            ):

                try:

                    delete_record(
                        COLLECTION,
                        approval_id,
                        db,
                    )

                    st.session_state.pop(
                        "approval_view_id",
                        None,
                    )

                    st.session_state.pop(
                        "approval_edit_id",
                        None,
                    )

                    st.success(
                        "Approval deleted."
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        "Unable to delete approval."
                    )

                    st.code(
                        f"{type(exc).__name__}: {exc}"
                    )


# ============================================================
# VIEW
# ============================================================

def _render_approval_view(
    approval: dict[str, Any],
    db: dict[str, Any],
) -> None:

    approval_id = approval.get(
        "id"
    )

    st.markdown(
        f"### Approval #{approval_id}"
    )

    title = (
        _safe_text(
            approval.get("title")
        )
        or f"Approval #{approval_id}"
    )

    status = (
        _safe_text(
            approval.get("status")
        )
        or "Pending"
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div style="
                color:#FFFFFF;
                font-size:22px;
                font-weight:900;
            ">
                {title}
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:6px;
            ">
                {_safe_text(approval.get("approval_type"))}
                ·
                {_project_name(
                    approval.get("project_id"),
                    db
                )}
            </div>

            <div style="
                color:#60A5FA;
                font-size:13px;
                font-weight:800;
                margin-top:14px;
            ">
                {status}
            </div>

            <div style="
                color:#94A3B8;
                font-size:12px;
                margin-top:5px;
            ">
                {_status_message(status)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "**Project**"
        )

        st.write(
            _project_name(
                approval.get("project_id"),
                db,
            )
        )

    with col2:

        st.markdown(
            "**Reviewer / Approver**"
        )

        st.write(
            _user_name(
                approval.get("assigned_to"),
                db,
            )
        )

    with col3:

        st.markdown(
            "**Due Date**"
        )

        st.write(
            _format_date(
                approval.get("due_date")
            )
        )

    st.divider()

    st.markdown(
        "**Linked Document**"
    )

    st.write(
        _document_name(
            approval.get("document_id"),
            db,
        )
    )

    st.markdown(
        "**Linked Drawing**"
    )

    st.write(
        _drawing_name(
            approval.get("drawing_id"),
            db,
        )
    )

    st.markdown(
        "**Description**"
    )

    description = _safe_text(
        approval.get("description")
    )

    st.write(
        description
        or "No description provided."
    )

    st.divider()

    st.markdown(
        "### Decision"
    )

    st.write(
        approval.get(
            "decision"
        )
        or "No decision recorded."
    )

    if approval.get(
        "decision_notes"
    ):

        st.markdown(
            "**Decision Notes**"
        )

        st.write(
            approval.get(
                "decision_notes"
            )
        )

    if status not in (
        "Approved",
        "Rejected",
        "Cancelled",
    ):

        st.markdown(
            "### Record Decision"
        )

        with st.form(
            f"approval_decision_{approval_id}"
        ):

            decision = st.selectbox(
                "Decision",
                [
                    "Approved",
                    "Rejected",
                    "Returned",
                ],
            )

            decision_notes = st.text_area(
                "Decision Notes",
            )

            submitted = st.form_submit_button(
                "Save Decision",
                use_container_width=True,
            )

            if submitted:

                try:

                    updated = update_record(
                        COLLECTION,
                        approval_id,
                        {
                            "status": decision,
                            "decision": decision,
                            "decision_notes": (
                                decision_notes.strip()
                            ),
                            "decided_at": _now(),
                            "updated_at": _now(),
                        },
                        db,
                    )

                    if updated:

                        st.success(
                            "Approval decision recorded."
                        )

                        st.rerun()

                except Exception as exc:

                    st.error(
                        "Unable to save the decision."
                    )

                    st.code(
                        f"{type(exc).__name__}: {exc}"
                    )

    st.write("")

    if st.button(
        "Back to Approvals",
        key=f"approval_back_{approval_id}",
    ):

        st.session_state.pop(
            "approval_view_id",
            None,
        )

        st.rerun()


# ============================================================
# EDIT
# ============================================================

def _render_approval_edit(
    approval: dict[str, Any],
    db: dict[str, Any],
) -> None:

    approval_id = approval.get(
        "id"
    )

    st.markdown(
        f"### Edit Approval #{approval_id}"
    )

    projects = _project_options(db)
    documents = _document_options(db)
    drawings = _drawing_options(db)
    users = _user_options(db)

    project_labels = [
        f"{p.get('id')} · "
        f"{p.get('name', p.get('project_name', 'Unnamed Project'))}"
        for p in projects
    ]

    document_labels = [
        "None"
    ] + [
        f"{d.get('id')} · "
        f"{d.get('title', d.get('name', 'Untitled Document'))}"
        for d in documents
    ]

    drawing_labels = [
        "None"
    ] + [
        f"{d.get('id')} · "
        f"{d.get('drawing_number', d.get('title', d.get('name', 'Untitled Drawing')))}"
        for d in drawings
    ]

    user_labels = [
        "Unassigned"
    ] + [
        f"{u.get('id')} · "
        f"{u.get('full_name', u.get('username', 'Unknown User'))}"
        for u in users
    ]

    current_project = str(
        approval.get(
            "project_id",
            "",
        )
    )

    project_index = 0

    for index, label in enumerate(
        project_labels
    ):

        if label.split(
            " · ",
            1,
        )[0] == current_project:

            project_index = index
            break

    current_document = str(
        approval.get(
            "document_id",
            "",
        )
    )

    document_index = 0

    for index, label in enumerate(
        document_labels
    ):

        if (
            label != "None"
            and label.split(
                " · ",
                1,
            )[0] == current_document
        ):

            document_index = index
            break

    current_drawing = str(
        approval.get(
            "drawing_id",
            "",
        )
    )

    drawing_index = 0

    for index, label in enumerate(
        drawing_labels
    ):

        if (
            label != "None"
            and label.split(
                " · ",
                1,
            )[0] == current_drawing
        ):

            drawing_index = index
            break

    current_user = str(
        approval.get(
            "assigned_to",
            "",
        )
    )

    user_index = 0

    for index, label in enumerate(
        user_labels
    ):

        if (
            label != "Unassigned"
            and label.split(
                " · ",
                1,
            )[0] == current_user
        ):

            user_index = index
            break

    current_due = None

    if approval.get(
        "due_date"
    ):

        try:

            current_due = date.fromisoformat(
                str(
                    approval.get(
                        "due_date"
                    )
                )
            )

        except ValueError:
            current_due = None

    with st.form(
        f"approval_edit_form_{approval_id}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            title = st.text_input(
                "Approval Title",
                value=_safe_text(
                    approval.get("title")
                ),
            )

            approval_type = st.selectbox(
                "Approval Type",
                APPROVAL_TYPES,
                index=(
                    APPROVAL_TYPES.index(
                        approval.get(
                            "approval_type"
                        )
                    )
                    if approval.get(
                        "approval_type"
                    ) in APPROVAL_TYPES
                    else 0
                ),
            )

            project_label = st.selectbox(
                "Project",
                project_labels,
                index=project_index,
            )

            status = st.selectbox(
                "Status",
                APPROVAL_STATUSES,
                index=(
                    APPROVAL_STATUSES.index(
                        approval.get(
                            "status"
                        )
                    )
                    if approval.get(
                        "status"
                    ) in APPROVAL_STATUSES
                    else 0
                ),
            )

        with col2:

            reviewer_label = st.selectbox(
                "Reviewer / Approver",
                user_labels,
                index=user_index,
            )

            due_date = st.date_input(
                "Due Date",
                value=current_due,
            )

            document_label = st.selectbox(
                "Linked Document",
                document_labels,
                index=document_index,
            )

            drawing_label = st.selectbox(
                "Linked Drawing",
                drawing_labels,
                index=drawing_index,
            )

        description = st.text_area(
            "Description",
            value=_safe_text(
                approval.get("description")
            ),
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

        if submitted:

            project_id = project_label.split(
                " · ",
                1,
            )[0]

            reviewer_id = None

            if reviewer_label != "Unassigned":

                reviewer_id = reviewer_label.split(
                    " · ",
                    1,
                )[0]

            document_id = None

            if document_label != "None":

                document_id = document_label.split(
                    " · ",
                    1,
                )[0]

            drawing_id = None

            if drawing_label != "None":

                drawing_id = drawing_label.split(
                    " · ",
                    1,
                )[0]

            due_value = ""

            if due_date:

                due_value = due_date.isoformat()

            errors = _validate_approval(
                title,
                approval_type,
                project_id,
                due_value,
            )

            if errors:

                for error in errors:
                    st.error(error)

                return

            updates = {
                "title": title.strip(),
                "approval_type": approval_type,
                "project_id": project_id,
                "document_id": document_id,
                "drawing_id": drawing_id,
                "assigned_to": reviewer_id,
                "status": status,
                "due_date": due_value,
                "description": description.strip(),
                "updated_at": _now(),
            }

            try:

                update_record(
                    COLLECTION,
                    approval_id,
                    updates,
                    db,
                )

                st.session_state.pop(
                    "approval_edit_id",
                    None,
                )

                st.session_state[
                    "approval_view_id"
                ] = approval_id

                st.success(
                    "Approval updated successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to update approval."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )

    if st.button(
        "Cancel",
        key=f"approval_cancel_edit_{approval_id}",
    ):

        st.session_state.pop(
            "approval_edit_id",
            None,
        )

        st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_approvals_module(
    db: dict[str, Any],
) -> None:
    """
    Render the Approvals workspace.

    Branding and the global module header intentionally remain
    outside this module so the existing application's visual
    system remains the single source of truth.
    """

    if not isinstance(
        db,
        dict,
    ):

        st.error(
            "Invalid database object."
        )

        return

    # --------------------------------------------------------
    # Session state
    # --------------------------------------------------------

    st.session_state.setdefault(
        "approval_view_id",
        None,
    )

    st.session_state.setdefault(
        "approval_edit_id",
        None,
    )

    # --------------------------------------------------------
    # Module header
    #
    # Keep your existing application-level SVG/module-header
    # helper here. The module itself does not replace it.
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-page-title">Approvals</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Review, approve and track project submissions and decisions."
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Selected record
    # --------------------------------------------------------

    edit_id = st.session_state.get(
        "approval_edit_id"
    )

    view_id = st.session_state.get(
        "approval_view_id"
    )

    if edit_id:

        approval = get_record(
            COLLECTION,
            edit_id,
            db,
        )

        if not approval:

            st.warning(
                "The selected approval no longer exists."
            )

            st.session_state.pop(
                "approval_edit_id",
                None,
            )

            return

        _render_approval_edit(
            approval,
            db,
        )

        return

    if view_id:

        approval = get_record(
            COLLECTION,
            view_id,
            db,
        )

        if not approval:

            st.warning(
                "The selected approval no longer exists."
            )

            st.session_state.pop(
                "approval_view_id",
                None,
            )

            return

        _render_approval_view(
            approval,
            db,
        )

        return

    # --------------------------------------------------------
    # Main tabs
    # --------------------------------------------------------

    tab_register, tab_create = st.tabs(
        [
            "Approval Register",
            "New Approval",
        ]
    )

    with tab_register:

        _render_approval_list(
            db
        )

    with tab_create:

        _create_approval(
            db
        )