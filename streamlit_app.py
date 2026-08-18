"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.

Features
--------
- JSON database persistence
- Authentication
- Project Directory
- Documents
- Drawings
- RFIs
- Tasks
- Approvals
- Settings
- Native Streamlit branding
- Shared branding CSS
- Session-state navigation
"""

from __future__ import annotations

import html
import importlib
from typing import Any

import streamlit as st

from modules import branding

from modules.database import (
    initialize_database,
    load_memory,
)


# ============================================================
# PAGE CONFIG
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
# SHARED BRANDING
# ============================================================

branding.inject_branding_css()


# ============================================================
# BRANDING HELPERS
# ============================================================

render_logo = branding.render_logo

render_module_header = (
    branding.render_module_header
)


# ============================================================
# MODULE LOADER
# ============================================================

def _load_renderer(
    module_name: str,
    function_name: str,
):
    """
    Safely load a module renderer.

    Unlike the previous implementation, import errors are
    displayed so a broken module cannot silently disappear.
    """

    try:

        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        st.error(
            f"Failed to import {module_name}"
        )

        st.exception(
            exc
        )

        return None

    renderer = getattr(
        module,
        function_name,
        None,
    )

    if not callable(renderer):

        st.error(
            f"{module_name} does not define "
            f"callable {function_name}()."
        )

        return None

    return renderer


# ============================================================
# MODULE RENDERERS
# ============================================================

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
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:

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

    if st.session_state.database is None:

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

    username = str(
        username or ""
    ).strip()

    password = str(
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
# LOGIN
# ============================================================

def render_login(
    database: dict[str, Any],
) -> None:

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Logo only
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-login-logo">',
        unsafe_allow_html=True,
    )

    render_logo(
        width=100,
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Login form
    # --------------------------------------------------------

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
        '</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:
    """
    Render sidebar branding using native Streamlit image
    rendering rather than HTML image wrappers.
    """

    logo_col, text_col = st.sidebar.columns(
        [1, 3],
        vertical_alignment="center",
    )

    with logo_col:

        render_logo(
            width=44,
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
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    user = (
        st.session_state.get(
            "user"
        )
        or {}
    )

    render_sidebar_branding()

    st.sidebar.markdown(
        """
        <div class="cs-section-label">
            Module Navigation
        </div>
        """,
        unsafe_allow_html=True,
    )

    modules = [
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

    current = st.session_state.get(
        "active_module",
        "Overview",
    )

    selected = current

    for module_key, label in modules:

        is_active = (
            module_key == current
        )

        if is_active:

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

                selected = module_key

                st.session_state.active_module = (
                    module_key
                )

                st.rerun()

    # --------------------------------------------------------
    # Administration
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-section-label">
            Administration
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Settings",
        key="nav_settings",
        use_container_width=True,
    ):

        st.session_state.active_module = (
            "Settings"
        )

        st.rerun()

    # --------------------------------------------------------
    # User
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

    safe_full_name = html.escape(
        full_name
    )

    safe_username = html.escape(
        username
    )

    safe_role = html.escape(
        role
    )

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
# SAFE NUMBER
# ============================================================

def _safe_float(
    value: Any,
) -> float:

    try:

        return float(
            value or 0
        )

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

    projects = database.get(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):

        projects = []

    total = len(
        projects
    )

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

    total_budget = 0.0

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):

            continue

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
        "Central workspace for architectural, "
        "engineering and construction activities.",
    )

    # --------------------------------------------------------
    # KPI cards
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
    # Workspace overview
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
# MODULE EXECUTOR
# ============================================================

def run_module(
    renderer,
    database: dict[str, Any],
    module_name: str,
) -> None:

    if renderer is None:

        st.error(
            f"{module_name} could not be loaded."
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
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

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

    render_module_header(
        "Settings",
        "Creative Studios workspace configuration.",
    )

    user = (
        st.session_state.get(
            "user"
        )
        or {}
    )

    name = str(
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

            <div class="cs-setting-row">
                Name:
                <strong>
                    {safe_name}
                </strong>
            </div>

            <div class="cs-setting-row">
                Username:
                <strong>
                    @{safe_username}
                </strong>
            </div>

            <div class="cs-setting-row">
                Role:
                <strong>
                    {safe_role}
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

    database = get_database()

    if not st.session_state.authenticated:

        render_login(
            database
        )

        return

    active_module = render_sidebar()

    render_active_module(
        active_module,
        database,
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()