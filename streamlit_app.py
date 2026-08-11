"""
Creative Studios
Database Module

JSON-based persistence layer for the Creative Studios
AEC Collaboration Platform.

This module is intentionally lightweight and defensive so
the Streamlit application can start even if the database
file is missing, empty, malformed, or partially populated.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = (
    BASE_DIR / "creativestudios_db.json"
)


# ============================================================
# DEFAULT DATABASE
# ============================================================

DEFAULT_DATABASE = {

    "users": [
        {
            "id": 1,
            "username": "admin",
            "password": "admin123",
            "name": "System Administrator",
            "full_name": "System Administrator",
            "role": "Admin",
            "email": "admin@creativestudios.local",
            "active": True,
        }
    ],

    "projects": [
        {
            "id": "PRJ-001",
            "project_id": "PRJ-001",
            "name": "Grand Horizon Commercial Complex",
            "project_name": "Grand Horizon Commercial Complex",
            "type": "Commercial",
            "project_type": "Commercial",
            "status": "Active",
            "phase": "Design Development",
            "client": "Grand Horizon Developments",
            "client_name": "Grand Horizon Developments",
            "location": "Kampala, Uganda",
            "project_manager": "System Administrator",
            "manager": "System Administrator",
            "budget": 1250000,
            "estimated_budget": 1250000,
            "description": (
                "A commercial development project managed "
                "through the Creative Studios AEC "
                "collaboration platform."
            ),
        }
    ],

    "drawings": [],

    "approvals": [],

    "boq": [],

    "rfi": [],

    "site_logs": [],

    "documents": [],

    "notifications": [],

    "activity_logs": [],
}


# ============================================================
# REQUIRED COLLECTIONS
# ============================================================

REQUIRED_COLLECTIONS = [

    "users",
    "projects",
    "drawings",
    "approvals",
    "boq",
    "rfi",
    "site_logs",
    "documents",
    "notifications",
    "activity_logs",

]


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _new_default_database() -> dict[str, Any]:

    """
    Return a completely independent copy of the default
    database.
    """

    return deepcopy(
        DEFAULT_DATABASE
    )


def _normalise_database(
    data: Any,
) -> dict[str, Any]:

    """
    Make sure the loaded database always has the expected
    dictionary structure and collections.
    """

    if not isinstance(
        data,
        dict,
    ):

        data = _new_default_database()


    for collection in REQUIRED_COLLECTIONS:

        value = data.get(
            collection
        )


        if not isinstance(
            value,
            list,
        ):

            data[
                collection
            ] = []


    # --------------------------------------------------------
    # If there are no users, restore the default administrator.
    # --------------------------------------------------------

    if not data["users"]:

        data["users"] = deepcopy(
            DEFAULT_DATABASE["users"]
        )


    return data


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict[str, Any]:

    """
    Load the JSON database.

    If the file does not exist, it is created.

    If the file is invalid or unreadable, a safe default
    database is returned and an attempt is made to repair
    the file.
    """

    try:

        if not DATABASE_FILE.exists():

            data = _new_default_database()

            save_memory(
                data
            )

            return data


        raw = DATABASE_FILE.read_text(
            encoding="utf-8"
        ).strip()


        if not raw:

            data = _new_default_database()

            save_memory(
                data
            )

            return data


        data = json.loads(
            raw
        )


        data = _normalise_database(
            data
        )


        return data


    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
    ):

        data = _new_default_database()


        # ----------------------------------------------------
        # Try to repair an invalid database.
        # ----------------------------------------------------

        try:

            save_memory(
                data
            )

        except Exception:

            pass


        return data


# ============================================================
# SAVE DATABASE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:

    """
    Save the supplied database dictionary to JSON.

    Returns:
        True  -> saved successfully
        False -> save failed
    """

    try:

        data = _normalise_database(
            data
        )


        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        # ----------------------------------------------------
        # Write to a temporary file first.
        #
        # This prevents a failed write from leaving the main
        # JSON database partially corrupted.
        # ----------------------------------------------------

        temporary_file = DATABASE_FILE.with_suffix(
            ".tmp"
        )


        temporary_file.write_text(
            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


        temporary_file.replace(
            DATABASE_FILE
        )


        return True


    except (
        OSError,
        TypeError,
        ValueError,
    ):

        return False


# ============================================================
# RESET DATABASE
# ============================================================

def reset_database() -> dict[str, Any]:

    """
    Replace the current database with the default database.

    Returns the new database dictionary.
    """

    data = _new_default_database()


    save_memory(
        data
    )


    return data


# ============================================================
# GET COLLECTION
# ============================================================

def get_collection(
    data: dict[str, Any],
    collection: str,
) -> list:

    """
    Safely retrieve a collection from the database.

    Example:

        projects = get_collection(db, "projects")
    """

    if not isinstance(
        data,
        dict,
    ):

        return []


    value = data.get(
        collection,
        [],
    )


    if not isinstance(
        value,
        list,
    ):

        value = []

        data[
            collection
        ] = value


    return value


# ============================================================
# ADD RECORD
# ============================================================

def add_record(
    data: dict[str, Any],
    collection: str,
    record: dict[str, Any],
) -> dict[str, Any]:

    """
    Add a dictionary record to a collection.

    The updated record is returned.
    """

    if not isinstance(
        data,
        dict,
    ):

        raise TypeError(
            "Database must be a dictionary."
        )


    if not isinstance(
        record,
        dict,
    ):

        raise TypeError(
            "Record must be a dictionary."
        )


    records = get_collection(
        data,
        collection,
    )


    records.append(
        record
    )


    return record


# ============================================================
# FIND RECORD
# ============================================================

def find_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
):

    """
    Find the first record matching a field.

    Returns:
        record dictionary or None
    """

    records = get_collection(
        data,
        collection,
    )


    for record in records:

        if not isinstance(
            record,
            dict,
        ):

            continue


        if record.get(
            field
        ) == value:

            return record


    return None


# ============================================================
# FIND ALL RECORDS
# ============================================================

def find_records(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
) -> list[dict[str, Any]]:

    """
    Find all records matching a field.
    """

    records = get_collection(
        data,
        collection,
    )


    results = []


    for record in records:

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


    return results


# ============================================================
# DELETE RECORD
# ============================================================

def delete_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
) -> bool:

    """
    Delete the first record matching a field.

    Returns:
        True  -> record deleted
        False -> record not found
    """

    records = get_collection(
        data,
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


        if record.get(
            field
        ) == value:

            records.pop(
                index
            )

            return True


    return False


# ============================================================
# UPDATE RECORD
# ============================================================

def update_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
    updates: dict[str, Any],
) -> bool:

    """
    Update the first matching record.

    Returns:
        True  -> updated
        False -> not found
    """

    if not isinstance(
        updates,
        dict,
    ):

        return False


    record = find_record(
        data,
        collection,
        field,
        value,
    )


    if record is None:

        return False


    record.update(
        updates
    )


    return True


# ============================================================
# DATABASE STATUS
# ============================================================

def database_exists() -> bool:

    """
    Return True when the database file exists.
    """

    return DATABASE_FILE.exists()


def database_path() -> str:

    """
    Return the absolute database path.
    """

    return str(
        DATABASE_FILE
    )


# ============================================================
# OPTIONAL COMPATIBILITY ALIASES
# ============================================================

# Some older Creative Studios modules may use these names.

load_database = load_memory

save_database = save_memory

get_data = load_memory


# ============================================================
# STARTUP CHECK
# ============================================================

if __name__ == "__main__":

    database = load_memory()

    print(
        "Creative Studios database loaded."
    )

    print(
        f"Database: {DATABASE_FILE}"
    )

    print(
        f"Projects: "
        f"{len(database.get('projects', []))}"
    )

    print(
        f"Users: "
        f"{len(database.get('users', []))}"
    )