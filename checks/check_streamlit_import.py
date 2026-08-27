"""
Creative Studios
Minimal streamlit_app.py smoke test.

Purpose:
- Import streamlit_app.py without starting Streamlit.
- Detect missing Python dependencies.
- Detect missing project modules.
- Detect top-level runtime errors.
- Report the exact file and line where possible.

This does NOT run `streamlit run`.
"""

from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP_FILE = ROOT / "streamlit_app.py"


# ============================================================
# RESULT HELPERS
# ============================================================

def fail(message: str) -> None:
    print()
    print("=" * 70)
    print("SMOKE TEST FAILED")
    print("=" * 70)
    print(message)
    print()
    sys.exit(1)


def show_exception(exc: BaseException) -> None:
    print()
    print("=" * 70)
    print("TOP-LEVEL RUNTIME ERROR")
    print("=" * 70)

    print(
        f"Type: {type(exc).__name__}"
    )

    print(
        f"Message: {exc}"
    )

    print()
    print("Traceback:")
    traceback.print_exc()


# ============================================================
# CHECK FILE
# ============================================================

print()
print("=" * 70)
print("CREATIVE STUDIOS IMPORT SMOKE TEST")
print("=" * 70)

if not APP_FILE.exists():

    fail(
        f"streamlit_app.py was not found:\n"
        f"{APP_FILE}"
    )

print(
    f"Testing: {APP_FILE}"
)


# ============================================================
# IMPORT STREAMLIT
# ============================================================

print()
print("[1/3] Checking Streamlit dependency...")

try:

    import streamlit

    print(
        f"PASS: streamlit {streamlit.__version__}"
    )

except ModuleNotFoundError as exc:

    fail(
        "Missing dependency: streamlit\n\n"
        "Install it with:\n"
        "    pip install streamlit"
    )

except Exception as exc:

    show_exception(exc)

    sys.exit(1)


# ============================================================
# IMPORT DATABASE FIRST
# ============================================================

print()
print("[2/3] Checking database dependency...")

try:

    from modules import database

    print(
        "PASS: modules.database imported."
    )

except ModuleNotFoundError as exc:

    missing = (
        exc.name
        or "unknown dependency"
    )

    fail(
        "Database dependency import failed.\n\n"
        f"Missing module: {missing}\n"
        f"Original error: {exc}"
    )

except Exception as exc:

    show_exception(exc)

    sys.exit(1)


# ============================================================
# IMPORT STREAMLIT APP
# ============================================================

print()
print("[3/3] Importing streamlit_app.py...")
print(
    "The Streamlit UI is NOT launched."
)


try:

    spec = importlib.util.spec_from_file_location(
        "creative_studios_app_smoke",
        APP_FILE,
    )

    if spec is None:

        fail(
            "Could not create import specification "
            "for streamlit_app.py."
        )

    if spec.loader is None:

        fail(
            "Could not create import loader "
            "for streamlit_app.py."
        )

    module = importlib.util.module_from_spec(
        spec
    )

    # Make the temporary module available while importing.
    sys.modules[
        "creative_studios_app_smoke"
    ] = module

    spec.loader.exec_module(
        module
    )

    print()
    print("=" * 70)
    print("SMOKE TEST PASSED")
    print("=" * 70)

    print(
        "streamlit_app.py imported successfully."
    )

    print(
        "No Streamlit server was launched."
    )

except ModuleNotFoundError as exc:

    print()
    print("=" * 70)
    print("MISSING DEPENDENCY / MODULE")
    print("=" * 70)

    print(
        f"Missing module: "
        f"{exc.name or 'unknown'}"
    )

    print(
        f"Error: {exc}"
    )

    print()
    print("Traceback:")
    traceback.print_exc()

    sys.exit(1)

except ImportError as exc:

    print()
    print("=" * 70)
    print("IMPORT ERROR")
    print("=" * 70)

    print(
        f"{type(exc).__name__}: {exc}"
    )

    print()
    print("Traceback:")
    traceback.print_exc()

    sys.exit(1)

except SyntaxError as exc:

    print()
    print("=" * 70)
    print("SYNTAX ERROR")
    print("=" * 70)

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
                " " * (exc.offset - 1)
                + "^"
            )

    sys.exit(1)

except Exception as exc:

    show_exception(exc)

    sys.exit(1)
