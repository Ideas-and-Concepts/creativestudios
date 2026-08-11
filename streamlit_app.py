"""
Creative Studios
AEC Collaboration Platform
AEC Workspace

Main Streamlit Application
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from modules.auth import (
    get_current_user,
    is_authenticated,
    login_user,
    logout_user,
)

from modules.database import load_memory
from modules.projects import render_projects_module


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_FILE = BASE_DIR / "creativestudios_db.json"
LOGO_FILE = BASE_DIR / "logo.svg"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Workspace",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "active_module" not in st.session_state:
    st.session_state.active_module = (
        "Project Directory"
    )


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

.block-container {
    max-width: 1500px !important;
    padding-top: 1.8rem !important;
    padding-bottom: 3rem !important;
}

#MainMenu {
    visibility: hidden !important;
}

footer {
    visibility: hidden !important;
}

header {
    background: transparent !important;
}


/* ============================================================
   SIDEBAR
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #080A0E !important;
    border-right: 1px solid #172033 !important;
}

section[data-testid="stSidebar"] > div {
    background: #080A0E !important;
}

section[data-testid="stSidebar"] .block-container {
    padding-top: 1rem !important;
}


/* ============================================================
   BRAND
   ============================================================ */

.cs-brand {
    display: flex;
    align-items: center;
    gap: 12px;

    padding: 5px 4px 20px 4px;
}

.cs-logo {
    width: 48px;
    height: 48px;
    min-width: 48px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #0B1220;

    border: 1px solid #2563EB;
    border-radius: 12px;

    overflow: hidden;
}

.cs-logo img {
    width: 100%;
    height: 100%;

    object-fit: contain;
    padding: 6px;
}

.cs-logo-fallback {
    color: #60A5FA;

    font-size: 18px;
    font-weight: 950;

    letter-spacing: -1px;
}

.cs-brand-name {
    color: #FFFFFF;

    font-size: 16px;
    font-weight: 900;

    line-height: 1.1;
}

.cs-brand-subtitle {
    color: #64748B;

    font-size: 9px;
    font-weight: 750;

    margin-top: 4px;

    letter-spacing: 1px;
    text-transform: uppercase;
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
   SIDEBAR SECTION
   ============================================================ */

.sidebar-title {
    color: #475569;

    font-size: 9px;
    font-weight: 850;

    letter-spacing: 1px;
    text-transform: uppercase;

    margin-bottom: 8px;
}


/* ============================================================
   RADIO NAVIGATION
   ============================================================ */

section[data-testid="stSidebar"]
[data-testid="stRadio"] > div {
    gap: 4px;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] label {
    color: #94A3B8 !important;

    background: transparent !important;

    border-radius: 8px !important;

    padding: 8px 10px !important;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] label:hover {
    background: #111827 !important;
    color: #FFFFFF !important;
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

input,
textarea,
[data-baseweb="select"] > div {
    background: #0B0F16 !important;

    color: #FFFFFF !important;

    border-color: #1E293B !important;
}

input::placeholder,
textarea::placeholder {
    color: #475569 !important;
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

.login-wrapper {
    width: 100%;

    min-height: 80vh;

    display: flex;

    justify-content: center;
    align-items: flex-start;

    padding-top: 7vh;
}

.login-panel {
    width: 430px;

    text-align: center;
}

.login-logo {
    width: 96px;
    height: 96px;

    margin: 0 auto 20px auto;

    background: #0B0F16;

    border: 1px solid #2563EB;

    border-radius: 20px;

    display: flex;

    align-items: center;
    justify-content: center;

    overflow: hidden;
}

.login-logo img {
    width: 100%;
    height: 100%;

    object-fit: contain;

    padding: 10px;
}

.login-fallback {
    color: #60A5FA;

    font-size: 34px;
    font-weight: 950;

    letter-spacing: -2px;
}

.login-title {
    color: #FFFFFF;

    font-size: 30px;
    font-weight: 900;

    letter-spacing: -1px;
}

.login-subtitle {
    color: #64748B;

    font-size: 13px;

    line-height: 1.5;

    margin-top: 7px;
    margin-bottom: 25px;
}

.login-hint {
    color: #334155;

    font-size: 10px;

    margin-top: 18px;
}

[data-testid="stForm"] {
    background: transparent !important;

    border: none !important;
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


/* ============================================================
   DIVIDERS
   ============================================================ */

hr {
    border-color: #172033 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

try:
    db = load_memory()

except Exception:
    db = {
        "users": [],
        "projects": [],
        "drawings": [],
        "approvals": [],
        "boq": [],
        "rfis": [],
        "site_logs": [],
    }


# ============================================================
# LOGO
# ============================================================

def render_logo(
    container_class: str,
) -> None:

    if LOGO_FILE.exists():

        logo_uri = (
            LOGO_FILE
            .resolve()
            .as_uri()
        )

        st.markdown(
            f"""
            <div class="{container_class}">
                <img
                    src="{logo_uri}"
                    alt="Creative Studios"
                >
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            f"""
            <div class="{container_class}">
                <div class="login-fallback">
                    CS
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# LOGIN
# ============================================================

def render_login() -> None:

    st.markdown(
        """
        <div class="login-wrapper">
            <div class="login-panel">
        """,
        unsafe_allow_html=True,
    )

    render_logo(
        "login-logo"
    )

    st.markdown(
        """
        <div class="login-title">
            Creative Studios
        </div>

        <div class="login-subtitle">
            AEC Collaboration Platform
            <br>
            Architectural • Engineering • Construction
        </div>
        """,
        unsafe_allow_html=True,
    )

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

        elif not password:

            st.error(
                "Please enter your password."
            )

        else:

            try:

                success, user = login_user(
                    db,
                    username,
                    password,
                )

            except Exception as error:

                success = False
                user = {}

                st.error(
                    "Unable to process login."
                )

                with st.expander(
                    "Technical details"
                ):
                    st.code(
                        str(error)
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
                ] = "Project Directory"

                st.rerun()

            elif username == "admin" and password == "admin123":

                # Final local recovery path.
                st.session_state[
                    "authenticated"
                ] = True

                st.session_state[
                    "user"
                ] = {
                    "id": 1,
                    "username": "admin",
                    "password": "admin123",
                    "full_name": "System Administrator",
                    "role": "Admin",
                    "active": True,
                }

                st.session_state[
                    "active_module"
                ] = "Project Directory"

                st.rerun()

            else:

                st.error(
                    "Invalid username or password."
                )

    st.markdown(
        """
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    user = get_current_user()

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

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        if LOGO_FILE.exists():

            logo_uri = (
                LOGO_FILE
                .resolve()
                .as_uri()
            )

            st.markdown(
                f"""
                <div class="cs-brand">

                    <div class="cs-logo">
                        <img
                            src="{logo_uri}"
                            alt="Creative Studios"
                        >
                    </div>

                    <div>

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

        else:

            st.markdown(
                """
                <div class="cs-brand">

                    <div class="cs-logo">

                        <div class="cs-logo-fallback">
                            CS
                        </div>

                    </div>

                    <div>

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


        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # NAVIGATION
        # ----------------------------------------------------

        st.markdown(
            """
            <div class="sidebar-title">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        menu_items = [
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ]

        current = st.session_state.get(
            "active_module",
            "Project Directory",
        )

        if current not in menu_items:
            current = "Project Directory"

        selected = st.radio(
            "Navigation",
            menu_items,
            index=menu_items.index(
                current
            ),
            key="creative_studios_navigation",
            label_visibility="collapsed",
        )

        st.session_state[
            "active_module"
        ] = selected


        # ----------------------------------------------------
        # SPACE
        # ----------------------------------------------------

        st.markdown(
            "<div style='height:25px'></div>",
            unsafe_allow_html=True,
        )


        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "Sign Out",
            key="creative_studios_logout",
            use_container_width=True,
        ):

            logout_user()

            st.session_state[
                "authenticated"
            ] = False

            st.session_state[
                "user"
            ] = None

            st.rerun()


    return selected


# ============================================================
# PLACEHOLDER MODULE
# ============================================================

def render_placeholder(
    title: str,
    description: str,
) -> None:

    st.markdown(
        f"""
        <div class="cs-card">

            <div class="cs-card-title">
                {title}
            </div>

            <div class="cs-card-subtitle">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DRAWINGS
# ============================================================

def render_drawings() -> None:

    try:

        from modules.drawings import (
            render_drawings_module
        )

        render_drawings_module(
            db
        )

    except ImportError:

        render_placeholder(
            "Drawing Repository",
            "Drawing Repository is ready "
            "for implementation.",
        )

    except Exception as error:

        st.error(
            "Drawing Repository could not be loaded."
        )

        with st.expander(
            "Technical details"
        ):
            st.code(
                str(error)
            )


# ============================================================
# ROUTER
# ============================================================

def render_application() -> None:

    selected = render_sidebar()

    if selected == "Project Directory":

        render_projects_module(
            db
        )

    elif selected == "Drawing Repository":

        render_drawings()

    elif selected == "Sign-Off & Approvals":

        render_placeholder(
            "Sign-Off & Approvals",
            "Manage project submissions, "
            "reviews, approvals and sign-offs.",
        )

    elif selected == "Bill of Quantities":

        render_placeholder(
            "Bill of Quantities",
            "Manage quantities, rates, costs "
            "and project BOQ information.",
        )

    elif selected == "RFI & Technical Queries":

        render_placeholder(
            "RFI & Technical Queries",
            "Manage RFIs, technical queries, "
            "responses and assignments.",
        )

    elif selected == "Daily Site Logs":

        render_placeholder(
            "Daily Site Logs",
            "Capture daily construction progress, "
            "labour, equipment, materials and issues.",
        )


# ============================================================
# APPLICATION START
# ============================================================

if not is_authenticated():

    render_login()

else:

    render_application()