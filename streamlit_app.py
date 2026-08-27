"""
Creative Studios
Architecture • Engineering • Construction

Main Streamlit application.
"""

from __future__ import annotations

from pathlib import Path
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

BASE_DIR = Path(branding.BASE_DIR)
LOGO_PATH = Path(branding.LOGO_PATH)

st.set_page_config(
    page_title="Creative Studios",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BRANDING / CSS
# ============================================================

def initialize_branding() -> None:
    """Initialize Creative Studios branding."""

    inject_css = getattr(
        branding,
        "inject_branding_css",
        None,
    )

    if callable(inject_css):
        try:
            inject_css()
            return
        except Exception:
            pass

    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"] {
            background: #05070B;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #080B12;
        }

        .cs-login-brand {
            text-align: center;
        }

        .cs-login-title {
            color: #FFFFFF;
            font-size: 28px;
            font-weight: 800;
            line-height: 1.2;
            margin-top: 10px;
        }

        .cs-login-subtitle {
            color: #64748B;
            font-size: 14px;
            margin-top: 5px;
            margin-bottom: 24px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


initialize_branding()


# ============================================================
# APPLICATION CONSTANTS
# ============================================================

APPLICATION_NAME = "Creative Studios"

APPLICATION_SUBTITLE = (
    "Architecture • Engineering • Construction"
)

DEFAULT_MODULE = "Overview"

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
        "active_module": DEFAULT_MODULE,
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
# AUTHENTICATION HELPERS
# ============================================================

def _auth_function(
    function_name: str,
):
    """
    Safely retrieve an authentication function.

    This keeps streamlit_app.py compatible with the
    existing modules.auth implementation.
    """

    try:
        from modules import auth

        function = getattr(
            auth,
            function_name,
            None,
        )

        if callable(function):
            return function

    except Exception:
        pass

    return None


def is_authenticated() -> bool:
    """Return the current authentication state."""

    function = _auth_function(
        "is_authenticated"
    )

    if callable(function):
        try:
            return bool(function())
        except Exception:
            pass

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def get_current_user() -> dict[str, Any]:
    """Return the currently authenticated user."""

    function = _auth_function(
        "get_current_user"
    )

    if callable(function):
        try:
            user = function()

            if isinstance(user, dict):
                return user

        except Exception:
            pass

    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):
        return user

    return {}


def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> Any:
    """
    Authenticate using the existing modules.auth implementation.

    Falls back to the database user collection if necessary.
    """

    function = _auth_function(
        "login_user"
    )

    if callable(function):

        try:
            result = function(
                database,
                username,
                password,
            )

            return result

        except TypeError:

            try:
                result = function(
                    username,
                    password,
                    database,
                )

                return result

            except Exception:
                pass

        except Exception:
            pass

    # --------------------------------------------------------
    # Fallback authentication
    # --------------------------------------------------------

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    users = database.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        return None

    import hashlib
    import hmac

    password_hash = hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()

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

        if user.get(
            "active",
            True,
        ) is False:
            return None

        stored_password = str(
            user.get(
                "password",
                user.get(
                    "password_hash",
                    "",
                ),
            )
        )

        password_matches = (
            stored_password == password
            or
            (
                len(stored_password) == 64
                and hmac.compare_digest(
                    password_hash,
                    stored_password.lower(),
                )
            )
        )

        if password_matches:
            return user

    return None


def logout_user() -> None:
    """Log the current user out."""

    function = _auth_function(
        "logout_user"
    )

    if callable(function):

        try:
            function()
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
    ] = DEFAULT_MODULE


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:
    """
    Render the Creative Studios login page.

    The logo is centered using native Streamlit columns.
    """

    st.write("")

    # --------------------------------------------------------
    # Main centered login area
    # --------------------------------------------------------

    left, center, right = st.columns(
        [1, 2, 1],
        gap="small",
    )

    with center:

        # ----------------------------------------------------
        # CENTERED LOGO
        # ----------------------------------------------------

        logo_left, logo_center, logo_right = st.columns(
            [1, 2, 1],
            gap="small",
        )

        with logo_center:

            if LOGO_PATH.exists():

                st.image(
                    str(LOGO_PATH),
                    width=150,
                )

            else:

                st.warning(
                    "Creative Studios logo was not found."
                )

        # ----------------------------------------------------
        # BRAND NAME
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="cs-login-brand">
                <div class="cs-login-title">
                    Creative Studios
                </div>

                <div class="cs-login-subtitle">
                    Architecture • Engineering • Construction
                </div>
            </div>
            """,
            unsafe_allow_html=True,
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

        # ----------------------------------------------------
        # PROCESS LOGIN
        # ----------------------------------------------------

        if not submitted:
            return

        username = str(
            username or ""
        ).strip()

        password = str(
            password or ""
        )

        if not username:

            st.error(
                "Please enter your username."
            )

            return

        if not password:

            st.error(
                "Please enter your password."
            )

            return

        try:

            result = authenticate_user(
                username,
                password,
                database,
            )

        except Exception as exc:

            st.error(
                f"Authentication error: {exc}"
            )

            return

        # ----------------------------------------------------
        # Support both common auth return formats:
        #
        #   user
        #   (authenticated, user)
        # ----------------------------------------------------

        authenticated = False
        user: dict[str, Any] | None = None

        if isinstance(
            result,
            tuple,
        ):

            if len(result) >= 2:

                authenticated = bool(
                    result[0]
                )

                if isinstance(
                    result[1],
                    dict,
                ):
                    user = result[1]

        elif isinstance(
            result,
            dict,
        ):

            user = result
            authenticated = True

        elif isinstance(
            result,
            bool,
        ):

            authenticated = result

            if authenticated:
                user = get_current_user()

        if not authenticated or user is None:

            st.error(
                "Invalid username or password."
            )

            return

        # ----------------------------------------------------
        # Establish session
        # ----------------------------------------------------

        st.session_state[
            "authenticated"
        ] = True

        st.session_state[
            "user"
        ] = user

        st.session_state[
            "active_module"
        ] = DEFAULT_MODULE

        st.rerun()


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """Render sidebar branding."""

    logo_col, text_col = st.sidebar.columns(
        [1, 3],
        gap="small",
    )

    with logo_col:

        render_logo = getattr(
            branding,
            "render_logo",
            None,
        )

        if callable(render_logo):

            try:
                render_logo(
                    width=44
                )

            except Exception:

                if LOGO_PATH.exists():

                    st.image(
                        str(LOGO_PATH),
                        width=44,
                    )

        elif LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=44,
            )

    with text_col:

        st.markdown(
            "**Creative Studios**"
        )

        st.caption(
            "AEC Workspace"
        )

    st.sidebar.divider()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

def render_sidebar() -> str:
    """Render the application navigation."""

    user = get_current_user()

    render_sidebar_branding()

    st.sidebar.caption(
        "MODULE NAVIGATION"
    )

    current_module = st.session_state.get(
        "active_module",
        DEFAULT_MODULE,
    )

    valid_modules = {
        module_key
        for module_key, _ in NAVIGATION
    }

    valid_modules.add(
        "Settings"
    )

    if current_module not in valid_modules:

        current_module = DEFAULT_MODULE

        st.session_state[
            "active_module"
        ] = current_module

    # --------------------------------------------------------
    # Navigation
    # --------------------------------------------------------

    for module_key, label in NAVIGATION:

        if module_key == current_module:

            # Native Streamlit button.
            # No HTML span is used.
            st.sidebar.button(
                f"●  {label}",
                key=f"active_nav_{module_key}",
                use_container_width=True,
                disabled=True,
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

    st.sidebar.divider()

    st.sidebar.caption(
        "ADMINISTRATION"
    )

    if current_module == "Settings":

        st.sidebar.button(
            "●  Settings",
            key="active_nav_settings",
            use_container_width=True,
            disabled=True,
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
    # Current user
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

    st.sidebar.divider()

    st.sidebar.caption(
        "SIGNED IN"
    )

    st.sidebar.write(
        f"**{full_name}**"
    )

    st.sidebar.caption(
        f"@{username} • {role}"
    )

    # --------------------------------------------------------
    # Sign out
    # --------------------------------------------------------

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        logout_user()

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

    # --------------------------------------------------------
    # Calculate project statistics
    # --------------------------------------------------------

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
    # Module header
    # --------------------------------------------------------

    render_header = getattr(
        branding,
        "render_module_header",
        None,
    )

    if callable(render_header):

        render_header(
            "AEC Workspace",
            (
                "Central workspace for "
                "architecture, engineering "
                "and construction activities."
            ),
        )

    else:

        st.title(
            "AEC Workspace"
        )

        st.caption(
            "Central workspace for architecture, "
            "engineering and construction activities."
        )

    # --------------------------------------------------------
    # KPI ROW
    #
    # Native Streamlit metrics.
    # --------------------------------------------------------

    columns = st.columns(
        5,
        gap="small",
    )

    with columns[0]:

        st.metric(
            "Projects",
            total_projects,
        )

    with columns[1]:

        st.metric(
            "Active",
            active_projects,
        )

    with columns[2]:

        st.metric(
            "Planning",
            planning_projects,
        )

    with columns[3]:

        st.metric(
            "Completed",
            completed_projects,
        )

    with columns[4]:

        st.metric(
            "Total Budget",
            f"${total_budget:,.2f}",
        )

    st.divider()

    # --------------------------------------------------------
    # Workspace overview
    # --------------------------------------------------------

    st.subheader(
        "Creative Studios Workspace"
    )

    st.caption(
        "Manage projects, documents, drawings, "
        "RFIs, tasks, approvals, bills of "
        "quantities and site activities from "
        "one integrated AEC workspace."
    )

    st.write("")

    # --------------------------------------------------------
    # Workspace summary
    # --------------------------------------------------------

    left, right = st.columns(
        2,
        gap="medium",
    )

    with left:

        with st.container(
            border=True,
        ):

            st.subheader(
                "Project Portfolio"
            )

            st.write(
                f"Total projects: **{total_projects}**"
            )

            st.write(
                f"Active projects: **{active_projects}**"
            )

            st.write(
                f"Planning projects: **{planning_projects}**"
            )

    with right:

        with st.container(
            border=True,
        ):

            st.subheader(
                "Project Status"
            )

            st.write(
                f"Completed projects: **{completed_projects}**"
            )

            st.write(
                f"Portfolio budget: **${total_budget:,.2f}**"
            )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:
    """Render a safe module placeholder."""

    render_header = getattr(
        branding,
        "render_module_header",
        None,
    )

    if callable(render_header):

        render_header(
            title,
            description,
        )

    else:

        st.title(title)
        st.caption(description)

    with st.container(
        border=True,
    ):

        st.subheader(
            title
        )

        st.caption(
            description
        )


# ============================================================
# SETTINGS
# ============================================================

def render_settings() -> None:
    """Render application settings."""

    render_header = getattr(
        branding,
        "render_module_header",
        None,
    )

    if callable(render_header):

        render_header(
            "Settings",
            "Creative Studios workspace configuration.",
        )

    else:

        st.title(
            "Settings"
        )

        st.caption(
            "Creative Studios workspace configuration."
        )

    user = get_current_user()

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

    with st.container(
        border=True,
    ):

        st.subheader(
            "Current User"
        )

        st.write(
            f"**Name:** {full_name}"
        )

        st.write(
            f"**Username:** @{username}"
        )

        st.write(
            f"**Role:** {role}"
        )


# ============================================================
# MODULE ROUTER
# ============================================================

def render_active_module(
    module_name: str,
    database: dict[str, Any],
) -> None:
    """Route the active application module."""

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

        boq_module = getattr(
            __import__(
                "modules.boq",
                fromlist=[
                    "render_boq_module"
                ],
            ),
            "render_boq_module",
            None,
        )

        if callable(boq_module):

            boq_module(
                database
            )

        else:

            render_placeholder(
                "Bill of Quantities",
                (
                    "Manage quantities, "
                    "costs and project estimates."
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
                "Manage project team members, "
                "responsibilities and workspace access."
            ),
        )

    elif module_name == "Settings":

        render_settings()

    else:

        st.session_state[
            "active_module"
        ] = DEFAULT_MODULE

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
    # Database
    # --------------------------------------------------------

    try:

        database = get_database()

    except Exception as exc:

        st.error(
            f"Unable to load workspace data: {exc}"
        )

        st.stop()

    # --------------------------------------------------------
    # Authentication
    # --------------------------------------------------------

    if not is_authenticated():

        try:

            render_login(
                database
            )

        except Exception as exc:

            st.error(
                f"Error rendering login: {exc}"
            )

        return

    # --------------------------------------------------------
    # Application
    # --------------------------------------------------------

    try:

        active_module = render_sidebar()

        render_active_module(
            active_module,
            database,
        )

    except Exception as exc:

        st.error(
            f"An error occurred: {exc}"
        )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()