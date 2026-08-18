"""
Creative Studios
AEC Collaboration Platform

RFI Module
----------
Requests for Information management for the AEC workspace.

Features:
    - Create RFI
    - Search RFIs
    - Filter by project
    - Filter by status
    - Filter by priority
    - View RFI details
    - Edit RFI
    - Delete RFI
    - Project linking
    - Status tracking
    - Persistence through modules.database
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    get_records,
    update_record,
)


# ============================================================
# CONSTANTS
# ============================================================

RFI_COLLECTION = "rfis"

STATUS_OPTIONS = [
    "Open",
    "Under Review",
    "Answered",
    "Closed",
    "Rejected",
]

PRIORITY_OPTIONS = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

CATEGORY_OPTIONS = [
    "Architectural",
    "Structural",
    "Civil",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Fire Protection",
    "Quantity Surveying",
    "General",
]


# ============================================================
# CSS
# ============================================================

def _render_css() -> None:

    st.markdown(
        """
        <style>

        .rfi-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 12px;
        }

        .rfi-title {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 850;
        }

        .rfi-number {
            color: #60A5FA;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.7px;
            margin-bottom: 5px;
        }

        .rfi-description {
            color: #94A3B8;
            font-size: 12px;
            line-height: 1.55;
            margin-top: 8px;
        }

        .rfi-meta {
            color: #64748B;
            font-size: 11px;
            margin-top: 10px;
        }

        .rfi-badge {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 800;
            margin-right: 5px;
        }

        .rfi-status-open {
            background: rgba(37, 99, 235, 0.15);
            color: #60A5FA;
        }

        .rfi-status-review {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
        }

        .rfi-status-answered {
            background: rgba(16, 185, 129, 0.15);
            color: #6EE7B7;
        }

        .rfi-status-closed {
            background: rgba(100, 116, 139, 0.15);
            color: #CBD5E1;
        }

        .rfi-status-rejected {
            background: rgba(239, 68, 68, 0.15);
            color: #FCA5A5;
        }

        .rfi-priority-low {
            background: rgba(100, 116, 139, 0.15);
            color: #CBD5E1;
        }

        .rfi-priority-medium {
            background: rgba(37, 99, 235, 0.15);
            color: #93C5FD;
        }

        .rfi-priority-high {
            background: rgba(245, 158, 11, 0.15);
            color: #FBBF24;
        }

        .rfi-priority-critical {
            background: rgba(220, 38, 38, 0.15);
            color: #FCA5A5;
        }

        .rfi-empty {
            background: #0B0F17;
            border: 1px dashed #243047;
            border-radius: 15px;
            padding: 35px;
            text-align: center;
            color: #64748B;
        }

        .rfi-detail-label {
            color: #64748B;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .rfi-detail-value {
            color: #E2E8F0;
            font-size: 13px;
            margin-top: 4px;
            margin-bottom: 14px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def _now() -> str:
    return datetime.now().isoformat(
        timespec="seconds"
    )


def _safe_text(
    value: Any,
) -> str:

    if value is None:
        return ""

    return str(value).strip()


def _project_name(
    project: dict[str, Any],
) -> str:

    return (
        _safe_text(
            project.get("name")
        )
        or _safe_text(
            project.get("project_name")
        )
        or f"Project #{project.get('id', '')}"
    )


def _get_projects(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    projects = get_records(
        "projects",
        db,
    )

    return [
        project
        for project in projects
        if isinstance(project, dict)
    ]


def _get_project_map(
    db: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    projects = _get_projects(db)

    result = {}

    for project in projects:

        project_id = project.get("id")

        if project_id is not None:

            result[str(project_id)] = project

    return result


def _status_class(
    status: str,
) -> str:

    value = status.lower()

    if value == "under review":
        return "rfi-status-review"

    if value == "answered":
        return "rfi-status-answered"

    if value == "closed":
        return "rfi-status-closed"

    if value == "rejected":
        return "rfi-status-rejected"

    return "rfi-status-open"


def _priority_class(
    priority: str,
) -> str:

    value = priority.lower()

    if value == "critical":
        return "rfi-priority-critical"

    if value == "high":
        return "rfi-priority-high"

    if value == "medium":
        return "rfi-priority-medium"

    return "rfi-priority-low"


def _next_rfi_number(
    rfis: list[dict[str, Any]],
) -> str:

    highest = 0

    for rfi in rfis:

        number = _safe_text(
            rfi.get("rfi_number")
        )

        if not number:
            continue

        digits = ""

        for char in reversed(number):

            if char.isdigit():
                digits = char + digits
            else:
                break

        if digits:

            try:
                highest = max(
                    highest,
                    int(digits),
                )
            except ValueError:
                pass

    return f"RFI-{highest + 1:04d}"


# ============================================================
# CREATE
# ============================================================

def _create_rfi(
    db: dict[str, Any],
) -> None:

    st.markdown(
        "### New RFI"
    )

    projects = _get_projects(db)

    if not projects:

        st.warning(
            "Create a project before creating an RFI."
        )

        return

    project_options = {
        _project_name(project): project.get("id")
        for project in projects
    }

    with st.form(
        "create_rfi_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_label = st.selectbox(
                "Project *",
                list(
                    project_options.keys()
                ),
            )

            subject = st.text_input(
                "Subject *",
                placeholder="Enter the RFI subject",
            )

            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
            )

        with col2:

            priority = st.selectbox(
                "Priority",
                PRIORITY_OPTIONS,
                index=1,
            )

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
            )

            requested_by = st.text_input(
                "Requested By",
                placeholder="Person raising the RFI",
            )

        question = st.text_area(
            "Question / Request *",
            placeholder=(
                "Describe the information or clarification "
                "required."
            ),
            height=130,
        )

        response = st.text_area(
            "Response",
            placeholder="Response can be added later.",
            height=110,
        )

        col1, col2 = st.columns(2)

        with col1:

            due_date = st.date_input(
                "Required By",
                value=None,
            )

        with col2:

            assigned_to = st.text_input(
                "Assigned To",
                placeholder="Responsible person",
            )

        submitted = st.form_submit_button(
            "Create RFI",
            use_container_width=True,
        )

        if submitted:

            if not subject.strip():

                st.error(
                    "RFI subject is required."
                )

                return

            if not question.strip():

                st.error(
                    "RFI question is required."
                )

                return

            project_id = project_options[
                project_label
            ]

            rfis = get_records(
                RFI_COLLECTION,
                db,
            )

            rfi_number = _next_rfi_number(
                rfis
            )

            record = {
                "rfi_number": rfi_number,
                "project_id": project_id,
                "subject": subject.strip(),
                "category": category,
                "priority": priority,
                "status": status,
                "question": question.strip(),
                "response": response.strip(),
                "requested_by": requested_by.strip(),
                "assigned_to": assigned_to.strip(),
                "due_date": (
                    due_date.isoformat()
                    if due_date
                    else ""
                ),
                "created_at": _now(),
                "updated_at": _now(),
            }

            try:

                add_record(
                    RFI_COLLECTION,
                    record,
                    db,
                )

                st.success(
                    f"{rfi_number} created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to create the RFI."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ============================================================
# VIEW
# ============================================================

def _view_rfi(
    rfi: dict[str, Any],
    db: dict[str, Any],
) -> None:

    project_map = _get_project_map(
        db
    )

    project = project_map.get(
        str(
            rfi.get(
                "project_id"
            )
        )
    )

    project_name = (
        _project_name(project)
        if project
        else "Unlinked Project"
    )

    status = _safe_text(
        rfi.get(
            "status",
            "Open",
        )
    )

    priority = _safe_text(
        rfi.get(
            "priority",
            "Medium",
        )
    )

    st.markdown(
        f"""
        <div class="rfi-card">

            <div class="rfi-number">
                {_safe_text(rfi.get("rfi_number"))}
            </div>

            <div class="rfi-title">
                {_safe_text(rfi.get("subject"))}
            </div>

            <div style="margin-top:9px;">

                <span class="rfi-badge {_status_class(status)}">
                    {status}
                </span>

                <span class="rfi-badge {_priority_class(priority)}">
                    {priority}
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="rfi-detail-label">Project</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{project_name}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="rfi-detail-label">Category</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{_safe_text(rfi.get('category'))}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            '<div class="rfi-detail-label">Requested By</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{_safe_text(rfi.get('requested_by')) or 'Not specified'}"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="rfi-detail-label">Question / Request</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="rfi-detail-value">'
        f"{_safe_text(rfi.get('question')) or 'No question provided.'}"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="rfi-detail-label">Response</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="rfi-detail-value">'
        f"{_safe_text(rfi.get('response')) or 'No response yet.'}"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="rfi-detail-label">Assigned To</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{_safe_text(rfi.get('assigned_to')) or 'Unassigned'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="rfi-detail-label">Required By</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{_safe_text(rfi.get('due_date')) or 'Not specified'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            '<div class="rfi-detail-label">Last Updated</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="rfi-detail-value">'
            f"{_safe_text(rfi.get('updated_at')) or 'Unknown'}"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# EDIT
# ============================================================

def _edit_rfi(
    rfi: dict[str, Any],
    db: dict[str, Any],
) -> None:

    projects = _get_projects(db)

    project_options = {
        _project_name(project): project.get("id")
        for project in projects
    }

    current_project_id = str(
        rfi.get(
            "project_id",
            "",
        )
    )

    project_labels = list(
        project_options.keys()
    )

    current_project_index = 0

    for index, label in enumerate(
        project_labels
    ):

        if str(
            project_options[label]
        ) == current_project_id:

            current_project_index = index
            break

    current_status = _safe_text(
        rfi.get(
            "status",
            "Open",
        )
    )

    current_priority = _safe_text(
        rfi.get(
            "priority",
            "Medium",
        )
    )

    current_category = _safe_text(
        rfi.get(
            "category",
            "General",
        )
    )

    if current_status not in STATUS_OPTIONS:
        current_status = "Open"

    if current_priority not in PRIORITY_OPTIONS:
        current_priority = "Medium"

    if current_category not in CATEGORY_OPTIONS:
        current_category = "General"

    with st.form(
        f"edit_rfi_{rfi.get('id')}",
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_label = st.selectbox(
                "Project",
                project_labels,
                index=current_project_index,
            )

            subject = st.text_input(
                "Subject",
                value=_safe_text(
                    rfi.get("subject")
                ),
            )

            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
                index=CATEGORY_OPTIONS.index(
                    current_category
                ),
            )

        with col2:

            priority = st.selectbox(
                "Priority",
                PRIORITY_OPTIONS,
                index=PRIORITY_OPTIONS.index(
                    current_priority
                ),
            )

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(
                    current_status
                ),
            )

            requested_by = st.text_input(
                "Requested By",
                value=_safe_text(
                    rfi.get("requested_by")
                ),
            )

        question = st.text_area(
            "Question / Request",
            value=_safe_text(
                rfi.get("question")
            ),
            height=130,
        )

        response = st.text_area(
            "Response",
            value=_safe_text(
                rfi.get("response")
            ),
            height=110,
        )

        assigned_to = st.text_input(
            "Assigned To",
            value=_safe_text(
                rfi.get("assigned_to")
            ),
        )

        due_date = st.text_input(
            "Required By",
            value=_safe_text(
                rfi.get("due_date")
            ),
            placeholder="YYYY-MM-DD",
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

        if submitted:

            if not subject.strip():

                st.error(
                    "RFI subject is required."
                )

                return

            if not question.strip():

                st.error(
                    "RFI question is required."
                )

                return

            project_id = project_options[
                project_label
            ]

            updates = {
                "project_id": project_id,
                "subject": subject.strip(),
                "category": category,
                "priority": priority,
                "status": status,
                "question": question.strip(),
                "response": response.strip(),
                "requested_by": requested_by.strip(),
                "assigned_to": assigned_to.strip(),
                "due_date": due_date.strip(),
                "updated_at": _now(),
            }

            try:

                updated = update_record(
                    RFI_COLLECTION,
                    rfi.get("id"),
                    updates,
                    db,
                )

                if updated is None:

                    st.error(
                        "RFI could not be found."
                    )

                else:

                    st.success(
                        "RFI updated successfully."
                    )

                    st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to update the RFI."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ============================================================
# DELETE
# ============================================================

def _delete_rfi(
    rfi: dict[str, Any],
    db: dict[str, Any],
) -> None:

    rfi_id = rfi.get(
        "id"
    )

    rfi_number = _safe_text(
        rfi.get(
            "rfi_number",
            "RFI",
        )
    )

    confirm_key = (
        f"confirm_delete_rfi_{rfi_id}"
    )

    if st.session_state.get(
        confirm_key,
        False,
    ):

        st.warning(
            f"Delete {rfi_number}? This action cannot be undone."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Confirm Delete",
                key=f"confirm_delete_button_{rfi_id}",
                use_container_width=True,
            ):

                try:

                    deleted = delete_record(
                        RFI_COLLECTION,
                        rfi_id,
                        db,
                    )

                    st.session_state[
                        confirm_key
                    ] = False

                    if deleted:

                        st.success(
                            f"{rfi_number} deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "RFI could not be found."
                        )

                except Exception as exc:

                    st.error(
                        "Unable to delete the RFI."
                    )

                    st.code(
                        f"{type(exc).__name__}: {exc}"
                    )

        with col2:

            if st.button(
                "Cancel",
                key=f"cancel_delete_button_{rfi_id}",
                use_container_width=True,
            ):

                st.session_state[
                    confirm_key
                ] = False

                st.rerun()

    else:

        if st.button(
            "Delete",
            key=f"delete_rfi_{rfi_id}",
            use_container_width=True,
        ):

            st.session_state[
                confirm_key
            ] = True

            st.rerun()


# ============================================================
# LIST
# ============================================================

def _render_rfi_list(
    db: dict[str, Any],
) -> None:

    rfis = get_records(
        RFI_COLLECTION,
        db,
    )

    projects = _get_projects(
        db
    )

    project_map = _get_project_map(
        db
    )

    if not rfis:

        st.markdown(
            """
            <div class="rfi-empty">
                No RFIs have been created yet.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    st.markdown(
        "### RFI Register"
    )

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        search = st.text_input(
            "Search",
            placeholder="RFI number, subject, question...",
        )

    with col2:

        status_filter = st.selectbox(
            "Status",
            ["All"] + STATUS_OPTIONS,
        )

    with col3:

        priority_filter = st.selectbox(
            "Priority",
            ["All"] + PRIORITY_OPTIONS,
        )

    with col4:

        project_filter_options = {
            "All Projects": None
        }

        for project in projects:

            project_filter_options[
                _project_name(project)
            ] = project.get("id")

        selected_project = st.selectbox(
            "Project",
            list(
                project_filter_options.keys()
            ),
        )

    filtered = []

    search_text = (
        search or ""
    ).strip().lower()

    selected_project_id = (
        project_filter_options[
            selected_project
        ]
    )

    for rfi in rfis:

        if not isinstance(
            rfi,
            dict,
        ):
            continue

        # Search
        if search_text:

            searchable = " ".join(
                [
                    _safe_text(
                        rfi.get("rfi_number")
                    ),
                    _safe_text(
                        rfi.get("subject")
                    ),
                    _safe_text(
                        rfi.get("question")
                    ),
                    _safe_text(
                        rfi.get("response")
                    ),
                    _safe_text(
                        rfi.get("requested_by")
                    ),
                    _safe_text(
                        rfi.get("assigned_to")
                    ),
                ]
            ).lower()

            if search_text not in searchable:

                continue

        # Status
        if (
            status_filter != "All"
            and _safe_text(
                rfi.get("status")
            ) != status_filter
        ):

            continue

        # Priority
        if (
            priority_filter != "All"
            and _safe_text(
                rfi.get("priority")
            ) != priority_filter
        ):

            continue

        # Project
        if (
            selected_project_id is not None
            and str(
                rfi.get("project_id")
            )
            != str(
                selected_project_id
            )
        ):

            continue

        filtered.append(
            rfi
        )

    st.caption(
        f"{len(filtered)} of {len(rfis)} RFI(s)"
    )

    if not filtered:

        st.info(
            "No RFIs match the selected filters."
        )

        return

    # --------------------------------------------------------
    # Records
    # --------------------------------------------------------

    for rfi in filtered:

        rfi_id = rfi.get(
            "id"
        )

        rfi_number = _safe_text(
            rfi.get(
                "rfi_number",
                f"RFI-{rfi_id}",
            )
        )

        subject = _safe_text(
            rfi.get(
                "subject",
                "Untitled RFI",
            )
        )

        status = _safe_text(
            rfi.get(
                "status",
                "Open",
            )
        )

        priority = _safe_text(
            rfi.get(
                "priority",
                "Medium",
            )
        )

        project = project_map.get(
            str(
                rfi.get(
                    "project_id"
                )
            )
        )

        project_name = (
            _project_name(project)
            if project
            else "Unlinked Project"
        )

        question = _safe_text(
            rfi.get(
                "question"
            )
        )

        st.markdown(
            f"""
            <div class="rfi-card">

                <div class="rfi-number">
                    {rfi_number}
                </div>

                <div class="rfi-title">
                    {subject}
                </div>

                <div style="margin-top:8px;">

                    <span class="rfi-badge {_status_class(status)}">
                        {status}
                    </span>

                    <span class="rfi-badge {_priority_class(priority)}">
                        {priority}
                    </span>

                </div>

                <div class="rfi-meta">
                    Project: {project_name}
                </div>

                <div class="rfi-description">
                    {question[:280]}
                    {"..." if len(question) > 280 else ""}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(
            [1, 1, 1]
        )

        with col1:

            if st.button(
                "View",
                key=f"view_rfi_{rfi_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_rfi_id"
                ] = rfi_id

                st.session_state[
                    "rfi_mode"
                ] = "view"

                st.rerun()

        with col2:

            if st.button(
                "Edit",
                key=f"edit_rfi_button_{rfi_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_rfi_id"
                ] = rfi_id

                st.session_state[
                    "rfi_mode"
                ] = "edit"

                st.rerun()

        with col3:

            _delete_rfi(
                rfi,
                db,
            )


# ============================================================
# MAIN MODULE
# ============================================================

def render_rfis_module(
    db: dict[str, Any],
) -> None:

    """
    Main entry point used by streamlit_app.py.
    """

    _render_css()

    st.markdown(
        '<div class="cs-page-title">RFIs</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Requests for Information and project clarification."
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    rfis = get_records(
        RFI_COLLECTION,
        db,
    )

    total = len(rfis)

    open_count = sum(
        1
        for rfi in rfis
        if _safe_text(
            rfi.get("status")
        )
        == "Open"
    )

    review_count = sum(
        1
        for rfi in rfis
        if _safe_text(
            rfi.get("status")
        )
        == "Under Review"
    )

    closed_count = sum(
        1
        for rfi in rfis
        if _safe_text(
            rfi.get("status")
        )
        == "Closed"
    )

    cols = st.columns(4)

    metrics = [
        ("Total RFIs", total),
        ("Open", open_count),
        ("Under Review", review_count),
        ("Closed", closed_count),
    ]

    for col, (
        label,
        value,
    ) in zip(
        cols,
        metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {label}
                    </div>

                    <div class="cs-kpi-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # --------------------------------------------------------
    # Selected RFI
    # --------------------------------------------------------

    selected_id = st.session_state.get(
        "selected_rfi_id"
    )

    mode = st.session_state.get(
        "rfi_mode"
    )

    if selected_id is not None:

        selected_rfi = None

        for rfi in rfis:

            if str(
                rfi.get("id")
            ) == str(
                selected_id
            ):

                selected_rfi = rfi
                break

        if selected_rfi is not None:

            if st.button(
                "← Back to RFI Register",
                key="back_to_rfi_register",
            ):

                st.session_state.pop(
                    "selected_rfi_id",
                    None,
                )

                st.session_state.pop(
                    "rfi_mode",
                    None,
                )

                st.rerun()

            if mode == "edit":

                st.markdown(
                    "### Edit RFI"
                )

                _edit_rfi(
                    selected_rfi,
                    db,
                )

            else:

                _view_rfi(
                    selected_rfi,
                    db,
                )

            return

        st.session_state.pop(
            "selected_rfi_id",
            None,
        )

        st.session_state.pop(
            "rfi_mode",
            None,
        )

    # --------------------------------------------------------
    # Main tabs
    # --------------------------------------------------------

    tab_register, tab_create = st.tabs(
        [
            "RFI Register",
            "New RFI",
        ]
    )

    with tab_register:

        _render_rfi_list(
            db
        )

    with tab_create:

        _create_rfi(
            db
        )