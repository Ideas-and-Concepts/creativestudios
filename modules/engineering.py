"""
Creative Studios
Engineering Module

Construction-focused engineering works management.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from modules.database import save_memory


# ============================================================
# CONSTANTS
# ============================================================

DISCIPLINES = [
    "Structural",
    "Civil",
    "Geotechnical",
    "Mechanical",
    "Electrical",
    "Plumbing",
    "Infrastructure",
    "Transportation",
    "Environmental",
    "Other",
]

WORK_TYPES = [
    "Design",
    "Foundation Works",
    "Structural Frame",
    "Reinforcement",
    "Concrete Works",
    "Earthworks",
    "Drainage",
    "Road Works",
    "External Works",
    "Mechanical Installation",
    "Electrical Installation",
    "Plumbing Installation",
    "Inspection",
    "Testing and Commissioning",
    "Technical Review",
    "Site Engineering",
    "As-Built Documentation",
    "Other",
]

STAGES = [
    "Design",
    "Tender",
    "Construction",
    "Testing and Commissioning",
    "As-Built",
]

STATUSES = [
    "Not Started",
    "In Progress",
    "Submitted",
    "Under Review",
    "Approved",
    "Issued for Construction",
    "Completed",
    "On Hold",
]

PRIORITIES = [
    "Low",
    "Normal",
    "High",
    "Critical",
]

APPROVAL_STATUSES = [
    "Not Required",
    "Pending",
    "Under Review",
    "Approved",
    "Rejected",
]


# ============================================================
# HELPERS
# ============================================================

def _text(value: Any, default: str = "") -> str:
    """Convert a value safely to text."""

    if value is None:
        return default

    return str(value).strip()


def _normalize_records(
    database: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize engineering construction records."""

    value = database.get("engineering", [])

    if not isinstance(value, list):
        value = []

    records: list[dict[str, Any]] = []

    for index, item in enumerate(value, start=1):

        if isinstance(item, dict):

            record = dict(item)

            if not record.get("id"):
                record["id"] = index

            record.setdefault("title", "")
            record.setdefault("project", "")
            record.setdefault("discipline", "Other")
            record.setdefault("work_type", "Other")
            record.setdefault("stage", "Construction")
            record.setdefault("status", "Not Started")
            record.setdefault("priority", "Normal")
            record.setdefault("drawing_number", "")
            record.setdefault("revision", "")
            record.setdefault("responsible", "")
            record.setdefault("contractor", "")
            record.setdefault("start_date", "")
            record.setdefault("target_date", "")
            record.setdefault("completion_date", "")
            record.setdefault("rfi_reference", "")
            record.setdefault("approval_status", "Not Required")
            record.setdefault("notes", "")

            records.append(record)

        elif isinstance(item, str):

            records.append(
                {
                    "id": index,
                    "title": item,
                    "project": "",
                    "discipline": "Other",
                    "work_type": "Other",
                    "stage": "Construction",
                    "status": "Not Started",
                    "priority": "Normal",
                    "drawing_number": "",
                    "revision": "",
                    "responsible": "",
                    "contractor": "",
                    "start_date": "",
                    "target_date": "",
                    "completion_date": "",
                    "rfi_reference": "",
                    "approval_status": "Not Required",
                    "notes": "",
                }
            )

    database["engineering"] = records

    return records


def _next_id(
    records: list[dict[str, Any]],
) -> int:
    """Return the next available engineering ID."""

    highest = 0

    for record in records:

        if not isinstance(record, dict):
            continue

        try:
            value = int(record.get("id", 0))
        except (TypeError, ValueError):
            continue

        highest = max(highest, value)

    return highest + 1


def _save(
    database: dict[str, Any],
) -> None:
    """Persist database changes."""

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

    return min(default, len(values) - 1)


# ============================================================
# MAIN MODULE
# ============================================================

def render_engineering_module(
    database: dict[str, Any],
) -> None:
    """Render the construction-focused Engineering module."""

    st.title("Engineering")

    st.caption(
        "Manage structural, civil, MEP and other engineering "
        "works throughout construction."
    )

    records = _normalize_records(database)

    # ========================================================
    # METRICS
    # ========================================================

    total = len(records)

    structural = sum(
        1
        for record in records
        if _text(record.get("discipline")).lower()
        == "structural"
    )

    civil = sum(
        1
        for record in records
        if _text(record.get("discipline")).lower()
        == "civil"
    )

    completed = sum(
        1
        for record in records
        if _text(record.get("status")).lower()
        == "completed"
    )

    columns = st.columns(4)

    columns[0].metric(
        "Engineering Works",
        total,
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
        "Completed",
        completed,
    )

    st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_add, tab_summary = st.tabs(
        [
            "Work Register",
            "Add Work",
            "Engineering Summary",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        if not records:

            st.info(
                "No engineering construction works have been registered."
            )

        else:

            search = st.text_input(
                "Search engineering works",
                placeholder="Search by title, project, discipline, drawing or engineer",
                key="engineering_search",
            )

            search_term = search.strip().lower()

            filtered_records = []

            for record in records:

                searchable = " ".join(
                    [
                        _text(record.get("title")),
                        _text(record.get("project")),
                        _text(record.get("discipline")),
                        _text(record.get("work_type")),
                        _text(record.get("drawing_number")),
                        _text(record.get("responsible")),
                        _text(record.get("contractor")),
                    ]
                ).lower()

                if not search_term or search_term in searchable:
                    filtered_records.append(record)

            if not filtered_records:

                st.info(
                    "No engineering works match the search."
                )

            for index, record in enumerate(filtered_records):

                record_id = record.get(
                    "id",
                    index + 1,
                )

                title = (
                    _text(
                        record.get("title"),
                        "Untitled Engineering Work",
                    )
                    or "Untitled Engineering Work"
                )

                project = _text(
                    record.get("project")
                )

                discipline = _text(
                    record.get(
                        "discipline",
                        "Other",
                    )
                )

                heading = title

                if project:
                    heading = f"{title} — {project}"

                with st.expander(
                    heading,
                    expanded=False,
                ):

                    st.caption(
                        f"Discipline: {discipline}"
                    )

                    with st.form(
                        f"engineering_edit_{record_id}"
                    ):

                        edited_title = st.text_input(
                            "Engineering Work Item",
                            value=title,
                        )

                        edited_project = st.text_input(
                            "Project",
                            value=_text(
                                record.get("project")
                            ),
                        )

                        edited_discipline = st.selectbox(
                            "Engineering Discipline",
                            DISCIPLINES,
                            index=_select_index(
                                DISCIPLINES,
                                record.get("discipline"),
                                len(DISCIPLINES) - 1,
                            ),
                        )

                        edited_work_type = st.selectbox(
                            "Work Type",
                            WORK_TYPES,
                            index=_select_index(
                                WORK_TYPES,
                                record.get("work_type"),
                                len(WORK_TYPES) - 1,
                            ),
                        )

                        edited_stage = st.selectbox(
                            "Construction Stage",
                            STAGES,
                            index=_select_index(
                                STAGES,
                                record.get("stage"),
                                STAGES.index("Construction"),
                            ),
                        )

                        edited_status = st.selectbox(
                            "Status",
                            STATUSES,
                            index=_select_index(
                                STATUSES,
                                record.get("status"),
                            ),
                        )

                        edited_priority = st.selectbox(
                            "Priority",
                            PRIORITIES,
                            index=_select_index(
                                PRIORITIES,
                                record.get("priority"),
                            ),
                        )

                        edited_drawing = st.text_input(
                            "Drawing / Reference Number",
                            value=_text(
                                record.get("drawing_number")
                            ),
                        )

                        edited_revision = st.text_input(
                            "Revision",
                            value=_text(
                                record.get("revision")
                            ),
                        )

                        edited_responsible = st.text_input(
                            "Responsible Engineer",
                            value=_text(
                                record.get("responsible")
                            ),
                        )

                        edited_contractor = st.text_input(
                            "Contractor",
                            value=_text(
                                record.get("contractor")
                            ),
                        )

                        date_columns = st.columns(3)

                        with date_columns[0]:
                            edited_start = st.text_input(
                                "Start Date",
                                value=_text(
                                    record.get("start_date")
                                ),
                                placeholder="YYYY-MM-DD",
                            )

                        with date_columns[1]:
                            edited_target = st.text_input(
                                "Target Date",
                                value=_text(
                                    record.get("target_date")
                                ),
                                placeholder="YYYY-MM-DD",
                            )

                        with date_columns[2]:
                            edited_completion = st.text_input(
                                "Completion Date",
                                value=_text(
                                    record.get("completion_date")
                                ),
                                placeholder="YYYY-MM-DD",
                            )

                        edited_rfi = st.text_input(
                            "RFI Reference",
                            value=_text(
                                record.get("rfi_reference")
                            ),
                        )

                        edited_approval = st.selectbox(
                            "Approval Status",
                            APPROVAL_STATUSES,
                            index=_select_index(
                                APPROVAL_STATUSES,
                                record.get("approval_status"),
                            ),
                        )

                        edited_notes = st.text_area(
                            "Technical Notes",
                            value=_text(
                                record.get("notes")
                            ),
                        )

                        save_clicked = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True,
                        )

                    if save_clicked:

                        cleaned_title = edited_title.strip()

                        if not cleaned_title:

                            st.error(
                                "Engineering work item is required."
                            )

                        else:

                            record["title"] = cleaned_title
                            record["project"] = edited_project.strip()
                            record["discipline"] = edited_discipline
                            record["work_type"] = edited_work_type
                            record["stage"] = edited_stage
                            record["status"] = edited_status
                            record["priority"] = edited_priority
                            record["drawing_number"] = edited_drawing.strip()
                            record["revision"] = edited_revision.strip()
                            record["responsible"] = edited_responsible.strip()
                            record["contractor"] = edited_contractor.strip()
                            record["start_date"] = edited_start.strip()
                            record["target_date"] = edited_target.strip()
                            record["completion_date"] = edited_completion.strip()
                            record["rfi_reference"] = edited_rfi.strip()
                            record["approval_status"] = edited_approval
                            record["notes"] = edited_notes.strip()

                            _save(database)

                            st.success(
                                "Engineering work updated."
                            )

                            st.rerun()

                    if st.button(
                        "Delete Work",
                        key=f"engineering_delete_{record_id}",
                        use_container_width=True,
                    ):

                        database["engineering"] = [
                            item
                            for item in records
                            if item is not record
                        ]

                        _save(database)

                        st.success(
                            "Engineering work deleted."
                        )

                        st.rerun()

    # ========================================================
    # ADD
    # ========================================================

    with tab_add:

        with st.form(
            "engineering_add_form",
            clear_on_submit=True,
        ):

            title = st.text_input(
                "Engineering Work Item"
            )

            project = st.text_input(
                "Project"
            )

            discipline = st.selectbox(
                "Engineering Discipline",
                DISCIPLINES,
            )

            work_type = st.selectbox(
                "Work Type",
                WORK_TYPES,
            )

            stage = st.selectbox(
                "Construction Stage",
                STAGES,
                index=STAGES.index(
                    "Construction"
                ),
            )

            status = st.selectbox(
                "Status",
                STATUSES,
            )

            priority = st.selectbox(
                "Priority",
                PRIORITIES,
                index=1,
            )

            drawing_number = st.text_input(
                "Drawing / Reference Number"
            )

            revision = st.text_input(
                "Revision"
            )

            responsible = st.text_input(
                "Responsible Engineer"
            )

            contractor = st.text_input(
                "Contractor"
            )

            start_date = st.text_input(
                "Start Date",
                placeholder="YYYY-MM-DD",
            )

            target_date = st.text_input(
                "Target Date",
                placeholder="YYYY-MM-DD",
            )

            rfi_reference = st.text_input(
                "RFI Reference"
            )

            approval_status = st.selectbox(
                "Approval Status",
                APPROVAL_STATUSES,
            )

            notes = st.text_area(
                "Technical Notes"
            )

            submitted = st.form_submit_button(
                "Add Engineering Work",
                use_container_width=True,
            )

        if submitted:

            cleaned_title = title.strip()

            if not cleaned_title:

                st.error(
                    "Engineering work item is required."
                )

            else:

                records.append(
                    {
                        "id": _next_id(records),
                        "title": cleaned_title,
                        "project": project.strip(),
                        "discipline": discipline,
                        "work_type": work_type,
                        "stage": stage,
                        "status": status,
                        "priority": priority,
                        "drawing_number": drawing_number.strip(),
                        "revision": revision.strip(),
                        "responsible": responsible.strip(),
                        "contractor": contractor.strip(),
                        "start_date": start_date.strip(),
                        "target_date": target_date.strip(),
                        "completion_date": "",
                        "rfi_reference": rfi_reference.strip(),
                        "approval_status": approval_status,
                        "notes": notes.strip(),
                    }
                )

                _save(database)

                st.success(
                    "Engineering work added."
                )

                st.rerun()

    # ========================================================
    # SUMMARY
    # ========================================================

    with tab_summary:

        if not records:

            st.info(
                "No engineering construction data is available."
            )

        else:

            st.subheader(
                "Works by Discipline"
            )

            discipline_counts: dict[str, int] = {}

            for record in records:

                discipline = _text(
                    record.get(
                        "discipline",
                        "Other",
                    )
                ) or "Other"

                discipline_counts[discipline] = (
                    discipline_counts.get(
                        discipline,
                        0,
                    )
                    + 1
                )

            for discipline, count in sorted(
                discipline_counts.items()
            ):

                st.write(
                    f"{discipline}: {count}"
                )

            st.subheader(
                "Works by Status"
            )

            status_counts: dict[str, int] = {}

            for record in records:

                status = _text(
                    record.get(
                        "status",
                        "Not Started",
                    )
                ) or "Not Started"

                status_counts[status] = (
                    status_counts.get(
                        status,
                        0,
                    )
                    + 1
                )

            for status, count in sorted(
                status_counts.items()
            ):

                st.write(
                    f"{status}: {count}"
                )