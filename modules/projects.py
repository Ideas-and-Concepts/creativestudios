"""
Creative Studios
Project Directory Module

Project management interface for the AEC Workspace.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# HELPERS
# ============================================================

def _safe_number(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        if value is None:
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    return str(value)


def _project_name(
    project: dict,
) -> str:

    return (
        project.get("project_name")
        or project.get("name")
        or "Unnamed Project"
    )


def _project_id(
    project: dict,
) -> str:

    return (
        project.get("project_id")
        or project.get("id")
        or "N/A"
    )


def _project_type(
    project: dict,
) -> str:

    return (
        project.get("project_type")
        or project.get("type")
        or "General"
    )


def _project_status(
    project: dict,
) -> str:

    return (
        project.get("status")
        or "Active"
    )


def _status_class(
    status: str,
) -> str:

    normalized = status.strip().lower()

    if normalized == "active":
        return "status-active"

    if normalized == "planning":
        return "status-planning"

    if normalized == "completed":
        return "status-completed"

    return "status-on-hold"


def _format_currency(
    value: Any,
) -> str:

    amount = _safe_number(value)

    return f"${amount:,.2f}"


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(
    db: dict,
    project: dict,
    project_index: int,
) -> None:

    name = _project_name(project)

    project_id = _project_id(project)

    project_type = _project_type(project)

    status = _project_status(project)

    client = (
        project.get("client_name")
        or project.get("client")
        or "Not specified"
    )

    location = project.get(
        "location",
        "Not specified",
    )

    manager = (
        project.get("project_manager")
        or project.get("manager")
        or "Not assigned"
    )

    budget = (
        project.get("estimated_budget")
        if project.get("estimated_budget") is not None
        else project.get("budget", 0)
    )

    description = project.get(
        "description",
        "",
    )

    css_class = _status_class(
        status
    )

    # --------------------------------------------------------
    # Card
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="project-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:20px;
            ">

                <div>

                    <div class="project-title">
                        {name}
                    </div>

                    <div class="project-meta">
                        {project_id}
                        &nbsp;•&nbsp;
                        {project_type}
                    </div>

                </div>

                <div class="project-status {css_class}">
                    {status}
                </div>

            </div>

            <div style="
                display:grid;
                grid-template-columns:
                    repeat(4, minmax(0, 1fr));
                gap:18px;
                margin-top:22px;
            ">

                <div>
                    <div style="
                        color:#475569;
                        font-size:9px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:.7px;
                    ">
                        Client
                    </div>

                    <div style="
                        color:#E2E8F0;
                        font-size:12px;
                        margin-top:5px;
                    ">
                        {client}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:9px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:.7px;
                    ">
                        Location
                    </div>

                    <div style="
                        color:#E2E8F0;
                        font-size:12px;
                        margin-top:5px;
                    ">
                        {location}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:9px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:.7px;
                    ">
                        Project Manager
                    </div>

                    <div style="
                        color:#E2E8F0;
                        font-size:12px;
                        margin-top:5px;
                    ">
                        {manager}
                    </div>
                </div>

                <div>
                    <div style="
                        color:#475569;
                        font-size:9px;
                        font-weight:800;
                        text-transform:uppercase;
                        letter-spacing:.7px;
                    ">
                        Budget
                    </div>

                    <div style="
                        color:#60A5FA;
                        font-size:13px;
                        font-weight:800;
                        margin-top:5px;
                    ">
                        {_format_currency(budget)}
                    </div>
                </div>

            </div>

            {
                f'''
                <div style="
                    margin-top:18px;
                    padding-top:14px;
                    border-top:1px solid #172033;
                    color:#64748B;
                    font-size:12px;
                    line-height:1.6;
                ">
                    {description}
                </div>
                '''
                if description
                else ""
            }

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Actions
    # --------------------------------------------------------

    action_col1, action_col2, action_col3 = st.columns(
        [1, 1, 5]
    )

    with action_col1:

        if st.button(
            "Edit",
            key=f"edit_project_{project_index}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_project"
            ] = project_index

            st.rerun()

    with action_col2:

        if st.button(
            "Delete",
            key=f"delete_project_{project_index}",
            use_container_width=True,
        ):

            st.session_state[
                "delete_project"
            ] = project_index

            st.rerun()

    # --------------------------------------------------------
    # Edit form
    # --------------------------------------------------------

    editing = st.session_state.get(
        "editing_project"
    )

    if editing == project_index:

        st.markdown(
            "### Edit Project"
        )

        with st.form(
            f"edit_project_form_{project_index}"
        ):

            name_input = st.text_input(
                "Project Name",
                value=_project_name(project),
            )

            id_input = st.text_input(
                "Project ID",
                value=_project_id(project),
            )

            type_input = st.selectbox(
                "Project Type",
                [
                    "Commercial",
                    "Residential",
                    "Industrial",
                    "Infrastructure",
                    "Institutional",
                    "Mixed Use",
                    "Other",
                ],
                index=(
                    [
                        "Commercial",
                        "Residential",
                        "Industrial",
                        "Infrastructure",
                        "Institutional",
                        "Mixed Use",
                        "Other",
                    ].index(project_type)
                    if project_type in [
                        "Commercial",
                        "Residential",
                        "Industrial",
                        "Infrastructure",
                        "Institutional",
                        "Mixed Use",
                        "Other",
                    ]
                    else 0
                ),
            )

            status_input = st.selectbox(
                "Status",
                [
                    "Active",
                    "Planning",
                    "Completed",
                    "On Hold",
                ],
                index=(
                    [
                        "Active",
                        "Planning",
                        "Completed",
                        "On Hold",
                    ].index(status)
                    if status in [
                        "Active",
                        "Planning",
                        "Completed",
                        "On Hold",
                    ]
                    else 0
                ),
            )

            client_input = st.text_input(
                "Client",
                value=_safe_text(
                    project.get(
                        "client_name"
                    )
                    or project.get(
                        "client"
                    )
                ),
            )

            location_input = st.text_input(
                "Location",
                value=_safe_text(
                    project.get(
                        "location"
                    )
                ),
            )

            manager_input = st.text_input(
                "Project Manager",
                value=_safe_text(
                    project.get(
                        "project_manager"
                    )
                    or project.get(
                        "manager"
                    )
                ),
            )

            budget_input = st.number_input(
                "Budget",
                min_value=0.0,
                value=_safe_number(
                    project.get(
                        "estimated_budget"
                    )
                    if project.get(
                        "estimated_budget"
                    ) is not None
                    else project.get(
                        "budget",
                        0,
                    )
                ),
                step=1000.0,
            )

            description_input = st.text_area(
                "Description",
                value=_safe_text(
                    project.get(
                        "description"
                    )
                ),
            )

            save_col, cancel_col = st.columns(2)

            with save_col:

                save_button = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

            with cancel_col:

                cancel_button = st.form_submit_button(
                    "Cancel",
                    use_container_width=True,
                )

            if save_button:

                if not name_input.strip():

                    st.error(
                        "Project Name is required."
                    )

                elif not id_input.strip():

                    st.error(
                        "Project ID is required."
                    )

                else:

                    project["name"] = name_input.strip()
                    project["project_name"] = name_input.strip()

                    project["id"] = id_input.strip()
                    project["project_id"] = id_input.strip()

                    project["type"] = type_input
                    project["project_type"] = type_input

                    project["status"] = status_input

                    project["client"] = client_input.strip()
                    project["client_name"] = client_input.strip()

                    project["location"] = location_input.strip()

                    project["manager"] = manager_input.strip()
                    project["project_manager"] = manager_input.strip()

                    project["budget"] = budget_input
                    project["estimated_budget"] = budget_input

                    project["description"] = description_input.strip()

                    project["updated_at"] = datetime.now().isoformat()

                    save_memory(
                        db
                    )

                    st.session_state.pop(
                        "editing_project",
                        None,
                    )

                    st.success(
                        "Project updated successfully."
                    )

                    st.rerun()

            if cancel_button:

                st.session_state.pop(
                    "editing_project",
                    None,
                )

                st.rerun()

    # --------------------------------------------------------
    # Delete confirmation
    # --------------------------------------------------------

    deleting = st.session_state.get(
        "delete_project"
    )

    if deleting == project_index:

        st.warning(
            f"Delete **{name}**? This action cannot be undone."
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:

            if st.button(
                "Confirm Delete",
                key=f"confirm_delete_{project_index}",
                use_container_width=True,
            ):

                db["projects"].pop(
                    project_index
                )

                save_memory(
                    db
                )

                st.session_state.pop(
                    "delete_project",
                    None,
                )

                st.rerun()

        with cancel_col:

            if st.button(
                "Cancel",
                key=f"cancel_delete_{project_index}",
                use_container_width=True,
            ):

                st.session_state.pop(
                    "delete_project",
                    None,
                )

                st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def _render_create_project(
    db: dict,
) -> None:

    st.markdown(
        "### Create New Project"
    )

    with st.form(
        "create_project_form"
    ):

        name = st.text_input(
            "Project Name",
            placeholder="Grand Horizon Commercial Complex",
        )

        col1, col2 = st.columns(2)

        with col1:

            project_id = st.text_input(
                "Project ID",
                placeholder="PRJ-002",
            )

            project_type = st.selectbox(
                "Project Type",
                [
                    "Commercial",
                    "Residential",
                    "Industrial",
                    "Infrastructure",
                    "Institutional",
                    "Mixed Use",
                    "Other",
                ],
            )

            status = st.selectbox(
                "Status",
                [
                    "Active",
                    "Planning",
                    "Completed",
                    "On Hold",
                ],
            )

        with col2:

            client = st.text_input(
                "Client"
            )

            location = st.text_input(
                "Location"
            )

            manager = st.text_input(
                "Project Manager"
            )

        budget = st.number_input(
            "Project Budget",
            min_value=0.0,
            value=0.0,
            step=1000.0,
        )

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if submitted:

        if not name.strip():

            st.error(
                "Project Name is required."
            )

            return

        if not project_id.strip():

            st.error(
                "Project ID is required."
            )

            return

        # ----------------------------------------------------
        # Duplicate project ID check
        # ----------------------------------------------------

        for existing in db.get(
            "projects",
            [],
        ):

            if str(
                existing.get(
                    "project_id",
                    existing.get(
                        "id",
                        "",
                    ),
                )
            ).strip().lower() == project_id.strip().lower():

                st.error(
                    "A project with this Project ID already exists."
                )

                return

        project = {

            "id": project_id.strip(),

            "project_id": project_id.strip(),

            "name": name.strip(),

            "project_name": name.strip(),

            "type": project_type,

            "project_type": project_type,

            "status": status,

            "client": client.strip(),

            "client_name": client.strip(),

            "location": location.strip(),

            "manager": manager.strip(),

            "project_manager": manager.strip(),

            "budget": budget,

            "estimated_budget": budget,

            "description": description.strip(),

            "created_at": datetime.now().isoformat(),

        }

        db.setdefault(
            "projects",
            [],
        ).append(
            project
        )

        save_memory(
            db
        )

        st.success(
            "Project created successfully."
        )

        st.rerun()


# ============================================================
# MAIN PROJECT MODULE
# ============================================================

def render_projects_module(
    db: dict,
) -> None:

    if not isinstance(
        db,
        dict,
    ):

        st.error(
            "Database could not be loaded."
        )

        return

    projects = db.setdefault(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):

        projects = []

        db["projects"] = projects

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color:#FFFFFF;
            font-size:32px;
            font-weight:900;
            letter-spacing:-0.7px;
        ">
            Project Directory
        </div>

        <div style="
            color:#64748B;
            font-size:13px;
            margin-top:5px;
            margin-bottom:26px;
        ">
            Central project workspace for architectural,
            engineering and construction activities.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Metrics
    # --------------------------------------------------------

    total_projects = len(
        projects
    )

    active_projects = sum(
        1
        for project in projects
        if _project_status(
            project
        ).lower()
        == "active"
    )

    planning_projects = sum(
        1
        for project in projects
        if _project_status(
            project
        ).lower()
        == "planning"
    )

    completed_projects = sum(
        1
        for project in projects
        if _project_status(
            project
        ).lower()
        == "completed"
    )

    total_budget = sum(
        _safe_number(
            project.get(
                "estimated_budget"
            )
            if project.get(
                "estimated_budget"
            ) is not None
            else project.get(
                "budget",
                0,
            )
        )
        for project in projects
        if isinstance(
            project,
            dict,
        )
    )

    metric1, metric2, metric3, metric4, metric5 = st.columns(5)

    with metric1:

        st.metric(
            "Total Projects",
            total_projects,
        )

    with metric2:

        st.metric(
            "Active",
            active_projects,
        )

    with metric3:

        st.metric(
            "Planning",
            planning_projects,
        )

    with metric4:

        st.metric(
            "Completed",
            completed_projects,
        )

    with metric5:

        st.metric(
            "Portfolio Budget",
            f"${total_budget:,.2f}",
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Portfolio header
    # --------------------------------------------------------

    header_col1, header_col2 = st.columns(
        [4, 1]
    )

    with header_col1:

        st.markdown(
            "### Project Portfolio"
        )

    with header_col2:

        create_project = st.button(
            "Create New Project",
            use_container_width=True,
        )

    if create_project:

        st.session_state[
            "show_create_project"
        ] = True

    # --------------------------------------------------------
    # Create project form
    # --------------------------------------------------------

    if st.session_state.get(
        "show_create_project",
        False,
    ):

        _render_create_project(
            db
        )

        st.markdown(
            "---"
        )

    # --------------------------------------------------------
    # Search and filters
    # --------------------------------------------------------

    search_col, status_col, type_col = st.columns(
        [2, 1, 1]
    )

    with search_col:

        search = st.text_input(
            "Search Projects",
            placeholder=(
                "Search by project ID, name, client, "
                "location or manager..."
            ),
        )

    with status_col:

        status_filter = st.selectbox(
            "Status",
            [
                "All",
                "Active",
                "Planning",
                "Completed",
                "On Hold",
            ],
        )

    with type_col:

        types = sorted(
            {
                _project_type(
                    project
                )
                for project in projects
                if isinstance(
                    project,
                    dict,
                )
            }
        )

        type_filter = st.selectbox(
            "Project Type",
            ["All"] + types,
        )

    # --------------------------------------------------------
    # Filter projects
    # --------------------------------------------------------

    search_lower = search.strip().lower()

    filtered_projects = []

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        searchable = " ".join(
            [
                _safe_text(
                    project.get(
                        "project_id"
                    )
                    or project.get(
                        "id"
                    )
                ),
                _project_name(
                    project
                ),
                _safe_text(
                    project.get(
                        "client_name"
                    )
                    or project.get(
                        "client"
                    )
                ),
                _safe_text(
                    project.get(
                        "location"
                    )
                ),
                _safe_text(
                    project.get(
                        "project_manager"
                    )
                    or project.get(
                        "manager"
                    )
                ),
            ]
        ).lower()

        if search_lower and search_lower not in searchable:

            continue

        if (
            status_filter != "All"
            and _project_status(
                project
            ).lower()
            != status_filter.lower()
        ):

            continue

        if (
            type_filter != "All"
            and _project_type(
                project
            ).lower()
            != type_filter.lower()
        ):

            continue

        filtered_projects.append(
            project
        )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            color:#64748B;
            font-size:12px;
            margin-top:18px;
            margin-bottom:14px;
        ">
            Showing {len(filtered_projects)}
            of {len(projects)}
            project{"s" if len(projects) != 1 else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Project cards
    # --------------------------------------------------------

    if not filtered_projects:

        st.info(
            "No projects match the selected filters."
        )

        return

    for project in filtered_projects:

        try:

            original_index = projects.index(
                project
            )

        except ValueError:

            original_index = 0

        _render_project_card(
            db,
            project,
            original_index,
        )