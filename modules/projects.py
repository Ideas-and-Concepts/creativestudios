"""
Creative Studios
Project Directory Module

Central project management workspace for the AEC platform.

Projects are the parent records for:
- Drawings
- BOQ
- RFIs
- Approvals
- Site Logs
"""

from datetime import date

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    save_memory,
    update_record,
)


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_TYPES = [
    "Commercial",
    "Residential",
    "Industrial",
    "Civic / Infrastructure",
    "Mixed-Use",
    "Hospitality",
    "Healthcare",
    "Education",
    "Other",
]

PROJECT_PHASES = [
    "Concept Design",
    "Schematic Design",
    "Design Development",
    "Construction Documents",
    "Bidding & Negotiation",
    "Construction Administration",
    "Construction",
    "Practical Completion",
    "Closed",
]

PROJECT_STATUSES = [
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Cancelled",
]


# ============================================================
# HELPERS
# ============================================================

def _safe_number(value, default=0.0):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def _project_exists(db, project_id, exclude_id=None):
    project_id = project_id.strip().lower()

    for project in get_collection(db, "projects"):
        current_id = str(project.get("id", "")).strip().lower()

        if current_id == project_id and current_id != str(
            exclude_id or ""
        ).strip().lower():
            return True

    return False


def _format_currency(value):
    return f"${_safe_number(value):,.2f}"


def _get_status_count(projects, status):
    return sum(
        1
        for project in projects
        if project.get("status", "Active") == status
    )


def _project_label(project):
    return (
        f"{project.get('id', 'N/A')} • "
        f"{project.get('name', 'Unnamed Project')}"
    )


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(db, project):

    project_id = project.get("id", "N/A")
    project_name = project.get("name", "Unnamed Project")
    project_type = project.get("type", "Other")
    phase = project.get("phase", "Concept Design")
    status = project.get("status", "Active")

    budget = _safe_number(
        project.get("budget", 0)
    )

    client = project.get(
        "client",
        "Not specified",
    )

    location = project.get(
        "location",
        "Not specified",
    )

    manager = project.get(
        "project_manager",
        "Not assigned",
    )

    with st.container(border=True):

        header_col, status_col = st.columns(
            [4, 1]
        )

        with header_col:

            st.markdown(
                f"### {project_name}"
            )

            st.caption(
                f"{project_id} • {project_type}"
            )

        with status_col:

            if status == "Active":
                st.success(
                    status,
                    icon="●",
                )

            elif status == "Completed":
                st.info(
                    status,
                    icon="✓",
                )

            elif status == "On Hold":
                st.warning(
                    status,
                    icon="Ⅱ",
                )

            elif status == "Cancelled":
                st.error(
                    status,
                    icon="×",
                )

            else:
                st.info(status)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown("**Phase**")
            st.write(phase)

        with col2:
            st.markdown("**Client**")
            st.write(client)

        with col3:
            st.markdown("**Location**")
            st.write(location)

        with col4:
            st.markdown("**Budget**")
            st.write(_format_currency(budget))

        st.markdown(
            f"**Project Manager:** {manager}"
        )

        description = project.get(
            "description",
            "",
        )

        if description:
            st.markdown(
                f"**Scope:** {description}"
            )

        with st.expander(
            "Project Details"
        ):

            detail1, detail2 = st.columns(2)

            with detail1:

                st.markdown(
                    f"**Start Date:** "
                    f"{project.get('start_date', 'Not specified')}"
                )

                st.markdown(
                    f"**Target Completion:** "
                    f"{project.get('target_completion', 'Not specified')}"
                )

                st.markdown(
                    f"**Lead Architect:** "
                    f"{project.get('lead_architect', 'Not assigned')}"
                )

            with detail2:

                st.markdown(
                    f"**Contract Value:** "
                    f"{_format_currency(project.get('contract_value', 0))}"
                )

                st.markdown(
                    f"**Created:** "
                    f"{project.get('created_at', 'Unknown')}"
                )

                st.markdown(
                    f"**Created By:** "
                    f"{project.get('created_by', 'System')}"
                )

        edit_col, delete_col = st.columns(
            2
        )

        with edit_col:

            if st.button(
                "Edit Project",
                key=f"edit_{project_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "editing_project_id"
                ] = project_id

                st.rerun()

        with delete_col:

            if st.button(
                "Delete Project",
                key=f"delete_{project_id}",
                use_container_width=True,
            ):

                st.session_state[
                    "delete_project_id"
                ] = project_id

                st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def _render_create_project(db):

    st.subheader(
        "Register New AEC Project"
    )

    st.caption(
        "Create the master project record that will "
        "connect the project's drawings, BOQ, RFIs, "
        "approvals and site records."
    )

    with st.form(
        "create_project_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_id = st.text_input(
                "Project ID *",
                placeholder="PRJ-002",
            )

            project_name = st.text_input(
                "Project Name *",
                placeholder="e.g. Riverside Office Development",
            )

            project_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES,
            )

            client = st.text_input(
                "Client / Developer",
                placeholder="Client company or organization",
            )

            location = st.text_input(
                "Project Location",
                placeholder="City / District / Country",
            )

            project_manager = st.text_input(
                "Project Manager",
            )

        with col2:

            status = st.selectbox(
                "Project Status",
                PROJECT_STATUSES,
                index=1,
            )

            phase = st.selectbox(
                "Lifecycle Phase",
                PROJECT_PHASES,
            )

            contract_value = st.number_input(
                "Contract Value",
                min_value=0.0,
                value=0.0,
                step=10000.0,
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=0.0,
                step=10000.0,
            )

            start_date = st.date_input(
                "Project Start Date",
                value=date.today(),
            )

            target_completion = st.date_input(
                "Target Completion Date",
                value=date.today(),
            )

            lead_architect = st.text_input(
                "Lead Architect / Consultant",
            )

        description = st.text_area(
            "Project Scope & Description",
            placeholder=(
                "Provide a concise description of the "
                "project scope, objectives and major works."
            ),
            height=120,
        )

        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if not submitted:
        return

    project_id = project_id.strip()
    project_name = project_name.strip()

    if not project_id:
        st.error(
            "Project ID is required."
        )
        return

    if not project_name:
        st.error(
            "Project Name is required."
        )
        return

    if _project_exists(
        db,
        project_id,
    ):
        st.error(
            f"Project ID '{project_id}' already exists."
        )
        return

    if target_completion < start_date:
        st.error(
            "Target completion date cannot be "
            "before the project start date."
        )
        return

    current_user = st.session_state.get(
        "user"
    )

    if isinstance(current_user, dict):
        created_by = current_user.get(
            "username",
            "System",
        )
    else:
        created_by = str(
            current_user or "System"
        )

    new_project = {
        "id": project_id,
        "name": project_name,
        "type": project_type,
        "phase": phase,
        "status": status,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": project_manager.strip(),
        "lead_architect": lead_architect.strip(),
        "contract_value": contract_value,
        "budget": budget,
        "start_date": str(start_date),
        "target_completion": str(
            target_completion
        ),
        "created_at": str(date.today()),
        "created_by": created_by,
        "description": description.strip(),
    }

    add_record(
        db,
        "projects",
        new_project,
    )

    st.success(
        f"Project '{project_name}' has been created."
    )

    st.rerun()


# ============================================================
# EDIT PROJECT
# ============================================================

def _render_edit_project(db, project):

    st.subheader(
        f"Edit Project: {project.get('name', '')}"
    )

    with st.form(
        f"edit_project_{project.get('id')}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_name = st.text_input(
                "Project Name",
                value=project.get(
                    "name",
                    "",
                ),
            )

            project_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES,
                index=(
                    PROJECT_TYPES.index(
                        project.get(
                            "type",
                            PROJECT_TYPES[0],
                        )
                    )
                    if project.get("type")
                    in PROJECT_TYPES
                    else 0
                ),
            )

            client = st.text_input(
                "Client / Developer",
                value=project.get(
                    "client",
                    "",
                ),
            )

            location = st.text_input(
                "Project Location",
                value=project.get(
                    "location",
                    "",
                ),
            )

            project_manager = st.text_input(
                "Project Manager",
                value=project.get(
                    "project_manager",
                    "",
                ),
            )

        with col2:

            status = st.selectbox(
                "Project Status",
                PROJECT_STATUSES,
                index=(
                    PROJECT_STATUSES.index(
                        project.get(
                            "status",
                            "Active",
                        )
                    )
                    if project.get("status")
                    in PROJECT_STATUSES
                    else 1
                ),
            )

            phase = st.selectbox(
                "Lifecycle Phase",
                PROJECT_PHASES,
                index=(
                    PROJECT_PHASES.index(
                        project.get(
                            "phase",
                            PROJECT_PHASES[0],
                        )
                    )
                    if project.get("phase")
                    in PROJECT_PHASES
                    else 0
                ),
            )

            contract_value = st.number_input(
                "Contract Value",
                min_value=0.0,
                value=_safe_number(
                    project.get(
                        "contract_value",
                        0,
                    )
                ),
                step=10000.0,
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=_safe_number(
                    project.get(
                        "budget",
                        0,
                    )
                ),
                step=10000.0,
            )

            try:
                existing_start = date.fromisoformat(
                    str(
                        project.get(
                            "start_date",
                            date.today(),
                        )
                    )
                )
            except ValueError:
                existing_start = date.today()

            try:
                existing_completion = date.fromisoformat(
                    str(
                        project.get(
                            "target_completion",
                            date.today(),
                        )
                    )
                )
            except ValueError:
                existing_completion = date.today()

            start_date = st.date_input(
                "Project Start Date",
                value=existing_start,
            )

            target_completion = st.date_input(
                "Target Completion Date",
                value=existing_completion,
            )

            lead_architect = st.text_input(
                "Lead Architect / Consultant",
                value=project.get(
                    "lead_architect",
                    "",
                ),
            )

        description = st.text_area(
            "Project Scope & Description",
            value=project.get(
                "description",
                "",
            ),
            height=120,
        )

        save_col, cancel_col = st.columns(2)

        with save_col:
            save_changes = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
            )

        with cancel_col:
            cancel_edit = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancel_edit:
        st.session_state.pop(
            "editing_project_id",
            None,
        )
        st.rerun()

    if not save_changes:
        return

    if not project_name.strip():
        st.error(
            "Project Name is required."
        )
        return

    if target_completion < start_date:
        st.error(
            "Target completion date cannot be "
            "before the project start date."
        )
        return

    updates = {
        "name": project_name.strip(),
        "type": project_type,
        "phase": phase,
        "status": status,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": project_manager.strip(),
        "lead_architect": lead_architect.strip(),
        "contract_value": contract_value,
        "budget": budget,
        "start_date": str(start_date),
        "target_completion": str(
            target_completion
        ),
        "description": description.strip(),
    }

    update_record(
        db,
        "projects",
        project.get("id"),
        updates,
    )

    st.session_state.pop(
        "editing_project_id",
        None,
    )

    st.success(
        "Project updated successfully."
    )

    st.rerun()


# ============================================================
# DELETE CONFIRMATION
# ============================================================

def _render_delete_confirmation(db, project):

    st.warning(
        f"Are you sure you want to delete "
        f"**{project.get('name', 'this project')}**?"
    )

    st.caption(
        "This removes the project record from the "
        "current database. Related records will be "
        "handled separately as the platform gains "
        "referential controls."
    )

    confirm_col, cancel_col = st.columns(2)

    with confirm_col:

        if st.button(
            "Yes, Delete Project",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "projects",
                project.get("id"),
            )

            st.session_state.pop(
                "delete_project_id",
                None,
            )

            st.success(
                "Project deleted successfully."
            )

            st.rerun()

    with cancel_col:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_project_id",
                None,
            )

            st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_projects_module(db):

    projects = get_collection(
        db,
        "projects",
    )

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                Project Directory
            </div>
            <div class="module-subtitle">
                Central project workspace for architectural,
                engineering and construction activities.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Dashboard KPIs
    # --------------------------------------------------------

    total_projects = len(projects)

    active_projects = _get_status_count(
        projects,
        "Active",
    )

    planning_projects = _get_status_count(
        projects,
        "Planning",
    )

    completed_projects = _get_status_count(
        projects,
        "Completed",
    )

    total_budget = sum(
        _safe_number(
            project.get("budget", 0)
        )
        for project in projects
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Projects",
            total_projects,
        )

    with col2:
        st.metric(
            "Active",
            active_projects,
        )

    with col3:
        st.metric(
            "Planning",
            planning_projects,
        )

    with col4:
        st.metric(
            "Completed",
            completed_projects,
        )

    with col5:
        st.metric(
            "Portfolio Budget",
            _format_currency(
                total_budget
            ),
        )

    st.divider()

    # --------------------------------------------------------
    # Edit Mode
    # --------------------------------------------------------

    editing_id = st.session_state.get(
        "editing_project_id"
    )

    if editing_id:

        project = next(
            (
                p
                for p in projects
                if str(p.get("id"))
                == str(editing_id)
            ),
            None,
        )

        if project:

            _render_edit_project(
                db,
                project,
            )

            st.divider()

        else:

            st.session_state.pop(
                "editing_project_id",
                None,
            )

    # --------------------------------------------------------
    # Delete Confirmation
    # --------------------------------------------------------

    deleting_id = st.session_state.get(
        "delete_project_id"
    )

    if deleting_id:

        project = next(
            (
                p
                for p in projects
                if str(p.get("id"))
                == str(deleting_id)
            ),
            None,
        )

        if project:

            _render_delete_confirmation(
                db,
                project,
            )

            st.divider()

    # --------------------------------------------------------
    # Navigation Tabs
    # --------------------------------------------------------

    tab_projects, tab_create = st.tabs(
        [
            "Project Portfolio",
            "Create New Project",
        ]
    )

    # --------------------------------------------------------
    # PROJECT PORTFOLIO
    # --------------------------------------------------------

    with tab_projects:

        if not projects:

            st.info(
                "No projects have been registered yet. "
                "Use 'Create New Project' to create "
                "the first project."
            )

        else:

            search = st.text_input(
                "Search Projects",
                placeholder=(
                    "Search by project ID, name, "
                    "client, location or manager..."
                ),
            )

            filter_col1, filter_col2 = st.columns(2)

            with filter_col1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"] + PROJECT_STATUSES,
                )

            with filter_col2:

                type_filter = st.selectbox(
                    "Project Type",
                    ["All"] + PROJECT_TYPES,
                )

            filtered_projects = []

            search_term = (
                search.strip().lower()
            )

            for project in projects:

                searchable = " ".join(
                    [
                        str(
                            project.get(
                                "id",
                                "",
                            )
                        ),
                        str(
                            project.get(
                                "name",
                                "",
                            )
                        ),
                        str(
                            project.get(
                                "client",
                                "",
                            )
                        ),
                        str(
                            project.get(
                                "location",
                                "",
                            )
                        ),
                        str(
                            project.get(
                                "project_manager",
                                "",
                            )
                        ),
                    ]
                ).lower()

                if (
                    search_term
                    and search_term not in searchable
                ):
                    continue

                if (
                    status_filter != "All"
                    and project.get(
                        "status",
                        "Active",
                    )
                    != status_filter
                ):
                    continue

                if (
                    type_filter != "All"
                    and project.get(
                        "type",
                        "Other",
                    )
                    != type_filter
                ):
                    continue

                filtered_projects.append(
                    project
                )

            st.caption(
                f"Showing {len(filtered_projects)} "
                f"of {len(projects)} projects"
            )

            for project in filtered_projects:

                _render_project_card(
                    db,
                    project,
                )

    # --------------------------------------------------------
    # CREATE PROJECT
    # --------------------------------------------------------

    with tab_create:

        _render_create_project(
            db
        )