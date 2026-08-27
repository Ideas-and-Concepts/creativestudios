"""
Creative Studios
Engineering Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import render_module_files


DISCIPLINES = [
    "Structural",
    "Civil",
    "Geotechnical",
    "Transportation",
    "Infrastructure",
    "Environmental",
    "Other",
]

STATUSES = [
    "Draft",
    "In Review",
    "Approved",
    "Issued",
]


def _normalize(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "engineering",
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
                    "title": item,
                    "project": "",
                    "discipline": "Other",
                    "status": "Draft",
                    "notes": "",
                }
            )

    database["engineering"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:

    ids = []

    for record in records:

        try:
            ids.append(
                int(record.get("id", 0))
            )

        except (
            TypeError,
            ValueError,
        ):
            pass

    return max(ids, default=0) + 1


def render_engineering_module(
    database: dict[str, Any],
) -> None:

    st.title("Engineering")

    st.caption(
        "Engineering design, technical coordination "
        "and construction engineering records."
    )

    records = _normalize(database)

    overview, register, files = st.tabs(
        [
            "Overview",
            "Engineering Register",
            "Files & Documents",
        ]
    )

    with overview:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Engineering Records",
            len(records),
        )

        c2.metric(
            "Structural",
            sum(
                r.get("discipline")
                == "Structural"
                for r in records
            ),
        )

        c3.metric(
            "Civil",
            sum(
                r.get("discipline")
                == "Civil"
                for r in records
            ),
        )

        c4.metric(
            "Infrastructure",
            sum(
                r.get("discipline")
                == "Infrastructure"
                for r in records
            ),
        )

        st.divider()

        st.write(
            "Engineering coordination includes structural "
            "systems, foundations, civil works, infrastructure, "
            "geotechnical design and technical construction records."
        )

    with register:

        for index, record in enumerate(records):

            record_id = record.get(
                "id",
                index + 1,
            )

            with st.expander(
                str(
                    record.get(
                        "title",
                        "Engineering Work Item",
                    )
                ),
                expanded=False,
            ):

                with st.form(
                    f"engineering_edit_{record_id}"
                ):

                    title = st.text_input(
                        "Engineering Work Item",
                        value=str(
                            record.get(
                                "title",
                                "",
                            )
                        ),
                    )

                    project = st.text_input(
                        "Project",
                        value=str(
                            record.get(
                                "project",
                                "",
                            )
                        ),
                    )

                    discipline = st.selectbox(
                        "Discipline",
                        DISCIPLINES,
                        index=(
                            DISCIPLINES.index(
                                record.get(
                                    "discipline",
                                    "Other",
                                )
                            )
                            if record.get(
                                "discipline",
                                "Other",
                            )
                            in DISCIPLINES
                            else len(DISCIPLINES) - 1
                        ),
                    )

                    status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=(
                            STATUSES.index(
                                record.get(
                                    "status",
                                    "Draft",
                                )
                            )
                            if record.get(
                                "status",
                                "Draft",
                            )
                            in STATUSES
                            else 0
                        ),
                    )

                    notes = st.text_area(
                        "Technical Notes",
                        value=str(
                            record.get(
                                "notes",
                                "",
                            )
                        ),
                    )

                    save = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save:

                    if not title.strip():

                        st.error(
                            "Engineering work item is required."
                        )

                    else:

                        record.update(
                            {
                                "title": title.strip(),
                                "project": project.strip(),
                                "discipline": discipline,
                                "status": status,
                                "notes": notes.strip(),
                            }
                        )

                        save_memory(database)

                        st.success(
                            "Engineering record updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Record",
                    key=f"engineering_delete_{record_id}",
                    use_container_width=True,
                ):

                    records.remove(record)

                    save_memory(database)

                    st.rerun()

        st.divider()

        with st.form(
            "engineering_add",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Engineering Work Item"
            )

            project = st.text_input(
                "Project"
            )

            discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            notes = st.text_area(
                "Technical Notes"
            )

            submitted = st.form_submit_button(
                "Add Engineering Record",
                use_container_width=True,
            )

        if submitted:

            if not title.strip():

                st.error(
                    "Engineering work item is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(records),
                        "title": title.strip(),
                        "project": project.strip(),
                        "discipline": discipline,
                        "status": status,
                        "notes": notes.strip(),
                    }
                )

                save_memory(database)

                st.success(
                    "Engineering record added."
                )

                st.rerun()

    with files:

        projects = sorted(
            {
                str(
                    r.get(
                        "project",
                        "",
                    )
                )
                for r in records
                if r.get("project")
            }
        )

        render_module_files(
            database,
            "Engineering",
            project_options=projects,
        )