"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.
"""

from pathlib import Path

import streamlit as st

from modules.database import load_memory
from modules.auth import (
    is_authenticated,
    login_user,
    logout_user,
    get_current_user,
)
from modules.projects import render_projects_module


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
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
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    .main {
        background: #050505 !important;
        color: #E5E7EB !important;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    section[data-testid="stSidebar"] {
        background: #080A0E !important;
        border-right: 1px solid #172033 !important;
    }

    section[data-testid="stSidebar"] > div {
        background: #080A0E !important;
    }


    /* ======================================================
       BRAND
       ====================================================== */

    .cs-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 5px 4px 20px 4px;
    }

    .cs-logo-box {
        width: 48px;
        height: 48px;
        min-width: 48px;
        border-radius: 12px;
        background: #0B1220;
        border: 1px solid #2563EB;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }

    .cs-logo-box img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        padding: 6px;
    }

    .cs-logo-fallback {
        color: #60A5FA;
        font-size: 18px;
        font-weight: 900;
    }

    .cs-brand-name {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 850;
        line-height: 1.1;
    }

    .cs-brand-subtitle {
        color: #64748B;
        font-size: 9px;
        margin-top: 4px;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-weight: 700;
    }


    /* ======================================================
       USER CARD
       ====================================================== */

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


    /* ======================================================
       NAVIGATION
       ====================================================== */

    section[data-testid="stSidebar"] .stRadio > div {
        gap: 5px;
    }

    section[data-testid="stSidebar"] .stRadio label {
        color: #94A3B8 !important;
        background: transparent;
        border-radius: 8px;
        padding: 8px 10px;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: #111827;
        color: #FFFFFF !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

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


    /* ======================================================
       INPUTS
       ====================================================== */

    input,
    textarea,
    [data-baseweb="select"] > div {
        background: #0B0F16 !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
    }

    label {
        color: #CBD5E1 !important;
    }


    /* ======================================================
       METRICS
       ====================================================== */

    [data-testid="stMetric"] {
        background: #0B0F16;
        border: 1px solid #172033;
        border-radius: 12px;
        padding: 15px;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }


    /* ======================================================
       LOGIN
       ====================================================== */

    .login-container {
        max-width: 430px;
        margin: 7vh auto 0 auto;
        text-align: center;
    }

    .login-logo {
        width: 92px;
        height: 92px;
        margin: 0 auto 20px auto;
        border-radius: 20px;
        background: #0B0F16;
        border: 1px solid #2563EB;
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
    }

    .login-title {
        color: #FFFFFF;
        font-size: 30px;
        font-weight: 900;
    }

    .login-subtitle {
        color: #64748B;
        font-size: 13px;
        margin-top: 6px;
        margin-bottom: 25px;
    }

    [data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
    }


    /* ======================================================
       PROJECT CARDS
       ====================================================== */

    .project-card {
        background: #0B0F16;
        border: 1px solid #172033;
        border-radius: 14px;
        padding: 20px;
        margin-top: 12px;
    }

    .project-card:hover {
        border-color: #2563EB;
    }

    .project-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 850;
    }

    .project-meta {
        color: #64748B;
        font-size: 12px;
        margin-top: 5px;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 800;
    }

    .status-active {
        background: #064E3B;
        color: #6EE7B7;
    }

    .status-planning {
        background: #422006;
        color: #FCD34D;
    }

    .status-completed {
        background: #172554;
        color: #93C5FD;
    }

    .status-on-hold {
        background: #450A0A;
        color: #FCA5A5;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION INITIALIZATION
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None


# ============================================================
# DATABASE
# ============================================================

db = load_memory()


# ============================================================
# LOGIN PAGE
# ============================================================

def render_login() -> None:

    st.markdown(
        '<div class="login-container">',
        unsafe_allow_html=True,
    )

    if LOGO_FILE.exists():

        logo_path = LOGO_FILE.as_posix()

        st.markdown(
            f"""
            <div class="login-logo">
                <img src="file://{logo_path}">
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            """
            <div class="login-logo">
                <div class="login-fallback">
                    CS
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="login-title">
            Creative Studios
        </div>

        <div class="login-subtitle">
            Architectural, Engineering & Construction
            Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):

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

        success, user = login_user(
            db,
            username,
            password,
        )

        if success:

            st.session_state["authenticated"] = True
            st.session_state["user"] = user

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# SIDEBAR
# ============================================================

def render_sidebar() -> str:

    user = get_current_user()

    full_name = user.get(
        "full_name",
        "System Administrator",
    )

    username = user.get(
        "username",
        "admin",
    )

    role = user.get(
        "role",
        "Admin",
    )

    with st.sidebar:

        # ----------------------------------------------------
        # BRAND
        # ----------------------------------------------------

        if LOGO_FILE.exists():

            logo_path = LOGO_FILE.as_posix()

            st.markdown(
                f"""
                <div class="cs-brand">

                    <div class="cs-logo-box">
                        <img src="file://{logo_path}">
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

                    <div class="cs-logo-box">
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
            <div style="
                color:#475569;
                font-size:9px;
                font-weight:850;
                letter-spacing:1px;
                text-transform:uppercase;
                margin-bottom:8px;
            ">
                AEC Workspace
            </div>
            """,
            unsafe_allow_html=True,
        )

        menu = st.radio(
            "Navigation",
            [
                "Project Directory",
                "Drawing Repository",
                "Sign-Off & Approvals",
                "Bill of Quantities",
                "RFI & Technical Queries",
                "Daily Site Logs",
            ],
            label_visibility="collapsed",
        )

        st.markdown(
            "<br>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Sign Out",
            use_container_width=True,
        ):

            logout_user()

            st.rerun()

    return menu


# ============================================================
# MODULE PLACEHOLDER
# ============================================================

def unavailable_module(
    title: str,
) -> None:

    st.markdown(
        f"""
        <div class="project-card">

            <div class="project-title">
                {title}
            </div>

            <div class="project-meta">
                This module is ready to be connected.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APPLICATION ROUTER
# ============================================================

def render_app() -> None:

    menu = render_sidebar()

    if menu == "Project Directory":

        render_projects_module(db)

    elif menu == "Drawing Repository":

        unavailable_module(
            "Drawing Repository"
        )

    elif menu == "Sign-Off & Approvals":

        unavailable_module(
            "Sign-Off & Approvals"
        )

    elif menu == "Bill of Quantities":

        unavailable_module(
            "Bill of Quantities"
        )

    elif menu == "RFI & Technical Queries":

        unavailable_module(
            "RFI & Technical Queries"
        )

    elif menu == "Daily Site Logs":

        unavailable_module(
            "Daily Site Logs"
        )


# ============================================================
# START APPLICATION
# ============================================================

if not is_authenticated():

    render_login()

else:

    render_app()