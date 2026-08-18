"""
Creative Studios
Import Preflight Checker

Purpose:
    1. Validate modules.database.
    2. Parse streamlit_app.py without starting Streamlit UI.
    3. Test the imports used by streamlit_app.py.
    4. Execute function/class definitions only.
    5. Report the exact failing file, line, column, symbol, and traceback.

Run:

    python check_imports.py

This script MUST NOT call st.set_page_config(), st.navigation(),
st.run(), render_login(), render_sidebar(), or any application
startup function.
"""

from __future__ import annotations

import ast
import importlib
import sys
import traceback
from pathlib import Path
from types import ModuleType


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

STREAMLIT_APP = ROOT / "streamlit_app.py"

DATABASE_MODULE = "modules.database"


# ============================================================
# OUTPUT HELPERS
# ============================================================

def header(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def success(message: str) -> None:
    print(f"[OK]   {message}")


def failure(message: str) -> None:
    print(f"[FAIL] {message}")


def warning(message: str) -> None:
    print(f"[WARN] {message}")


def info(message: str) -> None:
    print(f"[INFO] {message}")


# ============================================================
# EXCEPTION LOCATION
# ============================================================

def report_exception(
    exc: BaseException,
    *,
    source_file: Path | None = None,
    fallback_line: int | None = None,
) -> None:
    """
    Print the most useful exception location available.
    """

    print()
    print("Exception type:")
    print(f"    {type(exc).__name__}")

    print()
    print("Exception message:")
    print(f"    {exc}")

    if source_file is not None:
        print()
        print("File:")
        print(f"    {source_file}")

    traceback_lines = traceback.format_exception(
        type(exc),
        exc,
        exc.__traceback__,
    )

    print()
    print("Traceback:")
    print("".join(traceback_lines))

    if fallback_line is not None:
        print()
        print("Detected source line:")
        print(f"    {fallback_line}")


# ============================================================
# DATABASE CHECK
# ============================================================

def check_database() -> bool:
    """
    Import modules.database normally.

    database.py is expected to contain no Streamlit UI code,
    so a normal import is appropriate here.
    """

    header("1. modules.database")

    try:
        module = importlib.import_module(
            DATABASE_MODULE
        )

        success(
            "modules.database imported successfully."
        )

        info(
            f"Location: {getattr(module, '__file__', 'unknown')}"
        )

    except Exception as exc:

        failure(
            "modules.database failed to import."
        )

        report_exception(
            exc,
            source_file=ROOT / "modules" / "database.py",
        )

        return False

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
    print("Required database symbols:")

    missing = []

    for symbol in required_symbols:

        if hasattr(module, symbol):
            success(symbol)
        else:
            failure(symbol)
            missing.append(symbol)

    if missing:

        print()
        failure(
            "Missing database symbols:"
        )

        for symbol in missing:
            print(f"    {symbol}")

        return False

    return True


# ============================================================
# AST HELPERS
# ============================================================

def get_import_name(node: ast.AST) -> str:
    """
    Return a readable import description.
    """

    if isinstance(node, ast.Import):

        names = []

        for alias in node.names:
            names.append(alias.name)

        return "import " + ", ".join(names)

    if isinstance(node, ast.ImportFrom):

        module = node.module or ""

        if node.level:
            prefix = "." * node.level
            module = prefix + module

        names = []

        for alias in node.names:
            if alias.asname:
                names.append(
                    f"{alias.name} as {alias.asname}"
                )
            else:
                names.append(alias.name)

        return (
            f"from {module} import "
            + ", ".join(names)
        )

    return ast.dump(node)


def imported_symbols(
    node: ast.AST,
) -> list[str]:
    """
    Return individual imported symbols.
    """

    result: list[str] = []

    if isinstance(node, ast.Import):

        for alias in node.names:

            if alias.asname:
                result.append(
                    f"{alias.name} as {alias.asname}"
                )
            else:
                result.append(
                    alias.name
                )

    elif isinstance(node, ast.ImportFrom):

        module = node.module or ""

        for alias in node.names:

            if alias.name == "*":
                result.append(
                    f"{module} import *"
                )
                continue

            if alias.asname:
                result.append(
                    f"{module}.{alias.name} as {alias.asname}"
                )
            else:
                result.append(
                    f"{module}.{alias.name}"
                )

    return result


# ============================================================
# SAFE AST
# ============================================================

class SafeStreamlitTransformer(
    ast.NodeTransformer
):
    """
    Create a safe version of streamlit_app.py.

    Preserved:
        - imports
        - function definitions
        - async function definitions
        - class definitions

    Removed:
        - top-level UI execution
        - top-level function calls
        - top-level assignments
        - top-level Streamlit startup
        - if __name__ == "__main__"

    Function/class bodies are retained because defining them does
    not execute their bodies.

    Decorators are removed because decorators execute while a
    function/class is defined and could themselves start UI code.
    """

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> ast.FunctionDef:

        node.decorator_list = []

        node.returns = node.returns

        return node

    def visit_AsyncFunctionDef(
        self,
        node: ast.AsyncFunctionDef,
    ) -> ast.AsyncFunctionDef:

        node.decorator_list = []

        return node

    def visit_ClassDef(
        self,
        node: ast.ClassDef,
    ) -> ast.ClassDef:

        node.decorator_list = []

        return node

    def visit_Module(
        self,
        node: ast.Module,
    ) -> ast.Module:

        safe_body = []

        for child in node.body:

            if isinstance(
                child,
                (
                    ast.Import,
                    ast.ImportFrom,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.ClassDef,
                ),
            ):
                safe_body.append(child)

            elif isinstance(
                child,
                ast.If,
            ):
                # Never execute top-level if blocks.
                continue

            else:
                # Remove assignments, calls, expressions,
                # Streamlit configuration, etc.
                continue

        node.body = safe_body

        return node


# ============================================================
# STREAMLIT APP AST PARSE
# ============================================================

def parse_streamlit_app() -> ast.Module | None:
    """
    Parse streamlit_app.py without executing it.
    """

    header(
        "2. Parsing streamlit_app.py"
    )

    if not STREAMLIT_APP.exists():

        failure(
            f"File does not exist: {STREAMLIT_APP}"
        )

        return None

    try:

        source = STREAMLIT_APP.read_text(
            encoding="utf-8"
        )

    except Exception as exc:

        failure(
            "Could not read streamlit_app.py."
        )

        report_exception(
            exc,
            source_file=STREAMLIT_APP,
        )

        return None

    try:

        tree = ast.parse(
            source,
            filename=str(STREAMLIT_APP),
        )

        success(
            "streamlit_app.py passed Python AST parsing."
        )

        return tree

    except SyntaxError as exc:

        failure(
            "Syntax error detected in streamlit_app.py."
        )

        print()
        print("Exact location:")

        print(
            f"    File: {exc.filename}"
        )

        print(
            f"    Line: {exc.lineno}"
        )

        print(
            f"    Column: {exc.offset}"
        )

        print(
            f"    Message: {exc.msg}"
        )

        if exc.text:
            print()
            print("Source:")
            print(
                f"    {exc.text.rstrip()}"
            )

            if exc.offset:
                print(
                    "    "
                    + " " * (exc.offset - 1)
                    + "^"
                )

        return None


# ============================================================
# CHECK IMPORTS USED BY STREAMLIT APP
# ============================================================

def check_app_imports(
    tree: ast.Module,
) -> bool:

    header(
        "3. Checking streamlit_app.py imports"
    )

    imports = [
        node
        for node in tree.body
        if isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom,
            ),
        )
    ]

    if not imports:

        warning(
            "No top-level imports were found."
        )

        return True

    all_ok = True

    for node in imports:

        description = get_import_name(
            node
        )

        line = getattr(
            node,
            "lineno",
            "?",
        )

        column = getattr(
            node,
            "col_offset",
            0,
        )

        print()
        print(
            f"Import at line {line}, "
            f"column {column}:"
        )

        print(
            f"    {description}"
        )

        try:

            if isinstance(
                node,
                ast.Import,
            ):

                for alias in node.names:

                    importlib.import_module(
                        alias.name
                    )

            elif isinstance(
                node,
                ast.ImportFrom,
            ):

                module_name = node.module or ""

                if node.level:
                    # Resolve relative imports using
                    # the streamlit_app package context.
                    package = None

                    if node.level == 1:
                        package = (
                            ROOT.name
                        )

                    module_name = (
                        "." * node.level
                        + module_name
                    )

                if module_name.startswith("."):

                    # streamlit_app.py is at project root,
                    # so relative imports here are suspicious.
                    raise ImportError(
                        "Relative import found in "
                        "root-level streamlit_app.py: "
                        f"{description}"
                    )

                imported = importlib.import_module(
                    module_name
                )

                for alias in node.names:

                    if alias.name == "*":
                        continue

                    if not hasattr(
                        imported,
                        alias.name,
                    ):

                        raise ImportError(
                            f"cannot import name "
                            f"'{alias.name}' "
                            f"from '{module_name}'"
                        )

            success(
                "Import succeeded."
            )

        except Exception as exc:

            all_ok = False

            failure(
                "Import failed."
            )

            print()
            print("Exact import:")
            print(
                f"    {description}"
            )

            print()
            print("Source location:")
            print(
                f"    File: {STREAMLIT_APP}"
            )
            print(
                f"    Line: {line}"
            )
            print(
                f"    Column: {column}"
            )

            report_exception(
                exc,
                source_file=STREAMLIT_APP,
                fallback_line=line,
            )

    return all_ok


# ============================================================
# SAFE DEFINITION LOAD
# ============================================================

def check_definitions(
    tree: ast.Module,
) -> bool:
    """
    Execute imports + definitions only.

    This DOES NOT execute the application's UI startup.
    """

    header(
        "4. Loading streamlit_app.py definitions safely"
    )

    transformer = SafeStreamlitTransformer()

    safe_tree = transformer.visit(
        ast.fix_missing_locations(tree)
    )

    safe_tree = ast.fix_missing_locations(
        safe_tree
    )

    try:

        code = compile(
            safe_tree,
            filename=str(STREAMLIT_APP),
            mode="exec",
        )

    except Exception as exc:

        failure(
            "Could not compile the safe application AST."
        )

        report_exception(
            exc,
            source_file=STREAMLIT_APP,
        )

        return False

    namespace = {
        "__name__": (
            "creative_studios_preflight"
        ),
        "__file__": str(
            STREAMLIT_APP
        ),
        "__package__": None,
    }

    try:

        exec(
            code,
            namespace,
        )

        success(
            "Function/class definitions loaded successfully."
        )

    except Exception as exc:

        failure(
            "A definition/decorator/import-related operation failed."
        )

        report_exception(
            exc,
            source_file=STREAMLIT_APP,
        )

        return False

    print()
    print("Discovered application symbols:")

    symbols = sorted(
        name
        for name in namespace
        if not name.startswith("__")
    )

    if symbols:

        for name in symbols:
            print(
                f"    {name}"
            )

    else:

        warning(
            "No application symbols were discovered."
        )

    return True


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    header(
        "CREATIVE STUDIOS IMPORT PREFLIGHT"
    )

    print(
        f"Project root: {ROOT}"
    )

    print(
        f"Application: {STREAMLIT_APP}"
    )

    print()
    print(
        "IMPORTANT: Streamlit UI startup will NOT be executed."
    )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    if not check_database():

        header(
            "RESULT: FAILED"
        )

        print(
            "modules.database must be fixed first."
        )

        return 1

    # --------------------------------------------------------
    # AST
    # --------------------------------------------------------

    tree = parse_streamlit_app()

    if tree is None:

        header(
            "RESULT: FAILED"
        )

        return 1

    # --------------------------------------------------------
    # IMPORTS
    # --------------------------------------------------------

    imports_ok = check_app_imports(
        tree
    )

    if not imports_ok:

        header(
            "RESULT: FAILED"
        )

        print(
            "One or more streamlit_app.py imports failed."
        )

        return 1

    # --------------------------------------------------------
    # DEFINITIONS
    # --------------------------------------------------------

    definitions_ok = check_definitions(
        tree
    )

    if not definitions_ok:

        header(
            "RESULT: FAILED"
        )

        return 1

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    header(
        "RESULT: SUCCESS"
    )

    print(
        "modules.database is valid."
    )

    print(
        "streamlit_app.py syntax is valid."
    )

    print(
        "streamlit_app.py imports are valid."
    )

    print(
        "streamlit_app.py definitions loaded."
    )

    print()
    print(
        "Streamlit UI startup was NOT executed."
    )

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )