"""
Creative Studios
MEP Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_records(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "mep",
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
                    "discipline": "Mechanical",
                    "system": "",
                    "status": "Draft",
                    "notes": "",
                }
            )

    database["mep"] = records

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


def render_mep_module(
    database: dict[str, Any],
) -> None:
    """Render editable MEP workspace."""

    st.title("MEP")
    st.caption(
        "Create, edit and manage mechanical, electrical and plumbing coordination."
    )

    records = _normalize_records(
        database
    )

    columns = st.columns(5)

    columns[0].metric(
        "MEP Records",
        len(records),
    )

    columns[1].metric(
        "Mechanical",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Mechanical"
        ),
    )

    columns[2].metric(
        "Electrical",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Electrical"
        ),
    )

    columns[3].metric(
        "Plumbing",
        sum(
            1
            for record in records
            if record.get(
                "discipline"
            )
            == "Plumbing"
        ),
    )

    columns[4].metric(
        "Approved",
        sum(
            1
            for record in records
            if str(
                record.get(
                    "status",
                    "",
                )
            ).lower()
            == "approved"
        ),
    )

    st.divider()

    if records:

        st.subheader(
            "MEP Coordination Register"
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
                "MEP Work Item",
            )

            with st.expander(
                str(title),
                expanded=False,
            ):

                with st.form(
                    f"edit_mep_{record_id}"
                ):

                    edited_title = st.text_input(
                        "MEP Work Item",
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
                        "Mechanical",
                        "Electrical",
                        "Plumbing",
                    ]

                    current_discipline = str(
                        record.get(
                            "discipline",
                            "Mechanical",
                        )
                    )

                    discipline_index = (
                        disciplines.index(
                            current_discipline
                        )
                        if current_discipline
                        in disciplines
                        else 0
                    )

                    edited_discipline = st.selectbox(
                        "Discipline",
                        disciplines,
                        index=discipline_index,
                    )

                    edited_system = st.text_input(
                        "System",
                        value=str(
                            record.get(
                                "system",
                                "",
                            )
                            or ""
                        ),
                    )

                    statuses = [
                        "Draft",
                        "In Coordination",
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
                        "Coordination Notes",
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
                            "MEP work item is required."
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

                        record["system"] = (
                            edited_system.strip()
                        )

                        record["status"] = (
                            edited_status
                        )

                        record["notes"] = (
                            edited_notes.strip()
                        )

                        save_memory(database)

                        st.success(
                            "MEP record updated successfully."
                        )

                        st.rerun()

                if st.button(
                    "Delete Record",
                    key=f"delete_mep_{record_id}",
                    use_container_width=True,
                ):

                    records.remove(record)

                    save_memory(database)

                    st.success(
                        "MEP record deleted successfully."
                    )

                    st.rerun()

    else:

        st.info(
            "No MEP records have been created yet."
        )

    st.divider()

    with st.form(
        "mep_record_form",
        clear_on_submit=True,
    ):

        title = st.text_input(
            "MEP Work Item"
        )

        project = st.text_input(
            "Project"
        )

        discipline = st.selectbox(
            "Discipline",
            [
                "Mechanical",
                "Electrical",
                "Plumbing",
            ],
        )

        system = st.text_input(
            "System"
        )

        status = st.selectbox(
            "Status",
            [
                "Draft",
                "In Coordination",
                "In Review",
                "Approved",
                "Issued",
            ],
        )

        notes = st.text_area(
            "Coordination Notes"
        )

        submitted = st.form_submit_button(
            "Add MEP Record",
            use_container_width=True,
        )

    if submitted:

        if not title.strip():
            st.error(
                "MEP work item is required."
            )
            return

        records.append(
            {
                "id": _next_id(records),
                "title": title.strip(),
                "project": project.strip(),
                "discipline": discipline,
                "system": system.strip(),
                "status": status,
                "notes": notes.strip(),
            }
        )

        save_memory(database)

        st.success(
            "MEP record added successfully."
        )

        st.rerun()