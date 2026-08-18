"""
Creative Studios
AEC Collaboration Platform

Documents Module
----------------
Document Directory and document metadata management.

Features:
    - Document directory
    - Search
    - Project filtering
    - Document type filtering
    - Status filtering
    - Create document
    - Edit document
    - Delete document
    - Project linking
    - Validation
    - Error handling

Database contract:
    add_record()
    get_records()
    get_record()
    update_record()
    delete_record()
    next_id()
"""

from modules.branding import render_module_header

from __future__ import annotations

from datetime import date
from html import escape
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

DOCUMENT_COLLECTION = "documents"
PROJECT_COLLECTION = "projects"

DOCUMENT_TYPES = [
    "Contract",
    "Specification",
    "Drawing",
    "Report",
    "Correspondence",
    "Permit",
    "Certificate",
    "Meeting Minutes",
    "Other",
]

DOCUMENT_STATUSES = [
    "Draft",
    "Active",
    "Under Review",
    "Approved",
    "Archived",
]


# ============================================================
# CSS
# ============================================================

def _render_css() -> None:
    """Render module-specific styling."""

    st.markdown(
        """
        <style>

        .documents-header {
            margin-bottom: 22px;
        }

        .documents-title {
            color: #FFFFFF;
            font-size: 30px;
            font-weight: 900;
            letter-spacing: -0.7px;
        }

        .documents-subtitle {
            color: #64748B;
            font-size: 13px;
            margin-top: 5px;
        }

        .document-card {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 15px;
            padding: 18px;
            margin-bottom: 10px;
        }

        .document-number {
            color: #60A5FA;
            font-size: 11px;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .document-title {
            color: #FFFFFF;
            font-size: 17px;
            font-weight: 850;
            margin-top: 5px;
        }

        .document-meta {
            color: #64748B;
            font-size: 11px;
            margin-top: 7px;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 9px;
            border-radius: 999px;
            font-size: 9px;
            font-weight: 850;
            margin-top: 9px;
            border: 1px solid #1E293B;
            background: #111827;
            color: #CBD5E1;
        }

        .status-draft {
            color: #CBD5E1;
        }

        .status-active {
            color: #60A5FA;
        }

        .status-review {
            color: #FBBF24;
        }

        .status-approved {
            color: #4ADE80;
        }

        .status-archived {
            color: #94A3B8;
        }

        .documents-empty {
            background: #0B0F17;
            border: 1px dashed #1E293B;
            border-radius: 15px;
            padding: 35px;
            text-align: center;
            color: #64748B;
        }

        .document-stat {
            background: #0B0F17;
            border: 1px solid #172033;
            border-radius: 14px;
            padding: 15px;
            min-height: 90px;
        }

        .document-stat-label {
            color: #64748B;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
        }

        .document-stat-value {
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 900;
            margin-top: 6px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def _safe_string(
    value: Any,
    default: str = "",
) -> str:
    """Return a safe string."""

    if value is None:
        return default

    return str(value).strip()


def _project_name(
    project_id: Any,
    projects: list[dict[str, Any]],
) -> str:
    """Resolve project ID to project name."""

    if project_id in (
        None,
        "",
    ):
        return "Unassigned"

    for project in projects:

        if not isinstance(project, dict):
            continue

        if str(project.get("id")) == str(project_id):

            return _safe_string(
                project.get(
                    "name",
                    project.get(
                        "project_name",
                        f"Project {project_id}",
                    ),
                ),
                f"Project {project_id}",
            )

    return f"Project {project_id}"


def _status_class(status: str) -> str:
    """Return CSS class for document status."""

    normalized = status.lower()

    if normalized == "active":
        return "status-active"

    if normalized == "approved":
        return "status-approved"

    if normalized == "under review":
        return "status-review"

    if normalized == "archived":
        return "status-archived"

    return "status-draft"


def _document_number(
    document: dict[str, Any],
) -> str:
    """Return a readable document number."""

    return _safe_string(
        document.get(
            "document_number",
            document.get(
                "number",
                f"DOC-{document.get('id', ''):03}",
            ),
        ),
        "DOC",
    )


def _validate_document(
    document_number: str,
    title: str,
    document_type: str,
    status: str,
    revision: str,
    project_id: Any,
) -> list[str]:
    """Validate document input."""

    errors: list[str] = []

    if not document_number:
        errors.append(
            "Document number is required."
        )

    if not title:
        errors.append(
            "Document title is required."
        )

    if not document_type:
        errors.append(
            "Document type is required."
        )

    if document_type not in DOCUMENT_TYPES:
        errors.append(
            "Invalid document type."
        )

    if status not in DOCUMENT_STATUSES:
        errors.append(
            "Invalid document status."
        )

    if not revision:
        errors.append(
            "Revision is required."
        )

    if project_id in (
        None,
        "",
        "Unassigned",
    ):
        pass

    return errors


# ============================================================
# CREATE
# ============================================================

def _create_document(
    db: dict[str, Any],
    projects: list[dict[str, Any]],
) -> None:
    """Create a new document."""

    st.markdown(
        "### New Document"
    )

    project_options = [
        "Unassigned"
    ]

    project_lookup: dict[str, Any] = {}

    for project in projects:

        if not isinstance(project, dict):
            continue

        project_id = project.get("id")

        project_name = _safe_string(
            project.get(
                "name",
                project.get(
                    "project_name",
                    f"Project {project_id}",
                ),
            ),
            f"Project {project_id}",
        )

        display = (
            f"{project_name} "
            f"(#{project_id})"
        )

        project_options.append(
            display
        )

        project_lookup[display] = project_id

    with st.form(
        "create_document_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            document_number = st.text_input(
                "Document Number *",
                placeholder="DOC-001",
            )

            title = st.text_input(
                "Title *",
                placeholder="Project Contract",
            )

            document_type = st.selectbox(
                "Document Type *",
                DOCUMENT_TYPES,
            )

            status = st.selectbox(
                "Status *",
                DOCUMENT_STATUSES,
            )

        with col2:

            revision = st.text_input(
                "Revision *",
                value="Rev 0",
            )

            project_selection = st.selectbox(
                "Project",
                project_options,
            )

            document_date = st.date_input(
                "Document Date",
                value=date.today(),
            )

            author = st.text_input(
                "Author",
                placeholder="Creative Studios",
            )

        description = st.text_area(
            "Description",
            placeholder=(
                "Brief description of the document."
            ),
        )

        submitted = st.form_submit_button(
            "Create Document",
            use_container_width=True,
        )

        if not submitted:
            return

        document_number = document_number.strip()
        title = title.strip()
        revision = revision.strip()
        author = author.strip()
        description = description.strip()

        project_id = project_lookup.get(
            project_selection
        )

        errors = _validate_document(
            document_number,
            title,
            document_type,
            status,
            revision,
            project_id,
        )

        if errors:

            for error in errors:
                st.error(error)

            return

        existing = get_records(
            DOCUMENT_COLLECTION,
            db,
        )

        duplicate = any(
            _safe_string(
                item.get(
                    "document_number"
                )
            ).lower()
            == document_number.lower()
            for item in existing
        )

        if duplicate:

            st.error(
                "A document with this document number already exists."
            )

            return

        record = {
            "document_number": document_number,
            "title": title,
            "project_id": project_id,
            "document_type": document_type,
            "status": status,
            "revision": revision,
            "document_date": document_date.isoformat(),
            "author": author,
            "description": description,
        }

        try:

            add_record(
                DOCUMENT_COLLECTION,
                record,
                db,
            )

            st.success(
                "Document created successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                "Unable to create document."
            )

            st.exception(exc)


# ============================================================
# EDIT
# ============================================================

def _edit_document(
    db: dict[str, Any],
    projects: list[dict[str, Any]],
) -> None:
    """Edit an existing document."""

    documents = get_records(
        DOCUMENT_COLLECTION,
        db,
    )

    if not documents:

        st.info(
            "There are no documents to edit."
        )

        return

    options: dict[str, Any] = {}

    for document in documents:

        document_id = document.get("id")

        label = (
            f"{_document_number(document)}"
            f" • "
            f"{_safe_string(document.get('title'), 'Untitled')}"
        )

        options[label] = document_id

    selected_label = st.selectbox(
        "Select Document",
        list(options.keys()),
        key="document_edit_selector",
    )

    selected_id = options[selected_label]

    document = get_record(
        DOCUMENT_COLLECTION,
        selected_id,
        db,
    )

    if document is None:

        st.error(
            "Selected document could not be found."
        )

        return

    project_options = [
        "Unassigned"
    ]

    project_lookup: dict[str, Any] = {}

    selected_project_label = "Unassigned"

    for project in projects:

        if not isinstance(project, dict):
            continue

        project_id = project.get("id")

        project_name = _safe_string(
            project.get(
                "name",
                project.get(
                    "project_name",
                    f"Project {project_id}",
                ),
            ),
            f"Project {project_id}",
        )

        label = (
            f"{project_name} "
            f"(#{project_id})"
        )

        project_options.append(label)
        project_lookup[label] = project_id

        if str(project_id) == str(
            document.get("project_id")
        ):
            selected_project_label = label

    existing_date = document.get(
        "document_date"
    )

    try:

        parsed_date = (
            date.fromisoformat(
                str(existing_date)
            )
            if existing_date
            else date.today()
        )

    except ValueError:

        parsed_date = date.today()

    with st.form(
        f"edit_document_{selected_id}",
    ):

        col1, col2 = st.columns(2)

        with col1:

            document_number = st.text_input(
                "Document Number *",
                value=_document_number(
                    document
                ),
            )

            title = st.text_input(
                "Title *",
                value=_safe_string(
                    document.get("title")
                ),
            )

            current_type = _safe_string(
                document.get(
                    "document_type"
                )
            )

            document_type = st.selectbox(
                "Document Type *",
                DOCUMENT_TYPES,
                index=(
                    DOCUMENT_TYPES.index(
                        current_type
                    )
                    if current_type in DOCUMENT_TYPES
                    else 0
                ),
            )

            current_status = _safe_string(
                document.get("status")
            )

            status = st.selectbox(
                "Status *",
                DOCUMENT_STATUSES,
                index=(
                    DOCUMENT_STATUSES.index(
                        current_status
                    )
                    if current_status in DOCUMENT_STATUSES
                    else 0
                ),
            )

        with col2:

            revision = st.text_input(
                "Revision *",
                value=_safe_string(
                    document.get(
                        "revision",
                        "Rev 0",
                    )
                ),
            )

            project_selection = st.selectbox(
                "Project",
                project_options,
                index=(
                    project_options.index(
                        selected_project_label
                    )
                    if selected_project_label in project_options
                    else 0
                ),
            )

            document_date = st.date_input(
                "Document Date",
                value=parsed_date,
            )

            author = st.text_input(
                "Author",
                value=_safe_string(
                    document.get("author")
                ),
            )

        description = st.text_area(
            "Description",
            value=_safe_string(
                document.get("description")
            ),
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

        if not submitted:
            return

        document_number = document_number.strip()
        title = title.strip()
        revision = revision.strip()
        author = author.strip()
        description = description.strip()

        project_id = project_lookup.get(
            project_selection
        )

        errors = _validate_document(
            document_number,
            title,
            document_type,
            status,
            revision,
            project_id,
        )

        if errors:

            for error in errors:
                st.error(error)

            return

        duplicate = False

        for other in get_records(
            DOCUMENT_COLLECTION,
            db,
        ):

            if str(
                other.get("id")
            ) == str(selected_id):
                continue

            if (
                _safe_string(
                    other.get(
                        "document_number"
                    )
                ).lower()
                == document_number.lower()
            ):

                duplicate = True
                break

        if duplicate:

            st.error(
                "Another document already uses this document number."
            )

            return

        updates = {
            "document_number": document_number,
            "title": title,
            "project_id": project_id,
            "document_type": document_type,
            "status": status,
            "revision": revision,
            "document_date": document_date.isoformat(),
            "author": author,
            "description": description,
        }

        try:

            updated = update_record(
                DOCUMENT_COLLECTION,
                selected_id,
                updates,
                db,
            )

            if updated is None:

                st.error(
                    "Document could not be found."
                )

                return

            st.success(
                "Document updated successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                "Unable to update document."
            )

            st.exception(exc)


# ============================================================
# DELETE
# ============================================================

def _delete_document(
    db: dict[str, Any],
) -> None:
    """Delete a document."""

    documents = get_records(
        DOCUMENT_COLLECTION,
        db,
    )

    if not documents:

        st.info(
            "There are no documents to delete."
        )

        return

    options: dict[str, Any] = {}

    for document in documents:

        label = (
            f"{_document_number(document)}"
            f" • "
            f"{_safe_string(document.get('title'), 'Untitled')}"
        )

        options[label] = document.get("id")

    selected_label = st.selectbox(
        "Select Document",
        list(options.keys()),
        key="document_delete_selector",
    )

    selected_id = options[
        selected_label
    ]

    confirm = st.checkbox(
        "I understand that this document will be permanently deleted.",
        key="confirm_document_delete",
    )

    if st.button(
        "Delete Document",
        type="primary",
        use_container_width=True,
        disabled=not confirm,
    ):

        try:

            deleted = delete_record(
                DOCUMENT_COLLECTION,
                selected_id,
                db,
            )

            if deleted:

                st.success(
                    "Document deleted successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Document could not be found."
                )

        except Exception as exc:

            st.error(
                "Unable to delete document."
            )

            st.exception(exc)


# ============================================================
# DIRECTORY
# ============================================================

def _render_directory(
    db: dict[str, Any],
    projects: list[dict[str, Any]],
) -> None:
    """Render searchable document directory."""

    documents = get_records(
        DOCUMENT_COLLECTION,
        db,
    )

    if not documents:

        st.markdown(
            """
            <div class="documents-empty">
                <div style="
                    color:#FFFFFF;
                    font-size:17px;
                    font-weight:800;
                    margin-bottom:6px;
                ">
                    No Documents Yet
                </div>

                Create your first document using
                <strong>New Document</strong>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    project_names = [
        "All Projects"
    ]

    for project in projects:

        if not isinstance(project, dict):
            continue

        project_name = _safe_string(
            project.get(
                "name",
                project.get(
                    "project_name",
                    f"Project {project.get('id')}",
                ),
            )
        )

        if project_name:
            project_names.append(
                project_name
            )

    col1, col2, col3 = st.columns(3)

    with col1:

        search = st.text_input(
            "Search",
            placeholder=(
                "Search number, title, author..."
            ),
            key="documents_search",
        ).strip().lower()

    with col2:

        project_filter = st.selectbox(
            "Project",
            project_names,
            key="documents_project_filter",
        )

    with col3:

        status_filter = st.selectbox(
            "Status",
            ["All Statuses"] + DOCUMENT_STATUSES,
            key="documents_status_filter",
        )

    type_filter = st.selectbox(
        "Document Type",
        ["All Types"] + DOCUMENT_TYPES,
        key="documents_type_filter",
    )

    filtered: list[dict[str, Any]] = []

    for document in documents:

        if not isinstance(document, dict):
            continue

        searchable = " ".join(
            [
                _safe_string(
                    document.get(
                        "document_number"
                    )
                ),
                _safe_string(
                    document.get(
                        "title"
                    )
                ),
                _safe_string(
                    document.get(
                        "author"
                    )
                ),
                _safe_string(
                    document.get(
                        "description"
                    )
                ),
            ]
        ).lower()

        if search and search not in searchable:
            continue

        project_name = _project_name(
            document.get(
                "project_id"
            ),
            projects,
        )

        if (
            project_filter != "All Projects"
            and project_name != project_filter
        ):
            continue

        status = _safe_string(
            document.get(
                "status"
            )
        )

        if (
            status_filter != "All Statuses"
            and status != status_filter
        ):
            continue

        document_type = _safe_string(
            document.get(
                "document_type"
            )
        )

        if (
            type_filter != "All Types"
            and document_type != type_filter
        ):
            continue

        filtered.append(
            document
        )

    st.caption(
        f"{len(filtered)} document(s)"
    )

    if not filtered:

        st.markdown(
            """
            <div class="documents-empty">
                No documents match the current filters.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    filtered.sort(
        key=lambda item: (
            _safe_string(
                item.get(
                    "document_number"
                )
            ).lower()
        )
    )

    for document in filtered:

        number = escape(
            _document_number(
                document
            )
        )

        title = escape(
            _safe_string(
                document.get(
                    "title",
                    "Untitled Document",
                )
            )
        )

        status = _safe_string(
            document.get(
                "status",
                "Draft",
            )
        )

        revision = escape(
            _safe_string(
                document.get(
                    "revision",
                    "Rev 0",
                )
            )
        )

        document_type = escape(
            _safe_string(
                document.get(
                    "document_type",
                    "Other",
                )
            )
        )

        project = escape(
            _project_name(
                document.get(
                    "project_id"
                ),
                projects,
            )
        )

        author = escape(
            _safe_string(
                document.get(
                    "author"
                ),
                "Not specified",
            )
        )

        date_value = escape(
            _safe_string(
                document.get(
                    "document_date"
                ),
                "Not specified",
            )
        )

        status_class = _status_class(
            status
        )

        st.markdown(
            f"""
            <div class="document-card">

                <div class="document-number">
                    {number}
                </div>

                <div class="document-title">
                    {title}
                </div>

                <div class="document-meta">
                    Project: {project}
                    &nbsp; • &nbsp;
                    Type: {document_type}
                    &nbsp; • &nbsp;
                    {revision}
                </div>

                <div class="document-meta">
                    Author: {author}
                    &nbsp; • &nbsp;
                    Date: {date_value}
                </div>

                <span class="
                    status-badge
                    {status_class}
                ">
                    {escape(status)}
                </span>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MAIN MODULE
# ============================================================

def render_documents_module(
    db: dict[str, Any],
) -> None:
    """
    Main Documents module entry point.

    This function is intentionally compatible with:

        render_documents_module(db)
    """

    if not isinstance(db, dict):

        st.error(
            "Documents module received an invalid database."
        )

        return

    _render_css()

    projects = get_records(
        PROJECT_COLLECTION,
        db,
    )

    documents = get_records(
        DOCUMENT_COLLECTION,
        db,
    )

    st.markdown(
        """
        <div class="documents-header">

            <div class="documents-title">
                Documents
            </div>

            <div class="documents-subtitle">
                Central document register for Creative Studios
                AEC projects.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # STATISTICS
    # ========================================================

    total = len(documents)

    active = sum(
        1
        for document in documents
        if _safe_string(
            document.get("status")
        ).lower()
        == "active"
    )

    review = sum(
        1
        for document in documents
        if _safe_string(
            document.get("status")
        ).lower()
        == "under review"
    )

    approved = sum(
        1
        for document in documents
        if _safe_string(
            document.get("status")
        ).lower()
        == "approved"
    )

    stat_cols = st.columns(4)

    statistics = [
        ("Total Documents", total),
        ("Active", active),
        ("Under Review", review),
        ("Approved", approved),
    ]

    for col, (
        label,
        value,
    ) in zip(
        stat_cols,
        statistics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="document-stat">

                    <div class="document-stat-label">
                        {label}
                    </div>

                    <div class="document-stat-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # ========================================================
    # ACTION TABS
    # ========================================================

    tabs = st.tabs(
        [
            "Document Directory",
            "New Document",
            "Edit Document",
            "Delete Document",
        ]
    )

    with tabs[0]:

        _render_directory(
            db,
            projects,
        )

    with tabs[1]:

        _create_document(
            db,
            projects,
        )

    with tabs[2]:

        _edit_document(
            db,
            projects,
        )

    with tabs[3]:

        _delete_document(
            db
        )