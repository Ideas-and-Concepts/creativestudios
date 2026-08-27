"""
Creative Studios
Dashboard Module
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _safe_list(database: dict[str, Any], key: str) -> list[dict[str, Any]]:
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


def render_dashboard(database: dict[str, Any]) -> None:
    """Render the Creative Studios dashboard."""

    projects = _safe_list(database, "projects")
    documents = _safe_list(database, "documents")
    drawings = _safe_list(database, "drawings")
    rfis = _safe_list(database, "rfis")
    tasks = _safe_list(database, "tasks")

    active_projects = sum(
        1
        for project in projects
        if str(project.get("status", "")).lower() == "active"
    )

    open_rfis = sum(
        1
        for rfi in rfis
        if str(rfi.get("status", "")).lower()
        not in {"closed", "completed"}
    )

    open_tasks = sum(
        1
        for task in tasks
        if str(task.get("status", "")).lower()
        not in {"completed", "closed"}
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

    columns = st.columns(5)

    metrics = [
        ("Projects", len(projects)),
        ("Active Projects", active_projects),
        ("Documents", len(documents)),
        ("Drawings", len(drawings)),
        ("Open RFIs", open_rfis),
    ]

    for column, (label, value) in zip(columns, metrics):
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
                            project.get("project_name", "Unnamed"),
                        ),
                        "Status": project.get(
                            "status",
                            "Unknown",
                        ),
                        "Budget": _safe_float(
                            project.get(
                                "estimated_budget",
                                project.get("budget", 0),
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
            st.info("No projects have been created yet.")

    with right:
        st.subheader("Workspace Activity")

        activity = [
            ("Documents", len(documents)),
            ("Drawings", len(drawings)),
            ("Open RFIs", open_rfis),
            ("Open Tasks", open_tasks),
        ]

        for label, value in activity:
            st.write(f"**{label}:** {value}")

        st.write(
            f"**Total Project Budget:** "
            f"{total_budget:,.2f}"
        )