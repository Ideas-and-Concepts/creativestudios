"""
Creative Studios
Architecture Module

Architectural project and design management.
"""

from future import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

DESIGN_STAGES = [
"Concept",
"Schematic Design",
"Design Development",
"Construction Documentation",
"Tender Documentation",
"Construction",
"As-Built",
]

STATUSES = [
"Draft",
"In Review",
"Approved",
"Issued",
"Superseded",
]

BUILDING_TYPES = [
"Residential",
"Commercial",
"Office",
"Retail",
"Industrial",
"Institutional",
"Hospitality",
"Mixed Use",
"Infrastructure",
"Other",
]

def _normalize_records(database: dict[str, Any]) -> list[dict[str, Any]]:
"""Normalize architecture records into dictionaries."""

value = database.get("architecture", [])

if not isinstance(value, list):
    value = []

records: list[dict[str, Any]] = []

for index, item in enumerate(value, start=1):
    if isinstance(item, dict):
        record = dict(item)

        if not record.get("id"):
            record["id"] = index

        records.append(record)

    elif isinstance(item, str):
        records.append(
            {
                "id": index,
                "title": item,
                "project": "",
                "building_type": "Other",
                "site_location": "",
                "gross_floor_area": 0.0,
                "floors": 1,
                "stage": "Concept",
                "status": "Draft",
                "lead_architect": "",
                "notes": "",
            }
        )

database["architecture"] = records

return records

def _next_id(records: list[dict[str, Any]]) -> int:
"""Return the next available integer ID."""

ids: list[int] = []

for record in records:
    try:
        ids.append(int(record.get("id", 0)))
    except (TypeError, ValueError):
        continue

return max(ids, default=0) + 1

def _safe_float(value: Any) -> float:
"""Convert a value to float safely."""

try:
    return float(value or 0)
except (TypeError, ValueError):
    return 0.0

def _safe_int(value: Any, default: int = 0) -> int:
"""Convert a value to integer safely."""

try:
    return int(value)
except (TypeError, ValueError):
    return default

def _drawing_count(
database: dict[str, Any],
project: str,
discipline: str = "Architectural",
) -> int:
"""Count drawings belonging to an architectural project."""

drawings = database.get("drawings", [])

if not isinstance(drawings, list):
    return 0

count = 0

for drawing in drawings:
    if not isinstance(drawing, dict):
        continue

    drawing_project = str(
        drawing.get("project", "")
    ).strip()

    drawing_discipline = str(
        drawing.get("discipline", "")
    ).strip()

    if (
        drawing_project.lower() == project.lower()
        and drawing_discipline.lower() == discipline.lower()
    ):
        count += 1

return count

def _render_summary(
database: dict[str, Any],
records: list[dict[str, Any]],
) -> None:
"""Render architecture summary metrics."""

total_area = sum(
    _safe_float(record.get("gross_floor_area", 0))
    for record in records
)

issued = sum(
    1
    for record in records
    if str(record.get("status", "")).lower() == "issued"
)

in_review = sum(
    1
    for record in records
    if str(record.get("status", "")).lower() == "in review"
)

st.subheader("Architecture Overview")

columns = st.columns(5)

columns[0].metric(
    "Design Records",
    len(records),
)

columns[1].metric(
    "In Review",
    in_review,
)

columns[2].metric(
    "Issued",
    issued,
)

columns[3].metric(
    "Gross Floor Area",
    f"{total_area:,.2f}",
)

architectural_drawings = database.get("drawings", [])

if isinstance(architectural_drawings, list):
    drawing_count = sum(
        1
        for drawing in architectural_drawings
        if isinstance(drawing, dict)
        and str(
            drawing.get("discipline", "")
        ).lower()
        == "architectural"
    )
else:
    drawing_count = 0

columns[4].metric(
    "Architectural Drawings",
    drawing_count,
)

def _render_record_editor(
database: dict[str, Any],
records: list[dict[str, Any]],
record: dict[str, Any],
index: int,
) -> None:
"""Render an editable architecture record."""

record_id = record.get("id", index + 1)

title = str(
    record.get("title", "Untitled Design") or ""
)

with st.expander(
    title or "Untitled Design",
    expanded=False,
):
    with st.form(
        f"edit_architecture_{record_id}"
    ):
        col1, col2 = st.columns(2)

        with col1:
            edited_title = st.text_input(
                "Design Item",
                value=title,
            )

            edited_project = st.text_input(
                "Project",
                value=str(
                    record.get("project", "")
                    or ""
                ),
            )

            edited_building_type = st.selectbox(
                "Building Type",
                BUILDING_TYPES,
                index=(
                    BUILDING_TYPES.index(
                        str(
                            record.get(
                                "building_type",
                                "Other",
                            )
                        )
                    )
                    if str(
                        record.get(
                            "building_type",
                            "Other",
                        )
                    )
                    in BUILDING_TYPES
                    else len(BUILDING_TYPES) - 1
                ),
            )

            edited_site = st.text_input(
                "Site / Location",
                value=str(
                    record.get(
                        "site_location",
                        "",
                    )
                    or ""
                ),
            )

            edited_architect = st.text_input(
                "Lead Architect",
                value=str(
                    record.get(
                        "lead_architect",
                        "",
                    )
                    or ""
                ),
            )

        with col2:
            current_stage = str(
                record.get(
                    "stage",
                    "Concept",
                )
            )

            edited_stage = st.selectbox(
                "Design Stage",
                DESIGN_STAGES,
                index=(
                    DESIGN_STAGES.index(
                        current_stage
                    )
                    if current_stage in DESIGN_STAGES
                    else 0
                ),
            )

            current_status = str(
                record.get(
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

            edited_area = st.number_input(
                "Gross Floor Area",
                min_value=0.0,
                value=_safe_float(
                    record.get(
                        "gross_floor_area",
                        0,
                    )
                ),
                step=1.0,
            )

            edited_floors = st.number_input(
                "Number of Floors",
                min_value=1,
                value=max(
                    1,
                    _safe_int(
                        record.get(
                            "floors",
                            1,
                        ),
                        1,
                    ),
                ),
                step=1,
            )

        edited_notes = st.text_area(
            "Design Notes",
            value=str(
                record.get(
                    "notes",
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
        if not edited_title.strip():
            st.error("Design item is required.")
            return

        record["title"] = edited_title.strip()
        record["project"] = edited_project.strip()
        record["building_type"] = edited_building_type
        record["site_location"] = edited_site.strip()
        record["lead_architect"] = edited_architect.strip()
        record["stage"] = edited_stage
        record["status"] = edited_status
        record["gross_floor_area"] = edited_area
        record["floors"] = edited_floors
        record["notes"] = edited_notes.strip()

        save_memory(database)

        st.success(
            "Architecture record updated successfully."
        )

        st.rerun()

    drawing_count = _drawing_count(
        database,
        str(record.get("project", "")),
    )

    st.caption(
        f"Linked architectural drawings: {drawing_count}"
    )

    if st.button(
        "Delete Record",
        key=f"delete_architecture_{record_id}",
        use_container_width=True,
    ):
        records.remove(record)
        save_memory(database)

        st.success(
            "Architecture record deleted successfully."
        )

        st.rerun()

def render_architecture_module(
database: dict[str, Any],
) -> None:
"""Render the architecture workspace."""

st.title("Architecture")

st.caption(
    "Manage architectural projects, building information, design stages and architectural documentation."
)

records = _normalize_records(database)

tab_overview, tab_register, tab_new = st.tabs(
    [
        "Overview",
        "Design Register",
        "New Design",
    ]
)

with tab_overview:
    _render_summary(
        database,
        records,
    )

    st.divider()

    if records:
        st.subheader("Active Design Work")

        for record in records:
            project = str(
                record.get("project", "")
                or "Unassigned"
            )

            stage = str(
                record.get(
                    "stage",
                    "Concept",
                )
            )

            status = str(
                record.get(
                    "status",
                    "Draft",
                )
            )

            st.markdown(
                f"**{record.get('title', 'Untitled')}**  \n"
                f"Project: {project} | "
                f"Stage: {stage} | "
                f"Status: {status}"
            )

    else:
        st.info(
            "No architectural design records have been created yet."
        )

with tab_register:
    if not records:
        st.info(
            "No architecture records have been created yet."
        )
    else:
        for index, record in enumerate(records):
            _render_record_editor(
                database,
                records,
                record,
                index,
            )

with tab_new:
    st.subheader("Create Design Record")

    with st.form(
        "architecture_register_form",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Design Item"
            )

            project = st.text_input(
                "Project"
            )

            building_type = st.selectbox(
                "Building Type",
                BUILDING_TYPES,
            )

            site_location = st.text_input(
                "Site / Location"
            )

            lead_architect = st.text_input(
                "Lead Architect"
            )

        with col2:
            stage = st.selectbox(
                "Design Stage",
                DESIGN_STAGES,
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            gross_floor_area = st.number_input(
                "Gross Floor Area",
                min_value=0.0,
                step=1.0,
            )

            floors = st.number_input(
                "Number of Floors",
                min_value=1,
                value=1,
                step=1,
            )

        notes = st.text_area(
            "Design Notes"
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

        records.append(
            {
                "id": _next_id(records),
                "title": title.strip(),
                "project": project.strip(),
                "building_type": building_type,
                "site_location": site_location.strip(),
                "lead_architect": lead_architect.strip(),
                "gross_floor_area": gross_floor_area,
                "floors": floors,
                "stage": stage,
                "status": status,
                "notes": notes.strip(),
            }
        )

        save_memory(database)

        st.success(
            "Architecture record added successfully."
        )

        st.rerun()