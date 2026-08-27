"""
Creative Studios
Engineering Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_records(
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
            continue

    return max(ids, default=0) + 1


def render_engineering_module(
    database: dict[str, Any],
) -> None:
    """Render editable engineering workspace."""

    st.title("Engineering")
    st.caption(
        "Manage engineering disciplines, design records and technical activities."
    )

    records = _normalize_records(
        database
    )

    columns = st.columns(4)

    columns[0].metric(
        "Engineering Records",
        len(records),
    )

    columns[1].metric(
        "Structural",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Structural"
        ),
    )

    columns[2].metric(
        "Civil",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Civil"
        ),
    )

    columns[3].metric(
        "Infrastructure",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Infrastructure"
        ),
    )

    st.divider()

    if records:

        st.subheader(
            "Engineering Register"
        )

        for index, record in enumerate(
            records
        ):

            record_id = record.get(
                "id",
                index + 1,
            )

            title = record.get(
                "title",
                "Engineering Work Item",
            )

            with st.expander(
                str(title),
                expanded=False,
            ):

                with st.form(
                    f"edit_engineering_{record_id}"
                ):

                    edited_title = st.text_input(
                        "Engineering Work Item",
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

                    disciplines = [
                        "Structural",
                        "Civil",
                        "Infrastructure",
                        "Geotechnical",
                        "Transportation",
                        "Environmental",
                        "Other",
                    ]

                    current_discipline = str(
                        record.get(
                            "discipline",
                            "Other",
                        )
                    )

                    discipline_index = (
                        disciplines.index(
                            current_discipline
                        )
                        if current_discipline
                        in disciplines
                        else len(disciplines) - 1
                    )

                    edited_discipline = st.selectbox(
                        "Discipline",
                        disciplines,
                        index=discipline_index,
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
                        "Technical Notes",
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
                            "Engineering work item is required."
                        )
                    else:

                        record["title"] = (
                            edited_title.strip()
                        )

                        record["project"] = (
                            edited_project.strip()
                        )

                        record[
                            "discipline"
                        ] = edited_discipline

                        record["status"] = (
                            edited_status
                        )

                        record["notes"] = (
                            edited_notes.strip()
                        )

                        save_memory(database)

                        st.success(
                            "Engineering record updated successfully."
                        )

                        st.rerun()

                if st.button(
                    "Delete Record",
                    key=f"delete_engineering_{record_id}",
                    use_container_width=True,
                ):

                    records.remove(record)

                    save_memory(database)

                    st.success(
                        "Engineering record deleted successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "No engineering records have been created yet."
        )

    st.divider()

    with st.form(
        "engineering_record_form",
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
            [
                "Structural",
                "Civil",
                "Infrastructure",
                "Geotechnical",
                "Transportation",
                "Environmental",
                "Other",
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
            return

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
            "Engineering record added successfully."
        )

        st.rerun()