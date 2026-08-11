"""
Creative Studios
Project Directory

AEC Collaboration Platform
"""

import streamlit as st
from datetime import date

from .database import save_memory


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
# SAFE HELPERS
# ============================================================

def safe_number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def money(value):
    return f"${safe_number(value):,.2f}"


def safe_text(value, default=""):
    if value is None:
        return default
    return str(value)


def status_class(status):
    status = safe_text(
        status,
        "Active",
    ).lower()

    mapping = {
        "active": "status-active",
        "planning": "status-planning",
        "on hold": "status-hold",
        "completed": "status-completed",
        "cancelled": "status-cancelled",
    }

    return mapping.get(
        status,
        "status-default",
    )


# ============================================================
# NON-STREAMLIT ALERT
# ============================================================

def message(text, level="info"):

    colors = {
        "info": (
            "#2563EB",
            "#071B3A",
        ),
        "success": (
            "#22C55E",
            "#052E16",
        ),
        "error": (
            "#EF4444",
            "#450A0A",
        ),
        "warning": (
            "#F59E0B",
            "#422006",
        ),
    }

    border, background = colors.get(
        level,
        colors["info"],
    )

    st.markdown(
        f"""
        <div style="
            background:{background};
            border:1px solid {border};
            border-left:4px solid {border};
            border-radius:8px;
            padding:11px 14px;
            margin:10px 0;
            color:#E2E8F0;
            font-size:12px;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(project):

    project_id = safe_text(
        project.get("id"),
        "N/A",
    )

    name = safe_text(
        project.get("name"),
        "Unnamed Project",
    )

    project_type = safe_text(
        project.get("type"),
        "Commercial",
    )

    status = safe_text(
        project.get("status"),
        "Active",
    )

    phase = safe_text(
        project.get("phase"),
        "Concept Design",
    )

    client = safe_text(
        project.get("client"),
        "Not specified",
    )

    location = safe_text(
        project.get("location"),
        "Not specified",
    )

    manager = safe_text(
        project.get("project_manager"),
        "Not assigned",
    )

    budget = project.get(
        "budget",
        0,
    )

    description = safe_text(
        project.get("description"),
    )


    st.markdown(
        f"""
        <div class="project-card">

            <div class="project-card-top">

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

                <span class="
                    project-status
                    {status_class(status)}
                ">
                    {status.upper()}
                </span>

            </div>


            <div class="project-phase">
                Current Phase:
                <strong>{phase}</strong>
            </div>


            <div class="project-details">

                <div>
                    <div class="detail-label">
                        CLIENT
                    </div>

                    <div class="detail-value">
                        {client}
                    </div>
                </div>


                <div>
                    <div class="detail-label">
                        LOCATION
                    </div>

                    <div class="detail-value">
                        {location}
                    </div>
                </div>


                <div>
                    <div class="detail-label">
                        PROJECT MANAGER
                    </div>

                    <div class="detail-value">
                        {manager}
                    </div>
                </div>


                <div>
                    <div class="detail-label">
                        PORTFOLIO BUDGET
                    </div>

                    <div class="detail-value">
                        {money(budget)}
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

def create_project(db):

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
        "create_project_form",
        clear_on_submit=True,
    ):

        col1, col2 = st.columns(2)


        with col1:

            project_id = st.text_input(
                "Project ID *",
                placeholder="PRJ-002",
            )

            name = st.text_input(
                "Project Name *",
                placeholder=(
                    "New Commercial Complex"
                ),
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
            use_container_width=True,
        )


    if not submitted:
        return


    project_id = project_id.strip()
    name = name.strip()


    if not project_id:

        message(
            "Project ID is required.",
            "error",
        )

        return


    if not name:

        message(
            "Project Name is required.",
            "error",
        )

        return


    projects = db.setdefault(
        "projects",
        [],
    )


    # --------------------------------------------------------
    # DUPLICATE CHECK
    # --------------------------------------------------------

    for existing in projects:

        existing_id = safe_text(
            existing.get("id")
        )

        if (
            existing_id.lower()
            == project_id.lower()
        ):

            message(
                f"Project ID '{project_id}' "
                "already exists.",
                "error",
            )

            return


    # --------------------------------------------------------
    # CREATE RECORD
    # --------------------------------------------------------

    project = {
        "id": project_id,
        "name": name,
        "type": project_type,
        "status": status,
        "phase": phase,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "budget": budget,
        "start_date": str(start_date),
        "created_at": str(date.today()),
        "description": description.strip(),
    }


    projects.append(
        project
    )


    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    try:

        save_memory(db)

    except Exception as exc:

        message(
            "The project was created in memory "
            f"but could not be saved: {exc}",
            "error",
        )

        return


    st.session_state[
        "project_created"
    ] = name

    st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_projects_module(db):

    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    created = st.session_state.pop(
        "project_created",
        None,
    )

    if created:

        message(
            f"Project <strong>{created}</strong> "
            "was created successfully.",
            "success",
        )


    # --------------------------------------------------------
    # PAGE HEADER
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
    # PROJECT DATA
    # --------------------------------------------------------

    projects = db.setdefault(
        "projects",
        [],
    )


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total = len(
        projects
    )


    active = sum(
        1
        for p in projects
        if safe_text(
            p.get(
                "status",
                "Active",
            )
        ).lower()
        == "active"
    )


    planning = sum(
        1
        for p in projects
        if safe_text(
            p.get(
                "status",
            )
        ).lower()
        == "planning"
    )


    completed = sum(
        1
        for p in projects
        if safe_text(
            p.get(
                "status",
            )
        ).lower()
        == "completed"
    )


    portfolio_budget = sum(
        safe_number(
            p.get(
                "budget",
                0,
            )
        )
        for p in projects
    )


    k1, k2, k3, k4, k5 = st.columns(5)


    with k1:
        st.metric(
            "Total Projects",
            total,
        )


    with k2:
        st.metric(
            "Active",
            active,
        )


    with k3:
        st.metric(
            "Planning",
            planning,
        )


    with k4:
        st.metric(
            "Completed",
            completed,
        )


    with k5:
        st.metric(
            "Portfolio Budget",
            money(portfolio_budget),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    portfolio, create = st.tabs(
        [
            "Project Portfolio",
            "Create New Project",
        ]
    )


    # ========================================================
    # PORTFOLIO
    # ========================================================

    with portfolio:

        if not projects:

            st.markdown(
                """
                <div class="empty-state">

                    <div class="empty-title">
                        No Projects
                    </div>

                    <div class="empty-text">
                        Create your first project
                        using the Create New Project tab.
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


            f1, f2 = st.columns(2)


            with f1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"] + PROJECT_STATUSES,
                )


            with f2:

                type_filter = st.selectbox(
                    "Project Type",
                    ["All"] + PROJECT_TYPES,
                )


            search = (
                search or ""
            ).strip().lower()


            filtered = []


            for project in projects:

                searchable = " ".join(
                    safe_text(
                        project.get(
                            field,
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
                    and safe_text(
                        project.get(
                            "status",
                            "Active",
                        )
                    )
                    != status_filter
                ):
                    continue


                if (
                    type_filter != "All"
                    and safe_text(
                        project.get(
                            "type",
                            "",
                        )
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
                    font-size:11px;
                    margin:12px 0;
                ">
                    Showing
                    <strong style="color:#60A5FA;">
                        {len(filtered)}
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


            for project in filtered:

                render_project_card(
                    project
                )


    # ========================================================
    # CREATE
    # ========================================================

    with create:

        create_project(
            db
        )