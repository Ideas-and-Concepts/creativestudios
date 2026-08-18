"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit application.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st


# ============================================================
# DATABASE
# ============================================================

from modules.database import (
    load_memory,
    initialize_database,
)


# ============================================================
# OPTIONAL MODULE IMPORTS
# ============================================================

# These imports are deliberately protected so that one missing
# workspace module does not prevent the whole application from
# starting.

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
   TEXT
   ========================================================== */

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
        0 20px 70px rgba(0, 0, 0, 0.55),
        0 0 40px rgba(37, 99, 235, 0.06);
}


/* ==========================================================
   LOGIN LOGO
   ========================================================== */

.cs-logo {
    width: 82px;
    height: 82px;

    min-width: 82px;
    min-height: 82px;

    margin: 0 auto 18px auto;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            #2563EB 0%,
            #1D4ED8 55%,
            #172554 100%
        );

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    position: relative;
    overflow: hidden;

    box-shadow:
        0 14px 35px rgba(37, 99, 235, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

.cs-logo::before {
    content: "";

    position: absolute;

    width: 42px;
    height: 42px;

    border:
        2px solid
        rgba(255, 255, 255, 0.22);

    transform: rotate(45deg);

    border-radius: 7px;
}

.cs-logo-text {
    position: relative;

    z-index: 2;

    color: #FFFFFF !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: 27px;

    line-height: 1;

    font-weight: 900;

    letter-spacing: -1.5px;

    text-align: center;

    display: block !important;

    visibility: visible !important;

    opacity: 1 !important;
}


/* ==========================================================
   LOGIN BRAND
   ========================================================== */

.cs-brand-name {
    color: #FFFFFF !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: 28px;

    line-height: 1.15;

    font-weight: 900;

    text-align: center;

    letter-spacing: -0.8px;

    display: block !important;

    visibility: visible !important;
}

.cs-brand-subtitle {
    color: #64748B !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: 11px;

    line-height: 1.4;

    text-align: center;

    margin-top: 6px;

    letter-spacing: 1.6px;

    text-transform: uppercase;

    display: block !important;

    visibility: visible !important;
}


/* ==========================================================
   SIDEBAR BRAND
   ========================================================== */

.cs-sidebar-brand {
    width: 100%;

    padding:
        8px
        4px
        18px
        4px;

    margin-bottom: 14px;

    border-bottom:
        1px solid #172033;
}

.cs-sidebar-brand-row {
    width: 100%;

    display: flex !important;

    align-items: center !important;

    gap: 11px;

    visibility: visible !important;
}

.cs-sidebar-logo {
    width: 48px;
    height: 48px;

    min-width: 48px;
    min-height: 48px;

    border-radius: 14px;

    background:
        linear-gradient(
            145deg,
            #2563EB 0%,
            #1D4ED8 55%,
            #172554 100%
        );

    display: flex !important;

    align-items: center !important;
    justify-content: center !important;

    position: relative;

    overflow: hidden;

    box-shadow:
        0 8px 25px
        rgba(37, 99, 235, 0.30);
}

.cs-sidebar-logo::before {
    content: "";

    position: absolute;

    width: 25px;
    height: 25px;

    border:
        2px solid
        rgba(255, 255, 255, 0.22);

    transform: rotate(45deg);

    border-radius: 5px;
}

.cs-sidebar-logo-text {
    position: relative;

    z-index: 2;

    color: #FFFFFF !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: 17px;

    line-height: 1;

    font-weight: 900;

    letter-spacing: -1px;

    display: block !important;

    visibility: visible !important;

    opacity: 1 !important;
}

.cs-sidebar-name {
    color: #FFFFFF !important;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    font-size: 16px;

    line-height: 1.2;

    font-weight: 850;

    display: block !important;
}

.cs-sidebar-subtitle {
    color: #64748B !important;

    font-size: 9px;

    line-height: 1.3;

    margin-top: 4px;

    text-transform: uppercase;

    letter-spacing: 1px;

    display: block !important;
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
   USER CARD
   ========================================================== */

.cs-user-card {
    background: #0B0F17;

    border:
        1px solid #172033;

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


/* ==========================================================
   PAGE
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
   BRANDING VISIBILITY
   ========================================================== */

.cs-logo,
.cs-logo-text,
.cs-sidebar-brand,
.cs-sidebar-brand-row,
.cs-sidebar-logo,
.cs-sidebar-logo-text,
.cs-sidebar-name,
.cs-sidebar-subtitle {
    visibility: visible !important;

    opacity: 1 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# BRANDING FUNCTIONS
# ============================================================

def render_login_brand() -> None:
    """Render login-page Creative Studios branding."""

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    """Render sidebar Creative Studios branding."""

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


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

if "database" not in st.session_state:

    st.session_state.database = (
        initialize_database()
    )

else:

    # Refresh the database reference without
    # destroying the session.
    st.session_state.database = load_memory()


db = st.session_state.database


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_SESSION = {
    "authenticated": False,
    "user": None,
    "active_module": "Overview",
}


for key, value in DEFAULT_SESSION.items():

    if key not in st.session_state:

        st.session_state[key] = value


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate_user(
    username: str,
    password: str,
    database: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Authenticate against the users collection.

    Supports the current JSON database contract.
    """

    users = database.get(
        "users",
        [],
    )

    if not isinstance(
        users,
        list,
    ):
        return None

    username = (
        username or ""
    ).strip()

    password = (
        password or ""
    ).strip()

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

        if stored_username.lower() != username.lower():
            continue

        if user.get(
            "active",
            True,
        ) is False:
            return None

        # ----------------------------------------------------
        # Plain-text compatibility
        # ----------------------------------------------------

        stored_password = user.get(
            "password"
        )

        if stored_password is not None:

            if str(stored_password) == password:

                return user

        # ----------------------------------------------------
        # Existing password_hash compatibility
        # ----------------------------------------------------

        stored_hash = user.get(
            "password_hash"
        )

        if stored_hash is not None:

            if str(stored_hash) == password:

                return user

    return None


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:
    """Render the login page."""

    st.markdown(
        '<div class="cs-login-wrapper">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-login-card">',
        unsafe_allow_html=True,
    )

    # IMPORTANT:
    # Branding is rendered before the login form.
    render_login_brand()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.write("")

    # ========================================================
    # LOGIN FORM
    # ========================================================

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

            password = (
                password or ""
            ).strip()

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
    """Render the application sidebar."""

    user = (
        st.session_state.get(
            "user"
        )
        or {}
    )

    # IMPORTANT:
    # Sidebar branding is rendered on every authenticated
    # Streamlit rerun.
    render_sidebar_brand()

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

            st.rerun()

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

    # ========================================================
    # USER CARD
    # ========================================================

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

    # ========================================================
    # LOGOUT
    # ========================================================

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

def render_overview() -> None:
    """Render the AEC workspace overview."""

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

    active = 0
    planning = 0
    completed = 0

    budget = 0.0

    for project in projects:

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
        'AEC Workspace'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        'Central workspace for architectural, '
        'engineering and construction activities.'
        '</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(4)

    metrics = [
        ("Projects", total),
        ("Active", active),
        ("Planning", planning),
        ("Portfolio Budget", f"${budget:,.2f}"),
    ]

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
                Use Module Navigation in the sidebar
                to access projects, documents, drawings,
                RFIs, tasks and other construction
                operations.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SAFE MODULE RUNNER
# ============================================================

def run_module(
    renderer: Any,
    module_name: str,
) -> None:
    """
    Safely execute an optional workspace module.
    """

    if renderer is None:

        render_placeholder(
            module_name,
            f"{module_name} module is not installed yet.",
        )

        return

    try:

        renderer(db)

    except Exception as exc:

        st.error(
            f"{module_name} could not be loaded."
        )

        st.code(
            f"{type(exc).__name__}: {exc}"
        )


# ============================================================
# PLACEHOLDER
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:
    """Render a safe placeholder for future modules."""

    safe_title = html.escape(
        title
    )

    safe_description = html.escape(
        description
    )

    st.markdown(
        f"""
        <div class="cs-page-title">
            {safe_title}
        </div>

        <div class="cs-page-subtitle">
            {safe_description}
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
                {safe_title}
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
    """Render workspace settings."""

    st.markdown(
        '<div class="cs-page-title">'
        'Settings'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="cs-page-subtitle">'
        'Creative Studios workspace configuration.'
        '</div>',
        unsafe_allow_html=True,
    )

    user = (
        st.session_state.get(
            "user"
        )
        or {}
    )

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
# MODULE ROUTER
# ============================================================

def render_active_module(
    module_name: str,
) -> None:
    """Dispatch the selected workspace module."""

    if module_name == "Overview":

        render_overview()

    elif module_name == "Projects":

        run_module(
            render_projects_module,
            "Project Directory",
        )

    elif module_name == "Documents":

        run_module(
            render_documents_module,
            "Documents",
        )

    elif module_name == "Drawings":

        run_module(
            render_drawings_module,
            "Drawings",
        )

    elif module_name == "RFIs":

        run_module(
            render_rfis_module,
            "RFIs",
        )

    elif module_name == "Tasks":

        run_module(
            render_tasks_module,
            "Tasks",
        )

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

        render_overview()


# ============================================================
# APPLICATION
# ============================================================

if not st.session_state.authenticated:

    render_login()

else:

    active_module = render_sidebar()

    render_active_module(
        active_module
    )