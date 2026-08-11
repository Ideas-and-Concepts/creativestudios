"""
Creative Studios
JSON database module.

The database is stored in:

    creativestudios_db.json

The module is deliberately defensive so malformed or incomplete
JSON cannot prevent Streamlit from starting.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# ============================================================
# PATH
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
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }
    ],
    "projects": [
        {
            "id": 1,
            "project_id": "PRJ-001",
            "name": "Grand Horizon Commercial Complex",
            "client": "Grand Horizon Holdings",
            "location": "Kampala, Uganda",
            "manager": "Project Manager",
            "project_type": "Commercial",
            "status": "Active",
            "estimated_budget": 1250000,
            "description": (
                "Commercial architectural, engineering "
                "and construction project."
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
# SAFE COPY
# ============================================================

def _copy_default_database() -> dict:

    return json.loads(
        json.dumps(
            DEFAULT_DATABASE
        )
    )


# ============================================================
# NORMALIZE DATABASE
# ============================================================

def normalize_database(
    data: Any,
) -> dict:

    if not isinstance(
        data,
        dict,
    ):

        data = {}

    defaults = _copy_default_database()

    for key, default_value in defaults.items():

        if key not in data:

            data[key] = default_value

        elif not isinstance(
            data[key],
            list,
        ):

            data[key] = default_value


    return data


# ============================================================
# LOAD
# ============================================================

def load_memory() -> dict:

    if not DATABASE_FILE.exists():

        data = _copy_default_database()

        save_memory(data)

        return data


    try:

        with DATABASE_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return normalize_database(
            data
        )

    except (
        json.JSONDecodeError,
        OSError,
        TypeError,
        ValueError,
    ):

        return _copy_default_database()


# ============================================================
# SAVE
# ============================================================

def save_memory(
    data: dict,
) -> bool:

    try:

        data = normalize_database(
            data
        )

        with DATABASE_FILE.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return True

    except (
        OSError,
        TypeError,
        ValueError,
    ):

        return False


# ============================================================
# ADD RECORD
# ============================================================

def add_record(
    db: dict,
    collection: str,
    record: dict,
) -> dict:

    if collection not in db:

        db[collection] = []

    if not isinstance(
        db[collection],
        list,
    ):

        db[collection] = []

    existing = db[collection]

    numeric_ids = []

    for item in existing:

        if isinstance(
            item,
            dict,
        ):

            value = item.get(
                "id"
            )

            if isinstance(
                value,
                int,
            ):

                numeric_ids.append(
                    value
                )

    next_id = (
        max(numeric_ids) + 1
        if numeric_ids
        else 1
    )

    record = dict(record)

    record.setdefault(
        "id",
        next_id,
    )

    existing.append(
        record
    )

    save_memory(
        db
    )

    return record


# ============================================================
# UPDATE RECORD
# ============================================================

def update_record(
    db: dict,
    collection: str,
    record_id: int,
    updates: dict,
) -> bool:

    records = db.get(
        collection,
        [],
    )

    if not isinstance(
        records,
        list,
    ):

        return False

    for index, record in enumerate(
        records
    ):

        if not isinstance(
            record,
            dict,
        ):

            continue

        if record.get(
            "id"
        ) == record_id:

            updated = dict(
                record
            )

            updated.update(
                updates
            )

            records[index] = updated

            return save_memory(
                db
            )

    return False


# ============================================================
# DELETE RECORD
# ============================================================

def delete_record(
    db: dict,
    collection: str,
    record_id: int,
) -> bool:

    records = db.get(
        collection,
        [],
    )

    if not isinstance(
        records,
        list,
    ):

        return False

    original_length = len(
        records
    )

    db[collection] = [
        record
        for record in records
        if not (
            isinstance(
                record,
                dict,
            )
            and record.get("id")
            == record_id
        )
    ]

    if len(
        db[collection]
    ) == original_length:

        return False

    return save_memory(
        db
    )