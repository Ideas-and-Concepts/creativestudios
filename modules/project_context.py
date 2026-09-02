"""Creative Studios shared project context helpers."""
from __future__ import annotations

from typing import Any

from modules.database import get_records


def get_projects(database: dict[str, Any]) -> list[dict[str, Any]]:
    return get_records("projects", database)


def project_options(database: dict[str, Any]) -> list[dict[str, Any]]:
    projects = get_projects(database)
    def sort_key(project: dict[str, Any]) -> tuple[int, str]:
        try:
            return (int(project.get("id", 0) or 0), str(project.get("name", "")))
        except (TypeError, ValueError):
            return (0, str(project.get("name", "")))
    return sorted(projects, key=sort_key)


def project_label(project: dict[str, Any]) -> str:
    return f"{project.get('id')} | {project.get('name', 'Unnamed Project')}"


def project_map(database: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(project.get("id")): project for project in project_options(database)}


def select_project(database: dict[str, Any], label: str = "Project", key: str | None = None) -> int | None:
    import streamlit as st
    projects = project_options(database)
    if not projects:
        st.warning("No projects found. Create a project first in Projects.")
        return None
    labels = [project_label(project) for project in projects]
    selected = st.selectbox(label, labels, key=key)
    return int(projects[labels.index(selected)]["id"])


def filter_project_records(records: list[dict[str, Any]], project_id: int | None) -> list[dict[str, Any]]:
    if project_id is None:
        return []
    return [record for record in records if str(record.get("project_id")) == str(project_id)]
