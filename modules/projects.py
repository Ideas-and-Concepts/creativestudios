"""
Creative Studios
Project Directory Module
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from modules.branding import render_module_header
from modules.database import (
    add_record,
    delete_record,
    get_records,
    next_id,
    update_record,
)


PROJECT_STATUSES = [
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Cancelled",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_projects_module(
    database: dict[str, Any],
) -> None:

    render_module_header(
        "Project Directory",
        "Manage architectural, engineering and construction projects.",
    )

    projects = database.get("projects", [])

    if not isinstance(projects, list):
        projects = []

    # ========================================================
    # ACTION BAR
    # ========================================================

    col1, col2 = st.columns([4, 1])

    with col1:
        search = st.text_input(
            "Search projects",
            placeholder="Search by project name, client or location...",
            key="projects_search",
        )

    with col2:
        show_form = st.button(
            "New Project",
            use_container_width=True,
            key="new_project_button",
        )

    if show_form:
        st.session_state["show_project_form"] = True

    # ========================================================
    # CREATE PROJECT
    # ========================================================

    if st.session_state.get(
        "show_project_form",
        False,
    ):

        st.markdown("### New Project")

        with st.form(
            "create_project_form",
            clear_on_submit=True,
        ):

            name = st.text_input(
                "Project Name",
                key="project_name",
            )

            client = st.text_input(
                "Client",
                key="project_client",
            )

            location = st.text_input(
                "Location",
                key="project_location",
            )

            col_a, col_b = st.columns(2)

            with col_a:
                status = st.selectbox(
                    "Status",
                    PROJECT_STATUSES,
                    key="project_status",
                )

            with col_b:
                budget = st.number_input(
                    "Estimated Budget",
                    min_value=0.0,
                    step=1000.0,
                    key="project_budget",
                )

            description = st.text_area(
                "Description",
                key="project_description",
            )

            submitted = st.form_submit_button(
                "Create Project",
                use_container_width=True,
            )

            if submitted:

                if not name.strip():

                    st.error(
                        "Project name is required."
                    )

                else:

                    project = {
                        "id": next_id(
                            projects
                        ),
                        "name": name.strip(),
                        "client": client.strip(),
                        "location": location.strip(),
                        "status": status,
                        "estimated_budget": budget,
                        "description": description.strip(),
                    }

                    add_record(
                        database,
                        "projects",
                        project,
                    )

                    st.session_state[
                        "show_project_form"
                    ] = False

                    st.success(
                        "Project created successfully."
                    )

                    st.rerun()

    # ========================================================
    # FILTER
    # ========================================================

    filtered_projects = []

    search_value = search.strip().lower()

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        if search_value:

            searchable = " ".join(
                [
                    _text(project.get("name")),
                    _text(project.get("client")),
                    _text(project.get("location")),
                    _text(project.get("status")),
                ]
            ).lower()

            if search_value not in searchable:
                continue

        filtered_projects.append(project)

    # ========================================================
    # SUMMARY
    # ========================================================

    cols = st.columns(4)

    metrics = [
        (
            "Total",
            len(projects),
        ),
        (
            "Active",
            sum(
                1
                for p in projects
                if _text(
                    p.get("status")
                ).lower()
                == "active"
            ),
        ),
        (
            "Planning",
            sum(
                1
                for p in projects
                if _text(
                    p.get("status")
                ).lower()
                == "planning"
            ),
        ),
        (
            "Completed",
            sum(
                1
                for p in projects
                if _text(
                    p.get("status")
                ).lower()
                == "completed"
            ),
        ),
    ]

    for col, (label, value) in zip(
        cols,
        metrics,
    ):

        with col:

            st.metric(
                label,
                value,
            )

    st.write("")

    # ========================================================
    # PROJECT TABLE
    # ========================================================

    if not filtered_projects:

        st.info(
            "No projects found."
        )

        return

    for project in filtered_projects:

        project_id = project.get(
            "id"
        )

        name = html.escape(
            _text(
                project.get(
                    "name",
                    "Unnamed Project",
                )
            )
        )

        client = html.escape(
            _text(
                project.get(
                    "client",
                    "Not specified",
                )
            )
        )

        location = html.escape(
            _text(
                project.get(
                    "location",
                    "Not specified",
                )
            )
        )

        status = html.escape(
            _text(
                project.get(
                    "status",
                    "Planning",
                )
            )
        )

        st.markdown(
            f"""
            <div class="cs-card">

                <div style="
                    color:#FFFFFF;
                    font-size:17px;
                    font-weight:850;
                ">
                    {name}
                </div>

                <div style="
                    color:#64748B;
                    font-size:12px;
                    margin-top:6px;
                ">
                    Client: {client}
                    &nbsp; • &nbsp;
                    Location: {location}
                    &nbsp; • &nbsp;
                    Status: {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"Manage Project #{project_id}"
        ):

            with st.form(
                f"edit_project_{project_id}"
            ):

                edit_name = st.text_input(
                    "Project Name",
                    value=_text(
                        project.get("name")
                    ),
                )

                edit_client = st.text_input(
                    "Client",
                    value=_text(
                        project.get("client")
                    ),
                )

                edit_location = st.text_input(
                    "Location",
                    value=_text(
                        project.get("location")
                    ),
                )

                current_status = _text(
                    project.get(
                        "status",
                        "Planning",
                    )
                )

                status_index = (
                    PROJECT_STATUSES.index(
                        current_status
                    )
                    if current_status
                    in PROJECT_STATUSES
                    else 0
                )

                edit_status = st.selectbox(
                    "Status",
                    PROJECT_STATUSES,
                    index=status_index,
                )

                edit_budget = st.number_input(
                    "Estimated Budget",
                    min_value=0.0,
                    value=float(
                        project.get(
                            "estimated_budget",
                            0,
                        )
                        or 0
                    ),
                    step=1000.0,
                )

                edit_description = st.text_area(
                    "Description",
                    value=_text(
                        project.get(
                            "description"
                        )
                    ),
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save:

                    update_record(
                        database,
                        "projects",
                        project_id,
                        {
                            "name": edit_name.strip(),
                            "client": edit_client.strip(),
                            "location": edit_location.strip(),
                            "status": edit_status,
                            "estimated_budget": edit_budget,
                            "description": edit_description.strip(),
                        },
                    )

                    st.success(
                        "Project updated."
                    )

                    st.rerun()

            if st.button(
                "Delete Project",
                key=f"delete_project_{project_id}",
            ):

                delete_record(
                    database,
                    "projects",
                    project_id,
                )

                st.success(
                    "Project deleted."
                )

                st.rerun()