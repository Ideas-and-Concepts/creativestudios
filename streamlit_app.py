"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.

Architecture
------------
- Streamlit UI
- JSON database through modules.database
- Module-based workspace
- Inline SVG branding
- Session-state authentication
- Safe main() entry point
"""

from __future__ import annotations

from typing import Any, Callable

import hashlib

import streamlit as st


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
#
# These imports are intentionally isolated so that one module
# error does not prevent the rest of the application from
# loading.
#
# The modules use the existing JSON database contract:
#
#     render_xxx_module(db)
#
# ============================================================

try:
    from modules.projects import (
        render_projects_module,
    )
except Exception:
    render_projects_module = None


try:
    from modules.documents import (
        render_documents_module,
    )
except Exception:
    render_documents_module = None


try:
    from modules.drawings import (
        render_drawings_module,
    )
except Exception:
    render_drawings_module = None


try:
    from modules.rfis import (
        render_rfis_module,
    )
except Exception:
    render_rfis_module = None


try:
    from modules.tasks import (
        render_tasks_module,
    )
except Exception:
    render_tasks_module = None


try:
    from modules.approvals import (
        render_approvals_module,
    )
except Exception:
    render_approvals_module = None


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
    max-width: 430px;
    margin: 8vh auto 0 auto;
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

.cs-brand-name {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 900;
    text-align: center;
    margin-top: 18px;
}

.cs-brand-subtitle {
    color: #64748B;
    font-size: 12px;
    text-align: center;
    margin-top: 4px;
    letter-spacing: 1px;
    text-transform: uppercase;
}


/* ==========================================================
   LOGIN LOGO
   ========================================================== */

.cs-logo {
    width: 74px !important;
    height: 74px !important;

    min-width: 74px !important;
    min-height: 74px !important;

    max-width: 74px !important;
    max-height: 74px !important;

    flex: 0 0 74px !important;
    flex-shrink: 0 !important;

    display: flex !important;

    align-items: center !important;
    justify-content: center !important;

    margin: 0 auto !important;
    padding: 0 !important;

    line-height: 0 !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    border-radius: 18px;

    background: #2563EB;

    box-shadow:
        0 10px 35px rgba(37,99,235,0.35);
}

.cs-logo svg {
    display: block !important;

    width: 74px !important;
    height: 74px !important;

    min-width: 74px !important;
    min-height: 74px !important;

    max-width: 74px !important;
    max-height: 74px !important;

    flex: 0 0 74px !important;
    flex-shrink: 0 !important;

    margin: 0 !important;
    padding: 0 !important;
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {
    width: 100%;
    box-sizing: border-box;

    padding: 8px 4px 20px 4px;
    margin: 0 0 15px 0;

    border-bottom: 1px solid #172033;
}

.cs-sidebar-brand-row {
    width: 100%;

    display: flex;
    flex-direction: row;

    align-items: center;
    justify-content: flex-start;

    gap: 12px;

    min-height: 46px;

    box-sizing: border-box;
}


/* ==========================================================
   SIDEBAR LOGO
   ========================================================== */

.cs-sidebar-logo {
    width: 46px !important;
    height: 46px !important;

    min-width: 46px !important;
    min-height: 46px !important;

    max-width: 46px !important;
    max-height: 46px !important;

    flex: 0 0 46px !important;
    flex-shrink: 0 !important;

    display: flex !important;

    align-items: center !important;
    justify-content: center !important;

    align-self: center !important;

    margin: 0 !important;
    padding: 0 !important;

    line-height: 0 !important;

    box-sizing: border-box !important;

    overflow: hidden !important;

    border-radius: 13px;

    background: #2563EB;

    box-shadow:
        0 8px 25px rgba(37,99,235,0.30);
}

.cs-sidebar-logo svg {
    display: block !important;

    width: 46px !important;
    height: 46px !important;

    min-width: 46px !important;
    min-height: 46px !important;

    max-width: 46px !important;
    max-height: 46px !important;

    flex: 0 0 46px !important;
    flex-shrink: 0 !important;

    margin: 0 !important;
    padding: 0 !important;

    align-self: center !important;

    vertical-align: middle !important;
}


/* ==========================================================
   SIDEBAR BRAND TEXT
   ========================================================== */

.cs-sidebar-brand-text {
    min-width: 0;

    flex: 1 1 auto;

    display: flex;
    flex-direction: column;

    justify-content: center;

    align-self: center;
}

.cs-sidebar-name {
    color: #FFFFFF;

    font-size: 16px;
    font-weight: 850;

    line-height: 1.2;

    margin: 0;
    padding: 0;

    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cs-sidebar-subtitle {
    color: #64748B;

    font-size: 10px;

    line-height: 1.3;

    margin-top: 3px;
    padding: 0;

    text-transform: uppercase;
    letter-spacing: 0.8px;

    white-space: nowrap;
}


/* ==========================================================
   SIDEBAR SECTION
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
   PAGE HEADERS
   ========================================================== */

.cs-page-title {
    color: #FFFFFF;

    font-size: 30px;
    font-weight: 900;

    letter-spacing: -0.7px;
}

.cs-page-subtitle {
    color: #64748B;

    font-size: 13px;

    margin-top: 4px;
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


/* ==========================================================
   KPI
   ========================================================== */

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

.cs-kpi-blue {
    color: #60A5FA;
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
   ALERTS
   ========================================================== */

div[data-testid="stAlert"] {
    border-radius: 10px;
}


/* ==========================================================
   RESPONSIVE SIDEBAR
   ========================================================== */

@media (max-width: 768px) {

    .cs-sidebar-name {
        font-size: 14px;
    }

    .cs-sidebar-subtitle {
        font-size: 9px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE HELPER
# ============================================================

def get_database() -> dict[str, Any]:
    """
    Return the application's current JSON database.

    The database is stored in session state so modules share
    the same in-memory object during the current Streamlit run.
    """

    if "database" not in st.session_state:

        st.session_state.database = (
            initialize_database()
        )

    else:

        try:

            st.session_state.database = (
                load_memory()
            )

        except Exception:

            st.session_state.database = (
                initialize_database()
            )

    return st.session_state.database


# ============================================================
# SESSION STATE
# ============================================================

def initialize_session_state() -> None:
    """
    Initialize application session state without overwriting
    existing values.
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
# PASSWORD HELPER
# ============================================================

def _hash_password(password: str) -> str:
    """
    SHA-256 helper for compatibility with simple JSON users.

    If existing user records already contain password_hash,
    this allows plain passwords in the login form to be checked
    against the stored hash.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user from the users collection.

    Supported records:

        {
            "username": "admin",
            "password": "...",
            "password_hash": "...",
            "active": true
        }

    password_hash is preferred.
    """

    username = (
        username or ""
    ).strip()

    password = (
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

    password_hash = _hash_password(
        password
    )

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

        if (
            stored_username.lower()
            != username.lower()
        ):
            continue

        if user.get(
            "active",
            True,
        ) is False:

            return None

        stored_hash = user.get(
            "password_hash"
        )

        stored_password = user.get(
            "password"
        )

        if stored_hash:

            if str(
                stored_hash
            ) == password_hash:

                return user

        elif stored_password is not None:

            if str(
                stored_password
            ) == password:

                return user

    return None


# ============================================================
# SVG LOGO
# ============================================================

def render_cs_logo(
    size: int = 74,
    sidebar: bool = False,
) -> None:
    """
    Render the Creative Studios logo using inline SVG.

    Sidebar version:
    - fixed 46 x 46 dimensions
    - cannot shrink
    - vertically centered
    - cannot stretch
    - no emoji font dependency
    """

    if sidebar:

        logo_size = 46
        radius = 13
        wrapper_class = "cs-sidebar-logo"

    else:

        logo_size = size
        radius = 18
        wrapper_class = "cs-logo"

    st.markdown(
        f"""
        <div
            class="{wrapper_class}"
            style="
                width:{logo_size}px;
                height:{logo_size}px;

                min-width:{logo_size}px;
                min-height:{logo_size}px;

                max-width:{logo_size}px;
                max-height:{logo_size}px;

                flex:0 0 {logo_size}px;
                flex-shrink:0;

                display:flex;
                align-items:center;
                justify-content:center;

                align-self:center;

                margin:0;
                padding:0;

                line-height:0;

                box-sizing:border-box;

                overflow:hidden;

                border-radius:{radius}px;

                background:#2563EB;
            "
        >

            <svg
                width="{logo_size}"
                height="{logo_size}"
                viewBox="0 0 100 100"
                xmlns="http://www.w3.org/2000/svg"
                role="img"
                aria-label="Creative Studios logo"

                style="
                    display:block;

                    width:{logo_size}px;
                    height:{logo_size}px;

                    min-width:{logo_size}px;
                    min-height:{logo_size}px;

                    max-width:{logo_size}px;
                    max-height:{logo_size}px;

                    flex:0 0 {logo_size}px;
                    flex-shrink:0;

                    margin:0;
                    padding:0;

                    vertical-align:middle;
                "
            >

                <rect
                    x="0"
                    y="0"
                    width="100"
                    height="100"
                    rx="18"
                    fill="#2563EB"
                />

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


# ============================================================
# MODULE HEADER
# ============================================================

def render_module_header(
    title: str,
    subtitle: str,
) -> None:
    """
    Shared module heading helper.
    """

    st.markdown(
        f"""
        <div class="cs-page-title">
            {title}
        </div>

        <div class="cs-page-subtitle">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:
    """
    Render the authentication page.

    Branding and login controls intentionally live in the same
    visual card.
    """

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------

    render_cs_logo()

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="cs-brand-name">
            Creative Studios
        </div>

        <div class="cs-brand-subtitle">
            AEC Workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

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

            username = (
                username or ""
            ).strip()

            user = authenticate_user(
                username,
                password,
                st.session_state.database,
            )

            if user is not None:

                st.session_state.authenticated = True

                st.session_state.user = user

                st.session_state.active_module = (
                    "Overview"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.markdown(
        """
        </div>

        <div style="
            text-align:center;
            margin-top:18px;
            color:#475569;
            font-size:11px;
        ">
            Creative Studios • AEC Collaboration Platform
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:
    """
    Render the application sidebar.

    Navigation order is preserved.
    """

    user = (
        st.session_state.get("user")
        or {}
    )

    # --------------------------------------------------------
    # BRANDING
    # --------------------------------------------------------

    st.sidebar.markdown(
        """
        <div class="cs-sidebar-brand">
            <div class="cs-sidebar-brand-row">
        """,
        unsafe_allow_html=True,
    )

    render_cs_logo(
        sidebar=True
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
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # NAVIGATION LABEL
    # --------------------------------------------------------

    st.sidebar.markdown(
        '<div class="cs-section-label">'
        "Module Navigation"
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # MODULES
    # --------------------------------------------------------

    modules = [
        ("Overview", "Overview"),
        ("Projects", "Project Directory"),
        ("Documents", "Documents"),
        ("Drawings", "Drawings"),
        ("Approvals", "Approvals"),
        ("BOQ", "Bill of Quantities"),
        ("RFIs", "RFIs"),
        ("Site Logs", "Site Logs"),
        ("Tasks", "Tasks"),
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

    # --------------------------------------------------------
    # ADMINISTRATION
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

        selected = "Settings"

        st.session_state.active_module = (
            "Settings"
        )

        st.rerun()

    # --------------------------------------------------------
    # USER CARD
    # --------------------------------------------------------

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
    # SIGN OUT
    # --------------------------------------------------------

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
        "AEC Workspace",
        (
            "Central workspace for architectural, "
            "engineering and construction activities."
        ),
    )

    cols = st.columns(4)

    metrics = [
        ("Projects", total),
        ("Active", active),
        ("Planning", planning),
        (
            "Portfolio Budget",
            f"${budget:,.2f}",
        ),
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
                line-height:1.6;
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
                <strong>
                    {full_name}
                </strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Username:
                <strong>
                    @{username}
                </strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Role:
                <strong>
                    {role}
                </strong>
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
# SAFE MODULE EXECUTION
# ============================================================

def run_module(
    module_name: str,
    renderer: Callable[[dict[str, Any]], Any] | None,
    database: dict[str, Any],
) -> None:
    """
    Safely execute a module renderer.

    A module failure is displayed inside the application
    instead of taking down the entire Streamlit application.
    """

    if renderer is None:

        st.error(
            f"{module_name} module is not available."
        )

        st.caption(
            f"Check that the corresponding modules/{module_name.lower()}.py "
            "file exists and exposes the expected renderer."
        )

        return

    try:

        renderer(database)

    except Exception as exc:

        st.error(
            f"{module_name} module encountered an error."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# ACTIVE MODULE ROUTER
# ============================================================

def render_active_module(
    module_name: str,
    database: dict[str, Any],
) -> None:
    """
    Route the selected sidebar module to its renderer.
    """

    if module_name == "Overview":

        render_overview(
            database
        )

    elif module_name == "Projects":

        run_module(
            "Projects",
            render_projects_module,
            database,
        )

    elif module_name == "Documents":

        run_module(
            "Documents",
            render_documents_module,
            database,
        )

    elif module_name == "Drawings":

        run_module(
            "Drawings",
            render_drawings_module,
            database,
        )

    elif module_name == "Approvals":

        run_module(
            "Approvals",
            render_approvals_module,
            database,
        )

    elif module_name == "RFIs":

        run_module(
            "RFIs",
            render_rfis_module,
            database,
        )

    elif module_name == "Tasks":

        run_module(
            "Tasks",
            render_tasks_module,
            database,
        )

    elif module_name == "BOQ":

        render_placeholder(
            "Bill of Quantities",
            (
                "Manage quantities, costs and "
                "project estimates."
            ),
        )

    elif module_name == "Site Logs":

        render_placeholder(
            "Site Logs",
            (
                "Record daily construction "
                "site activity."
            ),
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

        st.session_state.active_module = (
            "Overview"
        )

        render_overview(
            database
        )


# ============================================================
# MAIN APPLICATION
# ============================================================

def main() -> None:
    """
    Main Streamlit application entry point.
    """

    initialize_session_state()

    database = get_database()

    if not st.session_state.authenticated:

        render_login()

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