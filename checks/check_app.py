"""Creative Studios application verification."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"

REQUIRED_DATABASE_FUNCTIONS = [
    "load_memory",
    "save_memory",
    "initialize_database",
    "add_record",
    "update_record",
    "delete_record",
    "next_id",
    "get_record",
    "get_records",
]

WORKSPACE_MODULES = [
    ("dashboard", "render_dashboard"),
    ("projects", "render_projects_module"),
    ("documents", "render_documents_module"),
    ("architecture", "render_architecture_module"),
    ("engineering", "render_engineering_module"),
    ("drawings", "render_drawings_module"),
    ("boq", "render_boq_module"),
    ("mep", "render_mep_module"),
    ("construction", "render_construction_module"),
]


def main() -> int:
    print("Creative Studios application verification")

    if not APP_FILE.exists():
        print(f"ERROR: {APP_FILE} does not exist.")
        return 1

    try:
        source = APP_FILE.read_text(encoding="utf-8")
        ast.parse(source, filename=str(APP_FILE))
    except SyntaxError as exc:
        print(f"STREAMLIT_APP SYNTAX ERROR: {exc}")
        return 1

    try:
        database = importlib.import_module("modules.database")
    except Exception as exc:
        print(f"DATABASE IMPORT FAILED: {type(exc).__name__}: {exc}")
        return 1

    missing = [
        name for name in REQUIRED_DATABASE_FUNCTIONS
        if not callable(getattr(database, name, None))
    ]
    if missing:
        print("MISSING DATABASE FUNCTIONS:")
        for name in missing:
            print(f"  - {name}")
        return 1

    try:
        db = database.initialize_database()
    except Exception as exc:
        print(f"DATABASE INITIALIZATION FAILED: {type(exc).__name__}: {exc}")
        return 1

    if not isinstance(db, dict):
        print("DATABASE INITIALIZATION FAILED: expected dictionary.")
        return 1

    for collection in [
        "users", "projects", "documents", "drawings", "architecture",
        "engineering", "mep", "boq", "construction", "rfis", "tasks",
        "approvals", "teams", "settings",
    ]:
        if collection not in db:
            print(f"MISSING COLLECTION: {collection}")
            return 1

    try:
        for module_name, renderer_name in WORKSPACE_MODULES:
            module = importlib.import_module(f"modules.{module_name}")
            renderer = getattr(module, renderer_name, None)
            if not callable(renderer):
                print(f"MISSING RENDERER: modules.{module_name}.{renderer_name}")
                return 1
            print(f"PASS: modules.{module_name}")
    except Exception as exc:
        print(f"MODULE IMPORT FAILED: {type(exc).__name__}: {exc}")
        return 1

    print("PASS: database contract")
    print("PASS: database initialization")
    print("PASS: streamlit_app syntax")
    print("PASS: workspace module imports")
    print("Creative Studios verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
