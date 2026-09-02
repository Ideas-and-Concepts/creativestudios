"""
Creative Studios
Shared Project Context

All project-aware modules use Project ID as the relationship key.
"""

from __future__ import annotations

from typing import Any

from modules.database import get_records


def get_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    return get_records("projects", database)


def project_options(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Return projects in stable ID order for selectors."""
    projects = get_projects(database)
    return sorted(projects, key=lambda p: int(p.get("id", 0) or 0))


def project_label(project: dict[str, Any]) -> str:
    return f"{project.get('id')} | {project.get('name', 'Unnamed Project')}"


def project_map(database: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(p.get("id")): p for p in project_options(database)}


def select_project(database: dict[str, Any], label: str = "Project") -> int | None:
    """Render a project selector and return its Project ID."""
    import streamlit as st

    projects = project_options(database)
    if not projects:
        st.warning("No projects found. Create a project first in Projects.")
        return None

    labels = [project_label(p) for p in projects]
    selected = st.selectbox(label, labels)
    return int(projects[labels.index(selected)]["id"])


def filter_project_records(
    records: list[dict[str, Any]],
    project_id: int | None,
) -> list[dict[str, Any]]:
    if project_id is None:
        return []
    return [r for r in records if str(r.get("project_id")) == str(project_id)]
