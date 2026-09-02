"""Creative Studios Streamlit import smoke test."""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_FILE = ROOT / "streamlit_app.py"


def main() -> int:
    print("Creative Studios Streamlit import smoke test")

    if not APP_FILE.exists():
        print(f"Missing application: {APP_FILE}")
        return 1

    try:
        source = APP_FILE.read_text(encoding="utf-8")
        ast.parse(source, filename=str(APP_FILE))
    except SyntaxError as exc:
        print(f"Syntax error: {exc}")
        return 1

    try:
        import streamlit
        print(f"Streamlit {streamlit.__version__}")
    except Exception as exc:
        print(f"Streamlit import failed: {type(exc).__name__}: {exc}")
        return 1

    try:
        importlib.import_module("modules.database")
        print("PASS: modules.database")
    except Exception as exc:
        print(f"Database import failed: {type(exc).__name__}: {exc}")
        return 1

    try:
        module_name = "creative_studios_app_smoke"
        spec = importlib.util.spec_from_file_location(module_name, APP_FILE)
        if spec is None or spec.loader is None:
            print("Unable to create application import specification.")
            return 1
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:
        print(f"Application import failed: {type(exc).__name__}: {exc}")
        return 1

    print("Streamlit application imported successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
