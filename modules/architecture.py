"""
Creative Studios
Architecture Module

Editable architectural design workspace.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


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


def _normalize_records(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize architecture records."""

    value = database.get(
        "architecture",
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
            record.setdefault("stage", "Concept")
            record.setdefault("status", "Draft")
            record.setdefault("notes", "")

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
    """Return the next available record ID."""

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
    """Safely persist the database."""

    save_memory(database)

    st.session_state.database = database


def render_architecture_module(
    database: dict[str, Any],
) -> None:
    """Render the editable Architecture module."""

    st.title("Architecture")

    st.caption(
        "Manage architectural design records, stages, approvals and documentation."
    )

    records = _normalize_records(
        database
    )

    # ========================================================
    # METRICS
    # ========================================================

    total = len(records)

    concept = sum(
        1
        for record in records
        if str(
            record.get(
                "stage",
                "",
            )
        ).strip().lower()
        == "concept"
    )

    development = sum(
        1
        for record in records
        if str(
            record.get(
                "stage",
                "",
            )
        ).strip().lower()
        == "design development"
    )

    issued = sum(
        1
        for record in records
        if str(
            record.get(
                "status",
                "",
            )
        ).strip().lower()
        == "issued"
    )

    columns = st.columns(4)

    columns[0].metric(
        "Design Records",
        total,
    )

    columns[1].metric(
        "Concept",
        concept,
    )

    columns[2].metric(
        "Design Development",
        development,
    )

    columns[3].metric(
        "Issued",
        issued,
    )

    st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_add = st.tabs(
        [
            "Design Register",
            "Add Design",
        ]
    )

    # ========================================================
    # DESIGN REGISTER
    # ========================================================

    with tab_register:

        if not records:

            st.info(
                "No architectural design records have been created yet."
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
                    "Untitled Design",
                )
                or "Untitled Design"
            )

            project = str(
                record.get(
                    "project",
                    "",
                )
                or ""
            )

            with st.expander(
                title,
                expanded=False,
            ):

                with st.form(
                    f"architecture_edit_{record_id}"
                ):

                    edited_title = st.text_input(
                        "Design Item",
                        value=title,
                    )

                    edited_project = st.text_input(
                        "Project",
                        value=project,
                    )

                    current_stage = str(
                        record.get(
                            "stage",
                            "Concept",
                        )
                        or "Concept"
                    )

                    if current_stage not in STAGES:
                        current_stage = "Concept"

                    edited_stage = st.selectbox(
                        "Design Stage",
                        STAGES,
                        index=STAGES.index(
                            current_stage
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
                        "Notes",
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
                            "Design item is required."
                        )

                    else:

                        record["title"] = cleaned_title
                        record["project"] = edited_project.strip()
                        record["stage"] = edited_stage
                        record["status"] = edited_status
                        record["notes"] = edited_notes.strip()

                        _save(database)

                        st.success(
                            "Architecture record updated."
                        )

                        st.rerun()

                delete_key = (
                    f"architecture_delete_{record_id}"
                )

                if st.button(
                    "Delete Record",
                    key=delete_key,
                    use_container_width=True,
                ):

                    database["architecture"] = [
                        item
                        for item in records
                        if item is not record
                    ]

                    _save(database)

                    st.success(
                        "Architecture record deleted."
                    )

                    st.rerun()

    # ========================================================
    # ADD DESIGN
    # ========================================================

    with tab_add:

        with st.form(
            "architecture_add_form",
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

            cleaned_title = title.strip()

            if not cleaned_title:

                st.error(
                    "Design item is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(records),
                        "title": cleaned_title,
                        "project": project.strip(),
                        "stage": stage,
                        "status": status,
                        "notes": notes.strip(),
                    }
                )

                _save(database)

                st.success(
                    "Architecture record added."
                )

                st.rerun()