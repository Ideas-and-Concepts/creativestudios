"""
Creative Studios
Drawings Module
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from modules.branding import render_module_header
from modules.database import (
    add_record,
    delete_record,
    next_id,
    update_record,
)


DRAWING_STATUSES = [
    "Draft",
    "For Review",
    "Approved",
    "Issued",
    "Superseded",
]


def _text(value: Any) -> str:
    return str(value or "").strip()


def render_drawings_module(
    database: dict[str, Any],
) -> None:

    render_module_header(
        "Drawings",
        "Manage architectural, engineering and construction drawings.",
    )

    drawings = database.get(
        "drawings",
        [],
    )

    if not isinstance(
        drawings,
        list,
    ):
        drawings = []

    search = st.text_input(
        "Search drawings",
        placeholder="Search drawing number, title, project or discipline...",
        key="drawings_search",
    )

    if st.button(
        "New Drawing",
        key="new_drawing",
    ):

        st.session_state[
            "show_drawing_form"
        ] = True

    if st.session_state.get(
        "show_drawing_form",
        False,
    ):

        with st.form(
            "drawing_form",
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

            discipline = st.text_input(
                "Discipline"
            )

            revision = st.text_input(
                "Revision",
                value="0",
            )

            status = st.selectbox(
                "Status",
                DRAWING_STATUSES,
            )

            submitted = st.form_submit_button(
                "Create Drawing",
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

                    drawing = {
                        "id": next_id(
                            drawings
                        ),
                        "drawing_number": number.strip(),
                        "title": title.strip(),
                        "project": project.strip(),
                        "discipline": discipline.strip(),
                        "revision": revision.strip(),
                        "status": status,
                    }

                    add_record(
                        database,
                        "drawings",
                        drawing,
                    )

                    st.session_state[
                        "show_drawing_form"
                    ] = False

                    st.success(
                        "Drawing created."
                    )

                    st.rerun()

    search_value = search.lower().strip()

    filtered = []

    for drawing in drawings:

        if not isinstance(
            drawing,
            dict,
        ):
            continue

        searchable = " ".join(
            [
                _text(drawing.get("drawing_number")),
                _text(drawing.get("title")),
                _text(drawing.get("project")),
                _text(drawing.get("discipline")),
                _text(drawing.get("status")),
            ]
        ).lower()

        if (
            not search_value
            or search_value in searchable
        ):

            filtered.append(drawing)

    st.metric(
        "Drawings",
        len(drawings),
    )

    st.write("")

    if not filtered:

        st.info(
            "No drawings found."
        )

        return

    for drawing in filtered:

        drawing_id = drawing.get(
            "id"
        )

        number = html.escape(
            _text(
                drawing.get(
                    "drawing_number",
                    "",
                )
            )
        )

        title = html.escape(
            _text(
                drawing.get(
                    "title",
                    "Untitled Drawing",
                )
            )
        )

        project = html.escape(
            _text(
                drawing.get(
                    "project",
                    "",
                )
            )
        )

        discipline = html.escape(
            _text(
                drawing.get(
                    "discipline",
                    "",
                )
            )
        )

        revision = html.escape(
            _text(
                drawing.get(
                    "revision",
                    "0",
                )
            )
        )

        status = html.escape(
            _text(
                drawing.get(
                    "status",
                    "Draft",
                )
            )
        )

        st.markdown(
            f"""
            <div class="cs-card">

                <div style="
                    color:#FFFFFF;
                    font-size:16px;
                    font-weight:850;
                ">
                    {number} · {title}
                </div>

                <div style="
                    color:#64748B;
                    font-size:12px;
                    margin-top:6px;
                ">
                    {project}
                    &nbsp; • &nbsp;
                    {discipline}
                    &nbsp; • &nbsp;
                    Rev {revision}
                    &nbsp; • &nbsp;
                    {status}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander(
            f"Edit Drawing #{drawing_id}"
        ):

            with st.form(
                f"edit_drawing_{drawing_id}"
            ):

                edit_number = st.text_input(
                    "Drawing Number",
                    value=_text(
                        drawing.get(
                            "drawing_number"
                        )
                    ),
                )

                edit_title = st.text_input(
                    "Drawing Title",
                    value=_text(
                        drawing.get("title")
                    ),
                )

                edit_project = st.text_input(
                    "Project",
                    value=_text(
                        drawing.get("project")
                    ),
                )

                edit_discipline = st.text_input(
                    "Discipline",
                    value=_text(
                        drawing.get("discipline")
                    ),
                )

                edit_revision = st.text_input(
                    "Revision",
                    value=_text(
                        drawing.get(
                            "revision",
                            "0",
                        )
                    ),
                )

                current_status = _text(
                    drawing.get(
                        "status",
                        "Draft",
                    )
                )

                edit_status = st.selectbox(
                    "Status",
                    DRAWING_STATUSES,
                    index=(
                        DRAWING_STATUSES.index(
                            current_status
                        )
                        if current_status
                        in DRAWING_STATUSES
                        else 0
                    ),
                )

                save = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if save:

                    update_record(
                        database,
                        "drawings",
                        drawing_id,
                        {
                            "drawing_number": edit_number.strip(),
                            "title": edit_title.strip(),
                            "project": edit_project.strip(),
                            "discipline": edit_discipline.strip(),
                            "revision": edit_revision.strip(),
                            "status": edit_status,
                        },
                    )

                    st.success(
                        "Drawing updated."
                    )

                    st.rerun()

            if st.button(
                "Delete Drawing",
                key=f"delete_drawing_{drawing_id}",
            ):

                delete_record(
                    database,
                    "drawings",
                    drawing_id,
                )

                st.success(
                    "Drawing deleted."
                )

                st.rerun()