"""
Creative Studios
Architectural, Engineering & Construction Collaboration Platform

Main Streamlit Application Controller

Version 1.1.0
"""

import streamlit as st

from modules.utils import (
    ensure_logo_svg,
    get_logo_html,
    LOGO_FILE,
)

from modules.database import (
    load_memory,
)

from modules.auth import (
    initialize_auth_session,
    login_user,
    require_auth,
    render_sidebar,
)

from modules.projects import (
    render_projects_module,
)

from modules.drawings import (
    render_drawings_module,
)

from modules.approvals import (
    render_approvals_module,
)

from modules.boq import (
    render_boq_module,
)


# ============================================================
# OPTIONAL MODULES
# ============================================================

try:

    from modules.rfi import (
        render_rfi_module,
    )

except ImportError:

    render_rfi_module = None


try:

    from modules.site_logs import (
        render_site_logs_module,
    )

except ImportError:

    render_site_logs_module = None


# ============================================================
# PAGE CONFIGURATION
# ============================================================

ensure_logo_svg()

st.set_page_config(
    page_title="Creative Studios | AEC Platform",
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BLUE THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       COLOR SYSTEM
       ======================================================== */

    :root {
        --cs-blue: #2563EB;
        --cs-blue-dark: #1D4ED8;
        --cs-blue-light: #DBEAFE;
        --cs-blue-pale: #EFF6FF;

        --cs-bg: #F8FAFC;
        --cs-white: #FFFFFF;

        --cs-text: #0F172A;
        --cs-muted: #64748B;
        --cs-border: #E2E8F0;
    }


    /* ========================================================
       APPLICATION
       ======================================================== */

    .stApp {
        background: var(--cs-bg);
    }


    [data-testid="stHeader"] {
        background: transparent;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #1D4ED8 0%,
                #2563EB 48%,
                #1E40AF 100%
            );

        border-right:
            1px solid
            rgba(255,255,255,0.12);
    }


    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }


    section[data-testid="stSidebar"] .stRadio > div {

        gap: 4px;
    }


    section[data-testid="stSidebar"]
    .stRadio label {

        padding:
            9px
            11px;

        border-radius:
            9px;

        transition:
            all 0.15s ease;
    }


    section[data-testid="stSidebar"]
    .stRadio label:hover {

        background:
            rgba(255,255,255,0.12);
    }


    section[data-testid="stSidebar"]
    .stRadio label[data-checked="true"] {

        background:
            rgba(255,255,255,0.18);
    }


    /* ========================================================
       LOGIN PAGE
       ======================================================== */

    .login-card {

        background:
            #FFFFFF;

        padding:
            40px;

        border-radius:
            20px;

        box-shadow:
            0 18px 50px
            rgba(37,99,235,0.12);

        border:
            1px solid
            #DBEAFE;
    }


    .login-title {

        text-align:
            center;

        color:
            #1E3A8A;

        font-size:
            30px;

        font-weight:
            800;

        margin-top:
            14px;

        margin-bottom:
            5px;
    }


    .login-subtitle {

        text-align:
            center;

        color:
            #64748B;

        font-size:
            14px;

        margin-bottom:
            25px;
    }


    /* ========================================================
       CONTENT HEADERS
       ======================================================== */

    .module-header {

        margin-bottom:
            22px;
    }


    .module-title {

        font-size:
            29px;

        font-weight:
            800;

        color:
            #1E3A8A;

        margin-bottom:
            4px;
    }


    .module-subtitle {

        color:
            #64748B;

        font-size:
            14px;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {

        border-radius:
            9px;

        font-weight:
            700;

        border:
            1px solid
            #2563EB;

        transition:
            all 0.15s ease;
    }


    .stButton > button:hover {

        border-color:
            #1D4ED8;

        color:
            #1D4ED8;
    }


    /* ========================================================
       FORM INPUTS
       ======================================================== */

    .stTextInput input:focus,
    .stTextArea textarea:focus {

        border-color:
            #2563EB;

        box-shadow:
            0 0 0 1px
            #2563EB;
    }


    /* ========================================================
       TABS
       ======================================================== */

    .stTabs [data-baseweb="tab-list"] {

        gap:
            6px;
    }


    .stTabs [data-baseweb="tab"] {

        font-weight:
            700;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {

        background:
            #FFFFFF;

        border:
            1px solid
            #DBEAFE;

        border-radius:
            12px;

        padding:
            12px;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {

        border-color:
            #DBEAFE;
    }


    /* ========================================================
       LINKS
       ======================================================== */

    a {

        color:
            #2563EB !important;
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

initialize_auth_session()

if "app_mode" not in st.session_state:

    st.session_state[
        "app_mode"
    ] = "Project Directory"


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.get(
    "authenticated",
    False,
):

    # Hide sidebar while logged out.
    # It will automatically return after authentication.
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

    left, center, right = st.columns(
        [1, 1.15, 1]
    )

    with center:

        st.markdown(
            "<br><br>",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-card">',
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        st.markdown(
            get_logo_html(
                width=130
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="login-title">
                Creative Studios
            </div>
            """,
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

        # ----------------------------------------------------
        # LOGIN FORM
        # ----------------------------------------------------

        with st.form(
            "creative_studios_login"
        ):

            username = st.text_input(
                "Username",
                placeholder=(
                    "Enter your username"
                ),
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder=(
                    "Enter your password"
                ),
            )

            submitted = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )

            if submitted:

                username = (
                    username or ""
                ).strip()

                password = (
                    password or ""
                )

                if (
                    not username
                    or not password
                ):

                    st.warning(
                        "Please enter your username and password."
                    )

                elif login_user(
                    db,
                    username,
                    password,
                ):

                    st.success(
                        "Authentication successful."
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
                color:#94A3B8;
                font-size:12px;
                margin-top:25px;
            ">
                Creative Studios AEC Platform
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

    st.stop()


# ============================================================
# AUTHENTICATED APPLICATION
# ============================================================

require_auth()


# ============================================================
# RESTORED SIDEBAR
# ============================================================

render_sidebar()


# ============================================================
# CURRENT MODULE
# ============================================================

app_mode = st.session_state.get(
    "app_mode",
    "Project Directory",
)


# ============================================================
# APPLICATION ROUTER
# ============================================================

if app_mode == "Project Directory":

    render_projects_module(
        db
    )


elif app_mode == "Drawing Repository":

    render_drawings_module(
        db
    )


elif app_mode == "Sign-Off & Approvals":

    render_approvals_module(
        db
    )


elif app_mode == "Bill of Quantities (BOQ)":

    render_boq_module(
        db
    )


elif app_mode == "RFI & Technical Queries":

    if render_rfi_module:

        render_rfi_module(
            db
        )

    else:

        st.title(
            "RFI & Technical Queries"
        )

        st.info(
            "The RFI module has not yet been installed."
        )


elif app_mode == "Daily Site Logs":

    if render_site_logs_module:

        render_site_logs_module(
            db
        )

    else:

        st.title(
            "Daily Site Logs"
        )

        st.info(
            "The Site Logs module has not yet been installed."
        )


else:

    st.session_state[
        "app_mode"
    ] = "Project Directory"

    st.rerun()