"""
Creative Studios
Database Persistence
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = BASE_DIR / "creativestudios_db.json"


def load_memory() -> dict[str, Any]:
    """Load the application database from JSON."""

    if not DB_FILE.exists():
        return {}

    try:
        with DB_FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}


def save_memory(
    database: dict[str, Any],
) -> None:
    """Persist the application database to JSON."""

    DB_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = DB_FILE.with_suffix(
        ".tmp"
    )

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

    temporary_file.replace(DB_FILE)