"""
Creative Studios
Drawings Module
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory
from modules.document_storage import render_module_files


DISCIPLINES = [
    "Architectural",
    "Structural",
    "Civil",
    "Electrical",
    "Mechanical",
    "Plumbing",
    "Other",
]

STATUSES = [
    "Draft",
    "In Review",
    "Approved",
    "Issued",
    "Superseded",
]


def _normalize(
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
            pass

    return max(ids, default=0) + 1


def render_drawings_module(
    database: dict[str, Any],
) -> None:

    st.title("Drawings")

    st.caption(
        "Manage architectural, structural and engineering "
        "construction drawings."
    )

    drawings = _normalize(database)

    architectural = [
        d for d in drawings
        if d.get("discipline")
        == "Architectural"
    ]

    structural = [
        d for d in drawings
        if d.get("discipline")
        == "Structural"
    ]

    overview, architectural_tab, structural_tab, register, files = (
        st.tabs(
            [
                "Overview",
                "Architectural Drawings",
                "Structural Drawings",
                "Register Drawing",
                "Files & Documents",
            ]
        )
    )

    with overview:

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Total Drawings",
            len(drawings),
        )

        c2.metric(
            "Architectural",
            len(architectural),
        )

        c3.metric(
            "Structural",
            len(structural),
        )

        c4.metric(
            "Issued",
            sum(
                d.get("status") == "Issued"
                for d in drawings
            ),
        )

    def render_register(
        records: list[dict[str, Any]],
        prefix: str,
    ) -> None:

        if not records:

            st.info(
                "No drawings in this category."
            )

            return

        for index, drawing in enumerate(records):

            drawing_id = drawing.get(
                "id",
                index + 1,
            )

            heading = (
                f"{drawing.get('drawing_number', '')} — "
                f"{drawing.get('title', 'Untitled Drawing')}"
            )

            with st.expander(
                heading,
                expanded=False,
            ):

                with st.form(
                    f"{prefix}_edit_{drawing_id}"
                ):

                    number = st.text_input(
                        "Drawing Number",
                        value=str(
                            drawing.get(
                                "drawing_number",
                                "",
                            )
                        ),
                    )

                    title = st.text_input(
                        "Drawing Title",
                        value=str(
                            drawing.get(
                                "title",
                                "",
                            )
                        ),
                    )

                    project = st.text_input(
                        "Project",
                        value=str(
                            drawing.get(
                                "project",
                                "",
                            )
                        ),
                    )

                    discipline = st.selectbox(
                        "Discipline",
                        DISCIPLINES,
                        index=(
                            DISCIPLINES.index(
                                drawing.get(
                                    "discipline",
                                    "Architectural",
                                )
                            )
                            if drawing.get(
                                "discipline",
                                "Architectural",
                            )
                            in DISCIPLINES
                            else 0
                        ),
                    )

                    revision = st.text_input(
                        "Revision",
                        value=str(
                            drawing.get(
                                "revision",
                                "A",
                            )
                        ),
                    )

                    status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=(
                            STATUSES.index(
                                drawing.get(
                                    "status",
                                    "Draft",
                                )
                            )
                            if drawing.get(
                                "status",
                                "Draft",
                            )
                            in STATUSES
                            else 0
                        ),
                    )

                    scale = st.text_input(
                        "Scale",
                        value=str(
                            drawing.get(
                                "scale",
                                "1:100",
                            )
                        ),
                    )

                    save = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save:

                    if not number.strip():

                        st.error(
                            "Drawing number is required."
                        )

                    elif not title.strip():

                        st.error(
                            "Drawing title is required."
                        )

                    else:

                        drawing.update(
                            {
                                "drawing_number": number.strip(),
                                "title": title.strip(),
                                "project": project.strip(),
                                "discipline": discipline,
                                "revision": revision.strip(),
                                "status": status,
                                "scale": scale.strip(),
                            }
                        )

                        save_memory(database)

                        st.success(
                            "Drawing updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Drawing",
                    key=f"{prefix}_delete_{drawing_id}",
                    use_container_width=True,
                ):

                    drawings.remove(drawing)

                    save_memory(database)

                    st.rerun()

    with architectural_tab:

        render_register(
            architectural,
            "architectural",
        )

    with structural_tab:

        render_register(
            structural,
            "structural",
        )

    with register:

        with st.form(
            "drawings_add",
            clear_on_submit=True,
        ):

            number = st.text_input(
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
                DISCIPLINES,
            )

            revision = st.text_input(
                "Revision",
                value="A",
            )

            status = st.selectbox(
                "Status",
                STATUSES,
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

            if not number.strip():

                st.error(
                    "Drawing number is required."
                )

            elif not title.strip():

                st.error(
                    "Drawing title is required."
                )

            else:

                drawings.append(
                    {
                        "id": _next_id(drawings),
                        "drawing_number": number.strip(),
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
                    "Drawing registered."
                )

                st.rerun()

    with files:

        projects = sorted(
            {
                str(
                    d.get(
                        "project",
                        "",
                    )
                )
                for d in drawings
                if d.get("project")
            }
        )

        render_module_files(
            database,
            "Drawings",
            project_options=projects,
        )