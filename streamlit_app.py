"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import html
import mimetypes
from typing import Any

import streamlit as st

from modules import (
    approvals,
    branding,
    documents,
    drawings,
    projects,
    rfis,
    site_logs,
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


# ============================================================
# BRANDING
# ============================================================

if hasattr(branding, "inject_branding_css"):
    branding.inject_branding_css()
else:
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


render_logo = branding.render_logo
render_module_header = branding.render_module_header


# ============================================================
# LOGIN CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       LOGIN BRANDING
       ====================================================== */

    .cs-login-brand {
        width: 100%;
        text-align: center;
        margin: 0 auto 28px auto;
    }

    .cs-login-brand img {
        display: block;
        width: 150px;
        max-width: 150px;
        height: auto;
        margin: 0 auto 16px auto;
    }

    .cs-login-brand-title {
        width: 100%;
        color: #FFFFFF;
        font-size: 28px;
        font-weight: 800;
        line-height: 1.2;
        text-align: center;
        margin: 0;
    }

    .cs-login-brand-subtitle {
        width: 100%;
        color: #64748B;
        font-size: 14px;
        line-height: 1.4;
        text-align: center;
        margin-top: 6px;
    }


    /* ======================================================
       OVERVIEW
       ====================================================== */

    .cs-overview-card {
        background: #0B0F17;
        border: 1px solid #172033;
        border-radius: 15px;
        padding: 22px;
        margin-top: 12px;
        width: 100%;
        box-sizing: border-box;
    }

    .cs-overview-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 850;
        line-height: 1.3;
    }

    .cs-overview-subtitle {
        color: #64748B;
        font-size: 13px;
        line-height: 1.6;
        margin-top: 7px;
    }


    /* ======================================================
       ACTIVE SIDEBAR MODULE
       ====================================================== */

    .cs-active-module-clean {
        width: 100%;
        box-sizing: border-box;
        background: #172554;
        border: 1px solid #2563EB;
        border-radius: 9px;
        color: #FFFFFF;
        padding: 0.55rem 0.75rem;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """Initialize application session state."""

    defaults: dict[str, Any] = {
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
    Load the application database once per Streamlit session.

    The database module already normalizes the JSON structure,
    so this function only guarantees that the returned value
    is a dictionary.
    """

    database = st.session_state.get("database")

    if database is None:
        database = load_memory()

        if not isinstance(database, dict):
            database = {}

        st.session_state["database"] = database

    return database


# ============================================================
# AUTHENTICATION
# ============================================================

def _hash_password(password: str) -> str:
    """Create a SHA-256 password hash."""

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def _password_matches(
    stored: str,
    provided: str,
) -> bool:
    """
    Compare a stored password with the supplied password.

    Supports:
    - Plain-text passwords used by the current local JSON database.
    - SHA-256 password hashes.
    """

    stored = str(stored or "")
    provided = str(provided or "")

    if not stored:
        return False

    # Current JSON database supports plain text.
    if hmac.compare_digest(
        stored,
        provided,
    ):
        return True

    # SHA-256 support.
    stored_lower = stored.lower()

    if (
        len(stored_lower) == 64
        and all(
            character in "0123456789abcdef"
            for character in stored_lower
        )
    ):
        return hmac.compare_digest(
            _hash_password(provided),
            stored_lower,
        )

    return False


def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """Authenticate a user from the application database."""

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:
        return None

    users = database.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        return None

    for user in users:

        if not isinstance(
            user,
            dict,
        ):
            continue

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        if stored_username != username:
            continue

        stored_password = str(
            user.get(
                "password",
                user.get(
                    "password_hash",
                    "",
                ),
            )
        )

        if not _password_matches(
            stored_password,
            password,
        ):
            continue

        if user.get(
            "active",
            True,
        ) is False:
            return None

        return user

    return None


# ============================================================
# LOGIN LOGO
# ============================================================

def _get_logo_data_uri() -> str | None:
    """
    Convert the application logo into a data URI.

    This lets the logo, title and subtitle exist inside the
    same HTML block, guaranteeing true visual centering.
    """

    try:
        if not LOGO_PATH.exists():
            return None

        logo_bytes = LOGO_PATH.read_bytes()

        if not logo_bytes:
            return None

        mime_type = (
            mimetypes.guess_type(
                str(LOGO_PATH)
            )[0]
            or "image/png"
        )

        encoded = base64.b64encode(
            logo_bytes
        ).decode("ascii")

        return (
            f"data:{mime_type};base64,{encoded}"
        )

    except Exception:
        return None


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:
    """
    Render the Creative Studios login page.

    The logo and both branding lines are rendered as one
    centered HTML component instead of separate Streamlit
    columns/components.
    """

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        logo_data_uri = _get_logo_data_uri()

        if logo_data_uri:

            st.markdown(
                f"""
                <div class="cs-login-brand">

                    <img
                        src="{logo_data_uri}"
                        alt="Creative Studios Logo"
                    >

                    <div class="cs-login-brand-title">
                        Creative Studios
                    </div>

                    <div class="cs-login-brand-subtitle">
                        Architecture • Engineering • Construction
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="cs-login-brand">

                    <div class="cs-login-brand-title">
                        Creative Studios
                    </div>

                    <div class="cs-login-brand-subtitle">
                        Architecture • Engineering • Construction
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.warning(
                f"Logo not found: {LOGO_PATH}"
            )

        # ----------------------------------------------------
        # LOGIN FORM
        # ----------------------------------------------------

        with st.form(
            "creative_studios_login",
            clear_on_submit=False,
        ):

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

            user = authenticate_user(
                username,
                password,
                database,
            )

            if user is None:

                st.error(
                    "Invalid username or password."
                )

                return

            st.session_state["authenticated"] = True
            st.session_state["user"] = user
            st.session_state["active_module"] = "Overview"

            st.rerun()


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """Render sidebar workspace branding."""

    logo_col, text_col = st.sidebar.columns(
        [1, 3]
    )

    with logo_col:

        render_logo(
            width=44
        )

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
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar() -> str:
    """Render application navigation."""

    user = (
        st.session_state.get("user")
        or {}
    )

    render_sidebar_branding()

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        'Module Navigation'
        '</div>',
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

    current_module = str(
        st.session_state.get(
            "active_module",
            "Overview",
        )
    )

    for module_key, label in navigation:

        if module_key == current_module:

            # Deliberately avoid the previous
            # cs-active-indicator HTML.
            st.sidebar.markdown(
                f"""
                <div class="cs-active-module-clean">
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

                st.session_state[
                    "active_module"
                ] = module_key

                st.rerun()

    # --------------------------------------------------------
    # ADMINISTRATION
    # --------------------------------------------------------

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        'Administration'
        '</div>',
        unsafe_allow_html=True,
    )

    if current_module == "Settings":

        st.sidebar.markdown(
            """
            <div class="cs-active-module-clean">
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

            st.session_state[
                "active_module"
            ] = "Settings"

            st.rerun()

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "",
            ),
        )
        or "System Administrator"
    ).strip()

    username = str(
        user.get(
            "username",
            "",
        )
        or "admin"
    ).strip()

    role = str(
        user.get(
            "role",
            "",
        )
        or "Admin"
    ).strip()

    st.sidebar.markdown(
        f"""
        <div class="cs-user-card">

            <div class="user-label">
                Signed In
            </div>

            <div class="user-name">
                {html.escape(full_name)}
            </div>

            <div class="user-login">
                @{html.escape(username)}
            </div>

            <div class="user-role">
                {html.escape(role)}
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

        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["active_module"] = "Overview"

        st.rerun()

    return current_module


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(
    value: Any,
) -> float:
    """Safely convert a value to float."""

    if value is None:
        return 0.0

    if isinstance(
        value,
        bool,
    ):
        return float(value)

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    try:
        cleaned = str(
            value
        ).replace(
            ",",
            "",
        ).strip()

        if not cleaned:
            return 0.0

        return float(cleaned)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


def _safe_status(
    value: Any,
) -> str:
    """Normalize project status."""

    return str(
        value or ""
    ).strip().lower()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview(
    database: dict[str, Any],
) -> None:
    """
    Render the main Creative Studios workspace overview.

    Uses native Streamlit metrics rather than HTML KPI markup.
    This avoids the visual/runtime issues previously seen with
    cs-kpi-label and cs-kpi-value.
    """

    projects_data = database.get(
        "projects",
        [],
    )

    if not isinstance(
        projects_data,
        list,
    ):
        projects_data = []

    valid_projects: list[dict[str, Any]] = [
        project
        for project in projects_data
        if isinstance(
            project,
            dict,
        )
    ]

    total_projects = len(
        valid_projects
    )

    active_projects = sum(
        1
        for project in valid_projects
        if _safe_status(
            project.get("status")
        ) == "active"
    )

    planning_projects = sum(
        1
        for project in valid_projects
        if _safe_status(
            project.get("status")
        ) == "planning"
    )

    completed_projects = sum(
        1
        for project in valid_projects
        if _safe_status(
            project.get("status")
        ) == "completed"
    )

    total_budget = sum(
        _safe_float(
            project.get(
                "estimated_budget",
                project.get(
                    "budget",
                    0,
                ),
            )
        )
        for project in valid_projects
    )

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    render_module_header(
        "AEC Workspace",
        (
            "Central workspace for architectural, "
            "engineering and construction activities."
        ),
    )

    # --------------------------------------------------------
    # KPI ROW
    # --------------------------------------------------------

    metric_columns = st.columns(
        5,
        gap="small",
    )

    with metric_columns[0]:
        st.metric(
            "Projects",
            total_projects,
        )

    with metric_columns[1]:
        st.metric(
            "Active",
            active_projects,
        )

    with metric_columns[2]:
        st.metric(
            "Planning",
            planning_projects,
        )

    with metric_columns[3]:
        st.metric(
            "Completed",
            completed_projects,
        )

    with metric_columns[4]:
        st.metric(
            "Total Budget",
            f"${total_budget:,.2f}",
        )

    st.write("")

    # --------------------------------------------------------
    # WORKSPACE CARD
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-overview-card">

            <div class="cs-overview-title">
                Creative Studios Workspace
            </div>

            <div class="cs-overview-subtitle">
                Manage projects, documents, drawings,
                RFIs, tasks, approvals, bills of
                quantities and site activities from
                one integrated AEC workspace.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # PROJECT SNAPSHOT
    # --------------------------------------------------------

    st.write("")

    st.subheader(
        "Project Snapshot"
    )

    if not valid_projects:

        st.info(
            "No projects have been created yet."
        )

        return

    snapshot_columns = st.columns(
        3,
        gap="medium",
    )

    # Active
    with snapshot_columns[0]:

        st.markdown(
            "### Active Projects"
        )

        active_list = [
            project
            for project in valid_projects
            if _safe_status(
                project.get("status")
            ) == "active"
        ]

        if not active_list:

            st.caption(
                "No active projects."
            )

        else:

            for project in active_list[:5]:

                name = str(
                    project.get(
                        "name",
                        "Unnamed Project",
                    )
                    or "Unnamed Project"
                )

                st.write(
                    f"• {name}"
                )

    # Planning
    with snapshot_columns[1]:

        st.markdown(
            "### Planning"
        )

        planning_list = [
            project
            for project in valid_projects
            if _safe_status(
                project.get("status")
            ) == "planning"
        ]

        if not planning_list:

            st.caption(
                "No planning projects."
            )

        else:

            for project in planning_list[:5]:

                name = str(
                    project.get(
                        "name",
                        "Unnamed Project",
                    )
                    or "Unnamed Project"
                )

                st.write(
                    f"• {name}"
                )

    # Completed
    with snapshot_columns[2]:

        st.markdown(
            "### Completed"
        )

        completed_list = [
            project
            for project in valid_projects
            if _safe_status(
                project.get("status")
            ) == "completed"
        ]

        if not completed_list:

            st.caption(
                "No completed projects."
            )

        else:

            for project in completed_list[:5]:

                name = str(
                    project.get(
                        "name",
                        "Unnamed Project",
                    )
                    or "Unnamed Project"
                )

                st.write(
                    f"• {name}"
                )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:
    """Render a safe placeholder module."""

    render_module_header(
        title,
        description,
    )

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
    """Render workspace settings."""

    render_module_header(
        "Settings",
        "Creative Studios workspace configuration.",
    )

    user = (
        st.session_state.get("user")
        or {}
    )

    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "",
            ),
        )
        or "System Administrator"
    ).strip()

    username = str(
        user.get(
            "username",
            "",
        )
        or "admin"
    ).strip()

    role = str(
        user.get(
            "role",
            "",
        )
        or "Admin"
    ).strip()

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
# MODULE ROUTER
# ============================================================

def render_active_module(
    module_name: str,
    database: dict[str, Any],
) -> None:
    """Route the selected module to its renderer."""

    if module_name == "Overview":

        render_overview(
            database
        )

    elif module_name == "Projects":

        projects.render_projects_module(
            database
        )

    elif module_name == "Documents":

        documents.render_documents_module(
            database
        )

    elif module_name == "Drawings":

        drawings.render_drawings_module(
            database
        )

    elif module_name == "RFIs":

        rfis.render_rfis_module(
            database
        )

    elif module_name == "Tasks":

        tasks.render_tasks_module(
            database
        )

    elif module_name == "Approvals":

        approvals.render_approvals_module(
            database
        )

    elif module_name == "BOQ":

        render_placeholder(
            "Bill of Quantities",
            (
                "Manage quantities, costs "
                "and project estimates."
            ),
        )

    elif module_name == "Site Logs":

        site_logs.render_site_logs_module(
            database
        )

    elif module_name == "Team":

        render_placeholder(
            "Team",
            (
                "Manage project team members "
                "and responsibilities."
            ),
        )

    elif module_name == "Settings":

        render_settings()

    else:

        st.session_state[
            "active_module"
        ] = "Overview"

        render_overview(
            database
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Creative Studios."""

    initialize_session_state()

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            "Unable to load workspace data."
        )

        st.exception(exc)

        st.stop()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    if not st.session_state.get(
        "authenticated",
        False,
    ):

        render_login(
            database
        )

        return

    # --------------------------------------------------------
    # APPLICATION
    # --------------------------------------------------------

    try:

        active_module = render_sidebar()

        render_active_module(
            active_module,
            database,
        )

    except Exception as exc:

        st.error(
            "An error occurred while "
            "rendering the workspace."
        )

        st.exception(exc)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()