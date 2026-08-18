"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.

Architecture
------------
- Streamlit UI
- JSON database through modules.database
- Shared branding/icons through modules.ui
- Workspace modules under modules/
- No pages/ directory required
"""

from __future__ import annotations

from typing import Any

import streamlit as st


# ============================================================
# DATABASE IMPORTS
# ============================================================

from modules.database import (
    load_memory,
    initialize_database,
)


# ============================================================
# SHARED UI IMPORTS
# ============================================================

from modules.ui import (
    MODULE_EMOJIS,
    MODULE_ICONS,
    render_login_brand,
    render_sidebar_brand,
    render_module_header,
    svg_icon,
)


# ============================================================
# OPTIONAL MODULE IMPORTS
# ============================================================

try:
    from modules.projects import (
        render_projects_module,
    )
except ImportError:
    render_projects_module = None


try:
    from modules.documents import (
        render_documents_module,
    )
except ImportError:
    render_documents_module = None


try:
    from modules.drawings import (
        render_drawings_module,
    )
except ImportError:
    render_drawings_module = None


try:
    from modules.rfis import (
        render_rfis_module,
    )
except ImportError:
    render_rfis_module = None


try:
    from modules.tasks import (
        render_tasks_module,
    )
except ImportError:
    render_tasks_module = None


# ============================================================
# PAGE CONFIG
# ============================================================

def configure_page() -> None:
    """
    Configure Streamlit page metadata.

    Called only from main().
    """

    st.set_page_config(
        page_title="Creative Studios",
        page_icon="CS",
        layout="wide",
        initial_sidebar_state="expanded",
    )


# ============================================================
# GLOBAL CSS
# ============================================================

def inject_global_css() -> None:
    """
    Inject the complete Creative Studios visual system.
    """

    st.markdown(
        """
        <style>

        /* ==================================================
           GLOBAL
           ================================================== */

        html,
        body,
        [data-testid="stAppViewContainer"] {

            background:#05070B !important;
            color:#F8FAFC !important;
        }


        [data-testid="stAppViewContainer"] {

            background:
                radial-gradient(
                    circle at top right,
                    rgba(37,99,235,0.10),
                    transparent 35%
                ),
                #05070B !important;
        }


        [data-testid="stHeader"] {

            background:transparent !important;
        }


        [data-testid="stToolbar"] {

            background:transparent !important;
        }


        .block-container {

            padding-top:2rem !important;
            padding-bottom:3rem !important;
        }

# ============================================================
# CREATIVE STUDIOS SVG BRANDING
# ============================================================

def render_cs_logo(
    size: int = 74,
    sidebar: bool = False,
) -> None:
    """
    Render the Creative Studios logo using inline SVG.

    Inline SVG is used so the logo does not depend on:
    - emoji fonts
    - local image files
    - relative asset paths
    - Streamlit Cloud static-file paths
    """

    if sidebar:
        logo_size = 46
        radius = 13
        font_size = 17
        wrapper_class = "cs-sidebar-logo"
        text_class = "cs-sidebar-logo-text"

    else:
        logo_size = size
        radius = 18
        font_size = 27
        wrapper_class = "cs-logo"
        text_class = "cs-logo-text"

    st.markdown(
        f"""
        <div class="{wrapper_class}"
             style="
                width:{logo_size}px;
                height:{logo_size}px;
                min-width:{logo_size}px;
                border-radius:{radius}px;
                background:#2563EB;
                display:flex;
                align-items:center;
                justify-content:center;
                overflow:hidden;
             ">

            <svg
                width="{logo_size}"
                height="{logo_size}"
                viewBox="0 0 100 100"
                xmlns="http://www.w3.org/2000/svg"
                role="img"
                aria-label="Creative Studios"
            >

                <rect
                    x="0"
                    y="0"
                    width="100"
                    height="100"
                    rx="18"
                    fill="#2563EB"
                />

                <!-- C -->
                <path
                    d="
                        M67 28
                        C61 22 53 19 45 19
                        C28 19 16 32 16 50
                        C16 68 28 81 45 81
                        C53 81 61 78 67 72
                    "
                    fill="none"
                    stroke="#FFFFFF"
                    stroke-width="9"
                    stroke-linecap="round"
                />

                <!-- S -->
                <path
                    d="
                        M75 31
                        C71 26 66 24 60 24
                        C53 24 48 28 48 34
                        C48 41 54 44 62 47
                        C70 50 76 54 76 62
                        C76 70 70 76 61 76
                        C54 76 48 73 44 68
                    "
                    fill="none"
                    stroke="#FFFFFF"
                    stroke-width="8"
                    stroke-linecap="round"
                />

            </svg>

        </div>
        """,
        unsafe_allow_html=True,
    )


        /* ==================================================
           TEXT
           ================================================== */

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {

            color:#F8FAFC !important;
        }


        p,
        label,
        span {

            color:#CBD5E1;
        }


        /* ==================================================
           SIDEBAR
           ================================================== */

        [data-testid="stSidebar"] {

            background:#080B12 !important;
            border-right:1px solid #172033 !important;
        }


        [data-testid="stSidebar"] > div:first-child {

            background:#080B12 !important;
        }


        /* ==================================================
           LOGIN
           ================================================== */

        .cs-login-wrapper {

            width:100%;
            max-width:430px;
            margin:8vh auto 0 auto;
        }


        .cs-login-card {

            background:#0B0F17;
            border:1px solid #1E293B;
            border-radius:20px;
            padding:36px;

            box-shadow:
                0 20px 70px rgba(0,0,0,0.55),
                0 0 40px rgba(37,99,235,0.06);
        }


        .cs-login-brand {

            text-align:center;
        }


        .cs-logo {

            width:74px;
            height:74px;
            margin:0 auto 18px auto;

            display:flex;
            align-items:center;
            justify-content:center;

            border-radius:19px;

            overflow:hidden;

            box-shadow:
                0 10px 35px rgba(37,99,235,0.35);
        }


        .cs-logo svg {

            display:block;
        }


        .cs-brand-name {

            color:#FFFFFF !important;

            font-family:
                Arial,
                Helvetica,
                sans-serif !important;

            font-size:27px !important;
            font-weight:900 !important;

            line-height:1.2 !important;

            text-align:center !important;
        }


        .cs-brand-subtitle {

            color:#64748B !important;

            font-family:
                Arial,
                Helvetica,
                sans-serif !important;

            font-size:12px !important;
            font-weight:600 !important;

            line-height:1.4 !important;

            text-align:center !important;

            margin-top:6px !important;

            letter-spacing:1px !important;

            text-transform:uppercase !important;
        }


        /* ==================================================
           SIDEBAR BRAND
           ================================================== */

        .cs-sidebar-brand {

            padding:8px 4px 20px 4px;

            margin-bottom:15px;

            border-bottom:1px solid #172033;
        }


        .cs-sidebar-brand-row {

            display:flex;

            align-items:center;

            gap:12px;
        }


        .cs-sidebar-logo {

            width:46px;
            height:46px;

            min-width:46px;

            display:flex;

            align-items:center;
            justify-content:center;

            border-radius:13px;

            overflow:hidden;

            box-shadow:
                0 8px 25px rgba(37,99,235,0.30);
        }


        .cs-sidebar-logo svg {

            display:block;
        }


        .cs-sidebar-name {

            color:#FFFFFF !important;

            font-family:
                Arial,
                Helvetica,
                sans-serif !important;

            font-size:16px !important;
            font-weight:850 !important;

            line-height:1.2 !important;
        }


        .cs-sidebar-subtitle {

            color:#64748B !important;

            font-family:
                Arial,
                Helvetica,
                sans-serif !important;

            font-size:10px !important;

            line-height:1.3 !important;

            margin-top:4px !important;

            text-transform:uppercase !important;

            letter-spacing:0.8px !important;
        }


        /* ==================================================
           SECTION LABEL
           ================================================== */

        .cs-section-label {

            color:#475569;

            font-size:10px;

            font-weight:850;

            letter-spacing:1.3px;

            text-transform:uppercase;

            margin-top:17px;

            margin-bottom:7px;
        }


        /* ==================================================
           SIDEBAR BUTTONS
           ================================================== */

        [data-testid="stSidebar"]
        div[data-testid="stButton"] > button {

            min-height:40px !important;

            background:#0B0F17 !important;

            color:#CBD5E1 !important;

            border:1px solid #172033 !important;

            border-radius:10px !important;

            font-size:13px !important;

            font-weight:700 !important;

            text-align:left !important;

            transition:
                background 0.15s ease,
                border-color 0.15s ease;
        }


        [data-testid="stSidebar"]
        div[data-testid="stButton"] > button:hover {

            background:#172554 !important;

            border-color:#2563EB !important;

            color:#FFFFFF !important;
        }


        /* ==================================================
           EMOJI
           ================================================== */

        .cs-emoji {

            font-family:
                "Noto Color Emoji",
                "Apple Color Emoji",
                "Segoe UI Emoji",
                "Segoe UI Symbol",
                sans-serif !important;

            font-size:15px !important;

            line-height:1 !important;

            display:inline-block;

            vertical-align:middle;
        }


        /* ==================================================
           MODULE HEADER
           ================================================== */

        .cs-module-header {

            display:flex;

            align-items:center;

            gap:14px;

            margin-bottom:25px;
        }


        .cs-module-header-icon {

            width:50px;
            height:50px;

            min-width:50px;

            display:flex;

            align-items:center;
            justify-content:center;

            border-radius:14px;

            background:#0B0F17;

            border:1px solid #1E293B;

            box-shadow:
                0 8px 25px rgba(0,0,0,0.25);
        }


        .cs-module-header-icon svg {

            display:block;
        }


        .cs-module-header-title {

            color:#FFFFFF;

            font-size:30px;

            font-weight:900;

            letter-spacing:-0.7px;

            line-height:1.2;
        }


        .cs-module-header-subtitle {

            color:#64748B;

            font-size:13px;

            margin-top:5px;
        }


        /* ==================================================
           PAGE TITLES
           ================================================== */

        .cs-page-title {

            color:#FFFFFF;

            font-size:30px;

            font-weight:900;

            letter-spacing:-0.7px;
        }


        .cs-page-subtitle {

            color:#64748B;

            font-size:13px;

            margin-top:4px;

            margin-bottom:25px;
        }


        /* ==================================================
           CARDS
           ================================================== */

        .cs-card {

            background:#0B0F17;

            border:1px solid #172033;

            border-radius:15px;

            padding:20px;
        }


        .cs-kpi {

            background:#0B0F17;

            border:1px solid #172033;

            border-radius:15px;

            padding:18px;

            min-height:110px;
        }


        .cs-kpi-label {

            color:#64748B;

            font-size:11px;

            text-transform:uppercase;

            letter-spacing:0.8px;
        }


        .cs-kpi-value {

            color:#FFFFFF;

            font-size:26px;

            font-weight:900;

            margin-top:7px;
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        div[data-testid="stButton"] > button {

            background:#111827 !important;

            color:#E2E8F0 !important;

            border:1px solid #1E293B !important;

            border-radius:9px !important;
        }


        div[data-testid="stButton"] > button:hover {

            background:#172554 !important;

            border-color:#2563EB !important;

            color:#FFFFFF !important;
        }


        div[data-testid="stFormSubmitButton"] > button {

            background:#2563EB !important;

            color:#FFFFFF !important;

            border:0 !important;

            border-radius:10px !important;

            font-weight:800 !important;
        }


        div[data-testid="stFormSubmitButton"] > button:hover {

            background:#1D4ED8 !important;
        }


        /* ==================================================
           INPUTS
           ================================================== */

        input,
        textarea,
        [data-baseweb="select"] > div {

            background:#0B0F17 !important;

            color:#FFFFFF !important;

            border-color:#1E293B !important;
        }


        /* ==================================================
           USER CARD
           ================================================== */

        .cs-user-card {

            background:#0B0F17;

            border:1px solid #172033;

            border-radius:13px;

            padding:13px;

            margin-top:15px;
        }


        .user-label {

            color:#60A5FA;

            font-size:9px;

            font-weight:850;

            letter-spacing:1px;

            text-transform:uppercase;
        }


        .user-name {

            color:#FFFFFF;

            font-size:14px;

            font-weight:800;

            margin-top:5px;
        }


        .user-login {

            color:#64748B;

            font-size:10px;

            margin-top:3px;
        }


        .user-role {

            display:inline-block;

            margin-top:8px;

            padding:4px 9px;

            background:#2563EB;

            color:#FFFFFF;

            border-radius:999px;

            font-size:9px;

            font-weight:850;
        }


        /* ==================================================
           ERROR
           ================================================== */

        .cs-login-error {

            margin-top:12px;

            padding:10px 12px;

            background:rgba(220,38,38,0.10);

            border:1px solid rgba(239,68,68,0.25);

            border-radius:9px;

            color:#FCA5A5 !important;

            font-size:12px;

            text-align:center;
        }


        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATABASE
# ============================================================

def get_app_database() -> dict[str, Any]:
    """
    Get the application database.

    Session state owns the current reference.
    modules.database owns persistence.
    """

    if "database" not in st.session_state:

        st.session_state.database = (
            initialize_database()
        )

    return st.session_state.database


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize application session variables.
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
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user against the JSON users collection.

    Supports the existing simple JSON user contract.

    Password handling:
    - password
    - password_hash
    """

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )

    if not username or not password:
        return None

    users = db.get(
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

        if str(
            user.get(
                "username",
                "",
            )
        ).strip().lower() != username.lower():

            continue

        if user.get(
            "active",
            True,
        ) is False:

            return None

        stored_password = user.get(
            "password",
            None,
        )

        stored_password_hash = user.get(
            "password_hash",
            None,
        )

        if stored_password is not None:

            if str(
                stored_password
            ) == password:

                return user

        if stored_password_hash is not None:

            if str(
                stored_password_hash
            ) == password:

                return user

    return None


# ============================================================
# LOGIN
# ============================================================

def render_login(
    db: dict[str, Any],
) -> None:
    """
    Render the unauthenticated login screen.
    """

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # Branding MUST be rendered inside the card,
    # before the login form.
    render_login_brand(st)

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.write("")

    with st.form(
        "creative_studios_login",
        clear_on_submit=False,
    ):

        username = st.text_input(
            "Username",
            placeholder="Enter username",
            key="login_username",
        )

        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter password",
            key="login_password",
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True,
        )

        if submitted:

            user = authenticate_user(
                username,
                password,
                db,
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
        <div style="
            text-align:center;
            margin-top:18px;
            color:#475569;
            font-size:11px;
        ">
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
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """
    Render sidebar navigation.

    Existing widget type remains st.sidebar.button.
    """

    user = st.session_state.get(
        "user"
    ) or {}

    # Branding first.
    render_sidebar_brand(st)

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
            "home",
            "🏠",
        ),
        (
            "Projects",
            "Project Directory",
            "projects",
            "🏗️",
        ),
        (
            "Documents",
            "Documents",
            "documents",
            "📄",
        ),
        (
            "Drawings",
            "Drawings",
            "drawings",
            "📐",
        ),
        (
            "Approvals",
            "Approvals",
            "approvals",
            "✅",
        ),
        (
            "BOQ",
            "Bill of Quantities",
            "boq",
            "📋",
        ),
        (
            "RFIs",
            "RFIs",
            "rfi",
            "❓",
        ),
        (
            "Site Logs",
            "Site Logs",
            "site",
            "🏢",
        ),
        (
            "Tasks",
            "Tasks",
            "tasks",
            "☑️",
        ),
        (
            "Team",
            "Team",
            "team",
            "👥",
        ),
    ]

    current = st.session_state.get(
        "active_module",
        "Overview",
    )

    selected = current

    for module_key, label, icon_name, emoji in modules:

        icon = svg_icon(
            icon_name,
            size=17,
            stroke="#60A5FA",
        )

        # SVG is displayed beside the actual Streamlit button.
        st.sidebar.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:7px;
                margin-bottom:-42px;
                position:relative;
                z-index:2;
                pointer-events:none;
                padding-left:10px;
            ">

                {icon}

                <span class="cs-emoji">
                    {emoji}
                </span>

            </div>
            """,
            unsafe_allow_html=True,
        )

        clicked = st.sidebar.button(
            label,
            key=f"nav_{module_key}",
            use_container_width=True,
        )

        if clicked:

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

    settings_icon = svg_icon(
        "settings",
        size=17,
        stroke="#60A5FA",
    )

    st.sidebar.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:7px;
            margin-bottom:-42px;
            position:relative;
            z-index:2;
            pointer-events:none;
            padding-left:10px;
        ">

            {settings_icon}

            <span class="cs-emoji">
                ⚙️
            </span>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.sidebar.button(
        "Settings",
        key="nav_settings",
        use_container_width=True,
    ):

        selected = "Settings"

        st.session_state.active_module = (
            "Settings"
        )

        st.rerun()

    # User card.
    full_name = str(
        user.get(
            "full_name",
            user.get(
                "name",
                "System Administrator",
            ),
        )
    )

    username = str(
        user.get(
            "username",
            "admin",
        )
    )

    role = str(
        user.get(
            "role",
            "Admin",
        )
    )

    st.sidebar.markdown(
        f"""
        <div class="cs-user-card">

            <div class="user-label">
                Signed In
            </div>

            <div class="user-name">
                {full_name}
            </div>

            <div class="user-login">
                @{username}
            </div>

            <div class="user-role">
                {role}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.write("")

    logout_icon = svg_icon(
        "logout",
        size=17,
        stroke="#F87171",
    )

    st.sidebar.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:7px;
            margin-bottom:-42px;
            position:relative;
            z-index:2;
            pointer-events:none;
            padding-left:10px;
        ">

            {logout_icon}

            <span class="cs-emoji">
                🚪
            </span>

        </div>
        """,
        unsafe_allow_html=True,
    )

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
# OVERVIEW
# ============================================================

def render_overview(
    db: dict[str, Any],
) -> None:

    projects = db.get(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):
        projects = []

    total = len(projects)

    active = sum(
        1
        for project in projects
        if isinstance(project, dict)
        and str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "active"
    )

    planning = sum(
        1
        for project in projects
        if isinstance(project, dict)
        and str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "planning"
    )

    completed = sum(
        1
        for project in projects
        if isinstance(project, dict)
        and str(
            project.get(
                "status",
                "",
            )
        ).lower()
        == "completed"
    )

    budget = 0.0

    for project in projects:

        if not isinstance(
            project,
            dict,
        ):
            continue

        try:

            budget += float(
                project.get(
                    "estimated_budget",
                    project.get(
                        "budget",
                        0,
                    ),
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            pass

    render_module_header(
        st,
        "AEC Workspace",
        (
            "Central workspace for architectural, "
            "engineering and construction activities."
        ),
        "home",
        "🏠",
    )

    cols = st.columns(4)

    metrics = [
        ("Projects", total),
        ("Active", active),
        ("Planning", planning),
        ("Portfolio Budget", f"${budget:,.2f}"),
    ]

    for col, (label, value) in zip(
        cols,
        metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {label}
                    </div>

                    <div class="cs-kpi-value">
                        {value}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    st.markdown(
        """
        <div class="cs-card">

            <div style="
                color:#FFFFFF;
                font-size:18px;
                font-weight:850;
            ">
                Workspace Overview
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:7px;
            ">
                Use Module Navigation in the sidebar to access
                projects, documents, drawings, approvals,
                RFIs, BOQ and construction operations.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAFE MODULE CALLER
# ============================================================

def _run_module(
    module_name: str,
    renderer: Any,
    db: dict[str, Any],
) -> None:
    """
    Execute an optional workspace module safely.
    """

    if renderer is None:

        st.error(
            f"{module_name} module is not available."
        )

        st.info(
            f"Expected renderer for {module_name} "
            "could not be imported."
        )

        return

    try:

        renderer(db)

    except Exception as exc:

        st.error(
            f"{module_name} encountered an error."
        )

        st.exception(exc)


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
    icon_name: str = "home",
    emoji: str = "",
) -> None:

    render_module_header(
        st,
        title,
        description,
        icon_name,
        emoji,
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div style="
                color:#60A5FA;
                font-size:12px;
                font-weight:800;
                text-transform:uppercase;
                letter-spacing:1px;
            ">
                Module
            </div>

            <div style="
                color:#FFFFFF;
                font-size:20px;
                font-weight:850;
                margin-top:8px;
            ">
                {title}
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:8px;
            ">
                {description}
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
        st,
        "Settings",
        "Creative Studios workspace configuration.",
        "settings",
        "⚙️",
    )

    user = st.session_state.get(
        "user"
    ) or {}

    full_name = user.get(
        "full_name",
        user.get(
            "name",
            "System Administrator",
        ),
    )

    username = user.get(
        "username",
        "admin",
    )

    role = user.get(
        "role",
        "Admin",
    )

    st.markdown(
        f"""
        <div class="cs-card">

            <div style="
                color:#FFFFFF;
                font-size:18px;
                font-weight:850;
            ">
                Current User
            </div>

            <div style="
                color:#94A3B8;
                margin-top:12px;
                font-size:13px;
            ">
                Name:
                <strong>{full_name}</strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Username:
                <strong>@{username}</strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Role:
                <strong>{role}</strong>
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
    db: dict[str, Any],
) -> None:

    if module_name == "Overview":

        render_overview(db)

    elif module_name == "Projects":

        _run_module(
            "Project Directory",
            render_projects_module,
            db,
        )

    elif module_name == "Documents":

        _run_module(
            "Documents",
            render_documents_module,
            db,
        )

    elif module_name == "Drawings":

        _run_module(
            "Drawings",
            render_drawings_module,
            db,
        )

    elif module_name == "RFIs":

        _run_module(
            "RFIs",
            render_rfis_module,
            db,
        )

    elif module_name == "Tasks":

        _run_module(
            "Tasks",
            render_tasks_module,
            db,
        )

    elif module_name == "Settings":

        render_settings()

    elif module_name == "Approvals":

        render_placeholder(
            "Approvals",
            "Track project approvals and decisions.",
            "approvals",
            "✅",
        )

    elif module_name == "BOQ":

        render_placeholder(
            "Bill of Quantities",
            "Manage quantities, costs and project estimates.",
            "boq",
            "📋",
        )

    elif module_name == "Site Logs":

        render_placeholder(
            "Site Logs",
            "Record daily construction site activity.",
            "site",
            "🏢",
        )

    elif module_name == "Team":

        render_placeholder(
            "Team",
            "Manage project team members and responsibilities.",
            "team",
            "👥",
        )

    else:

        st.session_state.active_module = (
            "Overview"
        )

        render_overview(db)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Start the Creative Studios Streamlit application.
    """

    configure_page()

    inject_global_css()

    initialize_session_state()

    db = get_app_database()

    if not st.session_state.authenticated:

        render_login(db)

        return

    active_module = render_sidebar()

    render_active_module(
        active_module,
        db,
    )


# ============================================================
# STREAMLIT ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()