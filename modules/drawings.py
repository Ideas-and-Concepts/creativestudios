"""
Creative Studios
Drawings Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


def _normalize_drawings(
    database: dict[str, Any],
) -> list[dict[str, Any]]:

    value = database.get(
        "drawings",
        [],
    )

    if not isinstance(value, list):
        value = []

    drawings = []

    for index, item in enumerate(
        value,
        start=1,
    ):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            drawings.append(record)

        elif isinstance(item, str):

            drawings.append(
                {
                    "id": index,
                    "drawing_number": "",
                    "title": item,
                    "project": "",
                    "discipline": "Architectural",
                    "revision": "A",
                    "status": "Draft",
                    "scale": "1:100",
                    "created_at": "",
                }
            )

    database["drawings"] = drawings

    return drawings


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


def render_drawings_module(
    database: dict[str, Any],
) -> None:
    """Render editable drawing repository."""

    st.title("Drawings")
    st.caption(
        "Create, edit and manage architectural, structural and engineering drawings."
    )

    drawings = _normalize_drawings(
        database
    )

    tab_vault, tab_register = st.tabs(
        [
            "Drawing Vault",
            "Register Drawing",
        ]
    )

    with tab_vault:

        if not drawings:

            st.info(
                "No drawings have been registered yet."
            )

        else:

            for index, drawing in enumerate(
                drawings
            ):

                drawing_id = drawing.get(
                    "id",
                    index + 1,
                )

                title = drawing.get(
                    "title",
                    "Untitled Drawing",
                )

                number = drawing.get(
                    "drawing_number",
                    "",
                )

                heading = (
                    f"{number} — {title}"
                    if number
                    else str(title)
                )

                with st.expander(
                    heading,
                    expanded=False,
                ):

                    with st.form(
                        f"edit_drawing_{drawing_id}"
                    ):

                        edited_number = st.text_input(
                            "Drawing Number",
                            value=str(
                                number or ""
                            ),
                        )

                        edited_title = st.text_input(
                            "Drawing Title",
                            value=str(
                                title or ""
                            ),
                        )

                        edited_project = st.text_input(
                            "Project",
                            value=str(
                                drawing.get(
                                    "project",
                                    "",
                                )
                                or ""
                            ),
                        )

                        disciplines = [
                            "Architectural",
                            "Structural",
                            "Civil",
                            "Electrical",
                            "Mechanical",
                            "Plumbing",
                            "Other",
                        ]

                        current_discipline = str(
                            drawing.get(
                                "discipline",
                                "Architectural",
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

                        edited_revision = st.text_input(
                            "Revision",
                            value=str(
                                drawing.get(
                                    "revision",
                                    "A",
                                )
                                or ""
                            ),
                        )

                        statuses = [
                            "Draft",
                            "In Review",
                            "Approved",
                            "Issued",
                            "Superseded",
                        ]

                        current_status = str(
                            drawing.get(
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

                        edited_scale = st.text_input(
                            "Scale",
                            value=str(
                                drawing.get(
                                    "scale",
                                    "1:100",
                                )
                                or ""
                            ),
                        )

                        submitted = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )

                    if submitted:

                        if not edited_number.strip():
                            st.error(
                                "Drawing number is required."
                            )
                        elif not edited_title.strip():
                            st.error(
                                "Drawing title is required."
                            )
                        else:

                            drawing[
                                "drawing_number"
                            ] = edited_number.strip()

                            drawing["title"] = (
                                edited_title.strip()
                            )

                            drawing["project"] = (
                                edited_project.strip()
                            )

                            drawing[
                                "discipline"
                            ] = edited_discipline

                            drawing[
                                "revision"
                            ] = edited_revision.strip()

                            drawing[
                                "status"
                            ] = edited_status

                            drawing["scale"] = (
                                edited_scale.strip()
                            )

                            save_memory(database)

                            st.success(
                                "Drawing updated successfully."
                            )

                            st.rerun()

                    if st.button(
                        "Delete Drawing",
                        key=f"delete_drawing_{drawing_id}",
                        use_container_width=True,
                    ):

                        drawings.remove(drawing)

                        save_memory(database)

                        st.success(
                            "Drawing deleted successfully."
                        )

                        st.rerun()

    with tab_register:

        with st.form(
            "register_drawing_form",
            clear_on_submit=True,
        ):

            drawing_number = st.text_input(
                "Drawing Number"
            )

            title = st.text_input(
                "Drawing Title"
            )

            project = st.text_input(
                "Project"
            )

            discipline = st.selectbox(
                "Discipline",
                [
                    "Architectural",
                    "Structural",
                    "Civil",
                    "Electrical",
                    "Mechanical",
                    "Plumbing",
                    "Other",
                ],
            )

            revision = st.text_input(
                "Revision",
                value="A",
            )

            status = st.selectbox(
                "Status",
                [
                    "Draft",
                    "In Review",
                    "Approved",
                    "Issued",
                    "Superseded",
                ],
            )

            scale = st.text_input(
                "Scale",
                value="1:100",
            )

            submitted = st.form_submit_button(
                "Register Drawing",
                use_container_width=True,
            )

        if submitted:

            if not drawing_number.strip():
                st.error(
                    "Drawing number is required."
                )
                return

            if not title.strip():
                st.error(
                    "Drawing title is required."
                )
                return

            drawings.append(
                {
                    "id": _next_id(drawings),
                    "drawing_number": (
                        drawing_number.strip()
                    ),
                    "title": title.strip(),
                    "project": project.strip(),
                    "discipline": discipline,
                    "revision": revision.strip(),
                    "status": status,
                    "scale": scale.strip(),
                    "created_at": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                }
            )

            save_memory(database)

            st.success(
                "Drawing registered successfully."
            )

            st.rerun()