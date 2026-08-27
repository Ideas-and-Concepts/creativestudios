"""
Creative Studios
Architecture • Engineering • Construction

Main Streamlit application entry point.
"""

from __future__ import annotations

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
# BRANDING
# ============================================================

def initialize_branding() -> None:
    """Load the Creative Studios global branding."""

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
# CONSTANTS
# ============================================================

APPLICATION_NAME = "Creative Studios"

APPLICATION_SUBTITLE = (
    "Architecture • Engineering • Construction"
)

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
    """Initialize Streamlit session state."""

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
    """Load the application database."""

    existing = st.session_state.get("database")

    if isinstance(existing, dict):
        return existing

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
    """Render the Creative Studios login page."""

    # --------------------------------------------------------
    # Page spacing
    # --------------------------------------------------------

    st.write("")

    # --------------------------------------------------------
    # Center the entire login area
    # --------------------------------------------------------

    left, center, right = st.columns(
        [1, 2, 1],
        gap="small",
    )

    with center:

        # ----------------------------------------------------
        # Centered logo
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
        # Brand identity
        # ----------------------------------------------------

        st.markdown(
            "<h1 style='"
            "text-align:center;"
            "font-size:28px;"
            "font-weight:800;"
            "margin:8px 0 0 0;"
            "'>"
            "Creative Studios"
            "</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='"
            "text-align:center;"
            "color:#64748B;"
            "font-size:14px;"
            "margin-top:5px;"
            "margin-bottom:24px;"
            "'>"
            "Architecture • Engineering • Construction"
            "</p>",
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

        # ----------------------------------------------------
        # Authentication
        # ----------------------------------------------------

        if submitted:

            username = str(
                username or ""
            ).strip()

            password = str(
                password or ""
            )

            if not username or not password:

                st.error(
                    "Please enter your username and password."
                )

                return

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

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        st.caption(
            "Creative Studios"
        )


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

        try:

            branding.render_logo(
                width=44
            )

        except Exception:

            if LOGO_PATH.exists():

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
    """Render application navigation."""

    user = auth.get_current_user()

    if not isinstance(
        user,
        dict,
    ):
        user = {}

    render_sidebar_branding()

    st.sidebar.caption(
        "MODULE NAVIGATION"
    )

    current_module = st.session_state.get(
        "active_module",
        "Overview",
    )

    valid_modules = {
        key
        for key, _ in NAVIGATION
    }

    valid_modules.add(
        "Settings"
    )

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

            # Native Streamlit element.
            # No HTML span/div is used.
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
    # User information
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

        try:
            auth.logout_user()
        except Exception:
            pass

        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["active_module"] = "Overview"
        st.session_state["database"] = None

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
    """Render the Creative Studios overview."""

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
    # Header
    # --------------------------------------------------------

    branding.render_module_header(
        "AEC Workspace",
        (
            "Central workspace for "
            "architecture, engineering "
            "and construction activities."
        ),
    )

    # --------------------------------------------------------
    # KPI row
    #
    # Native st.metric() replaces HTML KPI cards.
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
    #
    # Native Streamlit elements replace cs-card HTML.
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
    # Quick workspace summary
    # --------------------------------------------------------

    summary_left, summary_right = st.columns(
        2,
        gap="medium",
    )

    with summary_left:

        with st.container(
            border=True,
        ):

            st.write(
                "**Project Portfolio**"
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

    with summary_right:

        with st.container(
            border=True,
        ):

            st.write(
                "**Project Status**"
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
    """Render a module placeholder."""

    branding.render_module_header(
        title,
        description,
    )

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

    branding.render_module_header(
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
    """Route the active module."""

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
                f"Error rendering login: {exc}"
            )

        return

    # --------------------------------------------------------
    # Authenticated application
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
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()