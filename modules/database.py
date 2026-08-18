"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

JSON Database Layer
===================

Reliable JSON-backed storage for the Creative Studios
Streamlit application.

Public contract
---------------

    load_memory()
    save_memory(db)
    initialize_database()

    add_record(collection, record, db)
    update_record(collection, record_id, updates, db)
    delete_record(collection, record_id, db)

    get_record(collection, record_id, db)
    get_records(collection, db)
    get_all(collection, db)

    next_id(collection, db)

    authenticate_user(username, password, db)
"""

from __future__ import annotations

import copy
import hashlib
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


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _copy_defaults() -> dict[str, Any]:
    """Return a completely independent default database."""

    return copy.deepcopy(DEFAULT_DATABASE)


def _json_default(value: Any) -> str:
    """Convert common Python values into JSON-safe values."""

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    return str(value)


def _password_hash(password: str) -> str:
    """
    Create a deterministic SHA-256 password hash.

    This keeps the JSON database compatible with simple
    deployments while avoiding storing the password in
    plaintext.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def _ensure_collection(
    db: dict[str, Any],
    collection: str,
) -> list[dict[str, Any]]:
    """Return a valid list collection."""

    if not isinstance(db, dict):
        raise TypeError(
            "Database must be a dictionary."
        )

    if not isinstance(collection, str):
        raise TypeError(
            "Collection name must be a string."
        )

    collection = collection.strip()

    if not collection:
        raise ValueError(
            "Collection name cannot be empty."
        )

    if collection not in db:
        db[collection] = []

    if not isinstance(db[collection], list):
        db[collection] = []

    return db[collection]


# ============================================================
# NORMALIZATION
# ============================================================

def _normalize_database(
    data: Any,
) -> dict[str, Any]:
    """
    Normalize arbitrary JSON data into the expected
    Creative Studios database structure.
    """

    if not isinstance(data, dict):
        data = {}

    normalized = _copy_defaults()

    for key, value in data.items():
        normalized[key] = value

    list_collections = [
        "users",
        "projects",
        "documents",
        "drawings",
        "rfis",
        "tasks",
        "teams",
    ]

    for collection in list_collections:

        if not isinstance(
            normalized.get(collection),
            list,
        ):
            normalized[collection] = []

    if not isinstance(
        normalized.get("settings"),
        dict,
    ):
        normalized["settings"] = {}

    return normalized


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict[str, Any]:
    """
    Load the JSON database.

    Missing database:
        Creates a safe database.

    Corrupt database:
        Creates a backup and restores safe defaults.

    Unexpected read errors:
        Returns safe defaults rather than crashing the app.
    """

    try:

        DB_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not DB_FILE.exists():

            database = _copy_defaults()

            # Do not let first-run persistence prevent
            # the application from starting.
            try:
                save_memory(database)
            except Exception:
                pass

            return database

        with DB_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return _normalize_database(data)

    except json.JSONDecodeError:

        # Preserve corrupted database if possible.
        try:

            backup_path = DB_FILE.with_name(
                "creativestudios_db.corrupt.json"
            )

            if DB_FILE.exists():

                # Remove an older corruption backup first.
                if backup_path.exists():

                    try:
                        backup_path.unlink()
                    except Exception:
                        pass

                DB_FILE.replace(
                    backup_path
                )

        except Exception:
            pass

        database = _copy_defaults()

        try:
            save_memory(database)
        except Exception:
            pass

        return database

    except Exception:

        return _copy_defaults()


# ============================================================
# SAVE DATABASE
# ============================================================

def save_memory(
    db: dict[str, Any],
) -> bool:
    """
    Atomically save the complete database.

    Returns:
        True  = successful
        False = failed
    """

    if not isinstance(db, dict):
        return False

    database = _normalize_database(db)

    temporary_path: Path | None = None

    try:

        DB_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
            except Exception:
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
# INITIALIZATION
# ============================================================

def initialize_database() -> dict[str, Any]:
    """
    Load and normalize the database.

    Also ensures that a default administrator account exists.
    """

    db = load_memory()

    users = _ensure_collection(
        db,
        "users",
    )

    # --------------------------------------------------------
    # Default administrator
    # --------------------------------------------------------

    admin_exists = False

    for user in users:

        if not isinstance(user, dict):
            continue

        if str(
            user.get("username", "")
        ).strip().lower() == "admin":

            admin_exists = True
            break

    if not admin_exists:

        users.append(
            {
                "id": next_id(
                    "users",
                    db,
                ),
                "username": "admin",
                "password_hash": _password_hash(
                    "admin"
                ),
                "full_name": "System Administrator",
                "email": "",
                "role": "Admin",
                "active": True,
                "created_at": datetime.now().isoformat(),
            }
        )

    save_memory(db)

    return db


# ============================================================
# NEXT ID
# ============================================================

def next_id(
    collection: str,
    db: dict[str, Any],
) -> int:
    """Return the next numeric ID."""

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

            number = int(value)

            if number > highest:
                highest = number

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
    Add a record.

    Returns the inserted record.

    Raises:
        TypeError
        IOError
    """

    if not isinstance(record, dict):
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
            "Unable to save the database."
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
    """Find one record by ID."""

    records = _ensure_collection(
        db,
        collection,
    )

    for record in records:

        if not isinstance(record, dict):
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
    """Return all valid dictionary records."""

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

    Returns the updated record.

    Returns None when the record does not exist.
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

        # Never allow the update payload to change
        # the identity of the record.
        updated["id"] = record.get(
            "id"
        )

        records[index] = updated

        if not save_memory(db):

            records[index] = original

            raise IOError(
                "Unable to save the database."
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
    Delete a record.

    Returns True when deleted.
    """

    records = _ensure_collection(
        db,
        collection,
    )

    for index, record in enumerate(records):

        if not isinstance(record, dict):
            continue

        if str(
            record.get("id")
        ) != str(record_id):
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
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user against the JSON database.

    Supported password formats:

        password_hash
        password

    The legacy plaintext format is supported for compatibility,
    while new/default accounts use password_hash.
    """

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:
        return None

    users = _ensure_collection(
        db,
        "users",
    )

    password_hash = _password_hash(
        password
    )

    for user in users:

        if not isinstance(user, dict):
            continue

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        if stored_username.lower() != username.lower():
            continue

        active = user.get(
            "active",
            True,
        )

        if active is False:
            return None

        stored_hash = user.get(
            "password_hash"
        )

        stored_password = user.get(
            "password"
        )

        valid = False

        if stored_hash:

            valid = (
                str(stored_hash)
                == password_hash
            )

        elif stored_password is not None:

            valid = (
                str(stored_password)
                == password
            )

        if not valid:
            return None

        # Return a copy so UI code cannot accidentally mutate
        # the database record.
        authenticated_user = copy.deepcopy(
            user
        )

        authenticated_user.pop(
            "password",
            None,
        )

        authenticated_user.pop(
            "password_hash",
            None,
        )

        return authenticated_user

    return None


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

    return save_memory(db)


def get_all(
    collection: str,
    db: dict[str, Any],
) -> list[dict[str, Any]]:
    """Compatibility alias for get_records()."""

    return get_records(
        collection,
        db,
    )


# ============================================================
# PUBLIC EXPORTS
# ============================================================

__all__ = [
    "DB_FILE",
    "DEFAULT_DATABASE",
    "load_memory",
    "save_memory",
    "initialize_database",
    "add_record",
    "update_record",
    "delete_record",
    "get_record",
    "get_records",
    "get_all",
    "next_id",
    "authenticate_user",
    "load_database",
    "save_database",
]