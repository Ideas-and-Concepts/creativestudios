"""Creative Studios shared workspace database layer.

Neon PostgreSQL is the preferred shared store when DATABASE_URL is configured.
The JSON file is used only when DATABASE_URL is not configured, for local/offline development.
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
    "users": [], "projects": [], "documents": [], "drawings": [],
    "architecture": [], "engineering": [], "mep": [], "boq": [],
    "construction": [], "procurement": [], "cost_control": [], "rfis": [],
    "tasks": [], "approvals": [], "teams": [], "site_logs": [],
    "site_log_workforce": [], "site_log_equipment": [], "site_log_materials": [],
    "site_log_activities": [], "site_log_issues": [], "site_log_instructions": [],
    "activity_log": [], "document_versions": [], "settings": {},
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


def _database_url() -> str:
    value = os.getenv("DATABASE_URL", "").strip()
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get("DATABASE_URL", "")).strip()
    except Exception:
        return ""


def database_backend() -> str:
    return "neon" if _database_url() else "json"


def _neon_connect():
    url = _database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not configured.")
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("psycopg is required when DATABASE_URL is configured.") from exc
    return psycopg.connect(url, connect_timeout=10)


def _save_json(database: dict[str, Any]) -> bool:
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".tmp", prefix="creativestudios_",
            dir=DB_FILE.parent, delete=False,
        ) as temporary:
            json.dump(_normalize_database(database), temporary, indent=2,
                      ensure_ascii=False, default=_json_default)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, DB_FILE)
        return True
    except Exception:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)
        return False


def _load_json_file() -> dict[str, Any]:
    try:
        DB_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not DB_FILE.exists():
            database = copy.deepcopy(DEFAULT_DATABASE)
            _save_json(database)
            return database
        with DB_FILE.open("r", encoding="utf-8") as file:
            return _normalize_database(json.load(file))
    except (json.JSONDecodeError, OSError):
        return copy.deepcopy(DEFAULT_DATABASE)
    except Exception:
        return copy.deepcopy(DEFAULT_DATABASE)


def _load_neon() -> dict[str, Any]:
    with _neon_connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT data FROM workspace_state WHERE id = 1")
            row = cursor.fetchone()
        if row and isinstance(row[0], dict):
            database = _normalize_database(row[0])
        else:
            database = copy.deepcopy(DEFAULT_DATABASE)
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO workspace_state (id, data, updated_at) VALUES (1, %s::jsonb, now()) ON CONFLICT (id) DO NOTHING",
                    (json.dumps(database, ensure_ascii=False, default=_json_default),),
                )
            connection.commit()
        _save_json(database)
        return database


def load_memory() -> dict[str, Any]:
    """Load workspace data.

    When DATABASE_URL is configured, Neon is authoritative. Neon connection or
    query failures are surfaced instead of silently falling back to stale JSON.
    JSON is used only when no DATABASE_URL is configured.
    """
    if database_backend() == "neon":
        return _load_neon()
    return _load_json_file()


def initialize_database() -> dict[str, Any]:
    return load_memory()


def save_memory(db: dict[str, Any], *, force_json: bool = False) -> bool:
    """Persist workspace data to Neon when configured, otherwise to JSON."""
    database = _normalize_database(db)
    if not force_json and database_backend() == "neon":
        payload = json.dumps(database, ensure_ascii=False, default=_json_default)
        with _neon_connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO workspace_state (id, data, updated_at) VALUES (1, %s::jsonb, now()) ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data, updated_at = now()",
                    (payload,),
                )
            connection.commit()
        _save_json(database)
        return True
    return _save_json(database)


def _ensure_collection(db: dict[str, Any], collection: str) -> list[Any]:
    if not isinstance(db, dict):
        raise TypeError("Database must be a dictionary.")
    if collection not in db or not isinstance(db[collection], list):
        db[collection] = []
    return db[collection]


def get_collection(collection: str, db: dict[str, Any]) -> list[Any]:
    return _ensure_collection(db, collection)


def get_records(collection: str, db: dict[str, Any]) -> list[dict[str, Any]]:
    return [record for record in _ensure_collection(db, collection) if isinstance(record, dict)]


def next_id(collection: str, db: dict[str, Any]) -> int:
    highest = 0
    for record in _ensure_collection(db, collection):
        if isinstance(record, dict):
            try:
                highest = max(highest, int(record.get("id", 0)))
            except (TypeError, ValueError):
                pass
    return highest + 1


def add_record(collection: str, record: dict[str, Any], db: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise TypeError("Record must be a dictionary.")
    new_record = copy.deepcopy(record)
    if new_record.get("id") is None:
        new_record["id"] = next_id(collection, db)
    _ensure_collection(db, collection).append(new_record)
    try:
        if not save_memory(db):
            raise IOError("Unable to save the database.")
    except Exception:
        _ensure_collection(db, collection).pop()
        raise
    return new_record


def get_record(collection: str, record_id: Any, db: dict[str, Any]) -> dict[str, Any] | None:
    for record in _ensure_collection(db, collection):
        if isinstance(record, dict) and str(record.get("id")) == str(record_id):
            return record
    return None


def update_record(collection: str, record_id: Any, updates: dict[str, Any], db: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(updates, dict):
        raise TypeError("Updates must be a dictionary.")
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if isinstance(record, dict) and str(record.get("id")) == str(record_id):
            original = copy.deepcopy(record)
            updated = copy.deepcopy(record)
            updated.update(copy.deepcopy(updates))
            records[index] = updated
            try:
                if not save_memory(db):
                    raise IOError("Unable to save the database.")
            except Exception:
                records[index] = original
                raise
            return updated
    return None


def delete_record(collection: str, record_id: Any, db: dict[str, Any]) -> bool:
    records = _ensure_collection(db, collection)
    for index, record in enumerate(records):
        if isinstance(record, dict) and str(record.get("id")) == str(record_id):
            deleted = records.pop(index)
            try:
                if not save_memory(db):
                    raise IOError("Unable to save the database.")
            except Exception:
                records.insert(index, deleted)
                raise
            return True
    return False
