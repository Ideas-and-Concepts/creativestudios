"""Creative Studios shared project context helpers.

This module is the single project-selector contract used by Streamlit modules.
When Neon is configured, project lookups come from the same relational
``projects`` table used by the Next.js application. Local development keeps
the JSON workspace fallback.
"""
from __future__ import annotations

from typing import Any

from modules.database import database_backend, get_records, get_relational_projects


def get_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Return canonical project records from the active shared backend."""
    if database_backend() == "neon":
        return get_relational_projects()
    return get_records("projects", database)


def _project_sort_key(project: dict[str, Any]) -> tuple[str, str]:
    return (str(project.get("name", "")).lower(), str(project.get("id", "")))


def project_options(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Return projects in stable display order for downstream selectors."""
    return sorted(get_projects(database), key=_project_sort_key)


def project_label(project: dict[str, Any]) -> str:
    """Return a human-readable project identity, preferring its business code."""
    code = str(project.get("code") or "").strip()
    name = str(project.get("name") or "Unnamed Project").strip()
    return f"{code} | {name}" if code else name


def project_map(database: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Map canonical project IDs to project records."""
    return {str(project.get("id")): project for project in project_options(database)}


def select_project(
    database: dict[str, Any],
    label: str = "Project",
    key: str | None = None,
) -> Any | None:
    """Render a shared project selector and return the canonical project ID."""
    import streamlit as st

    projects = project_options(database)
    if not projects:
        st.warning("No projects found. Create a project first in Projects.")
        return None

    labels = [project_label(project) for project in projects]
    selected = st.selectbox(label, labels, key=key)
    return projects[labels.index(selected)].get("id")


def filter_project_records(
    records: list[dict[str, Any]],
    project_id: Any | None,
) -> list[dict[str, Any]]:
    """Filter records to one canonical project ID."""
    if project_id is None:
        return []
    return [record for record in records if str(record.get("project_id")) == str(project_id)]
