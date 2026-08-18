"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any, Callable

import streamlit as st


# ============================================================
# DATABASE IMPORTS
# ============================================================

from modules.database import (
    load_memory,
    save_memory,
    initialize_database,
)


# ============================================================
# OPTIONAL MODULE IMPORTS
# ============================================================
#
# These imports are isolated so that one optional workspace
# module cannot prevent the entire application from starting.
#
# The database contract remains unchanged.
# ============================================================

try:
    from modules.projects import render_projects_module
except Exception:
    render_projects_module = None


try:
    from modules.documents import render_documents_module
except Exception:
    render_documents_module = None


try:
    from modules.drawings import render_drawings_module
except Exception:
    render_drawings_module = None


try:
    from modules.rfis import render_rfis_module
except Exception:
    render_rfis_module = None


try:
    from modules.tasks import render_tasks_module
except Exception:
    render_tasks_module = None


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
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* ==========================================================
   GLOBAL
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
            circle at 85% 5%,
            rgba(37, 99, 235, 0.13),
            transparent 34%
        ),
        radial-gradient(
            circle at 15% 90%,
            rgba(30, 64, 175, 0.06),
            transparent 32%
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
    max-width: 1500px !important;
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
label {
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

[data-testid="stSidebar"] * {
    box-sizing: border-box;
}


/* ==========================================================
   CREATIVE STUDIOS LOGO
   ========================================================== */

/*
   The logo is intentionally built entirely from HTML/CSS.
   No external image, asset path, or uploaded file is required.
*/

.cs-logo-area {
    width: 100%;
    text-align: center;
    margin-bottom: 22px;
}

.cs-logo {
    width: 78px;
    height: 78px;
    min-width: 78px;
    min-height: 78px;

    margin: 0 auto 18px auto;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            #3B82F6 0%,
            #2563EB 48%,
            #1D4ED8 100%
        );

    border: 1px solid rgba(255,255,255,0.14);

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    box-shadow:
        0 15px 40px rgba(37,99,235,0.30),
        inset 0 1px 0 rgba(255,255,255,0.20);

    overflow: hidden;
}

.cs-logo-inner {
    width: 100%;
    height: 100%;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    color: #FFFFFF !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif !important;

    font-size: 28px !important;
    font-weight: 900 !important;

    letter-spacing: -1.5px !important;

    line-height: 1 !important;

    text-align: center !important;
}

.cs-logo-fallback {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    display: block !important;
}

.cs-brand-name {
    color: #FFFFFF !important;
    font-size: 28px !important;
    font-weight: 900 !important;
    line-height: 1.15 !important;
    text-align: center !important;
    letter-spacing: -0.8px !important;
}

.cs-brand-subtitle {
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-align: center !important;
    margin-top: 7px !important;
    letter-spacing: 1.4px !important;
    text-transform: uppercase !important;
}


/* ==========================================================
   LOGIN
   ========================================================== */

.cs-login-wrapper {
    width: 100%;
    max-width: 440px;
    margin: 7vh auto 0 auto;
}

.cs-login-card {
    background: rgba(11,15,23,0.96);
    border: 1px solid #1E293B;
    border-radius: 22px;
    padding: 34px 34px 30px 34px;

    box-shadow:
        0 25px 80px rgba(0,0,0,0.55),
        0 0 50px rgba(37,99,235,0.06);
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {
    padding: 8px 4px 20px 4px;
    margin-bottom: 14px;
    border-bottom: 1px solid #172033;
}

.cs-sidebar-brand-row {
    display: flex;
    align-items: center;
    gap: 12px;
}

.cs-sidebar-logo {
    width: 46px;
    height: 46px;
    min-width: 46px;
    min-height: 46px;

    border-radius: 13px;

    background:
        linear-gradient(
            145deg,
            #3B82F6,
            #2563EB,
            #1D4ED8
        );

    border: 1px solid rgba(255,255,255,0.12);

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    box-shadow:
        0 8px 25px rgba(37,99,235,0.30);
}

.cs-sidebar-logo-text {
    color: #FFFFFF !important;
    font-size: 17px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    letter-spacing: -0.5px !important;
}

.cs-sidebar-name {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 850 !important;
    line-height: 1.2 !important;
}

.cs-sidebar-subtitle {
    color: #64748B !important;
    font-size: 9px !important;
    margin-top: 4px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.9px !important;
}


/* ==========================================================
   SIDEBAR SECTION LABEL
   ========================================================== */

.cs-section-label {
    color: #475569 !important;
    font-size: 10px !important;
    font-weight: 850 !important;
    letter-spacing: 1.3px !important;
    text-transform: uppercase !important;
    margin-top: 17px !important;
    margin-bottom: 7px !important;
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
    color: #60A5FA !important;
    font-size: 9px !important;
    font-weight: 850 !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}

.user-name {
    color: #FFFFFF !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    margin-top: 5px !important;
}

.user-login {
    color: #64748B !important;
    font-size: 10px !important;
    margin-top: 3px !important;
}

.user-role {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 9px;
    background: #2563EB;
    color: #FFFFFF !important;
    border-radius: 999px;
    font-size: 9px !important;
    font-weight: 850 !important;
}


/* ==========================================================
   PAGE
   ========================================================== */

.cs-page-title {
    color: #FFFFFF !important;
    font-size: 30px !important;
    font-weight: 900 !important;
    letter-spacing: -0.7px !important;
    line-height: 1.15 !important;
}

.cs-page-subtitle {
    color: #64748B !important;
    font-size: 13px !important;
    margin-top: 5px !important;
    margin-bottom: 25px !important;
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
    color: #64748B !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}

.cs-kpi-value {
    color: #FFFFFF !important;
    font-size: 26px !important;
    font-weight: 900 !important;
    margin-top: 7px !important;
}

.cs-kpi-blue {
    color: #60A5FA !important;
}


/* ==========================================================
   BUTTONS
   ========================================================== */

div[data-testid="stButton"] > button {
    background: #111827 !important;
    color: #E2E8F0 !important;
    border: 1px solid #1E293B !important;
    border-radius: 9px !important;
    font-weight: 650 !important;
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

input::placeholder,
textarea::placeholder {
    color: #475569 !important;
}


/* ==========================================================
   ERROR MESSAGE
   ========================================================== */

.cs-login-error {
    color: #FCA5A5 !important;
    background: rgba(127,29,29,0.20);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 8px;
    padding: 9px 11px;
    margin-top: 10px;
    font-size: 11px;
    text-align: center;
}


/* ==========================================================
   STATUS BADGES
   ========================================================== */

.cs-status {
    display: inline-block;
    padding: 4px 9px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 800;
}

.cs-status-active {
    color: #86EFAC !important;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.20);
}

.cs-status-planning {
    color: #93C5FD !important;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.20);
}

.cs-status-completed {
    color: #A7F3D0 !important;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.20);
}


/* ==========================================================
   STREAMLIT ALERTS
   ========================================================== */

[data-testid="stAlert"] {
    border-radius: 10px !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Return the application database from session state.

    The JSON database contract remains:

        load_memory()
        save_memory()
        initialize_database()
    """

    if "database" not in st.session_state:

        try:
            st.session_state.database = (
                initialize_database()
            )

        except Exception:

            st.session_state.database = (
                load_memory()
            )

    return st.session_state.database


db = get_database()


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION_STATE: dict[str, Any] = {
    "authenticated": False,
    "user": None,
    "active_module": "Overview",
    "login_error": "",
}


for key, default_value in DEFAULT_SESSION_STATE.items():

    if key not in st.session_state:

        st.session_state[key] = default_value


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def _safe_string(value: Any) -> str:
    """Convert a value to a safe stripped string."""

    if value is None:
        return ""

    return str(value).strip()


def _password_matches(
    supplied_password: str,
    stored_password: Any,
) -> bool:
    """
    Support the common password formats used by the JSON app.

    Supported:

        password
        password_hash

    password_hash may be:

        plain text
        SHA-256 hex
        SHA-256 prefixed with sha256:
    """

    supplied = _safe_string(
        supplied_password
    )

    stored = _safe_string(
        stored_password
    )

    if not stored:
        return False

    # Plain-text compatibility.
    if hmac.compare_digest(
        supplied,
        stored,
    ):
        return True

    supplied_hash = hashlib.sha256(
        supplied.encode("utf-8")
    ).hexdigest()

    candidates = {
        supplied_hash,
        f"sha256:{supplied_hash}",
    }

    return stored.lower() in {
        value.lower()
        for value in candidates
    }


def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user from the JSON users collection.
    """

    username = _safe_string(
        username
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

        stored_username = _safe_string(
            user.get("username")
        )

        if stored_username.lower() != username.lower():
            continue

        active = user.get(
            "active",
            True,
        )

        if active is False:
            return None

        stored_password = user.get(
            "password_hash"
        )

        if stored_password is None:

            stored_password = user.get(
                "password"
            )

        if _password_matches(
            password,
            stored_password,
        ):

            return user

        return None

    return None


def ensure_default_admin(
    database: dict[str, Any],
) -> None:
    """
    Ensure the application has a usable administrator account
    when the users collection is completely empty.

    Default development credentials:

        Username: admin
        Password: admin
    """

    users = database.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        database["users"] = []
        users = database["users"]

    if users:
        return

    users.append(
        {
            "id": 1,
            "username": "admin",
            "password": "admin",
            "password_hash": "admin",
            "full_name": "System Administrator",
            "role": "Administrator",
            "email": "",
            "active": True,
        }
    )

    try:
        save_memory(database)
    except Exception:
        pass


ensure_default_admin(db)


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:
    """Render the Creative Studios login screen."""

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Branding
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-login-card">

            <div class="cs-logo-area">

                <div class="cs-logo">
                    <div class="cs-logo-inner">
                        <span class="cs-logo-fallback">
                            CS
                        </span>
                    </div>
                </div>

                <div class="cs-brand-name">
                    Creative Studios
                </div>

                <div class="cs-brand-subtitle">
                    AEC Workspace
                </div>

            </div>

        </div>
        """,
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

            username = username.strip()

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

                st.session_state.login_error = ""

                st.rerun()

            else:

                st.session_state.login_error = (
                    "Invalid username or password."
                )

    # --------------------------------------------------------
    # Error directly below the login controls
    # --------------------------------------------------------

    login_error = st.session_state.get(
        "login_error",
        "",
    )

    if login_error:

        st.markdown(
            f"""
            <div class="cs-login-error">
                {login_error}
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # Footer
    # --------------------------------------------------------

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
    """Render the main Creative Studios module navigation."""

    user = (
        st.session_state.get("user")
        or {}
    )

    # --------------------------------------------------------
    # Brand
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand">

            <div class="cs-sidebar-brand-row">

                <div class="cs-sidebar-logo">
                    <div class="cs-sidebar-logo-text">
                        CS
                    </div>
                </div>

                <div>
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

    # --------------------------------------------------------
    # Module navigation
    # --------------------------------------------------------

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

            st.session_state.active_module = (
                module_key
            )

            selected = module_key

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
    # User information
    # --------------------------------------------------------

    full_name = _safe_string(
        user.get(
            "full_name",
            "System Administrator",
        )
    )

    username = _safe_string(
        user.get(
            "username",
            "admin",
        )
    )

    role = _safe_string(
        user.get(
            "role",
            "Administrator",
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

    # --------------------------------------------------------
    # Sign out
    # --------------------------------------------------------

    if st.sidebar.button(
        "Sign Out",
        key="logout_button",
        use_container_width=True,
    ):

        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.active_module = "Overview"
        st.session_state.login_error = ""

        st.rerun()

    return selected


# ============================================================
# OVERVIEW
# ============================================================

def render_overview() -> None:
    """Render the main AEC workspace overview."""

    projects = db.get(
        "projects",
        [],
    )

    documents = db.get(
        "documents",
        [],
    )

    drawings = db.get(
        "drawings",
        [],
    )

    rfis = db.get(
        "rfis",
        [],
    )

    tasks = db.get(
        "tasks",
        [],
    )

    if not isinstance(projects, list):
        projects = []

    if not isinstance(documents, list):
        documents = []

    if not isinstance(drawings, list):
        drawings = []

    if not isinstance(rfis, list):
        rfis = []

    if not isinstance(tasks, list):
        tasks = []

    total_projects = len(projects)

    active_projects = sum(
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

    planning_projects = sum(
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

    completed_projects = sum(
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
            continue

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    st.markdown(
        '<div class="cs-page-title">'
        "AEC Workspace"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Central workspace for architectural, engineering "
        "and construction activities."
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # KPI row
    # --------------------------------------------------------

    cols = st.columns(4)

    metrics = [
        ("Projects", total_projects),
        ("Active", active_projects),
        ("Planning", planning_projects),
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

    # --------------------------------------------------------
    # Workspace statistics
    # --------------------------------------------------------

    cols = st.columns(5)

    workspace_metrics = [
        ("Documents", len(documents)),
        ("Drawings", len(drawings)),
        ("RFIs", len(rfis)),
        ("Tasks", len(tasks)),
        ("Completed Projects", completed_projects),
    ]

    for col, (label, value) in zip(
        cols,
        workspace_metrics,
    ):

        with col:

            st.markdown(
                f"""
                <div class="cs-card">

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

    # --------------------------------------------------------
    # Workspace overview card
    # --------------------------------------------------------

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
                line-height:1.7;
            ">
                Use Module Navigation in the sidebar to
                manage projects, documents, drawings, RFIs,
                tasks and construction operations.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAFE MODULE RENDERER
# ============================================================

def render_external_module(
    title: str,
    renderer: Callable[[dict[str, Any]], Any] | None,
) -> None:
    """
    Safely render an external workspace module.

    This prevents an individual module error from destroying
    the entire Creative Studios application.
    """

    if renderer is None:

        st.error(
            f"{title} module could not be loaded."
        )

        st.info(
            f"Check that modules/{title.lower().replace(' ', '_')}.py "
            "exists and can be imported."
        )

        return

    try:

        renderer(db)

    except Exception as exc:

        st.error(
            f"{title} module encountered an error."
        )

        st.code(
            f"{type(exc).__name__}: {exc}",
            language="text",
        )


# ============================================================
# PLACEHOLDER MODULE
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="cs-page-title">
            {title}
        </div>

        <div class="cs-page-subtitle">
            {description}
        </div>

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
                This workspace is ready for the next
                Creative Studios module.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SETTINGS
# ============================================================

def render_settings() -> None:

    st.markdown(
        '<div class="cs-page-title">'
        "Settings"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        "Creative Studios workspace configuration."
        "</div>",
        unsafe_allow_html=True,
    )

    user = (
        st.session_state.get("user")
        or {}
    )

    full_name = _safe_string(
        user.get(
            "full_name",
            "System Administrator",
        )
    )

    username = _safe_string(
        user.get(
            "username",
            "admin",
        )
    )

    role = _safe_string(
        user.get(
            "role",
            "Administrator",
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
) -> None:
    """Dispatch the selected sidebar module."""

    if module_name == "Overview":

        render_overview()

    elif module_name == "Projects":

        render_external_module(
            "Projects",
            render_projects_module,
        )

    elif module_name == "Documents":

        render_external_module(
            "Documents",
            render_documents_module,
        )

    elif module_name == "Drawings":

        render_external_module(
            "Drawings",
            render_drawings_module,
        )

    elif module_name == "RFIs":

        render_external_module(
            "RFIs",
            render_rfis_module,
        )

    elif module_name == "Tasks":

        render_external_module(
            "Tasks",
            render_tasks_module,
        )

    elif module_name == "Approvals":

        render_placeholder(
            "Approvals",
            "Track project approvals and decisions.",
        )

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

    elif module_name == "Settings":

        render_settings()

    else:

        st.session_state.active_module = (
            "Overview"
        )

        render_overview()


# ============================================================
# APPLICATION ENTRY
# ============================================================

if not st.session_state.get(
    "authenticated",
    False,
):

    render_login()

else:

    active_module = render_sidebar()

    render_active_module(
        active_module
    )