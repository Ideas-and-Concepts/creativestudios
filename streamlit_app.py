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
- SVG-based branding
- No emoji-font dependency
- Sidebar branding
- Login branding
- Session-state navigation
"""
from __future__ import annotations

from pathlib import Path

import base64
import html
import importlib
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# BRAND ASSET
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOGO_PATH = (
    BASE_DIR
    / "assets"
    / "creative_studios_logo.png"
)


def logo_exists() -> bool:
    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon="CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DATABASE
# ============================================================

from modules.database import (
    load_memory,
    save_memory,
    initialize_database,
    add_record,
    update_record,
    delete_record,
    next_id,
    get_record,
    get_records,
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

    This prevents one unfinished module from crashing the
    entire application during startup.
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
# GLOBAL CSS
# ============================================================

def inject_global_css() -> None:

    st.markdown(
        """
<style>

/* ==========================================================
   GLOBAL APPLICATION
   ========================================================== */

html,
body,
[data-testid="stAppViewContainer"] {
    background: #05070B !important;
    color: #F8FAFC !important;
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
    background: transparent !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
}

h1,
h2,
h3,
h4,
h5,
h6 {
    color: #F8FAFC !important;
}

p,
label,
span {
    color: #CBD5E1;
}


/* ==========================================================
   SIDEBAR
   ========================================================== */

[data-testid="stSidebar"] {
    background: #080B12 !important;
    border-right: 1px solid #172033 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: #080B12 !important;
}


/* ==========================================================
   LOGIN
   ========================================================== */

.cs-login-wrapper {
    width: min(430px, 92vw);
    margin: 7vh auto 0 auto;
}

.cs-login-card {
    background: #0B0F17;
    border: 1px solid #1E293B;
    border-radius: 20px;
    padding: 36px;
    box-shadow:
        0 20px 70px rgba(0,0,0,0.55),
        0 0 40px rgba(37,99,235,0.06);
}


/* ==========================================================
   SVG LOGO CONTAINERS
   ========================================================== */

.cs-logo-wrap {
    width: 76px;
    height: 76px;
    min-width: 76px;
    max-width: 76px;

    margin: 0 auto 18px auto;

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: visible;
    flex-shrink: 0;
}

.cs-logo-wrap img {
    display: block;

    width: 76px !important;
    height: 76px !important;

    min-width: 76px !important;
    min-height: 76px !important;

    max-width: 76px !important;
    max-height: 76px !important;

    object-fit: contain;

    flex-shrink: 0;
}


/* ==========================================================
   LOGIN BRAND
   ========================================================== */

.cs-brand-name {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 900;
    text-align: center;
    line-height: 1.15;
}

.cs-brand-subtitle {
    color: #64748B;
    font-size: 12px;
    text-align: center;
    margin-top: 5px;
    letter-spacing: 1px;
    text-transform: uppercase;
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {
    width: 100%;

    padding: 6px 2px 18px 2px;
    margin-bottom: 14px;

    border-bottom: 1px solid #172033;

    overflow: visible;
}

.cs-sidebar-brand-row {
    width: 100%;

    display: flex;
    align-items: center;

    gap: 11px;

    min-height: 48px;

    overflow: visible;
}

.cs-sidebar-logo-wrap {
    width: 46px;
    height: 46px;

    min-width: 46px;
    max-width: 46px;

    min-height: 46px;
    max-height: 46px;

    display: flex;
    align-items: center;
    justify-content: center;

    overflow: visible;
    flex-shrink: 0;
}

.cs-sidebar-logo-wrap img {
    display: block;

    width: 46px !important;
    height: 46px !important;

    min-width: 46px !important;
    min-height: 46px !important;

    max-width: 46px !important;
    max-height: 46px !important;

    object-fit: contain;

    flex-shrink: 0;
}

.cs-sidebar-brand-text {
    min-width: 0;
    overflow: hidden;
}

.cs-sidebar-name {
    color: #FFFFFF;
    font-size: 15px;
    font-weight: 850;
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cs-sidebar-subtitle {
    color: #64748B;
    font-size: 9px;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    white-space: nowrap;
}


/* ==========================================================
   SECTION LABEL
   ========================================================== */

.cs-section-label {
    color: #475569;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.3px;
    text-transform: uppercase;

    margin-top: 17px;
    margin-bottom: 7px;
}


/* ==========================================================
   USER CARD
   ========================================================== */

.cs-user-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 13px;

    padding: 13px;
    margin-top: 15px;
}

.user-label {
    color: #60A5FA;
    font-size: 9px;
    font-weight: 850;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.user-name {
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 800;
    margin-top: 5px;
}

.user-login {
    color: #64748B;
    font-size: 10px;
    margin-top: 3px;
}

.user-role {
    display: inline-block;

    margin-top: 8px;
    padding: 4px 9px;

    background: #2563EB;
    color: #FFFFFF !important;

    border-radius: 999px;

    font-size: 9px;
    font-weight: 850;
}


/* ==========================================================
   PAGE
   ========================================================== */

.cs-page-title {
    color: #FFFFFF;
    font-size: 30px;
    font-weight: 900;
    letter-spacing: -0.7px;
    line-height: 1.15;
}

.cs-page-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 5px;
    margin-bottom: 25px;
}


/* ==========================================================
   CARDS
   ========================================================== */

.cs-card {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;
    padding: 20px;
}

.cs-kpi {
    background: #0B0F17;
    border: 1px solid #172033;
    border-radius: 15px;

    padding: 18px;
    min-height: 110px;
}

.cs-kpi-label {
    color: #64748B;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.cs-kpi-value {
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 900;
    margin-top: 7px;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

div[data-testid="stButton"] > button {
    background: #111827 !important;
    color: #E2E8F0 !important;

    border: 1px solid #1E293B !important;
    border-radius: 9px !important;
}

div[data-testid="stButton"] > button:hover {
    background: #172554 !important;
    border-color: #2563EB !important;
    color: #FFFFFF !important;
}

div[data-testid="stFormSubmitButton"] > button {
    background: #2563EB !important;
    color: #FFFFFF !important;

    border: 0 !important;
    border-radius: 10px !important;

    font-weight: 800 !important;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    background: #1D4ED8 !important;
}


/* ==========================================================
   INPUTS
   ========================================================== */

input,
textarea,
[data-baseweb="select"] > div {
    background: #0B0F17 !important;
    color: #FFFFFF !important;
    border-color: #1E293B !important;
}


/* ==========================================================
   LOGIN ERROR
   ========================================================== */

.cs-login-error {
    background: rgba(127, 29, 29, 0.20);

    border: 1px solid rgba(248, 113, 113, 0.30);

    border-radius: 9px;

    padding: 9px 12px;

    margin-top: 10px;

    color: #FCA5A5 !important;

    font-size: 12px;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# SVG LOGO
# ============================================================

def _creative_studios_svg() -> str:
    """
    Return the canonical Creative Studios SVG logo.

    The SVG is self-contained and does not depend on:
    - emoji fonts
    - external image files
    - static directories
    - browser-installed fonts
    """

    return """
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="128"
    height="128"
    viewBox="0 0 128 128"
    fill="none"
>
    <defs>
        <linearGradient
            id="csGradient"
            x1="12"
            y1="10"
            x2="116"
            y2="118"
            gradientUnits="userSpaceOnUse"
        >
            <stop offset="0" stop-color="#3B82F6"/>
            <stop offset="1" stop-color="#1D4ED8"/>
        </linearGradient>
    </defs>

    <rect
        x="4"
        y="4"
        width="120"
        height="120"
        rx="28"
        fill="url(#csGradient)"
    />

    <rect
        x="5"
        y="5"
        width="118"
        height="118"
        rx="27"
        stroke="#60A5FA"
        stroke-opacity="0.35"
        stroke-width="2"
    />

    <path
        d="M83 40C77 35 69 32 60 32C43 32 30 45 30 64C30 83 43 96 60 96C69 96 77 93 83 88"
        stroke="white"
        stroke-width="9"
        stroke-linecap="round"
    />

    <path
        d="M73 64H101"
        stroke="white"
        stroke-width="9"
        stroke-linecap="round"
    />

    <path
        d="M92 55L101 64L92 73"
        stroke="white"
        stroke-width="7"
        stroke-linecap="round"
        stroke-linejoin="round"
    />
</svg>
"""


def _svg_data_uri() -> str:
    """
    Convert the SVG to a browser-safe base64 data URI.
    """

    svg = _creative_studios_svg().strip()

    encoded = base64.b64encode(
        svg.encode("utf-8")
    ).decode("ascii")

    return (
        "data:image/svg+xml;base64,"
        + encoded
    )


# ============================================================
# LOGIN BRANDING
# ============================================================

def render_login_branding() -> None:

    logo_uri = _svg_data_uri()

    st.markdown(
        f"""
        <div class="cs-login-card">

            <div class="cs-logo-wrap">
                <img
                    src="{logo_uri}"
                    alt="Creative Studios"
                    width="76"
                    height="76"
                />
            </div>

            <div class="cs-brand-name">
                Creative Studios
            </div>

            <div class="cs-brand-subtitle">
                AEC Workspace
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:

    logo_uri = _svg_data_uri()

    st.sidebar.markdown(
        f"""
        <div class="cs-sidebar-brand">

            <div class="cs-sidebar-brand-row">

                <div class="cs-sidebar-logo-wrap">

                    <img
                        src="{logo_uri}"
                        alt="Creative Studios"
                        width="46"
                        height="46"
                    />

                </div>

                <div class="cs-sidebar-brand-text">

                    <div class="cs-sidebar-name">
                        Creative Studios
                    </div>

                    <div class="cs-sidebar-subtitle">
                        AEC Workspace
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DATABASE HELPER
# ============================================================

def get_database() -> dict[str, Any]:

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

    defaults = {
        "authenticated": False,
        "user": None,
        "active_module": "Overview",
    }

    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value


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

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Administration"
        "</div>",
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

    full_name = html.escape(
        str(
            user.get(
                "full_name",
                "System Administrator",
            )
        )
    )

    username = html.escape(
        str(
            user.get(
                "username",
                "admin",
            )
        )
    )

    role = html.escape(
        str(
            user.get(
                "role",
                "Admin",
            )
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

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.active_module = "Overview"

        st.rerun()

    return selected


# ============================================================
# MODULE HEADER
# ============================================================

def render_module_header(
    title: str,
    subtitle: str,
) -> None:

    safe_title = html.escape(
        title
    )

    safe_subtitle = html.escape(
        subtitle
    )

    st.markdown(
        f"""
        <div class="cs-page-title">
            {safe_title}
        </div>

        <div class="cs-page-subtitle">
            {safe_subtitle}
        </div>
        """,
        unsafe_allow_html=True,
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
        ).lower()
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
        ).lower()
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
        "AEC Workspace",
        "Central workspace for architectural, "
        "engineering and construction activities.",
    )

    cols = st.columns(4)

    metrics = [
        ("Projects", total),
        ("Active", active),
        ("Planning", planning),
        ("Completed", completed),
    ]

    for col, (
        label,
        value,
    ) in zip(
        cols,
        metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="cs-kpi">

                    <div class="cs-kpi-label">
                        {html.escape(label)}
                    </div>

                    <div class="cs-kpi-value">
                        {html.escape(str(value))}
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
                {html.escape(title)}
            </div>

            <div style="
                color:#64748B;
                font-size:12px;
                margin-top:8px;
            ">
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
        st.session_state.get("user")
        or {}
    )

    name = html.escape(
        str(
            user.get(
                "full_name",
                "System Administrator",
            )
        )
    )

    username = html.escape(
        str(
            user.get(
                "username",
                "admin",
            )
        )
    )

    role = html.escape(
        str(
            user.get(
                "role",
                "Admin",
            )
        )
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
                <strong>{name}</strong>
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

    inject_global_css()

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