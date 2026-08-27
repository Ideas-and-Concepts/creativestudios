"""
Creative Studios
Architecture • Engineering • Construction

Main Streamlit application entry point.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from modules import (
    approvals,
    auth,
    boq,
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
# GLOBAL BRANDING
# ============================================================

def initialize_branding() -> None:
    """Apply Creative Studios global branding."""

    inject_css = getattr(
        branding,
        "inject_branding_css",
        None,
    )

    if callable(inject_css):
        inject_css()
        return

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #05070B;
            color: #F8FAFC;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #080B12;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


initialize_branding()


# ============================================================
# BRANDING HELPERS
# ============================================================

render_logo = branding.render_logo
render_module_header = branding.render_module_header


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APPLICATION_NAME = "Creative Studios"
APPLICATION_SUBTITLE = "Architecture • Engineering • Construction"


NAVIGATION = [
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
    """

    database = st.session_state.get("database")

    if isinstance(database, dict):
        return database

    database = load_memory()

    if not isinstance(database, dict):
        database = {}

    st.session_state["database"] = database

    return database


# ============================================================
# LOGIN
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:
    """Render the Creative Studios login screen."""

    _, center, _ = st.columns([1, 2, 1])

    with center:

        # ----------------------------------------------------
        # Logo
        # ----------------------------------------------------

        st.markdown(
            '<div style="text-align:center;">',
            unsafe_allow_html=True,
        )

        try:
            render_logo(width=150)

        except Exception:

            if LOGO_PATH.exists():
                st.image(
                    str(LOGO_PATH),
                    width=150,
                )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # Application identity
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div style="
                text-align: center;
                margin-top: 8px;
                margin-bottom: 24px;
            ">

                <div style="
                    color: #FFFFFF;
                    font-size: 28px;
                    font-weight: 800;
                    line-height: 1.2;
                ">
                    {html.escape(APPLICATION_NAME)}
                </div>

                <div style="
                    color: #64748B;
                    font-size: 14px;
                    margin-top: 5px;
                ">
                    {html.escape(APPLICATION_SUBTITLE)}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # Login form
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

        if not submitted:
            return

        # Authentication is delegated to auth.py.
        try:
            authenticated, user = auth.login_user(
                database,
                username,
                password,
            )

        except Exception as exc:
            st.error(
                f"Authentication error: {exc}"
            )
            return

        if not authenticated:
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
    """Render sidebar logo and workspace identity."""

    logo_col, text_col = st.sidebar.columns(
        [1, 3]
    )

    with logo_col:

        try:
            render_logo(width=44)

        except Exception:

            if LOGO_PATH.exists():
                st.image(
                    str(LOGO_PATH),
                    width=44,
                )

    with text_col:

        st.markdown(
            f"""
            <div class="cs-sidebar-name">
                {html.escape(APPLICATION_NAME)}
            </div>

            <div class="cs-sidebar-subtitle">
                {html.escape(APPLICATION_SUBTITLE)}
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

    user = auth.get_current_user()

    if not isinstance(user, dict):
        user = {}

    render_sidebar_branding()

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Module Navigation"
        "</div>",
        unsafe_allow_html=True,
    )

    current_module = st.session_state.get(
        "active_module",
        "Overview",
    )

    if not isinstance(
        current_module,
        str,
    ):
        current_module = "Overview"

    valid_modules = {
        module_key
        for module_key, _ in NAVIGATION
    }

    valid_modules.add("Settings")

    if current_module not in valid_modules:

        current_module = "Overview"

        st.session_state[
            "active_module"
        ] = current_module

    # --------------------------------------------------------
    # Main navigation
    # --------------------------------------------------------

    for module_key, label in NAVIGATION:

        if module_key == current_module:

            st.sidebar.markdown(
                f"""
                <div class="cs-active-module">

                    <span class="cs-active-indicator">
                        ●
                    </span>

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
    # Administration
    # --------------------------------------------------------

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Administration"
        "</div>",
        unsafe_allow_html=True,
    )

    if current_module == "Settings":

        st.sidebar.markdown(
            """
            <div class="cs-active-module">

                <span class="cs-active-indicator">
                    ●
                </span>

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
    # User card
    # --------------------------------------------------------

    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "System Administrator",
            ),
        )
        or "System Administrator"
    ).strip()

    username = str(
        user.get(
            "username",
            "admin",
        )
        or "admin"
    ).strip()

    role = str(
        user.get(
            "role",
            "Admin",
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

    # --------------------------------------------------------
    # Sign out
    # --------------------------------------------------------

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        try:
            auth.logout_user()
        except Exception:
            pass

        st.session_state[
            "authenticated"
        ] = False

        st.session_state[
            "user"
        ] = None

        st.session_state[
            "active_module"
        ] = "Overview"

        st.session_state[
            "database"
        ] = None

        st.rerun()

    return current_module


# ============================================================
# SAFE NUMBER
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

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0


# ============================================================
# OVERVIEW
# ============================================================

def render_overview(
    database: dict[str, Any],
) -> None:
    """Render the Creative Studios workspace overview."""

    projects_data = database.get(
        "projects",
        [],
    )

    if not isinstance(
        projects_data,
        list,
    ):
        projects_data = []

    total_projects = len(
        projects_data
    )

    active_projects = 0
    planning_projects = 0
    completed_projects = 0
    total_budget = 0.0

    for project in projects_data:

        if not isinstance(
            project,
            dict,
        ):
            continue

        status = str(
            project.get(
                "status",
                "",
            )
            or ""
        ).strip().lower()

        if status == "active":
            active_projects += 1

        elif status == "planning":
            planning_projects += 1

        elif status == "completed":
            completed_projects += 1

        total_budget += _safe_float(
            project.get(
                "estimated_budget",
                project.get(
                    "budget",
                    0,
                ),
            )
        )

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    render_module_header(
        "AEC Workspace",
        (
            "Central workspace for "
            "architecture, engineering "
            "and construction activities."
        ),
    )

    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    metrics = [
        (
            "Projects",
            str(total_projects),
        ),
        (
            "Active",
            str(active_projects),
        ),
        (
            "Planning",
            str(planning_projects),
        ),
        (
            "Completed",
            str(completed_projects),
        ),
        (
            "Total Budget",
            f"${total_budget:,.2f}",
        ),
    ]

    columns = st.columns(
        5,
        gap="small",
    )

    for column, (
        label,
        value,
    ) in zip(
        columns,
        metrics,
    ):

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
    # Workspace card
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-card">

            <div class="cs-card-title">
                Creative Studios Workspace
            </div>

            <div class="cs-card-subtitle">
                Manage projects, documents, drawings,
                RFIs, tasks, approvals, bills of
                quantities and site activities from
                one integrated AEC workspace.
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
    """Render a temporary module placeholder."""

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
    """Render Creative Studios settings."""

    render_module_header(
        "Settings",
        "Creative Studios workspace configuration.",
    )

    user = auth.get_current_user()

    if not isinstance(
        user,
        dict,
    ):
        user = {}

    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "System Administrator",
            ),
        )
        or "System Administrator"
    ).strip()

    username = str(
        user.get(
            "username",
            "admin",
        )
        or "admin"
    ).strip()

    role = str(
        user.get(
            "role",
            "Admin",
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
    """Route the selected module."""

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

        boq.render_boq_module(
            database
        )

    elif module_name == "Site Logs":

        site_logs.render_site_logs_module(
            database
        )

    elif module_name == "Team":

        render_placeholder(
            "Team",
            (
                "Manage project team members, "
                "responsibilities and workspace access."
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

    # --------------------------------------------------------
    # Session
    # --------------------------------------------------------

    initialize_session_state()

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            "Unable to load workspace data: "
            f"{exc}"
        )

        st.stop()

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    try:

        authenticated = auth.is_authenticated()

    except Exception:

        authenticated = bool(
            st.session_state.get(
                "authenticated",
                False,
            )
        )

    if not authenticated:

        try:

            render_login(
                database
            )

        except Exception as exc:

            st.error(
                "Error rendering login: "
                f"{exc}"
            )

        return

    # --------------------------------------------------------
    # Authenticated workspace
    # --------------------------------------------------------

    try:

        active_module = render_sidebar()

        render_active_module(
            active_module,
            database,
        )

    except Exception as exc:

        st.error(
            "An error occurred: "
            f"{exc}"
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()