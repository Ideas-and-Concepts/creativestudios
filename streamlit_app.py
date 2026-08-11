"""
Creative Studios
Architectural, Engineering & Construction Collaboration Platform

Main Streamlit Application Controller

Version 1.1.0
"""

import streamlit as st


# ============================================================
# CORE IMPORTS
# ============================================================

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
# LOGO
# ============================================================

ensure_logo_svg()


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title=(
        "Creative Studios | AEC Platform"
    ),
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CREATIVE STUDIOS BLUE + BLACK DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {

        background:
            linear-gradient(
                135deg,
                #F8FAFC 0%,
                #EFF6FF 100%
            );

        color:
            #0F172A;
    }


    [data-testid="stHeader"] {

        background:
            transparent;
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {

        background:
            linear-gradient(
                180deg,
                #020617 0%,
                #0F172A 45%,
                #172554 100%
            );

        border-right:
            2px solid #2563EB;

        box-shadow:
            8px 0 30px
            rgba(15,23,42,0.18);
    }


    section[data-testid="stSidebar"] * {

        color:
            #FFFFFF;
    }


    section[data-testid="stSidebar"]
    .stRadio label {

        color:
            #CBD5E1;

        padding:
            10px 12px;

        margin:
            3px 0;

        border-radius:
            9px;

        font-weight:
            650;
    }


    section[data-testid="stSidebar"]
    .stRadio label:hover {

        background:
            rgba(37,99,235,0.25);

        color:
            #FFFFFF;
    }


    /* ========================================================
       MAIN HEADINGS
       ======================================================== */

    h1,
    h2,
    h3 {

        color:
            #0F172A !important;

        font-weight:
            800;
    }


    /* ========================================================
       LOGIN
       ======================================================== */

    .login-card {

        background:
            #FFFFFF;

        padding:
            42px;

        border-radius:
            20px;

        border:
            1px solid #DBEAFE;

        border-top:
            5px solid #2563EB;

        box-shadow:
            0 25px 60px
            rgba(15,23,42,0.12);
    }


    .login-title {

        text-align:
            center;

        color:
            #020617;

        font-size:
            31px;

        font-weight:
            850;

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

        line-height:
            1.5;

        margin-bottom:
            25px;
    }


    /* ========================================================
       BUTTONS
       ======================================================== */

    .stButton > button {

        background:
            #020617;

        color:
            #FFFFFF;

        border:
            1px solid #020617;

        border-radius:
            9px;

        font-weight:
            750;

        min-height:
            42px;

        transition:
            all 0.15s ease;
    }


    .stButton > button:hover {

        background:
            #2563EB;

        border-color:
            #2563EB;

        color:
            #FFFFFF;
    }


    .stFormSubmitButton > button {

        background:
            #2563EB !important;

        border-color:
            #2563EB !important;

        color:
            #FFFFFF !important;

        font-weight:
            800 !important;
    }


    .stFormSubmitButton > button:hover {

        background:
            #1D4ED8 !important;

        border-color:
            #1D4ED8 !important;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input {

        background:
            #FFFFFF;

        color:
            #0F172A;

        border:
            1px solid #CBD5E1;

        border-radius:
            9px;
    }


    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {

        border-color:
            #2563EB;

        box-shadow:
            0 0 0 1px #2563EB;
    }


    /* ========================================================
       SELECTBOX
       ======================================================== */

    div[data-baseweb="select"] > div {

        background:
            #FFFFFF;

        border-radius:
            9px;

        border-color:
            #CBD5E1;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {

        background:
            #FFFFFF;

        border:
            1px solid #CBD5E1;

        border-top:
            4px solid #2563EB;

        border-radius:
            13px;

        padding:
            15px;

        box-shadow:
            0 7px 20px
            rgba(15,23,42,0.06);
    }


    [data-testid="stMetricLabel"] {

        color:
            #64748B !important;

        font-weight:
            700;
    }


    [data-testid="stMetricValue"] {

        color:
            #020617 !important;

        font-weight:
            850;
    }


    /* ========================================================
       TABS
       ======================================================== */

    button[data-baseweb="tab"] {

        color:
            #475569;

        font-weight:
            750;
    }


    button[data-baseweb="tab"][aria-selected="true"] {

        color:
            #2563EB;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {

        background:
            #FFFFFF;

        border:
            1px solid #CBD5E1;

        border-radius:
            10px;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {

        border-radius:
            10px;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {

        border-color:
            #CBD5E1;
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

    # Hide sidebar on login.
    st.markdown(
        """
        <style>

        section[data-testid="stSidebar"] {
            display:none;
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
                Architectural, Engineering & Construction
                Collaboration Platform
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
                    #
                    # login_user() already sets:
                    #
                    # authenticated = True
                    # user = complete user dictionary
                    #
                    # Therefore we DO NOT overwrite
                    # session_state["user"] here.

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
# AUTHENTICATION
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
        get_logo_html(
            width=85
        ),
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div style="
            text-align:center;
            color:#FFFFFF;
            font-size:20px;
            font-weight:850;
            margin-top:5px;
        ">
            Creative Studios
        </div>

        <div style="
            text-align:center;
            color:#93C5FD;
            font-size:9px;
            font-weight:800;
            letter-spacing:1.1px;
            text-transform:uppercase;
            margin-top:4px;
        ">
            AEC Collaboration Platform
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
            color:#60A5FA;
            font-size:10px;
            font-weight:850;
            letter-spacing:1px;
            text-transform:uppercase;
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

    current_user = st.session_state.get(
        "user"
    )


    if isinstance(
        current_user,
        dict,
    ):

        display_name = current_user.get(
            "name",
            current_user.get(
                "username",
                "User",
            ),
        )

        username = current_user.get(
            "username",
            "",
        )

        role = current_user.get(
            "role",
            "User",
        )

    else:

        display_name = str(
            current_user or "User"
        )

        username = ""
        role = "User"


    st.markdown(
        f"""
        <div style="
            background:#020617;
            border:1px solid #1E3A8A;
            border-left:3px solid #2563EB;
            border-radius:10px;
            padding:12px;
        ">

            <div style="
                color:#60A5FA;
                font-size:9px;
                font-weight:850;
                letter-spacing:1px;
                text-transform:uppercase;
            ">
                Signed In
            </div>

            <div style="
                color:#FFFFFF;
                font-size:15px;
                font-weight:800;
                margin-top:5px;
            ">
                {display_name}
            </div>

            <div style="
                color:#94A3B8;
                font-size:11px;
                margin-top:3px;
            ">
                @{username}
            </div>

            <div style="
                display:inline-block;
                margin-top:8px;
                padding:4px 9px;
                background:#2563EB;
                color:#FFFFFF;
                border-radius:999px;
                font-size:9px;
                font-weight:850;
            ">
                {role}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.write("")


    # --------------------------------------------------------
    # SIGN OUT
    # --------------------------------------------------------

    if st.button(
        "Sign Out",
        use_container_width=True,
        key="creative_studios_signout",
    ):

        st.session_state[
            "authenticated"
        ] = False

        st.session_state[
            "user"
        ] = None

        st.session_state[
            "app_mode"
        ] = "Project Directory"

        st.rerun()


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

        st.markdown(
            """
            <div style="
                background:#020617;
                color:#FFFFFF;
                padding:25px;
                border-radius:14px;
                border-left:5px solid #2563EB;
            ">

                <div style="
                    font-size:24px;
                    font-weight:800;
                ">
                    RFI & Technical Queries
                </div>

                <div style="
                    color:#CBD5E1;
                    margin-top:6px;
                ">
                    The RFI module is not currently installed.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


elif app_mode == "Daily Site Logs":

    if render_site_logs_module:

        render_site_logs_module(
            db
        )

    else:

        st.markdown(
            """
            <div style="
                background:#020617;
                color:#FFFFFF;
                padding:25px;
                border-radius:14px;
                border-left:5px solid #2563EB;
            ">

                <div style="
                    font-size:24px;
                    font-weight:800;
                ">
                    Daily Site Logs
                </div>

                <div style="
                    color:#CBD5E1;
                    margin-top:6px;
                ">
                    The Daily Site Logs module is not
                    currently installed.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )