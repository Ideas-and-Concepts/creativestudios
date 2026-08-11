"""
Creative Studios
Project Directory

Clean, independent project management module.
"""

import streamlit as st


# ============================================================
# CONSTANTS
# ============================================================

PROJECT_TYPES = [
    "Commercial",
    "Residential",
    "Industrial",
    "Mixed-Use",
    "Hospitality",
    "Healthcare",
    "Education",
    "Infrastructure",
]


PROJECT_STATUSES = [
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Cancelled",
]


PROJECT_PHASES = [
    "Concept Design",
    "Schematic Design",
    "Design Development",
    "Construction Documents",
    "Tender / Bidding",
    "Construction",
    "Practical Completion",
    "Closed",
]


# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(
    value,
    default="",
):

    if value is None:

        return default

    return str(value)


def safe_number(
    value,
):

    try:

        return float(
            value or 0
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


def money(
    value,
):

    return (
        f"${safe_number(value):,.2f}"
    )


def status_class(
    status,
):

    value = safe_text(
        status,
        "Active",
    ).strip().lower()


    if value == "active":

        return "status-active"


    if value == "planning":

        return "status-planning"


    if value == "completed":

        return "status-completed"


    if value == "on hold":

        return "status-hold"


    if value == "cancelled":

        return "status-cancelled"


    return "status-default"


# ============================================================
# SAFE MESSAGE
# ============================================================

def message(
    text,
    kind="info",
):

    if kind == "success":

        background = "#052E16"
        border = "#166534"
        accent = "#22C55E"
        foreground = "#BBF7D0"


    elif kind == "error":

        background = "#450A0A"
        border = "#991B1B"
        accent = "#EF4444"
        foreground = "#FECACA"


    else:

        background = "#071B3A"
        border = "#1D4ED8"
        accent = "#2563EB"
        foreground = "#BFDBFE"


    st.markdown(
        f"""
        <div style="
            background:{background};
            border:1px solid {border};
            border-left:4px solid {accent};
            color:{foreground};
            border-radius:8px;
            padding:11px 14px;
            margin:10px 0;
            font-size:12px;
        ">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAVE DATABASE
# ============================================================

def save_database(
    db,
):

    """
    Attempts to use the existing database module.

    If saving is unavailable, the application continues
    operating in memory instead of crashing.
    """

    try:

        from .database import save_memory

        save_memory(
            db
        )

        return True

    except Exception:

        return False


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(
    project,
):

    project_id = safe_text(
        project.get(
            "id",
            project.get(
                "project_id",
                "N/A",
            ),
        ),
        "N/A",
    )


    name = safe_text(
        project.get(
            "name",
            project.get(
                "project_name",
                "Unnamed Project",
            ),
        ),
        "Unnamed Project",
    )


    project_type = safe_text(
        project.get(
            "type",
            project.get(
                "project_type",
                "Commercial",
            ),
        ),
        "Commercial",
    )


    status = safe_text(
        project.get(
            "status",
            "Active",
        ),
        "Active",
    )


    phase = safe_text(
        project.get(
            "phase",
            project.get(
                "project_phase",
                "Concept Design",
            ),
        ),
        "Concept Design",
    )


    client = safe_text(
        project.get(
            "client",
            project.get(
                "client_name",
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


    budget = project.get(
        "budget",
        project.get(
            "estimated_budget",
            0,
        ),
    )


    description = safe_text(
        project.get(
            "description",
            "",
        )
    )


    description_block = ""


    if description:

        description_block = f"""
        <div class="project-description">
            {description}
        </div>
        """


    st.markdown(
        f"""
        <div class="project-card">

            <div class="project-header">

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
                    status
                    {status_class(status)}
                ">
                    {status.upper()}
                </span>

            </div>


            <div class="project-phase">

                Current Phase:
                <strong>
                    {phase}
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

            {description_block}

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project(
    db,
):

    st.markdown(
        """
        <div class="page-title">
            Create New Project
        </div>

        <div class="page-subtitle">
            Register a new architectural,
            engineering or construction project.
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


            project_name = st.text_input(
                "Project Name *",
                placeholder="New Project",
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
                "Current Phase",
                PROJECT_PHASES,
            )


            manager = st.text_input(
                "Project Manager",
            )


            budget = st.number_input(
                "Project Budget ($)",
                min_value=0.0,
                value=0.0,
                step=10000.0,
            )


        description = st.text_area(
            "Project Description",
            height=100,
        )


        submit = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )


    if not submit:

        return


    project_id = (
        project_id or ""
    ).strip()


    project_name = (
        project_name or ""
    ).strip()


    if not project_id:

        message(
            "Project ID is required.",
            "error",
        )

        return


    if not project_name:

        message(
            "Project Name is required.",
            "error",
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

        db[
            "projects"
        ] = projects


    for existing in projects:

        existing_id = safe_text(
            existing.get(
                "id",
                existing.get(
                    "project_id",
                    "",
                ),
            )
        ).strip().lower()


        if (
            existing_id
            == project_id.lower()
        ):

            message(
                f"Project ID "
                f"<strong>{project_id}</strong> "
                "already exists.",
                "error",
            )

            return


    new_project = {

        "id":
            project_id,

        "project_id":
            project_id,

        "name":
            project_name,

        "project_name":
            project_name,

        "type":
            project_type,

        "project_type":
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

        "description":
            (description or "").strip(),

    }


    projects.append(
        new_project
    )


    saved = save_database(
        db
    )


    if saved:

        message(
            f"Project "
            f"<strong>{project_name}</strong> "
            "created successfully.",
            "success",
        )

    else:

        message(
            f"Project "
            f"<strong>{project_name}</strong> "
            "created successfully for this session.",
            "info",
        )


# ============================================================
# PROJECT DIRECTORY
# ============================================================

def render_projects_module(
    db,
):

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


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        """
        <div class="page-title">
            Project Directory
        </div>

        <div class="page-subtitle">
            Central project workspace for
            architectural, engineering and
            construction activities.
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # KPI
    # ========================================================

    total_projects = len(
        projects
    )


    active_projects = sum(
        1
        for project in projects
        if safe_text(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "active"
    )


    planning_projects = sum(
        1
        for project in projects
        if safe_text(
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
        if safe_text(
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
                project.get(
                    "estimated_budget",
                    0,
                ),
            )
        )
        for project in projects
    )


    c1, c2, c3, c4, c5 = (
        st.columns(5)
    )


    with c1:

        st.metric(
            "Total Projects",
            total_projects,
        )


    with c2:

        st.metric(
            "Active",
            active_projects,
        )


    with c3:

        st.metric(
            "Planning",
            planning_projects,
        )


    with c4:

        st.metric(
            "Completed",
            completed_projects,
        )


    with c5:

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


    # ========================================================
    # TABS
    # ========================================================

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
                    "Search by project ID, "
                    "name, client, location "
                    "or manager..."
                ),
                key="project_search",
            )


            f1, f2 = st.columns(2)


            with f1:

                status_filter = st.selectbox(
                    "Status",
                    [
                        "All"
                    ] + PROJECT_STATUSES,
                    key="project_status_filter",
                )


            with f2:

                type_filter = st.selectbox(
                    "Project Type",
                    [
                        "All"
                    ] + PROJECT_TYPES,
                    key="project_type_filter",
                )


            query = (
                search or ""
            ).strip().lower()


            filtered = []


            for project in projects:

                searchable = " ".join(
                    [
                        safe_text(
                            project.get(
                                "id",
                                "",
                            )
                        ),
                        safe_text(
                            project.get(
                                "name",
                                project.get(
                                    "project_name",
                                    "",
                                ),
                            )
                        ),
                        safe_text(
                            project.get(
                                "client",
                                "",
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
                                "",
                            )
                        ),
                    ]
                ).lower()


                if (
                    query
                    and query not in searchable
                ):

                    continue


                current_status = safe_text(
                    project.get(
                        "status",
                        "",
                    )
                )


                current_type = safe_text(
                    project.get(
                        "type",
                        project.get(
                            "project_type",
                            "",
                        ),
                    )
                )


                if (
                    status_filter != "All"
                    and current_status
                    != status_filter
                ):

                    continue


                if (
                    type_filter != "All"
                    and current_type
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
                    <strong style="
                        color:#60A5FA;
                    ">
                        {len(filtered)}
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


            if not filtered:

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

                for project in filtered:

                    render_project_card(
                        project
                    )


    # ========================================================
    # CREATE
    # ========================================================

    with create_tab:

        create_project(
            db
        )