"""
Creative Studios
Application Import Verification

Checks:
1. modules.database imports
2. streamlit_app.py syntax
3. streamlit_app.py imports
4. database contract
5. module imports

Does NOT start Streamlit.
"""

from __future__ import annotations

import ast
import importlib
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent


# ============================================================
# HELPERS
# ============================================================

def report_error(
    title: str,
    exc: BaseException,
) -> None:

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    print(
        f"{type(exc).__name__}: {exc}"
    )

    traceback.print_exc()


# ============================================================
# 1. DATABASE IMPORT
# ============================================================

print()
print("=" * 70)
print("1. CHECKING modules.database")
print("=" * 70)

try:

    database = importlib.import_module(
        "modules.database"
    )

    print(
        "OK: modules.database imported."
    )

except Exception as exc:

    report_error(
        "DATABASE IMPORT FAILED",
        exc,
    )

    sys.exit(1)


# ============================================================
# 2. DATABASE CONTRACT
# ============================================================

print()
print("=" * 70)
print("2. CHECKING DATABASE CONTRACT")
print("=" * 70)


required_database_functions = [
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


database_errors = []


for function_name in required_database_functions:

    if not hasattr(
        database,
        function_name,
    ):

        database_errors.append(
            function_name
        )

    else:

        print(
            f"OK: database.{function_name}()"
        )


if database_errors:

    print()
    print(
        "MISSING DATABASE FUNCTIONS:"
    )

    for name in database_errors:

        print(
            f"  - {name}"
        )

    sys.exit(1)


# ============================================================
# 3. DATABASE INITIALIZATION
# ============================================================

print()
print("=" * 70)
print("3. CHECKING DATABASE INITIALIZATION")
print("=" * 70)

try:

    db = database.initialize_database()

    if not isinstance(
        db,
        dict,
    ):

        raise TypeError(
            "initialize_database() did not return a dictionary."
        )

    print(
        "OK: initialize_database() returned a dictionary."
    )

    expected_collections = [
        "users",
        "projects",
        "documents",
        "drawings",
        "rfis",
        "tasks",
        "teams",
        "settings",
    ]

    for collection in expected_collections:

        if collection not in db:

            raise RuntimeError(
                f"Missing collection: {collection}"
            )

        print(
            f"OK: collection '{collection}'"
        )

except Exception as exc:

    report_error(
        "DATABASE INITIALIZATION FAILED",
        exc,
    )

    sys.exit(1)


# ============================================================
# 4. STREAMLIT_APP SYNTAX
# ============================================================

print()
print("=" * 70)
print("4. CHECKING streamlit_app.py SYNTAX")
print("=" * 70)


app_file = ROOT / "streamlit_app.py"


if not app_file.exists():

    print(
        f"ERROR: {app_file} does not exist."
    )

    sys.exit(1)


try:

    source = app_file.read_text(
        encoding="utf-8"
    )

    ast.parse(
        source,
        filename=str(app_file),
    )

    print(
        "OK: streamlit_app.py syntax is valid."
    )

except SyntaxError as exc:

    print()
    print(
        "STREAMLIT_APP SYNTAX ERROR"
    )

    print(
        f"File: {exc.filename}"
    )

    print(
        f"Line: {exc.lineno}"
    )

    print(
        f"Column: {exc.offset}"
    )

    print(
        f"Error: {exc.msg}"
    )

    if exc.text:

        print()
        print(
            exc.text.rstrip()
        )

        if exc.offset:

            print(
                " " * (
                    exc.offset - 1
                )
                + "^"
            )

    sys.exit(1)


# ============================================================
# 5. AST IMPORT CHECK
# ============================================================

print()
print("=" * 70)
print("5. CHECKING streamlit_app.py DATABASE IMPORT")
print("=" * 70)


tree = ast.parse(
    source,
    filename=str(app_file),
)


database_imports = []


for node in ast.walk(tree):

    if isinstance(
        node,
        ast.ImportFrom,
    ):

        if node.module == "modules.database":

            names = [
                alias.name
                for alias in node.names
            ]

            database_imports.append(
                (
                    node.lineno,
                    names,
                )
            )


if not database_imports:

    print(
        "ERROR: No modules.database import found."
    )

    sys.exit(1)


for line_number, names in database_imports:

    print(
        f"Line {line_number}: "
        f"from modules.database import "
        f"{', '.join(names)}"
    )


# ============================================================
# 6. CHECK FOR DUPLICATE DATABASE IMPORTS
# ============================================================

print()
print("=" * 70)
print("6. CHECKING DUPLICATE DATABASE IMPORTS")
print("=" * 70)


if len(database_imports) > 1:

    print(
        "WARNING: Multiple database import blocks detected."
    )

    for line_number, names in database_imports:

        print(
            f"  Line {line_number}: "
            f"{', '.join(names)}"
        )

else:

    print(
        "OK: One modules.database import block."
    )


# ============================================================
# 7. CHECK WORKSPACE MODULES
# ============================================================

print()
print("=" * 70)
print("7. CHECKING WORKSPACE MODULES")
print("=" * 70)


workspace_modules = [
    (
        "projects",
        "render_projects_module",
    ),
    (
        "documents",
        "render_documents_module",
    ),
    (
        "drawings",
        "render_drawings_module",
    ),
    (
        "rfis",
        "render_rfis_module",
    ),
    (
        "tasks",
        "render_tasks_module",
    ),
]


for module_name, renderer_name in workspace_modules:

    try:

        module = importlib.import_module(
            f"modules.{module_name}"
        )

        print(
            f"OK: modules.{module_name}"
        )

        if hasattr(
            module,
            renderer_name,
        ):

            print(
                f"  OK: {renderer_name}()"
            )

        else:

            print(
                f"  WARNING: "
                f"{renderer_name}() not found."
            )

    except Exception as exc:

        print(
            f"ERROR: modules.{module_name}"
        )

        print(
            f"  {type(exc).__name__}: {exc}"
        )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 70)
print("CREATIVE STUDIOS VERIFICATION COMPLETE")
print("=" * 70)

print(
    "Database import:        PASS"
)

print(
    "Database contract:      PASS"
)

print(
    "Database initialization: PASS"
)

print(
    "streamlit_app syntax:   PASS"
)

print(
    "Streamlit UI startup:   NOT EXECUTED"
)

print()