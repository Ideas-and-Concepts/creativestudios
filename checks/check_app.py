"""Creative Studios application verification."""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"

REQUIRED_DATABASE_FUNCTIONS = [
    "load_memory", "save_memory", "initialize_database", "add_record",
    "update_record", "delete_record", "next_id", "get_record", "get_records",
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
    ("procurement", "render_procurement_module"),
    ("construction", "render_construction_module"),
    ("cost_control", "render_cost_control_module"),
    ("tasks", "render_tasks_module"),
    ("rfis", "render_rfis_module"),
    ("approvals", "render_approvals_module"),
    ("reports", "render_reports_module"),
    ("settings", "render_settings_module"),
]

REQUIRED_COLLECTIONS = [
    "users", "projects", "documents", "drawings", "architecture", "engineering",
    "mep", "boq", "construction", "procurement", "cost_control", "rfis", "tasks",
    "approvals", "teams", "settings",
]


def main() -> int:
    print("Creative Studios application verification")

    if not APP_FILE.exists():
        print(f"ERROR: {APP_FILE} does not exist.")
        return 1

    try:
        ast.parse(APP_FILE.read_text(encoding="utf-8"), filename=str(APP_FILE))
    except SyntaxError as exc:
        print(f"STREAMLIT_APP SYNTAX ERROR: {exc}")
        return 1

    try:
        database = importlib.import_module("modules.database")
    except Exception as exc:
        print(f"DATABASE IMPORT FAILED: {type(exc).__name__}: {exc}")
        return 1

    missing = [name for name in REQUIRED_DATABASE_FUNCTIONS if not callable(getattr(database, name, None))]
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

    for collection in REQUIRED_COLLECTIONS:
        if collection not in db:
            print(f"MISSING COLLECTION: {collection}")
            return 1

    failures = []
    for module_name, renderer_name in WORKSPACE_MODULES:
        try:
            module = importlib.import_module(f"modules.{module_name}")
            renderer = getattr(module, renderer_name, None)
            if not callable(renderer):
                failures.append(f"MISSING RENDERER: modules.{module_name}.{renderer_name}")
            else:
                print(f"PASS: modules.{module_name}.{renderer_name}")
        except Exception as exc:
            failures.append(f"MODULE IMPORT FAILED: modules.{module_name}: {type(exc).__name__}: {exc}")

    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("PASS: database contract")
    print("PASS: database initialization")
    print("PASS: streamlit_app syntax")
    print("PASS: all workspace module imports")
    print("Creative Studios verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
