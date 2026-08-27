"""
Creative Studios
Drawings Module

AEC drawing repository with separate architectural
and structural drawing registers.
"""

from future import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory

DISCIPLINES = [
"Architectural",
"Structural",
"Civil",
"Electrical",
"Mechanical",
"Plumbing",
"Other",
]

DRAWING_TYPES = {
"Architectural": [
"Site Plan",
"Floor Plan",
"Roof Plan",
"Elevation",
"Section",
"Reflected Ceiling Plan",
"Detail",
"Schedule",
"General Arrangement",
"Other",
],
"Structural": [
"Foundation Plan",
"Column Layout",
"Beam Layout",
"Slab Plan",
"Roof Structure",
"Stair Detail",
"Reinforcement Detail",
"Structural General Arrangement",
"Structural Detail",
"Other",
],
"Civil": [
"Site Development Plan",
"Road Layout",
"Drainage Plan",
"Grading Plan",
"Utility Plan",
"Detail",
"Other",
],
"Electrical": [
"Lighting Plan",
"Power Plan",
"Single Line Diagram",
"Panel Schedule",
"Detail",
"Other",
],
"Mechanical": [
"HVAC Plan",
"Mechanical Services Plan",
"Equipment Layout",
"Detail",
"Other",
],
"Plumbing": [
"Water Supply Plan",
"Drainage Plan",
"Sanitary Plan",
"Detail",
"Other",
],
"Other": [
"General Drawing",
"Detail",
"Other",
],
}

STATUSES = [
"Draft",
"In Review",
"Approved",
"Issued",
"Superseded",
]

DEFAULT_SCALE = "1:100"

def _normalize_drawings(
database: dict[str, Any],
) -> list[dict[str, Any]]:
"""Normalize drawing records."""

value = database.get(
    "drawings",
    [],
)

if not isinstance(value, list):
    value = []

drawings: list[dict[str, Any]] = []

for index, item in enumerate(value, start=1):
    if isinstance(item, dict):
        record = dict(item)

        if not record.get("id"):
            record["id"] = index

        record.setdefault(
            "discipline",
            "Architectural",
        )

        record.setdefault(
            "revision",
            "A",
        )

        record.setdefault(
            "status",
            "Draft",
        )

        record.setdefault(
            "scale",
            DEFAULT_SCALE,
        )

        drawings.append(record)

    elif isinstance(item, str):
        drawings.append(
            {
                "id": index,
                "drawing_number": "",
                "title": item,
                "project": "",
                "discipline": "Architectural",
                "drawing_type": "Other",
                "revision": "A",
                "status": "Draft",
                "scale": DEFAULT_SCALE,
                "prepared_by": "",
                "checked_by": "",
                "approved_by": "",
                "description": "",
                "created_at": "",
            }
        )

database["drawings"] = drawings

return drawings

def _next_id(
records: list[dict[str, Any]],
) -> int:
"""Return the next available drawing ID."""

ids: list[int] = []

for record in records:
    try:
        ids.append(
            int(record.get("id", 0))
        )
    except (TypeError, ValueError):
        continue

return max(ids, default=0) + 1

def _filtered_drawings(
drawings: list[dict[str, Any]],
discipline: str,
) -> list[dict[str, Any]]:
"""Return drawings for a discipline."""

return [
    drawing
    for drawing in drawings
    if str(
        drawing.get(
            "discipline",
            "",
        )
    ).strip().lower()
    == discipline.lower()
]

def _render_drawing_editor(
database: dict[str, Any],
drawings: list[dict[str, Any]],
drawing: dict[str, Any],
index: int,
) -> None:
"""Render an editable drawing record."""

drawing_id = drawing.get(
    "id",
    index + 1,
)

title = str(
    drawing.get(
        "title",
        "Untitled Drawing",
    )
    or ""
)

number = str(
    drawing.get(
        "drawing_number",
        "",
    )
    or ""
)

discipline = str(
    drawing.get(
        "discipline",
        "Architectural",
    )
)

if discipline not in DISCIPLINES:
    discipline = "Other"

heading = (
    f"{number} — {title}"
    if number
    else title or "Untitled Drawing"
)

with st.expander(
    heading,
    expanded=False,
):
    with st.form(
        f"edit_drawing_{drawing_id}"
    ):
        col1, col2 = st.columns(2)

        with col1:
            edited_number = st.text_input(
                "Drawing Number",
                value=number,
            )

            edited_title = st.text_input(
                "Drawing Title",
                value=title,
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

            edited_discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
                index=DISCIPLINES.index(
                    discipline
                ),
            )

            current_type = str(
                drawing.get(
                    "drawing_type",
                    "Other",
                )
            )

            type_options = DRAWING_TYPES.get(
                edited_discipline,
                ["Other"],
            )

            edited_type = st.selectbox(
                "Drawing Type",
                type_options,
                index=(
                    type_options.index(
                        current_type
                    )
                    if current_type in type_options
                    else len(type_options) - 1
                ),
            )

        with col2:
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

            current_status = str(
                drawing.get(
                    "status",
                    "Draft",
                )
            )

            edited_status = st.selectbox(
                "Status",
                STATUSES,
                index=(
                    STATUSES.index(
                        current_status
                    )
                    if current_status in STATUSES
                    else 0
                ),
            )

            edited_scale = st.text_input(
                "Scale",
                value=str(
                    drawing.get(
                        "scale",
                        DEFAULT_SCALE,
                    )
                    or ""
                ),
            )

            edited_prepared = st.text_input(
                "Prepared By",
                value=str(
                    drawing.get(
                        "prepared_by",
                        "",
                    )
                    or ""
                ),
            )

            edited_checked = st.text_input(
                "Checked By",
                value=str(
                    drawing.get(
                        "checked_by",
                        "",
                    )
                    or ""
                ),
            )

            edited_approved = st.text_input(
                "Approved By",
                value=str(
                    drawing.get(
                        "approved_by",
                        "",
                    )
                    or ""
                ),
            )

        edited_description = st.text_area(
            "Description",
            value=str(
                drawing.get(
                    "description",
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
        if not edited_number.strip():
            st.error(
                "Drawing number is required."
            )
            return

        if not edited_title.strip():
            st.error(
                "Drawing title is required."
            )
            return

        drawing["drawing_number"] = (
            edited_number.strip()
        )
        drawing["title"] = (
            edited_title.strip()
        )
        drawing["project"] = (
            edited_project.strip()
        )
        drawing["discipline"] = (
            edited_discipline
        )
        drawing["drawing_type"] = (
            edited_type
        )
        drawing["revision"] = (
            edited_revision.strip()
        )
        drawing["status"] = (
            edited_status
        )
        drawing["scale"] = (
            edited_scale.strip()
        )
        drawing["prepared_by"] = (
            edited_prepared.strip()
        )
        drawing["checked_by"] = (
            edited_checked.strip()
        )
        drawing["approved_by"] = (
            edited_approved.strip()
        )
        drawing["description"] = (
            edited_description.strip()
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

def _render_discipline_register(
database: dict[str, Any],
drawings: list[dict[str, Any]],
discipline: str,
) -> None:
"""Render a discipline-specific drawing register."""

discipline_drawings = _filtered_drawings(
    drawings,
    discipline,
)

if not discipline_drawings:
    st.info(
        f"No {discipline.lower()} drawings have been registered."
    )
    return

for index, drawing in enumerate(
    discipline_drawings
):
    _render_drawing_editor(
        database,
        drawings,
        drawing,
        index,
    )

def _render_register_form(
database: dict[str, Any],
drawings: list[dict[str, Any]],
) -> None:
"""Render new drawing registration form."""

with st.form(
    "register_drawing_form",
    clear_on_submit=True,
):
    col1, col2 = st.columns(2)

    with col1:
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
            DISCIPLINES,
        )

        drawing_type = st.selectbox(
            "Drawing Type",
            DRAWING_TYPES["Architectural"],
        )

    with col2:
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
            value=DEFAULT_SCALE,
        )

        prepared_by = st.text_input(
            "Prepared By"
        )

        checked_by = st.text_input(
            "Checked By"
        )

        approved_by = st.text_input(
            "Approved By"
        )

    description = st.text_area(
        "Description"
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

    # The form's drawing type list is initially architectural.
    # If another discipline was selected, safely use the first
    # appropriate type where possible.
    discipline_types = DRAWING_TYPES.get(
        discipline,
        ["Other"],
    )

    if drawing_type not in discipline_types:
        drawing_type = discipline_types[0]

    drawings.append(
        {
            "id": _next_id(drawings),
            "drawing_number": drawing_number.strip(),
            "title": title.strip(),
            "project": project.strip(),
            "discipline": discipline,
            "drawing_type": drawing_type,
            "revision": revision.strip(),
            "status": status,
            "scale": scale.strip(),
            "prepared_by": prepared_by.strip(),
            "checked_by": checked_by.strip(),
            "approved_by": approved_by.strip(),
            "description": description.strip(),
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

def render_drawings_module(
database: dict[str, Any],
) -> None:
"""Render the drawing repository."""

st.title("Drawings")

st.caption(
    "Manage architectural, structural and engineering drawing records."
)

drawings = _normalize_drawings(database)

architectural = _filtered_drawings(
    drawings,
    "Architectural",
)

structural = _filtered_drawings(
    drawings,
    "Structural",
)

total = len(drawings)

columns = st.columns(4)

columns[0].metric(
    "Total Drawings",
    total,
)

columns[1].metric(
    "Architectural",
    len(architectural),
)

columns[2].metric(
    "Structural",
    len(structural),
)

columns[3].metric(
    "Other Engineering",
    max(
        0,
        total
        - len(architectural)
        - len(structural),
    ),
)

st.divider()

tab_architecture, tab_structure, tab_other, tab_register = st.tabs(
    [
        "Architectural Drawings",
        "Structural Drawings",
        "Other Engineering",
        "Register Drawing",
    ]
)

with tab_architecture:
    st.subheader(
        "Architectural Drawings"
    )

    _render_discipline_register(
        database,
        drawings,
        "Architectural",
    )

with tab_structure:
    st.subheader(
        "Structural Drawings"
    )

    _render_discipline_register(
        database,
        drawings,
        "Structural",
    )

with tab_other:
    st.subheader(
        "Other Engineering Drawings"
    )

    other_disciplines = [
        discipline
        for discipline in DISCIPLINES
        if discipline not in {
            "Architectural",
            "Structural",
        }
    ]

    for discipline in other_disciplines:
        discipline_drawings = _filtered_drawings(
            drawings,
            discipline,
        )

        if discipline_drawings:
            st.markdown(
                f"### {discipline}"
            )

            _render_discipline_register(
                database,
                drawings,
                discipline,
            )

with tab_register:
    st.subheader(
        "Register New Drawing"
    )

    _render_register_form(
        database,
        drawings,
    )