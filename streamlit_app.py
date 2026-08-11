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
    login_user,
    require_auth,
    render_user_profile,
    render_sidebar_logout,
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
# BLUE CREATIVE STUDIOS THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background-color: #F8FAFC;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #1D4ED8 0%,
                #2563EB 52%,
                #1E40AF 100%
            );

        border-right:
            1px solid
            rgba(255,255,255,0.15);
    }


    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }


    section[data-testid="stSidebar"]
    .stRadio label {

        padding:
            9px 11px;

        border-radius:
            9px;

        font-weight:
            600;

        transition:
            all 0.15s ease;
    }


    section[data-testid="stSidebar"]
    .stRadio label:hover {

        background:
            rgba(255,255,255,0.13);
    }


    /* ========================================================
       LOGIN CARD
       ======================================================== */

    .login-card {

        background:
            #FFFFFF;

        padding:
            40px;

        border-radius:
            20px;

        border:
            1px solid
            #DBEAFE;

        box-shadow:
            0 20px 55px
            rgba(37,99,235,0.12);
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
            15px;

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
       CONTENT
       ======================================================== */

    .module-header {
        margin-bottom: 20px;
    }


    .module-title {

        font-size:
            29px;

        font-weight:
            800;

        color:
            #1E3A8A;

        margin-bottom:
            5px;
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
    }


    .stButton > button:hover {

        border-color:
            #1D4ED8;

        color:
            #1D4ED8;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input:focus,
    .stTextArea textarea:focus {

        border-color:
            #2563EB;

        box-shadow:
            0 0 0 1px #2563EB;
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

    st.session_state[
        "authenticated"
    ] = False


if "user" not in st.session_state:

    st.session_state[
        "user"
    ] = None


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


        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

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

                username = (
                    username or ""
                ).strip()


                password = (
                    password or ""
                )


                if not username:

                    st.warning(
                        "Please enter your username."
                    )


                elif not password:

                    st.warning(
                        "Please enter your password."
                    )


                elif login_user(
                    db,
                    username,
                    password,
                ):

                    # IMPORTANT:
                    # login_user() already stores the
                    # complete user dictionary.
                    #
                    # DO NOT replace it with the
                    # username string.

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
# AUTHENTICATION CHECK
# ============================================================

require_auth()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:8px 0 15px;
        ">

            <div style="
                font-size:21px;
                font-weight:800;
                color:#FFFFFF;
                letter-spacing:-0.5px;
            ">
                Creative Studios
            </div>

            <div style="
                font-size:9px;
                color:#DBEAFE;
                font-weight:700;
                letter-spacing:1.1px;
                text-transform:uppercase;
                margin-top:4px;
            ">
                AEC Collaboration Platform
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.divider()


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div style="
            font-size:10px;
            color:#BFDBFE;
            font-weight:800;
            text-transform:uppercase;
            letter-spacing:1px;
            margin-bottom:7px;
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


    current_mode = st.session_state.get(
        "app_mode",
        "Project Directory",
    )


    if current_mode not in menu_items:

        current_mode = (
            "Project Directory"
        )


    app_mode = st.radio(
        "Navigation",
        menu_items,
        index=menu_items.index(
            current_mode
        ),
        label_visibility="collapsed",
    )


    st.session_state[
        "app_mode"
    ] = app_mode


    st.divider()


    # --------------------------------------------------------
    # USER PROFILE
    # --------------------------------------------------------

    render_user_profile()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    render_sidebar_logout()


# ============================================================
# MAIN APPLICATION ROUTER
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
            "The RFI module is not currently installed."
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
            "The Daily Site Logs module is not currently installed."
        )