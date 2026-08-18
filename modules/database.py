"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

JSON-backed database layer.

No Streamlit dependency.
No SQLAlchemy dependency.
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
# PATHS
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

def _fresh_database() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_DATABASE)


def _normalize_database(
    data: Any,
) -> dict[str, Any]:

    if not isinstance(data, dict):
        data = {}

    normalized = copy.deepcopy(data)

    normalized.setdefault(
        "database_version",
        1,
    )

    for key, default in DEFAULT_DATABASE.items():

        if key == "database_version":
            continue

        if key not in normalized:
            normalized[key] = copy.deepcopy(default)

        elif not isinstance(
            normalized[key],
            list,
        ):
            normalized[key] = []

    return normalized


def _json_default(value: Any) -> str:

    if isinstance(
        value,
        datetime,
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


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict[str, Any]:

    if not DATABASE_FILE.exists():

        data = _fresh_database()

        save_memory(data)

        return data

    try:

        with DATABASE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            raw = json.load(file)

        return _normalize_database(raw)

    except (
        OSError,
        json.JSONDecodeError,
        UnicodeDecodeError,
    ):

        # Do not destroy a possibly recoverable file.
        # Create a safe in-memory database instead.
        return _fresh_database()


# ============================================================
# SAVE DATABASE
# ============================================================

def save_memory(
    data: dict[str, Any],
) -> bool:

    normalized = _normalize_database(
        data
    )

    temporary_path: Path | None = None

    try:

        DATABASE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fd, temporary_name = tempfile.mkstemp(
            prefix="creativestudios_",
            suffix=".tmp",
            dir=str(
                DATABASE_FILE.parent
            ),
        )

        temporary_path = Path(
            temporary_name
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

            file.write("\n")

            file.flush()

            try:
                os.fsync(
                    file.fileno()
                )
            except OSError:
                pass

        os.replace(
            temporary_path,
            DATABASE_FILE,
        )

        temporary_path = None

        return True

    except (
        OSError,
        TypeError,
        ValueError,
    ):

        return False

    finally:

        if (
            temporary_path is not None
            and temporary_path.exists()
        ):

            try:
                temporary_path.unlink()
            except OSError:
                pass


# ============================================================
# COMPATIBILITY ALIASES
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
) -> list[dict[str, Any]]:

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

            record_id = int(
                record.get(
                    "id",
                    0,
                )
            )

            highest = max(
                highest,
                record_id,
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

        record_value = record.get(
            field
        )

        if (
            record_value is not None
            and str(
                record_value
            ).lower()
            == str(value).lower()
        ):

            return record

    return None


# ============================================================
# PASSWORDS
# ============================================================

def hash_password(
    password: str,
) -> str:

    return hashlib.sha256(
        str(password).encode(
            "utf-8"
        )
    ).hexdigest()


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    if not password_hash:
        return False

    return (
        hash_password(password)
        == str(password_hash)
    )


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    data: dict[str, Any] | None = None,
) -> dict[str, Any] | None:

    if data is None:
        data = load_memory()

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:
        return None

    users = get_collection(
        "users",
        data,
    )

    for user in users:

        if not isinstance(
            user,
            dict,
        ):
            continue

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        if (
            stored_username.lower()
            != username.lower()
        ):
            continue

        if not user.get(
            "active",
            True,
        ):
            return None

        stored_hash = user.get(
            "password_hash"
        )

        # New format
        if stored_hash and verify_password(
            password,
            stored_hash,
        ):
            return user

        # Compatibility with a plain password
        # from an older JSON database.
        if (
            user.get("password")
            and str(
                user.get("password")
            ) == password
        ):

            user["password_hash"] = (
                hash_password(password)
            )

            user.pop(
                "password",
                None,
            )

            save_memory(data)

            return user

        return None

    return None


def login_user(
    username: str,
    password: str,
    data: dict[str, Any] | None = None,
):
    """
    Compatibility wrapper.

    Returns:
        (True, user)
        or
        (False, None)
    """

    user = authenticate_user(
        username,
        password,
        data,
    )

    if user is None:
        return False, None

    return True, user


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

        if not isinstance(
            user,
            dict,
        ):
            continue

        if str(
            user.get(
                "username",
                "",
            )
        ).lower() != "admin":

            continue

        changed = False

        if not user.get(
            "full_name"
        ):

            user[
                "full_name"
            ] = "System Administrator"

            changed = True

        if not user.get(
            "role"
        ):

            user[
                "role"
            ] = "Admin"

            changed = True

        if "active" not in user:

            user[
                "active"
            ] = True

            changed = True

        if not user.get(
            "password_hash"
        ):

            user[
                "password_hash"
            ] = hash_password(
                "admin"
            )

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
# INITIALIZATION
# ============================================================

def initialize_database() -> dict[str, Any]:

    data = load_memory()

    ensure_admin_user(
        data
    )

    return data


# ============================================================
# STARTUP TEST
# ============================================================

if __name__ == "__main__":

    db = initialize_database()

    print(
        "Creative Studios database initialized."
    )

    print(
        f"Database: {DATABASE_FILE}"
    )

    print(
        f"Users: {len(db.get('users', []))}"
    )

    print(
        f"Projects: {len(db.get('projects', []))}"
    )