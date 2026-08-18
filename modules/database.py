"""
Creative Studios
AEC Workspace
JSON database layer.

This module intentionally has NO Streamlit dependency.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_FILE = BASE_DIR / "creativestudios_db.json"


# ============================================================
# DEFAULT DATABASE
# ============================================================

DEFAULT_DATABASE: dict[str, Any] = {
    "database_version": 1,

    "users": [],

    "projects": [],
    "clients": [],
    "companies": [],
    "contacts": [],
    "team": [],

    "documents": [],
    "drawings": [],
    "approvals": [],

    "boq": [],
    "rfis": [],
    "site_logs": [],
    "tasks": [],

    "meetings": [],
    "submittals": [],
    "issues": [],
    "change_orders": [],

    "contracts": [],
    "invoices": [],
    "payments": [],

    "notifications": [],
    "activity_log": [],
}


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _new_database() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_DATABASE)


def _normalize(data: Any) -> dict[str, Any]:

    if not isinstance(data, dict):
        data = {}

    result = copy.deepcopy(data)

    result.setdefault(
        "database_version",
        1,
    )

    for key, default in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue

        if key not in result:
            result[key] = copy.deepcopy(default)

        elif not isinstance(result[key], list):
            result[key] = []

    return result


def _json_default(value: Any) -> str:

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Path):
        return str(value)

    if hasattr(value, "isoformat"):

        try:
            return value.isoformat()
        except Exception:
            pass

    return str(value)


# ============================================================
# LOAD
# ============================================================

def load_memory() -> dict[str, Any]:

    if not DATABASE_FILE.exists():

        data = _new_database()

        save_memory(data)

        return data

    try:

        with DATABASE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return _normalize(data)

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        data = _new_database()

        save_memory(data)

        return data


# ============================================================
# SAVE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:

    data = _normalize(data)

    temporary_file = None

    try:

        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fd, temporary_name = tempfile.mkstemp(
            prefix="creativestudios_",
            suffix=".tmp",
            dir=str(DATABASE_FILE.parent),
        )

        temporary_file = Path(
            temporary_name
        )

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=_json_default,
            )

            file.write("\n")

            file.flush()

            try:
                os.fsync(file.fileno())
            except OSError:
                pass

        os.replace(
            temporary_file,
            DATABASE_FILE,
        )

        temporary_file = None

        return True

    except (
        OSError,
        TypeError,
        ValueError,
    ):

        return False

    finally:

        if (
            temporary_file is not None
            and temporary_file.exists()
        ):

            try:
                temporary_file.unlink()
            except OSError:
                pass


# ============================================================
# COMPATIBILITY FUNCTIONS
# ============================================================

def load_database() -> dict[str, Any]:
    return load_memory()


def save_database(
    data: dict[str, Any],
) -> bool:
    return save_memory(data)


def get_db() -> dict[str, Any]:
    return load_memory()


def ensure_database() -> dict[str, Any]:
    return load_memory()


# ============================================================
# COLLECTIONS
# ============================================================

def get_collection(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> list:

    if data is None:
        data = load_memory()

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


def next_id(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> int:

    records = get_collection(
        collection_name,
        data,
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

            highest = max(
                highest,
                value,
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

    return highest + 1


# ============================================================
# RECORD CRUD
# ============================================================

def add_record(
    collection_name: str,
    record: dict[str, Any],
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if data is None:
        data = load_memory()

    if not isinstance(
        record,
        dict,
    ):
        raise TypeError(
            "record must be a dictionary"
        )

    new_record = copy.deepcopy(record)

    if new_record.get("id") is None:

        new_record["id"] = next_id(
            collection_name,
            data,
        )

    collection = get_collection(
        collection_name,
        data,
    )

    collection.append(
        new_record
    )

    data[
        collection_name
    ] = collection

    save_memory(data)

    return new_record


def update_record(
    collection_name: str,
    record_id: Any,
    updates: dict[str, Any],
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    if data is None:
        data = load_memory()

    collection = get_collection(
        collection_name,
        data,
    )

    for index, record in enumerate(
        collection
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

        updated = copy.deepcopy(
            record
        )

        updated.update(
            copy.deepcopy(
                updates
            )
        )

        updated["id"] = record.get(
            "id"
        )

        collection[index] = updated

        data[
            collection_name
        ] = collection

        save_memory(data)

        return updated

    return None


def delete_record(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
) -> bool:

    if data is None:
        data = load_memory()

    collection = get_collection(
        collection_name,
        data,
    )

    for index, record in enumerate(
        collection
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

        collection.pop(index)

        data[
            collection_name
        ] = collection

        save_memory(data)

        return True

    return False


def find_by_id(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    for record in get_collection(
        collection_name,
        data,
    ):

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


def find_one(
    collection_name: str,
    field: str,
    value: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    for record in get_collection(
        collection_name,
        data,
    ):

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get(field, "")
        ).lower() == str(
            value
        ).lower():

            return record

    return None


# ============================================================
# PASSWORDS
# ============================================================

def hash_password(
    password: str,
) -> str:

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    if not password_hash:
        return False

    return hash_password(
        password
    ) == password_hash


# ============================================================
# ADMIN USER
# ============================================================

def ensure_admin_user(
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:

    if data is None:
        data = load_memory()

    users = get_collection(
        "users",
        data,
    )

    for user in users:

        if str(
            user.get(
                "username",
                "",
            )
        ).lower() == "admin":

            changed = False

            if "active" not in user:
                user["active"] = True
                changed = True

            if "role" not in user:
                user["role"] = "Admin"
                changed = True

            if "full_name" not in user:
                user[
                    "full_name"
                ] = "System Administrator"
                changed = True

            if changed:
                save_memory(data)

            return user

    admin = {
        "id": next_id(
            "users",
            data,
        ),
        "username": "admin",
        "full_name": "System Administrator",
        "email": "admin@creativestudios.local",
        "password_hash": hash_password(
            "admin"
        ),
        "role": "Admin",
        "active": True,
        "created_at": datetime.now().isoformat(),
    }

    users.append(
        admin
    )

    data[
        "users"
    ] = users

    save_memory(data)

    return admin


# ============================================================
# INITIALIZE
# ============================================================

def initialize_database() -> dict[str, Any]:

    data = load_memory()

    ensure_admin_user(data)

    return data


# ============================================================
# MODULE TEST
# ============================================================

if __name__ == "__main__":

    database = initialize_database()

    print(
        "Creative Studios database OK"
    )

    print(
        f"Database file: {DATABASE_FILE}"
    )

    print(
        f"Users: {len(database.get('users', []))}"
    )

    print(
        f"Projects: {len(database.get('projects', []))}"
    )