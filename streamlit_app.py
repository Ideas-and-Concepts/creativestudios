"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.

Responsibilities
----------------
- Application startup
- Database initialization
- Authentication
- Session state
- Sidebar navigation
- Module routing
- Overview dashboard
- Settings
- Placeholder modules

Branding
--------
All branding CSS, logo rendering, and module-header styling
are provided centrally by modules.branding.

The application intentionally contains no duplicate branding
CSS so that modules.branding remains the single source of truth.
"""

from __future__ import annotations

import html
import importlib
import math
from pathlib import Path
from typing import Any

import streamlit as st

from modules.branding import (
    inject_branding_css,
    render_logo,
    render_module_header,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

CREATIVE_STUDIOS_LOGO = (
    ASSETS_DIR / "creative_studios.png"
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon=(
        str(CREATIVE_STUDIOS_LOGO)
        if CREATIVE_STUDIOS_LOGO.exists()
        else None
    ),
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE
# ============================================================

from modules.database import (
    initialize_database,
    load_memory,
)


# ============================================================
# OPTIONAL MODULE IMPORTS
# ============================================================

def _load_renderer(
    module_name: str,
    function_name: str,
):
    """
    Safely load a module renderer.

    A missing or unfinished module must not prevent
    the rest of Creative Studios from starting.
    """

    try:

        module = importlib.import_module(
            module_name
        )

        renderer = getattr(
            module,
            function_name,
            None,
        )

        if callable(renderer):
            return renderer

        return None

    except Exception:
        return None


render_projects_module = _load_renderer(
    "modules.projects",
    "render_projects_module",
)

render_documents_module = _load_renderer(
    "modules.documents",
    "render_documents_module",
)

render_drawings_module = _load_renderer(
    "modules.drawings",
    "render_drawings_module",
)

render_rfis_module = _load_renderer(
    "modules.rfis",
    "render_rfis_module",
)

render_tasks_module = _load_renderer(
    "modules.tasks",
    "render_tasks_module",
)

render_approvals_module = _load_renderer(
    "modules.approvals",
    "render_approvals_module",
)


# ============================================================
# BRANDING
# ============================================================

def initialize_branding() -> None:
    """
    Inject all Creative Studios branding.

    Branding CSS is intentionally maintained only in
    modules.branding.
    """

    inject_branding_css()


# ============================================================
# DATABASE HELPER
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Load or initialize the application database.
    """

    if "database" not in st.session_state:

        st.session_state.database = (
            initialize_database()
        )

    else:

        st.session_state.database = (
            load_memory()
        )

    return st.session_state.database


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user against the JSON database.
    """

    username = (
        username or ""
    ).strip()

    password = (
        password or ""
    ).strip()

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

        stored_password = str(
            user.get(
                "password",
                user.get(
                    "password_hash",
                    "",
                ),
            )
        )

        if (
            stored_username == username
            and stored_password == password
        ):

            if user.get(
                "active",
                True,
            ) is False:

                return None

            return user

    return None


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize required Streamlit session-state values.
    """

    defaults = {
        "authenticated": False,
        "user": None,
        "active_module": "Overview",
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


# ============================================================
# LOGIN BRANDING
# ============================================================

def render_login_branding() -> None:
    """
    Render logo-only login branding.

    The visual styling is owned by modules.branding.
    """

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-logo">',
        unsafe_allow_html=True,
    )

    if CREATIVE_STUDIOS_LOGO.exists():

        st.image(
            str(CREATIVE_STUDIOS_LOGO),
            width=110,
        )

    else:

        render_logo(
            width=110,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    render_login_branding()

    st.write("")

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

            if user is not None:

                st.session_state.authenticated = True

                st.session_state.user = user

                st.session_state.active_module = (
                    "Overview"
                )

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
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """
    Render Creative Studios sidebar branding.

    CSS remains centralized in modules.branding.
    """

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand">',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="cs-sidebar-brand-row">',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<div class="cs-sidebar-logo-wrap">',
        unsafe_allow_html=True,
    )

    if CREATIVE_STUDIOS_LOGO.exists():

        st.sidebar.image(
            str(CREATIVE_STUDIOS_LOGO),
            width=46,
        )

    else:

        render_logo(
            width=46,
        )

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand-text">

            <div class="cs-sidebar-name">
                Creative Studios
            </div>

            <div class="cs-sidebar-subtitle">
                AEC Workspace
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """
    Render module navigation.

    Existing session-state navigation behavior is preserved.
    """

    user = (
        st.session_state.get("user")
        or {}
    )

    render_sidebar_branding()

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Module Navigation"
        "</div>",
        unsafe_allow_html=True,
    )

    modules = [
        (
            "Overview",
            "Overview",
        ),
        (
            "Projects",
            "Project Directory",
        ),
        (
            "Documents",
            "Documents",
        ),
        (
            "Drawings",
            "Drawings",
        ),
        (
            "RFIs",
            "RFIs",
        ),
        (
            "Tasks",
            "Tasks",
        ),
        (
            "Approvals",
            "Approvals",
        ),
        (
            "BOQ",
            "Bill of Quantities",
        ),
        (
            "Site Logs",
            "Site Logs",
        ),
        (
            "Team",
            "Team",
        ),
    ]

    current = st.session_state.get(
        "active_module",
        "Overview",
    )

    selected = current

    for module_key, label in modules:

        is_active = (
            module_key == current
        )

        button_label = (
            f"●  {label}"
            if is_active
            else f"   {label}"
        )

        if st.sidebar.button(
            button_label,
            key=f"nav_{module_key}",
            use_container_width=True,
        ):

            selected = module_key

            st.session_state.active_module = (
                module_key
            )

            st.rerun()

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Administration"
        "</div>",
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "   Settings",
        key="nav_settings",
        use_container_width=True,
    ):

        st.session_state.active_module = (
            "Settings"
        )

        st.rerun()

    # --------------------------------------------------------
    # SAFE USER VALUES
    # --------------------------------------------------------

    full_name = str(
        user.get(
            "full_name",
            "",
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

    safe_full_name = html.escape(
        full_name
    )

    safe_username = html.escape(
        username
    )

    safe_role = html.escape(
        role
    )

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

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

        st.session_state.active_module = (
            "Overview"
        )

        st.rerun()

    return selected


# ============================================================
# SAFE BUDGET FORMATTER
# ============================================================

def format_budget(
    value: Any,
) -> str:
    """
    Safely format a budget value as Uganda Shillings.

    Invalid values, None, NaN and infinity are treated
    as zero rather than crashing the dashboard.
    """

    try:

        numeric_value = float(
            value or 0
        )

        if not math.isfinite(
            numeric_value
        ):
            numeric_value = 0.0

    except (
        TypeError,
        ValueError,
    ):

        numeric_value = 0.0

    return (
        f"UGX {numeric_value:,.2f}"
    )


# ============================================================
# OVERVIEW
# ============================================================

def render_overview(
    database: dict[str, Any],
) -> None:

    projects = database.get(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):
        projects = []

    # --------------------------------------------------------
    # PROJECT COUNTS
    # --------------------------------------------------------

    total = len(projects)

    active = sum(
        1
        for project in projects
        if isinstance(
            project,
            dict,
        )
        and str(
            project.get(
                "status",
                "",
            )
        ).strip().lower()
        == "active"
    )

    planning = sum(
        1
        for project in projects
        if isinstance(
            project,
            dict,
        )
        and str(
            project.get(
                "status",
                "",
            )
        ).strip().lower()
        == "planning"
    )

    completed = sum(
        1
        for project in projects
        if isinstance(
            project,
            dict,
        )
        and str(
            project.get(
                "status",
                "",
            )
        ).strip().lower()
        == "completed"
    )

    # --------------------------------------------------------
    # TOTAL PROJECT BUDGET
    # --------------------------------------------------------

    total_budget = 0.0

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        raw_budget = project.get(
            "estimated_budget",
            project.get(
                "budget",
                0,
            ),
        )

        try:

            budget_value = float(
                raw_budget or 0
            )

            if not math.isfinite(
                budget_value
            ):
                budget_value = 0.0

            total_budget += budget_value

        except (
            TypeError,
            ValueError,
        ):

            continue

    formatted_budget = format_budget(
        total_budget
    )

    # --------------------------------------------------------
    # SHARED MODULE HEADER
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
        (
            "Projects",
            str(total),
        ),
        (
            "Active",
            str(active),
        ),
        (
            "Planning",
            str(planning),
        ),
        (
            "Completed",
            str(completed),
        ),
        (
            "Total Budget",
            formatted_budget,
        ),
    ]

    columns = st.columns(
        len(metrics),
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
# MODULE ERROR HANDLER
# ============================================================

def run_module(
    renderer,
    database: dict[str, Any],
    module_name: str,
) -> None:

    if renderer is None:

        render_module_header(
            module_name,
            f"{module_name} module.",
        )

        st.warning(
            f"{module_name} module is not currently "
            "available."
        )

        return

    try:

        renderer(
            database
        )

    except Exception as exc:

        st.error(
            f"{module_name} encountered an error."
        )

        st.exception(
            exc
        )


# ============================================================
# PLACEHOLDER MODULE
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    safe_title = html.escape(
        title
    )

    safe_description = html.escape(
        description
    )

    render_module_header(
        title,
        description,
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                {safe_title}
            </div>

            <div class="cs-card-subtitle">
                {safe_description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SETTINGS
# ============================================================

def render_settings() -> None:

    render_module_header(
        "Settings",
        "Creative Studios workspace configuration.",
    )

    user = (
        st.session_state.get("user")
        or {}
    )

    name = str(
        user.get(
            "full_name",
            "",
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

    safe_name = html.escape(
        name
    )

    safe_username = html.escape(
        username
    )

    safe_role = html.escape(
        role
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                Current User
            </div>

            <div class="cs-card-subtitle">

                <div style="margin-top:12px;">
                    Name:
                    <strong>{safe_name}</strong>
                </div>

                <div style="margin-top:7px;">
                    Username:
                    <strong>@{safe_username}</strong>
                </div>

                <div style="margin-top:7px;">
                    Role:
                    <strong>{safe_role}</strong>
                </div>

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

    if module_name == "Overview":

        render_overview(
            database
        )

    elif module_name == "Projects":

        run_module(
            render_projects_module,
            database,
            "Project Directory",
        )

    elif module_name == "Documents":

        run_module(
            render_documents_module,
            database,
            "Documents",
        )

    elif module_name == "Drawings":

        run_module(
            render_drawings_module,
            database,
            "Drawings",
        )

    elif module_name == "RFIs":

        run_module(
            render_rfis_module,
            database,
            "RFIs",
        )

    elif module_name == "Tasks":

        run_module(
            render_tasks_module,
            database,
            "Tasks",
        )

    elif module_name == "Approvals":

        run_module(
            render_approvals_module,
            database,
            "Approvals",
        )

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

        st.session_state.active_module = (
            "Overview"
        )

        render_overview(
            database
        )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    initialize_session_state()

    # --------------------------------------------------------
    # SINGLE BRANDING SOURCE
    # --------------------------------------------------------

    initialize_branding()

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    database = get_database()

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not st.session_state.authenticated:

        render_login(
            database
        )

        return

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    active_module = render_sidebar()

    # --------------------------------------------------------
    # MODULE ROUTER
    # --------------------------------------------------------

    render_active_module(
        active_module,
        database,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()