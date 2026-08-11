"""
Creative Studios
Project Directory module.

This is a clean replacement for the old projects.py.

Important:
No st.success/st.warning/st.error calls with custom icons are used.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    update_record,
)


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:

        return default

    return str(
        value
    )


def safe_number(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None:
            return default

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def money(
    value: Any,
) -> str:

    amount = safe_number(
        value
    )

    return (
        f"${amount:,.2f}"
    )


def clean_status(
    value: Any,
) -> str:

    status = safe_text(
        value,
        "Active",
    ).strip()

    if not status:

        return "Active"

    return status


def status_class(
    status: str,
) -> str:

    normalized = (
        status.lower()
        .replace(
            " ",
            "-",
        )
    )

    if normalized == "active":

        return "status-active"

    if normalized == "planning":

        return "status-planning"

    if normalized == "completed":

        return "status-completed"

    if normalized in {
        "on-hold",
        "on_hold",
        "hold",
    }:

        return "status-on-hold"

    return "status-planning"


# ============================================================
# PAGE HEADER
# ============================================================

def render_header() -> None:

    st.markdown(
        """
        <div style="
            color:#FFFFFF;
            font-size:30px;
            font-weight:900;
            letter-spacing:-1px;
        ">
            Project Directory
        </div>

        <div style="
            color:#64748B;
            font-size:13px;
            margin-top:5px;
            margin-bottom:25px;
        ">
            Central project workspace for architectural,
            engineering and construction activities.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# STATISTICS
# ============================================================

def render_statistics(
    projects: list[dict],
) -> None:

    total = len(
        projects
    )

    active = sum(
        1
        for project in projects
        if clean_status(
            project.get(
                "status"
            )
        ).lower()
        == "active"
    )

    planning = sum(
        1
        for project in projects
        if clean_status(
            project.get(
                "status"
            )
        ).lower()
        == "planning"
    )

    completed = sum(
        1
        for project in projects
        if clean_status(
            project.get(
                "status"
            )
        ).lower()
        == "completed"
    )

    budget = sum(
        safe_number(
            project.get(
                "estimated_budget"
            )
        )
        for project in projects
    )

    columns = st.columns(
        5
    )

    columns[0].metric(
        "Total Projects",
        total,
    )

    columns[1].metric(
        "Active",
        active,
    )

    columns[2].metric(
        "Planning",
        planning,
    )

    columns[3].metric(
        "Completed",
        completed,
    )

    columns[4].metric(
        "Portfolio Budget",
        money(
            budget
        ),
    )


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(
    db: dict,
    project: dict,
) -> None:

    project_name = safe_text(
        project.get(
            "name"
        ),
        "Untitled Project",
    )

    project_id = safe_text(
        project.get(
            "project_id"
        ),
        "N/A",
    )

    project_type = safe_text(
        project.get(
            "project_type"
        ),
        "General",
    )

    client = safe_text(
        project.get(
            "client"
        ),
        "Not specified",
    )

    location = safe_text(
        project.get(
            "location"
        ),
        "Not specified",
    )

    manager = safe_text(
        project.get(
            "manager"
        ),
        "Not assigned",
    )

    status = clean_status(
        project.get(
            "status"
        )
    )

    budget = money(
        project.get(
            "estimated_budget"
        )
    )

    badge_class = status_class(
        status
    )

    st.markdown(
        f"""
        <div class="project-card">

            <div style="
                display:flex;
                justify-content:space-between;
                gap:20px;
                align-items:flex-start;
            ">

                <div>

                    <div class="project-title">
                        {project_name}
                    </div>

                    <div class="project-meta">
                        {project_id}
                        &nbsp;•&nbsp;
                        {project_type}
                    </div>

                </div>

                <span class="
                    status-badge
                    {badge_class}
                ">
                    {status}
                </span>

            </div>

            <div style="
                margin-top:18px;
                display:grid;
                grid-template-columns:
                    repeat(4, 1fr);
                gap:15px;
            ">

                <div>
                    <div style="
                        color:#475569;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Client
                    </div>

                    <div style="
                        color:#CBD5E1;
                        font-size:12px;
                        margin-top:4px;
                    ">
                        {client}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Location
                    </div>

                    <div style="
                        color:#CBD5E1;
                        font-size:12px;
                        margin-top:4px;
                    ">
                        {location}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Manager
                    </div>

                    <div style="
                        color:#CBD5E1;
                        font-size:12px;
                        margin-top:4px;
                    ">
                        {manager}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:10px;
                        text-transform:uppercase;
                    ">
                        Budget
                    </div>

                    <div style="
                        color:#60A5FA;
                        font-size:12px;
                        font-weight:800;
                        margin-top:4px;
                    ">
                        {budget}
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='height:4px'></div>",
        unsafe_allow_html=True,
    )

    edit_col, delete_col, spacer = st.columns(
        [1, 1, 5]
    )

    project_db_id = project.get(
        "id"
    )

    if edit_col.button(
        "Edit",
        key=f"edit_{project_db_id}",
    ):

        st.session_state[
            "editing_project"
        ] = project_db_id

        st.rerun()

    if delete_col.button(
        "Delete",
        key=f"delete_{project_db_id}",
    ):

        st.session_state[
            "delete_project"
        ] = project_db_id

        st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project_form(
    db: dict,
) -> None:

    st.markdown(
        "### Create New Project"
    )

    with st.form(
        "create_project_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(
            2
        )

        with col1:

            project_id = st.text_input(
                "Project ID",
                placeholder="PRJ-002",
            )

            name = st.text_input(
                "Project Name",
            )

            client = st.text_input(
                "Client",
            )

            location = st.text_input(
                "Location",
            )

        with col2:

            manager = st.text_input(
                "Project Manager",
            )

            project_type = st.selectbox(
                "Project Type",
                [
                    "Commercial",
                    "Residential",
                    "Industrial",
                    "Infrastructure",
                    "Institutional",
                    "Other",
                ],
            )

            status = st.selectbox(
                "Status",
                [
                    "Planning",
                    "Active",
                    "On Hold",
                    "Completed",
                ],
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                step=1000.0,
            )

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if not submitted:

        return

    if not name.strip():

        st.error(
            "Project Name is required."
        )

        return

    if not project_id.strip():

        project_id = (
            f"PRJ-{len(db.get('projects', [])) + 1:03d}"
        )

    record = {
        "project_id":
            project_id.strip(),
        "name":
            name.strip(),
        "client":
            client.strip(),
        "location":
            location.strip(),
        "manager":
            manager.strip(),
        "project_type":
            project_type,
        "status":
            status,
        "estimated_budget":
            budget,
        "description":
            description.strip(),
        "created_at":
            datetime.now().isoformat(),
    }

    add_record(
        db,
        "projects",
        record,
    )

    st.success(
        "Project created successfully."
    )

    st.rerun()


# ============================================================
# EDIT PROJECT
# ============================================================

def edit_project_form(
    db: dict,
    project: dict,
) -> None:

    st.markdown(
        "### Edit Project"
    )

    with st.form(
        f"edit_project_{project.get('id')}"
    ):

        col1, col2 = st.columns(
            2
        )

        with col1:

            project_id = st.text_input(
                "Project ID",
                value=safe_text(
                    project.get(
                        "project_id"
                    )
                ),
            )

            name = st.text_input(
                "Project Name",
                value=safe_text(
                    project.get(
                        "name"
                    )
                ),
            )

            client = st.text_input(
                "Client",
                value=safe_text(
                    project.get(
                        "client"
                    )
                ),
            )

            location = st.text_input(
                "Location",
                value=safe_text(
                    project.get(
                        "location"
                    )
                ),
            )

        with col2:

            manager = st.text_input(
                "Project Manager",
                value=safe_text(
                    project.get(
                        "manager"
                    )
                ),
            )

            project_types = [
                "Commercial",
                "Residential",
                "Industrial",
                "Infrastructure",
                "Institutional",
                "Other",
            ]

            current_type = safe_text(
                project.get(
                    "project_type"
                ),
                "Commercial",
            )

            if current_type not in project_types:

                project_types.append(
                    current_type
                )

            project_type = st.selectbox(
                "Project Type",
                project_types,
                index=project_types.index(
                    current_type
                ),
            )

            statuses = [
                "Planning",
                "Active",
                "On Hold",
                "Completed",
            ]

            current_status = clean_status(
                project.get(
                    "status"
                )
            )

            if current_status not in statuses:

                statuses.append(
                    current_status
                )

            status = st.selectbox(
                "Status",
                statuses,
                index=statuses.index(
                    current_status
                ),
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=safe_number(
                    project.get(
                        "estimated_budget"
                    )
                ),
                step=1000.0,
            )

        description = st.text_area(
            "Description",
            value=safe_text(
                project.get(
                    "description"
                )
            ),
        )

        save_col, cancel_col = st.columns(
            2
        )

        save = save_col.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

        cancel = cancel_col.form_submit_button(
            "Cancel",
            use_container_width=True,
        )

    if cancel:

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.rerun()

    if save:

        if not name.strip():

            st.error(
                "Project Name is required."
            )

            return

        update_record(
            db,
            "projects",
            int(
                project.get(
                    "id"
                )
            ),
            {
                "project_id":
                    project_id.strip(),
                "name":
                    name.strip(),
                "client":
                    client.strip(),
                "location":
                    location.strip(),
                "manager":
                    manager.strip(),
                "project_type":
                    project_type,
                "status":
                    status,
                "estimated_budget":
                    budget,
                "description":
                    description.strip(),
            },
        )

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.success(
            "Project updated successfully."
        )

        st.rerun()


# ============================================================
# DELETE CONFIRMATION
# ============================================================

def render_delete_confirmation(
    db: dict,
    project: dict,
) -> None:

    name = safe_text(
        project.get(
            "name"
        ),
        "this project",
    )

    st.warning(
        f"Delete '{name}'?"
    )

    yes_col, no_col = st.columns(
        2
    )

    if yes_col.button(
        "Delete Project",
        key=f"confirm_delete_{project.get('id')}",
        use_container_width=True,
    ):

        delete_record(
            db,
            "projects",
            int(
                project.get(
                    "id"
                )
            ),
        )

        st.session_state.pop(
            "delete_project",
            None,
        )

        st.success(
            "Project deleted successfully."
        )

        st.rerun()

    if no_col.button(
        "Cancel",
        key=f"cancel_delete_{project.get('id')}",
        use_container_width=True,
    ):

        st.session_state.pop(
            "delete_project",
            None,
        )

        st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_projects_module(
    db: dict,
) -> None:

    if not isinstance(
        db,
        dict,
    ):

        db = {
            "projects": []
        }

    projects = db.get(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):

        projects = []

    projects = [
        project
        for project in projects
        if isinstance(
            project,
            dict,
        )
    ]

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    render_header()

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    render_statistics(
        projects
    )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # CREATE PROJECT
    # --------------------------------------------------------

    with st.expander(
        "Create New Project"
    ):

        create_project_form(
            db
        )

    # --------------------------------------------------------
    # SEARCH / FILTERS
    # --------------------------------------------------------

    st.markdown(
        "### Project Portfolio"
    )

    search = st.text_input(
        "Search Projects",
        placeholder=(
            "Search by project ID, name, "
            "client, location or manager..."
        ),
    )

    col1, col2 = st.columns(
        2
    )

    statuses = sorted(
        {
            clean_status(
                project.get(
                    "status"
                )
            )
            for project in projects
        }
    )

    project_types = sorted(
        {
            safe_text(
                project.get(
                    "project_type"
                ),
                "General",
            )
            for project in projects
        }
    )

    with col1:

        status_filter = st.selectbox(
            "Status",
            ["All"] + statuses,
        )

    with col2:

        type_filter = st.selectbox(
            "Project Type",
            ["All"] + project_types,
        )

    # --------------------------------------------------------
    # FILTER
    # --------------------------------------------------------

    search_lower = search.strip().lower()

    filtered = []

    for project in projects:

        searchable = " ".join(
            [
                safe_text(
                    project.get(
                        "project_id"
                    )
                ),
                safe_text(
                    project.get(
                        "name"
                    )
                ),
                safe_text(
                    project.get(
                        "client"
                    )
                ),
                safe_text(
                    project.get(
                        "location"
                    )
                ),
                safe_text(
                    project.get(
                        "manager"
                    )
                ),
            ]
        ).lower()

        if search_lower and search_lower not in searchable:

            continue

        if (
            status_filter != "All"
            and clean_status(
                project.get(
                    "status"
                )
            )
            != status_filter
        ):

            continue

        if (
            type_filter != "All"
            and safe_text(
                project.get(
                    "project_type"
                ),
                "General",
            )
            != type_filter
        ):

            continue

        filtered.append(
            project
        )

    st.markdown(
        f"""
        <div style="
            color:#64748B;
            font-size:12px;
            margin-top:15px;
            margin-bottom:10px;
        ">
            Showing {len(filtered)}
            of {len(projects)}
            projects
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    editing_id = st.session_state.get(
        "editing_project"
    )

    if editing_id is not None:

        editing_project = next(
            (
                project
                for project in projects
                if project.get(
                    "id"
                )
                == editing_id
            ),
            None,
        )

        if editing_project:

            edit_project_form(
                db,
                editing_project,
            )

            st.divider()

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    deleting_id = st.session_state.get(
        "delete_project"
    )

    if deleting_id is not None:

        deleting_project = next(
            (
                project
                for project in projects
                if project.get(
                    "id"
                )
                == deleting_id
            ),
            None,
        )

        if deleting_project:

            render_delete_confirmation(
                db,
                deleting_project,
            )

            st.divider()

    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    if not filtered:

        st.markdown(
            """
            <div class="project-card">

                <div class="project-title">
                    No Projects Found
                </div>

                <div class="project-meta">
                    Try changing your search or
                    filters, or create a new project.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    for project in filtered:

        render_project_card(
            db,
            project,
        )