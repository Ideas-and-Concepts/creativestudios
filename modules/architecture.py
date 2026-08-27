"""
Creative Studios
Architecture Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _items(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    value = database.setdefault(
        "architecture",
        [],
    )

    if not isinstance(value, list):
        database["architecture"] = []
        return database["architecture"]

    return value


def render_architecture_module(
    database: dict[str, Any],
) -> None:
    """Render architecture workspace."""

    st.title("Architecture")
    st.caption(
        "Manage architectural design information and project activities."
    )

    records = _items(database)

    tab_overview, tab_design = st.tabs(
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
                for item in records
                if str(
                    item.get("stage", "")
                ).lower()
                == "concept"
            ),
        )

        columns[2].metric(
            "Design Development",
            sum(
                1
                for item in records
                if str(
                    item.get("stage", "")
                ).lower()
                == "design development"
            ),
        )

        columns[3].metric(
            "Issued",
            sum(
                1
                for item in records
                if str(
                    item.get("status", "")
                ).lower()
                == "issued"
            ),
        )

        st.info(
            "Use the Design Register to record architectural work items."
        )

    with tab_design:

        with st.form(
            "architecture_register_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Design Item",
            )

            project = st.text_input(
                "Project",
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
                "Notes",
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

            record_id = len(records) + 1

            records.append(
                {
                    "id": record_id,
                    "title": title.strip(),
                    "project": project.strip(),
                    "stage": stage,
                    "status": status,
                    "notes": notes.strip(),
                }
            )

            st.success(
                "Architecture record added successfully."
            )

            st.rerun()

        if records:

            st.subheader("Design Register")

            st.dataframe(
                records,
                use_container_width=True,
                hide_index=True,
            )