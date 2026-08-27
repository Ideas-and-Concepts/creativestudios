"""
Creative Studios
Drawings Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st


def _drawings(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    value = database.setdefault(
        "drawings",
        [],
    )

    if not isinstance(value, list):
        database["drawings"] = []
        return database["drawings"]

    return value


def _next_id(
    records: list[dict[str, Any]],
) -> int:

    ids = []

    for record in records:
        try:
            ids.append(
                int(record.get("id", 0))
            )
        except (TypeError, ValueError):
            continue

    return max(ids, default=0) + 1


def render_drawings_module(
    database: dict[str, Any],
) -> None:
    """Render drawing repository."""

    st.title("Drawings")
    st.caption(
        "Manage architectural, structural and engineering drawings."
    )

    drawings = _drawings(database)

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

            for drawing in drawings:

                number = drawing.get(
                    "drawing_number",
                    "-",
                )

                title = drawing.get(
                    "title",
                    "Untitled Drawing",
                )

                with st.container(
                    border=True
                ):

                    st.subheader(
                        f"{number} — {title}"
                    )

                    columns = st.columns(5)

                    columns[0].write(
                        f"**Discipline**  \n"
                        f"{drawing.get('discipline', '-')}"
                    )

                    columns[1].write(
                        f"**Revision**  \n"
                        f"{drawing.get('revision', '-')}"
                    )

                    columns[2].write(
                        f"**Status**  \n"
                        f"{drawing.get('status', '-')}"
                    )

                    columns[3].write(
                        f"**Project**  \n"
                        f"{drawing.get('project', '-')}"
                    )

                    columns[4].write(
                        f"**Scale**  \n"
                        f"{drawing.get('scale', '-')}"
                    )

    with tab_register:

        with st.form(
            "register_drawing_form",
            clear_on_submit=True,
        ):

            drawing_number = st.text_input(
                "Drawing Number",
            )

            title = st.text_input(
                "Drawing Title",
            )

            project = st.text_input(
                "Project",
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

            st.success(
                "Drawing registered successfully."
            )

            st.rerun()