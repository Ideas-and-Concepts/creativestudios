"""
Creative Studios
Drawings Module

Central construction drawing register.

Drawings are classified primarily as:
    Architectural
    Structural

Additional engineering disciplines are supported for future expansion.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# CONSTANTS
# ============================================================

DRAWING_CATEGORIES = [
    "Architectural",
    "Structural",
]

DISCIPLINES = [
    "Architectural",
    "Structural",
    "Civil",
    "Electrical",
    "Mechanical",
    "Plumbing",
    "Other",
]

ARCHITECTURAL_TYPES = [
    "Site Plan",
    "Floor Plan",
    "Roof Plan",
    "Elevation",
    "Section",
    "Architectural Detail",
    "Door Schedule",
    "Window Schedule",
    "Finishes Schedule",
    "Reflected Ceiling Plan",
    "As-Built",
    "Other",
]

STRUCTURAL_TYPES = [
    "Foundation Plan",
    "Column Layout",
    "Beam Layout",
    "Slab Plan",
    "Roof Structure",
    "Reinforcement Detail",
    "Structural Section",
    "Structural Detail",
    "Connection Detail",
    "As-Built",
    "Other",
]

STATUSES = [
    "Draft",
    "In Review",
    "Approved",
    "Issued for Construction",
    "As-Built",
    "Superseded",
]

SCALES = [
    "1:20",
    "1:25",
    "1:50",
    "1:75",
    "1:100",
    "1:200",
    "1:500",
    "NTS",
    "Other",
]


# ============================================================
# HELPERS
# ============================================================

def _text(value: Any, default: str = "") -> str:
    """Convert a value safely to text."""

    if value is None:
        return default

    return str(value).strip()


def _normalize_drawings(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize legacy and current drawing records."""

    value = database.get("drawings", [])

    if not isinstance(value, list):
        value = []

    drawings: list[dict[str, Any]] = []

    for index, item in enumerate(value, start=1):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            record.setdefault("drawing_number", "")
            record.setdefault("title", "")
            record.setdefault("project", "")
            record.setdefault("category", "")
            record.setdefault("discipline", "Architectural")
            record.setdefault("drawing_type", "Other")
            record.setdefault("revision", "A")
            record.setdefault("status", "Draft")
            record.setdefault("scale", "1:100")
            record.setdefault("prepared_by", "")
            record.setdefault("checked_by", "")
            record.setdefault("approved_by", "")
            record.setdefault("issue_date", "")
            record.setdefault("notes", "")
            record.setdefault("created_at", "")

            # Older versions used discipline without category.
            if not _text(record.get("category")):

                discipline = _text(
                    record.get(
                        "discipline",
                        "Architectural",
                    )
                )

                if discipline == "Structural":
                    record["category"] = "Structural"
                else:
                    record["category"] = "Architectural"

            drawings.append(record)

        elif isinstance(item, str):

            drawings.append(
                {
                    "id": index,
                    "drawing_number": "",
                    "title": item,
                    "project": "",
                    "category": "Architectural",
                    "discipline": "Architectural",
                    "drawing_type": "Other",
                    "revision": "A",
                    "status": "Draft",
                    "scale": "1:100",
                    "prepared_by": "",
                    "checked_by": "",
                    "approved_by": "",
                    "issue_date": "",
                    "notes": "",
                    "created_at": "",
                }
            )

    database["drawings"] = drawings

    return drawings


def _next_id(
    records: list[dict[str, Any]],
) -> int:
    """Return the next available drawing ID."""

    highest = 0

    for record in records:

        if not isinstance(record, dict):
            continue

        try:
            value = int(
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
            value,
        )

    return highest + 1


def _save(
    database: dict[str, Any],
) -> None:
    """Persist drawing changes."""

    save_memory(database)
    st.session_state.database = database


def _select_index(
    values: list[str],
    current: Any,
    default: int = 0,
) -> int:
    """Return a safe selectbox index."""

    value = _text(current)

    if value in values:
        return values.index(value)

    return min(
        default,
        len(values) - 1,
    )


def _drawing_types_for_category(
    category: str,
) -> list[str]:
    """Return drawing types appropriate for a category."""

    if category == "Structural":
        return STRUCTURAL_TYPES

    return ARCHITECTURAL_TYPES


# ============================================================
# MAIN MODULE
# ============================================================

def render_drawings_module(
    database: dict[str, Any],
) -> None:
    """Render the central construction drawing register."""

    st.title("Drawings")

    st.caption(
        "Manage controlled architectural and structural construction drawings, "
        "revisions, approvals and issue status."
    )

    drawings = _normalize_drawings(database)

    architectural = [
        drawing
        for drawing in drawings
        if _text(
            drawing.get(
                "category",
                "Architectural",
            )
        )
        == "Architectural"
    ]

    structural = [
        drawing
        for drawing in drawings
        if _text(
            drawing.get(
                "category",
                "Architectural",
            )
        )
        == "Structural"
    ]

    issued = sum(
        1
        for drawing in drawings
        if _text(
            drawing.get("status")
        ).lower()
        == "issued for construction"
    )

    superseded = sum(
        1
        for drawing in drawings
        if _text(
            drawing.get("status")
        ).lower()
        == "superseded"
    )

    # ========================================================
    # METRICS
    # ========================================================

    columns = st.columns(5)

    columns[0].metric(
        "Total Drawings",
        len(drawings),
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
        "Issued",
        issued,
    )

    columns[4].metric(
        "Superseded",
        superseded,
    )

    st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_architectural, tab_structural, tab_all, tab_add = st.tabs(
        [
            "Architectural Drawings",
            "Structural Drawings",
            "All Drawings",
            "Register Drawing",
        ]
    )

    # ========================================================
    # DRAWING EDITOR
    # ========================================================

    def render_drawing_records(
        records: list[dict[str, Any]],
        prefix: str,
    ) -> None:
        """Render editable drawing records."""

        if not records:

            st.info(
                "No drawings are registered in this category."
            )

            return

        search = st.text_input(
            "Search drawings",
            placeholder="Search by drawing number, title, project or revision",
            key=f"drawing_search_{prefix}",
        )

        search_term = search.strip().lower()

        filtered = []

        for drawing in records:

            searchable = " ".join(
                [
                    _text(drawing.get("drawing_number")),
                    _text(drawing.get("title")),
                    _text(drawing.get("project")),
                    _text(drawing.get("discipline")),
                    _text(drawing.get("drawing_type")),
                    _text(drawing.get("revision")),
                    _text(drawing.get("status")),
                    _text(drawing.get("prepared_by")),
                ]
            ).lower()

            if (
                not search_term
                or search_term in searchable
            ):
                filtered.append(drawing)

        if not filtered:

            st.info(
                "No drawings match the search."
            )

            return

        for index, drawing in enumerate(filtered):

            drawing_id = drawing.get(
                "id",
                index + 1,
            )

            number = _text(
                drawing.get("drawing_number")
            )

            title = (
                _text(
                    drawing.get(
                        "title",
                        "Untitled Drawing",
                    )
                )
                or "Untitled Drawing"
            )

            heading = title

            if number:
                heading = f"{number} — {title}"

            with st.expander(
                heading,
                expanded=False,
            ):

                st.caption(
                    f"Revision {_text(drawing.get('revision'), 'A')} | "
                    f"{_text(drawing.get('status'), 'Draft')}"
                )

                category = _text(
                    drawing.get(
                        "category",
                        "Architectural",
                    )
                )

                if category not in DRAWING_CATEGORIES:
                    category = "Architectural"

                with st.form(
                    f"drawing_edit_{prefix}_{drawing_id}"
                ):

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
                        value=_text(
                            drawing.get("project")
                        ),
                    )

                    edited_category = st.selectbox(
                        "Drawing Category",
                        DRAWING_CATEGORIES,
                        index=DRAWING_CATEGORIES.index(
                            category
                        ),
                    )

                    available_types = (
                        _drawing_types_for_category(
                            edited_category
                        )
                    )

                    current_type = _text(
                        drawing.get(
                            "drawing_type",
                            "Other",
                        )
                    )

                    if current_type not in available_types:
                        current_type = "Other"

                    edited_type = st.selectbox(
                        "Drawing Type",
                        available_types,
                        index=available_types.index(
                            current_type
                        ),
                    )

                    if edited_category == "Structural":
                        discipline_options = [
                            "Structural",
                            "Civil",
                            "Geotechnical",
                            "Other",
                        ]
                    else:
                        discipline_options = [
                            "Architectural",
                            "Other",
                        ]

                    current_discipline = _text(
                        drawing.get(
                            "discipline",
                            edited_category,
                        )
                    )

                    if (
                        current_discipline
                        not in discipline_options
                    ):
                        current_discipline = (
                            discipline_options[0]
                        )

                    edited_discipline = st.selectbox(
                        "Discipline",
                        discipline_options,
                        index=discipline_options.index(
                            current_discipline
                        ),
                    )

                    edited_revision = st.text_input(
                        "Revision",
                        value=_text(
                            drawing.get(
                                "revision",
                                "A",
                            )
                        ),
                    )

                    edited_status = st.selectbox(
                        "Status",
                        STATUSES,
                        index=_select_index(
                            STATUSES,
                            drawing.get("status"),
                        ),
                    )

                    edited_scale = st.selectbox(
                        "Scale",
                        SCALES,
                        index=_select_index(
                            SCALES,
                            drawing.get(
                                "scale",
                                "1:100",
                            ),
                            SCALES.index("Other"),
                        ),
                    )

                    edited_prepared = st.text_input(
                        "Prepared By",
                        value=_text(
                            drawing.get("prepared_by")
                        ),
                    )

                    edited_checked = st.text_input(
                        "Checked By",
                        value=_text(
                            drawing.get("checked_by")
                        ),
                    )

                    edited_approved = st.text_input(
                        "Approved By",
                        value=_text(
                            drawing.get("approved_by")
                        ),
                    )

                    edited_issue_date = st.text_input(
                        "Issue Date",
                        value=_text(
                            drawing.get("issue_date")
                        ),
                        placeholder="YYYY-MM-DD",
                    )

                    edited_notes = st.text_area(
                        "Notes",
                        value=_text(
                            drawing.get("notes")
                        ),
                    )

                    save_clicked = st.form_submit_button(
                        "Save Changes",
                        use_container_width=True,
                    )

                if save_clicked:

                    cleaned_number = (
                        edited_number.strip()
                    )

                    cleaned_title = (
                        edited_title.strip()
                    )

                    if not cleaned_number:

                        st.error(
                            "Drawing number is required."
                        )

                    elif not cleaned_title:

                        st.error(
                            "Drawing title is required."
                        )

                    else:

                        drawing["drawing_number"] = cleaned_number
                        drawing["title"] = cleaned_title
                        drawing["project"] = edited_project.strip()
                        drawing["category"] = edited_category
                        drawing["discipline"] = edited_discipline
                        drawing["drawing_type"] = edited_type
                        drawing["revision"] = edited_revision.strip()
                        drawing["status"] = edited_status
                        drawing["scale"] = edited_scale
                        drawing["prepared_by"] = edited_prepared.strip()
                        drawing["checked_by"] = edited_checked.strip()
                        drawing["approved_by"] = edited_approved.strip()
                        drawing["issue_date"] = edited_issue_date.strip()
                        drawing["notes"] = edited_notes.strip()

                        _save(database)

                        st.success(
                            "Drawing updated."
                        )

                        st.rerun()

                if st.button(
                    "Delete Drawing",
                    key=f"drawing_delete_{prefix}_{drawing_id}",
                    use_container_width=True,
                ):

                    database["drawings"] = [
                        item
                        for item in drawings
                        if item is not drawing
                    ]

                    _save(database)

                    st.success(
                        "Drawing deleted."
                    )

                    st.rerun()

    # ========================================================
    # ARCHITECTURAL
    # ========================================================

    with tab_architectural:

        render_drawing_records(
            architectural,
            "architectural",
        )

    # ========================================================
    # STRUCTURAL
    # ========================================================

    with tab_structural:

        render_drawing_records(
            structural,
            "structural",
        )

    # ========================================================
    # ALL DRAWINGS
    # ========================================================

    with tab_all:

        render_drawing_records(
            drawings,
            "all",
        )

    # ========================================================
    # REGISTER DRAWING
    # ========================================================

    with tab_add:

        with st.form(
            "drawing_register_form",
            clear_on_submit=True,
        ):

            drawing_number = st.text_input(
                "Drawing Number",
                placeholder="Example: A-101",
            )

            title = st.text_input(
                "Drawing Title"
            )

            project = st.text_input(
                "Project"
            )

            category = st.selectbox(
                "Drawing Category",
                DRAWING_CATEGORIES,
            )

            drawing_types = _drawing_types_for_category(
                category
            )

            drawing_type = st.selectbox(
                "Drawing Type",
                drawing_types,
            )

            if category == "Structural":

                discipline_options = [
                    "Structural",
                    "Civil",
                    "Geotechnical",
                    "Other",
                ]

            else:

                discipline_options = [
                    "Architectural",
                    "Other",
                ]

            discipline = st.selectbox(
                "Discipline",
                discipline_options,
            )

            revision = st.text_input(
                "Revision",
                value="A",
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            scale = st.selectbox(
                "Scale",
                SCALES,
                index=SCALES.index(
                    "1:100"
                ),
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

            issue_date = st.text_input(
                "Issue Date",
                placeholder="YYYY-MM-DD",
            )

            notes = st.text_area(
                "Notes"
            )

            submitted = st.form_submit_button(
                "Register Drawing",
                use_container_width=True,
            )

        if submitted:

            cleaned_number = drawing_number.strip()
            cleaned_title = title.strip()

            if not cleaned_number:

                st.error(
                    "Drawing number is required."
                )

            elif not cleaned_title:

                st.error(
                    "Drawing title is required."
                )

            else:

                drawings.append(
                    {
                        "id": _next_id(drawings),
                        "drawing_number": cleaned_number,
                        "title": cleaned_title,
                        "project": project.strip(),
                        "category": category,
                        "discipline": discipline,
                        "drawing_type": drawing_type,
                        "revision": revision.strip() or "A",
                        "status": status,
                        "scale": scale,
                        "prepared_by": prepared_by.strip(),
                        "checked_by": checked_by.strip(),
                        "approved_by": approved_by.strip(),
                        "issue_date": issue_date.strip(),
                        "notes": notes.strip(),
                        "created_at": datetime.now().isoformat(
                            timespec="seconds"
                        ),
                    }
                )

                _save(database)

                st.success(
                    "Drawing registered."
                )

                st.rerun()