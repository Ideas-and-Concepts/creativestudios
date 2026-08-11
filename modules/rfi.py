"""
Creative Studios
RFI & Technical Queries Module

Manages Requests for Information (RFIs) and
technical queries between project stakeholders.

Workflow:

Project
   ↓
RFI Raised
   ↓
Assigned
   ↓
Under Review
   ↓
Answered / Returned
   ↓
Closed
"""

from datetime import date, timedelta

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    update_record,
)


RFI_STATUSES = [
    "Open",
    "Assigned",
    "Under Review",
    "Answered",
    "Closed",
    "Cancelled",
]

RFI_PRIORITIES = [
    "Low",
    "Normal",
    "High",
    "Critical",
]

RFI_CATEGORIES = [
    "Architectural",
    "Structural",
    "Civil",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Fire Protection",
    "Materials",
    "Specification",
    "BOQ / Cost",
    "Site Condition",
    "Other",
]


# ============================================================
# DATABASE HELPERS
# ============================================================

def _get_projects(db):
    return get_collection(db, "projects")


def _get_rfis(db):
    return get_collection(db, "rfis")


def _get_drawings(db):
    return get_collection(db, "drawings")


def _project_name(db, project_id):

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


def _next_rfi_number(db, project_id):

    count = 0

    for rfi in _get_rfis(db):

        if str(
            rfi.get("project_id")
        ) == str(project_id):

            count += 1

    return (
        f"RFI-{project_id}-"
        f"{count + 1:04d}"
    )


def _is_overdue(rfi):

    status = rfi.get(
        "status",
        "Open",
    )

    if status in [
        "Closed",
        "Cancelled",
    ]:

        return False

    due_date = rfi.get(
        "due_date"
    )

    if not due_date:

        return False

    try:

        due = date.fromisoformat(
            str(due_date)
        )

        return due < date.today()

    except ValueError:

        return False


def _status_badge(status):

    if status == "Closed":

        st.success(
            status,
            icon="✓",
        )

    elif status == "Answered":

        st.success(
            status,
            icon="✓",
        )

    elif status == "Open":

        st.warning(
            status,
            icon="!",
        )

    elif status == "Under Review":

        st.info(
            status,
            icon="◌",
        )

    elif status == "Cancelled":

        st.error(
            status,
            icon="×",
        )

    else:

        st.caption(
            status
        )


def _priority_badge(priority):

    if priority == "Critical":

        st.error(
            "CRITICAL",
            icon="!",
        )

    elif priority == "High":

        st.warning(
            "HIGH",
            icon="▲",
        )

    elif priority == "Normal":

        st.info(
            "NORMAL"
        )

    else:

        st.caption(
            "LOW"
        )


# ============================================================
# RFI CARD
# ============================================================

def _render_rfi_card(
    db,
    rfi,
):

    rfi_id = rfi.get(
        "id",
        "",
    )

    status = rfi.get(
        "status",
        "Open",
    )

    priority = rfi.get(
        "priority",
        "Normal",
    )

    with st.container(
        border=True
    ):

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:

            st.markdown(
                f"### "
                f"{rfi.get('rfi_number', '')} "
                f"— "
                f"{rfi.get('subject', '')}"
            )

            st.caption(
                f"Project: "
                f"{_project_name(db, rfi.get('project_id'))}"
                f" • "
                f"{rfi.get('category', 'Other')}"
            )

        with top_right:

            _status_badge(
                status
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.markdown(
                "**Priority**"
            )

            _priority_badge(
                priority
            )

        with col2:

            st.markdown(
                "**Raised By**"
            )

            st.write(
                rfi.get(
                    "raised_by",
                    "Unknown",
                )
            )

        with col3:

            st.markdown(
                "**Assigned To**"
            )

            st.write(
                rfi.get(
                    "assigned_to",
                    "Not assigned",
                )
            )

        with col4:

            st.markdown(
                "**Due Date**"
            )

            due_date = rfi.get(
                "due_date",
                "",
            )

            st.write(
                due_date or "Not set"
            )

        if _is_overdue(rfi):

            st.error(
                "This RFI is overdue.",
                icon="⏰",
            )

        with st.expander(
            "RFI Details"
        ):

            st.markdown(
                f"**Question:**"
            )

            st.write(
                rfi.get(
                    "question",
                    "",
                )
            )

            related_document = rfi.get(
                "related_document",
                "",
            )

            if related_document:

                st.markdown(
                    f"**Related Document:** "
                    f"{related_document}"
                )

            response = rfi.get(
                "response",
                "",
            )

            if response:

                st.divider()

                st.markdown(
                    "**Response / Technical Direction**"
                )

                st.info(
                    response
                )

            if rfi.get(
                "resolution_date"
            ):

                st.markdown(
                    f"**Resolution Date:** "
                    f"{rfi.get('resolution_date')}"
                )

            if rfi.get(
                "notes"
            ):

                st.markdown(
                    f"**Notes:** "
                    f"{rfi.get('notes')}"
                )

        edit_col, delete_col = st.columns(
            2
        )

        with edit_col:

            if st.button(
                "Open / Update",
                key=f"open_rfi_{rfi_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "edit_rfi_id"
                ] = rfi_id

                st.rerun()

        with delete_col:

            if st.button(
                "Delete",
                key=f"delete_rfi_{rfi_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "delete_rfi_id"
                ] = rfi_id

                st.rerun()


# ============================================================
# CREATE RFI
# ============================================================

def _render_create_rfi(db):

    projects = _get_projects(db)
    drawings = _get_drawings(db)

    st.subheader(
        "Raise RFI / Technical Query"
    )

    if not projects:

        st.warning(
            "Create a project before raising an RFI."
        )

        return

    project_options = {
        _project_name(
            db,
            project.get("id"),
        ):
            project.get("id")
        for project in projects
    }

    with st.form(
        "create_rfi_form"
    ):

        project_label = st.selectbox(
            "Project *",
            list(
                project_options.keys()
            ),
        )

        project_id = project_options[
            project_label
        ]

        col1, col2 = st.columns(2)

        with col1:

            subject = st.text_input(
                "Subject *",
                placeholder=(
                    "Clarification on beam detail"
                ),
            )

            category = st.selectbox(
                "Category",
                RFI_CATEGORIES,
            )

            priority = st.selectbox(
                "Priority",
                RFI_PRIORITIES,
            )

        with col2:

            assigned_to = st.text_input(
                "Assigned To",
                placeholder=(
                    "e.g. Structural Engineer"
                ),
            )

            due_date = st.date_input(
                "Due Date",
                value=date.today()
                + timedelta(days=7),
            )

            related_documents = [
                "None"
            ]

            for drawing in drawings:

                if str(
                    drawing.get("project_id")
                ) == str(project_id):

                    related_documents.append(
                        (
                            f"{drawing.get('drawing_number', '')} "
                            f"— "
                            f"{drawing.get('title', '')} "
                            f"(Rev "
                            f"{drawing.get('revision', '0')})"
                        )
                    )

            related_document = st.selectbox(
                "Related Drawing / Document",
                related_documents,
            )

        question = st.text_area(
            "Technical Question *",
            placeholder=(
                "Clearly describe the information "
                "or clarification required."
            ),
            height=160,
        )

        notes = st.text_area(
            "Additional Notes",
            height=100,
        )

        submitted = st.form_submit_button(
            "Raise RFI",
            use_container_width=True,
        )

    if not submitted:

        return

    subject = subject.strip()

    question = question.strip()

    if not subject:

        st.error(
            "RFI subject is required."
        )

        return

    if not question:

        st.error(
            "Technical question is required."
        )

        return

    rfi_number = _next_rfi_number(
        db,
        project_id,
    )

    rfi = {

        "id": rfi_number,

        "rfi_number": rfi_number,

        "project_id": project_id,

        "subject": subject,

        "category": category,

        "priority": priority,

        "status": "Open",

        "raised_by": _current_user(),

        "assigned_to": assigned_to.strip(),

        "due_date": str(
            due_date
        ),

        "related_document": (
            ""
            if related_document == "None"
            else related_document
        ),

        "question": question,

        "response": "",

        "resolution_date": "",

        "resolved_by": "",

        "notes": notes.strip(),

        "created_at": str(
            date.today()
        ),

    }

    add_record(
        db,
        "rfis",
        rfi,
    )

    st.success(
        f"{rfi_number} raised successfully."
    )

    st.rerun()


# ============================================================
# UPDATE RFI
# ============================================================

def _render_edit_rfi(
    db,
    rfi,
):

    st.subheader(
        f"Update {rfi.get('rfi_number', '')}"
    )

    with st.form(
        f"edit_rfi_form_{rfi.get('id')}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            subject = st.text_input(
                "Subject",
                value=rfi.get(
                    "subject",
                    "",
                ),
            )

            category = st.selectbox(
                "Category",
                RFI_CATEGORIES,
                index=(
                    RFI_CATEGORIES.index(
                        rfi.get(
                            "category",
                            RFI_CATEGORIES[0],
                        )
                    )
                    if rfi.get("category")
                    in RFI_CATEGORIES
                    else 0
                ),
            )

            priority = st.selectbox(
                "Priority",
                RFI_PRIORITIES,
                index=(
                    RFI_PRIORITIES.index(
                        rfi.get(
                            "priority",
                            "Normal",
                        )
                    )
                    if rfi.get("priority")
                    in RFI_PRIORITIES
                    else 1
                ),
            )

        with col2:

            status = st.selectbox(
                "Status",
                RFI_STATUSES,
                index=(
                    RFI_STATUSES.index(
                        rfi.get(
                            "status",
                            "Open",
                        )
                    )
                    if rfi.get("status")
                    in RFI_STATUSES
                    else 0
                ),
            )

            assigned_to = st.text_input(
                "Assigned To",
                value=rfi.get(
                    "assigned_to",
                    "",
                ),
            )

            try:

                current_due = date.fromisoformat(
                    str(
                        rfi.get(
                            "due_date",
                            date.today(),
                        )
                    )
                )

            except ValueError:

                current_due = date.today()

            due_date = st.date_input(
                "Due Date",
                value=current_due,
            )

        question = st.text_area(
            "Technical Question",
            value=rfi.get(
                "question",
                "",
            ),
            height=140,
        )

        response = st.text_area(
            "Response / Technical Direction",
            value=rfi.get(
                "response",
                "",
            ),
            height=160,
        )

        notes = st.text_area(
            "Notes",
            value=rfi.get(
                "notes",
                "",
            ),
            height=100,
        )

        save = st.form_submit_button(
            "Save RFI",
            use_container_width=True,
        )

    if not save:

        return

    if not subject.strip():

        st.error(
            "Subject is required."
        )

        return

    if not question.strip():

        st.error(
            "Technical question is required."
        )

        return

    updates = {

        "subject": subject.strip(),

        "category": category,

        "priority": priority,

        "status": status,

        "assigned_to": assigned_to.strip(),

        "due_date": str(
            due_date
        ),

        "question": question.strip(),

        "response": response.strip(),

        "notes": notes.strip(),

        "updated_at": str(
            date.today()
        ),

        "updated_by": _current_user(),

    }

    if (
        status == "Answered"
        or status == "Closed"
    ):

        updates[
            "resolution_date"
        ] = str(
            date.today()
        )

        updates[
            "resolved_by"
        ] = _current_user()

    update_record(
        db,
        "rfis",
        rfi.get("id"),
        updates,
    )

    st.session_state.pop(
        "edit_rfi_id",
        None,
    )

    st.success(
        "RFI updated successfully."
    )

    st.rerun()


# ============================================================
# DELETE RFI
# ============================================================

def _render_delete_confirmation(
    db,
    rfi,
):

    st.warning(
        f"Delete "
        f"**{rfi.get('rfi_number', '')}**?"
    )

    st.write(
        rfi.get(
            "subject",
            "",
        )
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Delete RFI",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "rfis",
                rfi.get("id"),
            )

            st.session_state.pop(
                "delete_rfi_id",
                None,
            )

            st.success(
                "RFI deleted."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_rfi_id",
                None,
            )

            st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_rfi_module(db):

    rfis = _get_rfis(db)

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                RFI & Technical Queries
            </div>
            <div class="module-subtitle">
                Technical clarification, coordination
                and project information management.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI
    # ========================================================

    total = len(rfis)

    open_count = sum(
        1
        for rfi in rfis
        if rfi.get("status")
        in [
            "Open",
            "Assigned",
            "Under Review",
        ]
    )

    answered = sum(
        1
        for rfi in rfis
        if rfi.get("status")
        == "Answered"
    )

    closed = sum(
        1
        for rfi in rfis
        if rfi.get("status")
        == "Closed"
    )

    overdue = sum(
        1
        for rfi in rfis
        if _is_overdue(rfi)
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total RFIs",
            total,
        )

    with col2:

        st.metric(
            "Open",
            open_count,
        )

    with col3:

        st.metric(
            "Answered",
            answered,
        )

    with col4:

        st.metric(
            "Closed",
            closed,
        )

    with col5:

        st.metric(
            "Overdue",
            overdue,
        )

    st.divider()

    # ========================================================
    # EDIT
    # ========================================================

    edit_id = st.session_state.get(
        "edit_rfi_id"
    )

    if edit_id:

        rfi = next(
            (
                item
                for item in rfis
                if str(item.get("id"))
                == str(edit_id)
            ),
            None,
        )

        if rfi:

            _render_edit_rfi(
                db,
                rfi,
            )

            st.divider()

    # ========================================================
    # DELETE
    # ========================================================

    delete_id = st.session_state.get(
        "delete_rfi_id"
    )

    if delete_id:

        rfi = next(
            (
                item
                for item in rfis
                if str(item.get("id"))
                == str(delete_id)
            ),
            None,
        )

        if rfi:

            _render_delete_confirmation(
                db,
                rfi,
            )

            st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_create = st.tabs(
        [
            "RFI Register",
            "Raise RFI",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        if not rfis:

            st.info(
                "No RFIs or technical queries "
                "have been raised."
            )

        else:

            search = st.text_input(
                "Search RFIs",
                placeholder=(
                    "RFI number, subject, project, "
                    "category or assigned person..."
                ),
            )

            col1, col2, col3 = st.columns(3)

            with col1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"]
                    + RFI_STATUSES,
                )

            with col2:

                priority_filter = st.selectbox(
                    "Priority",
                    ["All"]
                    + RFI_PRIORITIES,
                )

            with col3:

                category_filter = st.selectbox(
                    "Category",
                    ["All"]
                    + RFI_CATEGORIES,
                )

            search_term = (
                search.strip().lower()
            )

            filtered = []

            for rfi in rfis:

                searchable = " ".join(
                    [
                        str(
                            rfi.get(
                                "rfi_number",
                                "",
                            )
                        ),
                        str(
                            rfi.get(
                                "subject",
                                "",
                            )
                        ),
                        str(
                            rfi.get(
                                "question",
                                "",
                            )
                        ),
                        str(
                            rfi.get(
                                "project_id",
                                "",
                            )
                        ),
                        str(
                            rfi.get(
                                "assigned_to",
                                "",
                            )
                        ),
                        str(
                            rfi.get(
                                "category",
                                "",
                            )
                        ),
                        _project_name(
                            db,
                            rfi.get(
                                "project_id",
                                "",
                            ),
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
                    and rfi.get(
                        "status"
                    )
                    != status_filter
                ):

                    continue

                if (
                    priority_filter != "All"
                    and rfi.get(
                        "priority"
                    )
                    != priority_filter
                ):

                    continue

                if (
                    category_filter != "All"
                    and rfi.get(
                        "category"
                    )
                    != category_filter
                ):

                    continue

                filtered.append(
                    rfi
                )

            st.caption(
                f"Showing {len(filtered)} "
                f"of {len(rfis)} RFIs"
            )

            # Critical and overdue RFIs first.
            filtered.sort(
                key=lambda item: (
                    not _is_overdue(item),
                    item.get(
                        "priority"
                    ) != "Critical",
                    item.get(
                        "due_date",
                        "",
                    ),
                )
            )

            for rfi in filtered:

                _render_rfi_card(
                    db,
                    rfi,
                )

    # ========================================================
    # CREATE
    # ========================================================

    with tab_create:

        _render_create_rfi(
            db
        )