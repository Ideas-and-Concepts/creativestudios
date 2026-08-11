"""
Creative Studios
Architectural, Engineering & Construction Collaboration Platform

Main Streamlit Application Controller
"""

import streamlit as st


# ============================================================
# MODULE IMPORTS
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
# LOGO
# ============================================================

ensure_logo_svg()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Creative Studios | AEC Platform",
    page_icon=LOGO_FILE,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BLUE + BLACK THEME
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

        color: #0F172A;
    }


    /* ========================================================
       HEADER
       ======================================================== */

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
                #020617 0%,
                #0F172A 55%,
                #172554 100%
            );

        border-right:
            2px solid #2563EB;

        box-shadow:
            8px 0 30px
            rgba(15, 23, 42, 0.20);
    }


    section[data-testid="stSidebar"] > div {
        padding-top: 1rem;
    }


    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }


    /* ========================================================
       SIDEBAR BRAND
       ======================================================== */

    .sidebar-brand {
        text-align: center;
        padding: 8px 5px 12px 5px;
    }


    .sidebar-brand-title {
        color: #FFFFFF;
        font-size: 21px;
        font-weight: 850;
        margin-top: 6px;
    }


    .sidebar-brand-subtitle {
        color: #60A5FA;
        font-size: 9px;
        font-weight: 800;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-top: 4px;
    }


    /* ========================================================
       SIDEBAR SECTION
       ======================================================== */

    .sidebar-section-title {
        color: #60A5FA;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin: 12px 0 7px 0;
    }


    /* ========================================================
       RADIO NAVIGATION
       ======================================================== */

    section[data-testid="stSidebar"]
    .stRadio > div {

        gap: 4px;
    }


    section[data-testid="stSidebar"]
    .stRadio label {

        background: transparent;

        color: #CBD5E1;

        padding:
            9px 11px;

        border-radius:
            9px;

        font-size:
            13px;

        font-weight:
            650;

        transition:
            all 0.15s ease;
    }


    section[data-testid="stSidebar"]
    .stRadio label:hover {

        background:
            rgba(37, 99, 235, 0.22);

        color:
            #FFFFFF;
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
            1px solid #1E293B;

        border-radius:
            9px;

        font-weight:
            750;

        min-height:
            40px;
    }


    .stButton > button:hover {

        background:
            #2563EB;

        border-color:
            #2563EB;

        color:
            #FFFFFF;
    }


    /* ========================================================
       FORM BUTTONS
       ======================================================== */

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
       SELECT BOX
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
            rgba(15, 23, 42, 0.06);
    }


    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-weight: 700;
    }


    [data-testid="stMetricValue"] {
        color: #020617 !important;
        font-weight: 850;
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
        border-radius: 10px;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #1E3A8A;
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


    left, center, right = st.columns(
        [1, 1.15, 1]
    )


    with center:

        st.markdown(
            "<br><br>",
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div style="
                background:#FFFFFF;
                padding:40px;
                border-radius:20px;
                border:1px solid #DBEAFE;
                border-top:5px solid #2563EB;
                box-shadow:
                    0 25px 60px
                    rgba(15,23,42,0.12);
            ">
            """,
            unsafe_allow_html=True,
        )


        st.markdown(
            get_logo_html(
                width=130
            ),
            unsafe_allow_html=True,
        )


        st.markdown(
            """
            <div style="
                text-align:center;
                color:#020617;
                font-size:30px;
                font-weight:850;
                margin-top:12px;
            ">
                Creative Studios
            </div>

            <div style="
                text-align:center;
                color:#64748B;
                font-size:14px;
                margin-top:5px;
                margin-bottom:25px;
            ">
                Architectural, Engineering &
                Construction Collaboration Platform
            </div>
            """,
            unsafe_allow_html=True,
        )


        with st.form(
            "login_form"
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


            submit = st.form_submit_button(
                "Sign In",
                use_container_width=True,
            )


            if submit:

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
                font-size:11px;
                margin-top:20px;
            ">
                Creative Studios AEC Platform
            </div>

            </div>
            """,
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
    # LOGO
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-brand">',
        unsafe_allow_html=True,
    )


    st.markdown(
        get_logo_html(
            width=82
        ),
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="sidebar-brand-title">
            Creative Studios
        </div>

        <div class="sidebar-brand-subtitle">
            AEC Collaboration Platform
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    st.divider()


    # --------------------------------------------------------
    # WORKSPACE NAVIGATION
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="sidebar-section-title">
            AEC Workspace
        </div>
        """,
        unsafe_allow_html=True,
    )


    navigation = [
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


    if current_mode not in navigation:
        current_mode = "Project Directory"


    selected_module = st.radio(
        "Navigation",
        navigation,
        index=navigation.index(
            current_mode
        ),
        label_visibility="collapsed",
    )


    st.session_state[
        "app_mode"
    ] = selected_module


    st.divider()


    # --------------------------------------------------------
    # USER INFORMATION
    # --------------------------------------------------------

    user = st.session_state.get(
        "user"
    )


    if isinstance(
        user,
        dict,
    ):

        display_name = user.get(
            "name",
            user.get(
                "username",
                "User",
            ),
        )

        username = user.get(
            "username",
            "",
        )

        role = user.get(
            "role",
            "User",
        )

    else:

        display_name = str(
            user or "User"
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
        key="sidebar_signout",
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
# MAIN APPLICATION ROUTER
# ============================================================

if selected_module == "Project Directory":

    render_projects_module(
        db
    )


elif selected_module == "Drawing Repository":

    render_drawings_module(
        db
    )


elif selected_module == "Sign-Off & Approvals":

    render_approvals_module(
        db
    )


elif selected_module == "Bill of Quantities (BOQ)":

    render_boq_module(
        db
    )


elif selected_module == "RFI & Technical Queries":

    if render_rfi_module:

        render_rfi_module(
            db
        )

    else:

        st.info(
            "RFI module is not currently available."
        )


elif selected_module == "Daily Site Logs":

    if render_site_logs_module:

        render_site_logs_module(
            db
        )

    else:

        st.info(
            "Daily Site Logs module is not currently available."
        )