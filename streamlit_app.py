"""
Creative Studios
Architectural, Engineering & Construction Collaboration Platform

Main Streamlit Application Controller
Version 1.0.0
"""

from pathlib import Path

import streamlit as st

from modules.utils import ensure_logo_svg, get_logo_html, LOGO_FILE
from modules.database import load_memory
from modules.auth import login_user, require_auth

from modules.projects import render_projects_module
from modules.drawings import render_drawings_module
from modules.approvals import render_approvals_module
from modules.boq import render_boq_module

# Optional modules
try:
    from modules.rfi import render_rfi_module
except ImportError:
    render_rfi_module = None

try:
    from modules.site_logs import render_site_logs_module
except ImportError:
    render_site_logs_module = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

# Make sure logo.svg exists before page configuration.
ensure_logo_svg()

st.set_page_config(
    page_title="Creative Studios | AEC Platform",
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------------
       GLOBAL
    -------------------------------------------------------- */

    .stApp {
        background-color: #F8FAFC;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    /* --------------------------------------------------------
       SIDEBAR
    -------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }

    section[data-testid="stSidebar"] * {
        color: #E2E8F0;
    }

    section[data-testid="stSidebar"] .stRadio label {
        padding: 8px 10px;
        border-radius: 8px;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #1E293B;
    }

    /* --------------------------------------------------------
       LOGIN
    -------------------------------------------------------- */

    .login-card {
        background: #FFFFFF;
        padding: 38px;
        border-radius: 18px;
        box-shadow: 0 10px 35px rgba(15, 23, 42, 0.08);
        border: 1px solid #E2E8F0;
    }

    .login-title {
        text-align: center;
        color: #0F172A;
        font-size: 30px;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 4px;
    }

    .login-subtitle {
        text-align: center;
        color: #64748B;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* --------------------------------------------------------
       CONTENT
    -------------------------------------------------------- */

    .module-header {
        margin-bottom: 20px;
    }

    .module-title {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }

    .module-subtitle {
        color: #64748B;
        font-size: 14px;
    }

    /* --------------------------------------------------------
       BUTTONS
    -------------------------------------------------------- */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
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
# LOGIN PAGE
# ============================================================

if not st.session_state["authenticated"]:

    # Hide sidebar while logged out
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 1.15, 1])

    with center:

        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            '<div class="login-card">',
            unsafe_allow_html=True,
        )

        # Logo
        st.markdown(
            get_logo_html(width=130),
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-title">Creative Studios</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="login-subtitle">
                Architectural, Engineering & Construction Collaboration
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Login form
        with st.form("creative_studios_login"):

            username = st.text_input(
                "Username",
                placeholder="Enter your username",
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

            if submitted:

                username = username.strip()

                if not username or not password:
                    st.warning("Please enter your username and password.")

                elif login_user(db, username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = username

                    st.success("Authentication successful.")

                    st.rerun()

                else:
                    st.error("Invalid username or password.")

        st.markdown(
            """
            <div style="
                text-align:center;
                color:#94A3B8;
                font-size:12px;
                margin-top:25px;
            ">
                Creative Studios AEC Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# ============================================================
# AUTHENTICATED APPLICATION
# ============================================================

require_auth()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # Logo
    st.markdown(
        get_logo_html(width=90),
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            text-align:center;
            font-size:18px;
            font-weight:700;
            margin-top:5px;
            margin-bottom:15px;
        ">
            Creative Studios
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        """
        <div style="
            font-size:11px;
            font-weight:700;
            color:#94A3B8;
            text-transform:uppercase;
            letter-spacing:1px;
            margin-bottom:8px;
        ">
            AEC Workspace
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu_items = [
        "Project Directory",
        "Drawing Repository",
        "Sign-Off & Approvals",
        "Bill of Quantities (BOQ)",
        "RFI & Technical Queries",
        "Daily Site Logs",
    ]

    app_mode = st.radio(
        "Navigation",
        menu_items,
        index=menu_items.index(
            st.session_state["app_mode"]
        )
        if st.session_state["app_mode"] in menu_items
        else 0,
        label_visibility="collapsed",
    )

    st.session_state["app_mode"] = app_mode

    st.divider()

    # Current user
    current_user = st.session_state.get("user")

    if current_user:
        st.markdown(
            f"""
            <div style="
                padding:10px;
                background:#1E293B;
                border-radius:8px;
                margin-bottom:10px;
            ">
                <div style="
                    font-size:11px;
                    color:#94A3B8;
                ">
                    SIGNED IN AS
                </div>

                <div style="
                    font-size:14px;
                    font-weight:600;
                    color:#F8FAFC;
                ">
                    {current_user}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button(
        "Sign Out",
        use_container_width=True,
    ):

        st.session_state["authenticated"] = False
        st.session_state["user"] = None
        st.session_state["app_mode"] = "Project Directory"

        st.rerun()


# ============================================================
# MAIN APPLICATION ROUTER
# ============================================================

if app_mode == "Project Directory":

    render_projects_module(db)


elif app_mode == "Drawing Repository":

    render_drawings_module(db)


elif app_mode == "Sign-Off & Approvals":

    render_approvals_module(db)


elif app_mode == "Bill of Quantities (BOQ)":

    render_boq_module(db)


elif app_mode == "RFI & Technical Queries":

    if render_rfi_module:
        render_rfi_module(db)

    else:
        st.title("RFI & Technical Queries")

        st.info(
            "The RFI module has not yet been installed."
        )


elif app_mode == "Daily Site Logs":

    if render_site_logs_module:
        render_site_logs_module(db)

    else:
        st.title("Daily Site Logs")

        st.info(
            "The Site Logs module has not yet been installed."
        )