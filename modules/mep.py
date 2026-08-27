"""
Creative Studios
MEP Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _items(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    value = database.setdefault(
        "mep",
        [],
    )

    if not isinstance(value, list):
        database["mep"] = []
        return database["mep"]

    return value


def render_mep_module(
    database: dict[str, Any],
) -> None:
    """Render mechanical, electrical and plumbing workspace."""

    st.title("MEP")
    st.caption(
        "Manage mechanical, electrical and plumbing coordination."
    )

    records = _items(database)

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
            if record.get("discipline")
            == "Mechanical"
        ),
    )

    columns[2].metric(
        "Electrical",
        sum(
            1
            for record in records
            if record.get("discipline")
            == "Electrical"
        ),
    )

    columns[3].metric(
        "Plumbing",
        sum(
            1
            for record in records
            if record.get("discipline")
            == "Plumbing"
        ),
    )

    columns[4].metric(
        "Approved",
        sum(
            1
            for record in records
            if str(
                record.get("status", "")
            ).lower()
            == "approved"
        ),
    )

    st.divider()

    with st.form(
        "mep_record_form",
        clear_on_submit=True,
    ):

        title = st.text_input(
            "MEP Work Item",
        )

        project = st.text_input(
            "Project",
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
            "System",
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
            "Coordination Notes",
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
                "id": len(records) + 1,
                "title": title.strip(),
                "project": project.strip(),
                "discipline": discipline,
                "system": system.strip(),
                "status": status,
                "notes": notes.strip(),
            }
        )

        st.success(
            "MEP record added successfully."
        )

        st.rerun()

    if records:

        st.subheader(
            "MEP Coordination Register"
        )

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No MEP records have been created yet."
        )