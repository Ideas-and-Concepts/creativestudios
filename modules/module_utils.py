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


def _workflow_label(collection: str, record: dict[str, Any]) -> tuple[str, str]:
    if collection == "rfis":
        return "RFI", f"{record.get('rfi_number') or 'RFI'} · {record.get('subject') or 'Information request'}"
    if collection == "approvals":
        number = record.get("approval_number") or "Approval"
        return "Approval", f"{number} · {record.get('subject') or 'Approval request'}"
    return collection.rstrip("s").title(), str(record.get("title") or record.get("name") or record.get("id") or collection)


def _record_workflow_event(
    database: dict[str, Any],
    collection: str,
    record: dict[str, Any],
    action: str,
    *,
    notify: bool = False,
) -> None:
    """Mirror important Streamlit mutations into the existing activity/notification collections."""
    entity_type, label = _workflow_label(collection, record)
    actor = record.get("updated_by") or record.get("requested_by") or record.get("raised_by") or record.get("assigned_to") or "Streamlit User"
    details = f"{label}: {action}."

    add_record(
        "activity_log",
        {
            "project_id": record.get("project_id"),
            "action": action,
            "entity_type": entity_type,
            "entity_id": record.get("id"),
            "entity_label": label,
            "actor": actor,
            "details": details,
            "timestamp": now_iso(),
        },
        database,
    )

    if not notify or collection not in {"rfis", "approvals"}:
        return

    recipient = record.get("assigned_to") if collection == "rfis" else record.get("reviewer") or record.get("approver")
    if not recipient:
        recipient = record.get("raised_by") if collection == "rfis" else record.get("requested_by")
    if not recipient:
        return

    severity = "normal"
    if collection == "rfis" and str(record.get("priority") or "").lower() in {"high", "critical"}:
        severity = str(record.get("priority")).lower()

    add_record(
        "notifications",
        {
            "project_id": record.get("project_id"),
            "title": f"{entity_type} workflow update",
            "message": details,
            "type": "workflow",
            "severity": severity,
            "recipient": recipient,
            "source_type": entity_type,
            "source_id": record.get("id"),
            "action_url": f"/{'rfis' if collection == 'rfis' else 'approvals'}",
            "is_read": False,
            "created_at": now_iso(),
        },
        database,
    )


def save_new_record(database: dict[str, Any], collection: str, record: dict[str, Any]) -> dict[str, Any]:
    """Insert a record through the real backing collection and persist it."""
    saved = add_record(collection, dict(record), database)
    if collection in {"rfis", "approvals"}:
        _record_workflow_event(database, collection, saved, "Created", notify=True)
    return saved


def save_updated_record(
    database: dict[str, Any],
    collection: str,
    record_id: Any,
    updates: dict[str, Any],
) -> bool:
    updated = update_record(collection, record_id, updates, database)
    if updated is not None and collection in {"rfis", "approvals"}:
        _record_workflow_event(database, collection, updated, "Updated", notify=True)
    return updated is not None


def remove_record(database: dict[str, Any], collection: str, record_id: Any) -> bool:
    if collection in {"rfis", "approvals"}:
        records = ensure_collection(database, collection)
        existing = next((r for r in records if str(r.get("id")) == str(record_id)), None)
        if existing:
            _record_workflow_event(database, collection, existing, "Deleted", notify=False)
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
