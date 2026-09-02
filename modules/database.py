"""Creative Studios JSON Database Layer."""
from __future__ import annotations

import copy
import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "creativestudios_db.json"

DEFAULT_DATABASE: dict[str, Any] = {
    "users": [],
    "projects": [],
    "documents": [],
    "drawings": [],
    "architecture": [],
    "engineering": [],
    "mep": [],
    "boq": [],
    "construction": [],
    "rfis": [],
    "tasks": [],
    "approvals": [],
    "teams": [],
    "site_logs": [],
    "site_log_workforce": [],
    "site_log_equipment": [],
    "site_log_materials": [],
    "site_log_activities": [],
    "site_log_issues": [],
    "site_log_instructions": [],
    "activity_log": [],
    "document_versions": [],
    "settings": {},
}


def _json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _normalize_database(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        data = {}

    normalized = copy.deepcopy(DEFAULT_DATABASE)
    normalized.update(data)

    for key in DEFAULT_DATABASE:
        if key == "settings":
            if not isinstance(normalized.get(key), dict):
                normalized[key] = {}
        elif not isinstance(normalized.get(key), list):
            normalized[key] = []

    return normalized


def load_memory() -> dict[str, Any]:
    """Load and normalize the application database."""
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DB_FILE.exists():
            database = copy.deepcopy(DEFAULT_DATABASE)
            save_memory(database)
            return database

        with DB_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return _normalize_database(data)

    except json.JSONDecodeError:
        database = copy.deepcopy(DEFAULT_DATABASE)
        save_memory(database)
        return database

    except OSError:
        return copy.deepcopy(DEFAULT_DATABASE)

    except Exception:
        return copy.deepcopy(DEFAULT_DATABASE)


def initialize_database() -> dict[str, Any]:
    """Initialize, normalize and return the application database."""
    return load_memory()


def save_memory(db: dict[str, Any]) -> bool:
    """Persist the normalized database atomically."""
    database = _normalize_database(db)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".tmp",
            prefix="creativestudios_",
            dir=DB_FILE.parent,
            delete=False,
        ) as temporary:
            json.dump(
                database,
                temporary,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            )
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)

        os.replace(temporary_path, DB_FILE)
        return True

    except Exception:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
        return False


def _ensure_collection(
    db: dict[str, Any],
    collection: str,
) -> list[Any]:
    if not isinstance(db, dict):
        raise TypeError("Database must be a dictionary.")

    if collection not in db or not isinstance(db[collection], list):
        db[collection] = []

    return db[collection]


def get_collection(
    collection: str,
    db: dict[str, Any],
) -> list[Any]:
    return _ensure_collection(db, collection)


def get_records(
    collection: str,
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        record
        for record in _ensure_collection(db, collection)
        if isinstance(record, dict)
    ]


def next_id(
    collection: str,
    db: dict[str, Any],
) -> int:
    highest = 0

    for record in _ensure_collection(db, collection):
        if isinstance(record, dict):
            try:
                highest = max(
                    highest,
                    int(record.get("id", 0)),
                )
            except (TypeError, ValueError):
                pass

    return highest + 1


def add_record(
    collection: str,
    record: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")

    new_record = copy.deepcopy(record)

    if new_record.get("id") is None:
        new_record["id"] = next_id(collection, db)

    _ensure_collection(db, collection).append(new_record)

    if not save_memory(db):
        _ensure_collection(db, collection).pop()
        raise IOError("Unable to save the database.")

    return new_record


def get_record(
    collection: str,
    record_id: Any,
    db: dict[str, Any],
) -> dict[str, Any] | None:
    for record in _ensure_collection(db, collection):
        if (
            isinstance(record, dict)
            and str(record.get("id")) == str(record_id)
        ):
            return record

    return None


def update_record(
    collection: str,
    record_id: Any,
    updates: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any] | None:
    if not isinstance(updates, dict):
        raise TypeError("Updates must be a dictionary.")

    records = _ensure_collection(db, collection)

    for index, record in enumerate(records):
        if (
            isinstance(record, dict)
            and str(record.get("id")) == str(record_id)
        ):
            original = copy.deepcopy(record)
            updated = copy.deepcopy(record)
            updated.update(copy.deepcopy(updates))
            records[index] = updated

            if not save_memory(db):
                records[index] = original
                raise IOError("Unable to save the database.")

            return updated

    return None


def delete_record(
    collection: str,
    record_id: Any,
    db: dict[str, Any],
) -> bool:
    records = _ensure_collection(db, collection)

    for index, record in enumerate(records):
        if (
            isinstance(record, dict)
            and str(record.get("id")) == str(record_id)
        ):
            deleted = records.pop(index)

            if not save_memory(db):
                records.insert(index, deleted)
                raise IOError("Unable to save the database.")

            return True

    return False
