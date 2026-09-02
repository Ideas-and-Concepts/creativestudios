"""Creative Studios shared project context helpers."""
from __future__ import annotations

from typing import Any

from modules.database import get_records


def get_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    return get_records("projects", database)


def _project_sort_key(project: dict[str, Any]) -> tuple[str, str]:
    return (str(project.get("name", "")).lower(), str(project.get("id", "")))


def project_options(database: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(get_projects(database), key=_project_sort_key)


def project_label(project: dict[str, Any]) -> str:
    return f"{project.get('id')} | {project.get('name', 'Unnamed Project')}"


def project_map(database: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(project.get("id")): project for project in project_options(database)}


def select_project(database: dict[str, Any], label: str = "Project", key: str | None = None) -> Any | None:
    import streamlit as st

    projects = project_options(database)
    if not projects:
        st.warning("No projects found. Create a project first in Projects.")
        return None
    labels = [project_label(project) for project in projects]
    selected = st.selectbox(label, labels, key=key)
    return projects[labels.index(selected)].get("id")


def filter_project_records(records: list[dict[str, Any]], project_id: Any | None) -> list[dict[str, Any]]:
    if project_id is None:
        return []
    return [record for record in records if str(record.get("project_id")) == str(project_id)]
