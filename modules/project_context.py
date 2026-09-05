"""Creative Studios shared project context helpers.

This module is the single project-selector contract used by Streamlit modules.
When Neon is configured, project lookups come from the same relational
``projects`` table used by the Next.js application. Local development keeps
the JSON workspace fallback.
"""
from __future__ import annotations

from typing import Any

from modules.database import database_backend, get_records, get_relational_projects

SHARED_PROJECT_KEY = "cs_selected_project_id"


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


def get_selected_project_id() -> str | None:
    """Return the shared project selection stored in Streamlit session state."""
    import streamlit as st

    value = st.session_state.get(SHARED_PROJECT_KEY)
    return str(value) if value not in (None, "", "all") else None


def set_selected_project_id(project_id: Any | None) -> None:
    """Update the shared project selection for all modules in this session."""
    import streamlit as st

    st.session_state[SHARED_PROJECT_KEY] = None if project_id in (None, "", "all") else str(project_id)


def select_project(
    database: dict[str, Any],
    label: str = "Project",
    key: str | None = None,
    include_all: bool = True,
) -> str | None:
    """Render the shared project selector and persist its canonical project ID."""
    import streamlit as st

    projects = project_options(database)
    if not projects:
        set_selected_project_id(None)
        st.warning("No projects found. Create a project first in Projects.")
        return None

    by_id = {str(project.get("id")): project for project in projects}
    options = ([None] if include_all else []) + list(by_id)
    current = get_selected_project_id()
    if current not in options:
        current = None if include_all else next(iter(by_id), None)
        set_selected_project_id(current)

    def format_option(value: Any) -> str:
        if value is None:
            return "All Projects"
        return project_label(by_id[str(value)])

    widget_key = key or "cs_shared_project_selector"
    selected = st.selectbox(
        label,
        options,
        index=options.index(current) if current in options else 0,
        format_func=format_option,
        key=widget_key,
    )
    set_selected_project_id(selected)
    return get_selected_project_id()


def filter_project_records(
    records: list[dict[str, Any]],
    project_id: Any | None,
) -> list[dict[str, Any]]:
    """Filter records to one canonical project ID."""
    if project_id is None:
        return records
    return [record for record in records if str(record.get("project_id")) == str(project_id)]
