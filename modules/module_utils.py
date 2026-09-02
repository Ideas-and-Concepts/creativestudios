"""Shared helpers for Creative Studios legacy Streamlit modules."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from modules.database import add_record, delete_record, update_record
from modules.project_context import project_label, project_options


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


def project_selector(database: dict[str, Any], key: str) -> tuple[int | None, list[dict[str, Any]]]:
    projects = project_options(database)
    if not projects:
        st.warning("Create a project first in Projects.")
        return None, []
    labels = [project_label(project) for project in projects]
    selected = st.selectbox("Project", labels, key=key)
    return int(projects[labels.index(selected)]["id"]), projects


def project_id_of(record: dict[str, Any]) -> int | None:
    value = record.get("project_id")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def project_records(records: list[dict[str, Any]], project_id: int) -> list[dict[str, Any]]:
    return [record for record in records if project_id_of(record) == project_id]


def save_new_record(database: dict[str, Any], collection: str, record: dict[str, Any]) -> dict[str, Any]:
    """Insert a new record into the real backing collection and persist it.

    ``get_records`` returns a filtered copy, so appending to its result does not
    modify the database. Use the database layer's ``add_record`` instead.
    """
    return add_record(collection, dict(record), database)


def save_updated_record(database: dict[str, Any], collection: str, record_id: Any, updates: dict[str, Any]) -> bool:
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
