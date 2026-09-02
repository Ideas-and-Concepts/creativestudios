"""
Creative Studios
JSON Database Layer

Provides required functions for modules.
"""

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from datetime import date, datetime


BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "creativestudios_db.json"


DEFAULT_DATABASE: dict[str, Any] = {
    "projects": [],
    "documents": [],
    "drawings": [],
    "rfis": [],
    "tasks": [],
    "teams": [],
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
    for collection in DEFAULT_DATABASE.keys():
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
        database = copy.deepcopy(DEFAULT_DATABASE)
        save_memory(database)
        return database
    except Exception:
        return copy.deepcopy(DEFAULT_DATABASE)


def save_memory(db: dict[str, Any]) -> bool:
    database = _normalize_database(db)
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
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
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
        return False


def _ensure_collection(db: dict[str, Any], collection: str) -> list[dict[str, Any]]:
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
        if isinstance(record, dict):
            try:
                value = int(record.get("id", 0))
                highest = max(highest, value)
            except (TypeError, ValueError):
                continue
    return highest + 1


def add_record(collection: str, record: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    records = _ensure_collection(db, collection)
    new_record = copy.deepcopy(record)
    if new_record.get("id") is None:
        new_record["id"] = next_id(collection, db)
    records.append(new_record)
    save_memory(db)
    return new_record


def update_record(collection: str, record_id: Any, updates: dict[str, Any], db: dict[str, Any]) -> dict[str, Any] | None:
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if str(record.get("id")) == str(record_id):
            updated = copy.deepcopy(record)
            updated.update(copy.deepcopy(updates))
            records[index] = updated
            save_memory(db)
            return updated
    return None


def delete_record(collection: str, record_id: Any, db: dict[str, Any]) -> bool:
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if str(record.get("id")) == str(record_id):
            records.pop(index)
            save_memory(db)
            return True
    return False