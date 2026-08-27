"""
Creative Studios
Architecture Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_records(
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
                    "notes": "",
                }
            )

    database["architecture"] = records

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
            continue

    return max(ids, default=0) + 1


def render_architecture_module(
    database: dict[str, Any],
) -> None:
    """Render editable architecture workspace."""

    st.title("Architecture")
    st.caption(
        "Manage architectural design information and project activities."
    )

    records = _normalize_records(
        database
    )

    tab_overview, tab_register = st.tabs(
        [
            "Overview",
            "Design Register",
        ]
    )

    with tab_overview:

        columns = st.columns(4)

        columns[0].metric(
            "Design Records",
            len(records),
        )

        columns[1].metric(
            "Concept",
            sum(
                1
                for record in records
                if str(
                    record.get(
                        "stage",
                        "",
                    )
                ).lower()
                == "concept"
            ),
        )

        columns[2].metric(
            "Design Development",
            sum(
                1
                for record in records
                if str(
                    record.get(
                        "stage",
                        "",
                    )
                ).lower()
                == "design development"
            ),
        )

        columns[3].metric(
            "Issued",
            sum(
                1
                for record in records
                if str(
                    record.get(
                        "status",
                        "",
                    )
                ).lower()
                == "issued"
            ),
        )

    with tab_register:

        if records:

            for index, record in enumerate(
                records
            ):

                record_id = record.get(
                    "id",
                    index + 1,
                )

                title = record.get(
                    "title",
                    "Untitled Design",
                )

                with st.expander(
                    str(title),
                    expanded=False,
                ):

                    with st.form(
                        f"edit_architecture_{record_id}"
                    ):

                        edited_title = st.text_input(
                            "Design Item",
                            value=str(
                                title or ""
                            ),
                        )

                        edited_project = st.text_input(
                            "Project",
                            value=str(
                                record.get(
                                    "project",
                                    "",
                                )
                                or ""
                            ),
                        )

                        stages = [
                            "Concept",
                            "Schematic Design",
                            "Design Development",
                            "Construction Documentation",
                            "Issued",
                        ]

                        current_stage = str(
                            record.get(
                                "stage",
                                "Concept",
                            )
                        )

                        stage_index = (
                            stages.index(
                                current_stage
                            )
                            if current_stage
                            in stages
                            else 0
                        )

                        edited_stage = st.selectbox(
                            "Design Stage",
                            stages,
                            index=stage_index,
                        )

                        statuses = [
                            "Draft",
                            "In Review",
                            "Approved",
                            "Issued",
                        ]

                        current_status = str(
                            record.get(
                                "status",
                                "Draft",
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

                        edited_notes = st.text_area(
                            "Notes",
                            value=str(
                                record.get(
                                    "notes",
                                    "",
                                )
                                or ""
                            ),
                        )

                        submitted = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )

                    if submitted:

                        if not edited_title.strip():
                            st.error(
                                "Design item is required."
                            )
                        else:

                            record["title"] = (
                                edited_title.strip()
                            )

                            record["project"] = (
                                edited_project.strip()
                            )

                            record["stage"] = (
                                edited_stage
                            )

                            record["status"] = (
                                edited_status
                            )

                            record["notes"] = (
                                edited_notes.strip()
                            )

                            save_memory(database)

                            st.success(
                                "Architecture record updated successfully."
                            )

                            st.rerun()

                    if st.button(
                        "Delete Record",
                        key=f"delete_architecture_{record_id}",
                        use_container_width=True,
                    ):

                        records.remove(record)

                        save_memory(database)

                        st.success(
                            "Architecture record deleted successfully."
                        )

                        st.rerun()

        else:

            st.info(
                "No architecture records have been created yet."
            )

        st.divider()

        with st.form(
            "architecture_register_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Design Item"
            )

            project = st.text_input(
                "Project"
            )

            stage = st.selectbox(
                "Design Stage",
                [
                    "Concept",
                    "Schematic Design",
                    "Design Development",
                    "Construction Documentation",
                    "Issued",
                ],
            )

            status = st.selectbox(
                "Status",
                [
                    "Draft",
                    "In Review",
                    "Approved",
                    "Issued",
                ],
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
                return

            records.append(
                {
                    "id": _next_id(records),
                    "title": title.strip(),
                    "project": project.strip(),
                    "stage": stage,
                    "status": status,
                    "notes": notes.strip(),
                }
            )

            save_memory(database)

            st.success(
                "Architecture record added successfully."
            )

            st.rerun()