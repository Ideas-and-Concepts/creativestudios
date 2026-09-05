"""Canonical Neon repositories for Streamlit operational modules."""
from __future__ import annotations

from typing import Any

from modules.database import _neon_connect, _rows_as_dicts

_REPOSITORIES = {
    "tasks": ("tasks", ("project_id", "title", "description", "status", "priority", "due_date"), "id,project_id,title,description,status,priority,due_date,created_at,updated_at"),
    "rfis": ("rfis", ("project_id", "rfi_number", "subject", "question", "response", "status", "raised_by", "assigned_to", "priority", "due_date", "response_date", "drawing_id", "boq_item_id", "construction_activity_id", "notes", "reference"), "id,project_id,rfi_number,subject,question,response,status,raised_by,assigned_to,priority,due_date,response_date,drawing_id,boq_item_id,construction_activity_id,notes,reference,created_at,updated_at"),
    "approvals": ("approvals", ("project_id", "subject", "approval_type", "approval_number", "status", "requested_by", "reviewer", "due_date", "submitted_at", "decided_at", "document_id", "drawing_id", "rfi_id", "comments"), "id,project_id,subject,approval_type,approval_number,status,requested_by,reviewer,due_date,submitted_at,decided_at,document_id,drawing_id,rfi_id,comments,created_at,updated_at"),
    "cost_control": ("cost_control", ("project_id", "cost_code", "description", "cost_type", "amount", "status", "notes"), "id,project_id,cost_code,description,cost_type,amount,status,notes,created_at,updated_at"),
    "construction": ("construction_activities", ("project_id", "boq_item_id", "activity_code", "name", "discipline", "contractor", "status", "progress", "planned_quantity", "actual_quantity", "unit", "planned_start", "planned_end", "actual_start", "actual_end", "notes"), "id,project_id,boq_item_id,activity_code,name,discipline,contractor,status,progress,planned_quantity,actual_quantity,unit,planned_start,planned_end,actual_start,actual_end,notes,created_at,updated_at"),
    "engineering_works": ("engineering_works", ("project_id", "category", "description", "status", "progress", "notes"), "id,project_id,category,description,status,progress,notes,created_at,updated_at"),
    "mep_works": ("mep_works", ("project_id", "drawing_id", "discipline", "category", "description", "specification", "status", "progress", "notes"), "id,project_id,drawing_id,discipline,category,description,specification,status,progress,notes,created_at,updated_at"),
}


def supports(collection: str) -> bool:
    return collection in _REPOSITORIES


def _config(collection: str):
    if not supports(collection):
        raise ValueError(f"No canonical operational repository for '{collection}'.")
    return _REPOSITORIES[collection]


def _clean(collection: str, values: dict[str, Any]) -> dict[str, Any]:
    _, fields, _ = _config(collection)
    unknown = set(values) - set(fields) - {"id", "created_at", "updated_at"}
    if unknown:
        raise ValueError(f"Unsupported {collection} fields: {', '.join(sorted(unknown))}")
    return {k: v for k, v in values.items() if k in fields}


def get_relational_records(collection: str, project_id: Any | None = None) -> list[dict[str, Any]]:
    table, _, select = _config(collection)
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            if project_id is None:
                cursor.execute(f"SELECT {select} FROM {table} ORDER BY created_at DESC")
            else:
                cursor.execute(f"SELECT {select} FROM {table} WHERE project_id=%s ORDER BY created_at DESC", (str(project_id),))
            return _rows_as_dicts(cursor)


def create_relational_record(collection: str, values: dict[str, Any]) -> dict[str, Any]:
    table, _, select = _config(collection)
    clean = _clean(collection, values)
    required = {"project_id"}
    required |= {"title"} if collection == "tasks" else set()
    required |= {"rfi_number", "subject", "question"} if collection == "rfis" else set()
    required |= {"subject", "approval_type"} if collection == "approvals" else set()
    required |= {"cost_code", "description", "cost_type"} if collection == "cost_control" else set()
    required |= {"activity_code", "name"} if collection == "construction" else set()
    required |= {"category", "description"} if collection in {"engineering_works", "mep_works"} else set()
    if collection == "construction":
        required |= {"activity_code", "name"}
    missing = required - set(clean)
    if missing:
        raise ValueError(f"Missing required {collection} fields: {', '.join(sorted(missing))}")
    defaults = {
        "tasks": {"status": "open", "priority": "normal"},
        "rfis": {"status": "open", "priority": "Medium"},
        "approvals": {"status": "pending"},
        "cost_control": {"status": "draft", "amount": 0},
        "construction": {"status": "planned", "progress": 0, "planned_quantity": 0, "actual_quantity": 0},
        "engineering_works": {"status": "planned", "progress": 0},
        "mep_works": {"status": "planned", "progress": 0},
    }[collection]
    for key, value in defaults.items():
        clean.setdefault(key, value)
    columns = list(clean)
    placeholders = ",".join(["%s"] * len(columns))
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders}) RETURNING {select}", [clean[c] for c in columns])
            rows = _rows_as_dicts(cursor)
        connection.commit()
    return rows[0]


def update_relational_record(collection: str, record_id: Any, values: dict[str, Any]) -> dict[str, Any] | None:
    table, _, select = _config(collection)
    clean = _clean(collection, values)
    if not clean:
        raise ValueError(f"No supported {collection} changes supplied.")
    assignments = ", ".join(f"{field}=%s" for field in clean)
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"UPDATE {table} SET {assignments},updated_at=now() WHERE id=%s RETURNING {select}", [*clean.values(), str(record_id)])
            rows = _rows_as_dicts(cursor)
        connection.commit()
    return rows[0] if rows else None


def delete_relational_record(collection: str, record_id: Any) -> bool:
    table, _, _ = _config(collection)
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {table} WHERE id=%s RETURNING id", (str(record_id),))
            deleted = cursor.fetchone() is not None
        connection.commit()
    return deleted
