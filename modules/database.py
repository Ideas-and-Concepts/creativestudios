"""
Creative Studios
AEC Collaboration Platform

JSON Database Layer
-------------------

Single, reliable database contract for the Streamlit application.

Public functions:

    load_memory()
    save_memory(db)
    initialize_database()

    add_record(collection, record, db)
    get_record(collection, record_id, db)
    get_records(collection, db)
    update_record(collection, record_id, updates, db)
    delete_record(collection, record_id, db)

    next_id(collection, db)

Compatibility aliases:

    load_database()
    save_database()
    get_all()
"""

from __future__ import annotations

import copy
import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "creativestudios_db.json"


# ============================================================
# DEFAULT DATABASE
# ============================================================

DEFAULT_DATABASE: dict[str, Any] = {
    "users": [],
    "projects": [],
    "documents": [],
    "drawings": [],
    "rfis": [],
    "tasks": [],
    "teams": [],
    "settings": {},
}


LIST_COLLECTIONS = (
    "users",
    "projects",
    "documents",
    "drawings",
    "rfis",
    "tasks",
    "teams",
)


# ============================================================
# SERIALIZATION
# ============================================================

def _json_default(value: Any) -> str:
    """Convert common Python values into JSON-safe values."""

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    return str(value)


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_database(data: Any) -> dict[str, Any]:
    """
    Normalize any loaded database into the expected structure.
    """

    if not isinstance(data, dict):
        data = {}

    normalized = copy.deepcopy(DEFAULT_DATABASE)

    for key, value in data.items():
        normalized[key] = value

    for collection in LIST_COLLECTIONS:
        if not isinstance(normalized.get(collection), list):
            normalized[collection] = []

    if not isinstance(normalized.get("settings"), dict):
        normalized["settings"] = {}

    return normalized


# ============================================================
# COLLECTION
# ============================================================

def _ensure_collection(
    db: dict[str, Any],
    collection: str,
) -> list[dict[str, Any]]:
    """
    Ensure a collection exists and is a list.
    """

    if not isinstance(db, dict):
        raise TypeError(
            "Database must be a dictionary."
        )

    if not isinstance(collection, str) or not collection.strip():
        raise ValueError(
            "Collection name must be a non-empty string."
        )

    if collection not in db:
        db[collection] = []

    if not isinstance(db[collection], list):
        db[collection] = []

    return db[collection]


# ============================================================
# LOAD
# ============================================================

def load_memory() -> dict[str, Any]:
    """
    Load the JSON database safely.

    Missing database:
        Creates a new database.

    Corrupted database:
        Creates a backup and restores safe defaults.

    Unexpected read errors:
        Returns safe defaults instead of crashing startup.
    """

    try:
        DB_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not DB_FILE.exists():
            database = copy.deepcopy(
                DEFAULT_DATABASE
            )

            save_memory(database)

            return database

        with DB_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return _normalize_database(data)

    except json.JSONDecodeError:
        # Preserve corrupted file if possible.
        try:
            backup = DB_FILE.with_name(
                "creativestudios_db.corrupt.json"
            )

            if DB_FILE.exists():
                if backup.exists():
                    backup.unlink()

                DB_FILE.replace(backup)

        except Exception:
            pass

        database = copy.deepcopy(
            DEFAULT_DATABASE
        )

        try:
            save_memory(database)
        except Exception:
            pass

        return database

    except Exception:
        return copy.deepcopy(
            DEFAULT_DATABASE
        )


# ============================================================
# SAVE
# ============================================================

def save_memory(
    db: dict[str, Any],
) -> bool:
    """
    Atomically save the complete database.
    """

    database = _normalize_database(db)

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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

            os.fsync(
                temporary.fileno()
            )

            temporary_path = Path(
                temporary.name
            )

        os.replace(
            temporary_path,
            DB_FILE,
        )

        return True

    except Exception:

        if (
            temporary_path is not None
            and temporary_path.exists()
        ):
            try:
                temporary_path.unlink()
            except Exception:
                pass

        return False


# ============================================================
# INITIALIZE
# ============================================================

def initialize_database() -> dict[str, Any]:
    """
    Load and normalize the database.
    """

    db = load_memory()

    # Ensure all standard collections exist.
    _normalize_database(db)

    # Persist the normalized structure.
    save_memory(db)

    return db


# ============================================================
# NEXT ID
# ============================================================

def next_id(
    collection: str,
    db: dict[str, Any],
) -> int:
    """
    Return the next available numeric ID.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    highest = 0

    for record in records:

        if not isinstance(record, dict):
            continue

        value = record.get("id")

        try:
            numeric_value = int(value)

            if numeric_value > highest:
                highest = numeric_value

        except (
            TypeError,
            ValueError,
        ):
            continue

    return highest + 1


# ============================================================
# ADD
# ============================================================

def add_record(
    collection: str,
    record: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any]:
    """
    Add a new record.
    """

    if not isinstance(record, dict):
        raise TypeError(
            "Record must be a dictionary."
        )

    records = _ensure_collection(
        db,
        collection,
    )

    new_record = copy.deepcopy(record)

    if new_record.get("id") is None:
        new_record["id"] = next_id(
            collection,
            db,
        )

    records.append(new_record)

    if not save_memory(db):

        records.pop()

        raise IOError(
            "Unable to save the database."
        )

    return new_record


# ============================================================
# GET ONE
# ============================================================

def get_record(
    collection: str,
    record_id: Any,
    db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Find one record by ID.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    for record in records:

        if not isinstance(record, dict):
            continue

        if str(record.get("id")) == str(record_id):
            return record

    return None


# ============================================================
# GET ALL
# ============================================================

def get_records(
    collection: str,
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Return all dictionary records in a collection.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    return [
        record
        for record in records
        if isinstance(record, dict)
    ]


# ============================================================
# UPDATE
# ============================================================

def update_record(
    collection: str,
    record_id: Any,
    updates: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Update a record by ID.
    """

    if not isinstance(updates, dict):
        raise TypeError(
            "Updates must be a dictionary."
        )

    records = _ensure_collection(
        db,
        collection,
    )

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            continue

        if str(record.get("id")) != str(record_id):
            continue

        original = copy.deepcopy(record)

        updated = copy.deepcopy(record)

        updated.update(
            copy.deepcopy(updates)
        )

        # Prevent accidental ID changes.
        updated["id"] = record.get("id")

        records[index] = updated

        if not save_memory(db):

            records[index] = original

            raise IOError(
                "Unable to save the database."
            )

        return updated

    return None


# ============================================================
# DELETE
# ============================================================

def delete_record(
    collection: str,
    record_id: Any,
    db: dict[str, Any],
) -> bool:
    """
    Delete a record by ID.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            continue

        if str(record.get("id")) != str(record_id):
            continue

        deleted = records.pop(index)

        if not save_memory(db):

            records.insert(
                index,
                deleted,
            )

            raise IOError(
                "Unable to save the database."
            )

        return True

    return False


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def load_database() -> dict[str, Any]:
    return load_memory()


def save_database(
    db: dict[str, Any],
) -> bool:
    return save_memory(db)


def get_all(
    collection: str,
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    return get_records(
        collection,
        db,
    )