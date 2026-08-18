"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

JSON Database Layer
-------------------
Single, reliable JSON-backed database contract.

Public API:
    load_memory()
    save_memory(db)
    initialize_database()

    add_record()
    get_record()
    get_records()
    update_record()
    delete_record()
    next_id()

Compatibility:
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
# DATABASE PATH
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
    "approvals": [],
    "boq": [],
    "site_logs": [],
    "settings": {},
}


# ============================================================
# JSON SERIALIZATION
# ============================================================

def _json_default(value: Any) -> str:
    """Convert common Python objects into JSON-safe values."""

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    return str(value)


# ============================================================
# DATABASE NORMALIZATION
# ============================================================

def _normalize_database(
    data: Any,
) -> dict[str, Any]:
    """
    Guarantee that the database always has the expected
    collections and data types.
    """

    if not isinstance(data, dict):
        data = {}

    database = copy.deepcopy(
        DEFAULT_DATABASE
    )

    # Preserve existing/custom collections.
    for key, value in data.items():
        database[key] = value

    collections = [
        "users",
        "projects",
        "documents",
        "drawings",
        "rfis",
        "tasks",
        "teams",
        "approvals",
        "boq",
        "site_logs",
    ]

    for collection in collections:

        if not isinstance(
            database.get(collection),
            list,
        ):
            database[collection] = []

    if not isinstance(
        database.get("settings"),
        dict,
    ):
        database["settings"] = {}

    return database


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict[str, Any]:
    """
    Load the JSON database.

    Missing database:
        Creates a clean database.

    Corrupt database:
        Attempts to preserve the corrupt file and creates
        a clean database.

    Other read errors:
        Returns safe defaults instead of crashing the app.
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

            raw_data = json.load(file)

        return _normalize_database(
            raw_data
        )

    except json.JSONDecodeError:

        # Preserve corrupt database.
        try:

            if DB_FILE.exists():

                backup_path = (
                    DB_FILE.with_name(
                        "creativestudios_db.corrupt.json"
                    )
                )

                # Avoid overwriting an existing backup.
                if backup_path.exists():

                    backup_path = (
                        DB_FILE.with_name(
                            "creativestudios_db.corrupt.backup.json"
                        )
                    )

                DB_FILE.replace(
                    backup_path
                )

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
# SAVE DATABASE
# ============================================================

def save_memory(
    db: dict[str, Any],
) -> bool:
    """
    Safely save the database using an atomic file replacement.
    """

    database = _normalize_database(
        db
    )

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

            try:
                os.fsync(
                    temporary.fileno()
                )
            except OSError:
                pass

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
    Load, normalize and persist the database.
    """

    database = load_memory()

    save_memory(
        database
    )

    return database


# ============================================================
# COLLECTION HELPER
# ============================================================

def _ensure_collection(
    db: dict[str, Any],
    collection: str,
) -> list[dict[str, Any]]:
    """
    Return a valid collection.
    """

    if not isinstance(
        db,
        dict,
    ):
        raise TypeError(
            "Database must be a dictionary."
        )

    if not isinstance(
        collection,
        str,
    ) or not collection.strip():

        raise ValueError(
            "Collection name is required."
        )

    if collection not in db:

        db[collection] = []

    if not isinstance(
        db[collection],
        list,
    ):

        db[collection] = []

    return db[collection]


# ============================================================
# NEXT ID
# ============================================================

def next_id(
    collection: str,
    db: dict[str, Any],
) -> int:
    """
    Return the next numeric ID for a collection.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    highest = 0

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            continue

        try:

            value = int(
                record.get(
                    "id",
                    0,
                )
            )

            if value > highest:
                highest = value

        except (
            TypeError,
            ValueError,
        ):

            continue

    return highest + 1


# ============================================================
# ADD RECORD
# ============================================================

def add_record(
    collection: str,
    record: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any]:
    """
    Add a record to a collection.
    """

    if not isinstance(
        record,
        dict,
    ):
        raise TypeError(
            "Record must be a dictionary."
        )

    records = _ensure_collection(
        db,
        collection,
    )

    new_record = copy.deepcopy(
        record
    )

    if new_record.get("id") is None:

        new_record["id"] = next_id(
            collection,
            db,
        )

    records.append(
        new_record
    )

    if not save_memory(db):

        records.pop()

        raise IOError(
            "Unable to save database."
        )

    return new_record


# ============================================================
# GET ONE RECORD
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

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get("id")
        ) == str(record_id):

            return record

    return None


# ============================================================
# GET ALL RECORDS
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
        if isinstance(
            record,
            dict,
        )
    ]


# ============================================================
# UPDATE RECORD
# ============================================================

def update_record(
    collection: str,
    record_id: Any,
    updates: dict[str, Any],
    db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Update an existing record.
    """

    if not isinstance(
        updates,
        dict,
    ):
        raise TypeError(
            "Updates must be a dictionary."
        )

    records = _ensure_collection(
        db,
        collection,
    )

    for index, record in enumerate(
        records
    ):

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get("id")
        ) != str(record_id):

            continue

        original = copy.deepcopy(
            record
        )

        updated = copy.deepcopy(
            record
        )

        updated.update(
            copy.deepcopy(
                updates
            )
        )

        records[index] = updated

        if not save_memory(db):

            records[index] = original

            raise IOError(
                "Unable to save database."
            )

        return updated

    return None


# ============================================================
# DELETE RECORD
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

    for index, record in enumerate(
        records
    ):

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get("id")
        ) != str(record_id):

            continue

        deleted = records.pop(
            index
        )

        if not save_memory(db):

            records.insert(
                index,
                deleted,
            )

            raise IOError(
                "Unable to save database."
            )

        return True

    return False


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def load_database() -> dict[str, Any]:
    """Compatibility alias for load_memory()."""

    return load_memory()


def save_database(
    db: dict[str, Any],
) -> bool:
    """Compatibility alias for save_memory()."""

    return save_memory(
        db
    )


def get_all(
    collection: str,
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compatibility alias for get_records()."""

    return get_records(
        collection,
        db,
    )