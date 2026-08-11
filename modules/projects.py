"""
Creative Studios
Project Directory Module

AEC Project Management
"""

from datetime import date

import streamlit as st

from .database import (
    get_collection,
    add_record,
    update_record,
    delete_record,
)


# ============================================================
# CONSTANTS
# ============================================================

PROJECT_TYPES = [
    "Commercial",
    "Residential",
    "Industrial",
    "Infrastructure",
    "Mixed-Use",
    "Hospitality",
    "Healthcare",
    "Education",
    "Other",
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
    "Tender / Procurement",
    "Construction",
    "Practical Completion",
    "Closed",
]


# ============================================================
# HELPERS
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default

        return float(value)

    except (TypeError, ValueError):
        return default


def money(value):
    return f"${safe_float(value):,.2f}"


def safe_date(value):
    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(
            str(value)
        )
    except (TypeError, ValueError):
        return date.today()


def get_projects(db):
    projects = get_collection(
        db,
        "projects",
    )

    if not isinstance(projects, list):
        return []

    return projects


def find_project(
    projects,
    project_id,
):
    for project in projects:

        if str(
            project.get(
                "id",
                "",
            )
        ) == str(project_id):

            return project

    return None


def current_user():
    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):

        return user.get(
            "username",
            "system",
        )

    return str(
        user or "system"
    )


# ============================================================
# STATUS BADGE
# ============================================================

def render_status(status):

    status = str(
        status or "Active"
    )

    styles = {

        "Active": (
            "#052E16",
            "#22C55E",
            "ACTIVE",
        ),

        "Planning": (
            "#172554",
            "#60A5FA",
            "PLANNING",
        ),

        "On Hold": (
            "#422006",
            "#F59E0B",
            "ON HOLD",
        ),

        "Completed": (
            "#1E1B4B",
            "#818CF8",
            "COMPLETED",
        ),

        "Cancelled": (
            "#450A0A",
            "#F87171",
            "CANCELLED",
        ),
    }

    background, foreground, label = styles.get(
        status,
        (
            "#1E293B",
            "#CBD5E1",
            status.upper(),
        ),
    )

    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:5px 10px;
            border-radius:20px;
            background:{background};
            color:{foreground};
            border:1px solid {foreground};
            font-size:10px;
            font-weight:800;
            letter-spacing:.5px;
        ">
            {label}
        </span>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(
    db,
    project,
):

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
        "Other",
    )

    status = project.get(
        "status",
        "Active",
    )

    phase = project.get(
        "phase",
        "Concept Design",
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


    # --------------------------------------------------------
    # CARD HEADER
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#0B1120;
            border:1px solid #1E293B;
            border-left:4px solid #2563EB;
            border-radius:12px;
            padding:18px 20px;
            margin-top:15px;
        ">

            <div style="
                color:#FFFFFF;
                font-size:20px;
                font-weight:800;
            ">
                {name}
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:5px;
            ">
                {project_id}
                &nbsp;•&nbsp;
                {project_type}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # STATUS / PHASE
    # --------------------------------------------------------

    col_status, col_phase = st.columns(
        [1, 4]
    )

    with col_status:

        render_status(
            status
        )

    with col_phase:

        st.markdown(
            f"""
            <div style="
                color:#94A3B8;
                padding-top:5px;
                font-size:12px;
            ">
                <strong style="color:#E2E8F0;">
                    Phase:
                </strong>
                {phase}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(
        4
    )

    with c1:

        st.markdown(
            """
            <div class="dark-info">
                <div class="dark-label">
                    CLIENT
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
                <div class="dark-value">
                    {client}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    with c2:

        st.markdown(
            """
            <div class="dark-info">
                <div class="dark-label">
                    LOCATION
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
                <div class="dark-value">
                    {location}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    with c3:

        st.markdown(
            """
            <div class="dark-info">
                <div class="dark-label">
                    PROJECT MANAGER
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
                <div class="dark-value">
                    {manager}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    with c4:

        st.markdown(
            """
            <div class="dark-info">
                <div class="dark-label">
                    BUDGET
                </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
                <div class="dark-value blue-value">
                    {money(budget)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


    if description:

        st.markdown(
            f"""
            <div style="
                background:#020617;
                border:1px solid #1E293B;
                border-radius:8px;
                padding:12px;
                margin-top:10px;
                color:#94A3B8;
                font-size:12px;
            ">
                <strong style="color:#E2E8F0;">
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

        d1, d2 = st.columns(2)

        with d1:

            st.markdown(
                f"""
                **Project ID:** {project_id}

                **Project Type:** {project_type}

                **Client:** {client}

                **Location:** {location}

                **Project Manager:** {manager}

                **Lead Architect:** {
                    project.get(
                        "lead_architect",
                        "Not assigned",
                    )
                }
                """
            )

        with d2:

            st.markdown(
                f"""
                **Status:** {status}

                **Phase:** {phase}

                **Budget:** {money(budget)}

                **Contract Value:** {
                    money(
                        project.get(
                            "contract_value",
                            0,
                        )
                    )
                }

                **Start Date:** {
                    project.get(
                        "start_date",
                        "Not specified",
                    )
                }

                **Target Completion:** {
                    project.get(
                        "target_completion",
                        "Not specified",
                    )
                }
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
            key=f"edit_{project_id}",
            use_container_width=True,
        ):

            st.session_state[
                "editing_project"
            ] = project_id

            st.session_state.pop(
                "deleting_project",
                None,
            )

            st.rerun()


    with delete_col:

        if st.button(
            "Delete Project",
            key=f"delete_{project_id}",
            use_container_width=True,
        ):

            st.session_state[
                "deleting_project"
            ] = project_id

            st.session_state.pop(
                "editing_project",
                None,
            )

            st.rerun()


# ============================================================
# CREATE PROJECT
# ============================================================

def create_project_form(db):

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

        c1, c2 = st.columns(2)

        with c1:

            project_id = st.text_input(
                "Project ID *",
                placeholder="PRJ-002",
            )

            name = st.text_input(
                "Project Name *",
                placeholder="New Commercial Development",
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

            manager = st.text_input(
                "Project Manager",
            )

        with c2:

            status = st.selectbox(
                "Status",
                PROJECT_STATUSES,
                index=1,
            )

            phase = st.selectbox(
                "Project Phase",
                PROJECT_PHASES,
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                step=10000.0,
            )

            contract_value = st.number_input(
                "Contract Value",
                min_value=0.0,
                step=10000.0,
            )

            start_date = st.date_input(
                "Start Date",
                value=date.today(),
            )

            completion_date = st.date_input(
                "Target Completion",
                value=date.today(),
            )


        lead_architect = st.text_input(
            "Lead Architect / Consultant"
        )


        description = st.text_area(
            "Project Description",
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
    name = name.strip()


    if not project_id:

        st.error(
            "Project ID is required."
        )

        return


    if not name:

        st.error(
            "Project Name is required."
        )

        return


    existing = get_projects(
        db
    )


    for project in existing:

        if str(
            project.get(
                "id",
                "",
            )
        ).lower() == project_id.lower():

            st.error(
                "That Project ID already exists."
            )

            return


    if completion_date < start_date:

        st.error(
            "Target completion cannot be "
            "before the start date."
        )

        return


    new_project = {
        "id": project_id,
        "name": name,
        "type": project_type,
        "status": status,
        "phase": phase,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "lead_architect": lead_architect.strip(),
        "budget": budget,
        "contract_value": contract_value,
        "start_date": str(start_date),
        "target_completion": str(
            completion_date
        ),
        "description": description.strip(),
        "created_by": current_user(),
        "created_at": str(
            date.today()
        ),
    }


    add_record(
        db,
        "projects",
        new_project,
    )


    st.success(
        "Project created successfully."
    )

    st.rerun()


# ============================================================
# EDIT PROJECT
# ============================================================

def edit_project_form(
    db,
    project,
):

    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">
                Edit Project
            </div>

            <div class="section-description">
                {project.get("id", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    project_type = project.get(
        "type",
        PROJECT_TYPES[0],
    )

    if project_type not in PROJECT_TYPES:
        project_type = PROJECT_TYPES[0]


    status = project.get(
        "status",
        "Active",
    )

    if status not in PROJECT_STATUSES:
        status = "Active"


    phase = project.get(
        "phase",
        PROJECT_PHASES[0],
    )

    if phase not in PROJECT_PHASES:
        phase = PROJECT_PHASES[0]


    with st.form(
        f"edit_form_{project.get('id')}"
    ):

        c1, c2 = st.columns(2)

        with c1:

            name = st.text_input(
                "Project Name *",
                value=str(
                    project.get(
                        "name",
                        "",
                    )
                ),
            )

            selected_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES,
                index=PROJECT_TYPES.index(
                    project_type
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
                "Location",
                value=str(
                    project.get(
                        "location",
                        "",
                    )
                ),
            )

            manager = st.text_input(
                "Project Manager",
                value=str(
                    project.get(
                        "project_manager",
                        "",
                    )
                ),
            )

        with c2:

            selected_status = st.selectbox(
                "Status",
                PROJECT_STATUSES,
                index=PROJECT_STATUSES.index(
                    status
                ),
            )

            selected_phase = st.selectbox(
                "Project Phase",
                PROJECT_PHASES,
                index=PROJECT_PHASES.index(
                    phase
                ),
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=safe_float(
                    project.get(
                        "budget",
                        0,
                    )
                ),
                step=10000.0,
            )

            contract_value = st.number_input(
                "Contract Value",
                min_value=0.0,
                value=safe_float(
                    project.get(
                        "contract_value",
                        0,
                    )
                ),
                step=10000.0,
            )

            start_date = st.date_input(
                "Start Date",
                value=safe_date(
                    project.get(
                        "start_date"
                    )
                ),
            )

            completion_date = st.date_input(
                "Target Completion",
                value=safe_date(
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
            "Project Description",
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

            save = st.form_submit_button(
                "Save Changes",
                type="primary",
                use_container_width=True,
            )


        with cancel_col:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )


    if cancel:

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.rerun()


    if not save:
        return


    name = name.strip()


    if not name:

        st.error(
            "Project Name is required."
        )

        return


    if completion_date < start_date:

        st.error(
            "Target completion cannot be "
            "before the start date."
        )

        return


    updates = {
        "name": name,
        "type": selected_type,
        "status": selected_status,
        "phase": selected_phase,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "lead_architect": lead_architect.strip(),
        "budget": budget,
        "contract_value": contract_value,
        "start_date": str(start_date),
        "target_completion": str(
            completion_date
        ),
        "description": description.strip(),
    }


    result = update_record(
        db,
        "projects",
        project.get("id"),
        updates,
    )


    if result:

        st.session_state.pop(
            "editing_project",
            None,
        )

        st.success(
            "Project updated successfully."
        )

        st.rerun()

    else:

        st.error(
            "Unable to update the project."
        )


# ============================================================
# DELETE PROJECT
# ============================================================

def delete_project_confirmation(
    db,
    project,
):

    name = project.get(
        "name",
        "this project",
    )


    st.markdown(
        f"""
        <div style="
            background:#1C0A0A;
            border:1px solid #7F1D1D;
            border-left:4px solid #EF4444;
            padding:18px;
            border-radius:10px;
        ">

            <div style="
                color:#FCA5A5;
                font-size:18px;
                font-weight:800;
            ">
                Delete Project
            </div>

            <div style="
                color:#FECACA;
                margin-top:6px;
                font-size:13px;
            ">
                Delete <strong>{name}</strong>?
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.warning(
        "This action removes the project record."
    )


    yes_col, no_col = st.columns(
        2
    )


    with yes_col:

        if st.button(
            "Confirm Delete",
            type="primary",
            use_container_width=True,
            key="confirm_delete",
        ):

            result = delete_record(
                db,
                "projects",
                project.get("id"),
            )

            st.session_state.pop(
                "deleting_project",
                None,
            )

            if result:

                st.success(
                    "Project deleted."
                )

            else:

                st.error(
                    "Unable to delete project."
                )

            st.rerun()


    with no_col:

        if st.button(
            "Cancel",
            use_container_width=True,
            key="cancel_delete",
        ):

            st.session_state.pop(
                "deleting_project",
                None,
            )

            st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_projects_module(db):

    projects = get_projects(
        db
    )


    # ========================================================
    # PAGE HEADER
    # ========================================================

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


    # ========================================================
    # KPIs
    # ========================================================

    total = len(
        projects
    )

    active = sum(
        1
        for p in projects
        if p.get(
            "status",
            "Active",
        ) == "Active"
    )

    planning = sum(
        1
        for p in projects
        if p.get(
            "status",
            "",
        ) == "Planning"
    )

    completed = sum(
        1
        for p in projects
        if p.get(
            "status",
            "",
        ) == "Completed"
    )

    total_budget = sum(
        safe_float(
            p.get(
                "budget",
                0,
            )
        )
        for p in projects
    )


    k1, k2, k3, k4, k5 = st.columns(
        5
    )


    with k1:
        st.metric(
            "TOTAL PROJECTS",
            total,
        )


    with k2:
        st.metric(
            "ACTIVE",
            active,
        )


    with k3:
        st.metric(
            "PLANNING",
            planning,
        )


    with k4:
        st.metric(
            "COMPLETED",
            completed,
        )


    with k5:
        st.metric(
            "PORTFOLIO BUDGET",
            money(total_budget),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    # ========================================================
    # EDIT / DELETE PANELS
    # ========================================================

    editing_id = st.session_state.get(
        "editing_project"
    )

    if editing_id:

        project = find_project(
            projects,
            editing_id,
        )

        if project:

            edit_project_form(
                db,
                project,
            )

            st.divider()


    deleting_id = st.session_state.get(
        "deleting_project"
    )

    if deleting_id:

        project = find_project(
            projects,
            deleting_id,
        )

        if project:

            delete_project_confirmation(
                db,
                project,
            )

            st.divider()


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

            st.info(
                "No projects have been created yet."
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


            f1, f2 = st.columns(
                2
            )


            with f1:

                status_filter = st.selectbox(
                    "Status",
                    ["All"] + PROJECT_STATUSES,
                    key="status_filter",
                )


            with f2:

                type_filter = st.selectbox(
                    "Project Type",
                    ["All"] + PROJECT_TYPES,
                    key="type_filter",
                )


            search = (
                search or ""
            ).strip().lower()


            filtered = []


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
                        "Other",
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
                    margin:12px 0;
                ">
                    Showing
                    <strong style="color:#2563EB;">
                        {len(filtered)}
                    </strong>
                    of
                    <strong style="color:#E2E8F0;">
                        {len(projects)}
                    </strong>
                    projects
                </div>
                """,
                unsafe_allow_html=True,
            )


            if not filtered:

                st.info(
                    "No projects match your search."
                )


            for project in filtered:

                render_project_card(
                    db,
                    project,
                )


    # ========================================================
    # CREATE
    # ========================================================

    with create_tab:

        create_project_form(
            db
        )