"""
Creative Studios
AEC Collaboration Platform

Drawings Module
----------------
JSON-backed AEC drawing register.

Features:
- Create drawings
- List drawings
- Edit drawings
- Delete drawings
- Search
- Project filtering
- Drawing type filtering
- Status filtering
- Revision tracking
- Revision history
- Links to Projects and Documents
- Streamlit-safe status badges

Does NOT modify authentication, login, sidebar,
or global navigation behavior.
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


DRAWINGS_COLLECTION = "drawings"
PROJECTS_COLLECTION = "projects"
DOCUMENTS_COLLECTION = "documents"

DRAWING_TYPES = [
    "Architectural",
    "Structural",
    "Civil",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Fire Protection",
    "Landscape",
    "Interior",
    "Site Plan",
    "Shop Drawing",
    "As-Built",
    "Other",
]

DRAWING_STATUSES = [
    "Draft",
    "Under Review",
    "Approved",
    "Issued",
    "Superseded",
    "Archived",
]

REVISION_REASONS = [
    "Initial Issue",
    "Client Comments",
    "Consultant Comments",
    "Design Change",
    "Site Change",
    "Coordination",
    "Correction",
    "As-Built Update",
    "Other",
]


# ============================================================
# CSS
# ============================================================

def _inject_css() -> None:
    st.markdown(
        """
<style>

.cs-drawing-header {
    margin-bottom: 24px;
}

.cs-drawing-title {
    color: #F8FAFC;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.7px;
}

.cs-drawing-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
}

.cs-drawing-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 19px;
    margin-top: 14px;
}

.cs-drawing-card:hover {
    border-color: #2563EB;
}

.cs-drawing-name {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 850;
}

.cs-drawing-meta {
    color: #64748B;
    font-size: 11px;
    margin-top: 5px;
}

.cs-drawing-info {
    color: #CBD5E1;
    font-size: 12px;
    margin-top: 5px;
}

.cs-drawing-status {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 850;
}

.cs-drawing-draft {
    color: #CBD5E1;
    background: rgba(71, 85, 105, 0.18);
    border: 1px solid #334155;
}

.cs-drawing-review {
    color: #93C5FD;
    background: rgba(30, 64, 175, 0.15);
    border: 1px solid rgba(30, 64, 175, 0.35);
}

.cs-drawing-approved {
    color: #BFDBFE;
    background: rgba(37, 99, 235, 0.15);
    border: 1px solid rgba(37, 99, 235, 0.35);
}

.cs-drawing-issued {
    color: #60A5FA;
    background: rgba(37, 99, 235, 0.20);
    border: 1px solid rgba(37, 99, 235, 0.45);
}

.cs-drawing-superseded {
    color: #FBBF24;
    background: rgba(245, 158, 11, 0.10);
    border: 1px solid rgba(245, 158, 11, 0.25);
}

.cs-drawing-archived {
    color: #94A3B8;
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid #334155;
}

.cs-drawing-empty {
    background: #0B0F17;
    border: 1px dashed #1E293B;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    color: #64748B;
}

.cs-drawing-section {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 850;
    margin-bottom: 12px;
}

.cs-revision-box {
    background: #080C13;
    border: 1px solid #172033;
    border-radius: 10px;
    padding: 12px;
    margin-top: 8px;
}

.cs-revision-number {
    color: #60A5FA;
    font-size: 14px;
    font-weight: 900;
}

.cs-revision-text {
    color: #CBD5E1;
    font-size: 12px;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# SAFE HELPERS
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


def _collection(
    db: dict[str, Any],
    name: str,
) -> list[dict[str, Any]]:

    records = db.get(name, [])

    if not isinstance(records, list):

        records = []

        db[name] = records

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
        "Draft": "cs-drawing-draft",
        "Under Review": "cs-drawing-review",
        "Approved": "cs-drawing-approved",
        "Issued": "cs-drawing-issued",
        "Superseded": "cs-drawing-superseded",
        "Archived": "cs-drawing-archived",
    }.get(
        status,
        "cs-drawing-draft",
    )


def _projects(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _collection(
        db,
        PROJECTS_COLLECTION,
    )


def _documents(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _collection(
        db,
        DOCUMENTS_COLLECTION,
    )


def _drawings(
    db: dict[str, Any],
) -> list[dict[str, Any]]:

    return _collection(
        db,
        DRAWINGS_COLLECTION,
    )


# ============================================================
# PROJECT / DOCUMENT LOOKUPS
# ============================================================

def _project_label(
    project: dict[str, Any],
) -> str:

    project_id = _text(
        project.get("project_id"),
        _text(project.get("id"), "N/A"),
    )

    name = _text(
        project.get("name"),
        project_id,
    )

    return f"{project_id} • {name}"


def _document_label(
    document: dict[str, Any],
) -> str:

    document_id = _text(
        document.get("document_id"),
        _text(document.get("id"), "N/A"),
    )

    title = _text(
        document.get("title"),
        document_id,
    )

    return f"{document_id} • {title}"


def _project_by_id(
    db: dict[str, Any],
    project_id: str,
) -> dict[str, Any] | None:

    for project in _projects(db):

        if str(
            project.get("project_id", "")
        ).strip().lower() == project_id.strip().lower():

            return project

    return None


def _document_by_id(
    db: dict[str, Any],
    document_id: str,
) -> dict[str, Any] | None:

    for document in _documents(db):

        if str(
            document.get("document_id", "")
        ).strip().lower() == document_id.strip().lower():

            return document

    return None


# ============================================================
# REVISION HELPERS
# ============================================================

def _revision_history(
    drawing: dict[str, Any],
) -> list[dict[str, Any]]:

    history = drawing.get(
        "revision_history",
        [],
    )

    if not isinstance(history, list):
        return []

    return [
        item
        for item in history
        if isinstance(item, dict)
    ]


def _make_initial_revision(
    revision: str,
    reason: str,
    revision_date: date,
    author: str,
) -> dict[str, Any]:

    return {
        "revision": revision.strip(),
        "reason": reason,
        "date": revision_date.isoformat(),
        "author": author.strip(),
        "created_at": datetime.now().isoformat(),
    }


# ============================================================
# VALIDATION
# ============================================================

def _validate(
    db: dict[str, Any],
    drawing_number: str,
    title: str,
    project_id: str,
    document_id: str,
    drawing_type: str,
    status: str,
    revision: str,
    revision_reason: str,
    drawing_date: date | None,
    exclude_id: Any = None,
) -> list[str]:

    errors: list[str] = []

    drawing_number = drawing_number.strip()
    title = title.strip()
    project_id = project_id.strip()
    document_id = document_id.strip()

    if not drawing_number:

        errors.append(
            "Drawing number is required."
        )

    elif len(drawing_number) > 80:

        errors.append(
            "Drawing number cannot exceed 80 characters."
        )

    else:

        for drawing in _drawings(db):

            existing = _text(
                drawing.get(
                    "drawing_number"
                )
            )

            if (
                existing.lower()
                == drawing_number.lower()
            ):

                if (
                    exclude_id is None
                    or str(
                        drawing.get("id")
                    )
                    != str(exclude_id)
                ):

                    errors.append(
                        "A drawing with this number already exists."
                    )

                    break

    if not title:

        errors.append(
            "Drawing title is required."
        )

    if not project_id:

        errors.append(
            "A project must be selected."
        )

    elif _project_by_id(
        db,
        project_id,
    ) is None:

        errors.append(
            f"Project '{project_id}' does not exist."
        )

    if document_id:

        if _document_by_id(
            db,
            document_id,
        ) is None:

            errors.append(
                f"Document '{document_id}' does not exist."
            )

    if drawing_type not in DRAWING_TYPES:

        errors.append(
            "Invalid drawing type."
        )

    if status not in DRAWING_STATUSES:

        errors.append(
            "Invalid drawing status."
        )

    if not revision.strip():

        errors.append(
            "Revision is required."
        )

    if revision_reason not in REVISION_REASONS:

        errors.append(
            "Invalid revision reason."
        )

    if drawing_date is None:

        errors.append(
            "Drawing date is required."
        )

    return errors


# ============================================================
# CREATE
# ============================================================

def _create_drawing(
    db: dict[str, Any],
    drawing_number: str,
    title: str,
    project_id: str,
    document_id: str,
    drawing_type: str,
    status: str,
    revision: str,
    revision_reason: str,
    drawing_date: date,
    author: str,
    description: str,
) -> None:

    now = datetime.now().isoformat()

    revision_entry = _make_initial_revision(
        revision,
        revision_reason,
        drawing_date,
        author,
    )

    record = {
        "id": next_id(
            DRAWINGS_COLLECTION,
            db,
        ),
        "drawing_number": drawing_number.strip(),
        "title": title.strip(),
        "project_id": project_id.strip(),
        "document_id": document_id.strip(),
        "drawing_type": drawing_type,
        "status": status,
        "current_revision": revision.strip(),
        "drawing_date": drawing_date.isoformat(),
        "author": author.strip(),
        "description": description.strip(),
        "revision_history": [
            revision_entry
        ],
        "created_at": now,
        "updated_at": now,
    }

    add_record(
        DRAWINGS_COLLECTION,
        record,
        db,
    )


# ============================================================
# CREATE FORM
# ============================================================

def _render_create_form(
    db: dict[str, Any],
) -> None:

    projects = _projects(db)
    documents = _documents(db)

    with st.expander(
        "Create New Drawing",
        expanded=False,
    ):

        if not projects:

            st.warning(
                "Create a Project before creating a Drawing."
            )

            return

        project_options = [
            _project_label(project)
            for project in projects
        ]

        project_map = {
            _project_label(project):
            _text(
                project.get(
                    "project_id"
                )
            )
            for project in projects
        }

        document_options = [
            "No linked document"
        ]

        document_map = {
            "No linked document": ""
        }

        for document in documents:

            label = _document_label(
                document
            )

            document_options.append(
                label
            )

            document_map[
                label
            ] = _text(
                document.get(
                    "document_id"
                )
            )

        with st.form(
            "create_drawing_form",
            clear_on_submit=True,
        ):

            left, right = st.columns(2)

            with left:

                drawing_number = st.text_input(
                    "Drawing Number *",
                    placeholder="A-101",
                )

                title = st.text_input(
                    "Drawing Title *",
                    placeholder="Ground Floor Plan",
                )

                project_label = st.selectbox(
                    "Project *",
                    project_options,
                )

                drawing_type = st.selectbox(
                    "Drawing Type *",
                    DRAWING_TYPES,
                )

            with right:

                document_label = st.selectbox(
                    "Linked Document",
                    document_options,
                )

                status = st.selectbox(
                    "Status *",
                    DRAWING_STATUSES,
                )

                revision = st.text_input(
                    "Revision *",
                    value="A",
                )

                drawing_date = st.date_input(
                    "Drawing Date *",
                    value=date.today(),
                )

            left2, right2 = st.columns(2)

            with left2:

                revision_reason = st.selectbox(
                    "Revision Reason *",
                    REVISION_REASONS,
                )

            with right2:

                author = st.text_input(
                    "Author / Originator",
                    placeholder="Architect / Engineer",
                )

            description = st.text_area(
                "Description",
                height=100,
            )

            submitted = st.form_submit_button(
                "Create Drawing",
                use_container_width=True,
            )

        if not submitted:
            return

        project_id = project_map[
            project_label
        ]

        document_id = document_map[
            document_label
        ]

        errors = _validate(
            db,
            drawing_number,
            title,
            project_id,
            document_id,
            drawing_type,
            status,
            revision,
            revision_reason,
            drawing_date,
        )

        if errors:

            for error in errors:
                st.error(error)

            return

        try:

            _create_drawing(
                db,
                drawing_number,
                title,
                project_id,
                document_id,
                drawing_type,
                status,
                revision,
                revision_reason,
                drawing_date,
                author,
                description,
            )

            st.success(
                "Drawing created successfully."
            )

            st.rerun()

        except Exception as exc:

            st.error(
                "Unable to create the drawing."
            )

            st.code(
                f"{type(exc).__name__}: {exc}"
            )


# ============================================================
# EDIT
# ============================================================

def _render_edit_form(
    db: dict[str, Any],
    drawing: dict[str, Any],
) -> None:

    record_id = drawing.get("id")

    projects = _projects(db)
    documents = _documents(db)

    project_map = {
        _project_label(project):
        _text(
            project.get(
                "project_id"
            )
        )
        for project in projects
    }

    project_labels = list(
        project_map.keys()
    )

    current_project_id = _text(
        drawing.get(
            "project_id"
        )
    )

    selected_project_label = next(
        (
            label
            for label, project_id
            in project_map.items()
            if project_id.lower()
            == current_project_id.lower()
        ),
        project_labels[0]
        if project_labels
        else "",
    )

    document_options = [
        "No linked document"
    ]

    document_map = {
        "No linked document": ""
    }

    for document in documents:

        label = _document_label(
            document
        )

        document_options.append(
            label
        )

        document_map[
            label
        ] = _text(
            document.get(
                "document_id"
            )
        )

    current_document_id = _text(
        drawing.get(
            "document_id"
        )
    )

    selected_document_label = next(
        (
            label
            for label, document_id
            in document_map.items()
            if document_id.lower()
            == current_document_id.lower()
        ),
        "No linked document",
    )

    current_type = _text(
        drawing.get(
            "drawing_type"
        ),
        "Other",
    )

    if current_type not in DRAWING_TYPES:
        current_type = "Other"

    current_status = _text(
        drawing.get(
            "status"
        ),
        "Draft",
    )

    if current_status not in DRAWING_STATUSES:
        current_status = "Draft"

    with st.form(
        f"edit_drawing_{record_id}",
    ):

        left, right = st.columns(2)

        with left:

            drawing_number = st.text_input(
                "Drawing Number *",
                value=_text(
                    drawing.get(
                        "drawing_number"
                    )
                ),
            )

            title = st.text_input(
                "Drawing Title *",
                value=_text(
                    drawing.get(
                        "title"
                    )
                ),
            )

            if project_labels:

                selected_project_label = st.selectbox(
                    "Project *",
                    project_labels,
                    index=project_labels.index(
                        selected_project_label
                    ),
                )

            else:

                st.error(
                    "No projects are available."
                )

                selected_project_label = ""

            drawing_type = st.selectbox(
                "Drawing Type *",
                DRAWING_TYPES,
                index=DRAWING_TYPES.index(
                    current_type
                ),
            )

        with right:

            selected_document_label = st.selectbox(
                "Linked Document",
                document_options,
                index=document_options.index(
                    selected_document_label
                ),
            )

            status = st.selectbox(
                "Status *",
                DRAWING_STATUSES,
                index=DRAWING_STATUSES.index(
                    current_status
                ),
            )

            current_revision = _text(
                drawing.get(
                    "current_revision"
                ),
                "A",
            )

            revision = st.text_input(
                "Revision *",
                value=current_revision,
            )

            drawing_date = st.date_input(
                "Drawing Date *",
                value=_date(
                    drawing.get(
                        "drawing_date"
                    )
                ) or date.today(),
            )

        revision_reason = st.selectbox(
            "Revision Reason *",
            REVISION_REASONS,
        )

        author = st.text_input(
            "Author / Originator",
            value=_text(
                drawing.get(
                    "author"
                )
            ),
        )

        description = st.text_area(
            "Description",
            value=_text(
                drawing.get(
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

    project_id = project_map.get(
        selected_project_label,
        "",
    )

    document_id = document_map.get(
        selected_document_label,
        "",
    )

    errors = _validate(
        db,
        drawing_number,
        title,
        project_id,
        document_id,
        drawing_type,
        status,
        revision,
        revision_reason,
        drawing_date,
        exclude_id=record_id,
    )

    if errors:

        for error in errors:
            st.error(error)

        return

    old_revision = _text(
        drawing.get(
            "current_revision"
        )
    )

    history = _revision_history(
        drawing
    )

    if revision.strip() != old_revision.strip():

        history.append(
            _make_initial_revision(
                revision,
                revision_reason,
                drawing_date,
                author,
            )
        )

    updates = {
        "drawing_number": drawing_number.strip(),
        "title": title.strip(),
        "project_id": project_id,
        "document_id": document_id,
        "drawing_type": drawing_type,
        "status": status,
        "current_revision": revision.strip(),
        "drawing_date": drawing_date.isoformat(),
        "author": author.strip(),
        "description": description.strip(),
        "revision_history": history,
        "updated_at": datetime.now().isoformat(),
    }

    try:

        result = update_record(
            DRAWINGS_COLLECTION,
            record_id,
            updates,
            db,
        )

        if result is None:

            st.error(
                "Drawing could not be found."
            )

            return

        st.success(
            "Drawing updated successfully."
        )

        st.rerun()

    except Exception as exc:

        st.error(
            "Unable to update the drawing."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# REVISION HISTORY
# ============================================================

def _render_revision_history(
    drawing: dict[str, Any],
) -> None:

    history = _revision_history(
        drawing
    )

    if not history:

        st.info(
            "No revision history is available."
        )

        return

    st.markdown(
        "**Revision History**"
    )

    for revision in reversed(history):

        revision_number = _text(
            revision.get(
                "revision"
            ),
            "N/A",
        )

        reason = _text(
            revision.get(
                "reason"
            ),
            "Not specified",
        )

        revision_date = _text(
            revision.get(
                "date"
            ),
            "N/A",
        )

        author = _text(
            revision.get(
                "author"
            ),
            "Not specified",
        )

        st.markdown(
            f"""
<div class="cs-revision-box">

    <div class="cs-revision-number">
        Revision {revision_number}
    </div>

    <div class="cs-revision-text">
        {reason}
        &nbsp; • &nbsp;
        {revision_date}
        &nbsp; • &nbsp;
        {author}
    </div>

</div>
""",
            unsafe_allow_html=True,
        )


# ============================================================
# DELETE
# ============================================================

def _render_delete(
    db: dict[str, Any],
    drawing: dict[str, Any],
) -> None:

    record_id = drawing.get(
        "id"
    )

    title = _text(
        drawing.get(
            "title"
        ),
        "this drawing",
    )

    st.warning(
        f'Delete "{title}"? '
        "This action cannot be undone."
    )

    left, right = st.columns(2)

    with left:

        if st.button(
            "Delete Drawing",
            key=f"confirm_delete_drawing_{record_id}",
            use_container_width=True,
        ):

            try:

                result = delete_record(
                    DRAWINGS_COLLECTION,
                    record_id,
                    db,
                )

                if result:

                    st.success(
                        "Drawing deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        "Drawing could not be found."
                    )

            except Exception as exc:

                st.error(
                    "Unable to delete the drawing."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )

    with right:

        if st.button(
            "Cancel",
            key=f"cancel_delete_drawing_{record_id}",
            use_container_width=True,
        ):

            st.session_state.pop(
                f"delete_drawing_{record_id}",
                None,
            )

            st.rerun()


# ============================================================
# DRAWING CARD
# ============================================================

def _render_drawing_card(
    db: dict[str, Any],
    drawing: dict[str, Any],
) -> None:

    record_id = drawing.get(
        "id"
    )

    drawing_number = _text(
        drawing.get(
            "drawing_number"
        ),
        "N/A",
    )

    title = _text(
        drawing.get(
            "title"
        ),
        "Untitled Drawing",
    )

    project_id = _text(
        drawing.get(
            "project_id"
        ),
        "N/A",
    )

    document_id = _text(
        drawing.get(
            "document_id"
        ),
        "Not linked",
    )

    drawing_type = _text(
        drawing.get(
            "drawing_type"
        ),
        "Other",
    )

    status = _text(
        drawing.get(
            "status"
        ),
        "Draft",
    )

    revision = _text(
        drawing.get(
            "current_revision"
        ),
        "A",
    )

    author = _text(
        drawing.get(
            "author"
        ),
        "Not specified",
    )

    drawing_date = _date_string(
        drawing.get(
            "drawing_date"
        )
    )

    project = _project_by_id(
        db,
        project_id,
    )

    document = _document_by_id(
        db,
        document_id,
    )

    project_name = (
        _text(
            project.get("name")
        )
        if project
        else project_id
    )

    document_title = (
        _text(
            document.get("title")
        )
        if document
        else document_id
    )

    css_class = _status_class(
        status
    )

    st.markdown(
        f"""
<div class="cs-drawing-card">

    <div style="
        display:flex;
        justify-content:space-between;
        gap:15px;
        align-items:flex-start;
    ">

        <div>

            <div class="cs-drawing-name">
                {drawing_number} • {title}
            </div>

            <div class="cs-drawing-meta">
                {drawing_type}
                &nbsp; • &nbsp;
                Revision {revision}
            </div>

        </div>

        <div>
            <span class="cs-drawing-status {css_class}">
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
            repeat(4, minmax(0, 1fr));
        gap:15px;
    ">

        <div>
            <div class="cs-drawing-meta">
                PROJECT
            </div>

            <div class="cs-drawing-info">
                {project_id}
                <br>
                {project_name}
            </div>
        </div>

        <div>
            <div class="cs-drawing-meta">
                DOCUMENT
            </div>

            <div class="cs-drawing-info">
                {document_id}
                <br>
                {document_title}
            </div>
        </div>

        <div>
            <div class="cs-drawing-meta">
                AUTHOR
            </div>

            <div class="cs-drawing-info">
                {author}
            </div>
        </div>

        <div>
            <div class="cs-drawing-meta">
                DRAWING DATE
            </div>

            <div class="cs-drawing-info">
                {drawing_date or "Not specified"}
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
            key=f"edit_drawing_{record_id}",
            use_container_width=True,
        ):

            st.session_state[
                f"editing_drawing_{record_id}"
            ] = True

            st.session_state.pop(
                f"delete_drawing_{record_id}",
                None,
            )

            st.rerun()

    with middle:

        if st.button(
            "Delete",
            key=f"delete_drawing_{record_id}",
            use_container_width=True,
        ):

            st.session_state[
                f"delete_drawing_{record_id}"
            ] = True

            st.session_state.pop(
                f"editing_drawing_{record_id}",
                None,
            )

            st.rerun()

    with right:

        if st.button(
            "Revision History",
            key=f"revision_drawing_{record_id}",
            use_container_width=False,
        ):

            st.session_state[
                f"revision_history_drawing_{record_id}"
            ] = not st.session_state.get(
                f"revision_history_drawing_{record_id}",
                False,
            )

            st.rerun()

    if st.session_state.get(
        f"editing_drawing_{record_id}",
        False,
    ):

        _render_edit_form(
            db,
            drawing,
        )

    if st.session_state.get(
        f"delete_drawing_{record_id}",
        False,
    ):

        _render_delete(
            db,
            drawing,
        )

    if st.session_state.get(
        f"revision_history_drawing_{record_id}",
        False,
    ):

        _render_revision_history(
            drawing
        )


# ============================================================
# MAIN MODULE
# ============================================================

def render_drawings_module(
    db: dict[str, Any] | None = None,
) -> None:

    _inject_css()

    if not isinstance(
        db,
        dict,
    ):

        db = load_memory()

    if DRAWINGS_COLLECTION not in db:

        db[
            DRAWINGS_COLLECTION
        ] = []

        save_memory(db)

    if PROJECTS_COLLECTION not in db:

        db[
            PROJECTS_COLLECTION
        ] = []

        save_memory(db)

    if DOCUMENTS_COLLECTION not in db:

        db[
            DOCUMENTS_COLLECTION
        ] = []

        save_memory(db)

    drawings = _drawings(db)
    projects = _projects(db)

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
<div class="cs-drawing-header">

    <div class="cs-drawing-title">
        Drawing Register
    </div>

    <div class="cs-drawing-subtitle">
        Central AEC drawing workspace for architectural,
        engineering, coordination and construction drawings.
    </div>

</div>
""",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    total = len(drawings)

    drafts = sum(
        1
        for drawing in drawings
        if drawing.get("status")
        == "Draft"
    )

    review = sum(
        1
        for drawing in drawings
        if drawing.get("status")
        == "Under Review"
    )

    approved = sum(
        1
        for drawing in drawings
        if drawing.get("status")
        == "Approved"
    )

    issued = sum(
        1
        for drawing in drawings
        if drawing.get("status")
        == "Issued"
    )

    columns = st.columns(5)

    metrics = [
        ("Total Drawings", total),
        ("Draft", drafts),
        ("Under Review", review),
        ("Approved", approved),
        ("Issued", issued),
    ]

    for column, (
        label,
        value,
    ) in zip(
        columns,
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
    # Register
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-drawing-section">'
        "Drawing Register"
        "</div>",
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search Drawings",
        placeholder=(
            "Search by drawing number, title, "
            "project, document, author or revision..."
        ),
        key="drawing_search",
    )

    filter_columns = st.columns(3)

    with filter_columns[0]:

        project_options = [
            "All"
        ]

        project_map = {}

        for project in projects:

            label = _project_label(
                project
            )

            project_options.append(
                label
            )

            project_map[
                label
            ] = _text(
                project.get(
                    "project_id"
                )
            )

        project_filter = st.selectbox(
            "Project",
            project_options,
            key="drawing_project_filter",
        )

    with filter_columns[1]:

        type_filter = st.selectbox(
            "Drawing Type",
            ["All"] + DRAWING_TYPES,
            key="drawing_type_filter",
        )

    with filter_columns[2]:

        status_filter = st.selectbox(
            "Status",
            ["All"] + DRAWING_STATUSES,
            key="drawing_status_filter",
        )

    search_text = search.strip().lower()

    selected_project_id = project_map.get(
        project_filter,
        "",
    )

    filtered = []

    for drawing in drawings:

        drawing_project_id = _text(
            drawing.get(
                "project_id"
            )
        )

        drawing_type = _text(
            drawing.get(
                "drawing_type"
            ),
            "Other",
        )

        drawing_status = _text(
            drawing.get(
                "status"
            ),
            "Draft",
        )

        if (
            selected_project_id
            and drawing_project_id.lower()
            != selected_project_id.lower()
        ):
            continue

        if (
            type_filter != "All"
            and drawing_type != type_filter
        ):
            continue

        if (
            status_filter != "All"
            and drawing_status != status_filter
        ):
            continue

        searchable = " ".join(
            [
                _text(
                    drawing.get(
                        "drawing_number"
                    )
                ),
                _text(
                    drawing.get(
                        "title"
                    )
                ),
                _text(
                    drawing.get(
                        "project_id"
                    )
                ),
                _text(
                    drawing.get(
                        "document_id"
                    )
                ),
                _text(
                    drawing.get(
                        "drawing_type"
                    )
                ),
                _text(
                    drawing.get(
                        "author"
                    )
                ),
                _text(
                    drawing.get(
                        "current_revision"
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
            drawing
        )

    st.caption(
        f"Showing {len(filtered)} "
        f"of {len(drawings)} drawings"
    )

    # --------------------------------------------------------
    # Empty state
    # --------------------------------------------------------

    if not filtered:

        st.markdown(
            """
<div class="cs-drawing-empty">

    <div style="
        color:#FFFFFF;
        font-size:17px;
        font-weight:800;
        margin-bottom:7px;
    ">
        No drawings found
    </div>

    <div>
        Create a drawing or adjust your search
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

    for drawing in filtered:

        _render_drawing_card(
            db,
            drawing,
        )