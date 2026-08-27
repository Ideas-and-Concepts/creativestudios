"""
Creative Studios
Engineering Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _items(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    value = database.setdefault(
        "engineering",
        [],
    )

    if not isinstance(value, list):
        database["engineering"] = []
        return database["engineering"]

    return value


def render_engineering_module(
    database: dict[str, Any],
) -> None:
    """Render engineering workspace."""

    st.title("Engineering")
    st.caption(
        "Manage engineering disciplines, design records and technical activities."
    )

    records = _items(database)

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
            if record.get("discipline")
            == "Structural"
        ),
    )

    columns[2].metric(
        "Civil",
        sum(
            1
            for record in records
            if record.get("discipline")
            == "Civil"
        ),
    )

    columns[3].metric(
        "Infrastructure",
        sum(
            1
            for record in records
            if record.get("discipline")
            == "Infrastructure"
        ),
    )

    st.divider()

    with st.form(
        "engineering_record_form",
        clear_on_submit=True,
    ):

        title = st.text_input(
            "Engineering Work Item",
        )

        project = st.text_input(
            "Project",
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
            "Technical Notes",
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
                "id": len(records) + 1,
                "title": title.strip(),
                "project": project.strip(),
                "discipline": discipline,
                "status": status,
                "notes": notes.strip(),
            }
        )

        st.success(
            "Engineering record added successfully."
        )

        st.rerun()

    if records:

        st.subheader(
            "Engineering Register"
        )

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True,
        )
    else:

        st.info(
            "No engineering records have been created yet."
        )