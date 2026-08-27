"""
Creative Studios
Projects Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_projects(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Normalize project records.

    Supports both the current dictionary format and
    legacy string records.
    """
    value = database.get("projects", [])

    if not isinstance(value, list):
        value = []

    normalized = []

    for index, item in enumerate(value, start=1):

        if isinstance(item, dict):
            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            if not record.get("name"):
                record["name"] = record.get(
                    "project_name",
                    f"Project {index}",
                )

            normalized.append(record)

        elif isinstance(item, str):
            normalized.append(
                {
                    "id": index,
                    "name": item,
                    "project_name": item,
                    "client": "",
                    "client_name": "",
                    "location": "",
                    "status": "Planning",
                    "budget": 0.0,
                    "estimated_budget": 0.0,
                    "description": "",
                    "created_at": "",
                }
            )

    database["projects"] = normalized
    return normalized


def _next_id(
    records: list[dict[str, Any]],
) -> int:
    ids = []

    for record in records:
        try:
            ids.append(int(record.get("id", 0)))
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


def _save(
    database: dict[str, Any],
) -> None:
    save_memory(database)


def render_projects_module(
    database: dict[str, Any],
) -> None:
    """Render the editable project directory."""

    st.title("Projects")
    st.caption(
        "Create, edit and manage Creative Studios projects."
    )

    projects = _normalize_projects(database)

    tab_directory, tab_create = st.tabs(
        [
            "Project Directory",
            "Create Project",
        ]
    )

    with tab_directory:

        if not projects:
            st.info(
                "No projects have been created yet."
            )
        else:

            for index, project in enumerate(
                projects
            ):

                project_id = project.get(
                    "id",
                    index + 1,
                )

                name = project.get(
                    "name",
                    project.get(
                        "project_name",
                        "Unnamed Project",
                    ),
                )

                with st.expander(
                    str(name),
                    expanded=False,
                ):

                    st.write(
                        f"Project ID: **{project_id}**"
                    )

                    edit_key = (
                        f"edit_project_{project_id}"
                    )

                    with st.form(edit_key):

                        edited_name = st.text_input(
                            "Project Name",
                            value=str(
                                name or ""
                            ),
                        )

                        edited_client = st.text_input(
                            "Client",
                            value=str(
                                project.get(
                                    "client",
                                    project.get(
                                        "client_name",
                                        "",
                                    ),
                                )
                                or ""
                            ),
                        )

                        edited_location = st.text_input(
                            "Project Location",
                            value=str(
                                project.get(
                                    "location",
                                    "",
                                )
                                or ""
                            ),
                        )

                        statuses = [
                            "Planning",
                            "Active",
                            "On Hold",
                            "Completed",
                            "Cancelled",
                        ]

                        current_status = str(
                            project.get(
                                "status",
                                "Planning",
                            )
                        )

                        status_index = (
                            statuses.index(
                                current_status
                            )
                            if current_status
                            in statuses
                            else 0
                        )

                        edited_status = st.selectbox(
                            "Status",
                            statuses,
                            index=status_index,
                        )

                        try:
                            current_budget = float(
                                project.get(
                                    "estimated_budget",
                                    project.get(
                                        "budget",
                                        0,
                                    ),
                                )
                                or 0
                            )
                        except (
                            TypeError,
                            ValueError,
                        ):
                            current_budget = 0.0

                        edited_budget = st.number_input(
                            "Estimated Budget",
                            min_value=0.0,
                            value=current_budget,
                            step=1000.0,
                        )

                        edited_description = st.text_area(
                            "Description",
                            value=str(
                                project.get(
                                    "description",
                                    "",
                                )
                                or ""
                            ),
                        )

                        submitted = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )

                    delete_key = (
                        f"delete_project_{project_id}"
                    )

                    if submitted:

                        if not edited_name.strip():
                            st.error(
                                "Project name is required."
                            )
                        else:
                            project["name"] = (
                                edited_name.strip()
                            )
                            project[
                                "project_name"
                            ] = edited_name.strip()

                            project["client"] = (
                                edited_client.strip()
                            )
                            project[
                                "client_name"
                            ] = edited_client.strip()

                            project["location"] = (
                                edited_location.strip()
                            )

                            project["status"] = (
                                edited_status
                            )

                            project[
                                "budget"
                            ] = edited_budget

                            project[
                                "estimated_budget"
                            ] = edited_budget

                            project[
                                "description"
                            ] = (
                                edited_description.strip()
                            )

                            _save(database)

                            st.success(
                                "Project updated successfully."
                            )

                            st.rerun()

                    if st.button(
                        "Delete Project",
                        key=delete_key,
                        use_container_width=True,
                    ):
                        projects.remove(project)
                        _save(database)

                        st.success(
                            "Project deleted successfully."
                        )

                        st.rerun()

    with tab_create:

        with st.form(
            "create_project_form",
            clear_on_submit=True,
        ):

            name = st.text_input(
                "Project Name"
            )

            client = st.text_input(
                "Client"
            )

            location = st.text_input(
                "Project Location"
            )

            status = st.selectbox(
                "Status",
                [
                    "Planning",
                    "Active",
                    "On Hold",
                    "Completed",
                    "Cancelled",
                ],
            )

            budget = st.number_input(
                "Estimated Budget",
                min_value=0.0,
                step=1000.0,
            )

            description = st.text_area(
                "Description"
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
                return

            projects.append(
                {
                    "id": _next_id(projects),
                    "name": name.strip(),
                    "project_name": name.strip(),
                    "client": client.strip(),
                    "client_name": client.strip(),
                    "location": location.strip(),
                    "status": status,
                    "budget": budget,
                    "estimated_budget": budget,
                    "description": description.strip(),
                    "created_at": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                }
            )

            _save(database)

            st.success(
                "Project created successfully."
            )

            st.rerun()