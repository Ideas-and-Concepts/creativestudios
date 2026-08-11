"""
Creative Studios
Project Directory Module

AEC Collaboration Platform
"""

import streamlit as st
from datetime import date

from .database import save_memory


# ============================================================
# PROJECT CONFIGURATION
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
]

PROJECT_PHASES = [
    "Concept Design",
    "Schematic Design",
    "Design Development",
    "Construction Documents",
    "Bidding & Negotiation",
    "Construction",
    "Construction Administration",
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

def safe_money(value):
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def safe_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_status_class(status):

    status = str(status or "Active").lower()

    if status == "active":
        return "status-active"

    if status == "planning":
        return "status-planning"

    if status == "completed":
        return "status-completed"

    if status == "on hold":
        return "status-hold"

    if status == "cancelled":
        return "status-cancelled"

    return "status-default"


def status_badge(status):

    status = str(status or "Active")

    css_class = get_status_class(status)

    st.markdown(
        f"""
        <span class="project-status {css_class}">
            {status.upper()}
        </span>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(project):

    project_id = project.get(
        "id",
        "N/A",
    )

    name = project.get(
        "name",
        "Unnamed Project",
    )

    project_type = project.get(
        "type",
        "Commercial",
    )

    phase = project.get(
        "phase",
        "Concept Design",
    )

    status = project.get(
        "status",
        "Active",
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

    budget = project.get(
        "budget",
        0,
    )

    description = project.get(
        "description",
        "",
    )


    st.markdown(
        f"""
        <div class="project-card">

            <div class="project-card-header">

                <div>

                    <div class="project-name">
                        {name}
                    </div>

                    <div class="project-code">
                        {project_id}
                        &nbsp;•&nbsp;
                        {project_type}
                    </div>

                </div>

                <div>
                    <span class="project-status {get_status_class(status)}">
                        {str(status).upper()}
                    </span>
                </div>

            </div>


            <div class="project-phase">
                Current Phase:
                <strong>{phase}</strong>
            </div>


            <div class="project-grid">

                <div class="project-detail">
                    <div class="detail-label">
                        CLIENT
                    </div>
                    <div class="detail-value">
                        {client}
                    </div>
                </div>


                <div class="project-detail">
                    <div class="detail-label">
                        LOCATION
                    </div>
                    <div class="detail-value">
                        {location}
                    </div>
                </div>


                <div class="project-detail">
                    <div class="detail-label">
                        PROJECT MANAGER
                    </div>
                    <div class="detail-value">
                        {manager}
                    </div>
                </div>


                <div class="project-detail">
                    <div class="detail-label">
                        BUDGET
                    </div>
                    <div class="detail-value">
                        {safe_money(budget)}
                    </div>
                </div>

            </div>


            {
                f'''
                <div class="project-description">
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


# ============================================================
# CREATE PROJECT
# ============================================================

def render_create_project(db):

    st.markdown(
        """
        <div class="section-header">
            <div class="section-title">
                Create New Project
            </div>

            <div class="section-description">
                Register a new architectural,
                engineering or construction project.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    with st.form(
        "new_project_form",
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
                placeholder="New Commercial Complex",
            )

            project_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES,
            )

            client = st.text_input(
                "Client / Developer",
            )

            location = st.text_input(
                "Location",
            )


        with col2:

            status = st.selectbox(
                "Status",
                PROJECT_STATUSES,
                index=1,
            )

            phase = st.selectbox(
                "Current Lifecycle Phase",
                PROJECT_PHASES,
            )

            manager = st.text_input(
                "Project Manager",
            )

            budget = st.number_input(
                "Estimated Budget ($)",
                min_value=0.0,
                value=500000.0,
                step=10000.0,
            )

            start_date = st.date_input(
                "Start Date",
                value=date.today(),
            )


        description = st.text_area(
            "Scope & Overview Description",
            height=110,
        )


        submitted = st.form_submit_button(
            "Create Project",
            type="primary",
            use_container_width=True,
        )


    if not submitted:
        return


    project_id = project_id.strip()
    project_name = project_name.strip()


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not project_id:

        st.markdown(
            """
            <div class="app-message error">
                Project ID is required.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return


    if not project_name:

        st.markdown(
            """
            <div class="app-message error">
                Project Name is required.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return


    projects = db.setdefault(
        "projects",
        [],
    )


    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    duplicate = any(
        str(existing.get("id", "")).lower()
        == project_id.lower()
        for existing in projects
    )


    if duplicate:

        st.markdown(
            f"""
            <div class="app-message error">
                Project ID
                <strong>{project_id}</strong>
                already exists.
            </div>
            """,
            unsafe_allow_html=True,
        )

        return


    # --------------------------------------------------------
    # NEW PROJECT
    # --------------------------------------------------------

    new_project = {
        "id": project_id,
        "name": project_name,
        "type": project_type,
        "phase": phase,
        "status": status,
        "budget": budget,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "created_at": str(date.today()),
        "start_date": str(start_date),
        "description": description.strip(),
    }


    projects.append(
        new_project
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        save_memory(db)

        st.session_state[
            "project_created"
        ] = project_name

        st.rerun()

    except Exception as exc:

        st.markdown(
            f"""
            <div class="app-message error">
                Unable to save project:
                {str(exc)}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# MAIN MODULE
# ============================================================

def render_projects_module(db):

    # --------------------------------------------------------
    # PROJECT CREATED MESSAGE
    # --------------------------------------------------------

    created = st.session_state.pop(
        "project_created",
        None,
    )


    if created:

        st.markdown(
            f"""
            <div class="app-message success">
                Project
                <strong>{created}</strong>
                was created successfully.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="page-header">

            <div class="page-title">
                Project Directory
            </div>

            <div class="page-subtitle">
                Central project workspace for
                architectural, engineering and
                construction activities.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    projects = db.setdefault(
        "projects",
        [],
    )


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total_projects = len(
        projects
    )


    active_projects = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "Active",
            )
        ).lower()
        == "active"
    )


    planning_projects = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "planning"
    )


    completed_projects = sum(
        1
        for project in projects
        if str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "completed"
    )


    portfolio_budget = sum(
        safe_number(
            project.get(
                "budget",
                0,
            )
        )
        for project in projects
    )


    k1, k2, k3, k4, k5 = st.columns(5)


    with k1:
        st.metric(
            "Total Projects",
            total_projects,
        )


    with k2:
        st.metric(
            "Active",
            active_projects,
        )


    with k3:
        st.metric(
            "Planning",
            planning_projects,
        )


    with k4:
        st.metric(
            "Completed",
            completed_projects,
        )


    with k5:
        st.metric(
            "Portfolio Budget",
            safe_money(
                portfolio_budget
            ),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    portfolio_tab, create_tab = st.tabs(
        [
            "Project Portfolio",
            "Create New Project",
        ]
    )


    # ========================================================
    # PORTFOLIO
    # ========================================================

    with portfolio_tab:

        if not projects:

            st.markdown(
                """
                <div class="empty-state">

                    <div class="empty-title">
                        No Projects
                    </div>

                    <div class="empty-text">
                        No projects have been registered yet.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
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


            search = (
                search or ""
            ).strip().lower()


            filtered_projects = []


            for project in projects:

                searchable = " ".join(
                    str(
                        project.get(
                            field,
                            "",
                        )
                    )
                    for field in [
                        "id",
                        "name",
                        "client",
                        "location",
                        "project_manager",
                    ]
                ).lower()


                if (
                    search
                    and search not in searchable
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
                        "",
                    )
                    != type_filter
                ):
                    continue


                filtered_projects.append(
                    project
                )


            st.markdown(
                f"""
                <div style="
                    color:#64748B;
                    font-size:11px;
                    margin:12px 0;
                ">
                    Showing
                    <strong style="color:#60A5FA;">
                        {len(filtered_projects)}
                    </strong>
                    of
                    <strong style="color:#FFFFFF;">
                        {len(projects)}
                    </strong>
                    projects
                </div>
                """,
                unsafe_allow_html=True,
            )


            for project in filtered_projects:

                render_project_card(
                    project
                )


    # ========================================================
    # CREATE
    # ========================================================

    with create_tab:

        render_create_project(
            db
        )