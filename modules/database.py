"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

JSON Database Layer

File:
    modules/database.py

Purpose:
    Reliable JSON-backed storage for the Creative Studios app.

Database:
    creativestudios_db.json

This module intentionally does NOT import Streamlit.

The application can safely use:

    from modules.database import load_memory

    db = load_memory()

and:

    from modules.database import save_memory

    save_memory(db)
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

MODULE_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = MODULE_DIR.parent

DATABASE_FILE = PROJECT_ROOT / "creativestudios_db.json"

BACKUP_DIR = PROJECT_ROOT / "database_backups"


# ============================================================
# DATABASE VERSION
# ============================================================

DATABASE_VERSION = 1


# ============================================================
# SAFE DEFAULT DATABASE
# ============================================================

DEFAULT_DATABASE: dict[str, Any] = {
    "database_version": DATABASE_VERSION,

    "users": [],

    "projects": [],

    "drawings": [],

    "documents": [],

    "approvals": [],

    "boq": [],

    "rfis": [],

    "site_logs": [],

    "team": [],

    "clients": [],

    "companies": [],

    "contacts": [],

    "contracts": [],

    "tasks": [],

    "meetings": [],

    "submittals": [],

    "issues": [],

    "change_orders": [],

    "invoices": [],

    "payments": [],

    "notifications": [],

    "activity_log": [],
}


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "DATABASE_FILE",
    "BACKUP_DIR",
    "DEFAULT_DATABASE",
    "load_memory",
    "save_memory",
    "ensure_database",
    "reset_database",
    "get_collection",
    "set_collection",
    "add_record",
    "update_record",
    "delete_record",
    "find_by_id",
    "find_one",
    "find_many",
    "count_records",
    "next_id",
    "database_exists",
    "backup_database",
]


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _deepcopy_default_database() -> dict[str, Any]:
    """
    Return an independent copy of the default database.
    """

    return copy.deepcopy(
        DEFAULT_DATABASE
    )


def _json_default(value: Any) -> Any:
    """
    Convert common Python values into JSON-safe values.
    """

    if isinstance(
        value,
        datetime,
    ):

        return value.isoformat()


    if isinstance(
        value,
        date,
    ):

        return value.isoformat()


    if isinstance(
        value,
        Path,
    ):

        return str(value)


    if hasattr(
        value,
        "isoformat",
    ):

        try:

            return value.isoformat()

        except Exception:
            pass


    return str(value)


def _normalize_id(value: Any) -> Any:
    """
    Normalize IDs without forcing everything into strings.
    """

    if value is None:
        return None


    if isinstance(
        value,
        bool,
    ):

        return int(value)


    if isinstance(
        value,
        int,
    ):

        return value


    if isinstance(
        value,
        float,
    ):

        if value.is_integer():
            return int(value)

        return value


    return str(value)


def _record_matches_id(
    record: Any,
    record_id: Any,
) -> bool:
    """
    Safely compare a record's ID.
    """

    if not isinstance(
        record,
        dict,
    ):

        return False


    stored_id = record.get(
        "id"
    )


    if stored_id == record_id:
        return True


    return (
        str(stored_id)
        == str(record_id)
    )


# ============================================================
# DATABASE NORMALIZATION
# ============================================================

def normalize_database(
    data: Any,
) -> dict[str, Any]:
    """
    Normalize arbitrary loaded JSON into the expected
    Creative Studios database structure.

    Invalid top-level data is replaced by safe defaults.
    Missing collections are created.
    Invalid collections are replaced with empty lists.
    """

    if not isinstance(
        data,
        dict,
    ):

        data = _deepcopy_default_database()


    normalized = copy.deepcopy(
        data
    )


    # --------------------------------------------------------
    # Database version
    # --------------------------------------------------------

    normalized.setdefault(
        "database_version",
        DATABASE_VERSION,
    )


    # --------------------------------------------------------
    # Collections
    # --------------------------------------------------------

    for key, default_value in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue


        if key not in normalized:

            normalized[key] = copy.deepcopy(
                default_value
            )


        elif not isinstance(
            normalized[key],
            list,
        ):

            normalized[key] = []


    return normalized


# ============================================================
# DATABASE EXISTENCE
# ============================================================

def database_exists() -> bool:
    """
    Return True when the JSON database exists.
    """

    try:

        return (
            DATABASE_FILE.exists()
            and DATABASE_FILE.is_file()
        )

    except OSError:

        return False


# ============================================================
# BACKUP
# ============================================================

def backup_database(
    source: Path | None = None,
) -> Path | None:
    """
    Create a timestamped backup of the current database.

    Returns:
        Path to backup file, or None if no backup was possible.
    """

    source = (
        source
        or DATABASE_FILE
    )


    try:

        if not source.exists():
            return None


        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )


        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )


        backup_path = (
            BACKUP_DIR
            / f"creativestudios_db_{timestamp}.json"
        )


        shutil.copy2(
            source,
            backup_path,
        )


        return backup_path

    except (
        OSError,
        shutil.Error,
    ):

        return None


# ============================================================
# LOAD
# ============================================================

def load_memory(
    create_if_missing: bool = True,
) -> dict[str, Any]:
    """
    Load the Creative Studios JSON database.

    Parameters
    ----------
    create_if_missing:
        Create the database automatically when it doesn't exist.

    Returns
    -------
    dict
        Normalized database dictionary.

    Recovery
    --------
    If the JSON file is malformed:

        1. A backup is attempted.
        2. Safe default data is created.
        3. The application continues instead of crashing.
    """

    # --------------------------------------------------------
    # Database does not exist
    # --------------------------------------------------------

    if not database_exists():

        data = _deepcopy_default_database()


        if create_if_missing:

            save_memory(
                data
            )


        return data


    # --------------------------------------------------------
    # Read database
    # --------------------------------------------------------

    try:

        with DATABASE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            raw_data = json.load(
                file
            )


    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError,
        ValueError,
    ):

        # ----------------------------------------------------
        # Corrupt database recovery
        # ----------------------------------------------------

        backup_database()


        data = _deepcopy_default_database()


        if create_if_missing:

            save_memory(
                data
            )


        return data


    # --------------------------------------------------------
    # Normalize
    # --------------------------------------------------------

    data = normalize_database(
        raw_data
    )


    # --------------------------------------------------------
    # Repair missing structure on disk
    # --------------------------------------------------------

    if create_if_missing:

        try:

            save_memory(
                data
            )

        except Exception:
            # Loading should still succeed even if the
            # environment temporarily prevents writing.
            pass


    return data


# ============================================================
# SAVE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:
    """
    Safely save the complete database.

    Uses a temporary file in the same directory and then
    replaces the destination file.

    Returns:
        True when saved successfully.
        False when saving failed.
    """

    if not isinstance(
        data,
        dict,
    ):

        return False


    normalized = normalize_database(
        data
    )


    normalized[
        "database_version"
    ] = DATABASE_VERSION


    temp_path: Path | None = None


    try:

        PROJECT_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )


        # ----------------------------------------------------
        # Create temporary file in the same directory.
        #
        # This keeps os.replace() on the same filesystem.
        # ----------------------------------------------------

        fd, temp_name = tempfile.mkstemp(
            prefix=".creativestudios_db_",
            suffix=".tmp",
            dir=str(PROJECT_ROOT),
        )


        temp_path = Path(
            temp_name
        )


        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                normalized,
                file,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            )


            file.write(
                "\n"
            )


            file.flush()


            try:

                os.fsync(
                    file.fileno()
                )

            except OSError:
                pass


        # ----------------------------------------------------
        # Atomic replacement
        # ----------------------------------------------------

        os.replace(
            temp_path,
            DATABASE_FILE,
        )


        temp_path = None


        return True


    except (
        OSError,
        TypeError,
        ValueError,
        OverflowError,
    ):

        return False


    finally:

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            try:

                temp_path.unlink()

            except OSError:

                pass


# ============================================================
# ENSURE DATABASE
# ============================================================

def ensure_database() -> dict[str, Any]:
    """
    Ensure that the database exists and has the correct
    top-level collections.

    Returns:
        Current normalized database.
    """

    data = load_memory(
        create_if_missing=True
    )


    changed = False


    for key, default_value in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue


        if key not in data:

            data[key] = copy.deepcopy(
                default_value
            )

            changed = True


        elif not isinstance(
            data[key],
            list,
        ):

            data[key] = []

            changed = True


    if (
        data.get(
            "database_version"
        )
        != DATABASE_VERSION
    ):

        data[
            "database_version"
        ] = DATABASE_VERSION

        changed = True


    if changed:

        save_memory(
            data
        )


    return data


# ============================================================
# RESET DATABASE
# ============================================================

def reset_database(
    backup: bool = True,
) -> dict[str, Any]:
    """
    Reset the database to safe defaults.

    Parameters
    ----------
    backup:
        If True, back up the current database before resetting.

    Returns
    -------
    dict
        Fresh database.
    """

    if (
        backup
        and database_exists()
    ):

        backup_database()


    data = _deepcopy_default_database()


    save_memory(
        data
    )


    return data


# ============================================================
# COLLECTION ACCESS
# ============================================================

def get_collection(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Return a database collection safely.

    Example:

        projects = get_collection(
            "projects"
        )
    """

    if not collection_name:

        return []


    if data is None:

        data = load_memory()


    if not isinstance(
        data,
        dict,
    ):

        return []


    collection = data.get(
        collection_name,
        [],
    )


    if not isinstance(
        collection,
        list,
    ):

        return []


    return collection


def set_collection(
    collection_name: str,
    records: list[Any],
    data: dict[str, Any] | None = None,
    save: bool = True,
) -> dict[str, Any]:
    """
    Replace a collection.

    Returns the modified database.
    """

    if data is None:

        data = load_memory()


    if not isinstance(
        records,
        list,
    ):

        records = []


    data[
        collection_name
    ] = records


    if save:

        save_memory(
            data
        )


    return data


# ============================================================
# ID GENERATION
# ============================================================

def next_id(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> int:
    """
    Return the next numeric ID for a collection.

    Example:

        project_id = next_id("projects")
    """

    records = get_collection(
        collection_name,
        data,
    )


    highest_id = 0


    for record in records:

        if not isinstance(
            record,
            dict,
        ):

            continue


        value = record.get(
            "id"
        )


        try:

            numeric_id = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            continue


        if numeric_id > highest_id:

            highest_id = numeric_id


    return highest_id + 1


# ============================================================
# ADD RECORD
# ============================================================

def add_record(
    collection_name: str,
    record: dict[str, Any],
    data: dict[str, Any] | None = None,
    save: bool = True,
) -> dict[str, Any]:
    """
    Add a record to a collection.

    An ID is automatically generated if the record does not
    already have one.

    Returns:
        The record that was added.
    """

    if data is None:

        data = load_memory()


    collection = get_collection(
        collection_name,
        data,
    )


    if not isinstance(
        record,
        dict,
    ):

        raise TypeError(
            "record must be a dictionary"
        )


    new_record = copy.deepcopy(
        record
    )


    if (
        "id" not in new_record
        or new_record.get("id") is None
    ):

        new_record[
            "id"
        ] = next_id(
            collection_name,
            data,
        )


    collection.append(
        new_record
    )


    data[
        collection_name
    ] = collection


    if save:

        save_memory(
            data
        )


    return new_record


# ============================================================
# UPDATE RECORD
# ============================================================

def update_record(
    collection_name: str,
    record_id: Any,
    updates: dict[str, Any],
    data: dict[str, Any] | None = None,
    save: bool = True,
) -> dict[str, Any] | None:
    """
    Update a record by ID.

    Returns:
        Updated record or None if not found.
    """

    if data is None:

        data = load_memory()


    if not isinstance(
        updates,
        dict,
    ):

        raise TypeError(
            "updates must be a dictionary"
        )


    collection = get_collection(
        collection_name,
        data,
    )


    for index, record in enumerate(
        collection
    ):

        if not _record_matches_id(
            record,
            record_id,
        ):

            continue


        updated = copy.deepcopy(
            record
        )


        updated.update(
            copy.deepcopy(
                updates
            )
        )


        # ID must not accidentally change.
        updated[
            "id"
        ] = record.get(
            "id"
        )


        collection[index] = updated


        data[
            collection_name
        ] = collection


        if save:

            save_memory(
                data
            )


        return updated


    return None


# ============================================================
# DELETE RECORD
# ============================================================

def delete_record(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
    save: bool = True,
) -> bool:
    """
    Delete a record by ID.

    Returns:
        True if deleted.
        False if not found.
    """

    if data is None:

        data = load_memory()


    collection = get_collection(
        collection_name,
        data,
    )


    for index, record in enumerate(
        collection
    ):

        if not _record_matches_id(
            record,
            record_id,
        ):

            continue


        del collection[index]


        data[
            collection_name
        ] = collection


        if save:

            save_memory(
                data
            )


        return True


    return False


# ============================================================
# FIND BY ID
# ============================================================

def find_by_id(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    Find one record by ID.
    """

    collection = get_collection(
        collection_name,
        data,
    )


    for record in collection:

        if _record_matches_id(
            record,
            record_id,
        ):

            return record


    return None


# ============================================================
# FIND ONE
# ============================================================

def find_one(
    collection_name: str,
    field: str,
    value: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """
    Find the first record matching field=value.
    """

    collection = get_collection(
        collection_name,
        data,
    )


    for record in collection:

        if not isinstance(
            record,
            dict,
        ):

            continue


        if record.get(
            field
        ) == value:

            return record


        # Helpful fallback for IDs and text fields.
        if (
            record.get(field) is not None
            and str(
                record.get(field)
            )
            == str(value)
        ):

            return record


    return None


# ============================================================
# FIND MANY
# ============================================================

def find_many(
    collection_name: str,
    field: str | None = None,
    value: Any = None,
    data: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Find all records matching an optional condition.

    Without field/value, returns all records.
    """

    collection = get_collection(
        collection_name,
        data,
    )


    if field is None:

        return list(
            collection
        )


    results: list[dict[str, Any]] = []


    for record in collection:

        if not isinstance(
            record,
            dict,
        ):

            continue


        if record.get(
            field
        ) == value:

            results.append(
                record
            )

            continue


        if (
            record.get(field) is not None
            and str(
                record.get(field)
            )
            == str(value)
        ):

            results.append(
                record
            )


    return results


# ============================================================
# COUNT
# ============================================================

def count_records(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> int:
    """
    Return the number of records in a collection.
    """

    return len(
        get_collection(
            collection_name,
            data,
        )
    )


# ============================================================
# OPTIONAL COMPATIBILITY ALIASES
# ============================================================

def load_database() -> dict[str, Any]:
    """
    Compatibility alias.
    """

    return load_memory()


def save_database(
    data: dict[str, Any],
) -> bool:
    """
    Compatibility alias.
    """

    return save_memory(
        data
    )


def get_db() -> dict[str, Any]:
    """
    Compatibility alias.
    """

    return load_memory()


# ============================================================
# INITIAL DATABASE CREATION
# ============================================================

if __name__ == "__main__":

    database = ensure_database()

    print(
        "Creative Studios JSON database"
    )

    print(
        f"Location: {DATABASE_FILE}"
    )

    print(
        f"Projects: {len(database.get('projects', []))}"
    )

    print(
        f"Users: {len(database.get('users', []))}"
    )