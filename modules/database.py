"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

JSON Database Layer
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import secrets
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent

DATABASE_FILE = PROJECT_ROOT / "creativestudios_db.json"
BACKUP_DIR = PROJECT_ROOT / "database_backups"

DATABASE_VERSION = 1


# ============================================================
# DEFAULT DATABASE
# ============================================================

DEFAULT_DATABASE: dict[str, Any] = {
    "database_version": DATABASE_VERSION,

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
# JSON HELPERS
# ============================================================

def _json_default(value: Any) -> Any:

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


def _fresh_database() -> dict[str, Any]:

    return copy.deepcopy(
        DEFAULT_DATABASE
    )


def normalize_database(
    data: Any,
) -> dict[str, Any]:

    if not isinstance(data, dict):
        data = _fresh_database()

    result = copy.deepcopy(data)

    result.setdefault(
        "database_version",
        DATABASE_VERSION,
    )

    for key, default in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue

        if key not in result:
            result[key] = copy.deepcopy(default)

        elif not isinstance(
            result[key],
            list,
        ):
            result[key] = []

    return result


# ============================================================
# DATABASE FILE
# ============================================================

def database_exists() -> bool:

    return (
        DATABASE_FILE.exists()
        and DATABASE_FILE.is_file()
    )


def backup_database() -> Path | None:

    if not database_exists():
        return None

    try:

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

        backup_path.write_bytes(
            DATABASE_FILE.read_bytes()
        )

        return backup_path

    except OSError:

        return None


# ============================================================
# LOAD
# ============================================================

def load_memory(
    create_if_missing: bool = True,
) -> dict[str, Any]:

    if not database_exists():

        data = _fresh_database()

        if create_if_missing:
            save_memory(data)

        return data

    try:

        with DATABASE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            raw = json.load(file)

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        backup_database()

        data = _fresh_database()

        if create_if_missing:
            save_memory(data)

        return data

    data = normalize_database(raw)

    return data


# ============================================================
# SAVE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:

    if not isinstance(data, dict):
        return False

    data = normalize_database(data)

    temp_path: Path | None = None

    try:

        PROJECT_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

        fd, filename = tempfile.mkstemp(
            prefix=".creativestudios_",
            suffix=".tmp",
            dir=str(PROJECT_ROOT),
        )

        temp_path = Path(filename)

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
            temp_path,
            DATABASE_FILE,
        )

        temp_path = None

        return True

    except (
        OSError,
        TypeError,
        ValueError,
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

    data = load_memory()

    changed = False

    for key, default in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue

        if key not in data:

            data[key] = copy.deepcopy(default)
            changed = True

        elif not isinstance(
            data[key],
            list,
        ):

            data[key] = []
            changed = True

    if data.get(
        "database_version"
    ) != DATABASE_VERSION:

        data[
            "database_version"
        ] = DATABASE_VERSION

        changed = True

    if changed:
        save_memory(data)

    return data


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


def set_collection(
    collection_name: str,
    records: list,
    data: dict[str, Any] | None = None,
    save: bool = True,
) -> dict[str, Any]:

    if data is None:
        data = load_memory()

    data[
        collection_name
    ] = records if isinstance(
        records,
        list,
    ) else []

    if save:
        save_memory(data)

    return data


# ============================================================
# IDS
# ============================================================

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
# RECORD OPERATIONS
# ============================================================

def add_record(
    collection_name: str,
    record: dict[str, Any],
    data: dict[str, Any] | None = None,
    save: bool = True,
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

    new_record = copy.deepcopy(
        record
    )

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

    if save:
        save_memory(data)

    return new_record


def update_record(
    collection_name: str,
    record_id: Any,
    updates: dict[str, Any],
    data: dict[str, Any] | None = None,
    save: bool = True,
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

        original_id = record.get(
            "id"
        )

        updated = copy.deepcopy(
            record
        )

        updated.update(
            copy.deepcopy(
                updates
            )
        )

        updated[
            "id"
        ] = original_id

        collection[index] = updated

        data[
            collection_name
        ] = collection

        if save:
            save_memory(data)

        return updated

    return None


def delete_record(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
    save: bool = True,
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

        if save:
            save_memory(data)

        return True

    return False


def find_by_id(
    collection_name: str,
    record_id: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    records = get_collection(
        collection_name,
        data,
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


def find_one(
    collection_name: str,
    field: str,
    value: Any,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    records = get_collection(
        collection_name,
        data,
    )

    for record in records:

        if not isinstance(
            record,
            dict,
        ):
            continue

        if str(
            record.get(field)
        ) == str(value):

            return record

    return None


def count_records(
    collection_name: str,
    data: dict[str, Any] | None = None,
) -> int:

    return len(
        get_collection(
            collection_name,
            data,
        )
    )


# ============================================================
# PASSWORD / AUTH HELPERS
# ============================================================

def hash_password(
    password: str,
) -> str:

    return hashlib.sha256(
        password.encode(
            "utf-8"
        )
    ).hexdigest()


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    return secrets.compare_digest(
        hash_password(password),
        password_hash,
    )


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

        if (
            str(
                user.get("username", "")
            ).lower()
            == "admin"
        ):

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
# RESET
# ============================================================

def reset_database(
    backup: bool = True,
) -> dict[str, Any]:

    if (
        backup
        and database_exists()
    ):
        backup_database()

    data = _fresh_database()

    save_memory(data)

    return data


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def load_database():
    return load_memory()


def save_database(data):
    return save_memory(data)


def get_db():
    return load_memory()


# ============================================================
# INITIALIZATION
# ============================================================

if __name__ == "__main__":

    db = ensure_database()

    ensure_admin_user(db)

    print(
        "Creative Studios database initialized."
    )

    print(
        f"Database: {DATABASE_FILE}"
    )

    print(
        f"Projects: {count_records('projects', db)}"
    )

    print(
        f"Users: {count_records('users', db)}"
    )