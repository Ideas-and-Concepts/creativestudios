"""
Creative Studios
AEC Collaboration Platform

Main Streamlit application.

Version: 2.0.0
"""

from pathlib import Path

import streamlit as st

from modules.database import load_memory, save_memory
from modules.projects import render_projects_module


# ============================================================
# PAGE CONFIGURATION
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
    [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: #050505 !important;
    }

    .stApp {
        background: #050505 !important;
        color: #F8FAFC !important;
    }

    [data-testid="stHeader"] {
        background: #050505 !important;
    }

    .main {
        background: #050505 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }


    /* ======================================================
       SIDEBAR
       ====================================================== */

    [data-testid="stSidebar"] {
        background: #080808 !important;
        border-right: 1px solid #172033 !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        background: #080808 !important;
    }


    /* ======================================================
       SIDEBAR BRAND
       ====================================================== */

    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 4px 16px 4px;
    }

    .sidebar-logo {
        width: 44px;
        height: 44px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #2563EB;
        color: #FFFFFF;

        border-radius: 10px;

        font-size: 17px;
        font-weight: 900;
        letter-spacing: -1px;

        box-shadow: 0 0 20px rgba(37, 99, 235, 0.25);
    }

    .sidebar-brand-text {
        min-width: 0;
    }

    .sidebar-brand-name {
        color: #FFFFFF;
        font-size: 16px;
        font-weight: 850;
        line-height: 1.1;
    }

    .sidebar-brand-subtitle {
        color: #64748B;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 4px;
    }


    /* ======================================================
       SIDEBAR DIVIDER
       ====================================================== */

    .sidebar-divider {
        height: 1px;
        background: #172033;
        margin: 8px 0 16px 0;
    }


    /* ======================================================
       USER CARD
       ====================================================== */

    .sidebar-user-card {
        background: #0D1117;
        border: 1px solid #172033;
        border-radius: 10px;
        padding: 13px;
        margin-bottom: 10px;
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
        font-size: 15px;
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
        margin-top: 9px;
        padding: 4px 9px;
        background: #2563EB;
        color: #FFFFFF;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 850;
    }


    /* ======================================================
       SIDEBAR SECTION
       ====================================================== */

    .sidebar-section-title {
        color: #475569;
        font-size: 9px;
        font-weight: 850;
        letter-spacing: 1.3px;
        margin: 4px 0 9px 0;
    }


    /* ======================================================
       SIDEBAR RADIO
       ====================================================== */

    [data-testid="stSidebar"] .stRadio label {
        color: #CBD5E1 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    [data-testid="stSidebar"] .stRadio label:hover {
        color: #FFFFFF !important;
    }


    /* ======================================================
       SIDEBAR BUTTON
       ====================================================== */

    [data-testid="stSidebar"] .stButton button {
        background: #0D1117 !important;
        color: #CBD5E1 !important;
        border: 1px solid #172033 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: #2563EB !important;
        color: #FFFFFF !important;
        border-color: #2563EB !important;
    }


    /* ======================================================
       MAIN TYPOGRAPHY
       ====================================================== */

    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
        color: #FFFFFF !important;
    }

    p {
        color: #94A3B8;
    }


    /* ======================================================
       INPUTS
       ====================================================== */

    input,
    textarea {
        background: #0D1117 !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
    }

    [data-baseweb="select"] > div {
        background: #0D1117 !important;
        color: #FFFFFF !important;
        border-color: #1E293B !important;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton button {
        border-radius: 8px;
        font-weight: 700;
    }


    /* ======================================================
       METRICS
       ====================================================== */

    [data-testid="stMetric"] {
        background: #0D1117;
        border: 1px solid #172033;
        border-radius: 12px;
        padding: 18px;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
    }

    [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }


    /* ======================================================
       LOGIN PAGE
       ====================================================== */

    .login-page {
        min-height: 75vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .login-container {
        width: 100%;
        max-width: 430px;
        margin: auto;
    }

    .login-logo {
        width: 72px;
        height: 72px;

        margin: 0 auto 18px auto;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #2563EB;
        color: #FFFFFF;

        border-radius: 16px;

        font-size: 25px;
        font-weight: 900;

        box-shadow: 0 0 30px rgba(37, 99, 235, 0.30);
    }

    .login-title {
        color: #FFFFFF;
        text-align: center;
        font-size: 30px;
        font-weight: 900;
        letter-spacing: -0.7px;
    }

    .login-subtitle {
        color: #64748B;
        text-align: center;
        font-size: 13px;
        margin-top: 6px;
        margin-bottom: 28px;
    }

    .login-label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }


    /* ======================================================
       PROJECT CARDS
       ====================================================== */

    .project-card {
        background: #0B0F14;
        border: 1px solid #172033;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        transition: border-color 0.15s ease;
    }

    .project-card:hover {
        border-color: #2563EB;
    }

    .project-title {
        color: #FFFFFF;
        font-size: 18px;
        font-weight: 800;
    }

    .project-meta {
        color: #64748B;
        font-size: 12px;
        margin-top: 5px;
    }

    .project-status {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 9px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .status-active {
        background: #0B3B82;
        color: #93C5FD;
    }

    .status-planning {
        background: #422006;
        color: #FCD34D;
    }

    .status-completed {
        background: #064E3B;
        color: #6EE7B7;
    }

    .status-on-hold {
        background: #3F3F46;
        color: #D4D4D8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE
# ============================================================

db = load_memory()


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None

if "app_mode" not in st.session_state:
    st.session_state["app_mode"] = "Project Directory"


# ============================================================
# LOGIN
# ============================================================

if not st.session_state["authenticated"]:

    st.markdown(
        '<div class="login-page"><div class="login-container">',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="login-logo">
            CS
        </div>

        <div class="login-title">
            Creative Studios
        </div>

        <div class="login-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("creative_studios_login"):

        st.markdown(
            '<div class="login-label">Username</div>',
            unsafe_allow_html=True,
        )

        username = st.text_input(
            "Username",
            label_visibility="collapsed",
            placeholder="Enter username",
        )

        st.markdown(
            '<div class="login-label">Password</div>',
            unsafe_allow_html=True,
        )

        password = st.text_input(
            "Password",
            type="password",
            label_visibility="collapsed",
            placeholder="Enter password",
        )

        submitted = st.form_submit_button(
            "Sign In",
            use_container_width=True,
        )

    if submitted:

        users = db.get(
            "users",
            [],
        )

        authenticated_user = None

        for user in users:

            if not isinstance(user, dict):
                continue

            if (
                str(user.get("username", "")).strip().lower()
                == username.strip().lower()
                and str(user.get("password", ""))
                == password
                and user.get("active", True)
            ):
                authenticated_user = user
                break

        if authenticated_user:

            st.session_state["authenticated"] = True
            st.session_state["user"] = authenticated_user

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )

    st.markdown(
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

current_user = st.session_state.get(
    "user",
    {},
)

if not isinstance(current_user, dict):
    current_user = {}


username = current_user.get(
    "username",
    "admin",
)

full_name = (
    current_user.get("full_name")
    or current_user.get("name")
    or "System Administrator"
)

role = current_user.get(
    "role",
    "Admin",
)


with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="sidebar-logo">
                CS
            </div>

            <div class="sidebar-brand-text">

                <div class="sidebar-brand-name">
                    Creative Studios
                </div>

                <div class="sidebar-brand-subtitle">
                    AEC Workspace
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-user-card">

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

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-section-title">
            AEC WORKSPACE
        </div>
        """,
        unsafe_allow_html=True,
    )

    app_mode = st.radio(
        "Select Module",
        [
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities (BOQ)",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ],
        index=[
            "Project Directory",
            "Drawing Repository",
            "Sign-Off & Approvals",
            "Bill of Quantities (BOQ)",
            "RFI & Technical Queries",
            "Daily Site Logs",
        ].index(
            st.session_state.get(
                "app_mode",
                "Project Directory",
            )
        ),
        label_visibility="collapsed",
    )

    st.session_state["app_mode"] = app_mode

    st.markdown(
        '<div class="sidebar-divider"></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Sign Out",
        use_container_width=True,
    ):

        st.session_state["authenticated"] = False
        st.session_state["user"] = None

        st.rerun()


# ============================================================
# MAIN ROUTER
# ============================================================

if app_mode == "Project Directory":

    render_projects_module(
        db
    )

elif app_mode == "Drawing Repository":

    st.title("Drawing Repository")
    st.info(
        "The Drawing Repository module is ready for integration."
    )

elif app_mode == "Sign-Off & Approvals":

    st.title("Sign-Off & Approvals")
    st.info(
        "The Approvals module is ready for integration."
    )

elif app_mode == "Bill of Quantities (BOQ)":

    st.title("Bill of Quantities")
    st.info(
        "The BOQ module is ready for integration."
    )

elif app_mode == "RFI & Technical Queries":

    st.title("RFI & Technical Queries")
    st.info(
        "The RFI module is ready for integration."
    )

elif app_mode == "Daily Site Logs":

    st.title("Daily Site Logs")
    st.info(
        "The Site Logs module is ready for integration."
    )