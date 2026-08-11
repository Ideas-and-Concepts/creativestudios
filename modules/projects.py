"""
Creative Studios
Project Directory Module

AEC Collaboration Platform
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
        return date.fromisoformat(str(value))
    except (TypeError, ValueError):
        return date.today()


def get_projects(db):
    try:
        records = get_collection(db, "projects")

        if isinstance(records, list):
            return records

        return []

    except Exception:
        return []


def find_project(projects, project_id):

    for project in projects:

        if str(
            project.get("id", "")
        ) == str(project_id):

            return project

    return None


def notify(message, level="info"):
    """
    Safe notification system.

    IMPORTANT:
    Do not use st.success/st.error/st.warning with icons.
    This avoids Streamlit emoji validation errors.
    """

    border = "#2563EB"
    background = "#071B3A"

    if level == "success":
        border = "#22C55E"
        background = "#052E16"

    elif level == "error":
        border = "#EF4444"
        background = "#450A0A"

    elif level == "warning":
        border = "#F59E0B"
        background = "#422006"

    st.markdown(
        f"""
        <div style="
            background:{background};
            border:1px solid {border};
            border-left:4px solid {border};
            border-radius:8px;
            padding:11px 14px;
            color:#E2E8F0;
            font-size:13px;
            margin:10px 0;
        ">
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# STATUS BADGE
# ============================================================

def status_badge(status):

    status = str(
        status or "Active"
    )

    palette = {
        "Active": (
            "#052E16",
            "#22C55E",
        ),
        "Planning": (
            "#172554",
            "#60A5FA",
        ),
        "On Hold": (
            "#422006",
            "#F59E0B",
        ),
        "Completed": (
            "#1E1B4B",
            "#818CF8",
        ),
        "Cancelled": (
            "#450A0A",
            "#F87171",
        ),
    }

    background, foreground = palette.get(
        status,
        (
            "#1E293B",
            "#CBD5E1",
        ),
    )

    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:5px 10px;
            border-radius:999px;
            background:{background};
            color:{foreground};
            border:1px solid {foreground};
            font-size:9px;
            font-weight:850;
            letter-spacing:.7px;
            text-transform:uppercase;
        ">
            {status}
        </span>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT CARD
# ============================================================

def render_project_card(db, project):

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
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#050B18;
            border:1px solid #1E293B;
            border-left:4px solid #2563EB;
            border-radius:12px;
            padding:18px 20px 14px 20px;
            margin-top:15px;
        ">

            <div style="
                color:#FFFFFF;
                font-size:19px;
                font-weight:850;
            ">
                {name}
            </div>

            <div style="
                color:#64748B;
                font-size:11px;
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
    # STATUS
    # --------------------------------------------------------

    c1, c2 = st.columns(
        [1, 5]
    )

    with c1:

        status_badge(
            status
        )

    with c2:

        st.markdown(
            f"""
            <div style="
                color:#94A3B8;
                font-size:11px;
                padding-top:5px;
            ">
                <strong style="color:#CBD5E1;">
                    Current Phase:
                </strong>
                {phase}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # DETAILS
    # --------------------------------------------------------

    d1, d2, d3, d4 = st.columns(
        4
    )

    details = [
        ("CLIENT", client),
        ("LOCATION", location),
        ("PROJECT MANAGER", manager),
        ("BUDGET", money(budget)),
    ]


    for column, (label, value) in zip(
        [d1, d2, d3, d4],
        details,
    ):

        with column:

            st.markdown(
                f"""
                <div style="
                    background:#050B18;
                    border:1px solid #1E293B;
                    border-radius:8px;
                    padding:10px;
                    min-height:58px;
                ">

                    <div style="
                        color:#64748B;
                        font-size:8px;
                        font-weight:850;
                        letter-spacing:.7px;
                    ">
                        {label}
                    </div>

                    <div style="
                        color:#E2E8F0;
                        font-size:11px;
                        font-weight:650;
                        margin-top:5px;
                    ">
                        {value}
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
                padding:11px;
                margin-top:10px;
                color:#94A3B8;
                font-size:11px;
            ">
                <strong style="color:#CBD5E1;">
                    Scope:
                </strong>
                {description}
            </div>
            """,
            unsafe_allow_html=True,
        )


    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    a1, a2, a3 = st.columns(
        [1, 1, 4]
    )


    with a1:

        if st.button(
            "Edit",
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


    with a2:

        if st.button(
            "Delete",
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
                Register a new AEC project.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    with st.form(
        "create_project",
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

            target_date = st.date_input(
                "Target Completion",
                value=date.today(),
            )


        architect = st.text_input(
            "Lead Architect / Consultant",
        )

        description = st.text_area(
            "Project Description",
            height=100,
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

        notify(
            "Project ID is required.",
            "error",
        )

        return


    if not name:

        notify(
            "Project Name is required.",
            "error",
        )

        return


    projects = get_projects(db)


    for project in projects:

        if str(
            project.get(
                "id",
                "",
            )
        ).lower() == project_id.lower():

            notify(
                "That Project ID already exists.",
                "error",
            )

            return


    if target_date < start_date:

        notify(
            "Target completion cannot be before "
            "the start date.",
            "error",
        )

        return


    record = {
        "id": project_id,
        "name": name,
        "type": project_type,
        "status": status,
        "phase": phase,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "lead_architect": architect.strip(),
        "budget": budget,
        "contract_value": contract_value,
        "start_date": str(start_date),
        "target_completion": str(target_date),
        "description": description.strip(),
    }


    try:

        add_record(
            db,
            "projects",
            record,
        )

        notify(
            "Project created successfully.",
            "success",
        )

        st.rerun()

    except Exception as exc:

        notify(
            f"Unable to create project: {exc}",
            "error",
        )


# ============================================================
# EDIT PROJECT
# ============================================================

def edit_project_form(db, project):

    project_id = project.get(
        "id"
    )


    project_type = project.get(
        "type",
        "Commercial",
    )

    if project_type not in PROJECT_TYPES:
        project_type = "Commercial"


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


    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-title">
                Edit Project
            </div>

            <div class="section-description">
                {project_id}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    with st.form(
        f"edit_project_{project_id}"
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

            target_date = st.date_input(
                "Target Completion",
                value=safe_date(
                    project.get(
                        "target_completion"
                    )
                ),
            )


        architect = st.text_input(
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
            height=100,
        )


        save = st.form_submit_button(
            "Save Changes",
            type="primary",
            use_container_width=True,
        )


    if not save:
        return


    if not name.strip():

        notify(
            "Project Name is required.",
            "error",
        )

        return


    if target_date < start_date:

        notify(
            "Target completion cannot be before "
            "the start date.",
            "error",
        )

        return


    updates = {
        "name": name.strip(),
        "type": selected_type,
        "status": selected_status,
        "phase": selected_phase,
        "client": client.strip(),
        "location": location.strip(),
        "project_manager": manager.strip(),
        "lead_architect": architect.strip(),
        "budget": budget,
        "contract_value": contract_value,
        "start_date": str(start_date),
        "target_completion": str(target_date),
        "description": description.strip(),
    }


    try:

        result = update_record(
            db,
            "projects",
            project_id,
            updates,
        )

        if result:

            st.session_state.pop(
                "editing_project",
                None,
            )

            notify(
                "Project updated successfully.",
                "success",
            )

            st.rerun()

        else:

            notify(
                "The project could not be updated.",
                "error",
            )

    except Exception as exc:

        notify(
            f"Update failed: {exc}",
            "error",
        )


# ============================================================
# DELETE
# ============================================================

def delete_project_confirmation(
    db,
    project,
):

    project_id = project.get(
        "id"
    )

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
            border-radius:10px;
            padding:16px;
            margin:12px 0;
        ">

            <div style="
                color:#FCA5A5;
                font-size:17px;
                font-weight:800;
            ">
                Delete Project
            </div>

            <div style="
                color:#FECACA;
                font-size:12px;
                margin-top:5px;
            ">
                Delete <strong>{name}</strong>?
                This action cannot be undone.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    c1, c2 = st.columns(2)


    with c1:

        if st.button(
            "Confirm Delete",
            type="primary",
            use_container_width=True,
            key=f"confirm_{project_id}",
        ):

            try:

                result = delete_record(
                    db,
                    "projects",
                    project_id,
                )

                st.session_state.pop(
                    "deleting_project",
                    None,
                )

                if result:

                    notify(
                        "Project deleted.",
                        "success",
                    )

                else:

                    notify(
                        "Project could not be deleted.",
                        "error",
                    )

                st.rerun()

            except Exception as exc:

                notify(
                    f"Delete failed: {exc}",
                    "error",
                )


    with c2:

        if st.button(
            "Cancel",
            use_container_width=True,
            key=f"cancel_{project_id}",
        ):

            st.session_state.pop(
                "deleting_project",
                None,
            )

            st.rerun()


# ============================================================
# MAIN PROJECT MODULE
# ============================================================

def render_projects_module(db):

    projects = get_projects(
        db
    )


    # ========================================================
    # HEADER
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
    # KPI
    # ========================================================

    total = len(projects)

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

    portfolio_budget = sum(
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


    # ========================================================
    # EDIT MODE
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


    # ========================================================
    # DELETE MODE
    # ========================================================

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

            notify(
                "No projects have been created yet.",
                "info",
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
                    font-size:11px;
                    margin:12px 0;
                ">
                    Showing
                    <strong style="color:#60A5FA;">
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


            for project in filtered:

                render_project_card(
                    db,
                    project,
                )


    # ========================================================
    # CREATE
    # ========================================================

    with create:

        create_project_form(
            db
        )