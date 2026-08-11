"""
Creative Studios
Daily Site Logs Module

AEC construction site reporting and daily progress control.

Workflow:

Project
    ↓
Daily Site Log
    ├── Site Conditions
    ├── Workforce
    ├── Equipment
    ├── Materials
    ├── Activities
    ├── Progress
    ├── Issues / Delays
    ├── Safety
    ├── Site Instructions
    └── Daily Summary
"""

from datetime import date

import streamlit as st

from .database import (
    add_record,
    delete_record,
    get_collection,
    update_record,
)


# ============================================================
# CONSTANTS
# ============================================================

LOG_STATUSES = [
    "Draft",
    "Submitted",
    "Reviewed",
    "Approved",
    "Rejected",
]

WEATHER_OPTIONS = [
    "Sunny / Clear",
    "Partly Cloudy",
    "Cloudy",
    "Rainy / Wet",
    "Heavy Rain",
    "Windy / Stormy",
    "Extreme Heat",
    "Other",
]

WORKING_CONDITIONS = [
    "Normal",
    "Wet Site",
    "Restricted Access",
    "Poor Visibility",
    "High Wind",
    "Extreme Heat",
    "Other",
]

ISSUE_CATEGORIES = [
    "Design",
    "Materials",
    "Labour",
    "Equipment",
    "Weather",
    "Client",
    "Consultant",
    "Contractor",
    "Subcontractor",
    "Access",
    "Safety",
    "Utilities",
    "Other",
]

UNITS = [
    "No.",
    "m",
    "m²",
    "m³",
    "kg",
    "ton",
    "bags",
    "L",
    "sets",
    "hours",
    "days",
    "item",
]


# ============================================================
# DATABASE HELPERS
# ============================================================

def _projects(db):
    return get_collection(
        db,
        "projects",
    )


def _logs(db):
    return get_collection(
        db,
        "site_logs",
    )


def _activities(db):
    return get_collection(
        db,
        "site_log_activities",
    )


def _materials(db):
    return get_collection(
        db,
        "site_log_materials",
    )


def _equipment(db):
    return get_collection(
        db,
        "site_log_equipment",
    )


def _issues(db):
    return get_collection(
        db,
        "site_log_issues",
    )


def _workforce(db):
    return get_collection(
        db,
        "site_log_workforce",
    )


def _instructions(db):
    return get_collection(
        db,
        "site_log_instructions",
    )


def _project_name(
    db,
    project_id,
):

    for project in _projects(db):

        if str(
            project.get("id")
        ) == str(project_id):

            return project.get(
                "name",
                project_id,
            )

    return project_id


def _current_user():

    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):

        return user.get(
            "name",
            user.get(
                "username",
                "System",
            ),
        )

    return str(
        user or "System"
    )


def _next_log_number(db):

    highest = 0

    for log in _logs(db):

        log_id = str(
            log.get(
                "id",
                "",
            )
        )

        if not log_id.startswith(
            "DSL-"
        ):

            continue

        try:

            number = int(
                log_id.split("-")[-1]
            )

            highest = max(
                highest,
                number,
            )

        except (
            ValueError,
            IndexError,
        ):

            continue

    return f"DSL-{highest + 1:05d}"


def _log_records(
    collection,
    log_id,
):

    return [
        record
        for record in collection
        if str(
            record.get("log_id")
        ) == str(log_id)
    ]


def _status_badge(status):

    if status == "Approved":

        st.success(
            status,
            icon="✓",
        )

    elif status == "Submitted":

        st.info(
            status,
        )

    elif status == "Reviewed":

        st.info(
            status,
        )

    elif status == "Rejected":

        st.error(
            status,
            icon="!",
        )

    else:

        st.warning(
            status,
        )


# ============================================================
# CREATE DAILY LOG
# ============================================================

def _render_create_log(db):

    projects = _projects(db)

    st.subheader(
        "Create Daily Site Log"
    )

    if not projects:

        st.warning(
            "Create a project before creating a site log."
        )

        return

    project_options = {
        _project_name(
            db,
            project.get("id"),
        ):
            project.get("id")
        for project in projects
    }

    with st.form(
        "create_daily_site_log"
    ):

        project_label = st.selectbox(
            "Project *",
            list(
                project_options.keys()
            ),
        )

        project_id = project_options[
            project_label
        ]

        log_date = st.date_input(
            "Log Date *",
            value=date.today(),
        )

        col1, col2 = st.columns(2)

        with col1:

            weather = st.selectbox(
                "Weather",
                WEATHER_OPTIONS,
            )

        with col2:

            working_condition = st.selectbox(
                "Working Conditions",
                WORKING_CONDITIONS,
            )

        site_access = st.text_input(
            "Site Access / General Condition",
            placeholder=(
                "e.g. Normal access, delivery gate operational"
            ),
        )

        col1, col2 = st.columns(2)

        with col1:

            overall_progress = st.number_input(
                "Overall Project Progress (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
            )

        with col2:

            workforce_total = st.number_input(
                "Total Workforce on Site",
                min_value=0,
                value=0,
                step=1,
            )

        activities_summary = st.text_area(
            "Major Activities Completed Today *",
            height=140,
            placeholder=(
                "Describe the major construction activities "
                "and milestones completed today."
            ),
        )

        achievements = st.text_area(
            "Key Achievements",
            height=100,
        )

        issues_summary = st.text_area(
            "Major Issues / Delays",
            height=100,
        )

        safety_summary = st.text_area(
            "Safety Summary",
            height=100,
            placeholder=(
                "Incidents, near misses, toolbox talks, "
                "PPE observations, etc."
            ),
        )

        tomorrow_plan = st.text_area(
            "Planned Activities for Tomorrow",
            height=120,
        )

        remarks = st.text_area(
            "General Remarks",
            height=100,
        )

        submitted = st.form_submit_button(
            "Create Daily Site Log",
            use_container_width=True,
        )

    if not submitted:

        return

    activities_summary = (
        activities_summary.strip()
    )

    if not activities_summary:

        st.error(
            "Major activities are required."
        )

        return

    log_id = _next_log_number(db)

    record = {

        "id": log_id,

        "project_id": project_id,

        "log_date": str(
            log_date
        ),

        "status": "Draft",

        "weather": weather,

        "working_condition": (
            working_condition
        ),

        "site_access": (
            site_access.strip()
        ),

        "overall_progress": float(
            overall_progress
        ),

        "workforce_total": int(
            workforce_total
        ),

        "activities_summary": (
            activities_summary
        ),

        "achievements": (
            achievements.strip()
        ),

        "issues_summary": (
            issues_summary.strip()
        ),

        "safety_summary": (
            safety_summary.strip()
        ),

        "tomorrow_plan": (
            tomorrow_plan.strip()
        ),

        "remarks": (
            remarks.strip()
        ),

        "prepared_by": _current_user(),

        "created_at": str(
            date.today()
        ),

        "submitted_at": "",

        "reviewed_by": "",

        "approved_by": "",

    }

    add_record(
        db,
        "site_logs",
        record,
    )

    st.success(
        f"{log_id} created successfully."
    )

    st.session_state[
        "open_site_log_id"
    ] = log_id

    st.rerun()


# ============================================================
# ADD WORKFORCE
# ============================================================

def _render_workforce_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Workforce"
    )

    with st.form(
        f"workforce_{log_id}"
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            category = st.text_input(
                "Worker Category *",
                placeholder=(
                    "Masons, Carpenters, Engineers..."
                ),
            )

        with col2:

            planned = st.number_input(
                "Planned",
                min_value=0,
                value=0,
                step=1,
            )

        with col3:

            actual = st.number_input(
                "Actual",
                min_value=0,
                value=0,
                step=1,
            )

        notes = st.text_input(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Workforce",
            use_container_width=True,
        )

    if not submitted:

        return

    if not category.strip():

        st.error(
            "Worker category is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-WF-"
            f"{len(_log_records(_workforce(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "category": category.strip(),

        "planned": int(
            planned
        ),

        "actual": int(
            actual
        ),

        "notes": notes.strip(),

    }

    add_record(
        db,
        "site_log_workforce",
        record,
    )

    st.success(
        "Workforce entry added."
    )

    st.rerun()


# ============================================================
# ADD EQUIPMENT
# ============================================================

def _render_equipment_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Equipment & Plant"
    )

    with st.form(
        f"equipment_{log_id}"
    ):

        col1, col2 = st.columns(2)

        with col1:

            equipment = st.text_input(
                "Equipment *",
                placeholder=(
                    "Excavator, Crane, Mixer..."
                ),
            )

            quantity = st.number_input(
                "Quantity",
                min_value=0,
                value=1,
                step=1,
            )

        with col2:

            hours = st.number_input(
                "Operating Hours",
                min_value=0.0,
                value=0.0,
                step=0.5,
            )

            idle_hours = st.number_input(
                "Idle / Breakdown Hours",
                min_value=0.0,
                value=0.0,
                step=0.5,
            )

        notes = st.text_input(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Equipment",
            use_container_width=True,
        )

    if not submitted:

        return

    if not equipment.strip():

        st.error(
            "Equipment name is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-EQ-"
            f"{len(_log_records(_equipment(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "equipment": equipment.strip(),

        "quantity": int(
            quantity
        ),

        "operating_hours": float(
            hours
        ),

        "idle_hours": float(
            idle_hours
        ),

        "notes": notes.strip(),

    }

    add_record(
        db,
        "site_log_equipment",
        record,
    )

    st.success(
        "Equipment entry added."
    )

    st.rerun()


# ============================================================
# ADD MATERIAL
# ============================================================

def _render_material_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Materials"
    )

    with st.form(
        f"materials_{log_id}"
    ):

        material = st.text_input(
            "Material *",
            placeholder=(
                "Cement, Sand, Aggregate, Steel..."
            ),
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            unit = st.selectbox(
                "Unit",
                UNITS,
            )

        with col2:

            received = st.number_input(
                "Quantity Received",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        with col3:

            used = st.number_input(
                "Quantity Used",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        remarks = st.text_input(
            "Remarks"
        )

        submitted = st.form_submit_button(
            "Add Material",
            use_container_width=True,
        )

    if not submitted:

        return

    if not material.strip():

        st.error(
            "Material name is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-MAT-"
            f"{len(_log_records(_materials(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "material": material.strip(),

        "unit": unit,

        "quantity_received": float(
            received
        ),

        "quantity_used": float(
            used
        ),

        "remarks": remarks.strip(),

    }

    add_record(
        db,
        "site_log_materials",
        record,
    )

    st.success(
        "Material entry added."
    )

    st.rerun()


# ============================================================
# ADD ACTIVITY
# ============================================================

def _render_activity_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Construction Activities"
    )

    with st.form(
        f"activity_{log_id}"
    ):

        description = st.text_input(
            "Activity *",
            placeholder=(
                "Blockwork to ground floor..."
            ),
        )

        location = st.text_input(
            "Location",
            placeholder=(
                "Block A / Grid A1-A8"
            ),
        )

        boq_reference = st.text_input(
            "BOQ Reference",
            placeholder=(
                "05.02.003"
            ),
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            planned_quantity = st.number_input(
                "Planned Quantity",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        with col2:

            today_quantity = st.number_input(
                "Today's Quantity",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        with col3:

            cumulative_quantity = st.number_input(
                "Cumulative Quantity",
                min_value=0.0,
                value=0.0,
                step=0.01,
            )

        unit = st.selectbox(
            "Unit",
            UNITS,
        )

        progress = st.number_input(
            "Activity Progress (%)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

        notes = st.text_area(
            "Notes",
            height=80,
        )

        submitted = st.form_submit_button(
            "Add Activity",
            use_container_width=True,
        )

    if not submitted:

        return

    if not description.strip():

        st.error(
            "Activity description is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-ACT-"
            f"{len(_log_records(_activities(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "description": (
            description.strip()
        ),

        "location": location.strip(),

        "boq_reference": (
            boq_reference.strip()
        ),

        "unit": unit,

        "planned_quantity": float(
            planned_quantity
        ),

        "today_quantity": float(
            today_quantity
        ),

        "cumulative_quantity": float(
            cumulative_quantity
        ),

        "progress": float(
            progress
        ),

        "notes": notes.strip(),

    }

    add_record(
        db,
        "site_log_activities",
        record,
    )

    st.success(
        "Activity added."
    )

    st.rerun()


# ============================================================
# ADD ISSUE
# ============================================================

def _render_issue_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Issues & Delays"
    )

    with st.form(
        f"issue_{log_id}"
    ):

        issue = st.text_input(
            "Issue *",
            placeholder=(
                "Drawing clarification required..."
            ),
        )

        category = st.selectbox(
            "Category",
            ISSUE_CATEGORIES,
        )

        impact = st.text_area(
            "Impact",
            height=80,
        )

        duration = st.number_input(
            "Delay / Impact Hours",
            min_value=0.0,
            value=0.0,
            step=0.5,
        )

        related_rfi = st.text_input(
            "Related RFI",
            placeholder=(
                "RFI-PRJ-0001"
            ),
        )

        responsible_party = st.text_input(
            "Responsible Party"
        )

        submitted = st.form_submit_button(
            "Add Issue",
            use_container_width=True,
        )

    if not submitted:

        return

    if not issue.strip():

        st.error(
            "Issue description is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-ISS-"
            f"{len(_log_records(_issues(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "issue": issue.strip(),

        "category": category,

        "impact": impact.strip(),

        "duration_hours": float(
            duration
        ),

        "related_rfi": (
            related_rfi.strip()
        ),

        "responsible_party": (
            responsible_party.strip()
        ),

    }

    add_record(
        db,
        "site_log_issues",
        record,
    )

    st.success(
        "Issue added."
    )

    st.rerun()


# ============================================================
# ADD SITE INSTRUCTION
# ============================================================

def _render_instruction_form(
    db,
    log,
):

    log_id = log.get("id")

    st.subheader(
        "Site Instructions"
    )

    with st.form(
        f"instruction_{log_id}"
    ):

        instruction = st.text_area(
            "Instruction *",
            height=100,
        )

        issued_by = st.text_input(
            "Issued By"
        )

        responsible_party = st.text_input(
            "Responsible Party"
        )

        related_rfi = st.text_input(
            "Related RFI"
        )

        submitted = st.form_submit_button(
            "Add Instruction",
            use_container_width=True,
        )

    if not submitted:

        return

    if not instruction.strip():

        st.error(
            "Instruction is required."
        )

        return

    record = {

        "id": (
            f"{log_id}-SI-"
            f"{len(_log_records(_instructions(db), log_id)) + 1:03d}"
        ),

        "log_id": log_id,

        "instruction": (
            instruction.strip()
        ),

        "issued_by": (
            issued_by.strip()
        ),

        "responsible_party": (
            responsible_party.strip()
        ),

        "related_rfi": (
            related_rfi.strip()
        ),

    }

    add_record(
        db,
        "site_log_instructions",
        record,
    )

    st.success(
        "Site instruction added."
    )

    st.rerun()


# ============================================================
# DISPLAY COLLECTION
# ============================================================

def _render_records(
    db,
    log,
):

    log_id = log.get("id")

    workforce = _log_records(
        _workforce(db),
        log_id,
    )

    equipment = _log_records(
        _equipment(db),
        log_id,
    )

    materials = _log_records(
        _materials(db),
        log_id,
    )

    activities = _log_records(
        _activities(db),
        log_id,
    )

    issues = _log_records(
        _issues(db),
        log_id,
    )

    instructions = _log_records(
        _instructions(db),
        log_id,
    )

    # --------------------------------------------------------
    # WORKFORCE
    # --------------------------------------------------------

    st.markdown(
        "### Workforce"
    )

    if workforce:

        total_planned = sum(
            item.get(
                "planned",
                0,
            )
            for item in workforce
        )

        total_actual = sum(
            item.get(
                "actual",
                0,
            )
            for item in workforce
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Planned Workforce",
            total_planned,
        )

        c2.metric(
            "Actual Workforce",
            total_actual,
        )

        for item in workforce:

            st.write(
                f"**{item.get('category')}** "
                f"| Planned: "
                f"{item.get('planned')} "
                f"| Actual: "
                f"{item.get('actual')}"
            )

    else:

        st.caption(
            "No workforce entries."
        )

    st.divider()

    # --------------------------------------------------------
    # EQUIPMENT
    # --------------------------------------------------------

    st.markdown(
        "### Equipment & Plant"
    )

    if equipment:

        for item in equipment:

            st.write(
                f"**{item.get('equipment')}** "
                f"| Qty: {item.get('quantity')} "
                f"| Operating: "
                f"{item.get('operating_hours')} hrs "
                f"| Idle/Breakdown: "
                f"{item.get('idle_hours')} hrs"
            )

    else:

        st.caption(
            "No equipment entries."
        )

    st.divider()

    # --------------------------------------------------------
    # MATERIALS
    # --------------------------------------------------------

    st.markdown(
        "### Materials"
    )

    if materials:

        for item in materials:

            st.write(
                f"**{item.get('material')}** "
                f"| Received: "
                f"{item.get('quantity_received')} "
                f"{item.get('unit')} "
                f"| Used: "
                f"{item.get('quantity_used')} "
                f"{item.get('unit')}"
            )

    else:

        st.caption(
            "No material entries."
        )

    st.divider()

    # --------------------------------------------------------
    # ACTIVITIES
    # --------------------------------------------------------

    st.markdown(
        "### Construction Activities"
    )

    if activities:

        for item in activities:

            progress = float(
                item.get(
                    "progress",
                    0,
                )
            )

            st.markdown(
                f"**{item.get('description')}**"
            )

            st.caption(
                f"Location: "
                f"{item.get('location') or 'Not specified'} "
                f"• BOQ: "
                f"{item.get('boq_reference') or 'Not linked'}"
            )

            st.progress(
                progress / 100
            )

            st.caption(
                f"Progress: {progress:.0f}% "
                f"• Today: "
                f"{item.get('today_quantity')} "
                f"{item.get('unit')} "
                f"• Cumulative: "
                f"{item.get('cumulative_quantity')} "
                f"{item.get('unit')}"
            )

    else:

        st.caption(
            "No activity entries."
        )

    st.divider()

    # --------------------------------------------------------
    # ISSUES
    # --------------------------------------------------------

    st.markdown(
        "### Issues & Delays"
    )

    if issues:

        for item in issues:

            st.warning(
                f"**{item.get('issue')}**"
            )

            st.caption(
                f"Category: "
                f"{item.get('category')} "
                f"• Impact: "
                f"{item.get('duration_hours')} hours "
                f"• RFI: "
                f"{item.get('related_rfi') or 'None'}"
            )

            if item.get(
                "impact"
            ):

                st.write(
                    item.get(
                        "impact"
                    )
                )

    else:

        st.success(
            "No issues or delays recorded."
        )

    st.divider()

    # --------------------------------------------------------
    # INSTRUCTIONS
    # --------------------------------------------------------

    st.markdown(
        "### Site Instructions"
    )

    if instructions:

        for item in instructions:

            st.info(
                item.get(
                    "instruction",
                    "",
                )
            )

            st.caption(
                f"Issued by: "
                f"{item.get('issued_by') or 'Not specified'} "
                f"• Responsible: "
                f"{item.get('responsible_party') or 'Not specified'} "
                f"• RFI: "
                f"{item.get('related_rfi') or 'None'}"
            )

    else:

        st.caption(
            "No site instructions recorded."
        )


# ============================================================
# OPEN LOG
# ============================================================

def _render_open_log(
    db,
    log,
):

    log_id = log.get(
        "id"
    )

    st.subheader(
        f"{log_id} — "
        f"{log.get('log_date', '')}"
    )

    st.caption(
        _project_name(
            db,
            log.get(
                "project_id"
            ),
        )
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Progress",
            f"{float(log.get('overall_progress', 0)):.0f}%",
        )

    with col2:

        st.metric(
            "Workforce",
            log.get(
                "workforce_total",
                0,
            ),
        )

    with col3:

        st.metric(
            "Weather",
            log.get(
                "weather",
                "N/A",
            ),
        )

    with col4:

        _status_badge(
            log.get(
                "status",
                "Draft",
            )
        )

    st.divider()

    # --------------------------------------------------------
    # SITE CONDITIONS
    # --------------------------------------------------------

    st.markdown(
        "### Site Conditions"
    )

    c1, c2 = st.columns(2)

    with c1:

        st.write(
            f"**Weather:** "
            f"{log.get('weather', '')}"
        )

        st.write(
            f"**Working Conditions:** "
            f"{log.get('working_condition', '')}"
        )

    with c2:

        st.write(
            f"**Site Access:** "
            f"{log.get('site_access') or 'Normal'}"
        )

    # --------------------------------------------------------
    # DAILY SUMMARY
    # --------------------------------------------------------

    st.markdown(
        "### Daily Summary"
    )

    st.write(
        f"**Activities**\n\n"
        f"{log.get('activities_summary', '')}"
    )

    if log.get(
        "achievements"
    ):

        st.write(
            f"**Key Achievements**\n\n"
            f"{log.get('achievements')}"
        )

    if log.get(
        "issues_summary"
    ):

        st.warning(
            log.get(
                "issues_summary"
            )
        )

    if log.get(
        "safety_summary"
    ):

        st.info(
            log.get(
                "safety_summary"
            )
        )

    if log.get(
        "tomorrow_plan"
    ):

        st.write(
            f"**Tomorrow's Plan**\n\n"
            f"{log.get('tomorrow_plan')}"
        )

    if log.get(
        "remarks"
    ):

        st.write(
            f"**Remarks**\n\n"
            f"{log.get('remarks')}"
        )

    st.divider()

    # --------------------------------------------------------
    # DETAIL TABS
    # --------------------------------------------------------

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "Workforce",
            "Equipment",
            "Materials",
            "Activities",
            "Issues",
            "Instructions",
        ]
    )

    with tab1:

        _render_workforce_form(
            db,
            log,
        )

        st.divider()

        workforce = _log_records(
            _workforce(db),
            log_id,
        )

        for item in workforce:

            st.write(
                f"{item.get('category')} "
                f"• Planned {item.get('planned')} "
                f"• Actual {item.get('actual')}"
            )

    with tab2:

        _render_equipment_form(
            db,
            log,
        )

        st.divider()

        equipment = _log_records(
            _equipment(db),
            log_id,
        )

        for item in equipment:

            st.write(
                f"{item.get('equipment')} "
                f"• Qty {item.get('quantity')} "
                f"• {item.get('operating_hours')} hrs"
            )

    with tab3:

        _render_material_form(
            db,
            log,
        )

        st.divider()

        materials = _log_records(
            _materials(db),
            log_id,
        )

        for item in materials:

            st.write(
                f"{item.get('material')} "
                f"• Received {item.get('quantity_received')} "
                f"• Used {item.get('quantity_used')} "
                f"{item.get('unit')}"
            )

    with tab4:

        _render_activity_form(
            db,
            log,
        )

        st.divider()

        activities = _log_records(
            _activities(db),
            log_id,
        )

        for item in activities:

            st.write(
                f"**{item.get('description')}** "
                f"• {item.get('progress', 0):.0f}%"
            )

    with tab5:

        _render_issue_form(
            db,
            log,
        )

        st.divider()

        issues = _log_records(
            _issues(db),
            log_id,
        )

        for item in issues:

            st.warning(
                f"{item.get('issue')} "
                f"• {item.get('category')}"
            )

    with tab6:

        _render_instruction_form(
            db,
            log,
        )

        st.divider()

        instructions = _log_records(
            _instructions(db),
            log_id,
        )

        for item in instructions:

            st.info(
                item.get(
                    "instruction",
                    "",
                )
            )

    st.divider()

    # --------------------------------------------------------
    # COMPLETE LOG
    # --------------------------------------------------------

    st.subheader(
        "Log Workflow"
    )

    current_status = log.get(
        "status",
        "Draft",
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if current_status == "Draft":

            if st.button(
                "Submit Log",
                use_container_width=True,
            ):

                update_record(
                    db,
                    "site_logs",
                    log_id,
                    {
                        "status": "Submitted",
                        "submitted_at": str(
                            date.today()
                        ),
                    },
                )

                st.success(
                    "Daily log submitted."
                )

                st.rerun()

    with col2:

        if current_status == "Submitted":

            if st.button(
                "Mark Reviewed",
                use_container_width=True,
            ):

                update_record(
                    db,
                    "site_logs",
                    log_id,
                    {
                        "status": "Reviewed",
                        "reviewed_by": _current_user(),
                    },
                )

                st.success(
                    "Daily log marked as reviewed."
                )

                st.rerun()

    with col3:

        if current_status == "Reviewed":

            if st.button(
                "Approve Log",
                use_container_width=True,
            ):

                update_record(
                    db,
                    "site_logs",
                    log_id,
                    {
                        "status": "Approved",
                        "approved_by": _current_user(),
                    },
                )

                st.success(
                    "Daily log approved."
                )

                st.rerun()

    st.divider()

    if st.button(
        "Delete Daily Log",
        type="secondary",
        use_container_width=True,
    ):

        st.session_state[
            "delete_site_log_id"
        ] = log_id

        st.rerun()

    if st.button(
        "← Back to Site Logs",
        use_container_width=True,
    ):

        st.session_state.pop(
            "open_site_log_id",
            None,
        )

        st.rerun()


# ============================================================
# DELETE LOG
# ============================================================

def _render_delete_log(
    db,
    log,
):

    st.warning(
        f"Delete **{log.get('id')}**?"
    )

    st.write(
        f"Project: "
        f"{_project_name(db, log.get('project_id'))}"
    )

    st.write(
        f"Date: "
        f"{log.get('log_date')}"
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "Confirm Delete",
            type="primary",
            use_container_width=True,
        ):

            delete_record(
                db,
                "site_logs",
                log.get("id"),
            )

            # Delete child records.
            for collection_name in [
                "site_log_workforce",
                "site_log_equipment",
                "site_log_materials",
                "site_log_activities",
                "site_log_issues",
                "site_log_instructions",
            ]:

                children = get_collection(
                    db,
                    collection_name,
                )

                db[
                    collection_name
                ] = [
                    item
                    for item in children
                    if str(
                        item.get("log_id")
                    )
                    != str(
                        log.get("id")
                    )
                ]

            # Persist child deletion.
            from .database import save_memory

            save_memory(db)

            st.session_state.pop(
                "delete_site_log_id",
                None,
            )

            st.session_state.pop(
                "open_site_log_id",
                None,
            )

            st.success(
                "Daily site log deleted."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.pop(
                "delete_site_log_id",
                None,
            )

            st.rerun()


# ============================================================
# MAIN MODULE
# ============================================================

def render_site_logs_module(db):

    logs = _logs(db)

    st.markdown(
        """
        <div class="module-header">
            <div class="module-title">
                Daily Site Logs
            </div>
            <div class="module-subtitle">
                Daily construction progress, workforce,
                equipment, materials, safety and site control.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # KPI
    # ========================================================

    today = str(
        date.today()
    )

    today_logs = [
        log
        for log in logs
        if log.get("log_date")
        == today
    ]

    submitted = sum(
        1
        for log in logs
        if log.get("status")
        == "Submitted"
    )

    approved = sum(
        1
        for log in logs
        if log.get("status")
        == "Approved"
    )

    total_issues = len(
        _issues(db)
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total Logs",
            len(logs),
        )

    with col2:

        st.metric(
            "Today's Logs",
            len(today_logs),
        )

    with col3:

        st.metric(
            "Submitted",
            submitted,
        )

    with col4:

        st.metric(
            "Approved",
            approved,
        )

    with col5:

        st.metric(
            "Site Issues",
            total_issues,
        )

    st.divider()

    # ========================================================
    # OPEN LOG
    # ========================================================

    open_id = st.session_state.get(
        "open_site_log_id"
    )

    if open_id:

        log = next(
            (
                item
                for item in logs
                if str(item.get("id"))
                == str(open_id)
            ),
            None,
        )

        if log:

            _render_open_log(
                db,
                log,
            )

            return

    # ========================================================
    # DELETE CONFIRMATION
    # ========================================================

    delete_id = st.session_state.get(
        "delete_site_log_id"
    )

    if delete_id:

        log = next(
            (
                item
                for item in logs
                if str(item.get("id"))
                == str(delete_id)
            ),
            None,
        )

        if log:

            _render_delete_log(
                db,
                log,
            )

            st.divider()

    # ========================================================
    # TABS
    # ========================================================

    tab_register, tab_create = st.tabs(
        [
            "Site Log Register",
            "Create Daily Log",
        ]
    )

    # ========================================================
    # REGISTER
    # ========================================================

    with tab_register:

        projects = _projects(db)

        if not logs:

            st.info(
                "No daily site logs have been recorded yet."
            )

        else:

            col1, col2 = st.columns(2)

            with col1:

                project_filter = st.selectbox(
                    "Project",
                    ["All"]
                    + [
                        project.get(
                            "name",
                            project.get("id"),
                        )
                        for project in projects
                    ],
                )

            with col2:

                status_filter = st.selectbox(
                    "Status",
                    ["All"]
                    + LOG_STATUSES,
                )

            search = st.text_input(
                "Search Site Logs",
                placeholder=(
                    "Log number, project, activities, "
                    "date or prepared by..."
                ),
            )

            search_term = (
                search.strip().lower()
            )

            filtered = []

            for log in logs:

                project_name = _project_name(
                    db,
                    log.get(
                        "project_id"
                    ),
                )

                searchable = " ".join(
                    [
                        str(
                            log.get(
                                "id",
                                "",
                            )
                        ),
                        str(
                            log.get(
                                "log_date",
                                "",
                            )
                        ),
                        str(
                            log.get(
                                "activities_summary",
                                "",
                            )
                        ),
                        str(
                            log.get(
                                "prepared_by",
                                "",
                            )
                        ),
                        project_name,
                    ]
                ).lower()

                if (
                    search_term
                    and search_term
                    not in searchable
                ):

                    continue

                if (
                    project_filter != "All"
                    and project_name
                    != project_filter
                ):

                    continue

                if (
                    status_filter != "All"
                    and log.get(
                        "status"
                    )
                    != status_filter
                ):

                    continue

                filtered.append(
                    log
                )

            filtered.sort(
                key=lambda item: item.get(
                    "log_date",
                    "",
                ),
                reverse=True,
            )

            st.caption(
                f"Showing {len(filtered)} "
                f"of {len(logs)} site logs"
            )

            for log in filtered:

                with st.container(
                    border=True
                ):

                    c1, c2 = st.columns(
                        [4, 1]
                    )

                    with c1:

                        st.markdown(
                            f"### "
                            f"{log.get('id')} "
                            f"• "
                            f"{log.get('log_date')}"
                        )

                        st.caption(
                            _project_name(
                                db,
                                log.get(
                                    "project_id"
                                ),
                            )
                        )

                    with c2:

                        _status_badge(
                            log.get(
                                "status",
                                "Draft",
                            )
                        )

                    c1, c2, c3, c4 = st.columns(
                        4
                    )

                    c1.metric(
                        "Progress",
                        f"{float(log.get('overall_progress', 0)):.0f}%",
                    )

                    c2.metric(
                        "Workforce",
                        log.get(
                            "workforce_total",
                            0,
                        ),
                    )

                    c3.write(
                        f"**Weather**\n\n"
                        f"{log.get('weather', 'N/A')}"
                    )

                    c4.write(
                        f"**Prepared By**\n\n"
                        f"{log.get('prepared_by', 'Unknown')}"
                    )

                    st.write(
                        log.get(
                            "activities_summary",
                            "",
                        )
                    )

                    if st.button(
                        "Open Daily Log",
                        key=f"open_{log.get('id')}",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "open_site_log_id"
                        ] = log.get(
                            "id"
                        )

                        st.rerun()

    # ========================================================
    # CREATE
    # ========================================================

    with tab_create:

        _render_create_log(
            db
        )