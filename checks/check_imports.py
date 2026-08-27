"""
Creative Studios
Targeted import diagnostic.

This script NEVER starts Streamlit.
It specifically diagnoses:

    from modules.database import (...)

Run:

    python check_imports.py
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
APP = ROOT / "streamlit_app.py"


def main() -> int:

    print("=" * 70)
    print("CREATIVE STUDIOS IMPORT DIAGNOSTIC")
    print("=" * 70)

    print(f"Project: {ROOT}")
    print(f"App:     {APP}")
    print()

    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not APP.exists():

        print(f"ERROR: {APP} does not exist.")

        return 1

    database_file = (
        ROOT / "modules" / "database.py"
    )

    if not database_file.exists():

        print(
            "ERROR: modules/database.py does not exist."
        )

        return 1

    # --------------------------------------------------------
    # Parse streamlit_app.py
    # --------------------------------------------------------

    try:

        source = APP.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(
            source,
            filename=str(APP),
        )

    except SyntaxError as exc:

        print()
        print("SYNTAX ERROR")
        print("-" * 70)
        print(f"File:   {exc.filename}")
        print(f"Line:   {exc.lineno}")
        print(f"Column: {exc.offset}")
        print(f"Error:  {exc.msg}")

        if exc.text:

            print()
            print(
                f"    {exc.text.rstrip()}"
            )

            if exc.offset:
                print(
                    "    "
                    + " " * (exc.offset - 1)
                    + "^"
                )

        return 1

    # --------------------------------------------------------
    # Find modules.database import
    # --------------------------------------------------------

    target = None

    for node in tree.body:

        if not isinstance(
            node,
            ast.ImportFrom,
        ):
            continue

        if node.module != "modules.database":
            continue

        target = node
        break

    if target is None:

        print(
            "ERROR: No 'from modules.database import ...' "
            "statement was found."
        )

        return 1

    # --------------------------------------------------------
    # Display exact source location
    # --------------------------------------------------------

    print(
        "FOUND DATABASE IMPORT"
    )
    print("-" * 70)

    print(
        f"File:   {APP}"
    )

    print(
        f"Line:   {target.lineno}"
    )

    print(
        f"Column: {target.col_offset}"
    )

    print()

    try:

        import_text = ast.get_source_segment(
            source,
            target,
        )

        print(import_text)

    except Exception:

        print(
            "Unable to display source segment."
        )

    # --------------------------------------------------------
    # Import database module
    # --------------------------------------------------------

    print()
    print(
        "LOADING modules.database"
    )
    print("-" * 70)

    try:

        database = importlib.import_module(
            "modules.database"
        )

    except Exception as exc:

        print(
            "DATABASE MODULE FAILED"
        )

        print()
        print(
            f"Exception: {type(exc).__name__}"
        )

        print(
            f"Message:   {exc}"
        )

        print()

        import traceback

        traceback.print_exc()

        return 1

    print(
        "modules.database imported successfully."
    )

    print(
        f"Location: {database.__file__}"
    )

    # --------------------------------------------------------
    # Test every imported symbol individually
    # --------------------------------------------------------

    print()
    print(
        "CHECKING IMPORTED SYMBOLS"
    )
    print("-" * 70)

    failures = []

    for alias in target.names:

        symbol = alias.name

        if symbol == "*":

            print(
                "[WARN] wildcard import detected"
            )

            continue

        display_name = symbol

        if alias.asname:

            display_name = (
                f"{symbol} as {alias.asname}"
            )

        if hasattr(
            database,
            symbol,
        ):

            value = getattr(
                database,
                symbol,
            )

            print(
                f"[OK]   {display_name}"
                f"    ({type(value).__name__})"
            )

        else:

            print(
                f"[FAIL] {display_name}"
            )

            failures.append(
                symbol
            )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    print()
    print("=" * 70)

    if failures:

        print(
            "IMPORT FAILURE FOUND"
        )

        print("=" * 70)

        print()

        for symbol in failures:

            print(
                f"Missing symbol: {symbol}"
            )

        print()
        print(
            "The problem is in modules/database.py, "
            "not Streamlit UI startup."
        )

        print()
        print(
            "Your streamlit_app.py expects these symbols "
            "to exist in modules.database."
        )

        return 1

    print(
        "ALL DATABASE IMPORTS ARE VALID."
    )

    print("=" * 70)

    print()
    print(
        "The line 13 database import is NOT the problem."
    )

    print(
        "If Streamlit still reports line 13, the next "
        "thing to inspect is a nested import or circular import."
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )
