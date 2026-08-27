"""
Creative Studios
Engineering Module

Editable engineering design workspace.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


DISCIPLINES = [
    "Structural",
    "Civil",
    "Infrastructure",
    "Geotechnical",
    "Transportation",
    "Environmental",
    "Other",
]

STATUSES = [
    "Draft",
    "In Review",
    "Approved",
    "Issued",
]


def _normalize_records(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize engineering records."""

    value = database.get(
        "engineering",
        [],
    )

    if not isinstance(value, list):
        value = []

    records: list[dict[str, Any]] = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            record.setdefault("title", "")
            record.setdefault("project", "")
            record.setdefault("discipline", "Other")
            record.setdefault("status", "Draft")
            record.setdefault("notes", "")

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
    """Return the next available engineering ID."""

    highest = 0

    for record in records:

        if not isinstance(record, dict):
            continue

        try:
            record_id = int(
                record.get(
                    "id",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        highest = max(
            highest,
            record_id,
        )

    return highest + 1


def _save(
    database: dict[str, Any],
) -> None:
    """Persist the database."""

    save_memory(database)

    st.session_state.database = database


def render_engineering_module(
    database: dict[str, Any],
) -> None:
    """Render the editable Engineering module."""

    st.title("Engineering")

    st.caption(
        "Manage engineering disciplines, technical design records and project engineering activities."
    )

    records = _normalize_records(
        database
    )

    # ========================================================
    # METRICS
    # ========================================================

    total = len(records)

    structural = sum(
        1
        for record in records
        if str(
            record.get(
                "discipline",
                "",
            )
        )
        == "Structural"
    )

    civil = sum(
        1
        for record in records
        if str(
            record.get(
                "discipline",
                "",
            )
        )
        == "Civil"
    )

    infrastructure = sum(
        1
        for record in records
        if str(
            record.get(
                "discipline",
                "",
            )
        )
        == "Infrastructure"
    )

    columns = st.columns(4)

    columns[0].metric(
        "Engineering Records",
        total,
    )

    columns[1].metric(
        "Structural",
        structural,
    )

    columns[2].metric(
        "Civil",
        civil,
    )

    columns[3].metric(
        "Infrastructure",
        infrastructure,
    )

    st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_add = st.tabs(
        [
            "Engineering Register",
            "Add Engineering Record",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        if not records:

            st.info(
                "No engineering records have been created yet."
            )

        for index, record in enumerate(
            records
        ):

            record_id = record.get(
                "id",
                index + 1,
            )

            title = str(
                record.get(
                    "title",
                    "Engineering Work Item",
                )
                or "Engineering Work Item"
            )

            with st.expander(
                title,
                expanded=False,
            ):

                with st.form(
                    f"engineering_edit_{record_id}"
                ):

                    edited_title = st.text_input(
                        "Engineering Work Item",
                        value=title,
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

                    current_discipline = str(
                        record.get(
                            "discipline",
                            "Other",
                        )
                        or "Other"
                    )

                    if current_discipline not in DISCIPLINES:
                        current_discipline = "Other"

                    edited_discipline = st.selectbox(
                        "Discipline",
                        DISCIPLINES,
                        index=DISCIPLINES.index(
                            current_discipline
                        ),
                    )

                    current_status = str(
                        record.get(
                            "status",
                            "Draft",
                        )
                        or "Draft"
                    )

                    if current_status not in STATUSES:
                        current_status = "Draft"

                    edited_status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=STATUSES.index(
                            current_status
                        ),
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

                    save_clicked = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save_clicked:

                    cleaned_title = edited_title.strip()

                    if not cleaned_title:

                        st.error(
                            "Engineering work item is required."
                        )

                    else:

                        record["title"] = cleaned_title
                        record["project"] = edited_project.strip()
                        record["discipline"] = edited_discipline
                        record["status"] = edited_status
                        record["notes"] = edited_notes.strip()

                        _save(database)

                        st.success(
                            "Engineering record updated."
                        )

                        st.rerun()

                delete_key = (
                    f"engineering_delete_{record_id}"
                )

                if st.button(
                    "Delete Record",
                    key=delete_key,
                    use_container_width=True,
                ):

                    database["engineering"] = [
                        item
                        for item in records
                        if item is not record
                    ]

                    _save(database)

                    st.success(
                        "Engineering record deleted."
                    )

                    st.rerun()

    # ========================================================
    # ADD
    # ========================================================

    with tab_add:

        with st.form(
            "engineering_add_form",
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

            cleaned_title = title.strip()

            if not cleaned_title:

                st.error(
                    "Engineering work item is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(records),
                        "title": cleaned_title,
                        "project": project.strip(),
                        "discipline": discipline,
                        "status": status,
                        "notes": notes.strip(),
                    }
                )

                _save(database)

                st.success(
                    "Engineering record added."
                )

                st.rerun()