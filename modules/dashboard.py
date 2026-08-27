"""
Creative Studios
Dashboard Module

AEC Collaboration Platform Dashboard.

The Dashboard provides:
    - Project statistics
    - Document statistics
    - Architecture statistics
    - Engineering statistics
    - MEP statistics
    - BOQ statistics
    - Drawing activity
    - Design status
    - Recent activity
    - System status

The Dashboard does not render the application logo.
Logo and application branding belong to streamlit_app.py.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# ============================================================
# DATABASE HELPERS
# ============================================================

def _get_records(
    database: dict[str, Any],
    key: str,
) -> list[Any]:
    """Safely return a database collection."""

    if not isinstance(database, dict):
        return []

    value = database.get(key, [])

    if isinstance(value, list):
        return value

    return []


def _count(
    database: dict[str, Any],
    key: str,
) -> int:
    """Return the number of records in a collection."""

    return len(
        _get_records(
            database,
            key,
        )
    )


def _count_matching(
    database: dict[str, Any],
    key: str,
    field: str,
    value: str,
) -> int:
    """Count records whose field exactly matches a value."""

    target = str(
        value
    ).strip().lower()

    total = 0

    for record in _get_records(
        database,
        key,
    ):

        if not isinstance(record, dict):
            continue

        current = str(
            record.get(
                field,
                "",
            )
        ).strip().lower()

        if current == target:
            total += 1

    return total


def _is_drawing(
    record: dict[str, Any],
) -> bool:
    """Determine whether a record represents a drawing."""

    fields = (
        "type",
        "category",
        "title",
        "name",
        "document_type",
    )

    for field in fields:

        value = str(
            record.get(
                field,
                "",
            )
        ).strip().lower()

        if "drawing" in value:
            return True

    return False


# ============================================================
# PAGE HEADER
# ============================================================

def render_header() -> None:
    """Render the Dashboard header."""

    st.title(
        "Dashboard"
    )

    st.caption(
        "Creative Studios AEC Collaboration Platform"
    )


# ============================================================
# PRIMARY METRICS
# ============================================================

def render_primary_metrics(
    database: dict[str, Any],
) -> None:
    """Render the primary Dashboard metrics."""

    projects = _count(
        database,
        "projects",
    )

    documents = _count(
        database,
        "documents",
    )

    architecture = _count(
        database,
        "architecture",
    )

    engineering = _count(
        database,
        "engineering",
    )

    columns = st.columns(
        4
    )

    with columns[0]:

        st.metric(
            label="Projects",
            value=projects,
            help="Project records",
        )

    with columns[1]:

        st.metric(
            label="Documents",
            value=documents,
            help="Project documents",
        )

    with columns[2]:

        st.metric(
            label="Architecture",
            value=architecture,
            help="Architecture records",
        )

    with columns[3]:

        st.metric(
            label="Engineering",
            value=engineering,
            help="Engineering records",
        )


# ============================================================
# CONSTRUCTION WORKSPACES
# ============================================================

def render_construction_workspaces(
    database: dict[str, Any],
) -> None:
    """Render construction discipline metrics."""

    st.divider()

    st.subheader(
        "Construction Workspaces"
    )

    architecture = _count(
        database,
        "architecture",
    )

    engineering = _count(
        database,
        "engineering",
    )

    mep = _count(
        database,
        "mep",
    )

    boq = _count(
        database,
        "boq",
    )

    columns = st.columns(
        4
    )

    with columns[0]:

        st.metric(
            "Architecture",
            architecture,
        )

    with columns[1]:

        st.metric(
            "Engineering",
            engineering,
        )

    with columns[2]:

        st.metric(
            "MEP",
            mep,
        )

    with columns[3]:

        st.metric(
            "BOQ",
            boq,
        )


# ============================================================
# DRAWING ACTIVITY
# ============================================================

def render_drawing_activity(
    database: dict[str, Any],
) -> None:
    """Render architectural and engineering drawing statistics."""

    st.subheader(
        "Drawing & Design Activity"
    )

    architecture_drawings = 0

    for record in _get_records(
        database,
        "architecture",
    ):

        if isinstance(record, dict):

            if _is_drawing(record):

                architecture_drawings += 1

    engineering_drawings = 0

    for record in _get_records(
        database,
        "engineering",
    ):

        if isinstance(record, dict):

            if _is_drawing(record):

                engineering_drawings += 1

    total_design_records = (
        _count(
            database,
            "architecture",
        )
        +
        _count(
            database,
            "engineering",
        )
    )

    columns = st.columns(
        3
    )

    with columns[0]:

        st.metric(
            "Architectural Drawings",
            architecture_drawings,
        )

    with columns[1]:

        st.metric(
            "Engineering Drawings",
            engineering_drawings,
        )

    with columns[2]:

        st.metric(
            "Total Design Records",
            total_design_records,
        )


# ============================================================
# STATUS SUMMARY
# ============================================================

def render_status_summary(
    database: dict[str, Any],
) -> None:
    """Render Architecture and Engineering status metrics."""

    st.subheader(
        "Current Status"
    )

    architecture_review = _count_matching(
        database,
        "architecture",
        "status",
        "In Review",
    )

    architecture_issued = _count_matching(
        database,
        "architecture",
        "status",
        "Issued",
    )

    engineering_review = _count_matching(
        database,
        "engineering",
        "status",
        "In Review",
    )

    engineering_issued = _count_matching(
        database,
        "engineering",
        "status",
        "Issued",
    )

    columns = st.columns(
        4
    )

    with columns[0]:

        st.metric(
            "Architecture Review",
            architecture_review,
        )

    with columns[1]:

        st.metric(
            "Architecture Issued",
            architecture_issued,
        )

    with columns[2]:

        st.metric(
            "Engineering Review",
            engineering_review,
        )

    with columns[3]:

        st.metric(
            "Engineering Issued",
            engineering_issued,
        )


# ============================================================
# RECENT ACTIVITY
# ============================================================

def _extract_title(
    record: dict[str, Any],
) -> str:
    """Extract a useful display title from a record."""

    possible_fields = (
        "name",
        "title",
        "project",
        "project_name",
        "document_name",
        "description",
    )

    for field in possible_fields:

        value = record.get(
            field
        )

        if value is not None:

            text = str(
                value
            ).strip()

            if text:
                return text

    return ""


def render_recent_activity(
    database: dict[str, Any],
) -> None:
    """Render recent project and design activity."""

    st.subheader(
        "Recent Activity"
    )

    activity: list[tuple[str, str]] = []

    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    for record in _get_records(
        database,
        "projects",
    ):

        if not isinstance(record, dict):
            continue

        title = _extract_title(
            record
        )

        if title:

            activity.append(
                (
                    "Project",
                    title,
                )
            )

    # --------------------------------------------------------
    # Architecture
    # --------------------------------------------------------

    for record in _get_records(
        database,
        "architecture",
    ):

        if not isinstance(record, dict):
            continue

        title = _extract_title(
            record
        )

        if title:

            activity.append(
                (
                    "Architecture",
                    title,
                )
            )

    # --------------------------------------------------------
    # Engineering
    # --------------------------------------------------------

    for record in _get_records(
        database,
        "engineering",
    ):

        if not isinstance(record, dict):
            continue

        title = _extract_title(
            record
        )

        if title:

            activity.append(
                (
                    "Engineering",
                    title,
                )
            )

    # --------------------------------------------------------
    # No activity
    # --------------------------------------------------------

    if not activity:

        st.info(
            "No project or design activity has been recorded yet."
        )

        return

    # --------------------------------------------------------
    # Display latest records
    # --------------------------------------------------------

    recent = activity[-10:]

    for area, title in reversed(
        recent
    ):

        with st.container(
            border=True
        ):

            st.write(
                title
            )

            st.caption(
                area
            )


# ============================================================
# SYSTEM STATUS
# ============================================================

def render_system_status(
    database: dict[str, Any],
) -> None:
    """Render overall system status."""

    st.divider()

    total_records = sum(
        [
            _count(
                database,
                "projects",
            ),
            _count(
                database,
                "documents",
            ),
            _count(
                database,
                "architecture",
            ),
            _count(
                database,
                "engineering",
            ),
            _count(
                database,
                "mep",
            ),
            _count(
                database,
                "boq",
            ),
        ]
    )

    if total_records > 0:

        st.success(
            "Creative Studios is operational and project data is available."
        )

    else:

        st.info(
            "Creative Studios is ready. Start by creating a project or design record."
        )


# ============================================================
# MAIN DASHBOARD RENDERER
# ============================================================

def render_dashboard(
    database: dict[str, Any],
) -> None:
    """
    Render the complete Creative Studios Dashboard.

    This function is the public renderer used by
    streamlit_app.py.
    """

    if not isinstance(
        database,
        dict,
    ):

        database = {}

    render_header()

    render_primary_metrics(
        database
    )

    render_construction_workspaces(
        database
    )

    render_drawing_activity(
        database
    )

    render_status_summary(
        database
    )

    render_recent_activity(
        database
    )

    render_system_status(
        database
    )