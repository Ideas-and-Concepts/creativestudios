"""
Creative Studios
Database Module

Supports:

1. Local JSON database
2. PostgreSQL database through DATABASE_URL

The application modules interact with the database through
load_memory() and save_memory().
"""

import json
import os
from copy import deepcopy
from pathlib import Path

import streamlit as st
from sqlalchemy import create_engine, text

from .utils import hash_password


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MEMORY_FILE = BASE_DIR / "creativestudios_db.json"


# ============================================================
# DEFAULT USERS
# ============================================================
#
# Passwords are hashed before being stored.
#
# IMPORTANT:
# These are development/bootstrap accounts.
# They should be replaced or disabled before production.
#

DEFAULT_USERS = [
    {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "name": "System Administrator",
        "role": "Admin",
        "active": True,
    },
    {
        "username": "arch_lead",
        "password_hash": hash_password("arch123"),
        "name": "Lead Architect",
        "role": "Architect",
        "active": True,
    },
    {
        "username": "struct_eng",
        "password_hash": hash_password("struct123"),
        "name": "Structural Specialist",
        "role": "Structural Engineer",
        "active": True,
    },
    {
        "username": "elec_eng",
        "password_hash": hash_password("elec123"),
        "name": "Electrical Systems Lead",
        "role": "Electrical Engineer",
        "active": True,
    },
    {
        "username": "plumber_lead",
        "password_hash": hash_password("plum123"),
        "name": "Master Plumber",
        "role": "Plumber",
        "active": True,
    },
]


# ============================================================
# DEFAULT APPLICATION DATA
# ============================================================

DEFAULT_MEMORY = {
    "users": DEFAULT_USERS,

    "projects": [
        {
            "id": "PRJ-001",
            "name": "Grand Horizon Commercial Complex",
            "type": "Commercial",
            "phase": "Schematic Design",
            "status": "Active",
            "budget": 1250000.0,
            "created_at": "2026-02-10",
            "description": (
                "10-story mixed-use commercial space "
                "with basement parking and green roofing."
            ),
        }
    ],

    "drawings": [],

    "approvals": [],

    "boq": [],

    "rfis": [],

    "site_logs": [],
}


# ============================================================
# POSTGRESQL ENGINE
# ============================================================

@st.cache_resource
def get_engine():
    """
    Create and cache the PostgreSQL engine.

    If DATABASE_URL is not configured, the application
    automatically falls back to the local JSON database.
    """

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return None

    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1,
        )

    try:
        return create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )

    except Exception as exc:
        st.warning(
            f"Unable to connect to PostgreSQL. "
            f"Using local database instead. ({exc})"
        )

        return None


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db() -> None:
    """
    Initialize the PostgreSQL application state table.
    """

    engine = get_engine()

    if engine is None:
        return

    with engine.begin() as connection:

        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    id INTEGER PRIMARY KEY,
                    data JSONB NOT NULL
                );
                """
            )
        )


# ============================================================
# DATA NORMALIZATION
# ============================================================

def normalize_memory(data: dict) -> dict:
    """
    Ensure all required application collections exist.
    """

    if not isinstance(data, dict):
        data = {}

    defaults = deepcopy(DEFAULT_MEMORY)

    for key, default_value in defaults.items():

        if key not in data or data[key] is None:
            data[key] = deepcopy(default_value)

    return data


# ============================================================
# LOCAL JSON DATABASE
# ============================================================

def load_local_memory() -> dict:
    """
    Load the local JSON database.
    """

    if not MEMORY_FILE.exists():

        data = deepcopy(DEFAULT_MEMORY)

        save_local_memory(data)

        return data

    try:

        raw_data = MEMORY_FILE.read_text(
            encoding="utf-8"
        )

        data = json.loads(raw_data)

        return normalize_memory(data)

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
    ):

        # If the JSON file is corrupted, return a clean
        # in-memory structure rather than crashing the app.
        return deepcopy(DEFAULT_MEMORY)


def save_local_memory(data: dict) -> bool:
    """
    Save application data to the local JSON database.
    """

    try:

        normalized = normalize_memory(data)

        MEMORY_FILE.write_text(
            json.dumps(
                normalized,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        return True

    except OSError as exc:

        st.error(
            f"Unable to save local database: {exc}"
        )

        return False


# ============================================================
# LOAD DATABASE
# ============================================================

def load_memory() -> dict:
    """
    Load application data.

    PostgreSQL is preferred when DATABASE_URL exists.
    Otherwise the local JSON database is used.
    """

    engine = get_engine()

    # --------------------------------------------------------
    # LOCAL MODE
    # --------------------------------------------------------

    if engine is None:
        return load_local_memory()

    # --------------------------------------------------------
    # POSTGRESQL MODE
    # --------------------------------------------------------

    try:

        init_db()

        with engine.connect() as connection:

            result = connection.execute(
                text(
                    """
                    SELECT data
                    FROM app_state
                    WHERE id = 1
                    """
                )
            ).fetchone()

            if result and result[0] is not None:

                data = result[0]

                if isinstance(data, str):
                    data = json.loads(data)

                return normalize_memory(data)

        # No database state exists yet.
        data = deepcopy(DEFAULT_MEMORY)

        save_memory(data)

        return data

    except Exception as exc:

        st.warning(
            "Database connection failed. "
            "Creative Studios is using the local database. "
            f"({exc})"
        )

        return load_local_memory()


# ============================================================
# SAVE DATABASE
# ============================================================

def save_memory(data: dict) -> bool:
    """
    Save application data.

    Uses PostgreSQL when DATABASE_URL exists.
    Otherwise saves to JSON.
    """

    normalized = normalize_memory(data)

    engine = get_engine()

    # --------------------------------------------------------
    # LOCAL MODE
    # --------------------------------------------------------

    if engine is None:
        return save_local_memory(normalized)

    # --------------------------------------------------------
    # POSTGRESQL MODE
    # --------------------------------------------------------

    try:

        init_db()

        with engine.begin() as connection:

            connection.execute(
                text(
                    """
                    INSERT INTO app_state (id, data)
                    VALUES (:id, CAST(:data AS JSONB))
                    ON CONFLICT (id)
                    DO UPDATE SET data = EXCLUDED.data;
                    """
                ),
                {
                    "id": 1,
                    "data": json.dumps(
                        normalized,
                        ensure_ascii=False,
                    ),
                },
            )

        return True

    except Exception as exc:

        st.error(
            f"Failed to save changes to PostgreSQL: {exc}"
        )

        return False


# ============================================================
# GENERIC COLLECTION HELPERS
# ============================================================

def get_collection(
    db: dict,
    collection_name: str,
) -> list:
    """
    Return a collection from the database.
    """

    collection = db.get(
        collection_name,
        [],
    )

    if not isinstance(collection, list):
        return []

    return collection


def add_record(
    db: dict,
    collection_name: str,
    record: dict,
) -> dict:
    """
    Add a record to a database collection and persist it.
    """

    if collection_name not in db:
        db[collection_name] = []

    db[collection_name].append(record)

    save_memory(db)

    return record


def update_record(
    db: dict,
    collection_name: str,
    record_id: str,
    updates: dict,
    id_field: str = "id",
) -> bool:
    """
    Update a record by ID.
    """

    records = get_collection(
        db,
        collection_name,
    )

    for record in records:

        if str(record.get(id_field)) == str(record_id):

            record.update(updates)

            save_memory(db)

            return True

    return False


def delete_record(
    db: dict,
    collection_name: str,
    record_id: str,
    id_field: str = "id",
) -> bool:
    """
    Delete a record by ID.
    """

    records = get_collection(
        db,
        collection_name,
    )

    original_length = len(records)

    db[collection_name] = [
        record
        for record in records
        if str(record.get(id_field)) != str(record_id)
    ]

    if len(db[collection_name]) != original_length:

        save_memory(db)

        return True

    return False


def find_record(
    db: dict,
    collection_name: str,
    record_id: str,
    id_field: str = "id",
):
    """
    Find one record by ID.
    """

    records = get_collection(
        db,
        collection_name,
    )

    for record in records:

        if str(record.get(id_field)) == str(record_id):
            return record

    return None