"""
Creative Studios
Engineering Module

Engineering project and technical design management.
"""

from future import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory

DISCIPLINES = [
"Structural",
"Civil",
"Geotechnical",
"Infrastructure",
"Transportation",
"Environmental",
"Mechanical",
"Electrical",
"Plumbing",
"Other",
]

DESIGN_STAGES = [
"Concept",
"Preliminary Design",
"Detailed Design",
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

STRUCTURAL_SYSTEMS = [
"Reinforced Concrete Frame",
"Steel Frame",
"Load Bearing Masonry",
"Timber Frame",
"Composite Structure",
"Precast Concrete",
"Other",
]

def _normalize_records(database: dict[str, Any]) -> list[dict[str, Any]]:
"""Normalize engineering records."""

value = database.get("engineering", [])

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
                "discipline": "Other",
                "design_stage": "Concept",
                "status": "Draft",
                "structural_system": "",
                "lead_engineer": "",
                "notes": "",
            }
        )

database["engineering"] = records

return records

def _next_id(records: list[dict[str, Any]]) -> int:
"""Return the next available ID."""

ids: list[int] = []

for record in records:
    try:
        ids.append(int(record.get("id", 0)))
    except (TypeError, ValueError):
        continue

return max(ids, default=0) + 1

def _structural_drawing_count(
database: dict[str, Any],
project: str,
) -> int:
"""Count structural drawings for a project."""

drawings = database.get("drawings", [])

if not isinstance(drawings, list):
    return 0

return sum(
    1
    for drawing in drawings
    if isinstance(drawing, dict)
    and str(
        drawing.get("project", "")
    ).strip().lower()
    == project.strip().lower()
    and str(
        drawing.get("discipline", "")
    ).strip().lower()
    == "structural"
)

def _render_summary(
database: dict[str, Any],
records: list[dict[str, Any]],
) -> None:
"""Render engineering summary."""

structural = sum(
    1
    for record in records
    if str(
        record.get("discipline", "")
    ).lower()
    == "structural"
)

civil = sum(
    1
    for record in records
    if str(
        record.get("discipline", "")
    ).lower()
    == "civil"
)

in_review = sum(
    1
    for record in records
    if str(
        record.get("status", "")
    ).lower()
    == "in review"
)

drawings = database.get("drawings", [])

structural_drawings = (
    sum(
        1
        for drawing in drawings
        if isinstance(drawing, dict)
        and str(
            drawing.get(
                "discipline",
                "",
            )
        ).lower()
        == "structural"
    )
    if isinstance(drawings, list)
    else 0
)

columns = st.columns(5)

columns[0].metric(
    "Engineering Records",
    len(records),
)

columns[1].metric(
    "Structural",
    structural,
)

columns[2].metric(
    "Civil",
    civil,
)

columns[3].metric(
    "In Review",
    in_review,
)

columns[4].metric(
    "Structural Drawings",
    structural_drawings,
)

def _render_record_editor(
database: dict[str, Any],
records: list[dict[str, Any]],
record: dict[str, Any],
index: int,
) -> None:
"""Render an editable engineering record."""

record_id = record.get(
    "id",
    index + 1,
)

title = str(
    record.get(
        "title",
        "Engineering Work Item",
    )
    or ""
)

with st.expander(
    title or "Engineering Work Item",
    expanded=False,
):
    with st.form(
        f"edit_engineering_{record_id}"
    ):
        col1, col2 = st.columns(2)

        with col1:
            edited_title = st.text_input(
                "Engineering Work Item",
                value=title,
            )

            edited_project = st.text_input(
                "Project",
                value=str(
                    record.get(
                        "project",
                        "",
                    )
                    or ""
                ),
            )

            current_discipline = str(
                record.get(
                    "discipline",
                    "Other",
                )
            )

            edited_discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
                index=(
                    DISCIPLINES.index(
                        current_discipline
                    )
                    if current_discipline in DISCIPLINES
                    else len(DISCIPLINES) - 1
                ),
            )

            edited_engineer = st.text_input(
                "Lead Engineer",
                value=str(
                    record.get(
                        "lead_engineer",
                        "",
                    )
                    or ""
                ),
            )

        with col2:
            current_stage = str(
                record.get(
                    "design_stage",
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

            current_system = str(
                record.get(
                    "structural_system",
                    "",
                )
                or ""
            )

            system_options = ["Not Applicable"] + STRUCTURAL_SYSTEMS

            edited_system = st.selectbox(
                "Structural System",
                system_options,
                index=(
                    system_options.index(
                        current_system
                    )
                    if current_system in system_options
                    else 0
                ),
            )

        edited_notes = st.text_area(
            "Technical Notes",
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
            st.error(
                "Engineering work item is required."
            )
            return

        record["title"] = edited_title.strip()
        record["project"] = edited_project.strip()
        record["discipline"] = edited_discipline
        record["lead_engineer"] = edited_engineer.strip()
        record["design_stage"] = edited_stage
        record["status"] = edited_status
        record["structural_system"] = (
            ""
            if edited_system == "Not Applicable"
            else edited_system
        )
        record["notes"] = edited_notes.strip()

        save_memory(database)

        st.success(
            "Engineering record updated successfully."
        )

        st.rerun()

    drawing_count = _structural_drawing_count(
        database,
        str(
            record.get(
                "project",
                "",
            )
        ),
    )

    if str(
        record.get(
            "discipline",
            "",
        )
    ).lower() == "structural":
        st.caption(
            f"Linked structural drawings: {drawing_count}"
        )

    if st.button(
        "Delete Record",
        key=f"delete_engineering_{record_id}",
        use_container_width=True,
    ):
        records.remove(record)

        save_memory(database)

        st.success(
            "Engineering record deleted successfully."
        )

        st.rerun()

def render_engineering_module(
database: dict[str, Any],
) -> None:
"""Render the engineering workspace."""

st.title("Engineering")

st.caption(
    "Manage engineering disciplines, technical design records and structural coordination."
)

records = _normalize_records(database)

tab_overview, tab_register, tab_new = st.tabs(
    [
        "Overview",
        "Engineering Register",
        "New Engineering Record",
    ]
)

with tab_overview:
    _render_summary(
        database,
        records,
    )

    st.divider()

    if records:
        st.subheader("Engineering Work")

        for record in records:
            st.markdown(
                f"**{record.get('title', 'Untitled')}**  \n"
                f"Project: "
                f"{record.get('project', '') or 'Unassigned'} | "
                f"Discipline: "
                f"{record.get('discipline', 'Other')} | "
                f"Stage: "
                f"{record.get('design_stage', 'Concept')} | "
                f"Status: "
                f"{record.get('status', 'Draft')}"
            )
    else:
        st.info(
            "No engineering records have been created yet."
        )

with tab_register:
    if not records:
        st.info(
            "No engineering records have been created yet."
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
    st.subheader(
        "Create Engineering Record"
    )

    with st.form(
        "engineering_record_form",
        clear_on_submit=True,
    ):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Engineering Work Item"
            )

            project = st.text_input(
                "Project"
            )

            discipline = st.selectbox(
                "Discipline",
                DISCIPLINES,
            )

            lead_engineer = st.text_input(
                "Lead Engineer"
            )

        with col2:
            design_stage = st.selectbox(
                "Design Stage",
                DESIGN_STAGES,
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            structural_system = st.selectbox(
                "Structural System",
                ["Not Applicable"] + STRUCTURAL_SYSTEMS,
            )

        notes = st.text_area(
            "Technical Notes"
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
                "id": _next_id(records),
                "title": title.strip(),
                "project": project.strip(),
                "discipline": discipline,
                "design_stage": design_stage,
                "status": status,
                "structural_system": (
                    ""
                    if structural_system == "Not Applicable"
                    else structural_system
                ),
                "lead_engineer": lead_engineer.strip(),
                "notes": notes.strip(),
            }
        )

        save_memory(database)

        st.success(
            "Engineering record added successfully."
        )

        st.rerun()