"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Streamlit Application Controller
"""

from __future__ import annotations

import json
from html import escape
from pathlib import Path

import streamlit as st


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="CS",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = (
    BASE_DIR / "creativestudios_db.json"
)


# ============================================================
# LOGO SEARCH
# ============================================================

LOGO_FILES = [
    BASE_DIR / "logo.png",
    BASE_DIR / "logo.jpg",
    BASE_DIR / "logo.jpeg",
    BASE_DIR / "logo.svg",

    BASE_DIR / "assets" / "logo.png",
    BASE_DIR / "assets" / "logo.jpg",
    BASE_DIR / "assets" / "logo.jpeg",
    BASE_DIR / "assets" / "logo.svg",

    BASE_DIR / "assets" / "creative_studios.png",
    BASE_DIR / "assets" / "creative_studios.jpg",
    BASE_DIR / "assets" / "creative_studios.svg",
]


def find_logo():
    for file_path in LOGO_FILES:
        if file_path.exists() and file_path.is_file():
            return file_path

    return None


LOGO_FILE = find_logo()


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "active_module" not in st.session_state:
    st.session_state["active_module"] = (
        "Overview"
    )


# ============================================================
# DATABASE
# ============================================================

def load_database():
    """
    Load the Creative Studios JSON database.

    The application continues to work even when the
    database file is missing or malformed.
    """

    # --------------------------------------------------------
    # Try modules.database first.
    # --------------------------------------------------------

    try:

        from modules.database import load_memory

        result = load_memory()

        if isinstance(result, dict):
            return result

    except Exception:
        pass


    # --------------------------------------------------------
    # Direct JSON fallback.
    # --------------------------------------------------------

    try:

        if DATABASE_FILE.exists():

            with DATABASE_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:

                result = json.load(file)

            if isinstance(result, dict):
                return result

    except Exception:
        pass


    # --------------------------------------------------------
    # Safe empty database.
    # --------------------------------------------------------

    return {
        "users": [],
        "projects": [],
        "drawings": [],
        "documents": [],
        "approvals": [],
        "boq": [],
        "rfis": [],
        "site_logs": [],
        "team": [],
    }


db = load_database()


# ============================================================
# SAFE VALUE HELPERS
# ============================================================

def clean_text(
    value,
    default="",
):
    if value is None:
        return default

    return escape(
        str(value)
    )


def get_user():
    user = st.session_state.get(
        "user"
    )

    if isinstance(user, dict):
        return user

    return {
        "id": 1,
        "username": "admin",
        "full_name": "System Administrator",
        "role": "Admin",
        "active": True,
    }


# ============================================================
# AUTHENTICATION
# ============================================================

def authenticate(
    username,
    password,
):
    """
    Authenticate the user.

    The application first attempts to use modules.auth.
    If that is unavailable, a safe local administrator
    account is available for the initial application.
    """

    username = str(
        username or ""
    ).strip()

    password = str(
        password or ""
    )


    # --------------------------------------------------------
    # Try existing authentication module.
    # --------------------------------------------------------

    try:

        from modules.auth import login_user

        result = login_user(
            db,
            username,
            password,
        )

        if isinstance(
            result,
            tuple,
        ):

            success = bool(
                result[0]
            )

            user = (
                result[1]
                if len(result) > 1
                else None
            )

            if success:

                if not isinstance(
                    user,
                    dict,
                ):

                    user = {
                        "username": username,
                        "full_name": username,
                        "role": "User",
                    }

                return True, user

    except Exception:
        pass


    # --------------------------------------------------------
    # Administrator fallback.
    # --------------------------------------------------------

    if (
        username == "admin"
        and password == "admin123"
    ):

        return True, {
            "id": 1,
            "username": "admin",
            "full_name": "System Administrator",
            "role": "Admin",
            "active": True,
        }


    return False, None


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
<style>

/* ============================================================
   GLOBAL
   ============================================================ */

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {

    background: #050505 !important;
    color: #E5E7EB !important;
}


[data-testid="stHeader"] {

    background: transparent !important;
}


[data-testid="stToolbar"] {

    visibility: hidden !important;
}


#MainMenu {

    visibility: hidden !important;
}


footer {

    visibility: hidden !important;
}


.block-container {

    max-width: 1500px !important;

    padding-top: 1.4rem !important;

    padding-bottom: 3rem !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {

    background: #07090D !important;

    border-right: 1px solid #172033 !important;

    min-width: 280px !important;
}


section[data-testid="stSidebar"] > div {

    background: #07090D !important;
}


section[data-testid="stSidebar"]
.block-container {

    padding-top: 1rem !important;

    padding-left: 1rem !important;

    padding-right: 1rem !important;
}


/* ============================================================
   BRAND
   ============================================================ */

.cs-sidebar-brand {

    display: flex;

    align-items: center;

    gap: 12px;

    padding: 3px 2px 18px 2px;
}


.cs-sidebar-logo {

    width: 48px;

    height: 48px;

    min-width: 48px;

    display: flex;

    align-items: center;

    justify-content: center;

    overflow: hidden;

    background: #0B1220;

    border: 1px solid #2563EB;

    border-radius: 12px;

    box-shadow:
        0 0 18px rgba(
            37,
            99,
            235,
            0.12
        );
}


.cs-sidebar-logo img {

    width: 100%;

    height: 100%;

    object-fit: contain;

    padding: 5px;
}


.cs-sidebar-fallback {

    color: #60A5FA;

    font-size: 19px;

    font-weight: 950;

    letter-spacing: -1px;
}


.cs-sidebar-name {

    color: #FFFFFF;

    font-size: 16px;

    font-weight: 900;

    line-height: 1.1;
}


.cs-sidebar-subtitle {

    color: #64748B;

    font-size: 9px;

    font-weight: 800;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin-top: 4px;
}


/* ============================================================
   USER CARD
   ============================================================ */

.cs-user-card {

    background: #0B0F16;

    border: 1px solid #172033;

    border-radius: 12px;

    padding: 13px;

    margin-bottom: 18px;
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

    font-size: 11px;

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


/* ============================================================
   NAVIGATION
   ============================================================ */

.cs-nav-heading {

    color: #475569;

    font-size: 9px;

    font-weight: 850;

    letter-spacing: 1px;

    text-transform: uppercase;

    margin: 5px 0 8px 2px;
}


section[data-testid="stSidebar"]
[data-testid="stRadio"] {

    width: 100%;
}


section[data-testid="stSidebar"]
[data-testid="stRadio"] label {

    color: #94A3B8 !important;

    background: transparent !important;

    border-radius: 8px !important;

    padding: 8px 9px !important;
}


section[data-testid="stSidebar"]
[data-testid="stRadio"] label:hover {

    color: #FFFFFF !important;

    background: #111827 !important;
}


/* ============================================================
   BUTTONS
   ============================================================ */

.stButton > button {

    background: #2563EB !important;

    color: #FFFFFF !important;

    border: 1px solid #2563EB !important;

    border-radius: 8px !important;

    font-weight: 750 !important;
}


.stButton > button:hover {

    background: #1D4ED8 !important;

    border-color: #3B82F6 !important;
}


/* ============================================================
   INPUTS
   ============================================================ */

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {

    background: #0B0F16 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


[data-baseweb="select"] > div {

    background: #0B0F16 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}


label {

    color: #CBD5E1 !important;
}


/* ============================================================
   METRICS
   ============================================================ */

[data-testid="stMetric"] {

    background: #0B0F16 !important;

    border: 1px solid #172033 !important;

    border-radius: 12px !important;

    padding: 15px !important;
}


[data-testid="stMetricLabel"] {

    color: #64748B !important;
}


[data-testid="stMetricValue"] {

    color: #FFFFFF !important;
}


/* ============================================================
   LOGIN
   ============================================================ */

.cs-login-logo {

    width: 96px;

    height: 96px;

    margin: 0 auto 20px auto;

    display: flex;

    align-items: center;

    justify-content: center;

    overflow: hidden;

    background: #0B0F16;

    border: 1px solid #2563EB;

    border-radius: 20px;

    box-shadow:
        0 0 30px rgba(
            37,
            99,
            235,
            0.12
        );
}


.cs-login-logo img {

    width: 82px;

    height: 82px;

    object-fit: contain;
}


.cs-login-fallback {

    color: #60A5FA;

    font-size: 34px;

    font-weight: 950;

    letter-spacing: -2px;
}


.cs-login-title {

    text-align: center;

    color: #FFFFFF;

    font-size: 31px;

    font-weight: 900;
}


.cs-login-subtitle {

    text-align: center;

    color: #64748B;

    font-size: 13px;

    line-height: 1.5;

    margin-top: 7px;

    margin-bottom: 25px;
}


/* ============================================================
   CARDS
   ============================================================ */

.cs-card {

    background: #0B0F16;

    border: 1px solid #172033;

    border-radius: 14px;

    padding: 20px;
}


.cs-card-title {

    color: #FFFFFF;

    font-size: 18px;

    font-weight: 850;
}


.cs-card-subtitle {

    color: #64748B;

    font-size: 12px;

    margin-top: 5px;
}


hr {

    border-color: #172033 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login():

    left, center, right = st.columns(
        [1, 1.15, 1]
    )

    with center:

        st.markdown(
            "<div style='height:7vh'></div>",
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        if LOGO_FILE:

            st.markdown(
                '<div class="cs-login-logo">',
                unsafe_allow_html=True,
            )

            st.image(
                str(LOGO_FILE),
                width=82,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="cs-login-logo">

                    <div class="cs-login-fallback">
                        CS
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="cs-login-title">
                Creative Studios
            </div>

            <div class="cs-login-subtitle">
                AEC Collaboration Platform
                <br>
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # LOGIN FORM
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
                "Sign In",
                use_container_width=True,
            )


        if submitted:

            username = str(
                username or ""
            ).strip()

            password = str(
                password or ""
            )


            if not username:

                st.error(
                    "Please enter your username."
                )

                return


            if not password:

                st.error(
                    "Please enter your password."
                )

                return


            success, user = authenticate(
                username,
                password,
            )


            if success:

                st.session_state[
                    "authenticated"
                ] = True

                st.session_state[
                    "user"
                ] = user

                st.session_state[
                    "active_module"
                ] = "Overview"

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar():

    user = get_user()


    full_name = clean_text(
        user.get(
            "full_name",
            "System Administrator",
        ),
        "System Administrator",
    )


    username = clean_text(
        user.get(
            "username",
            "admin",
        ),
        "admin",
    )


    role = clean_text(
        user.get(
            "role",
            "Admin",
        ),
        "Admin",
    )


    with st.sidebar:

        # ====================================================
        # CREATIVE STUDIOS BRAND
        # ====================================================

        if LOGO_FILE:

            st.markdown(
                '<div class="cs-sidebar-brand">',
                unsafe_allow_html=True,
            )

            st.markdown(
                '<div class="cs-sidebar-logo">',
                unsafe_allow_html=True,
            )

            st.image(
                str(LOGO_FILE),
                width=38,
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div>

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

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

        else:

            st.markdown(
                """
                <div class="cs-sidebar-brand">

                    <div class="cs-sidebar-logo">

                        <div class="cs-sidebar-fallback">
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
                """,
                unsafe_allow_html=True,
            )


        # ====================================================
        # USER
        # ====================================================

        st.markdown(
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


        # ====================================================
        # AEC WORKSPACE
        # ====================================================

        st.markdown(
            """
            <div class="cs-nav-heading">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )


        workspace_modules = [
            "Overview",
            "Project Directory",
            "Drawing Repository",
            "AEC Library",
            "Sign-Off & Approvals",
            "Bill of Quantities",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]


        # ====================================================
        # MANAGEMENT
        # ====================================================

        st.markdown(
            """
            <div class="cs-nav-heading">
                Management
            </div>
            """,
            unsafe_allow_html=True,
        )


        management_modules = [
            "Team & Collaboration",
            "Administration",
        ]


        all_modules = (
            workspace_modules
            + management_modules
        )


        current = st.session_state.get(
            "active_module",
            "Overview",
        )


        if current not in all_modules:
            current = "Overview"


        selected = st.radio(
            "Module Navigation",
            all_modules,
            index=all_modules.index(
                current
            ),
            key="creative_studios_module_navigation",
            label_visibility="collapsed",
        )


        st.session_state[
            "active_module"
        ] = selected


        # ====================================================
        # SIDEBAR FOOTER
        # ====================================================

        st.markdown(
            "<div style='height:25px'></div>",
            unsafe_allow_html=True,
        )


        if st.button(
            "Sign Out",
            key="creative_studios_logout",
            use_container_width=True,
        ):

            try:

                from modules.auth import logout_user

                logout_user()

            except Exception:
                pass


            st.session_state[
                "authenticated"
            ] = False

            st.session_state[
                "user"
            ] = None

            st.session_state[
                "active_module"
            ] = "Overview"

            st.rerun()


# ============================================================
# OVERVIEW
# ============================================================

def render_overview():

    st.title(
        "AEC Workspace"
    )

    st.caption(
        "Creative Studios Collaboration Platform"
    )


    projects = db.get(
        "projects",
        [],
    )

    if not isinstance(
        projects,
        list,
    ):
        projects = []


    total_projects = len(
        projects
    )


    active_projects = 0
    planning_projects = 0
    completed_projects = 0
    total_budget = 0.0


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


        if status in (
            "active",
            "in progress",
            "in_progress",
        ):
            active_projects += 1

        elif status == "planning":
            planning_projects += 1

        elif status in (
            "completed",
            "complete",
        ):
            completed_projects += 1


        budget = project.get(
            "estimated_budget",
            project.get(
                "budget",
                0,
            ),
        )


        try:
            total_budget += float(
                budget or 0
            )
        except (
            TypeError,
            ValueError,
        ):
            pass


    c1, c2, c3, c4 = st.columns(4)


    with c1:
        st.metric(
            "Total Projects",
            total_projects,
        )


    with c2:
        st.metric(
            "Active",
            active_projects,
        )


    with c3:
        st.metric(
            "Planning",
            planning_projects,
        )


    with c4:
        st.metric(
            "Completed",
            completed_projects,
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                Portfolio Budget
            </div>

            <div style="
                color:#60A5FA;
                font-size:30px;
                font-weight:900;
                margin-top:8px;
            ">
                ${total_budget:,.2f}
            </div>

            <div class="cs-card-subtitle">
                Current project portfolio value
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PROJECT DIRECTORY
# ============================================================

def render_projects():

    try:

        from modules.projects import (
            render_projects_module,
        )

        render_projects_module(
            db
        )

    except Exception as error:

        st.error(
            "Project Directory could not be loaded."
        )

        with st.expander(
            "Technical details"
        ):

            st.code(
                str(error)
            )


# ============================================================
# SAFE PLACEHOLDER MODULE
# ============================================================

def render_placeholder(
    title,
    description,
):

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                {clean_text(title)}
            </div>

            <div class="cs-card-subtitle">
                {clean_text(description)}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DRAWINGS
# ============================================================

def render_drawings():

    try:

        from modules.drawings import (
            render_drawings_module,
        )

        render_drawings_module(
            db
        )

    except Exception:

        render_placeholder(
            "Drawing Repository",
            "Manage architectural, structural, "
            "MEP and construction drawings.",
        )


# ============================================================
# AEC LIBRARY
# ============================================================

def render_library():

    st.title(
        "AEC Library"
    )

    st.caption(
        "Central repository for project documents "
        "and technical resources."
    )


    documents = db.get(
        "documents",
        [],
    )


    if not isinstance(
        documents,
        list,
    ):
        documents = []


    c1, c2, c3 = st.columns(3)


    with c1:
        st.metric(
            "Documents",
            len(documents),
        )


    with c2:
        st.metric(
            "Project Files",
            len(
                [
                    x
                    for x in documents
                    if isinstance(x, dict)
                    and x.get("project_id")
                ]
            ),
        )


    with c3:
        st.metric(
            "Categories",
            len(
                set(
                    str(
                        x.get(
                            "category",
                            "General",
                        )
                    )
                    for x in documents
                    if isinstance(x, dict)
                )
            ),
        )


    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    render_placeholder(
        "Document Library",
        "Store drawings, specifications, contracts, "
        "reports, templates, standards and other "
        "AEC project resources.",
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

def render_application():

    # Sidebar ALWAYS appears after login.
    render_sidebar()


    active = st.session_state.get(
        "active_module",
        "Overview",
    )


    if active == "Overview":

        render_overview()


    elif active == "Project Directory":

        render_projects()


    elif active == "Drawing Repository":

        render_drawings()


    elif active == "AEC Library":

        render_library()


    elif active == "Sign-Off & Approvals":

        render_placeholder(
            "Sign-Off & Approvals",
            "Manage submissions, reviews, approvals "
            "and project sign-off workflows.",
        )


    elif active == "Bill of Quantities":

        render_placeholder(
            "Bill of Quantities",
            "Manage project quantities, rates, "
            "materials and construction costs.",
        )


    elif active == "RFI & Technical Queries":

        render_placeholder(
            "RFI & Technical Queries",
            "Manage RFIs, technical queries, "
            "responses and technical assignments.",
        )


    elif active == "Daily Site Logs":

        render_placeholder(
            "Daily Site Logs",
            "Capture daily construction progress, "
            "labour, equipment, materials and issues.",
        )


    elif active == "Team & Collaboration":

        render_placeholder(
            "Team & Collaboration",
            "Manage project teams, responsibilities, "
            "collaboration and assignments.",
        )


    elif active == "Administration":

        render_placeholder(
            "Administration",
            "Manage users, permissions, system "
            "configuration and application settings.",
        )


# ============================================================
# APPLICATION ENTRY
# ============================================================

if st.session_state.get(
    "authenticated",
    False,
):

    render_application()

else:

    render_login()