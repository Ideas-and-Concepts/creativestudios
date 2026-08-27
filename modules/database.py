"""
Creative Studios
Database Persistence

JSON-based application database with safe initialization
and automatic default administrator creation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "creativestudios_db.json"


# ============================================================
# DEFAULT DATABASE STRUCTURE
# ============================================================

DEFAULT_COLLECTIONS: dict[str, list[Any]] = {
    "users": [],
    "projects": [],
    "documents": [],
    "architecture": [],
    "engineering": [],
    "drawings": [],
    "mep": [],
}


# ============================================================
# DEFAULT ADMINISTRATOR
# ============================================================

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def _hash_password(password: str) -> str:
    """Create a SHA-256 password hash."""

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def _default_admin() -> dict[str, Any]:
    """Return the default administrator record."""

    return {
        "id": 1,
        "username": DEFAULT_ADMIN_USERNAME,
        "password": _hash_password(
            DEFAULT_ADMIN_PASSWORD
        ),
        "full_name": "System Administrator",
        "role": "Administrator",
        "active": True,
    }


# ============================================================
# DATABASE NORMALIZATION
# ============================================================

def _normalize_database(
    data: Any,
) -> dict[str, Any]:
    """
    Ensure the database is a dictionary and contains all
    expected collections.

    Existing data is preserved.
    """

    if not isinstance(data, dict):
        data = {}

    for collection_name, default_value in DEFAULT_COLLECTIONS.items():

        if collection_name not in data:
            data[collection_name] = list(
                default_value
            )

        elif not isinstance(
            data[collection_name],
            list,
        ):
            data[collection_name] = list(
                default_value
            )

    return data


# ============================================================
# ADMIN INITIALIZATION
# ============================================================

def _ensure_default_admin(
    database: dict[str, Any],
) -> bool:
    """
    Ensure that an administrator account exists.

    Returns True when the database was modified.
    """

    users = database.get(
        "users",
        [],
    )

    if not isinstance(users, list):
        users = []
        database["users"] = users

    # --------------------------------------------------------
    # Check whether an administrator already exists.
    # --------------------------------------------------------

    for user in users:

        if not isinstance(user, dict):
            continue

        username = str(
            user.get(
                "username",
                "",
            )
            or ""
        ).strip().lower()

        if username == DEFAULT_ADMIN_USERNAME.lower():

            changed = False

            # Repair missing fields without overwriting
            # an existing password.
            if not user.get("full_name"):
                user["full_name"] = "System Administrator"
                changed = True

            if not user.get("role"):
                user["role"] = "Administrator"
                changed = True

            if "active" not in user:
                user["active"] = True
                changed = True

            return changed

    # --------------------------------------------------------
    # No administrator exists.
    # --------------------------------------------------------

    users.append(
        _default_admin()
    )

    return True


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict[str, Any]:
    """
    Load the Creative Studios database.

    If the database does not exist, it is created with the
    required collections and a default administrator.

    Existing database records are preserved.
    """

    database: dict[str, Any]

    if not DB_FILE.exists():

        database = _normalize_database({})

        _ensure_default_admin(
            database
        )

        save_memory(
            database
        )

        return database

    try:

        with DB_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

    except (
        json.JSONDecodeError,
        OSError,
    ):

        # Do not crash the application because of an invalid
        # or unreadable JSON database.
        database = _normalize_database({})

        _ensure_default_admin(
            database
        )

        save_memory(
            database
        )

        return database

    database = _normalize_database(
        data
    )

    changed = _ensure_default_admin(
        database
    )

    if changed:
        save_memory(
            database
        )

    return database


# ============================================================
# SAVE DATABASE
# ============================================================

def save_memory(
    database: dict[str, Any],
) -> None:
    """
    Persist the application database safely.

    Data is written to a temporary file first and then
    atomically replaced into the final database file.
    """

    if not isinstance(
        database,
        dict,
    ):
        raise TypeError(
            "database must be a dictionary"
        )

    database = _normalize_database(
        database
    )

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = DB_FILE.with_suffix(
        ".tmp"
    )

    try:

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                database,
                file,
                indent=4,
                ensure_ascii=False,
            )

            file.flush()

        temporary_file.replace(
            DB_FILE
        )

    finally:

        if temporary_file.exists():

            try:
                temporary_file.unlink()

            except OSError:
                pass