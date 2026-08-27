"""
Creative Studios
Architecture Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import render_module_files


STAGES = [
    "Concept",
    "Schematic Design",
    "Design Development",
    "Construction Documentation",
    "Issued",
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
        "architecture",
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
                    "stage": "Concept",
                    "status": "Draft",
                    "building_type": "General",
                    "notes": "",
                }
            )

    database["architecture"] = records

    return records


def _next_id(records: list[dict[str, Any]]) -> int:

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


def render_architecture_module(
    database: dict[str, Any],
) -> None:

    st.title("Architecture")

    st.caption(
        "Architectural design, construction documentation "
        "and project coordination."
    )

    records = _normalize(database)

    overview, register, files = st.tabs(
        [
            "Overview",
            "Design Register",
            "Files & Documents",
        ]
    )

    with overview:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Design Records",
            len(records),
        )

        c2.metric(
            "Concept",
            sum(
                r.get("stage") == "Concept"
                for r in records
            ),
        )

        c3.metric(
            "Construction Documentation",
            sum(
                r.get("stage")
                == "Construction Documentation"
                for r in records
            ),
        )

        c4.metric(
            "Issued",
            sum(
                r.get("status") == "Issued"
                for r in records
            ),
        )

        st.divider()

        st.subheader(
            "Architectural Work Areas"
        )

        st.write(
            "Building planning, room programming, "
            "layouts, elevations, sections, finishes, "
            "schedules and construction documentation."
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
                        "Untitled Design",
                    )
                ),
                expanded=False,
            ):

                with st.form(
                    f"architecture_edit_{record_id}"
                ):

                    title = st.text_input(
                        "Design Item",
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

                    building_type = st.selectbox(
                        "Building Type",
                        [
                            "General",
                            "Residential",
                            "Commercial",
                            "Office",
                            "Industrial",
                            "Institutional",
                            "Hospitality",
                            "Education",
                            "Mixed Use",
                        ],
                        index=(
                            [
                                "General",
                                "Residential",
                                "Commercial",
                                "Office",
                                "Industrial",
                                "Institutional",
                                "Hospitality",
                                "Education",
                                "Mixed Use",
                            ].index(
                                record.get(
                                    "building_type",
                                    "General",
                                )
                            )
                            if record.get(
                                "building_type",
                                "General",
                            )
                            in [
                                "General",
                                "Residential",
                                "Commercial",
                                "Office",
                                "Industrial",
                                "Institutional",
                                "Hospitality",
                                "Education",
                                "Mixed Use",
                            ]
                            else 0
                        ),
                    )

                    stage = st.selectbox(
                        "Design Stage",
                        STAGES,
                        index=(
                            STAGES.index(
                                record.get(
                                    "stage",
                                    "Concept",
                                )
                            )
                            if record.get(
                                "stage",
                                "Concept",
                            )
                            in STAGES
                            else 0
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
                        "Notes",
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
                            "Design item is required."
                        )

                    else:

                        record.update(
                            {
                                "title": title.strip(),
                                "project": project.strip(),
                                "building_type": building_type,
                                "stage": stage,
                                "status": status,
                                "notes": notes.strip(),
                            }
                        )

                        save_memory(database)

                        st.success(
                            "Architecture record updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Record",
                    key=f"architecture_delete_{record_id}",
                    use_container_width=True,
                ):

                    records.remove(record)

                    save_memory(database)

                    st.rerun()

        st.divider()

        with st.form(
            "architecture_add",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Design Item"
            )

            project = st.text_input(
                "Project"
            )

            building_type = st.selectbox(
                "Building Type",
                [
                    "General",
                    "Residential",
                    "Commercial",
                    "Office",
                    "Industrial",
                    "Institutional",
                    "Hospitality",
                    "Education",
                    "Mixed Use",
                ],
            )

            stage = st.selectbox(
                "Design Stage",
                STAGES,
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Add Design Record",
                use_container_width=True,
            )

        if submitted:

            if not title.strip():

                st.error(
                    "Design item is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(records),
                        "title": title.strip(),
                        "project": project.strip(),
                        "building_type": building_type,
                        "stage": stage,
                        "status": status,
                        "notes": notes.strip(),
                    }
                )

                save_memory(database)

                st.success(
                    "Architecture record added."
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
            "Architecture",
            project_options=projects,
        )