"""
Creative Studios
Project Directory

Safe, self-contained Project Directory module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    return str(value)


def safe_float(
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


def get_project_name(
    project: dict,
) -> str:

    return safe_text(
        project.get(
            "project_name",
            project.get(
                "name",
                "Unnamed Project",
            ),
        ),
        "Unnamed Project",
    )


def get_project_id(
    project: dict,
) -> str:

    return safe_text(
        project.get(
            "project_id",
            project.get(
                "id",
                "N/A",
            ),
        ),
        "N/A",
    )


def get_project_type(
    project: dict,
) -> str:

    return safe_text(
        project.get(
            "project_type",
            project.get(
                "type",
                "General",
            ),
        ),
        "General",
    )


def get_project_status(
    project: dict,
) -> str:

    status = safe_text(
        project.get(
            "status",
            "Active",
        ),
        "Active",
    ).strip()

    return status or "Active"


def get_project_budget(
    project: dict,
) -> float:

    value = project.get(
        "estimated_budget"
    )

    if value is None:

        value = project.get(
            "budget",
            0,
        )

    return safe_float(
        value
    )


def status_css(
    status: str,
) -> str:

    normalized = status.lower().strip()

    if normalized == "active":

        return "status-active"

    if normalized == "planning":

        return "status-planning"

    if normalized == "completed":

        return "status-completed"

    return "status-on-hold"


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(
    db: dict,
    project: dict,
    index: int,
) -> None:

    name = get_project_name(
        project
    )

    project_id = get_project_id(
        project
    )

    project_type = get_project_type(
        project
    )

    status = get_project_status(
        project
    )

    client = safe_text(
        project.get(
            "client_name",
            project.get(
                "client",
                "Not specified",
            ),
        ),
        "Not specified",
    )

    location = safe_text(
        project.get(
            "location",
            "Not specified",
        ),
        "Not specified",
    )

    manager = safe_text(
        project.get(
            "project_manager",
            project.get(
                "manager",
                "Not assigned",
            ),
        ),
        "Not assigned",
    )

    budget = get_project_budget(
        project
    )

    description = safe_text(
        project.get(
            "description",
            "",
        )
    )

    css = status_css(
        status
    )

    # --------------------------------------------------------
    # CARD
    # --------------------------------------------------------

    description_html = ""

    if description.strip():

        description_html = f"""
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
        """

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

                <div class="project-status {css}">
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
                        Portfolio Budget
                    </div>

                    <div style="
                        color:#60A5FA;
                        font-size:13px;
                        font-weight:800;
                        margin-top:5px;
                    ">
                        ${budget:,.2f}
                    </div>

                </div>

            </div>

            {description_html}

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    edit_col, delete_col, spacer = st.columns(
        [1, 1, 5]
    )

    with edit_col:

        edit = st.button(
            "Edit",
            key=f"edit_project_{index}",
            use_container_width=True,
        )

    with delete_col:

        delete = st.button(
            "Delete",
            key=f"delete_project_{index}",
            use_container_width=True,
        )

    if edit:

        st.session_state[
            "editing_project"
        ] = index

        st.session_state.pop(
            "delete_project",
            None,
        )

        st.rerun()

    if delete:

        st.session_state[
            "delete_project"
        ] = index

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.rerun()

    # --------------------------------------------------------
    # DELETE CONFIRMATION
    # --------------------------------------------------------

    if st.session_state.get(
        "delete_project"
    ) == index:

        st.warning(
            f"Delete '{name}'? This action cannot be undone."
        )

        confirm_col, cancel_col = st.columns(2)

        with confirm_col:

            confirm = st.button(
                "Confirm Delete",
                key=f"confirm_delete_{index}",
                use_container_width=True,
            )

        with cancel_col:

            cancel = st.button(
                "Cancel",
                key=f"cancel_delete_{index}",
                use_container_width=True,
            )

        if confirm:

            if (
                0 <= index < len(
                    db.get(
                        "projects",
                        [],
                    )
                )
            ):

                db["projects"].pop(
                    index
                )

                save_memory(
                    db
                )

            st.session_state.pop(
                "delete_project",
                None,
            )

            st.rerun()

        if cancel:

            st.session_state.pop(
                "delete_project",
                None,
            )

            st.rerun()

    # --------------------------------------------------------
    # EDIT FORM
    # --------------------------------------------------------

    if st.session_state.get(
        "editing_project"
    ) != index:

        return

    st.markdown(
        "### Edit Project"
    )

    with st.form(
        f"edit_project_form_{index}"
    ):

        name_input = st.text_input(
            "Project Name",
            value=name,
        )

        col1, col2 = st.columns(2)

        with col1:

            id_input = st.text_input(
                "Project ID",
                value=project_id,
            )

            type_options = [
                "Commercial",
                "Residential",
                "Industrial",
                "Infrastructure",
                "Institutional",
                "Mixed Use",
                "Other",
            ]

            type_index = (
                type_options.index(
                    project_type
                )
                if project_type in type_options
                else 0
            )

            type_input = st.selectbox(
                "Project Type",
                type_options,
                index=type_index,
            )

            status_options = [
                "Active",
                "Planning",
                "Completed",
                "On Hold",
            ]

            status_index = (
                status_options.index(
                    status
                )
                if status in status_options
                else 0
            )

            status_input = st.selectbox(
                "Status",
                status_options,
                index=status_index,
            )

        with col2:

            client_input = st.text_input(
                "Client",
                value=client,
            )

            location_input = st.text_input(
                "Location",
                value=location,
            )

            manager_input = st.text_input(
                "Project Manager",
                value=manager,
            )

        budget_input = st.number_input(
            "Budget",
            min_value=0.0,
            value=budget,
            step=1000.0,
        )

        description_input = st.text_area(
            "Description",
            value=description,
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

    if cancel_button:

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.rerun()

    if save_button:

        if not name_input.strip():

            st.error(
                "Project Name is required."
            )

            return

        if not id_input.strip():

            st.error(
                "Project ID is required."
            )

            return

        project["id"] = id_input.strip()
        project["project_id"] = id_input.strip()

        project["name"] = name_input.strip()
        project["project_name"] = name_input.strip()

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

        project["updated_at"] = (
            datetime.now().isoformat()
        )

        save_memory(
            db
        )

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def render_create_project(
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

        create_button = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if not create_button:

        return

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

    # --------------------------------------------------------
    # Duplicate ID
    # --------------------------------------------------------

    for existing in db.get(
        "projects",
        [],
    ):

        if not isinstance(
            existing,
            dict,
        ):

            continue

        existing_id = get_project_id(
            existing
        ).lower()

        if existing_id == project_id.strip().lower():

            st.error(
                "A project with this Project ID already exists."
            )

            return

    new_project = {

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

        "created_at": (
            datetime.now().isoformat()
        ),
    }

    db.setdefault(
        "projects",
        []
    ).append(
        new_project
    )

    save_memory(
        db
    )

    st.session_state[
        "show_create_project"
    ] = False

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

        st.error(
            "Database is unavailable."
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
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            color:#FFFFFF;
            font-size:32px;
            font-weight:900;
            letter-spacing:-0.8px;
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

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    total_projects = len(
        projects
    )

    active = 0
    planning = 0
    completed = 0
    portfolio_budget = 0.0

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):

            continue

        project_status = (
            get_project_status(
                project
            ).lower()
        )

        if project_status == "active":

            active += 1

        elif project_status == "planning":

            planning += 1

        elif project_status == "completed":

            completed += 1

        portfolio_budget += get_project_budget(
            project
        )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:

        st.metric(
            "Total Projects",
            total_projects,
        )

    with c2:

        st.metric(
            "Active",
            active,
        )

    with c3:

        st.metric(
            "Planning",
            planning,
        )

    with c4:

        st.metric(
            "Completed",
            completed,
        )

    with c5:

        st.metric(
            "Portfolio Budget",
            f"${portfolio_budget:,.2f}",
        )

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # PORTFOLIO HEADER
    # --------------------------------------------------------

    title_col, button_col = st.columns(
        [4, 1]
    )

    with title_col:

        st.markdown(
            "### Project Portfolio"
        )

    with button_col:

        if st.button(
            "Create New Project",
            use_container_width=True,
        ):

            st.session_state[
                "show_create_project"
            ] = not st.session_state.get(
                "show_create_project",
                False,
            )

            st.session_state.pop(
                "editing_project",
                None,
            )

            st.rerun()

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    if st.session_state.get(
        "show_create_project",
        False,
    ):

        render_create_project(
            db
        )

        st.markdown(
            "---"
        )

    # --------------------------------------------------------
    # FILTERS
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

        project_types = sorted(
            {
                get_project_type(
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
            ["All"] + project_types,
        )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    search_value = search.strip().lower()

    filtered = []

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):

            continue

        searchable = " ".join(
            [
                get_project_id(
                    project
                ),
                get_project_name(
                    project
                ),
                safe_text(
                    project.get(
                        "client_name",
                        project.get(
                            "client",
                            "",
                        ),
                    )
                ),
                safe_text(
                    project.get(
                        "location",
                        "",
                    )
                ),
                safe_text(
                    project.get(
                        "project_manager",
                        project.get(
                            "manager",
                            "",
                        ),
                    )
                ),
            ]
        ).lower()

        if (
            search_value
            and search_value not in searchable
        ):

            continue

        if (
            status_filter != "All"
            and get_project_status(
                project
            ).lower()
            != status_filter.lower()
        ):

            continue

        if (
            type_filter != "All"
            and get_project_type(
                project
            ).lower()
            != type_filter.lower()
        ):

            continue

        filtered.append(
            project
        )

    # --------------------------------------------------------
    # RESULT COUNT
    # --------------------------------------------------------

    plural = (
        "projects"
        if len(projects) != 1
        else "project"
    )

    st.markdown(
        f"""
        <div style="
            color:#64748B;
            font-size:12px;
            margin-top:17px;
            margin-bottom:13px;
        ">
            Showing {len(filtered)}
            of {len(projects)}
            {plural}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # EMPTY STATE
    # --------------------------------------------------------

    if not filtered:

        st.info(
            "No projects match the selected filters."
        )

        return

    # --------------------------------------------------------
    # CARDS
    # --------------------------------------------------------

    for project in filtered:

        try:

            index = projects.index(
                project
            )

        except ValueError:

            continue

        render_project_card(
            db,
            project,
            index,
        )