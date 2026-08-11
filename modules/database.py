"""
Creative Studios
JSON Database Module
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parent.parent

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
                "A commercial development project "
                "managed through the Creative Studios "
                "AEC collaboration platform."
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
# COLLECTIONS
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
# NORMALISE DATABASE
# ============================================================

def _normalise_database(
    data: Any,
) -> dict[str, Any]:

    if not isinstance(
        data,
        dict,
    ):

        data = deepcopy(
            DEFAULT_DATABASE
        )

    for collection in REQUIRED_COLLECTIONS:

        if not isinstance(
            data.get(
                collection
            ),
            list,
        ):

            data[
                collection
            ] = []

    # Always ensure an administrator exists.

    users = data.get(
        "users",
        [],
    )

    admin_exists = False

    for user in users:

        if not isinstance(
            user,
            dict,
        ):
            continue

        if str(
            user.get(
                "username",
                ""
            )
        ).lower() == "admin":

            admin_exists = True
            break

    if not admin_exists:

        users.insert(
            0,
            deepcopy(
                DEFAULT_DATABASE[
                    "users"
                ][0]
            ),
        )

    return data


# ============================================================
# LOAD
# ============================================================

def load_memory() -> dict[str, Any]:

    """
    Load the Creative Studios JSON database.

    Automatically creates or repairs the database when
    necessary.
    """

    try:

        if not DATABASE_FILE.exists():

            data = deepcopy(
                DEFAULT_DATABASE
            )

            save_memory(
                data
            )

            return data

        content = DATABASE_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if not content:

            data = deepcopy(
                DEFAULT_DATABASE
            )

            save_memory(
                data
            )

            return data

        data = json.loads(
            content
        )

        data = _normalise_database(
            data
        )

        return data

    except (
        OSError,
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):

        data = deepcopy(
            DEFAULT_DATABASE
        )

        try:

            save_memory(
                data
            )

        except Exception:

            pass

        return data


# ============================================================
# SAVE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:

    """
    Save database safely.

    Returns True when successful.
    """

    try:

        data = _normalise_database(
            data
        )

        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

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
# RESET
# ============================================================

def reset_database() -> dict[str, Any]:

    data = deepcopy(
        DEFAULT_DATABASE
    )

    save_memory(
        data
    )

    return data


# ============================================================
# COLLECTION
# ============================================================

def get_collection(
    data: dict[str, Any],
    collection: str,
) -> list:

    if not isinstance(
        data,
        dict,
    ):

        return []

    if not isinstance(
        data.get(
            collection
        ),
        list,
    ):

        data[
            collection
        ] = []

    return data[
        collection
    ]


# ============================================================
# FIND
# ============================================================

def find_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
):

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
# ADD
# ============================================================

def add_record(
    data: dict[str, Any],
    collection: str,
    record: dict[str, Any],
) -> dict[str, Any]:

    records = get_collection(
        data,
        collection,
    )

    records.append(
        record
    )

    return record


# ============================================================
# UPDATE
# ============================================================

def update_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
    updates: dict[str, Any],
) -> bool:

    record = find_record(
        data,
        collection,
        field,
        value,
    )

    if record is None:
        return False

    if not isinstance(
        updates,
        dict,
    ):
        return False

    record.update(
        updates
    )

    return True


# ============================================================
# DELETE
# ============================================================

def delete_record(
    data: dict[str, Any],
    collection: str,
    field: str,
    value: Any,
) -> bool:

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
# COMPATIBILITY ALIASES
# ============================================================

load_database = load_memory

save_database = save_memory

get_data = load_memory


# ============================================================
# DATABASE INFORMATION
# ============================================================

def database_exists() -> bool:

    return DATABASE_FILE.exists()


def database_path() -> str:

    return str(
        DATABASE_FILE
    )