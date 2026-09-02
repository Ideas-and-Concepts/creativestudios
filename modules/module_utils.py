"""Shared helpers for Creative Studios legacy Streamlit modules."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import add_record, delete_record, update_record
from modules.project_context import filter_project_records, project_label, project_options


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_collection(database: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    raw = database.get(collection, [])
    if not isinstance(raw, list):
        raw = []
    records: list[dict[str, Any]] = []
    for index, item in enumerate(raw, 1):
        if isinstance(item, dict):
            record = dict(item)
            record.setdefault("id", index)
            records.append(record)
    database[collection] = records
    return records


def project_selector(database: dict[str, Any], key: str) -> tuple[Any | None, list[dict[str, Any]]]:
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects.")
        return None, []

    labels = [project_label(project) for project in projects]
    selected = st.selectbox("Project", labels, key=key)
    project = projects[labels.index(selected)]
    return project.get("id"), projects


def project_id_of(record: dict[str, Any]) -> Any | None:
    return record.get("project_id")


def project_records(records: list[dict[str, Any]], project_id: Any) -> list[dict[str, Any]]:
    return filter_project_records(records, project_id)


def save_new_record(database: dict[str, Any], collection: str, record: dict[str, Any]) -> dict[str, Any]:
    """Insert a record through the real backing collection and persist it."""
    return add_record(collection, dict(record), database)


def save_updated_record(
    database: dict[str, Any],
    collection: str,
    record_id: Any,
    updates: dict[str, Any],
) -> bool:
    return update_record(collection, record_id, updates, database) is not None


def remove_record(database: dict[str, Any], collection: str, record_id: Any) -> bool:
    return delete_record(collection, record_id, database)


def render_record_actions(
    database: dict[str, Any],
    collection: str,
    record: dict[str, Any],
    key_prefix: str,
) -> bool:
    record_id = record.get("id")
    col1, col2 = st.columns(2)
    with col1:
        st.caption(f"Record ID: {record_id}")
    with col2:
        if st.button("Delete", key=f"{key_prefix}_delete_{record_id}", use_container_width=True):
            remove_record(database, collection, record_id)
            st.rerun()
    return False
