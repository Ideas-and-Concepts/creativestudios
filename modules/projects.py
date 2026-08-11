"""
Creative Studios
Project Directory Module
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

def text(value, default=""):

    if value is None:
        return default

    return str(value)


def number(value):

    try:
        return float(value or 0)

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def money(value):

    return f"${number(value):,.2f}"


def status_css(status):

    status = text(
        status,
        "Active",
    ).lower()


    mapping = {

        "active":
            "status-active",

        "planning":
            "status-planning",

        "completed":
            "status-completed",

        "on hold":
            "status-hold",

        "cancelled":
            "status-cancelled",

    }


    return mapping.get(
        status,
        "status-default",
    )


# ============================================================
# MESSAGE
# ============================================================

def show_message(
    content,
    kind="info",
):

    styles = {

        "success": {
            "background": "#052E16",
            "border": "#166534",
            "accent": "#22C55E",
            "text": "#BBF7D0",
        },

        "error": {
            "background": "#450A0A",
            "border": "#991B1B",
            "accent": "#EF4444",
            "text": "#FECACA",
        },

        "info": {
            "background": "#071B3A",
            "border": "#1D4ED8",
            "accent": "#2563EB",
            "text": "#BFDBFE",
        },

    }


    style = styles.get(
        kind,
        styles["info"],
    )


    st.markdown(
        f"""
        <div style="
            background:{style['background']};
            border:1px solid {style['border']};
            border-left:4px solid {style['accent']};
            color:{style['text']};
            border-radius:8px;
            padding:11px 14px;
            margin:10px 0;
            font-size:12px;
        ">
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(
    project,
):

    project_id = text(
        project.get("id"),
        "N/A",
    )

    project_name = text(
        project.get("name"),
        "Unnamed Project",
    )

    project_type = text(
        project.get("type"),
        "Commercial",
    )

    project_status = text(
        project.get("status"),
        "Active",
    )

    project_phase = text(
        project.get("phase"),
        "Concept Design",
    )

    client = text(
        project.get("client"),
        "Not specified",
    )

    location = text(
        project.get("location"),
        "Not specified",
    )

    manager = text(
        project.get(
            "project_manager"
        ),
        "Not assigned",
    )

    budget = project.get(
        "budget",
        0,
    )

    description = text(
        project.get(
            "description"
        )
    )


    description_html = ""


    if description:

        description_html = f"""
        <div class="project-description">
            {description}
        </div>
        """


    st.markdown(
        f"""
        <div class="project-card">

            <div class="project-card-top">

                <div>

                    <div class="project-name">
                        {project_name}
                    </div>

                    <div class="project-code">
                        {project_id}
                        &nbsp;•&nbsp;
                        {project_type}
                    </div>

                </div>

                <span class="
                    project-status
                    {status_css(project_status)}
                ">
                    {project_status.upper()}
                </span>

            </div>


            <div class="project-phase">

                Current Phase:
                <strong>
                    {project_phase}
                </strong>

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
                        BUDGET
                    </div>

                    <div class="detail-value">
                        {money(budget)}
                    </div>

                </div>

            </div>


            {description_html}

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CREATE PROJECT
# ============================================================

def _create_project(
    db,
):

    st.markdown(
        """
        <div class="page-header">

            <div class="page-title">
                Create New Project
            </div>

            <div class="page-subtitle">
                Register a new architectural,
                engineering or construction project.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    with st.form(
        "create_new_project",
        clear_on_submit=True,
    ):

        left, right = st.columns(2)


        with left:

            project_id = st.text_input(
                "Project ID *",
                placeholder="PRJ-002",
            )


            project_name = st.text_input(
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


        with right:

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
            "Project Description",
            height=110,
        )


        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )


    if not submitted:

        return


    project_id = (
        project_id or ""
    ).strip()


    project_name = (
        project_name or ""
    ).strip()


    if not project_id:

        show_message(
            "Project ID is required.",
            "error",
        )

        return


    if not project_name:

        show_message(
            "Project Name is required.",
            "error",
        )

        return


    projects = db.setdefault(
        "projects",
        [],
    )


    for existing in projects:

        existing_id = text(
            existing.get("id")
        ).strip().lower()


        if (
            existing_id
            == project_id.lower()
        ):

            show_message(
                f"Project ID "
                f"<strong>{project_id}</strong> "
                "already exists.",
                "error",
            )

            return


    new_project = {

        "id":
            project_id,

        "name":
            project_name,

        "type":
            project_type,

        "status":
            status,

        "phase":
            phase,

        "client":
            (client or "").strip(),

        "location":
            (location or "").strip(),

        "project_manager":
            (manager or "").strip(),

        "budget":
            budget,

        "start_date":
            str(start_date),

        "created_at":
            str(date.today()),

        "description":
            (description or "").strip(),

    }


    projects.append(
        new_project
    )


    try:

        save_memory(
            db
        )

    except Exception as exc:

        show_message(
            "Project was created in memory, "
            f"but saving failed: {exc}",
            "error",
        )

        return


    st.session_state[
        "project_created"
    ] = project_name


    st.rerun()


# ============================================================
# MAIN PROJECT MODULE
# ============================================================

def render_projects_module(
    db,
):

    # --------------------------------------------------------
    # CREATION MESSAGE
    # --------------------------------------------------------

    created = st.session_state.pop(
        "project_created",
        None,
    )


    if created:

        show_message(
            f"Project "
            f"<strong>{created}</strong> "
            "was created successfully.",
            "success",
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
    # DATABASE
    # --------------------------------------------------------

    if not isinstance(
        db,
        dict,
    ):

        db = {}


    projects = db.setdefault(
        "projects",
        [],
    )


    if not isinstance(
        projects,
        list,
    ):

        projects = []

        db[
            "projects"
        ] = projects


    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    total = len(
        projects
    )


    active = sum(
        1
        for project in projects
        if text(
            project.get(
                "status",
                "Active",
            )
        ).lower()
        == "active"
    )


    planning = sum(
        1
        for project in projects
        if text(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "planning"
    )


    completed = sum(
        1
        for project in projects
        if text(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "completed"
    )


    portfolio_budget = sum(
        number(
            project.get(
                "budget",
                0,
            )
        )
        for project in projects
    )


    k1, k2, k3, k4, k5 = (
        st.columns(5)
    )


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
            money(
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
                        There are currently
                        no projects in the portfolio.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            search = st.text_input(
                "Search Projects",
                placeholder=(
                    "Search by project ID, "
                    "name, client, location "
                    "or manager..."
                ),
            )


            filter1, filter2 = (
                st.columns(2)
            )


            with filter1:

                status_filter = st.selectbox(
                    "Status",
                    [
                        "All"
                    ]
                    + PROJECT_STATUSES,
                )


            with filter2:

                type_filter = st.selectbox(
                    "Project Type",
                    [
                        "All"
                    ]
                    + PROJECT_TYPES,
                )


            query = (
                search or ""
            ).strip().lower()


            filtered_projects = []


            for project in projects:

                fields = [

                    "id",

                    "name",

                    "client",

                    "location",

                    "project_manager",

                ]


                searchable = " ".join(
                    text(
                        project.get(
                            field,
                            "",
                        )
                    )
                    for field in fields
                ).lower()


                if (
                    query
                    and query
                    not in searchable
                ):

                    continue


                current_status = text(
                    project.get(
                        "status",
                        "Active",
                    )
                )


                current_type = text(
                    project.get(
                        "type",
                        "",
                    )
                )


                if (
                    status_filter
                    != "All"
                    and current_status
                    != status_filter
                ):

                    continue


                if (
                    type_filter
                    != "All"
                    and current_type
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

                    <strong style="
                        color:#60A5FA;
                    ">
                        {len(filtered_projects)}
                    </strong>

                    of

                    <strong style="
                        color:#FFFFFF;
                    ">
                        {len(projects)}
                    </strong>

                    projects

                </div>
                """,
                unsafe_allow_html=True,
            )


            if not filtered_projects:

                st.markdown(
                    """
                    <div class="empty-state">

                        <div class="empty-title">
                            No Matching Projects
                        </div>

                        <div class="empty-text">
                            Try changing your
                            search or filters.
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )


            else:

                for project in (
                    filtered_projects
                ):

                    _render_project_card(
                        project
                    )


    # ========================================================
    # CREATE PROJECT
    # ========================================================

    with create_tab:

        _create_project(
            db
        )