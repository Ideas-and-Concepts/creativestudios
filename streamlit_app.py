"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from modules import site_logs

from __future__ import annotations

import hashlib
import hmac
import html
from typing import Any

import streamlit as st

from modules import (
    approvals,
    branding,
    documents,
    drawings,
    projects,
    rfis,
    tasks,
)

from modules.database import load_memory


# ============================================================
# PAGE CONFIGURATION
# ============================================================

BASE_DIR = branding.BASE_DIR
LOGO_PATH = branding.LOGO_PATH

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------
# CSS INJECTION (fallback-safe)
# ------------------------------------------------------------
def _inject_fallback_css() -> None:
    """Minimal CSS fallback if branding.inject_branding_css is unavailable."""
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #05070B;
            color: #F8FAFC;
        }
        [data-testid="stSidebar"] {
            background: #080B12;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


if hasattr(branding, "inject_branding_css"):
    branding.inject_branding_css()
else:
    _inject_fallback_css()


# ============================================================
# BRANDING
# ============================================================

render_logo = branding.render_logo
render_module_header = branding.render_module_header


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """Initialize application session state."""

    defaults = {
        "authenticated": False,
        "user": None,
        "active_module": "Overview",
        "database": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================
# DATABASE
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Load or initialize the application database.

    The database is loaded only once per session.
    On subsequent reruns, the existing session state is preserved.
    """
    if st.session_state.database is None:
        st.session_state.database = load_memory()
    return st.session_state.database


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def _hash_password(password: str) -> str:
    """Create a SHA-256 hash of a password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _password_matches(stored: str, provided: str) -> bool:
    """
    Compare a stored password (or hash) with a user-provided password.

    Supports:
    - Plaintext passwords (legacy users)
    - SHA-256 hashes
    """
    if not stored:
        return False

    # Backwards compatibility: plaintext comparison
    if stored == provided:
        return True

    # If stored value looks like a SHA-256 hash, compare hashes
    if len(stored) == 64 and all(c in "0123456789abcdef" for c in stored.lower()):
        return hmac.compare_digest(_hash_password(provided), stored.lower())

    return False


def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """Authenticate a user."""

    username = str(username or "").strip()
    password = str(password or "").strip()

    users = database.get("users", [])

    if not isinstance(users, list):
        return None

    for user in users:
        if not isinstance(user, dict):
            continue

        stored_username = str(user.get("username", "")).strip()
        stored_password = str(
            user.get("password", user.get("password_hash", ""))
        )

        if stored_username != username:
            continue

        if not _password_matches(stored_password, password):
            continue

        if user.get("active", True) is False:
            return None

        return user

    return None


# ============================================================
# LOGIN
# ============================================================

def render_login(database: dict[str, Any]) -> None:
    """Render the logo-only Creative Studios login."""

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGO ONLY
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-login-logo">',
        unsafe_allow_html=True,
    )

    render_logo(width=100)

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # FORM
    # --------------------------------------------------------

    with st.form("creative_studios_login", clear_on_submit=False):
        username = st.text_input(
            "Username",
            placeholder="Enter username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

        if submitted:
            user = authenticate_user(username, password, database)

            if user is not None:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.active_module = "Overview"
                st.rerun()
            else:
                st.markdown(
                    """
                    <div class="cs-login-error">
                        Invalid username or password.
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown(
        """
        <div class="cs-login-footer">
            Creative Studios • AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """
    Render the sidebar logo and workspace identity.

    Logo rendering is handled by branding.render_logo().
    """

    logo_col, text_col = st.sidebar.columns([1, 3])

    with logo_col:
        render_logo(width=44)

    with text_col:
        st.markdown(
            """
            <div class="cs-sidebar-name">
                Creative Studios
            </div>

            <div class="cs-sidebar-subtitle">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        '<div class="cs-sidebar-divider"></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """Render the application navigation."""

    user = st.session_state.get("user") or {}

    render_sidebar_branding()

    st.sidebar.markdown(
        """
        <div class="cs-section-label">
            Module Navigation
        </div>
        """,
        unsafe_allow_html=True,
    )

    navigation = [
        ("Overview", "Overview"),
        ("Projects", "Project Directory"),
        ("Documents", "Documents"),
        ("Drawings", "Drawings"),
        ("RFIs", "RFIs"),
        ("Tasks", "Tasks"),
        ("Approvals", "Approvals"),
        ("BOQ", "Bill of Quantities"),
        ("Site Logs", "Site Logs"),
        ("Team", "Team"),
    ]

    current_module = st.session_state.get("active_module", "Overview")

    for module_key, label in navigation:
        if module_key == current_module:
            st.sidebar.markdown(
                f"""
                <div class="cs-active-module">
                    <span class="cs-active-indicator">●</span>
                    {html.escape(label)}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            if st.sidebar.button(
                label,
                key=f"nav_{module_key}",
                use_container_width=True,
            ):
                st.session_state.active_module = module_key
                st.rerun()

    # --------------------------------------------------------
    # ADMINISTRATION
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-section-label">
            Administration
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Settings button with active state
    if current_module == "Settings":
        st.sidebar.markdown(
            """
            <div class="cs-active-module">
                <span class="cs-active-indicator">●</span>
                Settings
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        if st.sidebar.button(
            "Settings",
            key="nav_settings",
            use_container_width=True,
        ):
            st.session_state.active_module = "Settings"
            st.rerun()

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

    full_name = str(
        user.get("full_name", user.get("name", ""))
        or "System Administrator"
    ).strip()

    username = str(user.get("username", "") or "admin").strip()
    role = str(user.get("role", "") or "Admin").strip()

    safe_full_name = html.escape(full_name)
    safe_username = html.escape(username)
    safe_role = html.escape(role)

    st.sidebar.markdown(
        f"""
        <div class="cs-user-card">

            <div class="user-label">
                Signed In
            </div>

            <div class="user-name">
                {safe_full_name}
            </div>

            <div class="user-login">
                @{safe_username}
            </div>

            <div class="user-role">
                {safe_role}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.write("")

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.active_module = "Overview"
        st.rerun()

    return current_module


# ============================================================
# SAFE NUMBER
# ============================================================

def _safe_float(value: Any) -> float:
    """Safely convert a value to float."""
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# OVERVIEW
# ============================================================

def render_overview(database: dict[str, Any]) -> None:
    """Render the AEC Workspace overview."""

    projects_data = database.get("projects", [])

    if not isinstance(projects_data, list):
        projects_data = []

    total_projects = len(projects_data)
    active_projects = 0
    planning_projects = 0
    completed_projects = 0
    total_budget = 0.0

    for project in projects_data:
        if not isinstance(project, dict):
            continue

        status = str(project.get("status", "")).strip().lower()

        if status == "active":
            active_projects += 1
        elif status == "planning":
            planning_projects += 1
        elif status == "completed":
            completed_projects += 1

        total_budget += _safe_float(
            project.get(
                "estimated_budget",
                project.get("budget", 0),
            )
        )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    render_module_header(
        "AEC Workspace",
        "Central workspace for architectural, "
        "engineering and construction activities.",
    )

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    metrics = [
        ("Projects", str(total_projects)),
        ("Active", str(active_projects)),
        ("Planning", str(planning_projects)),
        ("Completed", str(completed_projects)),
        ("Total Budget", f"${total_budget:,.2f}"),
    ]

    columns = st.columns(5, gap="small")

    for column, (label, value) in zip(columns, metrics):
        with column:
            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {html.escape(label)}
                    </div>

                    <div class="cs-kpi-value">
                        {html.escape(value)}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    # --------------------------------------------------------
    # WORKSPACE OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-card">

            <div class="cs-card-title">
                Workspace Overview
            </div>

            <div class="cs-card-subtitle">
                Use the navigation panel to manage
                projects, documents, drawings, RFIs,
                tasks and approvals.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:
    """Render a placeholder module."""

    render_module_header(title, description)

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-label">
                Module
            </div>

            <div class="cs-card-title">
                {html.escape(title)}
            </div>

            <div class="cs-card-subtitle">
                {html.escape(description)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SETTINGS
# ============================================================

def render_settings() -> None:
    """Render settings."""

    render_module_header(
        "Settings",
        "Creative Studios workspace configuration.",
    )

    user = st.session_state.get("user") or {}

    full_name = str(
        user.get("full_name", user.get("name", ""))
        or "System Administrator"
    ).strip()

    username = str(user.get("username", "") or "admin").strip()
    role = str(user.get("role", "") or "Admin").strip()

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                Current User
            </div>

            <div class="cs-setting-row">
                Name:
                <strong>
                    {html.escape(full_name)}
                </strong>
            </div>

            <div class="cs-setting-row">
                Username:
                <strong>
                    @{html.escape(username)}
                </strong>
            </div>

            <div class="cs-setting-row">
                Role:
                <strong>
                    {html.escape(role)}
                </strong>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# ROUTER
# ============================================================

def render_active_module(
    module_name: str,
    database: dict[str, Any],
) -> None:
    """
    Route the selected module.

    All six modules are imported directly.
    """

    if module_name == "Overview":
        render_overview(database)

    elif module_name == "Projects":
        projects.render_projects_module(database)

    elif module_name == "Documents":
        documents.render_documents_module(database)

    elif module_name == "Drawings":
        drawings.render_drawings_module(database)

    elif module_name == "RFIs":
        rfis.render_rfis_module(database)

    elif module_name == "Tasks":
        tasks.render_tasks_module(database)

    elif module_name == "Approvals":
        approvals.render_approvals_module(database)

    elif module_name == "Settings":
        render_settings()

    elif module_name == "BOQ":
        render_placeholder(
            "Bill of Quantities",
            "Manage quantities, costs and project estimates.",
        )

    elif module_name == "Site Logs":
        render_placeholder(
            "Site Logs",
            "Record daily construction site activity.",
        )

    elif module_name == "Team":
        render_placeholder(
            "Team",
            "Manage project team members and responsibilities.",
        )

    else:
        st.session_state.active_module = "Overview"
        render_overview(database)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()

    try:
        database = get_database()
    except Exception as exc:
        st.error(f"Unable to load workspace data: {exc}")
        st.stop()

    if not st.session_state.authenticated:
        try:
            render_login(database)
        except Exception as exc:
            st.error(f"Error rendering login: {exc}")
        return

    try:
        active_module = render_sidebar()
        render_active_module(active_module, database)
    except Exception as exc:
        st.error(f"An error occurred: {exc}")


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()