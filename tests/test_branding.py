"""
Creative Studios
Branding / Authentication Branch Tests

Verifies:

1. The global CSS marker block exists.
2. CSS is injected before branding renderers are defined.
3. render_login_brand() exists.
4. render_sidebar_brand() exists.
5. The unauthenticated branch calls render_login().
6. The authenticated branch calls render_sidebar().
7. render_login() calls render_login_brand().
8. render_sidebar() calls render_sidebar_brand().

The test does NOT import streamlit_app.py, so Streamlit UI startup
does not occur.
"""

from __future__ import annotations

import ast
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

APP_FILE = ROOT_DIR / "streamlit_app.py"


# ============================================================
# HELPERS
# ============================================================

def load_source() -> str:
    """Load streamlit_app.py as plain text."""

    assert APP_FILE.exists(), (
        f"streamlit_app.py was not found at: {APP_FILE}"
    )

    return APP_FILE.read_text(
        encoding="utf-8"
    )


def load_ast() -> ast.Module:
    """Parse streamlit_app.py without executing it."""

    source = load_source()

    try:
        return ast.parse(
            source,
            filename=str(APP_FILE),
        )

    except SyntaxError as exc:

        raise AssertionError(
            "streamlit_app.py contains a syntax error:\n"
            f"File: {exc.filename}\n"
            f"Line: {exc.lineno}\n"
            f"Column: {exc.offset}\n"
            f"Error: {exc.msg}"
        ) from exc


def get_function(
    tree: ast.Module,
    function_name: str,
) -> ast.FunctionDef:
    """Return a top-level function by name."""

    for node in tree.body:

        if (
            isinstance(node, ast.FunctionDef)
            and node.name == function_name
        ):
            return node

    raise AssertionError(
        f"Function '{function_name}' was not found "
        f"in streamlit_app.py."
    )


def function_contains_call(
    function: ast.FunctionDef,
    function_name: str,
) -> bool:
    """Check whether a function calls another function."""

    for node in ast.walk(function):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        target = node.func

        if (
            isinstance(target, ast.Name)
            and target.id == function_name
        ):
            return True

    return False


def find_call_lines(
    tree: ast.Module,
    function_name: str,
) -> list[int]:
    """
    Find line numbers where a named function is called
    from the top-level application code.
    """

    lines: list[int] = []

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call,
        ):
            continue

        if not isinstance(
            node.func,
            ast.Name,
        ):
            continue

        if node.func.id == function_name:

            lines.append(
                node.lineno
            )

    return sorted(lines)


# ============================================================
# CSS TEST
# ============================================================

def test_css_marker_exists():

    source = load_source()

    assert ".cs-logo" in source, (
        "Login logo CSS marker '.cs-logo' is missing."
    )

    assert ".cs-logo-text" in source, (
        "Login logo text CSS marker is missing."
    )

    assert ".cs-sidebar-logo" in source, (
        "Sidebar logo CSS marker '.cs-sidebar-logo' is missing."
    )

    assert ".cs-sidebar-logo-text" in source, (
        "Sidebar logo text CSS marker is missing."
    )

    assert "unsafe_allow_html=True" in source, (
        "CSS/HTML rendering requires unsafe_allow_html=True."
    )


# ============================================================
# CSS ORDER TEST
# ============================================================

def test_css_is_injected_before_branding_renderers():

    source = load_source()

    css_position = source.find(
        "<style>"
    )

    login_renderer_position = source.find(
        "def render_login_brand"
    )

    sidebar_renderer_position = source.find(
        "def render_sidebar_brand"
    )

    assert css_position != -1, (
        "Global <style> block was not found."
    )

    assert login_renderer_position != -1, (
        "render_login_brand() was not found."
    )

    assert sidebar_renderer_position != -1, (
        "render_sidebar_brand() was not found."
    )

    assert css_position < login_renderer_position, (
        "The CSS marker block must be injected "
        "before render_login_brand() is defined."
    )

    assert css_position < sidebar_renderer_position, (
        "The CSS marker block must be injected "
        "before render_sidebar_brand() is defined."
    )


# ============================================================
# LOGIN BRANDING TEST
# ============================================================

def test_login_branding_renderer_exists_and_is_used():

    tree = load_ast()

    login_brand = get_function(
        tree,
        "render_login_brand",
    )

    assert function_contains_call(
        login_brand,
        "markdown",
    ), (
        "render_login_brand() must use st.markdown() "
        "to render the CSS-based branding."
    )

    render_login = get_function(
        tree,
        "render_login",
    )

    assert function_contains_call(
        render_login,
        "render_login_brand",
    ), (
        "render_login() must call render_login_brand()."
    )


# ============================================================
# SIDEBAR BRANDING TEST
# ============================================================

def test_sidebar_branding_renderer_exists_and_is_used():

    tree = load_ast()

    sidebar_brand = get_function(
        tree,
        "render_sidebar_brand",
    )

    assert function_contains_call(
        sidebar_brand,
        "markdown",
    ), (
        "render_sidebar_brand() must use markdown "
        "to render the branding."
    )

    render_sidebar = get_function(
        tree,
        "render_sidebar",
    )

    assert function_contains_call(
        render_sidebar,
        "render_sidebar_brand",
    ), (
        "render_sidebar() must call render_sidebar_brand()."
    )


# ============================================================
# LOGIN FORM TEST
# ============================================================

def test_login_renderer_contains_login_form():

    tree = load_ast()

    render_login = get_function(
        tree,
        "render_login",
    )

    assert function_contains_call(
        render_login,
        "form",
    ), (
        "render_login() must contain a Streamlit form."
    )

    assert function_contains_call(
        render_login,
        "text_input",
    ), (
        "render_login() must contain text inputs."
    )

    assert function_contains_call(
        render_login,
        "form_submit_button",
    ), (
        "render_login() must contain a login submit button."
    )


# ============================================================
# AUTHENTICATION BRANCH TEST
# ============================================================

def test_authentication_branches_render_correct_ui():

    tree = load_ast()

    source = load_source()

    render_login = get_function(
        tree,
        "render_login",
    )

    render_sidebar = get_function(
        tree,
        "render_sidebar",
    )

    # --------------------------------------------------------
    # Login function exists
    # --------------------------------------------------------

    assert render_login is not None

    # --------------------------------------------------------
    # Sidebar function exists
    # --------------------------------------------------------

    assert render_sidebar is not None

    # --------------------------------------------------------
    # Application must contain authentication state
    # --------------------------------------------------------

    assert "authenticated" in source, (
        "Authentication state was not found."
    )

    # --------------------------------------------------------
    # Application must call render_login()
    # --------------------------------------------------------

    login_calls = find_call_lines(
        tree,
        "render_login",
    )

    assert login_calls, (
        "No call to render_login() was found."
    )

    # --------------------------------------------------------
    # Application must call render_sidebar()
    # --------------------------------------------------------

    sidebar_calls = find_call_lines(
        tree,
        "render_sidebar",
    )

    assert sidebar_calls, (
        "No call to render_sidebar() was found."
    )

    # --------------------------------------------------------
    # Verify application-level authentication branch
    # --------------------------------------------------------

    found_auth_branch = False

    for node in tree.body:

        if not isinstance(
            node,
            ast.If,
        ):
            continue

        # Look for:
        #
        # if not st.session_state.authenticated:
        #
        # or equivalent authentication check.

        condition_source = ast.unparse(
            node.test
        )

        if "authenticated" not in condition_source:
            continue

        branch_calls = []

        for child in node.body:

            for nested in ast.walk(child):

                if isinstance(
                    nested,
                    ast.Call,
                ) and isinstance(
                    nested.func,
                    ast.Name,
                ):

                    branch_calls.append(
                        nested.func.id
                    )

        alternate_calls = []

        for child in node.orelse:

            for nested in ast.walk(child):

                if isinstance(
                    nested,
                    ast.Call,
                ) and isinstance(
                    nested.func,
                    ast.Name,
                ):

                    alternate_calls.append(
                        nested.func.id
                    )

        if (
            "render_login" in branch_calls
            and "render_sidebar" in alternate_calls
        ):

            found_auth_branch = True
            break

    assert found_auth_branch, (
        "Could not verify the expected authentication routing:\n"
        "unauthenticated -> render_login()\n"
        "authenticated   -> render_sidebar()"
    )


# ============================================================
# RERUN SAFETY TEST
# ============================================================

def test_login_rerun_preserves_authentication_state():

    source = load_source()

    assert (
        "st.session_state.authenticated = True"
        in source
    ), (
        "Successful login must set "
        "authenticated=True before rerun."
    )

    assert (
        "st.session_state.user = user"
        in source
    ), (
        "Successful login must store the authenticated "
        "user before rerun."
    )

    assert (
        "st.session_state.active_module = \"Overview\""
        in source
    ), (
        "Successful login should reset the active module "
        "to Overview."
    )

    assert "st.rerun()" in source, (
        "Successful login should rerun the Streamlit app."
    )


# ============================================================
# SESSION DEFAULT SAFETY TEST
# ============================================================

def test_session_defaults_are_not_unconditionally_reset():

    source = load_source()

    assert (
        'if key not in st.session_state'
        in source
    ), (
        "Session defaults should only be assigned when "
        "the key does not already exist."
    )


# ============================================================
# FINAL BRANDING TEST
# ============================================================

def test_complete_branding_contract():

    tree = load_ast()

    source = load_source()

    login_brand = get_function(
        tree,
        "render_login_brand",
    )

    sidebar_brand = get_function(
        tree,
        "render_sidebar_brand",
    )

    # Login renderer
    assert function_contains_call(
        login_brand,
        "markdown",
    )

    # Sidebar renderer
    assert function_contains_call(
        sidebar_brand,
        "markdown",
    )

    # CSS markers
    required_markers = [
        ".cs-logo",
        ".cs-logo-text",
        ".cs-sidebar-logo",
        ".cs-sidebar-logo-text",
        ".cs-brand-name",
        ".cs-brand-subtitle",
        ".cs-sidebar-name",
        ".cs-sidebar-subtitle",
    ]

    for marker in required_markers:

        assert marker in source, (
            f"Required branding marker missing: {marker}"
        )

    # Renderer usage
    render_login = get_function(
        tree,
        "render_login",
    )

    render_sidebar = get_function(
        tree,
        "render_sidebar",
    )

    assert function_contains_call(
        render_login,
        "render_login_brand",
    )

    assert function_contains_call(
        render_sidebar,
        "render_sidebar_brand",
    )