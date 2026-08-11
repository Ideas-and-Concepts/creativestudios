"""
Creative Studios
Drawing Repository Module

Manages project drawings, revisions, disciplines,
statuses and document control.
"""

from datetime import date

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    update_record,
)


DISCIPLINES = [
    "Architectural",
    "Structural",
    "Civil",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Fire Protection",
    "Landscape",
    "Interior Design",
    "Other",
]

DRAWING_TYPES = [
    "General Arrangement",
    "Floor Plan",
    "Elevation",
    "Section",
    "Detail",
    "Structural",
    "MEP",
    "Civil",
    "Site Plan",
    "Schedule",
    "Specification",
    "As-Built",
    "Other",
]

DRAWING_STATUSES = [
    "Draft",
    "For Review",
    "For Approval",
    "Approved",
    "Issued for Construction",
    "Superseded",
    "As-Built",
]


def _get_projects(db):
    return get_collection(db, "projects")


def _get_drawings(db):
    return get_collection(db, "drawings")


def _project_name(db, project_id):
    for project in _get_projects(db):
        if str(project.get("id")) == str(project_id):
            return project.get("name", project_id)

    return project_id


def _next_revision(db, drawing_number):
    revisions = []

    for drawing in _get_drawings(db):
        if (
            str(drawing.get("drawing_number", "")).strip().lower()
            == str(drawing_number).strip().lower()
        ):
            revisions.append(
                str(drawing.get("revision", "0"))
            )

    if not revisions:
        return "0"

    numeric = []

    for revision in revisions:
        cleaned = revision.upper().replace("REV", "").strip()

        try:
            numeric.append(int(cleaned))
        except ValueError:
            pass

    if numeric:
        return str(max(numeric) + 1)

    return "0"


def _drawing_exists(db, project_id, drawing_number, exclude_id=None):
    for drawing in _get_drawings(db):

        if (
            str(drawing.get("project_id")) == str(project_id)
            and str(drawing.get("drawing_number", "")).strip().lower()
            == str(drawing_number).strip().lower()
            and str(drawing.get("id")) != str(exclude_id)
        ):
            return True

    return False


def _status_badge(status):
    if status == "Approved":
        st.success(status, icon="✓")

    elif status == "Issued for Construction":
        st.success(status, icon="🏗️")

    elif status == "For Approval":
        st.warning(status, icon="!")

    elif status == "For Review":
        st.info(status, icon="◌")

    elif status == "Superseded":
        st.error(status, icon="↗")

    else:
        st.caption(status)


def _render_drawing_card(db, drawing):

    drawing_id = drawing.get("id", "")
    project_id = drawing.get("project_id", "")
    drawing_number = drawing.get(
        "drawing_number",
        "N/A",
    )

    title = drawing.get(
        "title",
        "Untitled Drawing",
    )

    discipline = drawing.get(
        "discipline",
        "Other",
    )

    drawing_type = drawing.get(
        "drawing_type",
        "Other",
    )

    revision = drawing.get(
        "revision",
        "0",
    )

    status = drawing.get(
        "status",
        "Draft",
    )

    with st.container(border=True):

        top_left, top_right = st.columns(
            [4, 1]
        )

        with top_left:

            st.markdown(
                f"### {drawing_number} — {title}"
            )

            st.caption(
                f"{_project_name(db, project_id)} "
                f"• {discipline} • {drawing_type}"
            )

        with top_right:
            _status_badge(status)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Revision**")
            st.write(f"Rev {revision}")

        with col2:
            st.markdown("**Issue Date**")
            st.write(
                drawing.get(
                    "issue_date",
                    "Not issued",
                )
            )

        with col3:
            st.markdown("**Prepared By**")
            st.write(
                drawing.get(
                    "prepared_by",
                    "Not assigned",
                )
            )

        with col4:
            st.markdown("**Checked By**")
            st.write(
                drawing.get(
                    "checked_by",
                    "Not assigned",
                )
            )

        with st.expander("Drawing Details"):

            st.markdown(
                f"**Project:** "
                f"{_project_name(db, project_id)}"
            )

            st.markdown(
                f"**Project ID:** {project_id}"
            )

            st.markdown(
                f"**Drawing Type:** {drawing_type}"
            )

            st.markdown(
                f"**Approved By:** "
                f"{drawing.get('approved_by', 'Not assigned')}"
            )

            st.markdown(
                f"**Created:** "
                f"{drawing.get('created_at', '')}"
            )

            notes = drawing.get(
                "notes",
                "",
            )

            if notes:
                st.markdown(
                    f"**Notes:** {notes}"
                )

        edit_col, revision_col, delete_col = st.columns(3)

        with edit_col:

            if st.button(
                "Edit",
                key=f"edit_drawing_{drawing_id}",
                use_container_width=True,
            ):
                st.session_state[
                    "editing_drawing_id"
                ] = drawing_id

                st.rerun()

        with revision_col:

            if st.button(
                "New Revision",
                key=f"revision_drawing_{drawing_id}",
                use_container_width=True,
            ):
                st.session_state[
                    "revision_drawing_id"
                ] = drawing_id

                st.rerun()

        with delete_col:

            if st.button(
                "Delete",
                key=f"delete_drawing_{drawing_id}",
                use_container_width=True,
            ):
                st.session_state[
                    "delete_drawing_id"
                ] = drawing_id

                st.rerun()


def _render_create_drawing(db):

    projects = _get_projects(db)

    st.subheader("Register Drawing")

    if not projects:

        st.warning(
            "Create a project before registering drawings."
        )

        return

    project_options = {
        _project_name(db, project.get("id")):
            project.get("id")
        for project in projects
    }

    with st.form("create_drawing_form"):

        project_label = st.selectbox(
            "Project *",
            list(project_options.keys()),
        )

        project_id = project_options[
            project_label
        ]

        col1, col2 = st.columns(2)

        with col1:

            drawing_number = st.text_input(
                "Drawing Number *",
                placeholder="A-101",
            )

            title = st.text_input(
                "Drawing Title *",
                placeholder="Ground Floor Plan",
            )

            discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
            )

            drawing_type = st.selectbox(
                "Drawing Type",
                DRAWING_TYPES,
            )

            revision = st.text_input(
                "Revision",
                value="0",
            )

        with col2:

            status = st.selectbox(
                "Status",
                DRAWING_STATUSES,
                index=1,
            )

            issue_date = st.date_input(
                "Issue Date",
                value=date.today(),
            )

            prepared_by = st.text_input(
                "Prepared By",
            )

            checked_by = st.text_input(
                "Checked By",
            )

            approved_by = st.text_input(
                "Approved By",
            )

        notes = st.text_area(
            "Notes",
            height=100,
        )

        submitted = st.form_submit_button(
            "Register Drawing",
            use_container_width=True,
        )

    if not submitted:
        return

    drawing_number = drawing_number.strip()
    title = title.strip()

    if not drawing_number:
        st.error(
            "Drawing number is required."
        )
        return

    if not title:
        st.error(
            "Drawing title is required."
        )
        return

    if _drawing_exists(
        db,
        project_id,
        drawing_number,
    ):
        st.error(
            f"Drawing {drawing_number} already exists "
            f"for this project."
        )
        return

    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):
        created_by = user.get(
            "username",
            "System",
        )
    else:
        created_by = str(
            user or "System"
        )

    drawing = {
        "id": (
            f"DRW-{project_id}-"
            f"{drawing_number}-REV{revision}"
        ),
        "project_id": project_id,
        "drawing_number": drawing_number,
        "title": title,
        "discipline": discipline,
        "drawing_type": drawing_type,
        "revision": revision.strip() or "0",
        "status": status,
        "issue_date": str(issue_date),
        "prepared_by": prepared_by.strip(),
        "checked_by": checked_by.strip(),
        "approved_by": approved_by.strip(),
        "notes": notes.strip(),
        "created_at": str(date.today()),
        "created_by": created_by,
    }

    add_record(
        db,
        "drawings",
        drawing,
    )

    st.success(
        f"Drawing {drawing_number} registered."
    )

    st.rerun()


def _render_edit_drawing(db, drawing):

    projects = _get_projects(db)

    st.subheader(
        f"Edit Drawing: "
        f"{drawing.get('drawing_number', '')}"
    )

    project_options = {
        _project_name(db, project.get("id")):
            project.get("id")
        for project in projects
    }

    current_project = drawing.get(
        "project_id"
    )

    project_labels = list(
        project_options.keys()
    )

    current_label = next(
        (
            label
            for label, project_id
            in project_options.items()
            if str(project_id)
            == str(current_project)
        ),
        project_labels[0]
        if project_labels
        else None,
    )

    with st.form(
        f"edit_drawing_form_{drawing.get('id')}"
    ):

        project_label = st.selectbox(
            "Project",
            project_labels,
            index=(
                project_labels.index(
                    current_label
                )
                if current_label in project_labels
                else 0
            ),
        )

        project_id = project_options[
            project_label
        ]

        col1, col2 = st.columns(2)

        with col1:

            drawing_number = st.text_input(
                "Drawing Number",
                value=drawing.get(
                    "drawing_number",
                    "",
                ),
            )

            title = st.text_input(
                "Drawing Title",
                value=drawing.get(
                    "title",
                    "",
                ),
            )

            discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
                index=(
                    DISCIPLINES.index(
                        drawing.get(
                            "discipline",
                            DISCIPLINES[0],
                        )
                    )
                    if drawing.get("discipline")
                    in DISCIPLINES
                    else 0
                ),
            )

            drawing_type = st.selectbox(
                "Drawing Type",
                DRAWING_TYPES,
                index=(
                    DRAWING_TYPES.index(
                        drawing.get(
                            "drawing_type",
                            DRAWING_TYPES[0],
                        )
                    )
                    if drawing.get("drawing_type")
                    in DRAWING_TYPES
                    else 0
                ),
            )

        with col2:

            revision = st.text_input(
                "Revision",
                value=str(
                    drawing.get(
                        "revision",
                        "0",
                    )
                ),
            )

            status = st.selectbox(
                "Status",
                DRAWING_STATUSES,
                index=(
                    DRAWING_STATUSES.index(
                        drawing.get(
                            "status",
                            DRAWING_STATUSES[0],
                        )
                    )
                    if drawing.get("status")
                    in DRAWING_STATUSES
                    else 0
                ),
            )

            try:
                existing_date = date.fromisoformat(
                    str(
                        drawing.get(
                            "issue_date",
                            date.today(),
                        )
                    )
                )
            except ValueError:
                existing_date = date.today()

            issue_date = st.date_input(
                "Issue Date",
                value=existing_date,
            )

            prepared_by = st.text_input(
                "Prepared By",
                value=drawing.get(
                    "prepared_by",
                    "",
                ),
            )

            checked_by = st.text_input(
                "Checked By",
                value=drawing.get(
                    "checked_by",
                    "",
                ),
            )

            approved_by = st.text_input(
                "Approved By",
                value=drawing.get(
                    "approved_by",
                    "",
                ),
            )

        notes = st.text_area(
            "Notes",
            value=drawing.get(
                "notes",
                "",
            ),
            height=100,
        )

        save_col, cancel_col = st.columns(2)

        with save_col:

            save_changes = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
            )

        with cancel_col:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancel:

        st.session_state.pop(
            "editing_drawing_id",
            None,
        )

        st.rerun()

    if not save_changes:
        return

    drawing_number = drawing_number.strip()
    title = title.strip()

    if not drawing_number or not title:

        st.error(
            "Drawing number and title are required."
        )

        return

    if _drawing_exists(
        db,
        project_id,
        drawing_number,
        exclude_id=drawing.get("id"),
    ):

        st.error(
            "Another drawing with this number "
            "already exists in the selected project."
        )

        return

    updates = {
        "project_id": project_id,
        "drawing_number": drawing_number,
        "title": title,
        "discipline": discipline,
        "drawing_type": drawing_type,
        "revision": revision.strip() or "0",
        "status": status,
        "issue_date": str(issue_date),
        "prepared_by": prepared_by.strip(),
        "checked_by": checked_by.strip(),
        "approved_by": approved_by.strip(),
        "notes": notes.strip(),
    }

    update_record(
        db,
        "drawings",
        drawing.get("id"),
        updates,
    )

    st.session_state.pop(
        "editing_drawing_id",
        None,
    )

    st.success(
        "Drawing updated successfully."
    )

    st.rerun()


def _render_new_revision(db, drawing):

    st.subheader(
        f"New Revision: "
        f"{drawing.get('drawing_number', '')}"
    )

    current_revision = str(
        drawing.get(
            "revision",
            "0",
        )
    )

    next_revision = _next_revision(
        db,
        drawing.get(
            "drawing_number",
            "",
        ),
    )

    st.info(
        f"Current revision: Rev {current_revision}  "
        f"→  Proposed revision: Rev {next_revision}"
    )

    with st.form(
        f"revision_form_{drawing.get('id')}"
    ):

        revision = st.text_input(
            "New Revision",
            value=next_revision,
        )

        status = st.selectbox(
            "Revision Status",
            DRAWING_STATUSES,
            index=1,
        )

        issue_date = st.date_input(
            "Issue Date",
            value=date.today(),
        )

        prepared_by = st.text_input(
            "Prepared By",
            value=drawing.get(
                "prepared_by",
                "",
            ),
        )

        checked_by = st.text_input(
            "Checked By",
            value=drawing.get(
                "checked_by",
                "",
            ),
        )

        notes = st.text_area(
            "Revision Notes",
            placeholder=(
                "Describe the changes made in this revision."
            ),
        )

        create_revision = st.form_submit_button(
            "Create Revision",
            use_container_width=True,
        )

    if not create_revision:
        return

    revision = revision.strip()

    if not revision:

        st.error(
            "Revision number is required."
        )

        return

    existing = _drawing_exists(
        db,
        drawing.get("project_id"),
        drawing.get("drawing_number"),
    )

    # Existing record is expected, so create a new
    # revision record with its own ID.
    new_drawing = dict(drawing)

    new_drawing["id"] = (
        f"DRW-{drawing.get('project_id')}-"
        f"{drawing.get('drawing_number')}-"
        f"REV{revision}"
    )

    new_drawing["revision"] = revision
    new_drawing["status"] = status
    new_drawing["issue_date"] = str(issue_date)
    new_drawing["prepared_by"] = prepared_by.strip()
    new_drawing["checked_by"] = checked_by.strip()
    new_drawing["approved_by"] = ""
    new_drawing["notes"] = notes.strip()
    new_drawing["created_at"] = str(date.today())

    # Prevent duplicate revision IDs.
    duplicate_revision = any(
        str(item.get("id"))
        == str(new_drawing["id"])
        for item in _get_drawings(db)
    )

    if duplicate_revision:

        st.error(
            f"Revision {revision} already exists."
        )

        return

    add_record(
        db,
        "drawings",
        new_drawing,
    )

    st.session_state.pop(
        "revision_drawing_id",
        None,
    )

    st.success(
        f"Revision {revision} created."
    )

    st.rerun()


def _render_delete_confirmation(db, drawing):

    st.warning(
        f"Delete drawing "
        f"**{drawing.get('drawing_number', '')} "
        f"- Rev {drawing.get('revision', '0')}**?"
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:

        if st.button(
            "Delete Drawing",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "drawings",
                drawing.get("id"),
            )

            st.session_state.pop(
                "delete_drawing_id",
                None,
            )

            st.success(
                "Drawing deleted."
            )

            st.rerun()

    with cancel_col:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_drawing_id",
                None,
            )

            st.rerun()


def render_drawings_module(db):

    projects = _get_projects(db)
    drawings = _get_drawings(db)

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                Drawing Repository
            </div>
            <div class="module-subtitle">
                Controlled repository for project drawings,
                revisions and technical documents.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI AREA
    # ========================================================

    total_drawings = len(drawings)

    approved = sum(
        1
        for drawing in drawings
        if drawing.get("status") == "Approved"
    )

    for_review = sum(
        1
        for drawing in drawings
        if drawing.get("status") == "For Review"
    )

    ifc = sum(
        1
        for drawing in drawings
        if drawing.get("status")
        == "Issued for Construction"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Drawings",
            total_drawings,
        )

    with col2:
        st.metric(
            "Approved",
            approved,
        )

    with col3:
        st.metric(
            "For Review",
            for_review,
        )

    with col4:
        st.metric(
            "Issued for Construction",
            ifc,
        )

    st.divider()

    # ========================================================
    # EDIT
    # ========================================================

    editing_id = st.session_state.get(
        "editing_drawing_id"
    )

    if editing_id:

        drawing = next(
            (
                item
                for item in drawings
                if str(item.get("id"))
                == str(editing_id)
            ),
            None,
        )

        if drawing:

            _render_edit_drawing(
                db,
                drawing,
            )

            st.divider()

    # ========================================================
    # NEW REVISION
    # ========================================================

    revision_id = st.session_state.get(
        "revision_drawing_id"
    )

    if revision_id:

        drawing = next(
            (
                item
                for item in drawings
                if str(item.get("id"))
                == str(revision_id)
            ),
            None,
        )

        if drawing:

            _render_new_revision(
                db,
                drawing,
            )

            st.divider()

    # ========================================================
    # DELETE
    # ========================================================

    delete_id = st.session_state.get(
        "delete_drawing_id"
    )

    if delete_id:

        drawing = next(
            (
                item
                for item in drawings
                if str(item.get("id"))
                == str(delete_id)
            ),
            None,
        )

        if drawing:

            _render_delete_confirmation(
                db,
                drawing,
            )

            st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_repository, tab_register = st.tabs(
        [
            "Drawing Repository",
            "Register Drawing",
        ]
    )

    # ========================================================
    # REPOSITORY
    # ========================================================

    with tab_repository:

        if not drawings:

            st.info(
                "No drawings have been registered yet."
            )

        else:

            search = st.text_input(
                "Search Drawings",
                placeholder=(
                    "Drawing number, title, discipline "
                    "or project..."
                ),
            )

            filter_col1, filter_col2, filter_col3 = st.columns(3)

            with filter_col1:

                project_filter = st.selectbox(
                    "Project",
                    ["All"]
                    + [
                        project.get("id")
                        for project in projects
                    ],
                )

            with filter_col2:

                discipline_filter = st.selectbox(
                    "Discipline",
                    ["All"] + DISCIPLINES,
                )

            with filter_col3:

                status_filter = st.selectbox(
                    "Status",
                    ["All"] + DRAWING_STATUSES,
                )

            search_term = (
                search.strip().lower()
            )

            filtered = []

            for drawing in drawings:

                searchable = " ".join(
                    [
                        str(
                            drawing.get(
                                "drawing_number",
                                "",
                            )
                        ),
                        str(
                            drawing.get(
                                "title",
                                "",
                            )
                        ),
                        str(
                            drawing.get(
                                "discipline",
                                "",
                            )
                        ),
                        str(
                            drawing.get(
                                "drawing_type",
                                "",
                            )
                        ),
                        str(
                            drawing.get(
                                "project_id",
                                "",
                            )
                        ),
                        _project_name(
                            db,
                            drawing.get(
                                "project_id",
                                "",
                            ),
                        ),
                    ]
                ).lower()

                if (
                    search_term
                    and search_term not in searchable
                ):
                    continue

                if (
                    project_filter != "All"
                    and str(
                        drawing.get(
                            "project_id"
                        )
                    )
                    != str(project_filter)
                ):
                    continue

                if (
                    discipline_filter != "All"
                    and drawing.get(
                        "discipline"
                    )
                    != discipline_filter
                ):
                    continue

                if (
                    status_filter != "All"
                    and drawing.get(
                        "status"
                    )
                    != status_filter
                ):
                    continue

                filtered.append(
                    drawing
                )

            st.caption(
                f"Showing {len(filtered)} "
                f"of {len(drawings)} drawings"
            )

            for drawing in filtered:

                _render_drawing_card(
                    db,
                    drawing,
                )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        _render_create_drawing(
            db
        )