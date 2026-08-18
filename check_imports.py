"""
Creative Studios import preflight checker.

Run:
    python check_imports.py

This intentionally does NOT start Streamlit.
It checks modules.database first, then streamlit_app.py.
"""

from __future__ import annotations

import importlib
import importlib.util
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def print_header(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def check_database() -> bool:
    print_header("1. CHECKING modules.database")

    try:
        module = importlib.import_module(
            "modules.database"
        )

        print("OK: modules.database imported successfully.")
        print(f"Location: {getattr(module, '__file__', 'unknown')}")

        required_symbols = [
            "load_memory",
            "save_memory",
            "load_database",
            "save_database",
            "get_db",
            "ensure_database",
            "get_collection",
            "add_record",
            "update_record",
            "delete_record",
            "find_by_id",
            "find_one",
            "hash_password",
            "verify_password",
            "ensure_admin_user",
            "initialize_database",
        ]

        print()
        print("Checking required symbols:")

        failed = False

        for symbol in required_symbols:

            if hasattr(module, symbol):
                print(f"  OK   {symbol}")
            else:
                print(f"  FAIL {symbol}")
                failed = True

        if failed:
            print()
            print(
                "ERROR: One or more required symbols are missing "
                "from modules.database."
            )

            return False

        return True

    except Exception as exc:

        print()
        print("FAILED: modules.database")
        print(f"Exception type: {type(exc).__name__}")
        print(f"Exception: {exc}")

        print()
        print("FULL TRACEBACK:")
        traceback.print_exc()

        return False


def check_streamlit_app() -> bool:
    print_header("2. CHECKING streamlit_app.py")

    app_path = ROOT / "streamlit_app.py"

    if not app_path.exists():

        print(
            f"FAILED: {app_path} does not exist."
        )

        return False

    print(f"File: {app_path}")

    try:

        spec = importlib.util.spec_from_file_location(
            "creative_studios_streamlit_app_preflight",
            app_path,
        )

        if spec is None:
            print(
                "FAILED: Could not create import specification."
            )
            return False

        if spec.loader is None:
            print(
                "FAILED: No loader available for streamlit_app.py."
            )
            return False

        module = importlib.util.module_from_spec(
            spec
        )

        print()
        print(
            "Importing streamlit_app.py..."
        )
        print(
            "WARNING: This may execute top-level Streamlit code."
        )

        spec.loader.exec_module(module)

        print()
        print(
            "OK: streamlit_app.py imported successfully."
        )

        return True

    except Exception as exc:

        print()
        print("FAILED: streamlit_app.py")
        print(f"Exception type: {type(exc).__name__}")
        print(f"Exception: {exc}")

        print()
        print("FULL TRACEBACK:")
        traceback.print_exc()

        return False


def main() -> int:

    print_header(
        "CREATIVE STUDIOS IMPORT PREFLIGHT"
    )

    print(f"Project root: {ROOT}")

    database_ok = check_database()

    if not database_ok:

        print_header("STOPPED")

        print(
            "modules.database failed."
        )

        print(
            "Fix this error before testing streamlit_app.py."
        )

        return 1

    streamlit_ok = check_streamlit_app()

    print_header("PREFLIGHT RESULT")

    if database_ok and streamlit_ok:

        print(
            "SUCCESS: Both modules imported successfully."
        )

        return 0

    print(
        "FAILURE: One or more imports failed."
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(
        main()
    )