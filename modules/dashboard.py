"""
Creative Studios
Dashboard Module

Main AEC collaboration dashboard.

The Dashboard:
    - Displays project statistics
    - Displays document statistics
    - Displays Architecture statistics
    - Displays Engineering statistics
    - Displays MEP statistics
    - Displays BOQ statistics
    - Displays drawing activity
    - Displays design status
    - Provides a simple system overview

The Dashboard does NOT render the application logo.
The application logo belongs to the main sidebar in
streamlit_app.py.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# ============================================================
# SAFE DATABASE HELPERS
# ============================================================

def _get_records(
    database: dict[str, Any],
    key: str,
) -> list[Any]:
    """
    Safely return a database collection.

    Missing collections, invalid values and legacy database
    structures are handled without crashing the Dashboard.
    """

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
    """Count dictionary records matching a field/value."""

    total = 0

    target = str(
        value
    ).strip().lower()

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


def _count_contains(
    database: dict[str, Any],
    key: str,
    field: str,
    value: str,
) -> int:
    """Count dictionary records where a field contains text."""

    total = 0

    target = str(
        value
    ).strip().lower()

    if not target:
        return 0

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

        if target in current:
            total += 1

    return total


# ============================================================
# DASHBOARD CSS
# ============================================================

def inject_dashboard_css() -> None:
    """Apply Dashboard-specific styling."""

    st.markdown(
        """
        <style>

        .cs-dashboard-title {
            font-size: 32px;
            font-weight: 750;
            line-height: 1.15;
            margin-bottom: 0.25rem;
        }

        .cs-dashboard-subtitle {
            font-size: 14px;
            opacity: 0.65;
            margin-bottom: 1.5rem;
        }

        .cs-dashboard-section {
            font-size: 21px;
            font-weight: 700;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }

        .cs-dashboard-card {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 12px;
            padding: 1rem;
            min-height: 105px;
        }

        .cs-dashboard-card-title {
            font-size: 15px;
            font-weight: 700;
        }

        .cs-dashboard-card-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 0.35rem;
        }

        .cs-dashboard-card-description {
            font-size: 12px;
            opacity: 0.60;
            margin-top: 0.25rem;
        }

        .cs-dashboard-activity {
            border: 1px solid rgba(128, 128, 128, 0.20);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            margin-bottom: 0.6rem;
        }

        .cs-dashboard-activity-title {
            font-size: 14px;
            font-weight: 700;
        }

        .cs-dashboard-activity-area {
            font-size: 12px;
            opacity: 0.60;
            margin-top: 0.2rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HEADER
# ============================================================

def render_header() -> None:
    """Render the Dashboard heading."""

    st.markdown(
        """
        <div class="cs-dashboard-title">
            Dashboard
        </div>

        <div class="cs-dashboard-subtitle">
            Creative Studios AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PRIMARY METRICS
# ============================================================

def render_primary_metrics(
    database: dict[str, Any],
) -> None:
    """Render the primary application metrics."""

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

    columns = st.columns(4)

    metrics = [
        (
            columns[0],
            "Projects",
            projects,
            "Project records",
        ),
        (
            columns[1],
            "Documents",
            documents,
            "Project documents",
        ),
        (
            columns[2],
            "Architecture",
            architecture,
            "Architecture records",
        ),
        (
            columns[3],
            "Engineering",
            engineering,
            "Engineering records",
        ),
    ]

    for column, title, value, description in metrics:

        with column:

            st.markdown(
                f"""
                <div class="cs-dashboard-card">

                    <div class="cs-dashboard-card-title">
                        {title}
                    </div>

                    <div class="cs-dashboard-card-value">
                        {value}
                    </div>

                    <div class="cs-dashboard-card-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# CONSTRUCTION WORKSPACES
# ============================================================

def render_construction_workspaces(
    database: dict[str, Any],
) -> None:
    """Render construction discipline statistics."""

    st.divider()

    st.markdown(
        """
        <div class="cs-dashboard-section">
            Construction Workspaces
        </div>
        """,
        unsafe_allow_html=True,
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

    columns = st.columns(4)

    values = [
        (
            columns[0],
            "Architecture",
            architecture,
        ),
        (
            columns[1],
            "Engineering",
            engineering,
        ),
        (
            columns[2],
            "MEP",
            mep,
        ),
        (
            columns[3],
            "BOQ",
            boq,
        ),
    ]

    for column, title, value in values:

        with column:

            st.metric(
                title,
                value,
            )


# ============================================================
# DRAWING ACTIVITY
# ============================================================

def render_drawing_activity(
    database: dict[str, Any],
) -> None:
    """Render Architecture and Engineering drawing statistics."""

    st.subheader(
        "Drawing & Design Activity"
    )

    architecture_drawings = 0

    engineering_drawings = 0

    # Architecture records
    for record in _get_records(
        database,
        "architecture",
    ):

        if not isinstance(record, dict):
            continue

        record_type = str(
            record.get(
                "type",
                "",
            )
        ).lower()

        category = str(
            record.get(
                "category",
                "",
            )
        ).lower()

        title = str(
            record.get(
                "title",
                "",
            )
        ).lower()

        if (
            "drawing" in record_type
            or "drawing" in category
            or "drawing" in title
        ):
            architecture_drawings += 1

    # Engineering records
    for record in _get_records(
        database,
        "engineering",
    ):

        if not isinstance(record, dict):
            continue

        record_type = str(
            record.get(
                "type",
                "",
            )
        ).lower()

        category = str(
            record.get(
                "category",
                "",
            )
        ).lower()

        title = str(
            record.get(
                "title",
                "",
            )
        ).lower()

        if (
            "drawing" in record_type
            or "drawing" in category
            or "drawing" in title
        ):
            engineering_drawings += 1

    total_design = (
        _count(
            database,
            "architecture",
        )
        + _count(
            database,
            "engineering",
        )
    )

    columns = st.columns(3)

    columns[0].metric(
        "Architectural Drawings",
        architecture_drawings,
    )

    columns[1].metric(
        "Engineering Drawings",
        engineering_drawings,
    )

    columns[2].metric(
        "Total Design Records",
        total_design,
    )


# ============================================================
# STATUS SUMMARY
# ============================================================

def render_status_summary(
    database: dict[str, Any],
) -> None:
    """Render Architecture and Engineering status information."""

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

    columns = st.columns(4)

    status_values = [
        (
            columns[0],
            "Architecture Review",
            architecture_review,
        ),
        (
            columns[1],
            "Architecture Issued",
            architecture_issued,
        ),
        (
            columns[2],
            "Engineering Review",
            engineering_review,
        ),
        (
            columns[3],
            "Engineering Issued",
            engineering_issued,
        ),
    ]

    for column, title, value in status_values:

        with column:

            st.metric(
                title,
                value,
            )


# ============================================================
# RECENT ACTIVITY
# ============================================================

def render_recent_activity(
    database: dict[str, Any],
) -> None:
    """Render recent project and design activity."""

    st.subheader(
        "Recent Activity"
    )

    activity: list[tuple[str, str]] = []

    # Projects
    projects = _get_records(
        database,
        "projects",
    )

    for record in projects[-5:]:

        if isinstance(record, dict):

            title = (
                record.get("name")
                or record.get("title")
                or record.get("project")
            )

            if title:

                activity.append(
                    (
                        "Project",
                        str(title),
                    )
                )

    # Architecture
    architecture = _get_records(
        database,
        "architecture",
    )

    for record in architecture[-5:]:

        if isinstance(record, dict):

            title = (
                record.get("title")
                or record.get("name")
            )

            if title:

                activity.append(
                    (
                        "Architecture",
                        str(title),
                    )
                )

    # Engineering
    engineering = _get_records(
        database,
        "engineering",
    )

    for record in engineering[-5:]:

        if isinstance(record, dict):

            title = (
                record.get("title")
                or record.get("name")
            )

            if title:

                activity.append(
                    (
                        "Engineering",
                        str(title),
                    )
                )

    if not activity:

        st.info(
            "No project or design activity has been recorded yet."
        )

        return

    for area, title in reversed(
        activity[-10:]
    ):

        st.markdown(
            f"""
            <div class="cs-dashboard-activity">

                <div class="cs-dashboard-activity-title">
                    {title}
                </div>

                <div class="cs-dashboard-activity-area">
                    {area}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
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
            _count(database, "projects"),
            _count(database, "documents"),
            _count(database, "architecture"),
            _count(database, "engineering"),
            _count(database, "mep"),
            _count(database, "boq"),
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
# MAIN RENDERER
# ============================================================

def render_dashboard(
    database: dict[str, Any],
) -> None:
    """
    Render the complete Creative Studios Dashboard.

    This is the renderer expected by streamlit_app.py.
    """

    if not isinstance(database, dict):
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