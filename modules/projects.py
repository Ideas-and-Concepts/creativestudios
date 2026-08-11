"""
Creative Studios
Project Directory Module

Clean Streamlit implementation.
No st.success(), st.warning(), st.error(), or st.info()
icons are used for project status rendering.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# HELPERS
# ============================================================

def text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def project_name(project: dict) -> str:
    return text(
        project.get("project_name")
        or project.get("name"),
        "Unnamed Project",
    )


def project_id(project: dict) -> str:
    return text(
        project.get("project_id")
        or project.get("id"),
        "N/A",
    )


def project_type(project: dict) -> str:
    return text(
        project.get("project_type")
        or project.get("type"),
        "General",
    )


def project_status(project: dict) -> str:
    value = text(
        project.get("status"),
        "Active",
    ).strip()

    return value or "Active"


def project_budget(project: dict) -> float:
    value = project.get("estimated_budget")

    if value is None:
        value = project.get("budget", 0)

    return number(value)


def status_class(status: str) -> str:
    value = status.lower().strip()

    if value == "active":
        return "cs-status-active"

    if value == "planning":
        return "cs-status-planning"

    if value == "completed":
        return "cs-status-completed"

    return "cs-status-hold"


# ============================================================
# PROJECT CSS
# ============================================================

def inject_project_css() -> None:

    st.markdown(
        """
        <style>

        .cs-project-card {
            background:#0A0F16;
            border:1px solid #172033;
            border-radius:14px;
            padding:22px;
            margin-top:12px;
            margin-bottom:8px;
        }

        .cs-project-card:hover {
            border-color:#2563EB;
        }

        .cs-project-title {
            color:#FFFFFF;
            font-size:18px;
            font-weight:850;
        }

        .cs-project-meta {
            color:#64748B;
            font-size:12px;
            margin-top:5px;
        }

        .cs-project-status {
            display:inline-block;
            padding:5px 10px;
            border-radius:999px;
            font-size:9px;
            font-weight:850;
            text-transform:uppercase;
            letter-spacing:.5px;
        }

        .cs-status-active {
            background:#082F63;
            color:#93C5FD;
        }

        .cs-status-planning {
            background:#422006;
            color:#FCD34D;
        }

        .cs-status-completed {
            background:#064E3B;
            color:#6EE7B7;
        }

        .cs-status-hold {
            background:#27272A;
            color:#D4D4D8;
        }

        .cs-project-label {
            color:#475569;
            font-size:9px;
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:.7px;
        }

        .cs-project-value {
            color:#E2E8F0;
            font-size:12px;
            margin-top:5px;
        }

        .cs-project-budget {
            color:#60A5FA;
            font-size:13px;
            font-weight:800;
            margin-top:5px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project(db: dict) -> None:

    st.markdown("### Create New Project")

    with st.form("create_project_form"):

        name = st.text_input(
            "Project Name",
            placeholder="Grand Horizon Commercial Complex",
        )

        col1, col2 = st.columns(2)

        with col1:

            pid = st.text_input(
                "Project ID",
                placeholder="PRJ-002",
            )

            ptype = st.selectbox(
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

            client = st.text_input("Client")

            location = st.text_input("Location")

            manager = st.text_input(
                "Project Manager"
            )

        budget = st.number_input(
            "Estimated Budget",
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

    if not submitted:
        return

    if not name.strip():

        st.error(
            "Project Name is required."
        )

        return

    if not pid.strip():

        st.error(
            "Project ID is required."
        )

        return

    for existing in db.get(
        "projects",
        [],
    ):

        if not isinstance(
            existing,
            dict,
        ):
            continue

        if (
            project_id(existing).lower()
            == pid.strip().lower()
        ):

            st.error(
                "A project with this Project ID already exists."
            )

            return

    new_project = {

        "id": pid.strip(),

        "project_id": pid.strip(),

        "name": name.strip(),

        "project_name": name.strip(),

        "type": ptype,

        "project_type": ptype,

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
        new_project
    )

    save_memory(db)

    st.session_state[
        "create_project"
    ] = False

    st.rerun()


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(
    db: dict,
    project: dict,
    index: int,
) -> None:

    name = project_name(project)

    pid = project_id(project)

    ptype = project_type(project)

    status = project_status(project)

    client = text(
        project.get(
            "client_name"
        )
        or project.get(
            "client"
        ),
        "Not specified",
    )

    location = text(
        project.get("location"),
        "Not specified",
    )

    manager = text(
        project.get(
            "project_manager"
        )
        or project.get(
            "manager"
        ),
        "Not assigned",
    )

    budget = project_budget(project)

    css = status_class(status)

    st.markdown(
        f"""
        <div class="cs-project-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:20px;
            ">

                <div>

                    <div class="cs-project-title">
                        {name}
                    </div>

                    <div class="cs-project-meta">
                        {pid}
                        &nbsp;•&nbsp;
                        {ptype}
                    </div>

                </div>

                <div class="cs-project-status {css}">
                    {status}
                </div>

            </div>


            <div style="
                display:grid;
                grid-template-columns:
                repeat(4,minmax(0,1fr));
                gap:20px;
                margin-top:22px;
            ">

                <div>
                    <div class="cs-project-label">
                        Client
                    </div>

                    <div class="cs-project-value">
                        {client}
                    </div>
                </div>


                <div>
                    <div class="cs-project-label">
                        Location
                    </div>

                    <div class="cs-project-value">
                        {location}
                    </div>
                </div>


                <div>
                    <div class="cs-project-label">
                        Project Manager
                    </div>

                    <div class="cs-project-value">
                        {manager}
                    </div>
                </div>


                <div>
                    <div class="cs-project-label">
                        Portfolio Budget
                    </div>

                    <div class="cs-project-budget">
                        ${budget:,.2f}
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    edit_col, delete_col, _ = st.columns(
        [1, 1, 6]
    )

    with edit_col:

        edit = st.button(
            "Edit",
            key=f"project_edit_{index}",
            use_container_width=True,
        )

    with delete_col:

        delete = st.button(
            "Delete",
            key=f"project_delete_{index}",
            use_container_width=True,
        )

    if edit:

        st.session_state[
            "edit_project"
        ] = index

        st.rerun()

    if delete:

        st.session_state[
            "delete_project"
        ] = index

        st.rerun()

    # --------------------------------------------------------
    # DELETE CONFIRMATION
    # --------------------------------------------------------

    if st.session_state.get(
        "delete_project"
    ) == index:

        st.markdown(
            """
            <div style="
                background:#160A0A;
                border:1px solid #4C1D1D;
                border-radius:10px;
                padding:14px;
                margin-top:8px;
            ">
                <div style="
                    color:#FCA5A5;
                    font-size:13px;
                    font-weight:700;
                ">
                    Confirm project deletion
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        yes_col, no_col = st.columns(2)

        with yes_col:

            confirm = st.button(
                "Confirm Delete",
                key=f"confirm_delete_{index}",
                use_container_width=True,
            )

        with no_col:

            cancel = st.button(
                "Cancel",
                key=f"cancel_delete_{index}",
                use_container_width=True,
            )

        if confirm:

            projects = db.get(
                "projects",
                [],
            )

            if (
                0 <= index < len(projects)
            ):

                projects.pop(index)

                save_memory(db)

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


# ============================================================
# EDIT PROJECT
# ============================================================

def edit_project(
    db: dict,
    index: int,
) -> None:

    projects = db.get(
        "projects",
        [],
    )

    if (
        index < 0
        or index >= len(projects)
    ):

        st.session_state.pop(
            "edit_project",
            None,
        )

        return

    project = projects[index]

    st.markdown(
        "### Edit Project"
    )

    with st.form(
        f"edit_project_{index}"
    ):

        name = st.text_input(
            "Project Name",
            value=project_name(project),
        )

        pid = st.text_input(
            "Project ID",
            value=project_id(project),
        )

        ptype_options = [
            "Commercial",
            "Residential",
            "Industrial",
            "Infrastructure",
            "Institutional",
            "Mixed Use",
            "Other",
        ]

        current_type = project_type(
            project
        )

        if current_type not in ptype_options:
            current_type = "Other"

        ptype = st.selectbox(
            "Project Type",
            ptype_options,
            index=ptype_options.index(
                current_type
            ),
        )

        status_options = [
            "Active",
            "Planning",
            "Completed",
            "On Hold",
        ]

        current_status = project_status(
            project
        )

        if current_status not in status_options:
            current_status = "Active"

        status = st.selectbox(
            "Status",
            status_options,
            index=status_options.index(
                current_status
            ),
        )

        client = st.text_input(
            "Client",
            value=text(
                project.get(
                    "client_name"
                )
                or project.get(
                    "client"
                )
            ),
        )

        location = st.text_input(
            "Location",
            value=text(
                project.get("location")
            ),
        )

        manager = st.text_input(
            "Project Manager",
            value=text(
                project.get(
                    "project_manager"
                )
                or project.get(
                    "manager"
                )
            ),
        )

        budget = st.number_input(
            "Estimated Budget",
            min_value=0.0,
            value=project_budget(project),
            step=1000.0,
        )

        description = st.text_area(
            "Description",
            value=text(
                project.get(
                    "description"
                )
            ),
        )

        save_col, cancel_col = st.columns(2)

        with save_col:

            save = st.form_submit_button(
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
            "edit_project",
            None,
        )

        st.rerun()

    if save:

        if not name.strip():

            st.error(
                "Project Name is required."
            )

            return

        project["id"] = pid.strip()

        project["project_id"] = pid.strip()

        project["name"] = name.strip()

        project["project_name"] = name.strip()

        project["type"] = ptype

        project["project_type"] = ptype

        project["status"] = status

        project["client"] = client.strip()

        project["client_name"] = client.strip()

        project["location"] = location.strip()

        project["manager"] = manager.strip()

        project["project_manager"] = manager.strip()

        project["budget"] = budget

        project["estimated_budget"] = budget

        project["description"] = description.strip()

        project["updated_at"] = datetime.now().isoformat()

        save_memory(db)

        st.session_state.pop(
            "edit_project",
            None,
        )

        st.rerun()


# ============================================================
# MAIN
# ============================================================

def render_projects_module(
    db: dict,
) -> None:

    inject_project_css()

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
            letter-spacing:-.8px;
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

    total = len(projects)

    active = 0
    planning = 0
    completed = 0
    budget = 0.0

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        status = project_status(
            project
        ).lower()

        if status == "active":
            active += 1

        elif status == "planning":
            planning += 1

        elif status == "completed":
            completed += 1

        budget += project_budget(
            project
        )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric(
            "Total Projects",
            total,
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
            f"${budget:,.2f}",
        )

    # --------------------------------------------------------
    # PORTFOLIO
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
                "create_project"
            ] = not st.session_state.get(
                "create_project",
                False,
            )

            st.rerun()

    # --------------------------------------------------------
    # CREATE FORM
    # --------------------------------------------------------

    if st.session_state.get(
        "create_project",
        False,
    ):

        create_project(db)

        st.markdown("---")

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
                "Search by project ID, name, "
                "client, location or manager..."
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
                project_type(p)
                for p in projects
                if isinstance(p, dict)
            }
        )

        type_filter = st.selectbox(
            "Project Type",
            ["All"] + types,
        )

    # --------------------------------------------------------
    # FILTER
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
                project_id(project),
                project_name(project),
                text(
                    project.get(
                        "client_name"
                    )
                    or project.get(
                        "client"
                    )
                ),
                text(
                    project.get(
                        "location"
                    )
                ),
                text(
                    project.get(
                        "project_manager"
                    )
                    or project.get(
                        "manager"
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
            and project_status(project).lower()
            != status_filter.lower()
        ):
            continue

        if (
            type_filter != "All"
            and project_type(project).lower()
            != type_filter.lower()
        ):
            continue

        filtered.append(project)

    st.markdown(
        f"""
        <div style="
            color:#64748B;
            font-size:12px;
            margin-top:16px;
            margin-bottom:12px;
        ">
            Showing {len(filtered)}
            of {len(projects)}
            {"project" if len(projects) == 1 else "projects"}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # EDIT
    # --------------------------------------------------------

    if "edit_project" in st.session_state:

        edit_project(
            db,
            st.session_state["edit_project"],
        )

        st.markdown("---")

    # --------------------------------------------------------
    # EMPTY
    # --------------------------------------------------------

    if not filtered:

        st.markdown(
            """
            <div style="
                background:#0A0F16;
                border:1px solid #172033;
                border-radius:12px;
                padding:35px;
                text-align:center;
                color:#64748B;
            ">
                No projects found.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    # --------------------------------------------------------
    # PROJECTS
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