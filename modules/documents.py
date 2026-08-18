"""
Creative Studios
AEC Collaboration Platform

Documents Module
JSON-backed CRUD implementation.

This module does not modify authentication,
login, sidebar, or navigation behavior.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    load_memory,
    next_id,
    save_memory,
    update_record,
)


DOCUMENT_COLLECTION = "documents"

DOCUMENT_TYPES = [
    "Contract",
    "Drawing",
    "Specification",
    "Report",
    "Proposal",
    "BOQ",
    "Invoice",
    "Certificate",
    "Meeting Minutes",
    "Other",
]

DOCUMENT_STATUSES = [
    "Draft",
    "Under Review",
    "Approved",
    "Issued",
    "Archived",
]


# ============================================================
# CSS
# ============================================================

def _inject_css() -> None:
    st.markdown(
        """
<style>

.cs-doc-header {
    margin-bottom: 24px;
}

.cs-doc-title {
    color: #F8FAFC;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.7px;
}

.cs-doc-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
}

.cs-doc-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 19px;
    margin-top: 14px;
}

.cs-doc-card:hover {
    border-color: #2563EB;
}

.cs-doc-name {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 850;
}

.cs-doc-meta {
    color: #64748B;
    font-size: 11px;
    margin-top: 5px;
}

.cs-doc-info {
    color: #CBD5E1;
    font-size: 12px;
    margin-top: 5px;
}

.cs-doc-status {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 850;
}

.cs-doc-draft {
    color: #CBD5E1;
    background: rgba(71,85,105,0.18);
    border: 1px solid #334155;
}

.cs-doc-review {
    color: #93C5FD;
    background: rgba(30,64,175,0.15);
    border: 1px solid rgba(30,64,175,0.35);
}

.cs-doc-approved {
    color: #BFDBFE;
    background: rgba(37,99,235,0.15);
    border: 1px solid rgba(37,99,235,0.35);
}

.cs-doc-issued {
    color: #60A5FA;
    background: rgba(37,99,235,0.20);
    border: 1px solid rgba(37,99,235,0.45);
}

.cs-doc-archived {
    color: #94A3B8;
    background: rgba(15,23,42,0.5);
    border: 1px solid #334155;
}

.cs-doc-empty {
    background: #0B0F17;
    border: 1px dashed #1E293B;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    color: #64748B;
}

.cs-doc-section {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 850;
    margin-bottom: 12px;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def _text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    return str(value).strip()


def _date(
    value: Any,
) -> date | None:

    if value is None:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = _text(value)

    if not value:
        return None

    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError:
        return None


def _date_string(
    value: Any,
) -> str:

    parsed = _date(value)

    if parsed is None:
        return ""

    return parsed.isoformat()


def _documents(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    records = db.get(
        DOCUMENT_COLLECTION,
        [],
    )

    if not isinstance(records, list):

        records = []

        db[
            DOCUMENT_COLLECTION
        ] = records

        save_memory(db)

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


def _status_class(
    status: str,
) -> str:

    return {
        "Draft": "cs-doc-draft",
        "Under Review": "cs-doc-review",
        "Approved": "cs-doc-approved",
        "Issued": "cs-doc-issued",
        "Archived": "cs-doc-archived",
    }.get(
        status,
        "cs-doc-draft",
    )


# ============================================================
# VALIDATION
# ============================================================

def _validate(
    db: dict[str, Any],
    document_id: str,
    title: str,
    project_id: str,
    document_type: str,
    status: str,
    revision: str,
    document_date: date | None,
    exclude_id: Any = None,
) -> list[str]:

    errors: list[str] = []

    document_id = document_id.strip()

    if not document_id:
        errors.append(
            "Document ID is required."
        )

    elif len(document_id) > 60:
        errors.append(
            "Document ID cannot exceed 60 characters."
        )

    else:

        for record in _documents(db):

            existing = _text(
                record.get(
                    "document_id"
                )
            )

            if (
                existing.lower()
                == document_id.lower()
            ):

                if (
                    exclude_id is None
                    or str(
                        record.get("id")
                    )
                    != str(exclude_id)
                ):

                    errors.append(
                        "A document with this ID already exists."
                    )

                    break

    if not title.strip():

        errors.append(
            "Document title is required."
        )

    if not project_id.strip():

        errors.append(
            "Project ID is required."
        )

    if document_type not in DOCUMENT_TYPES:

        errors.append(
            "Invalid document type."
        )

    if status not in DOCUMENT_STATUSES:

        errors.append(
            "Invalid document status."
        )

    if not revision.strip():

        errors.append(
            "Revision is required."
        )

    if document_date is None:

        errors.append(
            "Document date is required."
        )

    return errors


# ============================================================
# CREATE
# ============================================================

def _create_document(
    db: dict[str, Any],
    document_id: str,
    title: str,
    project_id: str,
    document_type: str,
    status: str,
    revision: str,
    document_date: date,
    author: str,
    description: str,
) -> None:

    now = datetime.now().isoformat()

    record = {
        "id": next_id(
            DOCUMENT_COLLECTION,
            db,
        ),
        "document_id": document_id.strip(),
        "title": title.strip(),
        "project_id": project_id.strip(),
        "document_type": document_type,
        "status": status,
        "revision": revision.strip(),
        "document_date": document_date.isoformat(),
        "author": author.strip(),
        "description": description.strip(),
        "created_at": now,
        "updated_at": now,
    }

    add_record(
        DOCUMENT_COLLECTION,
        record,
        db,
    )


# ============================================================
# CREATE FORM
# ============================================================

def _render_create_form(
    db: dict[str, Any],
) -> None:

    with st.expander(
        "Create New Document",
        expanded=False,
    ):

        with st.form(
            "create_document_form",
            clear_on_submit=True,
        ):

            left, right = st.columns(2)

            with left:

                document_id = st.text_input(
                    "Document ID *",
                    placeholder="DOC-001",
                )

                title = st.text_input(
                    "Document Title *",
                    placeholder="Architectural General Arrangement",
                )

                project_id = st.text_input(
                    "Project ID *",
                    placeholder="PRJ-001",
                )

                document_type = st.selectbox(
                    "Document Type *",
                    DOCUMENT_TYPES,
                )

            with right:

                status = st.selectbox(
                    "Status *",
                    DOCUMENT_STATUSES,
                )

                revision = st.text_input(
                    "Revision *",
                    value="A",
                )

                document_date = st.date_input(
                    "Document Date *",
                    value=date.today(),
                )

                author = st.text_input(
                    "Author / Originator",
                    placeholder="Architect / Engineer / Consultant",
                )

            description = st.text_area(
                "Description",
                height=100,
            )

            submitted = st.form_submit_button(
                "Create Document",
                use_container_width=True,
            )

        if not submitted:
            return

        errors = _validate(
            db,
            document_id,
            title,
            project_id,
            document_type,
            status,
            revision,
            document_date,
        )

        if errors:

            for error in errors:
                st.error(error)

            return

        try:

            _create_document(
                db,
                document_id,
                title,
                project_id,
                document_type,
                status,
                revision,
                document_date,
                author,
                description,
            )

            st.success(
                "Document created successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                "Unable to create the document."
            )

            st.code(
                f"{type(exc).__name__}: {exc}"
            )


# ============================================================
# EDIT
# ============================================================

def _render_edit_form(
    db: dict[str, Any],
    document: dict[str, Any],
) -> None:

    record_id = document.get("id")

    with st.form(
        f"edit_document_{record_id}",
    ):

        left, right = st.columns(2)

        with left:

            document_id = st.text_input(
                "Document ID *",
                value=_text(
                    document.get(
                        "document_id"
                    )
                ),
            )

            title = st.text_input(
                "Document Title *",
                value=_text(
                    document.get(
                        "title"
                    )
                ),
            )

            project_id = st.text_input(
                "Project ID *",
                value=_text(
                    document.get(
                        "project_id"
                    )
                ),
            )

            current_type = _text(
                document.get(
                    "document_type"
                ),
                "Other",
            )

            if current_type not in DOCUMENT_TYPES:
                current_type = "Other"

            document_type = st.selectbox(
                "Document Type *",
                DOCUMENT_TYPES,
                index=DOCUMENT_TYPES.index(
                    current_type
                ),
            )

        with right:

            current_status = _text(
                document.get(
                    "status"
                ),
                "Draft",
            )

            if current_status not in DOCUMENT_STATUSES:
                current_status = "Draft"

            status = st.selectbox(
                "Status *",
                DOCUMENT_STATUSES,
                index=DOCUMENT_STATUSES.index(
                    current_status
                ),
            )

            revision = st.text_input(
                "Revision *",
                value=_text(
                    document.get(
                        "revision"
                    ),
                    "A",
                ),
            )

            document_date = st.date_input(
                "Document Date *",
                value=_date(
                    document.get(
                        "document_date"
                    )
                ) or date.today(),
            )

            author = st.text_input(
                "Author / Originator",
                value=_text(
                    document.get(
                        "author"
                    )
                ),
            )

        description = st.text_area(
            "Description",
            value=_text(
                document.get(
                    "description"
                )
            ),
            height=100,
        )

        submitted = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

    if not submitted:
        return

    errors = _validate(
        db,
        document_id,
        title,
        project_id,
        document_type,
        status,
        revision,
        document_date,
        exclude_id=record_id,
    )

    if errors:

        for error in errors:
            st.error(error)

        return

    updates = {
        "document_id": document_id.strip(),
        "title": title.strip(),
        "project_id": project_id.strip(),
        "document_type": document_type,
        "status": status,
        "revision": revision.strip(),
        "document_date": document_date.isoformat(),
        "author": author.strip(),
        "description": description.strip(),
        "updated_at": datetime.now().isoformat(),
    }

    try:

        result = update_record(
            DOCUMENT_COLLECTION,
            record_id,
            updates,
            db,
        )

        if result is None:

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
            "Unable to update the document."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# DELETE
# ============================================================

def _render_delete(
    db: dict[str, Any],
    document: dict[str, Any],
) -> None:

    record_id = document.get("id")

    title = _text(
        document.get(
            "title"
        ),
        "this document",
    )

    st.warning(
        f'Delete "{title}"? '
        "This action cannot be undone."
    )

    left, right = st.columns(2)

    with left:

        if st.button(
            "Delete Document",
            key=f"confirm_delete_document_{record_id}",
            use_container_width=True,
        ):

            try:

                result = delete_record(
                    DOCUMENT_COLLECTION,
                    record_id,
                    db,
                )

                if result:

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
                    "Unable to delete the document."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )

    with right:

        if st.button(
            "Cancel",
            key=f"cancel_delete_document_{record_id}",
            use_container_width=True,
        ):

            st.session_state.pop(
                f"delete_document_{record_id}",
                None,
            )

            st.rerun()


# ============================================================
# DOCUMENT CARD
# ============================================================

def _render_document_card(
    db: dict[str, Any],
    document: dict[str, Any],
) -> None:

    record_id = document.get(
        "id"
    )

    document_id = _text(
        document.get(
            "document_id"
        ),
        "N/A",
    )

    title = _text(
        document.get(
            "title"
        ),
        "Untitled Document",
    )

    project_id = _text(
        document.get(
            "project_id"
        ),
        "N/A",
    )

    document_type = _text(
        document.get(
            "document_type"
        ),
        "Other",
    )

    status = _text(
        document.get(
            "status"
        ),
        "Draft",
    )

    revision = _text(
        document.get(
            "revision"
        ),
        "A",
    )

    author = _text(
        document.get(
            "author"
        ),
        "Not specified",
    )

    document_date = _date_string(
        document.get(
            "document_date"
        )
    )

    css_class = _status_class(
        status
    )

    st.markdown(
        f"""
<div class="cs-doc-card">

    <div style="
        display:flex;
        justify-content:space-between;
        gap:15px;
        align-items:flex-start;
    ">

        <div>

            <div class="cs-doc-name">
                {title}
            </div>

            <div class="cs-doc-meta">
                {document_id}
                &nbsp; • &nbsp;
                {document_type}
                &nbsp; • &nbsp;
                Revision {revision}
            </div>

        </div>

        <div>
            <span class="cs-doc-status {css_class}">
                {status}
            </span>
        </div>

    </div>

    <div style="
        height:1px;
        background:#172033;
        margin:15px 0;
    "></div>

    <div style="
        display:grid;
        grid-template-columns:
            repeat(3, minmax(0, 1fr));
        gap:15px;
    ">

        <div>
            <div class="cs-doc-meta">
                PROJECT
            </div>

            <div class="cs-doc-info">
                {project_id}
            </div>
        </div>

        <div>
            <div class="cs-doc-meta">
                AUTHOR
            </div>

            <div class="cs-doc-info">
                {author}
            </div>
        </div>

        <div>
            <div class="cs-doc-meta">
                DOCUMENT DATE
            </div>

            <div class="cs-doc-info">
                {document_date or "Not specified"}
            </div>
        </div>

    </div>

</div>
""",
        unsafe_allow_html=True,
    )

    left, middle, right = st.columns(
        [1, 1, 4]
    )

    with left:

        if st.button(
            "Edit",
            key=f"edit_document_{record_id}",
            use_container_width=True,
        ):

            st.session_state[
                f"editing_document_{record_id}"
            ] = True

            st.session_state.pop(
                f"delete_document_{record_id}",
                None,
            )

            st.rerun()

    with middle:

        if st.button(
            "Delete",
            key=f"delete_document_{record_id}",
            use_container_width=True,
        ):

            st.session_state[
                f"delete_document_{record_id}"
            ] = True

            st.session_state.pop(
                f"editing_document_{record_id}",
                None,
            )

            st.rerun()

    if st.session_state.get(
        f"editing_document_{record_id}",
        False,
    ):

        _render_edit_form(
            db,
            document,
        )

    if st.session_state.get(
        f"delete_document_{record_id}",
        False,
    ):

        _render_delete(
            db,
            document,
        )


# ============================================================
# MAIN MODULE
# ============================================================

def render_documents_module(
    db: dict[str, Any] | None = None,
) -> None:

    _inject_css()

    if not isinstance(
        db,
        dict,
    ):

        db = load_memory()

    if DOCUMENT_COLLECTION not in db:

        db[
            DOCUMENT_COLLECTION
        ] = []

        save_memory(db)

    documents = _documents(
        db
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
<div class="cs-doc-header">

    <div class="cs-doc-title">
        Document Register
    </div>

    <div class="cs-doc-subtitle">
        Central document workspace for project
        information, technical records and controlled
        project documentation.
    </div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total = len(documents)

    drafts = sum(
        1
        for document in documents
        if document.get("status")
        == "Draft"
    )

    review = sum(
        1
        for document in documents
        if document.get("status")
        == "Under Review"
    )

    approved = sum(
        1
        for document in documents
        if document.get("status")
        == "Approved"
    )

    issued = sum(
        1
        for document in documents
        if document.get("status")
        == "Issued"
    )

    cols = st.columns(5)

    metrics = [
        ("Total Documents", total),
        ("Draft", drafts),
        ("Under Review", review),
        ("Approved", approved),
        ("Issued", issued),
    ]

    for column, (
        label,
        value,
    ) in zip(
        cols,
        metrics,
    ):

        with column:

            st.metric(
                label,
                value,
            )

    st.write("")

    # --------------------------------------------------------
    # Create
    # --------------------------------------------------------

    _render_create_form(
        db
    )

    # --------------------------------------------------------
    # Search / filters
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-doc-section">'
        "Document Register"
        "</div>",
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search Documents",
        placeholder=(
            "Search by document ID, title, "
            "project, type, author or revision..."
        ),
        key="document_search",
    )

    left, right = st.columns(2)

    with left:

        status_filter = st.selectbox(
            "Status",
            ["All"] + DOCUMENT_STATUSES,
            key="document_status_filter",
        )

    with right:

        type_filter = st.selectbox(
            "Document Type",
            ["All"] + DOCUMENT_TYPES,
            key="document_type_filter",
        )

    search_text = search.strip().lower()

    filtered = []

    for document in documents:

        status = _text(
            document.get(
                "status"
            ),
            "Draft",
        )

        document_type = _text(
            document.get(
                "document_type"
            ),
            "Other",
        )

        if (
            status_filter != "All"
            and status != status_filter
        ):
            continue

        if (
            type_filter != "All"
            and document_type != type_filter
        ):
            continue

        searchable = " ".join(
            [
                _text(
                    document.get(
                        "document_id"
                    )
                ),
                _text(
                    document.get(
                        "title"
                    )
                ),
                _text(
                    document.get(
                        "project_id"
                    )
                ),
                _text(
                    document.get(
                        "document_type"
                    )
                ),
                _text(
                    document.get(
                        "author"
                    )
                ),
                _text(
                    document.get(
                        "revision"
                    )
                ),
            ]
        ).lower()

        if (
            search_text
            and search_text not in searchable
        ):
            continue

        filtered.append(
            document
        )

    st.caption(
        f"Showing {len(filtered)} "
        f"of {len(documents)} documents"
    )

    # --------------------------------------------------------
    # Empty state
    # --------------------------------------------------------

    if not filtered:

        st.markdown(
            """
<div class="cs-doc-empty">

    <div style="
        color:#FFFFFF;
        font-size:17px;
        font-weight:800;
        margin-bottom:7px;
    ">
        No documents found
    </div>

    <div>
        Create a document or adjust your search
        and filters.
    </div>

</div>
""",
            unsafe_allow_html=True,
        )

        return

    # --------------------------------------------------------
    # Cards
    # --------------------------------------------------------

    for document in filtered:

        _render_document_card(
            db,
            document,
        )