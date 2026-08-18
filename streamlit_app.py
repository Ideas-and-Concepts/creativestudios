"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import streamlit as st

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

from modules.projects import render_projects_module


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

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

[data-testid="stSidebar"] {
    background: #080B12 !important;
    border-right: 1px solid #172033 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: #080B12 !important;
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

/* ========================================================
   LOGIN
   ======================================================== */

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

.cs-logo {
    width: 74px;
    height: 74px;
    border-radius: 18px;
    background: #2563EB;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 18px auto;
    box-shadow:
        0 10px 35px rgba(37,99,235,0.35);
}

.cs-logo-text {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 900;
    letter-spacing: -1px;
}

.cs-brand-name {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 900;
    text-align: center;
}

.cs-brand-subtitle {
    color: #64748B;
    font-size: 12px;
    text-align: center;
    margin-top: 4px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ========================================================
   SIDEBAR
   ======================================================== */

.cs-sidebar-brand {
    padding: 8px 4px 20px 4px;
    margin-bottom: 15px;
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
    border-radius: 13px;
    background: #2563EB;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 8px 25px rgba(37,99,235,0.30);
}

.cs-sidebar-logo-text {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 900;
}

.cs-sidebar-name {
    color: #FFFFFF;
    font-size: 16px;
    font-weight: 850;
}

.cs-sidebar-subtitle {
    color: #64748B;
    font-size: 10px;
    margin-top: 3px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.cs-section-label {
    color: #475569;
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 1.3px;
    text-transform: uppercase;
    margin-top: 17px;
    margin-bottom: 7px;
}

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
    color: #FFFFFF;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 850;
}

/* ========================================================
   CONTENT
   ======================================================== */

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

.cs-kpi-blue {
    color: #60A5FA;
}

/* ========================================================
   BUTTONS
   ======================================================== */

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

/* ========================================================
   INPUTS
   ======================================================== */

input,
textarea,
[data-baseweb="select"] > div {
    background: #0B0F17 !important;
    color: #FFFFFF !important;
    border-color: #1E293B !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

if "database" not in st.session_state:
    st.session_state.database = initialize_database()

db = st.session_state.database


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "active_module" not in st.session_state:
    st.session_state.active_module = "Overview"


# ============================================================
# AUTHENTICATION
# ============================================================

def _hash_password(password: str) -> str:
    """
    SHA-256 password hash used by the local JSON authentication
    layer.
    """

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate a user against the JSON database.

    Supports:

        password_hash

    and, for development compatibility:

        password
    """

    username = str(username or "").strip()

    if not username or not password:
        return None

    users = database.get(
        "users",
        [],
    )

    if not isinstance(users, list):
        users = []

    password_hash = _hash_password(
        password
    )

    for user in users:

        if not isinstance(user, dict):
            continue

        stored_username = str(
            user.get(
                "username",
                "",
            )
        ).strip()

        if stored_username.lower() != username.lower():
            continue

        if user.get("active", True) is False:
            return None

        stored_hash = user.get(
            "password_hash"
        )

        if stored_hash:

            if hmac.compare_digest(
                str(stored_hash),
                password_hash,
            ):
                return user

            # Do not continue with plaintext if a hash exists.
            return None

        stored_password = user.get(
            "password"
        )

        if stored_password is not None:

            if hmac.compare_digest(
                str(stored_password),
                password,
            ):
                return user

            return None

    return None


def ensure_admin_user() -> None:
    """
    Ensure a development administrator exists.

    This only creates the admin account if the users collection
    is empty and therefore does not overwrite existing users.
    """

    users = db.get(
        "users",
        [],
    )

    if not isinstance(users, list):
        db["users"] = []
        users = db["users"]

    if users:
        return

    users.append(
        {
            "id": 1,
            "username": "admin",
            "password_hash": _hash_password(
                "admin"
            ),
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }
    )

    save_memory(db)


ensure_admin_user()


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="cs-login-card">

            <div class="cs-logo">
                <div class="cs-logo-text">
                    CS
                </div>
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
            "Sign In",
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
                st.session_state.active_module = "Overview"

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
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


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    user = (
        st.session_state.get("user")
        or {}
    )

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

            st.session_state.active_module = (
                module_key
            )

            selected = module_key

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

        selected = "Settings"

        st.rerun()

    full_name = str(
        user.get(
            "full_name",
            "System Administrator",
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
# OVERVIEW
# ============================================================

def render_overview() -> None:

    projects = db.get(
        "projects",
        [],
    )

    if not isinstance(projects, list):
        projects = []

    total = len(projects)

    active = 0
    planning = 0
    completed = 0
    budget = 0.0

    for project in projects:

        if not isinstance(project, dict):
            continue

        status = str(
            project.get(
                "status",
                "",
            )
        ).strip().lower()

        if status == "active":
            active += 1

        elif status == "planning":
            planning += 1

        elif status == "completed":
            completed += 1

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

    cols = st.columns(4)

    metrics = [
        ("Total Projects", total),
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
# PROJECTS
# ============================================================

def render_projects() -> None:

    try:

        render_projects_module(
            db
        )

    except Exception as exc:

        st.error(
            "Project Directory encountered an error."
        )

        st.exception(exc)


# ============================================================
# DOCUMENTS
# ============================================================

def render_documents() -> None:

    try:

        from modules.documents import (
            render_documents_module,
        )

        render_documents_module(
            db
        )

    except ModuleNotFoundError:

        render_placeholder(
            "Documents",
            "Central document management workspace.",
        )

    except ImportError as exc:

        st.error(
            "Documents module could not be loaded."
        )

        st.exception(exc)

    except Exception as exc:

        st.error(
            "Documents module encountered an error."
        )

        st.exception(exc)


# ============================================================
# DRAWINGS
# ============================================================

def render_drawings() -> None:

    try:

        from modules.drawings import (
            render_drawings_module,
        )

        render_drawings_module(
            db
        )

    except ModuleNotFoundError:

        render_placeholder(
            "Drawings",
            "Architectural and engineering drawing workspace.",
        )

    except ImportError as exc:

        st.error(
            "Drawings module could not be loaded."
        )

        st.exception(exc)

    except Exception as exc:

        st.error(
            "Drawings module encountered an error."
        )

        st.exception(exc)


# ============================================================
# PLACEHOLDER
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

    user = (
        st.session_state.get("user")
        or {}
    )

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
                    {user.get(
                        "full_name",
                        "System Administrator",
                    )}
                </strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Username:
                <strong>
                    @{user.get(
                        "username",
                        "admin",
                    )}
                </strong>
            </div>

            <div style="
                color:#94A3B8;
                margin-top:7px;
                font-size:13px;
            ">
                Role:
                <strong>
                    {user.get(
                        "role",
                        "Admin",
                    )}
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
) -> None:

    if module_name == "Overview":

        render_overview()

    elif module_name == "Projects":

        render_projects()

    elif module_name == "Documents":

        render_documents()

    elif module_name == "Drawings":

        render_drawings()

    elif module_name == "Settings":

        render_settings()

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

    elif module_name == "RFIs":

        render_placeholder(
            "RFIs",
            "Manage requests for information.",
        )

    elif module_name == "Site Logs":

        render_placeholder(
            "Site Logs",
            "Record daily construction site activity.",
        )

    elif module_name == "Tasks":

        render_placeholder(
            "Tasks",
            "Manage project tasks and assignments.",
        )

    elif module_name == "Team":

        render_placeholder(
            "Team",
            "Manage project team members and responsibilities.",
        )

    else:

        st.session_state.active_module = "Overview"

        render_overview()


# ============================================================
# APPLICATION START
# ============================================================

if not st.session_state.authenticated:

    render_login()

else:

    active_module = render_sidebar()

    render_active_module(
        active_module
    )