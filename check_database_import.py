from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent

APP_FILE = ROOT / "streamlit_app.py"
DB_FILE = ROOT / "modules" / "database.py"


def get_database_imports() -> list[str]:
    tree = ast.parse(
        APP_FILE.read_text(encoding="utf-8"),
        filename=str(APP_FILE),
    )

    for node in tree.body:

        if not isinstance(
            node,
            ast.ImportFrom,
        ):
            continue

        if node.module != "modules.database":
            continue

        return [
            alias.name
            for alias in node.names
            if alias.name != "*"
        ]

    return []


def get_database_definitions() -> set[str]:
    tree = ast.parse(
        DB_FILE.read_text(encoding="utf-8"),
        filename=str(DB_FILE),
    )

    names: set[str] = set()

    for node in tree.body:

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):

            names.add(node.name)

    return names


def main() -> None:

    print("=" * 60)
    print("Creative Studios database import diagnostic")
    print("=" * 60)

    imports = get_database_imports()
    definitions = get_database_definitions()

    print("\nImported by streamlit_app.py:")

    for name in imports:
        print(f"  - {name}")

    print("\nDefined by modules/database.py:")

    for name in sorted(definitions):
        print(f"  - {name}")

    missing = [
        name
        for name in imports
        if name not in definitions
    ]

    if missing:

        print("\n❌ IMPORT MISMATCH")

        for name in missing:
            print(
                f"  Missing symbol: {name}"
            )

        print(
            "\nThese names are being imported by "
            "streamlit_app.py but are not defined "
            "in modules/database.py."
        )

        raise SystemExit(1)

    print(
        "\n✅ Database import contract matches."
    )


if __name__ == "__main__":
    main()