"""
Creative Studios
AEC Collaboration Platform
Project Directory Module

Full JSON-backed Project Directory CRUD.

Database contract:
    modules.database.load_memory()
    modules.database.save_memory()
    modules.database.add_record()
    modules.database.update_record()
    modules.database.delete_record()
    modules.database.next_id()

This module does not manage authentication or sidebar navigation.
"""

from modules.branding import render_module_header

from __future__ import annotations

from datetime import date, datetime
from typing import Any

import streamlit as st

from modules.database import (
    add_record,
    delete_record,
    load_memory,
    next_id,
    save_memory,
    update_record,
)


# ============================================================
# CONSTANTS
# ============================================================

PROJECT_COLLECTION = "projects"

PROJECT_STATUSES = [
    "Active",
    "Planning",
    "On Hold",
    "Completed",
    "Cancelled",
]

PROJECT_TYPES = [
    "Commercial",
    "Residential",
    "Industrial",
    "Infrastructure",
    "Institutional",
    "Renovation",
    "Other",
]


# ============================================================
# CSS
# ============================================================

def _inject_project_css() -> None:
    st.markdown(
        """
<style>

.cs-project-header {
    margin-bottom: 24px;
}

.cs-project-title {
    color: #F8FAFC;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.7px;
}

.cs-project-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
}

.cs-project-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 20px;
    margin-top: 14px;
}

.cs-project-card:hover {
    border-color: #2563EB;
}

.cs-project-name {
    color: #FFFFFF;
    font-size: 18px;
    font-weight: 850;
}

.cs-project-meta {
    color: #64748B;
    font-size: 11px;
    margin-top: 5px;
}

.cs-project-info {
    color: #CBD5E1;
    font-size: 12px;
    margin-top: 5px;
}

.cs-project-budget {
    color: #60A5FA;
    font-size: 17px;
    font-weight: 850;
}

.cs-status {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 850;
    border: 1px solid transparent;
}

.cs-status-active {
    color: #60A5FA;
    background: rgba(37,99,235,0.15);
    border-color: rgba(37,99,235,0.35);
}

.cs-status-planning {
    color: #93C5FD;
    background: rgba(30,64,175,0.15);
    border-color: rgba(30,64,175,0.35);
}

.cs-status-hold {
    color: #CBD5E1;
    background: rgba(71,85,105,0.18);
    border-color: rgba(71,85,105,0.35);
}

.cs-status-completed {
    color: #BFDBFE;
    background: rgba(30,58,138,0.20);
    border-color: rgba(30,58,138,0.40);
}

.cs-status-cancelled {
    color: #94A3B8;
    background: rgba(15,23,42,0.50);
    border-color: #334155;
}

.cs-project-empty {
    background: #0B0F17;
    border: 1px dashed #1E293B;
    border-radius: 15px;
    padding: 40px;
    text-align: center;
    color: #64748B;
}

.cs-project-section {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 850;
    margin-bottom: 12px;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# GENERAL HELPERS
# ============================================================

def _safe_text(
    value: Any,
    default: str = "",
) -> str:

    if value is None:
        return default

    return str(value).strip()


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    if value is None:
        return default

    if isinstance(
        value,
        bool,
    ):
        return default

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _format_money(
    value: Any,
) -> str:

    amount = _safe_float(value)

    return f"${amount:,.2f}"


def _safe_date(
    value: Any,
) -> date | None:

    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value.date()

    if isinstance(
        value,
        date,
    ):
        return value

    text = _safe_text(value)

    if not text:
        return None

    for fmt in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ):

        try:
            return datetime.strptime(
                text,
                fmt,
            ).date()

        except ValueError:
            continue

    return None


def _date_string(
    value: Any,
) -> str:

    parsed = _safe_date(value)

    if parsed is None:
        return ""

    return parsed.isoformat()


def _project_status(
    project: dict[str, Any],
) -> str:

    status = _safe_text(
        project.get(
            "status",
            "Planning",
        )
    )

    if status not in PROJECT_STATUSES:
        return "Planning"

    return status


def _status_css_class(
    status: str,
) -> str:

    normalized = status.lower()

    if normalized == "active":
        return "cs-status-active"

    if normalized == "planning":
        return "cs-status-planning"

    if normalized == "on hold":
        return "cs-status-hold"

    if normalized == "completed":
        return "cs-status-completed"

    if normalized == "cancelled":
        return "cs-status-cancelled"

    return "cs-status-planning"


# ============================================================
# DATABASE HELPERS
# ============================================================

def _get_projects(
    db: dict[str, Any] | None,
) -> list[dict[str, Any]]:

    if not isinstance(
        db,
        dict,
    ):
        db = load_memory()

    projects = db.get(
        PROJECT_COLLECTION,
        [],
    )

    if not isinstance(
        projects,
        list,
    ):
        projects = []

        db[
            PROJECT_COLLECTION
        ] = projects

        save_memory(db)

    valid_projects = []

    for project in projects:

        if isinstance(
            project,
            dict,
        ):
            valid_projects.append(
                project
            )

    return valid_projects


def _project_exists(
    db: dict[str, Any],
    project_id: str,
    exclude_id: Any = None,
) -> bool:

    target = project_id.strip().lower()

    for project in _get_projects(db):

        existing_id = _safe_text(
            project.get(
                "project_id",
                "",
            )
        ).lower()

        if existing_id != target:
            continue

        if (
            exclude_id is not None
            and str(
                project.get("id")
            )
            == str(exclude_id)
        ):
            continue

        return True

    return False


# ============================================================
# VALIDATION
# ============================================================

def _validate_project(
    db: dict[str, Any],
    project_id: str,
    project_name: str,
    client: str,
    location: str,
    manager: str,
    project_type: str,
    status: str,
    budget: Any,
    start_date: Any,
    end_date: Any,
    exclude_id: Any = None,
) -> list[str]:

    errors: list[str] = []

    project_id = _safe_text(
        project_id
    )

    project_name = _safe_text(
        project_name
    )

    client = _safe_text(
        client
    )

    location = _safe_text(
        location
    )

    manager = _safe_text(
        manager
    )

    if not project_id:
        errors.append(
            "Project ID is required."
        )

    elif len(project_id) > 50:
        errors.append(
            "Project ID cannot exceed 50 characters."
        )

    elif _project_exists(
        db,
        project_id,
        exclude_id,
    ):
        errors.append(
            "A project with this Project ID already exists."
        )

    if not project_name:
        errors.append(
            "Project Name is required."
        )

    elif len(project_name) > 200:
        errors.append(
            "Project Name cannot exceed 200 characters."
        )

    if not client:
        errors.append(
            "Client is required."
        )

    if not location:
        errors.append(
            "Location is required."
        )

    if not manager:
        errors.append(
            "Project Manager is required."
        )

    if project_type not in PROJECT_TYPES:
        errors.append(
            "Please select a valid Project Type."
        )

    if status not in PROJECT_STATUSES:
        errors.append(
            "Please select a valid Project Status."
        )

    try:

        numeric_budget = float(
            budget
        )

        if numeric_budget < 0:
            errors.append(
                "Estimated Budget cannot be negative."
            )

    except (
        TypeError,
        ValueError,
    ):

        errors.append(
            "Estimated Budget must be a valid number."
        )

    parsed_start = _safe_date(
        start_date
    )

    parsed_end = _safe_date(
        end_date
    )

    if start_date and parsed_start is None:
        errors.append(
            "Start Date is invalid."
        )

    if end_date and parsed_end is None:
        errors.append(
            "End Date is invalid."
        )

    if (
        parsed_start is not None
        and parsed_end is not None
        and parsed_end < parsed_start
    ):

        errors.append(
            "End Date cannot be before Start Date."
        )

    return errors


# ============================================================
# PROJECT CREATE
# ============================================================

def _create_project(
    db: dict[str, Any],
    project_id: str,
    project_name: str,
    client: str,
    location: str,
    manager: str,
    project_type: str,
    status: str,
    budget: float,
    start_date: date | None,
    end_date: date | None,
    description: str,
) -> dict[str, Any]:

    now = datetime.now().isoformat()

    project = {
        "id": next_id(
            PROJECT_COLLECTION,
            db,
        ),
        "project_id": project_id.strip(),
        "name": project_name.strip(),
        "project_name": project_name.strip(),
        "client": client.strip(),
        "location": location.strip(),
        "manager": manager.strip(),
        "project_manager": manager.strip(),
        "project_type": project_type,
        "status": status,
        "estimated_budget": float(
            budget
        ),
        "budget": float(
            budget
        ),
        "start_date": (
            start_date.isoformat()
            if start_date
            else ""
        ),
        "end_date": (
            end_date.isoformat()
            if end_date
            else ""
        ),
        "description": description.strip(),
        "created_at": now,
        "updated_at": now,
    }

    return add_record(
        PROJECT_COLLECTION,
        project,
        db,
    )


# ============================================================
# CREATE FORM
# ============================================================

def _render_create_form(
    db: dict[str, Any],
) -> None:

    st.markdown(
        '<div class="cs-project-section">'
        "Create New Project"
        "</div>",
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
                placeholder="Project name",
            )

            client = st.text_input(
                "Client *",
                placeholder="Client / organization",
            )

            location = st.text_input(
                "Location *",
                placeholder="Project location",
            )

            manager = st.text_input(
                "Project Manager *",
                placeholder="Project manager",
            )

        with col2:

            project_type = st.selectbox(
                "Project Type *",
                PROJECT_TYPES,
            )

            status = st.selectbox(
                "Status *",
                PROJECT_STATUSES,
                index=1,
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=0.0,
                step=1000.0,
            )

            start_date = st.date_input(
                "Start Date",
                value=None,
            )

            end_date = st.date_input(
                "End Date",
                value=None,
            )

        description = st.text_area(
            "Description",
            placeholder=(
                "Brief project description..."
            ),
            height=110,
        )

        submitted = st.form_submit_button(
            "Create Project",
            use_container_width=True,
        )

    if not submitted:
        return

    errors = _validate_project(
        db,
        project_id,
        project_name,
        client,
        location,
        manager,
        project_type,
        status,
        budget,
        start_date,
        end_date,
    )

    if errors:

        for error in errors:
            st.error(error)

        return

    try:

        _create_project(
            db=db,
            project_id=project_id,
            project_name=project_name,
            client=client,
            location=location,
            manager=manager,
            project_type=project_type,
            status=status,
            budget=float(budget),
            start_date=start_date,
            end_date=end_date,
            description=description,
        )

        st.success(
            "Project created successfully."
        )

        st.rerun()

    except Exception as exc:

        st.error(
            "Unable to create the project."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# EDIT FORM
# ============================================================

def _render_edit_form(
    db: dict[str, Any],
    project: dict[str, Any],
) -> None:

    project_db_id = project.get(
        "id"
    )

    st.markdown(
        '<div class="cs-project-section">'
        "Edit Project"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.form(
        f"edit_project_{project_db_id}",
    ):

        col1, col2 = st.columns(2)

        with col1:

            project_id = st.text_input(
                "Project ID *",
                value=_safe_text(
                    project.get(
                        "project_id"
                    )
                ),
            )

            project_name = st.text_input(
                "Project Name *",
                value=_safe_text(
                    project.get(
                        "project_name",
                        project.get(
                            "name",
                            "",
                        ),
                    )
                ),
            )

            client = st.text_input(
                "Client *",
                value=_safe_text(
                    project.get(
                        "client"
                    )
                ),
            )

            location = st.text_input(
                "Location *",
                value=_safe_text(
                    project.get(
                        "location"
                    )
                ),
            )

            manager = st.text_input(
                "Project Manager *",
                value=_safe_text(
                    project.get(
                        "project_manager",
                        project.get(
                            "manager",
                            "",
                        ),
                    )
                ),
            )

        with col2:

            current_type = _safe_text(
                project.get(
                    "project_type",
                    "Commercial",
                )
            )

            if current_type not in PROJECT_TYPES:
                current_type = "Other"

            project_type = st.selectbox(
                "Project Type *",
                PROJECT_TYPES,
                index=PROJECT_TYPES.index(
                    current_type
                ),
            )

            current_status = _project_status(
                project
            )

            status = st.selectbox(
                "Status *",
                PROJECT_STATUSES,
                index=PROJECT_STATUSES.index(
                    current_status
                ),
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                value=_safe_float(
                    project.get(
                        "estimated_budget",
                        project.get(
                            "budget",
                            0,
                        ),
                    )
                ),
                step=1000.0,
            )

            existing_start = _safe_date(
                project.get(
                    "start_date"
                )
            )

            existing_end = _safe_date(
                project.get(
                    "end_date"
                )
            )

            start_date = st.date_input(
                "Start Date",
                value=existing_start,
            )

            end_date = st.date_input(
                "End Date",
                value=existing_end,
            )

        description = st.text_area(
            "Description",
            value=_safe_text(
                project.get(
                    "description"
                )
            ),
            height=110,
        )

        save_changes = st.form_submit_button(
            "Save Changes",
            use_container_width=True,
        )

    if not save_changes:
        return

    errors = _validate_project(
        db,
        project_id,
        project_name,
        client,
        location,
        manager,
        project_type,
        status,
        budget,
        start_date,
        end_date,
        exclude_id=project_db_id,
    )

    if errors:

        for error in errors:
            st.error(error)

        return

    updates = {
        "project_id": project_id.strip(),
        "name": project_name.strip(),
        "project_name": project_name.strip(),
        "client": client.strip(),
        "location": location.strip(),
        "manager": manager.strip(),
        "project_manager": manager.strip(),
        "project_type": project_type,
        "status": status,
        "estimated_budget": float(
            budget
        ),
        "budget": float(
            budget
        ),
        "start_date": (
            start_date.isoformat()
            if start_date
            else ""
        ),
        "end_date": (
            end_date.isoformat()
            if end_date
            else ""
        ),
        "description": description.strip(),
        "updated_at": datetime.now().isoformat(),
    }

    try:

        updated = update_record(
            PROJECT_COLLECTION,
            project_db_id,
            updates,
            db,
        )

        if updated is None:

            st.error(
                "The project could not be found."
            )

            return

        st.success(
            "Project updated successfully."
        )

        st.rerun()

    except Exception as exc:

        st.error(
            "Unable to update the project."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# DELETE
# ============================================================

def _delete_project(
    db: dict[str, Any],
    project: dict[str, Any],
) -> None:

    project_db_id = project.get(
        "id"
    )

    project_name = _safe_text(
        project.get(
            "project_name",
            project.get(
                "name",
                "this project",
            ),
        )
    )

    st.warning(
        f'Delete "{project_name}"? '
        "This action cannot be undone."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Delete Project",
            key=f"confirm_delete_{project_db_id}",
            use_container_width=True,
        ):

            try:

                deleted = delete_record(
                    PROJECT_COLLECTION,
                    project_db_id,
                    db,
                )

                if deleted:

                    st.success(
                        "Project deleted successfully."
                    )

                    st.rerun()

                else:

                    st.error(
                        "The project could not be found."
                    )

            except Exception as exc:

                st.error(
                    "Unable to delete the project."
                )

                st.code(
                    f"{type(exc).__name__}: {exc}"
                )

    with col2:

        if st.button(
            "Cancel",
            key=f"cancel_delete_{project_db_id}",
            use_container_width=True,
        ):

            st.session_state.pop(
                f"delete_{project_db_id}",
                None,
            )

            st.rerun()


# ============================================================
# PROJECT CARD
# ============================================================

def _render_project_card(
    db: dict[str, Any],
    project: dict[str, Any],
) -> None:

    project_db_id = project.get(
        "id"
    )

    project_id = _safe_text(
        project.get(
            "project_id",
            "N/A",
        )
    )

    project_name = _safe_text(
        project.get(
            "project_name",
            project.get(
                "name",
                "Unnamed Project",
            ),
        ),
        "Unnamed Project",
    )

    project_type = _safe_text(
        project.get(
            "project_type",
            "Other",
        ),
        "Other",
    )

    status = _project_status(
        project
    )

    client = _safe_text(
        project.get(
            "client",
            "Not specified",
        ),
        "Not specified",
    )

    location = _safe_text(
        project.get(
            "location",
            "Not specified",
        ),
        "Not specified",
    )

    manager = _safe_text(
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
        "estimated_budget",
        project.get(
            "budget",
            0,
        ),
    )

    css_class = _status_css_class(
        status
    )

    st.markdown(
        f"""
        <div class="cs-project-card">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:flex-start;
                gap:15px;
            ">

                <div>

                    <div class="cs-project-name">
                        {project_name}
                    </div>

                    <div class="cs-project-meta">
                        {project_id}
                        &nbsp; • &nbsp;
                        {project_type}
                    </div>

                </div>

                <div>
                    <span class="cs-status {css_class}">
                        {status}
                    </span>
                </div>

            </div>

            <div style="
                height:1px;
                background:#172033;
                margin:16px 0;
            "></div>

            <div style="
                display:grid;
                grid-template-columns:
                    repeat(4, minmax(0, 1fr));
                gap:15px;
            ">

                <div>
                    <div class="cs-project-meta">
                        CLIENT
                    </div>
                    <div class="cs-project-info">
                        {client}
                    </div>
                </div>

                <div>
                    <div class="cs-project-meta">
                        LOCATION
                    </div>
                    <div class="cs-project-info">
                        {location}
                    </div>
                </div>

                <div>
                    <div class="cs-project-meta">
                        PROJECT MANAGER
                    </div>
                    <div class="cs-project-info">
                        {manager}
                    </div>
                </div>

                <div>
                    <div class="cs-project-meta">
                        ESTIMATED BUDGET
                    </div>
                    <div class="cs-project-budget">
                        {_format_money(budget)}
                    </div>
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(
        [1, 1, 4]
    )

    edit_key = (
        f"edit_project_{project_db_id}"
    )

    delete_key = (
        f"delete_project_{project_db_id}"
    )

    with col1:

        if st.button(
            "Edit",
            key=edit_key,
            use_container_width=True,
        ):

            st.session_state[
                f"editing_{project_db_id}"
            ] = True

            st.session_state.pop(
                f"delete_{project_db_id}",
                None,
            )

            st.rerun()

    with col2:

        if st.button(
            "Delete",
            key=delete_key,
            use_container_width=True,
        ):

            st.session_state[
                f"delete_{project_db_id}"
            ] = True

            st.session_state.pop(
                f"editing_{project_db_id}",
                None,
            )

            st.rerun()

    if st.session_state.get(
        f"editing_{project_db_id}",
        False,
    ):

        _render_edit_form(
            db,
            project,
        )

    if st.session_state.get(
        f"delete_{project_db_id}",
        False,
    ):

        _delete_project(
            db,
            project,
        )


# ============================================================
# PROJECT DIRECTORY
# ============================================================

def render_projects_module(
    db: dict[str, Any] | None = None,
) -> None:

    _inject_project_css()

    # --------------------------------------------------------
    # Database safety
    # --------------------------------------------------------

    if not isinstance(
        db,
        dict,
    ):

        db = load_memory()

    if "projects" not in db:

        db["projects"] = []

        save_memory(db)

    projects = _get_projects(
        db
    )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-project-header">

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
    # KPI calculations
    # --------------------------------------------------------

    total_projects = len(
        projects
    )

    active_projects = sum(
        1
        for project in projects
        if _project_status(project)
        == "Active"
    )

    planning_projects = sum(
        1
        for project in projects
        if _project_status(project)
        == "Planning"
    )

    completed_projects = sum(
        1
        for project in projects
        if _project_status(project)
        == "Completed"
    )

    portfolio_budget = sum(
        _safe_float(
            project.get(
                "estimated_budget",
                project.get(
                    "budget",
                    0,
                ),
            )
        )
        for project in projects
    )

    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    cols = st.columns(5)

    metrics = [
        (
            "Total Projects",
            str(total_projects),
        ),
        (
            "Active",
            str(active_projects),
        ),
        (
            "Planning",
            str(planning_projects),
        ),
        (
            "Completed",
            str(completed_projects),
        ),
        (
            "Portfolio Budget",
            _format_money(
                portfolio_budget
            ),
        ),
    ]

    for column, (
        label,
        value,
    ) in zip(
        cols,
        metrics,
    ):

        with column:

            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {label}
                    </div>

                    <div class="cs-kpi-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # --------------------------------------------------------
    # Create project
    # --------------------------------------------------------

    with st.expander(
        "Create New Project",
        expanded=False,
    ):

        _render_create_form(
            db
        )

    # --------------------------------------------------------
    # Search / filters
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-project-section">'
        "Project Portfolio"
        "</div>",
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search Projects",
        placeholder=(
            "Search by project ID, name, client, "
            "location or manager..."
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

    # --------------------------------------------------------
    # Filtering
    # --------------------------------------------------------

    search_text = search.strip().lower()

    filtered_projects = []

    for project in projects:

        status = _project_status(
            project
        )

        project_type = _safe_text(
            project.get(
                "project_type",
                "Other",
            )
        )

        if (
            status_filter != "All"
            and status != status_filter
        ):
            continue

        if (
            type_filter != "All"
            and project_type != type_filter
        ):
            continue

        searchable = " ".join(
            [
                _safe_text(
                    project.get(
                        "project_id"
                    )
                ),
                _safe_text(
                    project.get(
                        "project_name",
                        project.get(
                            "name"
                        ),
                    )
                ),
                _safe_text(
                    project.get(
                        "client"
                    )
                ),
                _safe_text(
                    project.get(
                        "location"
                    )
                ),
                _safe_text(
                    project.get(
                        "project_manager",
                        project.get(
                            "manager"
                        ),
                    )
                ),
            ]
        ).lower()

        if (
            search_text
            and search_text not in searchable
        ):
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
    # Empty state
    # --------------------------------------------------------

    if not filtered_projects:

        st.markdown(
            """
            <div class="cs-project-empty">

                <div style="
                    color:#FFFFFF;
                    font-size:17px;
                    font-weight:800;
                    margin-bottom:7px;
                ">
                    No projects found
                </div>

                <div>
                    Try changing your search or filters,
                    or create a new project.
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