"""
Creative Studios
AEC Collaboration Platform

JSON Database Layer
"""

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
    "rfis": [],
    "tasks": [],
    "teams": [],
    "site_logs": [],
    "site_log_workforce": [],
    "site_log_equipment": [],
    "site_log_materials": [],
    "site_log_activities": [],
    "site_log_issues": [],
    "site_log_instructions": [],
    "construction": [],
    "activity_log": [],
    "document_versions": [],
    "boq": [],
    "settings": {},
}


def _json_default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    return str(value)


def _normalize_database(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        data = {}

    normalized = copy.deepcopy(DEFAULT_DATABASE)
    for key, value in data.items():
        normalized[key] = value

    list_collections = [
        "users", "projects", "documents", "drawings", "rfis", "tasks", "teams",
        "site_logs", "site_log_workforce", "site_log_equipment", "site_log_materials",
        "site_log_activities", "site_log_issues", "site_log_instructions",
        "construction", "activity_log", "document_versions", "boq",
    ]

    for collection in list_collections:
        if not isinstance(normalized.get(collection), list):
            normalized[collection] = []

    if not isinstance(normalized.get("settings"), dict):
        normalized["settings"] = {}

    return normalized


def load_memory() -> dict[str, Any]:
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
        try:
            backup = DB_FILE.with_suffix(".corrupt.json")
            if DB_FILE.exists():
                DB_FILE.replace(backup)
        except Exception:
            pass

        database = copy.deepcopy(DEFAULT_DATABASE)
        try:
            save_memory(database)
        except Exception:
            pass
        return database
    except Exception:
        return copy.deepcopy(DEFAULT_DATABASE)


def save_memory(db: dict[str, Any]) -> bool:
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
            json.dump(database, temporary, indent=2, ensure_ascii=False, default=_json_default)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)

        os.replace(temporary_path, DB_FILE)
        return True
    except Exception:
        if temporary_path is not None and temporary_path.exists():
            try:
                temporary_path.unlink()
            except Exception:
                pass
        return False


def _ensure_collection(db: dict[str, Any], collection: str) -> list[dict[str, Any]]:
    if not isinstance(db, dict):
        raise TypeError("Database must be a dictionary.")
    if collection not in db:
        db[collection] = []
    if not isinstance(db[collection], list):
        db[collection] = []
    return db[collection]


def get_collection(collection: str, db: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the raw list for a collection, ensuring it exists."""
    return _ensure_collection(db, collection)


def next_id(collection: str, db: dict[str, Any]) -> int:
    records = _ensure_collection(db, collection)
    highest = 0
    for record in records:
        if not isinstance(record, dict):
            continue
        try:
            value = int(record.get("id"))
            highest = max(highest, value)
        except (TypeError, ValueError):
            continue
    return highest + 1


def add_record(collection: str, record: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")
    records = _ensure_collection(db, collection)
    new_record = copy.deepcopy(record)
    if new_record.get("id") is None:
        new_record["id"] = next_id(collection, db)
    records.append(new_record)
    if not save_memory(db):
        records.pop()
        raise IOError("Unable to save the database.")
    return new_record


def get_record(collection: str, record_id: Any, db: dict[str, Any]) -> dict[str, Any] | None:
    records = _ensure_collection(db, collection)
    for record in records:
        if not isinstance(record, dict):
            continue
        if str(record.get("id")) == str(record_id):
            return record
    return None


def update_record(collection: str, record_id: Any, updates: dict[str, Any], db: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(updates, dict):
        raise TypeError("Updates must be a dictionary.")
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        if str(record.get("id")) != str(record_id):
            continue
        original = copy.deepcopy(record)
        updated = copy.deepcopy(record)
        updated.update(copy.deepcopy(updates))
        records[index] = updated
        if not save_memory(db):
            records[index] = original
            raise IOError("Unable to save the database.")
        return updated
    return None


def delete_record(collection: str, record_id: Any, db: dict[str, Any]) -> bool:
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            continue
        if str(record.get("id")) != str(record_id):
            continue
        deleted = records.pop(index)
        if not save_memory(db):
            records.insert(index, deleted)
            raise IOError("Unable to save the database.")
        return True
    return False


def get_records(collection: str, db: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for record in _ensure_collection(db, collection) if isinstance(record, dict)]


def initialize_database() -> dict[str, Any]:
    db = load_memory()
    save_memory(db)
    return db


def load_database() -> dict[str, Any]:
    return load_memory()


def save_database(db: dict[str, Any]) -> bool:
    return save_memory(db)


def get_all(collection: str, db: dict[str, Any]) -> list[dict[str, Any]]:
    return get_records(collection, db)