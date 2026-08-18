"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Project Directory Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    get_collection,
    save_memory,
    update_record,
)


# ============================================================
# CONSTANTS
# ============================================================

PROJECT_COLLECTION = "projects"

STATUS_OPTIONS = [
    "All",
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Cancelled",
]

PROJECT_TYPES = [
    "All",
    "Commercial",
    "Residential",
    "Industrial",
    "Infrastructure",
    "Institutional",
    "Mixed Use",
    "Other",
]


# ============================================================
# CSS
# ============================================================

def _inject_project_css() -> None:
    """Inject project-module styling."""

    st.markdown(
        """
        <style>

        /* ==================================================
           PROJECT MODULE
           ================================================== */

        .cs-project-page {
            color: #E5E7EB;
        }

        .cs-project-title {
            font-size: 32px;
            font-weight: 850;
            line-height: 1.1;
            color: #FFFFFF;
            margin-bottom: 6px;
        }

        .cs-project-subtitle {
            color: #94A3B8;
            font-size: 14px;
            margin-bottom: 24px;
        }


        /* ==================================================
           KPI CARDS
           ================================================== */

        .cs-kpi {
            background: #0B0F17;
            border: 1px solid #1E293B;
            border-radius: 14px;
            padding: 18px;
            min-height: 105px;
            box-shadow: 0 8px 24px rgba(0,0,0,.20);
        }

        .cs-kpi-label {
            color: #94A3B8;
            font-size: 11px;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: .7px;
        }

        .cs-kpi-value {
            color: #FFFFFF;
            font-size: 27px;
            font-weight: 850;
            margin-top: 8px;
        }

        .cs-kpi-blue {
            color: #60A5FA;
        }


        /* ==================================================
           SECTION
           ================================================== */

        .cs-section {
            background: #080C12;
            border: 1px solid #172033;
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        .cs-section-title {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 4px;
        }

        .cs-section-subtitle {
            color: #64748B;
            font-size: 12px;
            margin-bottom: 16px;
        }


        /* ==================================================
           PROJECT CARD
           ================================================== */

        .cs-project-card {
            background: #0B0F17;
            border: 1px solid #1E293B;
            border-radius: 16px;
            padding: 20px;
            margin: 10px 0;
            transition: border-color .15s ease,
                        box-shadow .15s ease,
                        transform .15s ease;
        }

        .cs-project-card:hover {
            border-color: #2563EB;
            box-shadow: 0 10px 30px rgba(37,99,235,.12);
            transform: translateY(-1px);
        }

        .cs-project-name {
            color: #FFFFFF;
            font-size: 18px;
            font-weight: 820;
            margin-bottom: 5px;
        }

        .cs-project-meta {
            color: #64748B;
            font-size: 12px;
            margin-bottom: 14px;
        }

        .cs-project-label {
            color: #64748B;
            font-size: 10px;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: .5px;
        }

        .cs-project-value {
            color: #CBD5E1;
            font-size: 13px;
            margin-top: 3px;
        }


        /* ==================================================
           STATUS BADGES
           ================================================== */

        .cs-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: .3px;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .cs-status-active {
            color: #86EFAC;
            background: rgba(22,163,74,.14);
            border: 1px solid rgba(34,197,94,.25);
        }

        .cs-status-planning {
            color: #93C5FD;
            background: rgba(37,99,235,.15);
            border: 1px solid rgba(59,130,246,.25);
        }

        .cs-status-on-hold {
            color: #FDE68A;
            background: rgba(217,119,6,.14);
            border: 1px solid rgba(245,158,11,.25);
        }

        .cs-status-completed {
            color: #67E8F9;
            background: rgba(8,145,178,.14);
            border: 1px solid rgba(6,182,212,.25);
        }

        .cs-status-cancelled {
            color: #FDA4AF;
            background: rgba(190,24,93,.14);
            border: 1px solid rgba(244,63,94,.25);
        }

        .cs-status-default {
            color: #CBD5E1;
            background: rgba(100,116,139,.14);
            border: 1px solid rgba(100,116,139,.25);
        }


        /* ==================================================
           EMPTY STATE
           ================================================== */

        .cs-empty {
            text-align: center;
            padding: 50px 20px;
            color: #64748B;
        }

        .cs-empty-title {
            color: #CBD5E1;
            font-size: 18px;
            font-weight: 750;
            margin-bottom: 6px;
        }

        .cs-empty-text {
            color: #64748B;
            font-size: 13px;
        }


        /* ==================================================
           FORM
           ================================================== */

        .cs-form-title {
            color: #FFFFFF;
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 16px;
        }


        /* ==================================================
           STREAMLIT BUTTONS
           ================================================== */

        div.stButton > button {
            border-radius: 9px;
            border: 1px solid #26354D;
            background: #101827;
            color: #E5E7EB;
            font-weight: 700;
        }

        div.stButton > button:hover {
            border-color: #2563EB;
            color: #FFFFFF;
            background: #111C30;
        }

        div.stButton > button[kind="primary"] {
            background: #2563EB;
            border-color: #2563EB;
            color: #FFFFFF;
        }

        div.stButton > button[kind="primary"]:hover {
            background: #1D4ED8;
            border-color: #1D4ED8;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def _text(
    value: Any,
    default: str = "",
) -> str:
    """Safely convert a value to text."""

    if value is None:
        return default

    return str(value)


def _number(
    value: Any,
    default: float = 0.0,
) -> float:
    """Safely convert a value to float."""

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return default


def _money(
    value: Any,
) -> str:
    """Format project budget."""

    amount = _number(value)

    return f"${amount:,.2f}"


def _status_class(
    status: Any,
) -> str:
    """Return CSS class for a project status."""

    normalized = _text(
        status,
        "Active",
    ).strip().lower()


    mapping = {
        "active": "cs-status-active",
        "planning": "cs-status-planning",
        "on hold": "cs-status-on-hold",
        "completed": "cs-status-completed",
        "cancelled": "cs-status-cancelled",
    }


    return mapping.get(
        normalized,
        "cs-status-default",
    )


def _status_badge(
    status: Any,
) -> str:
    """Generate safe HTML status badge."""

    status_text = _text(
        status,
        "Active",
    ).strip()


    if not status_text:
        status_text = "Active"


    css_class = _status_class(
        status_text
    )


    return (
        f'<span class="cs-status {css_class}">'
        f"{status_text}"
        f"</span>"
    )


def _project_id(
    project: dict[str, Any],
) -> str:
    """Return project display ID."""

    value = (
        project.get("project_id")
        or project.get("code")
        or project.get("reference")
    )


    if value:
        return _text(value)


    project_id = project.get(
        "id"
    )


    if project_id is not None:
        return f"PRJ-{int(project_id):03d}"


    return "PRJ-NEW"


def _project_name(
    project: dict[str, Any],
) -> str:
    """Return project name."""

    return (
        _text(
            project.get("name")
        ).strip()
        or _text(
            project.get("project_name")
        ).strip()
        or "Untitled Project"
    )


def _project_type(
    project: dict[str, Any],
) -> str:
    """Return project type."""

    return (
        _text(
            project.get("project_type")
        ).strip()
        or _text(
            project.get("type")
        ).strip()
        or "Other"
    )


def _project_status(
    project: dict[str, Any],
) -> str:
    """Return project status."""

    status = (
        _text(
            project.get("status")
        ).strip()
    )


    return status or "Active"


def _project_budget(
    project: dict[str, Any],
) -> float:
    """Return project estimated budget."""

    return _number(
        project.get(
            "estimated_budget",
            project.get(
                "budget",
                0,
            ),
        )
    )


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(
    db: dict[str, Any],
    project: dict[str, Any],
) -> None:
    """
    Render one project card.

    IMPORTANT:
    This function does NOT use st.success(), st.warning(),
    st.error(), or icon="●".

    Status is rendered entirely using CSS.
    """

    name = _project_name(
        project
    )

    project_id = _project_id(
        project
    )

    project_type = _project_type(
        project
    )

    status = _project_status(
        project
    )

    client = _text(
        project.get(
            "client"
        ),
        "Not specified",
    )

    location = _text(
        project.get(
            "location"
        ),
        "Not specified",
    )

    manager = _text(
        project.get(
            "project_manager",
            project.get(
                "manager",
                "Not assigned",
            ),
        ),
        "Not assigned",
    )

    budget = _project_budget(
        project
    )


    # --------------------------------------------------------
    # CARD
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="cs-project-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:15px;
            ">

                <div style="flex:1;">

                    <div class="cs-project-name">
                        {_escape_html(name)}
                    </div>

                    <div class="cs-project-meta">
                        {_escape_html(project_id)}
                        &nbsp;•&nbsp;
                        {_escape_html(project_type)}
                    </div>

                </div>

                <div>
                    {_status_badge(status)}
                </div>

            </div>

            <div style="
                display:grid;
                grid-template-columns:
                    repeat(auto-fit,minmax(130px,1fr));
                gap:16px;
                margin-top:15px;
            ">

                <div>
                    <div class="cs-project-label">
                        Client
                    </div>

                    <div class="cs-project-value">
                        {_escape_html(client)}
                    </div>
                </div>

                <div>
                    <div class="cs-project-label">
                        Location
                    </div>

                    <div class="cs-project-value">
                        {_escape_html(location)}
                    </div>
                </div>

                <div>
                    <div class="cs-project-label">
                        Manager
                    </div>

                    <div class="cs-project-value">
                        {_escape_html(manager)}
                    </div>
                </div>

                <div>
                    <div class="cs-project-label">
                        Budget
                    </div>

                    <div class="cs-project-value">
                        {_escape_html(_money(budget))}
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------------

    project_key = project.get(
        "id"
    )


    if project_key is None:
        return


    col1, col2, col3 = st.columns(
        [1, 1, 1]
    )


    with col1:

        if st.button(
            "View",
            key=f"project_view_{project_key}",
            use_container_width=True,
        ):

            st.session_state[
                "selected_project_id"
            ] = project_key

            st.session_state[
                "project_action"
            ] = "view"

            st.rerun()


    with col2:

        if st.button(
            "Edit",
            key=f"project_edit_{project_key}",
            use_container_width=True,
        ):

            st.session_state[
                "selected_project_id"
            ] = project_key

            st.session_state[
                "project_action"
            ] = "edit"

            st.rerun()


    with col3:

        if st.button(
            "Delete",
            key=f"project_delete_{project_key}",
            use_container_width=True,
        ):

            st.session_state[
                "selected_project_id"
            ] = project_key

            st.session_state[
                "project_action"
            ] = "delete"

            st.rerun()


# ============================================================
# HTML ESCAPING
# ============================================================

def _escape_html(
    value: Any,
) -> str:
    """
    Escape user/database text before putting it into HTML.
    """

    import html

    return html.escape(
        _text(value)
    )


# ============================================================
# PROJECT FORM
# ============================================================

def _render_project_form(
    db: dict[str, Any],
    project: dict[str, Any] | None = None,
) -> None:
    """Render create/edit project form."""

    editing = project is not None


    title = (
        "Edit Project"
        if editing
        else "Create New Project"
    )


    st.markdown(
        f"""
        <div class="cs-section">
            <div class="cs-form-title">
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    existing_name = (
        _project_name(project)
        if editing
        else ""
    )

    existing_type = (
        _project_type(project)
        if editing
        else "Commercial"
    )

    existing_status = (
        _project_status(project)
        if editing
        else "Planning"
    )

    existing_client = (
        _text(
            project.get("client")
        )
        if editing
        else ""
    )

    existing_location = (
        _text(
            project.get("location")
        )
        if editing
        else ""
    )

    existing_manager = (
        _text(
            project.get(
                "project_manager",
                project.get(
                    "manager"
                ),
            )
        )
        if editing
        else ""
    )

    existing_budget = (
        _project_budget(project)
        if editing
        else 0.0
    )

    existing_description = (
        _text(
            project.get(
                "description"
            )
        )
        if editing
        else ""
    )


    with st.form(
        key=(
            "edit_project_form"
            if editing
            else "create_project_form"
        )
    ):

        col1, col2 = st.columns(
            2
        )


        with col1:

            name = st.text_input(
                "Project Name",
                value=existing_name,
                placeholder=(
                    "Grand Horizon Commercial Complex"
                ),
            )


            project_type = st.selectbox(
                "Project Type",
                PROJECT_TYPES[1:],
                index=(
                    PROJECT_TYPES[1:].index(
                        existing_type
                    )
                    if existing_type
                    in PROJECT_TYPES[1:]
                    else 0
                ),
            )


            client = st.text_input(
                "Client",
                value=existing_client,
            )


            location = st.text_input(
                "Location",
                value=existing_location,
            )


        with col2:

            status = st.selectbox(
                "Status",
                STATUS_OPTIONS[1:],
                index=(
                    STATUS_OPTIONS[1:].index(
                        existing_status
                    )
                    if existing_status
                    in STATUS_OPTIONS[1:]
                    else 0
                ),
            )


            manager = st.text_input(
                "Project Manager",
                value=existing_manager,
            )


            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=float(
                    existing_budget
                ),
                step=1000.0,
            )


        description = st.text_area(
            "Project Description",
            value=existing_description,
            placeholder=(
                "Brief description of the project..."
            ),
        )


        submitted = st.form_submit_button(
            "Update Project"
            if editing
            else "Create Project",
            type="primary",
            use_container_width=True,
        )


        if submitted:

            if not name.strip():

                st.error(
                    "Project Name is required."
                )

                return


            project_data = {
                "name": name.strip(),
                "project_name": name.strip(),
                "project_type": project_type,
                "status": status,
                "client": client.strip(),
                "location": location.strip(),
                "project_manager": manager.strip(),
                "estimated_budget": float(
                    budget
                ),
                "description": description.strip(),
                "updated_at": datetime.now().isoformat(),
            }


            if editing:

                update_record(
                    PROJECT_COLLECTION,
                    project.get("id"),
                    project_data,
                    db,
                    save=True,
                )

                st.session_state[
                    "project_action"
                ] = None

                st.success(
                    "Project updated successfully."
                )

            else:

                project_data[
                    "project_id"
                ] = (
                    f"PRJ-"
                    f"{len(get_collection(PROJECT_COLLECTION, db)) + 1:03d}"
                )

                project_data[
                    "created_at"
                ] = datetime.now().isoformat()


                add_record(
                    PROJECT_COLLECTION,
                    project_data,
                    db,
                    save=True,
                )

                st.session_state[
                    "project_action"
                ] = None

                st.success(
                    "Project created successfully."
                )


            st.rerun()


# ============================================================
# PROJECT DETAILS
# ============================================================

def _render_project_details(
    project: dict[str, Any],
) -> None:
    """Render project detail view."""

    name = _project_name(
        project
    )

    project_id = _project_id(
        project
    )

    status = _project_status(
        project
    )

    project_type = _project_type(
        project
    )

    budget = _project_budget(
        project
    )


    st.markdown(
        f"""
        <div class="cs-section">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                gap:20px;
            ">

                <div>

                    <div class="cs-project-name">
                        {_escape_html(name)}
                    </div>

                    <div class="cs-project-meta">
                        {_escape_html(project_id)}
                        &nbsp;•&nbsp;
                        {_escape_html(project_type)}
                    </div>

                </div>

                {_status_badge(status)}

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    col1, col2, col3 = st.columns(
        3
    )


    with col1:

        st.metric(
            "Estimated Budget",
            _money(budget),
        )


    with col2:

        st.metric(
            "Client",
            _text(
                project.get(
                    "client"
                ),
                "Not specified",
            ),
        )


    with col3:

        st.metric(
            "Manager",
            _text(
                project.get(
                    "project_manager",
                    project.get(
                        "manager"
                    ),
                ),
                "Not assigned",
            ),
        )


    st.markdown(
        "### Project Information"
    )


    details = {
        "Project ID": project_id,
        "Project Name": name,
        "Project Type": project_type,
        "Status": status,
        "Client": _text(
            project.get("client"),
            "Not specified",
        ),
        "Location": _text(
            project.get("location"),
            "Not specified",
        ),
        "Project Manager": _text(
            project.get(
                "project_manager",
                project.get(
                    "manager"
                ),
            ),
            "Not assigned",
        ),
        "Description": _text(
            project.get(
                "description"
            ),
            "No description provided.",
        ),
    }


    for label, value in details.items():

        c1, c2 = st.columns(
            [1, 3]
        )


        with c1:

            st.caption(
                label
            )


        with c2:

            st.write(
                value
            )


# ============================================================
# PROJECT DELETE
# ============================================================

def _render_delete_confirmation(
    db: dict[str, Any],
    project: dict[str, Any],
) -> None:
    """Render delete confirmation."""

    name = _project_name(
        project
    )


    st.warning(
        f'You are about to delete "{name}".'
    )


    col1, col2 = st.columns(
        2
    )


    with col1:

        if st.button(
            "Cancel",
            key="cancel_delete_project",
            use_container_width=True,
        ):

            st.session_state[
                "project_action"
            ] = None

            st.rerun()


    with col2:

        if st.button(
            "Delete Project",
            key="confirm_delete_project",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                PROJECT_COLLECTION,
                project.get("id"),
                db,
                save=True,
            )


            st.session_state[
                "project_action"
            ] = None

            st.session_state[
                "selected_project_id"
            ] = None

            st.success(
                "Project deleted successfully."
            )

            st.rerun()


# ============================================================
# KPI
# ============================================================

def _render_project_kpis(
    projects: list[dict[str, Any]],
) -> None:
    """Render project KPI cards."""

    total = len(
        projects
    )


    active = sum(
        1
        for project in projects
        if _project_status(project).lower()
        == "active"
    )


    planning = sum(
        1
        for project in projects
        if _project_status(project).lower()
        == "planning"
    )


    completed = sum(
        1
        for project in projects
        if _project_status(project).lower()
        == "completed"
    )


    budget = sum(
        _project_budget(project)
        for project in projects
    )


    columns = st.columns(
        5
    )


    values = [
        (
            "Total Projects",
            total,
        ),
        (
            "Active",
            active,
        ),
        (
            "Planning",
            planning,
        ),
        (
            "Completed",
            completed,
        ),
        (
            "Portfolio Budget",
            _money(budget),
        ),
    ]


    for column, (
        label,
        value,
    ) in zip(
        columns,
        values,
    ):

        with column:

            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {_escape_html(label)}
                    </div>

                    <div class="cs-kpi-value cs-kpi-blue">
                        {_escape_html(value)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# MAIN PROJECT MODULE
# ============================================================

def render_projects_module(
    db: dict[str, Any],
) -> None:
    """
    Render the complete Creative Studios Project Directory.
    """

    _inject_project_css()


    if not isinstance(
        db,
        dict,
    ):

        db = {
            "projects": []
        }


    projects = get_collection(
        PROJECT_COLLECTION,
        db,
    )


    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-project-page">

            <div class="cs-project-title">
                Project Directory
            </div>

            <div class="cs-project-subtitle">
                Central project workspace for architectural,
                engineering and construction activities.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    _render_project_kpis(
        projects
    )


    # --------------------------------------------------------
    # Active action
    # --------------------------------------------------------

    action = st.session_state.get(
        "project_action"
    )


    selected_id = st.session_state.get(
        "selected_project_id"
    )


    selected_project = None


    if selected_id is not None:

        for project in projects:

            if str(
                project.get("id")
            ) == str(
                selected_id
            ):

                selected_project = project

                break


    if action == "create":

        _render_project_form(
            db
        )

        st.divider()


    elif (
        action == "edit"
        and selected_project
    ):

        _render_project_form(
            db,
            selected_project,
        )

        st.divider()


    elif (
        action == "view"
        and selected_project
    ):

        _render_project_details(
            selected_project
        )

        st.divider()


    elif (
        action == "delete"
        and selected_project
    ):

        _render_delete_confirmation(
            db,
            selected_project,
        )

        st.divider()


    # --------------------------------------------------------
    # Project portfolio
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-section">

            <div class="cs-section-title">
                Project Portfolio
            </div>

            <div class="cs-section-subtitle">
                Search, filter and manage your active
                construction project portfolio.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # Create button
    # --------------------------------------------------------

    create_col, spacer = st.columns(
        [1, 4]
    )


    with create_col:

        if st.button(
            "Create New Project",
            type="primary",
            use_container_width=True,
        ):

            st.session_state[
                "project_action"
            ] = "create"

            st.session_state[
                "selected_project_id"
            ] = None

            st.rerun()


    st.write("")


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
            label_visibility="visible",
        )


    with status_col:

        selected_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
        )


    with type_col:

        selected_type = st.selectbox(
            "Project Type",
            PROJECT_TYPES,
        )


    # --------------------------------------------------------
    # Filtering
    # --------------------------------------------------------

    search_value = (
        search.strip().lower()
    )


    filtered_projects: list[
        dict[str, Any]
    ] = []


    for project in projects:

        if not isinstance(
            project,
            dict,
        ):

            continue


        project_status = _project_status(
            project
        )


        project_type = _project_type(
            project
        )


        # Status filter
        if (
            selected_status != "All"
            and project_status.lower()
            != selected_status.lower()
        ):

            continue


        # Type filter
        if (
            selected_type != "All"
            and project_type.lower()
            != selected_type.lower()
        ):

            continue


        # Search
        if search_value:

            searchable = " ".join(
                [
                    _text(
                        project.get(
                            "id"
                        )
                    ),
                    _text(
                        project.get(
                            "project_id"
                        )
                    ),
                    _project_name(
                        project
                    ),
                    _project_type(
                        project
                    ),
                    _text(
                        project.get(
                            "client"
                        )
                    ),
                    _text(
                        project.get(
                            "location"
                        )
                    ),
                    _text(
                        project.get(
                            "project_manager",
                            project.get(
                                "manager"
                            ),
                        )
                    ),
                ]
            ).lower()


            if search_value not in searchable:

                continue


        filtered_projects.append(
            project
        )


    # --------------------------------------------------------
    # Result count
    # --------------------------------------------------------

    st.caption(
        f"Showing {len(filtered_projects)} "
        f"of {len(projects)} projects"
    )


    # --------------------------------------------------------
    # No projects
    # --------------------------------------------------------

    if not filtered_projects:

        st.markdown(
            """
            <div class="cs-empty">

                <div class="cs-empty-title">
                    No Projects Found
                </div>

                <div class="cs-empty-text">
                    Create a project or adjust your
                    search and filters.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        return


    # --------------------------------------------------------
    # Project cards
    # --------------------------------------------------------

    for project in filtered_projects:

        _render_project_card(
            db,
            project,
        )