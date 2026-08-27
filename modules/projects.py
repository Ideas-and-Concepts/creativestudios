"""
Creative Studios
Projects Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


def _projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    value = database.setdefault("projects", [])

    if not isinstance(value, list):
        database["projects"] = []
        return database["projects"]

    return value


def _next_id(records: list[dict[str, Any]]) -> int:
    ids = []

    for record in records:
        try:
            ids.append(int(record.get("id", 0)))
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


def render_projects_module(
    database: dict[str, Any],
) -> None:
    """Render project directory."""

    st.title("Projects")
    st.caption(
        "Create and manage Creative Studios projects."
    )

    projects = _projects(database)

    tab_directory, tab_create = st.tabs(
        ["Project Directory", "Create Project"]
    )

    with tab_directory:

        if not projects:
            st.info("No projects have been created yet.")
        else:
            for project in projects:

                project_id = project.get("id", "")
                name = project.get(
                    "name",
                    project.get(
                        "project_name",
                        "Unnamed Project",
                    ),
                )

                status = project.get(
                    "status",
                    "Planning",
                )

                client = project.get(
                    "client",
                    project.get(
                        "client_name",
                        "Not specified",
                    ),
                )

                with st.container(border=True):

                    top_left, top_right = st.columns(
                        [3, 1]
                    )

                    with top_left:
                        st.subheader(str(name))
                        st.write(
                            f"Client: {client}"
                        )

                    with top_right:
                        st.write(
                            f"Status: **{status}**"
                        )

                    details = st.columns(4)

                    details[0].write(
                        f"**Project ID**  \n{project_id}"
                    )

                    details[1].write(
                        f"**Location**  \n"
                        f"{project.get('location', 'Not specified')}"
                    )

                    details[2].write(
                        f"**Budget**  \n"
                        f"{project.get('budget', project.get('estimated_budget', 0))}"
                    )

                    details[3].write(
                        f"**Created**  \n"
                        f"{project.get('created_at', 'Not specified')}"
                    )

    with tab_create:

        with st.form(
            "create_project_form",
            clear_on_submit=True,
        ):

            name = st.text_input(
                "Project Name",
            )

            client = st.text_input(
                "Client",
            )

            location = st.text_input(
                "Project Location",
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
                "Description",
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

            project = {
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

            projects.append(project)

            st.success(
                "Project created successfully."
            )

            st.rerun()