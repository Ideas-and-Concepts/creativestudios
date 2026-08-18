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
- Native PNG branding
- Sidebar branding
- Logo-only login branding
- Shared module branding
- Active sidebar module indicator
- Session-state navigation
"""

from __future__ import annotations

import html
import importlib
from pathlib import Path
from typing import Any

import streamlit as st


# ============================================================
# APPLICATION PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ASSETS_DIR = BASE_DIR / "assets"

LOGO_PATH = ASSETS_DIR / "Artboard 1.png"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon="assets/Artboard 1.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BRANDING HELPERS
# ============================================================

def logo_exists() -> bool:
    """
    Check whether the Creative Studios logo exists.
    """

    return (
        LOGO_PATH.exists()
        and LOGO_PATH.is_file()
    )


def verify_branding_asset() -> bool:
    """
    Verify the shared Creative Studios logo.
    """

    return logo_exists()


# ============================================================
# DATABASE
# ============================================================

from modules.database import (
    add_record,
    delete_record,
    get_record,
    get_records,
    initialize_database,
    load_memory,
    next_id,
    save_memory,
    update_record,
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

    An unavailable module will not prevent the
    rest of the application from starting.
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
            rgba(37, 99, 235, 0.10),
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

    border-right:
        1px solid #172033 !important;
}


[data-testid="stSidebar"] > div:first-child {

    background: #080B12 !important;
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {

    width: 100%;

    padding:
        6px 2px 18px 2px;

    margin-bottom: 14px;

    border-bottom:
        1px solid #172033;

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


.cs-sidebar-logo {

    width: 46px !important;

    height: 46px !important;

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
   SIDEBAR SECTION LABEL
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
   SIDEBAR BUTTONS
   ========================================================== */

[data-testid="stSidebar"] div[data-testid="stButton"] {

    margin-bottom: 3px;
}


[data-testid="stSidebar"]
div[data-testid="stButton"] > button {

    background: transparent !important;

    color: #94A3B8 !important;

    border: 1px solid transparent !important;

    border-radius: 9px !important;

    min-height: 38px;

    text-align: left !important;

    transition:
        background 0.15s ease,
        border 0.15s ease,
        color 0.15s ease;
}


[data-testid="stSidebar"]
div[data-testid="stButton"] > button:hover {

    background: #111827 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


/* ==========================================================
   ACTIVE SIDEBAR MODULE
   ========================================================== */

[data-testid="stSidebar"]
.cs-nav-active {

    position: relative;

    background:
        linear-gradient(
            90deg,
            rgba(37, 99, 235, 0.18),
            rgba(37, 99, 235, 0.05)
        );

    border-left:
        3px solid #3B82F6;

    color: #FFFFFF;

    border-radius: 9px;
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
   LOGIN
   ========================================================== */

.cs-login-wrapper {

    width: min(430px, 92vw);

    margin:
        7vh auto 0 auto;
}


.cs-login-card {

    background: #0B0F17;

    border:
        1px solid #1E293B;

    border-radius: 20px;

    padding:
        30px 36px 36px 36px;

    box-shadow:
        0 20px 70px rgba(0, 0, 0, 0.55),
        0 0 40px rgba(37, 99, 235, 0.06);

    text-align: center;
}


/* ==========================================================
   LOGIN LOGO
   ========================================================== */

.cs-login-logo {

    display: flex;

    align-items: center;

    justify-content: center;

    width: 100%;

    margin:
        0 auto 22px auto;

    padding: 4px 0;
}


.cs-login-card
[data-testid="stImage"] {

    display: flex;

    justify-content: center;

    align-items: center;

    margin:
        0 auto 20px auto;
}


.cs-login-card
[data-testid="stImage"] img {

    width: 100px !important;

    height: 100px !important;

    max-width: 100px !important;

    max-height: 100px !important;

    object-fit: contain;
}


/* ==========================================================
   LOGIN INPUTS
   ========================================================== */

.cs-login-card
[data-testid="stTextInput"] {

    margin-top: 4px;
}


.cs-login-card
input {

    background: #0B0F17 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

div[data-testid="stButton"] > button {

    background: #111827 !important;

    color: #E2E8F0 !important;

    border:
        1px solid #1E293B !important;

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

    border:
        1px solid #172033;

    border-radius: 15px;

    padding: 20px;
}


.cs-kpi {

    background: #0B0F17;

    border:
        1px solid #172033;

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
   LOGIN ERROR
   ========================================================== */

.cs-login-error {

    background:
        rgba(127, 29, 29, 0.20);

    border:
        1px solid rgba(248, 113, 113, 0.30);

    border-radius: 9px;

    padding: 9px 12px;

    margin-top: 10px;

    color: #FCA5A5 !important;

    font-size: 12px;
}


/* ==========================================================
   LOGO WARNING
   ========================================================== */

.cs-logo-warning {

    color: #FCA5A5;

    background:
        rgba(127, 29, 29, 0.20);

    border:
        1px solid rgba(248, 113, 113, 0.25);

    border-radius: 9px;

    padding: 10px;

    font-size: 11px;

    text-align: center;
}

</style>
""",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR BRANDING
# ============================================================

def render_sidebar_branding() -> None:

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand">

            <div class="cs-sidebar-brand-row">

                <div class="cs-sidebar-logo-wrap">
        """,
        unsafe_allow_html=True,
    )

    if logo_exists():

        st.sidebar.image(
            str(LOGO_PATH),
            width=46,
        )

    st.sidebar.markdown(
        """
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

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGO ONLY
    # --------------------------------------------------------

    if logo_exists():

        st.image(
            str(LOGO_PATH),
            width=100,
        )

    else:

        st.markdown(
            """
            <div class="cs-logo-warning">
                Creative Studios logo not found.
                Check assets/Artboard 1.png.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='height:8px;'></div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGIN FORM
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
        <div style="
            text-align:center;
            margin-top:18px;
            color:#475569;
            font-size:11px;
        ">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
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

        if module_key == current:

            st.sidebar.markdown(
                f"""
                <div class="cs-nav-active">
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

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Administration"
        "</div>",
        unsafe_allow_html=True,
    )

    if current == "Settings":

        st.sidebar.markdown(
            """
            <div class="cs-nav-active">
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

            st.session_state.active_module = (
                "Settings"
            )

            st.rerun()

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

    full_name = str(
        user.get(
            "full_name",
            "",
        )
        or ""
    ).strip()

    username = str(
        user.get(
            "username",
            "",
        )
        or ""
    ).strip()

    role = str(
        user.get(
            "role",
            "",
        )
        or ""
    ).strip()

    if not full_name:

        full_name = "System Administrator"

    if not username:

        username = "admin"

    if not role:

        role = "Admin"

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
# MODULE HEADER
# ============================================================

def render_module_header(
    title: str,
    subtitle: str,
) -> None:

    safe_title = html.escape(
        str(title or "")
    )

    safe_subtitle = html.escape(
        str(subtitle or "")
    )

    logo_col, content_col = st.columns(
        [0.08, 0.92],
        vertical_alignment="center",
    )

    with logo_col:

        if logo_exists():

            st.image(
                str(LOGO_PATH),
                width=52,
            )

    with content_col:

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

    name = str(
        user.get(
            "full_name",
            "",
        )
        or ""
    ).strip()

    username = str(
        user.get(
            "username",
            "",
        )
        or ""
    ).strip()

    role = str(
        user.get(
            "role",
            "",
        )
        or ""
    ).strip()

    if not name:

        name = "System Administrator"

    if not username:

        username = "admin"

    if not role:

        role = "Admin"

    safe_name = html.escape(name)

    safe_username = html.escape(username)

    safe_role = html.escape(role)

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
                <strong>{safe_name}</strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Username:
                <strong>@{safe_username}</strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Role:
                <strong>{safe_role}</strong>
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

    # --------------------------------------------------------
    # BRANDING CHECK
    # --------------------------------------------------------

    if not verify_branding_asset():

        st.warning(
            "Creative Studios logo not found at "
            "assets/Artboard 1.png"
        )

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
    # NAVIGATION
    # --------------------------------------------------------

    active_module = render_sidebar()

    # --------------------------------------------------------
    # ACTIVE MODULE
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
