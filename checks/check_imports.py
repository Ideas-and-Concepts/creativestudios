"""Creative Studios targeted import diagnostic."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "streamlit_app.py"


def main() -> int:
    print("Creative Studios import diagnostic")

    if not APP.exists():
        print(f"ERROR: {APP} does not exist.")
        return 1

    try:
        source = APP.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(APP))
    except SyntaxError as exc:
        print(f"SYNTAX ERROR: {exc}")
        return 1

    imports = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "modules.database":
            imports.extend(alias.name for alias in node.names if alias.name != "*")

    if not imports:
        print("ERROR: No modules.database import found.")
        return 1

    try:
        database = importlib.import_module("modules.database")
    except Exception as exc:
        print(f"DATABASE MODULE FAILED: {type(exc).__name__}: {exc}")
        return 1

    failures = [name for name in imports if not hasattr(database, name)]
    if failures:
        print("IMPORT FAILURE FOUND")
        for name in failures:
            print(f"  Missing symbol: {name}")
        return 1

    print("ALL DATABASE IMPORTS ARE VALID.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
