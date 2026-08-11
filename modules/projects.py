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
    """Safely convert a value to float."""

    try:
        if value is None or value == "":
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def _format_currency(value):
    """Format project money values."""

    return f"${_safe_number(value):,.2f}"


def _project_exists(
    db,
    project_id,
    exclude_id=None,
):
    """Check whether a project ID already exists."""

    requested_id = str(
        project_id or ""
    ).strip().lower()

    excluded = str(
        exclude_id or ""
    ).strip().lower()

    for project in get_collection(
        db,
        "projects",
    ):

        current_id = str(
            project.get(
                "id",
                "",
            )
        ).strip().lower()

        if (
            current_id == requested_id
            and current_id != excluded
        ):
            return True

    return False


def _get_status_count(
    projects,
    status,
):
    """Count projects by status."""

    return sum(
        1
        for project in projects
        if project.get(
            "status",
            "Active",
        ) == status
    )


def _get_project_by_id(
    projects,
    project_id,
):
    """Return a project by ID."""

    for project in projects:

        if str(
            project.get(
                "id",
                "",
            )
        ) == str(project_id):

            return project

    return None


def _safe_date(
    value,
    fallback=None,
):
    """Convert stored date text into a Python date."""

    if fallback is None:
        fallback = date.today()

    if isinstance(
        value,
        date,
    ):
        return value

    try:

        return date.fromisoformat(
            str(value)
        )

    except (
        TypeError,
        ValueError,
    ):
        return fallback


def _current_username():
    """Safely obtain the current username."""

    user = st.session_state.get(
        "user"
    )

    if isinstance(
        user,
        dict,
    ):

        return str(
            user.get(
                "username",
                "System",
            )
        )

    return str(
        user or "System"
    )


# ============================================================
# STATUS BADGE
# ============================================================

def _render_status_badge(status):
    """
    Render a CSS status badge.

    This intentionally avoids Streamlit's icon parameter,
    which caused the previous application crash.
    """

    status = str(
        status or "Active"
    )

    status_styles = {

        "Active": (
            "#DCFCE7",
            "#166534",
            "●",
        ),

        "Planning": (
            "#DBEAFE",
            "#1D4ED8",
            "○",
        ),

        "On Hold": (
            "#FEF3C7",
            "#92400E",
            "Ⅱ",
        ),

        "Completed": (
            "#E0E7FF",
            "#3730A3",
            "✓",
        ),

        "Cancelled": (
            "#FEE2E2",
            "#991B1B",
            "×",
        ),
    }

    background, foreground, symbol = (
        status_styles.get(
            status,
            (
                "#E2E8F0",
                "#334155",
                "•",
            ),
        )
    )

    st.markdown(
        f"""
        <div style="
            display:inline-flex;
            align-items:center;
            gap:7px;
            padding:6px 11px;
            border-radius:999px;
            background:{background};
            color:{foreground};
            font-size:11px;
            font-weight:800;
            white-space:nowrap;
        ">
            <span>{symbol}</span>
            <span>{status}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(
    db,
    project,
):

    project_id = project.get(
        "id",
        "N/A",
    )

    project_name = project.get(
        "name",
        "Unnamed Project",
    )

    project_type = project.get(
        "type",
        "Other",
    )

    phase = project.get(
        "phase",
        "Concept Design",
    )

    status = project.get(
        "status",
        "Active",
    )

    budget = _safe_number(
        project.get(
            "budget",
            0,
        )
    )

    contract_value = _safe_number(
        project.get(
            "contract_value",
            0,
        )
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

    description = project.get(
        "description",
        "",
    )


    # --------------------------------------------------------
    # CARD
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #CBD5E1;
            border-left:5px solid #2563EB;
            border-radius:14px;
            padding:20px;
            margin:12px 0 5px 0;
            box-shadow:0 6px 20px
                rgba(15,23,42,0.07);
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:20px;
            ">

                <div>

                    <div style="
                        color:#0F172A;
                        font-size:21px;
                        font-weight:800;
                    ">
                        {project_name}
                    </div>

                    <div style="
                        color:#64748B;
                        font-size:12px;
                        margin-top:4px;
                    ">
                        {project_id} &nbsp;•&nbsp; {project_type}
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    status_col, phase_col = st.columns(
        [1, 4]
    )

    with status_col:

        _render_status_badge(
            status
        )

    with phase_col:

        st.markdown(
            f"""
            <div style="
                color:#64748B;
                font-size:12px;
                padding-top:5px;
            ">
                <strong style="color:#0F172A;">
                    Current Phase:
                </strong>
                {phase}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            "**Client**"
        )

        st.write(
            client
        )

    with col2:

        st.markdown(
            "**Location**"
        )

        st.write(
            location
        )

    with col3:

        st.markdown(
            "**Project Manager**"
        )

        st.write(
            manager
        )

    with col4:

        st.markdown(
            "**Budget**"
        )

        st.markdown(
            f"""
            <div style="
                font-size:16px;
                font-weight:800;
                color:#1D4ED8;
            ">
                {_format_currency(budget)}
            </div>
            """,
            unsafe_allow_html=True,
        )


    if description:

        st.markdown(
            f"""
            <div style="
                margin-top:8px;
                padding:10px 12px;
                background:#F8FAFC;
                border-radius:8px;
                color:#475569;
                font-size:13px;
            ">
                <strong style="color:#0F172A;">
                    Scope:
                </strong>
                {description}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    with st.expander(
        "Project Details"
    ):

        detail1, detail2 = st.columns(2)

        with detail1:

            st.markdown(
                f"""
                **Start Date:**  
                {project.get("start_date", "Not specified")}

                **Target Completion:**  
                {project.get("target_completion", "Not specified")}

                **Lead Architect:**  
                {project.get("lead_architect", "Not assigned")}
                """
            )

        with detail2:

            st.markdown(
                f"""
                **Contract Value:**  
                {_format_currency(contract_value)}

                **Created:**  
                {project.get("created_at", "Unknown")}

                **Created By:**  
                {project.get("created_by", "System")}
                """
            )


    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    edit_col, delete_col = st.columns(
        2
    )

    with edit_col:

        if st.button(
            "Edit Project",
            key=f"edit_project_{project_id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_project_id"
            ] = project_id

            st.session_state.pop(
                "delete_project_id",
                None,
            )

            st.rerun()


    with delete_col:

        if st.button(
            "Delete Project",
            key=f"delete_project_{project_id}",
            use_container_width=True,
        ):

            st.session_state[
                "delete_project_id"
            ] = project_id

            st.session_state.pop(
                "editing_project_id",
                None,
            )

            st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def _render_create_project(db):

    st.markdown(
        """
        <div style="
            background:#020617;
            color:#FFFFFF;
            padding:20px;
            border-radius:12px;
            border-left:5px solid #2563EB;
            margin-bottom:18px;
        ">
            <div style="
                font-size:21px;
                font-weight:800;
            ">
                Register New AEC Project
            </div>

            <div style="
                color:#CBD5E1;
                font-size:13px;
                margin-top:5px;
            ">
                Create the master project record that connects
                drawings, BOQ, RFIs, approvals and site records.
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

            project_name = st.text_input(
                "Project Name *",
                placeholder="Riverside Office Development",
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
                "Describe the project scope, objectives "
                "and major works."
            ),
            height=120,
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
        "created_at": str(
            date.today()
        ),
        "created_by": _current_username(),
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

def _render_edit_project(
    db,
    project,
):

    st.markdown(
        f"""
        <div style="
            background:#020617;
            color:#FFFFFF;
            padding:18px 20px;
            border-radius:12px;
            border-left:5px solid #2563EB;
            margin-bottom:18px;
        ">
            <div style="
                font-size:20px;
                font-weight:800;
            ">
                Edit Project
            </div>

            <div style="
                color:#93C5FD;
                font-size:13px;
                margin-top:3px;
            ">
                {project.get("id", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    project_type_value = project.get(
        "type",
        PROJECT_TYPES[0],
    )

    if project_type_value not in PROJECT_TYPES:
        project_type_value = PROJECT_TYPES[0]


    status_value = project.get(
        "status",
        "Active",
    )

    if status_value not in PROJECT_STATUSES:
        status_value = "Active"


    phase_value = project.get(
        "phase",
        PROJECT_PHASES[0],
    )

    if phase_value not in PROJECT_PHASES:
        phase_value = PROJECT_PHASES[0]


    with st.form(
        f"edit_project_form_{project.get('id')}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_name = st.text_input(
                "Project Name *",
                value=str(
                    project.get(
                        "name",
                        "",
                    )
                ),
            )

            project_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES,
                index=PROJECT_TYPES.index(
                    project_type_value
                ),
            )

            client = st.text_input(
                "Client / Developer",
                value=str(
                    project.get(
                        "client",
                        "",
                    )
                ),
            )

            location = st.text_input(
                "Project Location",
                value=str(
                    project.get(
                        "location",
                        "",
                    )
                ),
            )

            project_manager = st.text_input(
                "Project Manager",
                value=str(
                    project.get(
                        "project_manager",
                        "",
                    )
                ),
            )

        with col2:

            status = st.selectbox(
                "Project Status",
                PROJECT_STATUSES,
                index=PROJECT_STATUSES.index(
                    status_value
                ),
            )

            phase = st.selectbox(
                "Lifecycle Phase",
                PROJECT_PHASES,
                index=PROJECT_PHASES.index(
                    phase_value
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

            start_date = st.date_input(
                "Project Start Date",
                value=_safe_date(
                    project.get(
                        "start_date"
                    )
                ),
            )

            target_completion = st.date_input(
                "Target Completion Date",
                value=_safe_date(
                    project.get(
                        "target_completion"
                    )
                ),
            )

            lead_architect = st.text_input(
                "Lead Architect / Consultant",
                value=str(
                    project.get(
                        "lead_architect",
                        "",
                    )
                ),
            )


        description = st.text_area(
            "Project Scope & Description",
            value=str(
                project.get(
                    "description",
                    "",
                )
            ),
            height=120,
        )


        save_col, cancel_col = st.columns(
            2
        )

        with save_col:

            save_changes = st.form_submit_button(
                "Save Changes",
                type="primary",
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


    success = update_record(
        db,
        "projects",
        project.get("id"),
        updates,
    )


    if success:

        st.session_state.pop(
            "editing_project_id",
            None,
        )

        st.success(
            "Project updated successfully."
        )

        st.rerun()

    else:

        st.error(
            "The project could not be updated."
        )


# ============================================================
# DELETE CONFIRMATION
# ============================================================

def _render_delete_confirmation(
    db,
    project,
):

    project_name = project.get(
        "name",
        "this project",
    )

    st.markdown(
        f"""
        <div style="
            background:#FEF2F2;
            border:1px solid #FECACA;
            border-left:5px solid #DC2626;
            padding:18px;
            border-radius:12px;
            margin-bottom:15px;
        ">

            <div style="
                color:#991B1B;
                font-size:18px;
                font-weight:800;
            ">
                Delete Project
            </div>

            <div style="
                color:#7F1D1D;
                font-size:13px;
                margin-top:5px;
            ">
                You are about to delete:
                <strong>{project_name}</strong>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.warning(
        "This removes the project record from the "
        "current database."
    )


    confirm_col, cancel_col = st.columns(
        2
    )


    with confirm_col:

        if st.button(
            "Yes, Delete Project",
            type="primary",
            use_container_width=True,
            key="confirm_project_delete",
        ):

            deleted = delete_record(
                db,
                "projects",
                project.get("id"),
            )

            st.session_state.pop(
                "delete_project_id",
                None,
            )

            if deleted:

                st.success(
                    "Project deleted successfully."
                )

            else:

                st.error(
                    "The project could not be deleted."
                )

            st.rerun()


    with cancel_col:

        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_project_delete",
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


    # ========================================================
    # HEADER
    # ========================================================

    st.markdown(
        """
        <div style="
            background:
                linear-gradient(
                    135deg,
                    #020617 0%,
                    #0F172A 60%,
                    #172554 100%
                );

            padding:28px 30px;

            border-radius:16px;

            border-left:6px solid #2563EB;

            margin-bottom:22px;

            box-shadow:
                0 12px 30px
                rgba(15,23,42,0.15);
        ">

            <div style="
                color:#FFFFFF;
                font-size:30px;
                font-weight:850;
            ">
                Project Directory
            </div>

            <div style="
                color:#BFDBFE;
                font-size:14px;
                margin-top:6px;
            ">
                Central project workspace for architectural,
                engineering and construction activities.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # KPI DASHBOARD
    # ========================================================

    total_projects = len(
        projects
    )

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

    portfolio_budget = sum(
        _safe_number(
            project.get(
                "budget",
                0,
            )
        )
        for project in projects
    )


    k1, k2, k3, k4, k5 = st.columns(
        5
    )


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
            _format_currency(
                portfolio_budget
            ),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # ========================================================
    # EDIT MODE
    # ========================================================

    editing_id = st.session_state.get(
        "editing_project_id"
    )

    if editing_id:

        project = _get_project_by_id(
            projects,
            editing_id,
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


    # ========================================================
    # DELETE MODE
    # ========================================================

    deleting_id = st.session_state.get(
        "delete_project_id"
    )

    if deleting_id:

        project = _get_project_by_id(
            projects,
            deleting_id,
        )

        if project:

            _render_delete_confirmation(
                db,
                project,
            )

            st.divider()

        else:

            st.session_state.pop(
                "delete_project_id",
                None,
            )


    # ========================================================
    # MAIN TABS
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
                <div style="
                    background:#FFFFFF;
                    border:1px solid #CBD5E1;
                    border-radius:14px;
                    padding:35px;
                    text-align:center;
                ">

                    <div style="
                        color:#0F172A;
                        font-size:20px;
                        font-weight:800;
                    ">
                        No Projects Yet
                    </div>

                    <div style="
                        color:#64748B;
                        font-size:13px;
                        margin-top:6px;
                    ">
                        Create your first AEC project
                        from the Create New Project tab.
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
                key="project_search",
            )


            filter_col1, filter_col2 = st.columns(
                2
            )


            with filter_col1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"] + PROJECT_STATUSES,
                    key="project_status_filter",
                )


            with filter_col2:

                type_filter = st.selectbox(
                    "Project Type",
                    ["All"] + PROJECT_TYPES,
                    key="project_type_filter",
                )


            search_term = (
                search or ""
            ).strip().lower()


            filtered_projects = []


            for project in projects:

                searchable_fields = [

                    project.get(
                        "id",
                        "",
                    ),

                    project.get(
                        "name",
                        "",
                    ),

                    project.get(
                        "client",
                        "",
                    ),

                    project.get(
                        "location",
                        "",
                    ),

                    project.get(
                        "project_manager",
                        "",
                    ),

                ]


                searchable = " ".join(
                    str(value)
                    for value in searchable_fields
                ).lower()


                if (
                    search_term
                    and search_term
                    not in searchable
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


            if not filtered_projects:

                st.info(
                    "No projects match the selected filters."
                )


            for project in filtered_projects:

                _render_project_card(
                    db,
                    project,
                )


    # ========================================================
    # CREATE
    # ========================================================

    with create_tab:

        _render_create_project(
            db
        )