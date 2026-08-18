"""
Creative Studios
AEC Collaboration Platform

Tasks Module
------------
AEC task management workspace.

Features:
    - Create tasks
    - Search tasks
    - Filter tasks
    - Project linking
    - RFI linking
    - Document references
    - Drawing references
    - Status tracking
    - Priority tracking
    - Due dates
    - Assignment
    - View
    - Edit
    - Delete
    - JSON persistence through modules.database
"""

from __future__ import annotations

from datetime import date, datetime
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

TASK_COLLECTION = "tasks"

STATUS_OPTIONS = [
    "Not Started",
    "In Progress",
    "Blocked",
    "Completed",
    "Cancelled",
]

PRIORITY_OPTIONS = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

CATEGORY_OPTIONS = [
    "General",
    "Design",
    "Architecture",
    "Structural",
    "Civil",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Procurement",
    "Site",
    "Documentation",
    "Quality",
    "Safety",
]


# ============================================================
# CSS
# ============================================================

def _render_css() -> None:

    st.markdown(
        """
        <style>

        .task-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 12px;
        }

        .task-number {
            color: #60A5FA;
            font-size: 10px;
            font-weight: 850;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }

        .task-title {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 850;
        }

        .task-description {
            color: #94A3B8;
            font-size: 12px;
            line-height: 1.55;
            margin-top: 8px;
        }

        .task-meta {
            color: #64748B;
            font-size: 11px;
            margin-top: 9px;
        }

        .task-badge {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 800;
            margin-right: 5px;
        }

        .task-status-not-started {
            background: rgba(100,116,139,0.15);
            color: #CBD5E1;
        }

        .task-status-progress {
            background: rgba(37,99,235,0.15);
            color: #60A5FA;
        }

        .task-status-blocked {
            background: rgba(239,68,68,0.15);
            color: #FCA5A5;
        }

        .task-status-completed {
            background: rgba(16,185,129,0.15);
            color: #6EE7B7;
        }

        .task-status-cancelled {
            background: rgba(71,85,105,0.15);
            color: #94A3B8;
        }

        .task-priority-low {
            background: rgba(100,116,139,0.15);
            color: #CBD5E1;
        }

        .task-priority-medium {
            background: rgba(37,99,235,0.15);
            color: #93C5FD;
        }

        .task-priority-high {
            background: rgba(245,158,11,0.15);
            color: #FBBF24;
        }

        .task-priority-critical {
            background: rgba(220,38,38,0.15);
            color: #FCA5A5;
        }

        .task-overdue {
            color: #FCA5A5;
            font-weight: 800;
        }

        .task-due {
            color: #FBBF24;
            font-weight: 700;
        }

        .task-detail-label {
            color: #64748B;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .task-detail-value {
            color: #E2E8F0;
            font-size: 13px;
            margin-top: 4px;
            margin-bottom: 14px;
        }

        .task-empty {
            background: #0B0F17;
            border: 1px dashed #243047;
            border-radius: 15px;
            padding: 35px;
            text-align: center;
            color: #64748B;
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


def _document_name(
    document: dict[str, Any],
) -> str:

    return (
        _safe_text(
            document.get("title")
        )
        or _safe_text(
            document.get("name")
        )
        or _safe_text(
            document.get("document_number")
        )
        or f"Document #{document.get('id', '')}"
    )


def _drawing_name(
    drawing: dict[str, Any],
) -> str:

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
        or f"Drawing #{drawing.get('id', '')}"
    )


def _rfi_name(
    rfi: dict[str, Any],
) -> str:

    return (
        _safe_text(
            rfi.get("rfi_number")
        )
        or _safe_text(
            rfi.get("subject")
        )
        or f"RFI #{rfi.get('id', '')}"
    )


def _get_collection(
    db: dict[str, Any],
    collection: str,
) -> list[dict[str, Any]]:

    try:

        records = get_records(
            collection,
            db,
        )

        return [
            record
            for record in records
            if isinstance(record, dict)
        ]

    except Exception:

        return []


def _get_projects(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _get_collection(
        db,
        "projects",
    )


def _get_rfis(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _get_collection(
        db,
        "rfis",
    )


def _get_documents(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _get_collection(
        db,
        "documents",
    )


def _get_drawings(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _get_collection(
        db,
        "drawings",
    )


def _project_map(
    db: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(project.get("id")): project
        for project in _get_projects(db)
        if project.get("id") is not None
    }


def _rfi_map(
    db: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(rfi.get("id")): rfi
        for rfi in _get_rfis(db)
        if rfi.get("id") is not None
    }


def _document_map(
    db: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(document.get("id")): document
        for document in _get_documents(db)
        if document.get("id") is not None
    }


def _drawing_map(
    db: dict[str, Any],
) -> dict[str, dict[str, Any]]:

    return {
        str(drawing.get("id")): drawing
        for drawing in _get_drawings(db)
        if drawing.get("id") is not None
    }


# ============================================================
# TASK NUMBER
# ============================================================

def _next_task_number(
    tasks: list[dict[str, Any]],
) -> str:

    highest = 0

    for task in tasks:

        number = _safe_text(
            task.get("task_number")
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

    return f"TASK-{highest + 1:04d}"


# ============================================================
# BADGES
# ============================================================

def _status_class(
    status: str,
) -> str:

    value = status.lower()

    if value == "in progress":
        return "task-status-progress"

    if value == "blocked":
        return "task-status-blocked"

    if value == "completed":
        return "task-status-completed"

    if value == "cancelled":
        return "task-status-cancelled"

    return "task-status-not-started"


def _priority_class(
    priority: str,
) -> str:

    value = priority.lower()

    if value == "critical":
        return "task-priority-critical"

    if value == "high":
        return "task-priority-high"

    if value == "medium":
        return "task-priority-medium"

    return "task-priority-low"


# ============================================================
# DUE DATE HELPERS
# ============================================================

def _parse_date(
    value: Any,
) -> date | None:

    text = _safe_text(value)

    if not text:
        return None

    try:

        return date.fromisoformat(
            text
        )

    except ValueError:

        return None


def _due_state(
    task: dict[str, Any],
) -> str:

    due = _parse_date(
        task.get("due_date")
    )

    if due is None:
        return ""

    if _safe_text(
        task.get("status")
    ) in [
        "Completed",
        "Cancelled",
    ]:

        return ""

    today = date.today()

    if due < today:
        return "overdue"

    if due == today:
        return "today"

    return "upcoming"


# ============================================================
# CREATE TASK
# ============================================================

def _create_task(
    db: dict[str, Any],
) -> None:

    st.markdown(
        "### New Task"
    )

    projects = _get_projects(
        db
    )

    if not projects:

        st.warning(
            "Create a project before creating a task."
        )

        return

    project_options = {
        _project_name(project): project.get("id")
        for project in projects
    }

    rfis = _get_rfis(
        db
    )

    documents = _get_documents(
        db
    )

    drawings = _get_drawings(
        db
    )

    with st.form(
        "create_task_form",
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

            title = st.text_input(
                "Task Title *",
                placeholder="Enter task title",
            )

            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
            )

            assigned_to = st.text_input(
                "Assigned To",
                placeholder="Person responsible",
            )

        with col2:

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
            )

            priority = st.selectbox(
                "Priority",
                PRIORITY_OPTIONS,
                index=1,
            )

            due_date = st.date_input(
                "Due Date",
                value=None,
            )

            created_by = st.text_input(
                "Created By",
                placeholder="Person creating task",
            )

        description = st.text_area(
            "Description",
            placeholder="Describe the task and expected outcome.",
            height=120,
        )

        st.markdown(
            "#### References"
        )

        rfi_options = {
            "No RFI": None
        }

        for rfi in rfis:

            rfi_options[
                _rfi_name(rfi)
            ] = rfi.get("id")

        rfi_label = st.selectbox(
            "Related RFI",
            list(
                rfi_options.keys()
            ),
        )

        document_options = {
            "No Document": None
        }

        for document in documents:

            document_options[
                _document_name(document)
            ] = document.get("id")

        document_label = st.selectbox(
            "Related Document",
            list(
                document_options.keys()
            ),
        )

        drawing_options = {
            "No Drawing": None
        }

        for drawing in drawings:

            drawing_options[
                _drawing_name(drawing)
            ] = drawing.get("id")

        drawing_label = st.selectbox(
            "Related Drawing",
            list(
                drawing_options.keys()
            ),
        )

        submitted = st.form_submit_button(
            "Create Task",
            use_container_width=True,
        )

        if submitted:

            if not title.strip():

                st.error(
                    "Task title is required."
                )

                return

            task_number = _next_task_number(
                get_records(
                    TASK_COLLECTION,
                    db,
                )
            )

            record = {
                "task_number": task_number,
                "project_id": project_options[
                    project_label
                ],
                "title": title.strip(),
                "description": description.strip(),
                "category": category,
                "status": status,
                "priority": priority,
                "assigned_to": assigned_to.strip(),
                "created_by": created_by.strip(),
                "due_date": (
                    due_date.isoformat()
                    if due_date
                    else ""
                ),
                "rfi_id": rfi_options[
                    rfi_label
                ],
                "document_id": document_options[
                    document_label
                ],
                "drawing_id": drawing_options[
                    drawing_label
                ],
                "created_at": _now(),
                "updated_at": _now(),
            }

            try:

                add_record(
                    TASK_COLLECTION,
                    record,
                    db,
                )

                st.success(
                    f"{task_number} created successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to create task."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ============================================================
# VIEW TASK
# ============================================================

def _view_task(
    task: dict[str, Any],
    db: dict[str, Any],
) -> None:

    project_map = _project_map(
        db
    )

    rfi_map = _rfi_map(
        db
    )

    document_map = _document_map(
        db
    )

    drawing_map = _drawing_map(
        db
    )

    project = project_map.get(
        str(
            task.get("project_id")
        )
    )

    rfi = rfi_map.get(
        str(
            task.get("rfi_id")
        )
    )

    document = document_map.get(
        str(
            task.get("document_id")
        )
    )

    drawing = drawing_map.get(
        str(
            task.get("drawing_id")
        )
    )

    status = _safe_text(
        task.get(
            "status",
            "Not Started",
        )
    )

    priority = _safe_text(
        task.get(
            "priority",
            "Medium",
        )
    )

    st.markdown(
        f"""
        <div class="task-card">

            <div class="task-number">
                {_safe_text(task.get("task_number"))}
            </div>

            <div class="task-title">
                {_safe_text(task.get("title"))}
            </div>

            <div style="margin-top:9px;">

                <span class="task-badge {_status_class(status)}">
                    {status}
                </span>

                <span class="task-badge {_priority_class(priority)}">
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
            '<div class="task-detail-label">Project</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_project_name(project) if project else 'Unlinked'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="task-detail-label">Assigned To</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_safe_text(task.get('assigned_to')) or 'Unassigned'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        due = _safe_text(
            task.get("due_date")
        )

        due_state = _due_state(
            task
        )

        if due_state == "overdue":

            due_html = (
                f'<span class="task-overdue">'
                f"{due} • OVERDUE"
                "</span>"
            )

        elif due_state == "today":

            due_html = (
                f'<span class="task-due">'
                f"{due} • DUE TODAY"
                "</span>"
            )

        else:

            due_html = (
                due
                or "Not specified"
            )

        st.markdown(
            '<div class="task-detail-label">Due Date</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{due_html}"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="task-detail-label">Description</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="task-detail-value">'
        f"{_safe_text(task.get('description')) or 'No description.'}"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "#### References"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            '<div class="task-detail-label">RFI</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_rfi_name(rfi) if rfi else 'None'}"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="task-detail-label">Document</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_document_name(document) if document else 'None'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="task-detail-label">Drawing</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_drawing_name(drawing) if drawing else 'None'}"
            "</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="task-detail-label">Category</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_safe_text(task.get('category')) or 'General'}"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "#### Record Information"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            '<div class="task-detail-label">Created By</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_safe_text(task.get('created_by')) or 'Unknown'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            '<div class="task-detail-label">Created</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_safe_text(task.get('created_at')) or 'Unknown'}"
            "</div>",
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            '<div class="task-detail-label">Updated</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="task-detail-value">'
            f"{_safe_text(task.get('updated_at')) or 'Unknown'}"
            "</div>",
            unsafe_allow_html=True,
        )


# ============================================================
# EDIT TASK
# ============================================================

def _edit_task(
    task: dict[str, Any],
    db: dict[str, Any],
) -> None:

    projects = _get_projects(
        db
    )

    rfis = _get_rfis(
        db
    )

    documents = _get_documents(
        db
    )

    drawings = _get_drawings(
        db
    )

    project_options = {
        _project_name(project): project.get("id")
        for project in projects
    }

    if not project_options:

        st.warning(
            "No projects are available."
        )

        return

    rfi_options = {
        "No RFI": None
    }

    for rfi in rfis:

        rfi_options[
            _rfi_name(rfi)
        ] = rfi.get("id")

    document_options = {
        "No Document": None
    }

    for document in documents:

        document_options[
            _document_name(document)
        ] = document.get("id")

    drawing_options = {
        "No Drawing": None
    }

    for drawing in drawings:

        drawing_options[
            _drawing_name(drawing)
        ] = drawing.get("id")

    current_project_id = str(
        task.get(
            "project_id",
            "",
        )
    )

    project_labels = list(
        project_options.keys()
    )

    project_index = 0

    for index, label in enumerate(
        project_labels
    ):

        if str(
            project_options[label]
        ) == current_project_id:

            project_index = index
            break

    current_status = _safe_text(
        task.get(
            "status",
            "Not Started",
        )
    )

    current_priority = _safe_text(
        task.get(
            "priority",
            "Medium",
        )
    )

    current_category = _safe_text(
        task.get(
            "category",
            "General",
        )
    )

    if current_status not in STATUS_OPTIONS:
        current_status = "Not Started"

    if current_priority not in PRIORITY_OPTIONS:
        current_priority = "Medium"

    if current_category not in CATEGORY_OPTIONS:
        current_category = "General"

    rfi_index = 0

    current_rfi_id = str(
        task.get(
            "rfi_id",
            "",
        )
    )

    for index, label in enumerate(
        rfi_options.keys()
    ):

        value = rfi_options[label]

        if value is not None and str(value) == current_rfi_id:

            rfi_index = index
            break

    document_index = 0

    current_document_id = str(
        task.get(
            "document_id",
            "",
        )
    )

    for index, label in enumerate(
        document_options.keys()
    ):

        value = document_options[label]

        if value is not None and str(value) == current_document_id:

            document_index = index
            break

    drawing_index = 0

    current_drawing_id = str(
        task.get(
            "drawing_id",
            "",
        )
    )

    for index, label in enumerate(
        drawing_options.keys()
    ):

        value = drawing_options[label]

        if value is not None and str(value) == current_drawing_id:

            drawing_index = index
            break

    with st.form(
        f"edit_task_form_{task.get('id')}",
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_label = st.selectbox(
                "Project",
                project_labels,
                index=project_index,
            )

            title = st.text_input(
                "Task Title",
                value=_safe_text(
                    task.get("title")
                ),
            )

            category = st.selectbox(
                "Category",
                CATEGORY_OPTIONS,
                index=CATEGORY_OPTIONS.index(
                    current_category
                ),
            )

            assigned_to = st.text_input(
                "Assigned To",
                value=_safe_text(
                    task.get("assigned_to")
                ),
            )

        with col2:

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(
                    current_status
                ),
            )

            priority = st.selectbox(
                "Priority",
                PRIORITY_OPTIONS,
                index=PRIORITY_OPTIONS.index(
                    current_priority
                ),
            )

            due_date = st.text_input(
                "Due Date",
                value=_safe_text(
                    task.get("due_date")
                ),
                placeholder="YYYY-MM-DD",
            )

            created_by = st.text_input(
                "Created By",
                value=_safe_text(
                    task.get("created_by")
                ),
            )

        description = st.text_area(
            "Description",
            value=_safe_text(
                task.get("description")
            ),
            height=120,
        )

        st.markdown(
            "#### References"
        )

        rfi_label = st.selectbox(
            "Related RFI",
            list(
                rfi_options.keys()
            ),
            index=rfi_index,
        )

        document_label = st.selectbox(
            "Related Document",
            list(
                document_options.keys()
            ),
            index=document_index,
        )

        drawing_label = st.selectbox(
            "Related Drawing",
            list(
                drawing_options.keys()
            ),
            index=drawing_index,
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

        if submitted:

            if not title.strip():

                st.error(
                    "Task title is required."
                )

                return

            parsed_due_date = ""

            if due_date.strip():

                parsed_due_date = (
                    _parse_date(
                        due_date
                    )
                )

                if parsed_due_date is None:

                    st.error(
                        "Due date must use YYYY-MM-DD format."
                    )

                    return

                parsed_due_date = (
                    parsed_due_date.isoformat()
                )

            updates = {
                "project_id": project_options[
                    project_label
                ],
                "title": title.strip(),
                "description": description.strip(),
                "category": category,
                "status": status,
                "priority": priority,
                "assigned_to": assigned_to.strip(),
                "created_by": created_by.strip(),
                "due_date": parsed_due_date,
                "rfi_id": rfi_options[
                    rfi_label
                ],
                "document_id": document_options[
                    document_label
                ],
                "drawing_id": drawing_options[
                    drawing_label
                ],
                "updated_at": _now(),
            }

            try:

                updated = update_record(
                    TASK_COLLECTION,
                    task.get("id"),
                    updates,
                    db,
                )

                if updated is None:

                    st.error(
                        "Task could not be found."
                    )

                    return

                st.success(
                    "Task updated successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    "Unable to update task."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )


# ============================================================
# DELETE
# ============================================================

def _delete_task(
    task: dict[str, Any],
    db: dict[str, Any],
) -> None:

    task_id = task.get(
        "id"
    )

    task_number = _safe_text(
        task.get(
            "task_number",
            "Task",
        )
    )

    confirm_key = (
        f"confirm_delete_task_{task_id}"
    )

    if st.session_state.get(
        confirm_key,
        False,
    ):

        st.warning(
            f"Delete {task_number}? This action cannot be undone."
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Confirm Delete",
                key=f"confirm_delete_task_button_{task_id}",
                use_container_width=True,
            ):

                try:

                    deleted = delete_record(
                        TASK_COLLECTION,
                        task_id,
                        db,
                    )

                    st.session_state[
                        confirm_key
                    ] = False

                    if deleted:

                        st.success(
                            f"{task_number} deleted."
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Task could not be found."
                        )

                except Exception as exc:

                    st.error(
                        "Unable to delete task."
                    )

                    st.code(
                        f"{type(exc).__name__}: {exc}"
                    )

        with col2:

            if st.button(
                "Cancel",
                key=f"cancel_delete_task_button_{task_id}",
                use_container_width=True,
            ):

                st.session_state[
                    confirm_key
                ] = False

                st.rerun()

    else:

        if st.button(
            "Delete",
            key=f"delete_task_{task_id}",
            use_container_width=True,
        ):

            st.session_state[
                confirm_key
            ] = True

            st.rerun()


# ============================================================
# TASK REGISTER
# ============================================================

def _render_task_register(
    db: dict[str, Any],
) -> None:

    tasks = _get_collection(
        db,
        TASK_COLLECTION,
    )

    projects = _get_projects(
        db
    )

    project_map = _project_map(
        db
    )

    if not tasks:

        st.markdown(
            """
            <div class="task-empty">
                No tasks have been created yet.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        search = st.text_input(
            "Search",
            placeholder="Task number, title, description...",
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

        project_options = {
            "All Projects": None
        }

        for project in projects:

            project_options[
                _project_name(project)
            ] = project.get("id")

        project_filter = st.selectbox(
            "Project",
            list(
                project_options.keys()
            ),
        )

    filtered = []

    search_text = (
        search or ""
    ).strip().lower()

    selected_project_id = project_options[
        project_filter
    ]

    for task in tasks:

        if not isinstance(
            task,
            dict,
        ):

            continue

        if search_text:

            searchable = " ".join(
                [
                    _safe_text(
                        task.get("task_number")
                    ),
                    _safe_text(
                        task.get("title")
                    ),
                    _safe_text(
                        task.get("description")
                    ),
                    _safe_text(
                        task.get("assigned_to")
                    ),
                    _safe_text(
                        task.get("created_by")
                    ),
                ]
            ).lower()

            if search_text not in searchable:

                continue

        if (
            status_filter != "All"
            and _safe_text(
                task.get("status")
            ) != status_filter
        ):

            continue

        if (
            priority_filter != "All"
            and _safe_text(
                task.get("priority")
            ) != priority_filter
        ):

            continue

        if (
            selected_project_id is not None
            and str(
                task.get("project_id")
            )
            != str(
                selected_project_id
            )
        ):

            continue

        filtered.append(
            task
        )

    st.caption(
        f"{len(filtered)} of {len(tasks)} task(s)"
    )

    if not filtered:

        st.info(
            "No tasks match the selected filters."
        )

        return

    for task in filtered:

        task_id = task.get(
            "id"
        )

        task_number = _safe_text(
            task.get(
                "task_number",
                f"TASK-{task_id}",
            )
        )

        title = _safe_text(
            task.get(
                "title",
                "Untitled Task",
            )
        )

        description = _safe_text(
            task.get(
                "description"
            )
        )

        status = _safe_text(
            task.get(
                "status",
                "Not Started",
            )
        )

        priority = _safe_text(
            task.get(
                "priority",
                "Medium",
            )
        )

        project = project_map.get(
            str(
                task.get(
                    "project_id"
                )
            )
        )

        project_name = (
            _project_name(project)
            if project
            else "Unlinked Project"
        )

        due_date = _safe_text(
            task.get(
                "due_date"
            )
        )

        due_state = _due_state(
            task
        )

        if due_state == "overdue":

            due_html = (
                f'<span class="task-overdue">'
                f"Due: {due_date} • OVERDUE"
                "</span>"
            )

        elif due_state == "today":

            due_html = (
                f'<span class="task-due">'
                f"Due: {due_date} • TODAY"
                "</span>"
            )

        else:

            due_html = (
                f"Due: {due_date}"
                if due_date
                else "No due date"
            )

        st.markdown(
            f"""
            <div class="task-card">

                <div class="task-number">
                    {task_number}
                </div>

                <div class="task-title">
                    {title}
                </div>

                <div style="margin-top:8px;">

                    <span class="task-badge {_status_class(status)}">
                        {status}
                    </span>

                    <span class="task-badge {_priority_class(priority)}">
                        {priority}
                    </span>

                </div>

                <div class="task-meta">
                    Project: {project_name}
                    &nbsp; • &nbsp;
                    {due_html}
                </div>

                <div class="task-description">
                    {description[:260]}
                    {"..." if len(description) > 260 else ""}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            if st.button(
                "View",
                key=f"view_task_{task_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_task_id"
                ] = task_id

                st.session_state[
                    "task_mode"
                ] = "view"

                st.rerun()

        with col2:

            if st.button(
                "Edit",
                key=f"edit_task_{task_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "selected_task_id"
                ] = task_id

                st.session_state[
                    "task_mode"
                ] = "edit"

                st.rerun()

        with col3:

            _delete_task(
                task,
                db,
            )


# ============================================================
# MAIN MODULE
# ============================================================

def render_tasks_module(
    db: dict[str, Any],
) -> None:

    """
    Main entry point for streamlit_app.py.
    """

    _render_css()

    st.markdown(
        '<div class="cs-page-title">Tasks</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Manage project activities, assignments, deadlines "
        "and linked AEC records."
        "</div>",
        unsafe_allow_html=True,
    )

    tasks = _get_collection(
        db,
        TASK_COLLECTION,
    )

    total = len(tasks)

    not_started = sum(
        1
        for task in tasks
        if _safe_text(
            task.get("status")
        )
        == "Not Started"
    )

    in_progress = sum(
        1
        for task in tasks
        if _safe_text(
            task.get("status")
        )
        == "In Progress"
    )

    completed = sum(
        1
        for task in tasks
        if _safe_text(
            task.get("status")
        )
        == "Completed"
    )

    overdue = sum(
        1
        for task in tasks
        if _due_state(task)
        == "overdue"
    )

    cols = st.columns(4)

    metrics = [
        ("Total Tasks", total),
        ("In Progress", in_progress),
        ("Completed", completed),
        ("Overdue", overdue),
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

    # ========================================================
    # SELECTED TASK
    # ========================================================

    selected_id = st.session_state.get(
        "selected_task_id"
    )

    mode = st.session_state.get(
        "task_mode"
    )

    if selected_id is not None:

        selected_task = None

        for task in tasks:

            if str(
                task.get("id")
            ) == str(
                selected_id
            ):

                selected_task = task

                break

        if selected_task is not None:

            if st.button(
                "← Back to Task Register",
                key="back_to_task_register",
            ):

                st.session_state.pop(
                    "selected_task_id",
                    None,
                )

                st.session_state.pop(
                    "task_mode",
                    None,
                )

                st.rerun()

            if mode == "edit":

                st.markdown(
                    "### Edit Task"
                )

                _edit_task(
                    selected_task,
                    db,
                )

            else:

                _view_task(
                    selected_task,
                    db,
                )

            return

        st.session_state.pop(
            "selected_task_id",
            None,
        )

        st.session_state.pop(
            "task_mode",
            None,
        )

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_create = st.tabs(
        [
            "Task Register",
            "New Task",
        ]
    )

    with tab_register:

        _render_task_register(
            db
        )

    with tab_create:

        _create_task(
            db
        )