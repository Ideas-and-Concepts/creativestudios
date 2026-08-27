"""
Creative Studios
Dashboard Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _safe_records(
    database: dict[str, Any],
    key: str,
) -> list[dict[str, Any]]:
    """Return only dictionary records from a database collection."""
    value = database.get(key, [])

    if not isinstance(value, list):
        return []

    return [
        item
        for item in value
        if isinstance(item, dict)
    ]


def _safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def render_dashboard(
    database: dict[str, Any],
) -> None:
    """Render the Creative Studios dashboard."""

    projects = _safe_records(database, "projects")
    documents = _safe_records(database, "documents")
    drawings = _safe_records(database, "drawings")
    architecture = _safe_records(database, "architecture")
    engineering = _safe_records(database, "engineering")
    mep = _safe_records(database, "mep")

    active_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).strip().lower()
        == "active"
    )

    completed_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).strip().lower()
        == "completed"
    )

    planning_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).strip().lower()
        == "planning"
    )

    total_budget = sum(
        _safe_float(
            project.get(
                "estimated_budget",
                project.get("budget", 0),
            )
        )
        for project in projects
    )

    st.title("Dashboard")
    st.caption(
        "Creative Studios AEC collaboration workspace."
    )

    metrics = [
        ("Projects", len(projects)),
        ("Active", active_projects),
        ("Planning", planning_projects),
        ("Completed", completed_projects),
        ("Documents", len(documents)),
    ]

    columns = st.columns(5)

    for column, (label, value) in zip(
        columns,
        metrics,
    ):
        with column:
            st.metric(label, value)

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Project Summary")

        if projects:
            rows = []

            for project in projects:
                rows.append(
                    {
                        "Project": project.get(
                            "name",
                            project.get(
                                "project_name",
                                "Unnamed Project",
                            ),
                        ),
                        "Client": project.get(
                            "client",
                            project.get(
                                "client_name",
                                "",
                            ),
                        ),
                        "Status": project.get(
                            "status",
                            "Unknown",
                        ),
                        "Budget": _safe_float(
                            project.get(
                                "estimated_budget",
                                project.get(
                                    "budget",
                                    0,
                                ),
                            )
                        ),
                    }
                )

            st.dataframe(
                rows,
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(
                "No projects have been created yet."
            )

    with right:
        st.subheader("Workspace Summary")

        summary = [
            ("Documents", len(documents)),
            ("Drawings", len(drawings)),
            ("Architecture Records", len(architecture)),
            ("Engineering Records", len(engineering)),
            ("MEP Records", len(mep)),
        ]

        for label, value in summary:
            st.write(
                f"**{label}:** {value}"
            )

        st.write(
            f"**Total Project Budget:** "
            f"{total_budget:,.2f}"
        )