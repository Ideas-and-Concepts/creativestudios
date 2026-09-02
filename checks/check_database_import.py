"""Creative Studios database import diagnostic."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"
DB_FILE = ROOT / "modules" / "database.py"


def get_database_imports() -> list[str]:
    tree = ast.parse(APP_FILE.read_text(encoding="utf-8"), filename=str(APP_FILE))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "modules.database":
            return [alias.name for alias in node.names if alias.name != "*"]
    return []


def get_database_definitions() -> set[str]:
    tree = ast.parse(DB_FILE.read_text(encoding="utf-8"), filename=str(DB_FILE))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def main() -> int:
    print("Creative Studios database import diagnostic")
    imports = get_database_imports()
    definitions = get_database_definitions()
    missing = [name for name in imports if name not in definitions]

    if missing:
        print("IMPORT MISMATCH")
        for name in missing:
            print(f"  Missing symbol: {name}")
        return 1

    print("Database import contract matches.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
