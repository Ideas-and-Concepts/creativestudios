"""
Creative Studios
Dashboard Module

Main AEC collaboration dashboard.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# ============================================================
# HELPERS
# ============================================================

def _records(
    database: dict[str, Any],
    key: str,
) -> list[Any]:
    """Safely return a database collection."""

    value = database.get(
        key,
        [],
    )

    if isinstance(value, list):
        return value

    return []


def _count(
    database: dict[str, Any],
    key: str,
) -> int:
    """Count records in a database collection."""

    return len(
        _records(
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
    """Count dictionary records matching a field."""

    total = 0

    for record in _records(
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

        if current == value.strip().lower():
            total += 1

    return total


# ============================================================
# DASHBOARD CSS
# ============================================================

def inject_dashboard_css() -> None:
    """Apply dashboard styling."""

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

        .cs-dashboard-card {
            border: 1px solid rgba(128,128,128,0.20);
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

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DASHBOARD
# ============================================================

def render_dashboard(
    database: dict[str, Any],
) -> None:
    """Render the Creative Studios Dashboard."""

    if not isinstance(database, dict):
        database = {}

    inject_dashboard_css()

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

    # --------------------------------------------------------
    # Primary metrics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Construction workspaces
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "Construction Workspaces"
    )

    workspace_columns = st.columns(4)

    mep = _count(
        database,
        "mep",
    )

    boq = _count(
        database,
        "boq",
    )

    architecture_drawings = _count_matching(
        database,
        "architecture",
        "type",
        "Architectural Drawing",
    )

    engineering_drawings = _count_matching(
        database,
        "engineering",
        "type",
        "Engineering Drawing",
    )

    workspace_metrics = [
        (
            workspace_columns[0],
            "Architecture",
            architecture,
        ),
        (
            workspace_columns[1],
            "Engineering",
            engineering,
        ),
        (
            workspace_columns[2],
            "MEP",
            mep,
        ),
        (
            workspace_columns[3],
            "BOQ",
            boq,
        ),
    ]

    for column, title, value in workspace_metrics:

        with column:

            st.metric(
                title,
                value,
            )

    # --------------------------------------------------------
    # Drawing summary
    # --------------------------------------------------------

    st.subheader(
        "Drawing & Design Activity"
    )

    drawing_columns = st.columns(3)

    drawing_columns[0].metric(
        "Architectural Drawings",
        architecture_drawings,
    )

    drawing_columns[1].metric(
        "Engineering Drawings",
        engineering_drawings,
    )

    drawing_columns[2].metric(
        "Total Design Records",
        architecture + engineering,
    )

    # --------------------------------------------------------
    # Status summary
    # --------------------------------------------------------

    st.subheader(
        "Current Status"
    )

    status_columns = st.columns(4)

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

    status_data = [
        (
            status_columns[0],
            "Architecture Review",
            architecture_review,
        ),
        (
            status_columns[1],
            "Architecture Issued",
            architecture_issued,
        ),
        (
            status_columns[2],
            "Engineering Review",
            engineering_review,
        ),
        (
            status_columns[3],
            "Engineering Issued",
            engineering_issued,
        ),
    ]

    for column, title, value in status_data:

        with column:

            st.metric(
                title,
                value,
            )

    # --------------------------------------------------------
    # System status
    # --------------------------------------------------------

    st.divider()

    st.success(
        "Creative Studios is ready for AEC project collaboration."
    )