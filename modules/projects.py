"""
Creative Studios
Projects Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import render_module_files


STATUSES = [
    "Planning",
    "Active",
    "On Hold",
    "Completed",
    "Cancelled",
]


def _normalize(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "projects",
        [],
    )

    if not isinstance(value, list):
        value = []

    records = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            records.append(record)

        elif isinstance(item, str):

            records.append(
                {
                    "id": index,
                    "name": item,
                    "client": "",
                    "location": "",
                    "status": "Planning",
                    "description": "",
                    "created_at": "",
                }
            )

    database["projects"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:

    values = []

    for record in records:

        try:
            values.append(
                int(record.get("id", 0))
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    return max(values, default=0) + 1


def render_projects_module(
    database: dict[str, Any],
) -> None:

    st.title("Projects")

    st.caption(
        "Manage construction projects and their "
        "associated information."
    )

    projects = _normalize(database)

    overview, register, files = st.tabs(
        [
            "Overview",
            "Project Register",
            "Files & Documents",
        ]
    )

    with overview:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Projects",
            len(projects),
        )

        c2.metric(
            "Active",
            sum(
                p.get("status") == "Active"
                for p in projects
            ),
        )

        c3.metric(
            "Planning",
            sum(
                p.get("status") == "Planning"
                for p in projects
            ),
        )

        c4.metric(
            "Completed",
            sum(
                p.get("status") == "Completed"
                for p in projects
            ),
        )

    with register:

        for index, project in enumerate(projects):

            project_id = project.get(
                "id",
                index + 1,
            )

            name = str(
                project.get(
                    "name",
                    "Unnamed Project",
                )
            )

            with st.expander(
                name,
                expanded=False,
            ):

                with st.form(
                    f"project_edit_{project_id}"
                ):

                    edited_name = st.text_input(
                        "Project Name",
                        value=name,
                    )

                    client = st.text_input(
                        "Client",
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

                    status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=(
                            STATUSES.index(
                                project.get(
                                    "status",
                                    "Planning",
                                )
                            )
                            if project.get(
                                "status",
                                "Planning",
                            )
                            in STATUSES
                            else 0
                        ),
                    )

                    description = st.text_area(
                        "Description",
                        value=str(
                            project.get(
                                "description",
                                "",
                            )
                        ),
                    )

                    save = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save:

                    if not edited_name.strip():

                        st.error(
                            "Project name is required."
                        )

                    else:

                        project.update(
                            {
                                "name": edited_name.strip(),
                                "client": client.strip(),
                                "location": location.strip(),
                                "status": status,
                                "description": description.strip(),
                            }
                        )

                        save_memory(database)

                        st.success(
                            "Project updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Project",
                    key=f"project_delete_{project_id}",
                    use_container_width=True,
                ):

                    projects.remove(project)

                    save_memory(database)

                    st.rerun()

        st.divider()

        with st.form(
            "project_add",
            clear_on_submit=True,
        ):

            name = st.text_input(
                "Project Name"
            )

            client = st.text_input(
                "Client"
            )

            location = st.text_input(
                "Location"
            )

            status = st.selectbox(
                "Status",
                STATUSES,
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

            else:

                projects.append(
                    {
                        "id": _next_id(projects),
                        "name": name.strip(),
                        "client": client.strip(),
                        "location": location.strip(),
                        "status": status,
                        "description": description.strip(),
                        "created_at": datetime.now().isoformat(
                            timespec="seconds"
                        ),
                    }
                )

                save_memory(database)

                st.success(
                    "Project created."
                )

                st.rerun()

    with files:

        project_names = sorted(
            {
                str(
                    p.get(
                        "name",
                        "",
                    )
                )
                for p in projects
                if p.get("name")
            }
        )

        render_module_files(
            database,
            "Projects",
            project_options=project_names,
        )